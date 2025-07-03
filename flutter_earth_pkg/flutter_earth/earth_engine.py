"""Earth Engine management for Flutter Earth."""
import os
import time
import logging
from typing import Optional, Dict
from pathlib import Path
import ee
import ee.data

from .auth_setup import AuthManager
from .errors import EarthEngineError
from .utils import handle_errors

class EarthEngineManager:
    """Manages Earth Engine initialization and operations."""
    
    def __init__(self):
        self.initialized = False
        self.project = None
        self._last_health_check = 0
        self._health_check_interval = 300  # 5 minutes
        self.auth_manager = AuthManager()
        self.logger = logging.getLogger(__name__)
        
    def _check_connection_health(self) -> bool:
        """Check if the Earth Engine connection is healthy."""
        current_time = time.time()
        if current_time - self._last_health_check < self._health_check_interval:
            return True
            
        try:
            # Simple test to verify connection
            test_image = ee.Image('USGS/SRTMGL1_003')
            _ = test_image.geometry().bounds().getInfo()
            self._last_health_check = current_time
            return True
        except Exception as e:
            self.logger.warning(f"Connection health check failed: {e}")
            return False
    
    @handle_errors
    def initialize(self, project: Optional[str] = None, force: bool = False) -> Dict:
        """Initialize Earth Engine with proper authentication.
        
        Args:
            project: Optional project ID (will use stored credentials if not provided)
            force: Force reinitialization even if already initialized
        
        Returns:
            Dictionary with status, message, and initialized flag
        """
        if self.initialized and not force:
            if self._check_connection_health():
                return {
                    "status": "online",
                    "message": "Earth Engine connection is healthy.",
                    "initialized": True
                }
            self.logger.info("Connection unhealthy, forcing reinitialization")
            
        self.project = project
        
        # Try to get project from environment if not provided
        if not project:
            project = os.environ.get('EARTHENGINE_PROJECT')
            if project:
                self.logger.info(f"Using project from environment: {project}")
                self.project = project
        
        # Check authentication status first
        if not self.auth_manager.has_credentials():
            self.logger.warning("No authentication credentials found")
            return {
                "status": "auth_required",
                "message": "Authentication credentials required. Please set up Earth Engine authentication.",
                "initialized": False,
                "needs_auth": True
            }
        
        # Initialize Earth Engine with stored credentials
        success, message = self.auth_manager.initialize_earth_engine()
        
        if success:
            self.initialized = True
            self._last_health_check = time.time()
            self.logger.info("Earth Engine initialized successfully")
            return {
                "status": "online",
                "message": message,
                "initialized": True
            }
        else:
            self.logger.error(f"Earth Engine initialization failed: {message}")
            return {
                "status": "error",
                "message": message,
                "initialized": False
            }
    
    def get_auth_status(self) -> Dict:
        """Get current authentication status."""
        return self.auth_manager.get_auth_info()
    
    def is_authenticated(self) -> bool:
        """Check if Earth Engine is authenticated."""
        return self.auth_manager.is_authenticated()
    
    def needs_authentication(self) -> bool:
        """Check if authentication is needed."""
        return self.auth_manager.needs_authentication()
    
    def test_connection(self, project_id: str, key_file: str) -> Dict:
        """Test Earth Engine connection with provided credentials."""
        try:
            self.auth_manager.test_connection(project_id, key_file)
            return {
                "status": "success",
                "message": "Connection test completed successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }
    
    def save_credentials(self, project_id: str, key_file: str) -> Dict:
        """Save authentication credentials."""
        try:
            self.auth_manager.save_credentials(project_id, key_file)
            return {
                "status": "success",
                "message": "Credentials saved successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to save credentials: {str(e)}"
            }
    
    def clear_credentials(self) -> bool:
        """Clear all stored credentials."""
        return self.auth_manager.clear_credentials()
    
    def get_credentials(self) -> Dict:
        """Get current credentials."""
        return self.auth_manager.get_credentials()
    
    def get_asset_roots(self) -> list:
        """Get Earth Engine asset roots."""
        if not self.initialized:
            raise EarthEngineError("Earth Engine not initialized")
        
        try:
            return ee.data.getAssetRoots()
        except Exception as e:
            raise EarthEngineError(f"Failed to get asset roots: {e}")
    
    def get_image_info(self, image_id: str) -> Dict:
        """Get information about an Earth Engine image."""
        if not self.initialized:
            raise EarthEngineError("Earth Engine not initialized")
        
        try:
            image = ee.Image(image_id)
            return {
                "id": image_id,
                "geometry": image.geometry().getInfo(),
                "properties": image.getInfo().get('properties', {})
            }
        except Exception as e:
            raise EarthEngineError(f"Failed to get image info: {e}")
    
    def validate_image_id(self, image_id: str) -> bool:
        """Validate if an image ID exists in Earth Engine."""
        if not self.initialized:
            return False
        
        try:
            image = ee.Image(image_id)
            # Try to get basic info to validate
            _ = image.geometry().bounds().getInfo()
            return True
        except Exception:
            return False

# Global Earth Engine manager instance
ee_manager = EarthEngineManager() 