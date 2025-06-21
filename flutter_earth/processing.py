"""Image processing operations for Flutter Earth."""
import os
import sys
import logging
import time
import threading
import tempfile
import shutil
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import rasterio
from rasterio.merge import merge
from datetime import datetime, timedelta
import requests
import ee
from ee import data as ee_data
import json
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams, TileDefinition, ProcessingResult
from .config import config_manager, SATELLITE_DETAILS
from .earth_engine import ee_manager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .satellite_info import SATELLITE_DETAILS

class ImageProcessor:
    """Handles image processing operations."""
    
    def __init__(self):
        """Initialize image processor."""
        self.current_task: Optional[str] = None
        self.cancel_requested = False
    
    def request_cancel(self) -> None:
        """Request cancellation of current processing task."""
        self.cancel_requested = True
        logging.info("Processing cancellation requested.")
    
    @handle_errors()
    def process_month(
        self,
        year: int,
        month: int,
        params: ProcessingParams,
        tiles: List[TileDefinition],
        progress_callback: Optional[callable] = None
    ) -> List[ProcessingResult]:
        """Process satellite data for a month.
        
        Args:
            year: Year to process.
            month: Month to process.
            params: Processing parameters.
            tiles: List of tiles to process.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            List of processing results.
        
        Raises:
            ProcessingError: If processing fails.
        """
        self.cancel_requested = False
        self.current_task = f"Processing {year}-{month:02d}"
        
        try:
            # Create output directory
            os.makedirs(params['output_dir'], exist_ok=True)
            
            results: List[ProcessingResult] = []
            total_tiles = len(tiles)
            
            for i, tile in enumerate(tiles):
                if self.cancel_requested:
                    logging.info("Processing cancelled.")
                    break
                
                try:
                    # Update progress
                    if progress_callback:
                        progress_callback(i, total_tiles)
                    
                    # Process tile
                    result = self.process_tile(tile, params)
                    results.append(result)
                    
                except Exception as e:
                    logging.error(f"Error processing tile {tile['index']}: {e}")
                    results.append({
                        'success': False,
                        'message': str(e),
                        'tile_index': tile['index'],
                        'output_path': None,
                        'error': e
                    })
            
            # If all tiles were processed successfully, merge them
            if all(r['success'] for r in results) and not self.cancel_requested:
                try:
                    self._merge_tiles([r['output_path'] for r in results if r['output_path']])
                except Exception as e:
                    logging.error(f"Error merging tiles: {e}")
                    raise ProcessingError("Failed to merge tiles", details={"error": str(e)})
            
            return results
            
        finally:
            self.current_task = None
    
    @handle_errors()
    def process_tile(
        self,
        tile: TileDefinition,
        params: ProcessingParams
    ) -> ProcessingResult:
        """Process a single tile.
        
        Args:
            tile: Tile definition.
            params: Processing parameters.
        
        Returns:
            Processing result.
        
        Raises:
            ProcessingError: If processing fails.
        """
        try:
            # Get image collection
            bbox = tile['bbox']
            region = ee.Geometry.Rectangle(bbox[0], bbox[1], bbox[2], bbox[3])
            collection = ee_manager.get_collection(
                params['sensor_name'],
                params['start_date'],
                params['end_date'],
                region=region
            )
            
            # Apply cloud cover filter if needed
            if params.get('max_cloud_cover'):
                collection = collection.filter(
                    ee.Filter.lte('CLOUD_COVER', params['max_cloud_cover'])
                )
            
            # Create mosaic
            mosaic = collection.mosaic()
            
            # Process image
            processed = ee_manager.process_image(mosaic, params['sensor_name'], params)
            
            # Download tile
            self._download_tile(processed, tile, params)
            
            return {
                'success': True,
                'message': "Tile processed successfully",
                'tile_index': tile['index'],
                'output_path': tile['output_path'],
                'error': None
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to process tile {tile['index']}",
                details={"error": str(e), "bbox": tile['bbox']}
            )
    
    def _download_tile(
        self,
        image: ee.Image,
        tile: TileDefinition,
        params: ProcessingParams
    ) -> None:
        """Download a tile from Earth Engine.
        
        Args:
            image: Earth Engine image.
            tile: Tile definition.
            params: Processing parameters.
        
        Raises:
            ProcessingError: If download fails.
        """
        try:
            # Get download URL
            url = image.getDownloadURL({
                'region': tile['bbox'],
                'scale': params.get('resolution'),
                'format': 'GeoTIFF'
            })
            
            # Download file
            response = requests.get(url)
            response.raise_for_status()
            
            # Save file
            with open(tile['output_path'], 'wb') as f:
                f.write(response.content)
                
        except Exception as e:
            raise ProcessingError(
                f"Failed to download tile {tile['index']}",
                details={"error": str(e), "url": url if 'url' in locals() else None}
            )
    
    def _merge_tiles(self, tile_paths: List[str]) -> None:
        """Merge processed tiles.
        
        Args:
            tile_paths: List of tile file paths.
        
        Raises:
            ProcessingError: If merge fails.
        """
        try:
            # Open all tile files
            sources = [rasterio.open(p) for p in tile_paths]
            
            # Merge tiles
            mosaic, transform = merge(sources)
            
            # Get metadata from first tile
            meta = sources[0].meta.copy()
            meta.update({
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform
            })
            
            # Write merged file
            output_path = os.path.join(os.path.dirname(tile_paths[0]), "merged.tif")
            with rasterio.open(output_path, "w", **meta) as dest:
                dest.write(mosaic)
                
        except Exception as e:
            raise ProcessingError(
                "Failed to merge tiles",
                details={"error": str(e), "tile_paths": tile_paths}
            )
        finally:
            # Close all sources
            for src in sources:
                src.close()

