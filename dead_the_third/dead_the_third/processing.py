"""Image processing operations for Flutter Earth."""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import rasterio
from rasterio.merge import merge
from datetime import datetime
import requests
import ee

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams, TileDefinition, ProcessingResult
from .config import config_manager
from .earth_engine import ee_manager

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