"""Download manager for Flutter Earth."""
import os
import logging
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from PySide6.QtCore import QObject, Signal

from .earth_engine import EarthEngineManager
from .utils import (
    validate_bbox, validate_dates, create_output_dir,
    get_sensor_details, process_image, save_image,
    calculate_tiles, merge_tiles, cleanup_temp_files
)
from .download_worker import DownloadWorkerThread

class DownloadManager(QObject):
    """Manages satellite imagery downloads with advanced logic (now using DownloadWorkerThread for all processing). Emits error_occurred(user_message, log_message) for robust error handling."""
    progress_update = Signal(int, int)  # current, total
    tile_downloaded = Signal(int, str)  # tile_index, output_path
    error_occurred = Signal(str, str)   # user_message, log_message
    download_complete = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.earth_engine = EarthEngineManager()
        self.config = {}
        self.worker = None  # Reference to the current DownloadWorkerThread
        self.cancel_requested = False
        self.retry_count = 3
        self.timeout = 60  # seconds
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration."""
        self.config = config
        if not self.earth_engine.initialized:
            self.earth_engine.initialize()
        self.retry_count = config.get('retry_count', 3)
        self.timeout = config.get('timeout', 60)
    
    def request_cancel(self) -> None:
        """Request cancellation of current download."""
        self.cancel_requested = True
        if self.worker is not None:
            self.worker.request_cancel()
        self.logger.info("Download cancellation requested")
    
    def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a threaded download request using DownloadWorkerThread.
        Returns immediately; results are delivered via signals.
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
            Dict with 'started': True if thread started, else error info.
        """
        try:
            self.cancel_requested = False
            self._validate_params(params)
            output_dir = create_output_dir(params['output_dir'])
            tiles = calculate_tiles(
                params['area_of_interest'],
                self.config.get('tile_size', 1.0)
            )
            # Stop any previous worker
            if self.worker is not None and self.worker.isRunning():
                self.worker.request_cancel()
                self.worker.wait()
            # Start new worker thread
            self.worker = DownloadWorkerThread(
                tiles=tiles,
                params=params,
                earth_engine=self.earth_engine,
                config=self.config
            )
            self.worker.progress_update.connect(self.progress_update.emit)
            self.worker.tile_downloaded.connect(self.tile_downloaded.emit)
            self.worker.error_occurred.connect(self.error_occurred.emit)
            self.worker.download_complete.connect(self.download_complete.emit)
            self.worker.start()
            return {'started': True, 'message': 'Download started in background thread.'}
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            self.error_occurred.emit("Processing failed.", str(e))
            self.download_complete.emit(False, str(e))
            return {'started': False, 'message': str(e)}
    
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
    
    # Remove all old _process_tiles, _process_tile_with_retry, _process_tile, _merge_results, _validate_tile methods
    # ... existing code ... 