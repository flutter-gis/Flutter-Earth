from PySide6.QtCore import QThread, Signal
import logging
import os
from typing import List, Dict, Any
import ee  # <-- Add this import for ee.Filter

class DownloadWorkerThread(QThread):
    """
    QThread for processing satellite imagery downloads in the background.
    Emits signals for progress, tile completion, errors, and overall completion.
    Usage:
        thread = DownloadWorkerThread(tiles, params, earth_engine, config)
        thread.progress_update.connect(...)
        thread.tile_downloaded.connect(...)
        thread.error_occurred.connect(lambda user_msg, log_msg: ...)
        thread.download_complete.connect(...)
        thread.start()
    """
    progress_update = Signal(int, int)  # current, total
    tile_downloaded = Signal(int, str)  # tile_index, output_path
    error_occurred = Signal(str, str)   # user_message, log_message
    download_complete = Signal(bool, str)  # success, message

    def __init__(self, tiles: List[Dict[str, Any]], params: Dict[str, Any], earth_engine, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.tiles = tiles
        self.params = params
        self.earth_engine = earth_engine
        self.config = config
        self.cancel_requested = False
        self.logger = logging.getLogger(__name__)
        self.retry_count = config.get('retry_count', 3)

    def request_cancel(self):
        self.cancel_requested = True
        self.logger.info("DownloadWorkerThread: Cancellation requested.")

    def run(self):
        results = []
        total = len(self.tiles)
        try:
            for i, tile in enumerate(self.tiles):
                if self.cancel_requested:
                    self.logger.info("DownloadWorkerThread: Cancelled by user.")
                    break
                result = self._process_tile_with_retry(tile)
                results.append(result)
                if result['success']:
                    self.tile_downloaded.emit(tile['index'], result.get('output_path', ''))
                else:
                    user_msg = f"Tile {tile['index']} failed: {result.get('message', 'Unknown error')}"
                    log_msg = str(result.get('error', result.get('message', 'Unknown error')))
                    self.error_occurred.emit(user_msg, log_msg)
                self.progress_update.emit(i + 1, total)
            # Merge results if all successful and not cancelled
            if all(r['success'] for r in results) and not self.cancel_requested:
                try:
                    self._merge_results(results)
                except Exception as e:
                    self.logger.error(f"Error merging results: {e}", exc_info=True)
                    self.error_occurred.emit("Failed to merge results.", str(e))
                    self.download_complete.emit(False, f"Merging failed: {e}")
                    return
            if self.cancel_requested:
                self.download_complete.emit(False, "Download cancelled by user.")
            elif all(r['success'] for r in results):
                self.download_complete.emit(True, "Processing completed successfully")
            else:
                self.download_complete.emit(False, "Some tiles failed to process.")
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            self.error_occurred.emit("Processing failed.", str(e))
            self.download_complete.emit(False, str(e))

    def _process_tile_with_retry(self, tile: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(1, self.retry_count + 1):
            if self.cancel_requested:
                return {
                    'success': False,
                    'message': 'Download cancelled by user.',
                    'tile_index': tile['index']
                }
            try:
                result = self._process_tile(tile)
                if result['success']:
                    if self._validate_tile(result['output_path']):
                        return result
                    else:
                        raise Exception(f"Tile {tile['index']} failed validation after download.")
                else:
                    raise Exception(result.get('message', 'Unknown error'))
            except Exception as e:
                self.logger.warning(f"Attempt {attempt} failed for tile {tile['index']}: {e}", exc_info=True)
                if attempt == self.retry_count:
                    return {
                        'success': False,
                        'message': f"Failed after {self.retry_count} attempts: {e}",
                        'tile_index': tile['index'],
                        'error': e
                    }
        return {
            'success': False,
            'message': f"Failed after {self.retry_count} attempts.",
            'tile_index': tile['index']
        }

    def _process_tile(self, tile: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Get image collection
            collection = self.earth_engine.get_collection(
                self.params['sensor_name'],
                self.params['start_date'],
                self.params['end_date'],
                bbox=tile['bbox']
            )
            # Apply cloud cover filter
            if self.params.get('max_cloud_cover'):
                collection = collection.filter(
                    ee.Filter.lte('CLOUD_COVER', self.params['max_cloud_cover'])
                )
            # Create mosaic
            mosaic = collection.mosaic()
            # Process image
            from .utils import process_image, save_image, get_sensor_details
            processed = process_image(mosaic, self.params)
            # Save image
            output_path = os.path.join(
                self.params['output_dir'],
                f"tile_{tile['index']}.tif"
            )
            resolution = get_sensor_details(self.params['sensor_name']).get('resolution', 30)
            save_image(processed, output_path, tile['bbox'], resolution)
            return {
                'success': True,
                'message': "Tile processed successfully",
                'tile_index': tile['index'],
                'output_path': output_path,
                'error': None
            }
        except Exception as e:
            self.logger.error(f"Error processing tile {tile['index']}: {e}", exc_info=True)
            return {
                'success': False,
                'message': str(e),
                'tile_index': tile['index'],
                'output_path': None,
                'error': e
            }

    def _validate_tile(self, file_path: str) -> bool:
        # Check file existence and size
        try:
            return os.path.exists(file_path) and os.path.getsize(file_path) > 1024
        except Exception:
            return False

    def _merge_results(self, results: List[Dict[str, Any]]):
        # Merge processed tiles (call existing merge_tiles)
        from .utils import merge_tiles
        output_dir = self.params['output_dir']
        tile_paths = [r['output_path'] for r in results if r['output_path']]
        output_path = os.path.join(output_dir, "merged_mosaic.tif")
        merge_tiles(tile_paths, output_path) 