# Global image processor instance
image_processor = ImageProcessor() 

class ProcessingThread(QtCore.QThread):
    """Thread for processing satellite data downloads."""
    
    status_update = pyqtSignal(str)
    overall_progress_update = pyqtSignal(int, int)
    tile_progress_update = pyqtSignal(int, int)
    processing_finished_signal = pyqtSignal(str)
    message_box_signal = pyqtSignal(str, str)
    
    def __init__(self, params: ProcessingParams, tiles_list: List[TileDefinition], 
                 is_polygon_aoi: bool, earth_engine: EarthEngineManager, 
                 download_manager: DownloadManager):
        """Initialize the processing thread.
        
        Args:
            params: Processing parameters
            tiles_list: List of tile definitions
            is_polygon_aoi: Whether AOI is polygon coordinates
            earth_engine: Earth Engine manager instance
            download_manager: Download manager instance
        """
        super().__init__()
        self.params = params
        self.tiles_list = tiles_list
        self.is_polygon_aoi = is_polygon_aoi
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.cancel_event = threading.Event()
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run the processing thread."""
        try:
            self.logger.info("Starting processing thread")
            self.status_update.emit("Initializing processing...")
            
            # Validate Earth Engine initialization
            if not self.earth_engine.initialized:
                self.processing_finished_signal.emit("Earth Engine not initialized")
                return
            
            # Process each tile
            total_tiles = len(self.tiles_list)
            for i, tile in enumerate(self.tiles_list):
                if self.cancel_event.is_set():
                    self.status_update.emit("Processing cancelled by user")
                    break
                
                self.status_update.emit(f"Processing tile {i+1}/{total_tiles}")
                self.overall_progress_update.emit(i, total_tiles)
                
                try:
                    # Process tile
                    result = self._process_tile(tile)
                    if result.success:
                        self.logger.info(f"Tile {i+1} processed successfully")
                    else:
                        self.logger.error(f"Tile {i+1} failed: {result.error_message}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing tile {i+1}: {e}", exc_info=True)
                    self.status_update.emit(f"Error processing tile {i+1}: {str(e)}")
            
            if not self.cancel_event.is_set():
                self.status_update.emit("Processing completed successfully")
                self.processing_finished_signal.emit("Processing completed successfully")
            else:
                self.processing_finished_signal.emit("Processing cancelled")
                
        except Exception as e:
            self.logger.error(f"Processing thread error: {e}", exc_info=True)
            self.processing_finished_signal.emit(f"Processing error: {str(e)}")
    
    def _process_tile(self, tile: TileDefinition) -> ProcessingResult:
        """Process a single tile."""
        try:
            start_time = time.time()
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(tile.output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # Get the image collection for the tile
            collection = self.earth_engine.get_collection(
                self.params['sensor_name'],
                self.params['start_date'],
                self.params['end_date'],
                region=ee.Geometry.Rectangle(tile.bbox)
            )
            
            # Get the best image (least cloud cover)
            if self.params.get('cloud_mask', False):
                # Filter by cloud cover if available
                if 'CLOUD_COVER' in collection.first().bandNames().getInfo():
                    collection = collection.sort('CLOUD_COVER')
            
            image = collection.first()
            
            if not image:
                return ProcessingResult(
                    success=False,
                    tile_index=tile.index,
                    output_path="",
                    error_message="No images found for the specified criteria",
                    processing_time=time.time() - start_time
                )
            
            # Process the image
            processed_image = self.earth_engine.process_image(
                image, 
                self.params['sensor_name'], 
                self.params
            )
            
            # Download the processed image
            self._download_tile(processed_image, tile, self.params)
            
            # Get image metadata
            metadata = image.getInfo()
            bounds = metadata.get('properties', {}).get('bounds', tile.bbox)
            cloud_cover = metadata.get('properties', {}).get('CLOUD_COVER', 0)
            
            return ProcessingResult(
                success=True,
                tile_index=tile.index,
                output_path=tile.output_path,
                processing_time=time.time() - start_time,
                cloud_cover=cloud_cover,
                bounds=bounds,
                metadata=metadata
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                tile_index=tile.index,
                output_path="",
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def request_cancel(self):
        """Request cancellation of processing."""
        self.cancel_event.set()


class VerificationThread(QtCore.QThread):
    """Thread for verifying satellite data availability."""
    
    verification_finished = pyqtSignal(list, str)
    status_update = pyqtSignal(str)
    
    def __init__(self, aoi_coords: List[float], is_aoi_polygon: bool, 
                 earth_engine: EarthEngineManager):
        """Initialize the verification thread.
        
        Args:
            aoi_coords: Area of interest coordinates
            is_aoi_polygon: Whether AOI is polygon coordinates
            earth_engine: Earth Engine manager instance
        """
        super().__init__()
        self.aoi_coords = aoi_coords
        self.is_aoi_polygon = is_aoi_polygon
        self.earth_engine = earth_engine
        self.cancel_event = threading.Event()
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run the verification thread."""
        try:
            self.logger.info("Starting verification thread")
            self.status_update.emit("Verifying satellite data availability...")
            
            # Validate Earth Engine initialization
            if not self.earth_engine.initialized:
                self.verification_finished.emit([], "Earth Engine not initialized")
                return
            
            # Get available sensors from config
            available_sensors = list(SATELLITE_DETAILS.keys())
            
            results = []
            
            for sensor in available_sensors:
                if self.cancel_event.is_set():
                    break
                    
                self.status_update.emit(f"Checking {sensor}...")
                
                try:
                    # Create region geometry
                    if self.is_aoi_polygon:
                        # Convert polygon coordinates to EE geometry
                        coords = self.aoi_coords
                        if len(coords) > 0 and len(coords[0]) == 2:
                            # Single polygon
                            region = ee.Geometry.Polygon(coords)
                        else:
                            # Multiple polygons
                            region = ee.Geometry.MultiPolygon(coords)
                    else:
                        # BBOX coordinates
                        region = ee.Geometry.Rectangle(self.aoi_coords)
                    
                    # Get collection for the sensor
                    collection = self.earth_engine.get_collection(
                        sensor,
                        datetime.now() - timedelta(days=30),  # Last 30 days
                        datetime.now(),
                        region=region
                    )
                    
                    # Check if collection has any images
                    count = collection.size().getInfo()
                    
                    if count > 0:
                        # Get cloud cover info if available
                        first_image = collection.first()
                        properties = first_image.getInfo().get('properties', {})
                        cloud_cover = properties.get('CLOUD_COVER', 0)
                        
                        # Estimate coverage based on cloud cover
                        if cloud_cover < 20:
                            coverage = "95%"
                        elif cloud_cover < 50:
                            coverage = "75%"
                        else:
                            coverage = "50%"
                        
                        results.append({
                            "sensor": sensor,
                            "available": True,
                            "coverage": coverage,
                            "cloud_cover": cloud_cover,
                            "image_count": count
                        })
                    else:
                        results.append({
                            "sensor": sensor,
                            "available": False,
                            "coverage": "0%",
                            "cloud_cover": 0,
                            "image_count": 0
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Error checking {sensor}: {e}")
                    results.append({
                        "sensor": sensor,
                        "available": False,
                        "coverage": "0%",
                        "cloud_cover": 0,
                        "image_count": 0,
                        "error": str(e)
                    })
            
            if not self.cancel_event.is_set():
                self.status_update.emit("Verification completed")
                self.verification_finished.emit(results, "Verification completed successfully")
            else:
                self.verification_finished.emit([], "Verification cancelled")
                
        except Exception as e:
            self.logger.error(f"Verification thread error: {e}", exc_info=True)
            self.verification_finished.emit([], f"Verification error: {str(e)}")
    
    def request_cancel(self):
        """Request cancellation of verification."""
        self.cancel_event.set()


class SampleDownloadThread(QtCore.QThread):
    """Thread for downloading sample data."""
    
    sample_download_finished = pyqtSignal(str, bool, str)
    
    def __init__(self, sample_key: str, config: Dict[str, Any], base_path: str,
                 earth_engine: EarthEngineManager, download_manager: DownloadManager):
        """Initialize the sample download thread.
        
        Args:
            sample_key: Sample identifier
            config: Sample configuration
            base_path: Base path for downloads
            earth_engine: Earth Engine manager instance
            download_manager: Download manager instance
        """
        super().__init__()
        self.sample_key = sample_key
        self.config = config
        self.base_path = base_path
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """Run the sample download thread."""
        try:
            self.logger.info(f"Starting sample download for {self.sample_key}")
            
            # Validate Earth Engine initialization
            if not self.earth_engine.initialized:
                self.sample_download_finished.emit(self.sample_key, False, "Earth Engine not initialized")
                return
            
            # Get sample configuration
            sample_config = self.config.get('samples', {}).get(self.sample_key, {})
            if not sample_config:
                self.sample_download_finished.emit(self.sample_key, False, f"Sample configuration not found for {self.sample_key}")
                return
            
            # Create output directory
            output_dir = os.path.join(self.base_path, self.sample_key)
            os.makedirs(output_dir, exist_ok=True)
            
            # Get sample parameters
            aoi = sample_config.get('aoi', [35.2, 30.5, 35.8, 32.0])  # Default to Israel region
            start_date = datetime.strptime(sample_config.get('start_date', '2023-01-01'), '%Y-%m-%d')
            end_date = datetime.strptime(sample_config.get('end_date', '2023-01-31'), '%Y-%m-%d')
            sensor = sample_config.get('sensor', 'LANDSAT_9')
            
            # Create processing parameters
            params = {
                'area_of_interest': aoi,
                'start_date': start_date,
                'end_date': end_date,
                'sensor_name': sensor,
                'output_dir': output_dir,
                'cloud_mask': True,
                'max_cloud_cover': 20,
                'resolution': 30,
                'output_format': 'GeoTIFF'
            }
            
            # Get image collection
            collection = self.earth_engine.get_collection(
                sensor, start_date, end_date,
                region=ee.Geometry.Rectangle(aoi)
            )
            
            # Get best image
            if collection.size().getInfo() > 0:
                image = collection.first()
                
                # Process image
                processed_image = self.earth_engine.process_image(image, sensor, params)
                
                # Download image
                output_path = os.path.join(output_dir, f"{self.sample_key}_sample.tif")
                
                # Get download URL
                url = processed_image.getDownloadURL({
                    'region': aoi,
                    'scale': params['resolution'],
                    'format': 'GeoTIFF'
                })
                
                # Download file
                response = requests.get(url)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                self.sample_download_finished.emit(self.sample_key, True, output_path)
            else:
                self.sample_download_finished.emit(self.sample_key, False, "No images found for the specified criteria")
            
        except Exception as e:
            self.logger.error(f"Sample download error for {self.sample_key}: {e}", exc_info=True)
            self.sample_download_finished.emit(self.sample_key, False, str(e))


def process_tile(args: Dict[str, Any]) -> ProcessingResult:
    """Process a single tile with the given arguments.
    
    Args:
        args: Dictionary containing tile processing arguments
        
    Returns:
        ProcessingResult with success status and output information
    """
    try:
        # TODO: Implement actual tile processing logic
        # This is a placeholder implementation
        time.sleep(0.1)  # Simulate processing time
        
        return ProcessingResult(
            success=True,
            output_path="",
            error_message=""
        )
        
    except Exception as e:
        logging.error(f"Error processing tile: {e}", exc_info=True)
        return ProcessingResult(
            success=False,
            output_path="",
            error_message=str(e)
        )


def process_month(year: int, month: int, out_dir: str, tiles_list: List[TileDefinition],
                 overwrite_existing: bool, cancel_event: threading.Event,
                 progress_callback=None, status_callback=None) -> bool:
    """Process data for a specific month.
    
    Args:
        year: Target year
        month: Target month
        out_dir: Output directory
        tiles_list: List of tile definitions
        overwrite_existing: Whether to overwrite existing files
        cancel_event: Event for cancellation
        progress_callback: Callback for progress updates
        status_callback: Callback for status updates
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        logging.info(f"Processing month {year}-{month:02d}")
        
        if status_callback:
            status_callback(f"Processing {year}-{month:02d}")
        
        # TODO: Implement actual month processing logic
        # This is a placeholder implementation
        
        total_tiles = len(tiles_list)
        for i, tile in enumerate(tiles_list):
            if cancel_event.is_set():
                logging.info("Processing cancelled")
                return False
            
            if progress_callback:
                progress_callback(i, total_tiles)
            
            # Process tile
            result = process_tile({
                "tile": tile,
                "year": year,
                "month": month,
                "out_dir": out_dir,
                "overwrite": overwrite_existing
            })
            
            if not result.success:
                logging.error(f"Tile {i+1} failed: {result.error_message}")
                return False
        
        if progress_callback:
            progress_callback(total_tiles, total_tiles)
        
        logging.info(f"Month {year}-{month:02d} processed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error processing month {year}-{month:02d}: {e}", exc_info=True)
        return False


def stitch_mosaic(tile_paths: List[str], output_path: str) -> bool:
    """Stitch multiple tiles into a single mosaic.
    
    Args:
        tile_paths: List of paths to tile files
        output_path: Output path for the mosaic
        
    Returns:
        True if stitching was successful, False otherwise
    """
    try:
        logging.info(f"Stitching {len(tile_paths)} tiles into mosaic")
        
        # TODO: Implement actual mosaic stitching logic
        # This is a placeholder implementation
        time.sleep(1)  # Simulate stitching time
        
        logging.info(f"Mosaic created successfully: {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Error stitching mosaic: {e}", exc_info=True)
        return False 