"""Earth Engine operations for Flutter Earth."""
import logging
from typing import Optional, List, Dict, Any, Union
import ee
from ee import data as ee_data
from datetime import datetime, date
import functools
import time
from threading import Lock
import os
import json
from pathlib import Path

from .errors import EarthEngineError, handle_errors
from .types import ProcessingParams, EEImage, EEFeatureCollection
from .config import config_manager
from .auth_setup import AuthManager

def require_initialized(func):
    """Decorator to ensure Earth Engine is initialized."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.initialized:
            self.initialize()
        if not self.initialized:
            raise EarthEngineError("Earth Engine not initialized")
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if "Token has expired" in str(e):
                logging.warning("Earth Engine token expired, reinitializing...")
                self.initialized = False
                self.initialize()
                return func(self, *args, **kwargs)
            raise
    return wrapper

class EarthEngineManager:
    """Manages Earth Engine operations."""
    
    def __init__(self):
        """Initialize Earth Engine manager."""
        self.initialized = False
        self.project = None
        self._collection_cache = {}
        self._cache_lock = Lock()
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
    
    def _check_connection_health(self) -> bool:
        """Check if Earth Engine connection is healthy.
        
        Returns:
            True if connection is healthy.
        """
        now = time.time()
        if now - self._last_health_check < self._health_check_interval:
            return True
            
        try:
            ee_data.getAssetRoots()
            self._last_health_check = now
            return True
        except Exception as e:
            logging.warning(f"Earth Engine health check failed: {e}")
            self.initialized = False
            return False
    
    @handle_errors()
    def initialize(self, project: Optional[str] = None, force: bool = False, parent=None) -> bool:
        """Initialize Earth Engine.
        
        Args:
            project: Optional project ID.
            force: Force reinitialization even if already initialized.
            parent: Parent widget for authentication dialogs.
        
        Returns:
            True if initialization successful, False otherwise.
        """
        if self.initialized and not force:
            if self._check_connection_health():
                return True
            logging.info("Connection unhealthy, forcing reinitialization")
            
        self.project = project
        
        # Try to get project from environment if not provided
        if not project:
            project = os.environ.get('EARTHENGINE_PROJECT')
            if project:
                logging.info(f"Using project from environment: {project}")
                self.project = project
        
        # Try to load stored credentials first
        auth_manager = AuthManager()
        credentials = auth_manager.load_credentials()
        
        if credentials:
            try:
                # Initialize with stored service account credentials
                try:
                    service_account_creds = ee.ServiceAccountCredentials('', credentials['key_file'])
                except AttributeError:
                    # Fall back to regular initialization if ServiceAccountCredentials not available
                    ee.Initialize(project=credentials['project_id'])
                else:
                    ee.Initialize(service_account_creds, project=credentials['project_id'])
                ee_data.getAssetRoots()
                logging.info("Earth Engine initialized successfully with stored credentials.")
                self.initialized = True
                self._last_health_check = time.time()
                return True
            except Exception as e:
                logging.warning(f"Failed to initialize with stored credentials: {e}")
                # Fall back to interactive setup
        
        # Try interactive authentication setup
        if parent:
            try:
                if auth_manager.initialize_earth_engine(parent):
                    self.initialized = True
                    self._last_health_check = time.time()
                    return True
            except Exception as e:
                logging.warning(f"Interactive authentication setup failed: {e}")
        
        # Fall back to traditional initialization methods
        try:
            # Try high-volume endpoint first
            ee.Initialize(
                project=project,
                opt_url='https://earthengine-highvolume.googleapis.com'
            )
            # Verify initialization
            ee_data.getAssetRoots()
            logging.info("Earth Engine initialized successfully (high-volume).")
            self.initialized = True
            self._last_health_check = time.time()
            return True
        except Exception as e_hv:
            logging.warning(
                f"High-volume EE initialization failed: {e_hv}. "
                "Trying default endpoint."
            )
            try:
                ee.Initialize(project=project)
                ee_data.getAssetRoots()
                logging.info("Earth Engine initialized successfully (default).")
                self.initialized = True
                self._last_health_check = time.time()
                return True
            except Exception as e_def:
                err_msg = str(e_def).lower()
                
                # Log the error but don't raise - return False instead
                logging.error(f"Earth Engine initialization failed: {e_def}")
                
                # Provide specific guidance based on error type
                if "no project found" in err_msg or "project" in err_msg:
                    logging.error(
                        "Earth Engine project not found. Please:\n"
                        "1. Create a Google Cloud project with Earth Engine API enabled\n"
                        "2. Set up service account authentication using the setup dialog\n"
                        "3. Or set environment variable: EARTHENGINE_PROJECT=your-project-id\n"
                        "4. Visit https://developers.google.com/earth-engine/guides/access to sign up"
                    )
                elif any(x in err_msg for x in ["authenticate", "oauth", "credentials"]):
                    logging.error(
                        "Authentication required. Please:\n"
                        "1. Set up service account authentication using the setup dialog\n"
                        "2. Or run: python -c 'import ee; ee.Authenticate()'\n"
                        "3. Follow the authentication prompts in your browser\n"
                        "4. Make sure you have Earth Engine access enabled"
                    )
                elif "permission" in err_msg or "forbidden" in err_msg:
                    logging.error(
                        "Permission denied. Please:\n"
                        "1. Make sure you have Earth Engine access enabled\n"
                        "2. Check that your Google Cloud project has Earth Engine API enabled\n"
                        "3. Verify your service account has the correct roles\n"
                        "4. Visit https://developers.google.com/earth-engine/guides/access to sign up"
                    )
                else:
                    logging.error(
                        f"Earth Engine initialization failed: {e_def}\n"
                        "Please check:\n"
                        "1. Your internet connection\n"
                        "2. Earth Engine service status\n"
                        "3. Your authentication and project setup\n"
                        "4. Try setting up service account authentication"
                    )
                
                # Return False instead of raising exception
                return False
    
    def _get_cache_key(self, sensor_name: str, start_date: Union[datetime, date], 
                       end_date: Union[datetime, date], region: Optional[Any]) -> str:
        """Generate cache key for collection parameters."""
        region_str = str(region.getInfo()) if region else "None"
        return f"{sensor_name}_{start_date}_{end_date}_{region_str}"
    
    @require_initialized
    @handle_errors()
    def get_collection(
        self,
        sensor_name: str,
        start_date: Union[datetime, date],
        end_date: Union[datetime, date],
        region: Optional[Any] = None,
        use_cache: bool = True
    ) -> Any:
        """Get image collection for sensor.
        
        Args:
            sensor_name: Name of the sensor.
            start_date: Start date.
            end_date: End date.
            region: Optional region to filter by.
            use_cache: Whether to use cached collection if available.
        
        Returns:
            Earth Engine image collection.
        
        Raises:
            EarthEngineError: If collection cannot be retrieved.
        """
        details = config_manager.get_satellite_details(sensor_name)
        if not details:
            raise EarthEngineError(f"Unknown sensor: {sensor_name}")
            
        if use_cache:
            cache_key = self._get_cache_key(sensor_name, start_date, end_date, region)
            with self._cache_lock:
                if cache_key in self._collection_cache:
                    logging.info(f"Using cached collection for {sensor_name}")
                    return self._collection_cache[cache_key]
            
        collection = ee.ImageCollection(details['collection_id'])
        
        # Filter by date
        collection = collection.filterDate(start_date, end_date)
        
        # Filter by region if provided
        if region:
            collection = collection.filterBounds(region)
        
        if use_cache:
            with self._cache_lock:
                self._collection_cache[cache_key] = collection
                # Limit cache size
                if len(self._collection_cache) > 10:
                    self._collection_cache.pop(next(iter(self._collection_cache)))
        
        return collection
    
    @require_initialized
    @handle_errors()
    def process_image(
        self,
        image: EEImage,
        sensor_name: str,
        params: ProcessingParams
    ) -> EEImage:
        """Process Earth Engine image.
        
        Args:
            image: Earth Engine image.
            sensor_name: Name of the sensor.
            params: Processing parameters.
        
        Returns:
            Processed Earth Engine image.
        
        Raises:
            EarthEngineError: If processing fails.
        """
        # Apply cloud masking if enabled and supported
        if params.get('cloud_mask', False):
            details = config_manager.get_satellite_details(sensor_name)
            if details and details['cloud_cover']:
                if sensor_name == 'LANDSAT_9':
                    image = self._mask_clouds_landsat(image)
                elif sensor_name == 'SENTINEL_2':
                    image = self._mask_clouds_sentinel2(image)
        
        # Apply scaling factors
        if sensor_name == 'LANDSAT_9':
            image = self._scale_landsat(image)
        elif sensor_name == 'SENTINEL_2':
            image = self._scale_sentinel2(image)
        elif sensor_name == 'ERA5_TEMP':
            image = self._scale_era5(image)
        
        return image
    
    def _mask_clouds_landsat(self, image: EEImage) -> EEImage:
        """Apply cloud masking for Landsat."""
        qa = image.select('QA_PIXEL')
        cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)  # Cloud
        shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)  # Cloud shadow
        return image.updateMask(cloud_mask.And(shadow_mask))
    
    def _mask_clouds_sentinel2(self, image: EEImage) -> EEImage:
        """Apply cloud masking for Sentinel-2."""
        qa = image.select('QA60')
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)  # Opaque clouds
        cirrus_mask = qa.bitwiseAnd(1 << 11).eq(0)  # Cirrus clouds
        return image.updateMask(cloud_mask.And(cirrus_mask))
    
    def _scale_landsat(self, image: EEImage) -> EEImage:
        """Apply scaling factors for Landsat."""
        optical_bands = image.select('SR_.*')
        thermal_bands = image.select('ST_.*')
        
        # Scale optical bands
        optical_scaled = optical_bands.multiply(0.0000275).add(-0.2)
        
        # Scale thermal bands
        thermal_scaled = thermal_bands.multiply(0.00341802).add(149.0)
        
        return image.addBands(optical_scaled, None, True) \
                   .addBands(thermal_scaled, None, True)
    
    def _scale_sentinel2(self, image: EEImage) -> EEImage:
        """Apply scaling factors for Sentinel-2."""
        bands_to_scale = image.select('B.*')
        scaled = bands_to_scale.divide(10000.0)
        
        # Keep QA bands as they are
        qa_bands = image.select(['QA60', 'SCL'])
        
        return image.addBands(scaled, None, True) \
                   .addBands(qa_bands, None, True)
    
    def _scale_era5(self, image: EEImage) -> EEImage:
        """Apply scaling factors for ERA5."""
        # Convert from Kelvin to Celsius
        temp = image.select('temperature_2m').subtract(273.15)
        return image.addBands(temp, ['temperature_2m_celsius'], True)

# Global Earth Engine manager instance
ee_manager = EarthEngineManager() 