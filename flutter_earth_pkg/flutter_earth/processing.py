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
from PySide6.QtCore import QThread, Signal
import glob

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

class SampleDownloadThread(QThread):
    """
    QThread for downloading sample data with advanced logic (ported from FE Old.py).
    Emits sample_download_finished(str sample_key, bool success, str message_or_filepath) when done.
    Emits error_occurred(str user_message, str log_message) on error.
    Emits sample_download_progress(int current, int total) for progress updates.

    Usage Example:
        thread = SampleDownloadThread(sample_key, config, base_path, earth_engine, download_manager)
        thread.sample_download_finished.connect(your_slot)
        thread.error_occurred.connect(lambda user_msg, log_msg: ...)
        thread.sample_download_progress.connect(lambda current, total: ...)
        thread.start()
        # To cancel: thread.request_cancel()

    Best Practices:
        - Do not update GUI directly from this thread; use signals.
        - Always connect sample_download_finished, error_occurred, and sample_download_progress before starting.
        - Use request_cancel() to safely stop the thread.
    """
    sample_download_finished: Signal = Signal(str, bool, str)  # sample_key, success, message_or_filepath
    error_occurred: Signal = Signal(str, str)  # user_message, log_message
    sample_download_progress: Signal = Signal(int, int)  # current, total

    def __init__(self, sample_key: str, config: dict, base_path: str, earth_engine, download_manager):
        super().__init__()
        self.sample_key = sample_key
        self.config = config
        self.base_path = base_path
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.logger = logging.getLogger(__name__)
        self._cancel_requested = False

    def request_cancel(self):
        """Request cancellation of the sample download."""
        self._cancel_requested = True
        self.requestInterruption()
        self.logger.info(f"SampleDownloadThread: Cancellation requested for {self.sample_key}")

    def run(self):
        original_use_best_res = None
        original_target_res = None
        try:
            if self._cancel_requested or self.isInterruptionRequested():
                msg = f"SampleDownloadThread: Cancelled before start for {self.sample_key}"
                self.logger.info(msg)
                self.error_occurred.emit("Sample download cancelled before start.", msg)
                self.sample_download_finished.emit(self.sample_key, False, "Cancelled before start")
                return
            # EE init check
            if not (hasattr(self.earth_engine, 'initialized') and self.earth_engine.initialized):
                msg = "SampleDownloadThread: EE not initialized. Cannot download sample."
                self.logger.error(msg)
                self.error_occurred.emit("Earth Engine not initialized.", msg)
                self.sample_download_finished.emit(self.sample_key, False, "EE Not Initialized for Sample")
                return

            roi_geometry = ee.Geometry.Rectangle(self.config["bbox"])
            start_date_obj = datetime(self.config["year"], self.config["month"], 1)
            ee_start_date_str = ee.Date(start_date_obj.strftime('%Y-%m-%d'))
            from dateutil.relativedelta import relativedelta
            ee_end_date_str = ee.Date((start_date_obj + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d'))
            sensor_name = self.config["sensor"]
            self.logger.info(f"SampleDownloadThread: Building mosaic for {sensor_name} {self.config['year']}-{self.config['month']:02d}")

            # Get collection and filter
            image_collection = self.earth_engine.get_collection(sensor_name)
            filtered_collection = image_collection.filterDate(ee_start_date_str, ee_end_date_str).filterBounds(roi_geometry)
            self.sample_download_progress.emit(1, 4)  # Step 1: Collection filtered
            if filtered_collection.size().getInfo() == 0:
                msg = f"SampleDownloadThread: No images found for {sensor_name} in the period/ROI for sample."
                self.logger.warning(msg)
                self.error_occurred.emit("No images found for sample.", msg)
                self.sample_download_finished.emit(self.sample_key, False, f"No images for {sensor_name} ({self.sample_key}) sample")
                return

            # Masking and processing functions
            CLOUD_MASKS = getattr(self.earth_engine, 'CLOUD_MASKS', {})
            SENSOR_PROCESSORS = getattr(self.earth_engine, 'SENSOR_PROCESSORS', {})
            masking_function = CLOUD_MASKS.get(sensor_name, lambda img: img)
            processing_function = SENSOR_PROCESSORS.get(sensor_name, lambda img: img)

            def safe_processing_and_masking_sample(input_image):
                if self._cancel_requested or self.isInterruptionRequested():
                    raise Exception("Sample download cancelled during processing.")
                masked_image = masking_function(input_image)
                processed_image = processing_function(masked_image)
                return processed_image.set('fe_check_sample', 1)

            processed_collection_for_sample = filtered_collection.map(safe_processing_and_masking_sample).filter(ee.Filter.neq('fe_check_sample', None))
            self.sample_download_progress.emit(2, 4)  # Step 2: Masking/processing done
            if processed_collection_for_sample.size().getInfo() == 0:
                msg = f"SampleDownloadThread: All images masked out for {sensor_name} sample."
                self.logger.warning(msg)
                self.error_occurred.emit("All images masked out for sample.", msg)
                self.sample_download_finished.emit(self.sample_key, False, f"All images masked for {sensor_name} ({self.sample_key}) sample")
                return

            initial_mosaic_image = processed_collection_for_sample.median().clip(roi_geometry)
            all_bands_in_initial_mosaic = initial_mosaic_image.bandNames().getInfo()
            if not all_bands_in_initial_mosaic:
                msg = f"SampleDownloadThread: Initial median mosaic for {sensor_name} ({self.sample_key}) has no bands. Aborting sample."
                self.logger.warning(msg)
                self.error_occurred.emit("No bands found in mosaic.", msg)
                self.sample_download_finished.emit(self.sample_key, False, f"Initial mosaic no bands for {sensor_name} ({self.sample_key})")
                return

            selected_bands_for_download = []
            if sensor_name == "SENTINEL2":
                s2_optical_bands = [b for b in all_bands_in_initial_mosaic if b.startswith('B') and b not in ['B8A', 'B9']]
                tcc_bands = ['B4', 'B3', 'B2']
                if all(b in all_bands_in_initial_mosaic for b in tcc_bands):
                    test_image_tcc = initial_mosaic_image.select(tcc_bands)
                    if test_image_tcc.bandNames().getInfo():
                        selected_bands_for_download = tcc_bands
                        self.logger.info(f"SampleDownloadThread: Using TCC bands {tcc_bands} for {sensor_name} sample.")
                if not selected_bands_for_download and len(s2_optical_bands) >= 3:
                    potential_bands = s2_optical_bands[:3]
                    test_image_3opt = initial_mosaic_image.select(potential_bands)
                    if test_image_3opt.bandNames().getInfo():
                        selected_bands_for_download = potential_bands
                        self.logger.info(f"SampleDownloadThread: TCC failed/invalid. Using first 3 optical bands {selected_bands_for_download} for {sensor_name} sample.")
                if not selected_bands_for_download and len(s2_optical_bands) >= 1:
                    potential_band = [s2_optical_bands[0]]
                    test_image_1opt = initial_mosaic_image.select(potential_band)
                    if test_image_1opt.bandNames().getInfo():
                        selected_bands_for_download = potential_band
                        self.logger.info(f"SampleDownloadThread: 3-band failed/invalid. Using first optical band {selected_bands_for_download} for {sensor_name} sample (grayscale).")
            if not selected_bands_for_download:
                if len(all_bands_in_initial_mosaic) >= 3:
                    selected_bands_for_download = all_bands_in_initial_mosaic[:3]
                    self.logger.info(f"SampleDownloadThread: Using first 3 available bands {selected_bands_for_download} for {sensor_name} sample.")
                elif all_bands_in_initial_mosaic:
                    selected_bands_for_download = [all_bands_in_initial_mosaic[0]]
                    self.logger.info(f"SampleDownloadThread: Using first available band {selected_bands_for_download} for {sensor_name} sample (grayscale).")
            if not selected_bands_for_download:
                msg = f"SampleDownloadThread: Could not select any valid bands for download for {sensor_name} ({self.sample_key})"
                self.logger.error(msg)
                self.error_occurred.emit("No valid bands to download for sample.", msg)
                self.sample_download_finished.emit(self.sample_key, False, f"No valid bands to download for {sensor_name} ({self.sample_key})")
                return

            mosaic_image_for_download = initial_mosaic_image.select(selected_bands_for_download)
            self.logger.info(f"SampleDownloadThread: Mosaic built for {sensor_name} sample. Proceeding to download.")
            self.sample_download_progress.emit(3, 4)  # Step 3: Mosaic built
            output_filepath = os.path.join(self.base_path, f"{self.sample_key}_sample.tif")
            global APP_CONFIG
            APP_CONFIG = getattr(self, 'APP_CONFIG', {})
            original_use_best_res = APP_CONFIG.get('USE_BEST_RESOLUTION')
            original_target_res = APP_CONFIG.get('TARGET_RESOLUTION')
            APP_CONFIG['USE_BEST_RESOLUTION'] = False
            APP_CONFIG['TARGET_RESOLUTION'] = self.config.get("target_resolution", 30)
            if self._cancel_requested or self.isInterruptionRequested():
                msg = f"SampleDownloadThread: Cancelled before download for {self.sample_key}"
                self.logger.info(msg)
                self.error_occurred.emit("Sample download cancelled before download.", msg)
                self.sample_download_finished.emit(self.sample_key, False, "Cancelled before download")
                return
            download_successful = self.download_manager.download_tile(
                mosaic_image_for_download, self.config["bbox"], output_filepath, 0, sensor_name
            )
            self.sample_download_progress.emit(4, 4)  # Step 4: Download complete
            if self._cancel_requested or self.isInterruptionRequested():
                msg = f"SampleDownloadThread: Cancelled after download for {self.sample_key}"
                self.logger.info(msg)
                self.error_occurred.emit("Sample download cancelled after download.", msg)
                self.sample_download_finished.emit(self.sample_key, False, "Cancelled after download")
                return
            if download_successful:
                self.logger.info(f"SampleDownloadThread: Sample data downloaded successfully to {output_filepath}")
                self.sample_download_finished.emit(self.sample_key, True, output_filepath)
            else:
                msg = f"SampleDownloadThread: Failed to download sample data for {sensor_name} ({self.sample_key})."
                self.logger.error(msg)
                self.error_occurred.emit("Failed to download sample data.", msg)
                self.sample_download_finished.emit(self.sample_key, False, f"Download failed for {sensor_name} ({self.sample_key}) sample")
        except Exception as e:
            msg = f"SampleDownloadThread: Error during sample download for {self.sample_key}: {e}"
            self.logger.error(msg, exc_info=True)
            self.error_occurred.emit("Error during sample download.", msg)
            self.sample_download_finished.emit(self.sample_key, False, f"Error ({self.sample_key}): {str(e)[:100]}")
        finally:
            if original_use_best_res is not None:
                APP_CONFIG['USE_BEST_RESOLUTION'] = original_use_best_res
            if original_target_res is not None:
                APP_CONFIG['TARGET_RESOLUTION'] = original_target_res

# Global image processor instance
image_processor = ImageProcessor()

# --- Cloud Masking and Image Processing Functions (ported from FE Old.py) ---
def mask_clouds_landsat_sr_c2(image):
    # Bitmask for cloud and cloud shadow
    cloud_shadow_bit = 3
    clouds_bit = 5
    qa_pixel = image.select('QA_PIXEL')
    cloud_shadow = qa_pixel.bitwiseAnd(1 << cloud_shadow_bit).neq(0)
    clouds = qa_pixel.bitwiseAnd(1 << clouds_bit).neq(0)
    mask = cloud_shadow.Or(clouds).Not()
    return image.updateMask(mask)

def mask_clouds_sentinel2_sr(image):
    # Sentinel-2 QA60 band cloud mask
    qa60 = image.select('QA60')
    cloud_mask = qa60.bitwiseAnd(1 << 10).eq(0).And(qa60.bitwiseAnd(1 << 11).eq(0))
    return image.updateMask(cloud_mask)

def process_landsat_c2_sr(image):
    # Scale Landsat Collection 2 SR bands
    optical_bands = image.select(['SR_B.'])
    scaled = optical_bands.multiply(0.0000275).add(-0.2)
    return image.addBands(scaled, None, True)

def process_sentinel2_sr(image):
    # Scale Sentinel-2 SR bands
    optical_bands = image.select(['B.*'])
    scaled = optical_bands.multiply(0.0001)
    return image.addBands(scaled, None, True)

def process_era5_temp(image):
    # Convert ERA5-Land temperature from Kelvin to Celsius
    temp = image.select('temperature_2m').subtract(273.15)
    return image.addBands(temp.rename('temperature_2m_celsius'), None, True)

# Register functions for dynamic lookup
CLOUD_MASKS = {
    'LANDSAT_9': mask_clouds_landsat_sr_c2,
    'LANDSAT_8': mask_clouds_landsat_sr_c2,
    'SENTINEL2': mask_clouds_sentinel2_sr,
}
SENSOR_PROCESSORS = {
    'LANDSAT_9': process_landsat_c2_sr,
    'LANDSAT_8': process_landsat_c2_sr,
    'SENTINEL2': process_sentinel2_sr,
    'ERA5_LAND': process_era5_temp,
}

# --- Mosaic and Tile Stitching Functions (ported from FE Old.py) ---
def build_mosaic(tile_paths: list, output_mosaic_path: str) -> bool:
    """Merge multiple tile GeoTIFFs into a single mosaic GeoTIFF."""
    import rasterio
    from rasterio.merge import merge
    import numpy as np
    try:
        sources = [rasterio.open(p) for p in tile_paths if os.path.exists(p)]
        if not sources:
            logging.error("No valid tile files found for mosaic.")
            return False
        mosaic, transform = merge(sources)
        meta = sources[0].meta.copy()
        meta.update({
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": transform
        })
        with rasterio.open(output_mosaic_path, "w", **meta) as dest:
            dest.write(mosaic)
        for src in sources:
            src.close()
        logging.info(f"Mosaic created at {output_mosaic_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to build mosaic: {e}")
        return False

def stitch_mosaic(tile_dir: str, output_mosaic_path: str) -> bool:
    """Find all GeoTIFFs in a directory and merge them into a mosaic."""
    tile_paths = glob.glob(os.path.join(tile_dir, '*.tif'))
    if not tile_paths:
        logging.error(f"No .tif files found in {tile_dir} for stitching.")
        return False
    return build_mosaic(tile_paths, output_mosaic_path)

# --- Index Analysis Functions (ported from FE Old.py) ---
def calculate_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    ndvi = (nir - red) / (nir + red + 1e-10)
    return ndvi

def calculate_evi(red: np.ndarray, nir: np.ndarray, blue: np.ndarray) -> np.ndarray:
    # EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
    evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1.0)
    return evi

def run_index_analysis(input_raster_path: str, output_path: str, index_type: str, band_map: dict) -> bool:
    import rasterio
    try:
        with rasterio.open(input_raster_path) as src:
            bands = {}
            for key, band_idx in band_map.items():
                bands[key] = src.read(band_idx)
            profile = src.profile.copy()
        if index_type == 'NDVI':
            index_data = calculate_ndvi(bands['red'], bands['nir'])
        elif index_type == 'EVI':
            index_data = calculate_evi(bands['red'], bands['nir'], bands['blue'])
        else:
            logging.error(f"Unknown index type: {index_type}")
            return False
        profile.update(dtype=rasterio.float32, count=1)
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(index_data.astype(rasterio.float32), 1)
        logging.info(f"{index_type} written to {output_path}")
        return True
    except Exception as e:
        logging.error(f"Index analysis failed for {input_raster_path}: {e}")
        return False

def batch_index_analysis(input_files: list, output_dir: str, index_type: str, band_map: dict) -> list:
    results = []
    for input_path in input_files:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_dir, f"{base}_{index_type}.tif")
        success = run_index_analysis(input_path, output_path, index_type, band_map)
        results.append({'input': input_path, 'output': output_path, 'success': success})
    return results

INDEX_FUNCTIONS = {
    'NDVI': calculate_ndvi,
    'EVI': calculate_evi,
} 