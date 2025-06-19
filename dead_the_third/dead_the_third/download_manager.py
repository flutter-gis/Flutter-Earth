"""Download manager for Flutter Earth."""
import os
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .earth_engine import EarthEngineManager
from .utils import (
    validate_bbox, validate_dates, create_output_dir,
    get_sensor_details, process_image, save_image,
    calculate_tiles, merge_tiles, cleanup_temp_files
)

class DownloadManager:
    """Manages satellite imagery downloads."""
    
    def __init__(self):
        """Initialize download manager."""
        self.logger = logging.getLogger(__name__)
        self.earth_engine = EarthEngineManager()
        self.config = {}
        self.cancel_requested = False
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration."""
        self.config = config
        if not self.earth_engine.initialized:
            self.earth_engine.initialize()
    
    def request_cancel(self) -> None:
        """Request cancellation of current download."""
        self.cancel_requested = True
        self.logger.info("Download cancellation requested")
    
    def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a download request.
        
        Args:
            params: Processing parameters including:
                - area_of_interest: Bounding box or GeoJSON
                - start_date: Start date
                - end_date: End date
                - sensor_name: Name of satellite sensor
                - output_dir: Output directory
                - cloud_mask: Whether to apply cloud masking
                - max_cloud_cover: Maximum cloud cover percentage
        
        Returns:
            Processing results.
        """
        try:
            # Reset cancel flag
            self.cancel_requested = False
            
            # Validate parameters
            self._validate_params(params)
            
            # Create output directory
            output_dir = create_output_dir(params['output_dir'])
            
            # Calculate tiles
            tiles = calculate_tiles(
                params['area_of_interest'],
                self.config.get('tile_size', 1.0)
            )
            
            # Process tiles
            results = self._process_tiles(tiles, params)
            
            # Merge tiles if all successful
            if all(r['success'] for r in results) and not self.cancel_requested:
                self._merge_results(results, output_dir)
            
            return {
                'success': True,
                'message': "Processing completed successfully",
                'results': results
            }
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                'success': False,
                'message': str(e),
                'results': []
            }
    
    def _validate_params(self, params: Dict[str, Any]) -> None:
        """Validate processing parameters."""
        # Check required parameters
        required = ['area_of_interest', 'start_date', 'end_date', 
                   'sensor_name', 'output_dir']
        missing = [p for p in required if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
        # Validate bbox
        if not validate_bbox(params['area_of_interest']):
            raise ValueError("Invalid area of interest")
        
        # Validate dates
        params['start_date'], params['end_date'] = validate_dates(
            params['start_date'],
            params['end_date']
        )
        
        # Validate sensor
        sensor_details = get_sensor_details(params['sensor_name'])
        if not sensor_details:
            raise ValueError(f"Unknown sensor: {params['sensor_name']}")
    
    def _process_tiles(
        self,
        tiles: List[Dict[str, Any]],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Process multiple tiles in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.get('max_workers', 4)) as executor:
            future_to_tile = {
                executor.submit(self._process_tile, tile, params): tile
                for tile in tiles
            }
            
            for future in as_completed(future_to_tile):
                tile = future_to_tile[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing tile {tile['index']}: {e}")
                    results.append({
                        'success': False,
                        'message': str(e),
                        'tile_index': tile['index']
                    })
                
                if self.cancel_requested:
                    break
        
        return results
    
    def _process_tile(
        self,
        tile: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single tile."""
        try:
            # Get image collection
            collection = self.earth_engine.get_collection(
                params['sensor_name'],
                params['start_date'],
                params['end_date'],
                bbox=tile['bbox']
            )
            
            # Apply cloud cover filter
            if params.get('max_cloud_cover'):
                collection = collection.filter(
                    ee.Filter.lte('CLOUD_COVER', params['max_cloud_cover'])
                )
            
            # Create mosaic
            mosaic = collection.mosaic()
            
            # Process image
            processed = process_image(mosaic, params)
            
            # Save image
            output_path = os.path.join(
                params['output_dir'],
                f"tile_{tile['index']}.tif"
            )
            save_image(
                processed,
                output_path,
                tile['bbox'],
                get_sensor_details(params['sensor_name'])['resolution']
            )
            
            return {
                'success': True,
                'message': "Tile processed successfully",
                'tile_index': tile['index'],
                'output_path': output_path
            }
            
        except Exception as e:
            raise Exception(f"Failed to process tile {tile['index']}: {e}")
    
    def _merge_results(
        self,
        results: List[Dict[str, Any]],
        output_dir: str
    ) -> None:
        """Merge successful tile results."""
        try:
            # Get successful tile paths
            tile_paths = [
                r['output_path'] for r in results
                if r['success'] and os.path.exists(r['output_path'])
            ]
            
            if not tile_paths:
                return
            
            # Merge tiles
            output_path = os.path.join(output_dir, "merged_mosaic.tif")
            merge_tiles(tile_paths, output_path)
            
            # Cleanup individual tiles
            cleanup_temp_files(tile_paths)
            
        except Exception as e:
            self.logger.error(f"Failed to merge results: {e}")
            raise 