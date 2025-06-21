"""Sample data manager for Flutter Earth."""
import os
import logging
import json
import threading
import queue
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams
from .config import config_manager
from .earth_engine import ee_manager
from .download_manager import download_manager


class SampleManager:
    """Manages sample data downloads and configuration."""
    
    def __init__(self):
        """Initialize the sample manager."""
        self.logger = logging.getLogger(__name__)
        self.download_queue = queue.Queue()
        self.download_thread = None
        self.is_downloading = False
        self.current_download = None
        
        # Sample configurations
        self.sample_configs = {
            "jerusalem_sample": {
                "area_name": "Jerusalem",
                "sensor": "SENTINEL2",
                "year": 2024,
                "month": 6,
                "bbox": [35.2, 31.7, 35.3, 31.8],
                "output_subdir": "samples/jerusalem",
                "target_resolution": 10,
                "description": "High-resolution Sentinel-2 imagery of Jerusalem area"
            },
            "tel_aviv_sample": {
                "area_name": "Tel Aviv",
                "sensor": "LANDSAT_8",
                "year": 2024,
                "month": 6,
                "bbox": [34.7, 32.0, 34.8, 32.1],
                "output_subdir": "samples/tel_aviv",
                "target_resolution": 30,
                "description": "Landsat 8 imagery of Tel Aviv metropolitan area"
            },
            "haifa_sample": {
                "area_name": "Haifa",
                "sensor": "SENTINEL2",
                "year": 2024,
                "month": 5,
                "bbox": [34.9, 32.7, 35.0, 32.8],
                "output_subdir": "samples/haifa",
                "target_resolution": 10,
                "description": "Sentinel-2 imagery of Haifa Bay area"
            },
            "dead_sea_sample": {
                "area_name": "Dead Sea",
                "sensor": "LANDSAT_8",
                "year": 2024,
                "month": 4,
                "bbox": [35.4, 31.3, 35.5, 31.4],
                "output_subdir": "samples/dead_sea",
                "target_resolution": 30,
                "description": "Landsat 8 imagery of Dead Sea region"
            }
        }
        
        # Start download thread
        self._start_download_thread()
    
    def _start_download_thread(self) -> None:
        """Start the background download thread."""
        if self.download_thread is None or not self.download_thread.is_alive():
            self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
            self.download_thread.start()
    
    def _download_worker(self) -> None:
        """Background worker for processing download queue."""
        while True:
            try:
                # Get next download from queue
                download_item = self.download_queue.get(timeout=1)
                if download_item is None:  # Shutdown signal
                    break
                
                sample_key, callback = download_item
                self._download_sample_data(sample_key, callback)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in download worker: {e}")
    
    def queue_sample_download(
        self, 
        sample_key: str, 
        callback: Optional[Callable[[str, bool, str], None]] = None
    ) -> bool:
        """Queue a sample for download.
        
        Args:
            sample_key: Sample configuration key.
            callback: Optional callback function (sample_key, success, message).
        
        Returns:
            True if queued successfully, False otherwise.
        """
        if sample_key not in self.sample_configs:
            self.logger.error(f"Unknown sample key: {sample_key}")
            if callback:
                callback(sample_key, False, f"Unknown sample key: {sample_key}")
            return False
        
        # Check if already exists
        if self._sample_exists(sample_key):
            self.logger.info(f"Sample {sample_key} already exists")
            if callback:
                callback(sample_key, True, "Sample already exists")
            return True
        
        # Add to queue
        self.download_queue.put((sample_key, callback))
        self.logger.info(f"Queued sample download: {sample_key}")
        return True
    
    def _download_sample_data(
        self, 
        sample_key: str, 
        callback: Optional[Callable[[str, bool, str], None]] = None
    ) -> None:
        """Download sample data.
        
        Args:
            sample_key: Sample configuration key.
            callback: Optional callback function.
        """
        try:
            self.is_downloading = True
            self.current_download = sample_key
            
            config = self.sample_configs[sample_key]
            self.logger.info(f"Starting download of sample: {sample_key}")
            
            # Create output directory
            output_dir = os.path.join(
                config_manager.config.get('output_dir', 'flutter_earth_downloads'),
                config['output_subdir']
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # Check if Earth Engine is initialized
            if not ee_manager.initialized:
                if not ee_manager.initialize():
                    raise ProcessingError("Earth Engine not initialized")
            
            # Get image collection
            start_date = datetime(config['year'], config['month'], 1)
            end_date = datetime(config['year'], config['month'] + 1, 1) if config['month'] < 12 else datetime(config['year'] + 1, 1, 1)
            
            region = ee_manager.create_geometry_from_bbox(config['bbox'])
            collection = ee_manager.get_collection(
                config['sensor'],
                start_date,
                end_date,
                region=region
            )
            
            # Apply cloud cover filter
            collection = collection.filter(ee_manager.Filter.lte('CLOUD_COVER', 20))
            
            # Create mosaic
            mosaic = collection.mosaic()
            
            # Process image
            processed = ee_manager.process_image(mosaic, config['sensor'], {
                'cloud_mask': True,
                'resolution': config['target_resolution']
            })
            
            # Download
            output_filename = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
            output_path = os.path.join(output_dir, output_filename)
            
            success = download_manager.download_tile(
                processed,
                config['bbox'],
                output_path,
                0,
                config['sensor']
            )
            
            if success:
                self.logger.info(f"Successfully downloaded sample: {sample_key}")
                if callback:
                    callback(sample_key, True, output_path)
            else:
                raise ProcessingError("Download failed")
                
        except Exception as e:
            self.logger.error(f"Failed to download sample {sample_key}: {e}")
            if callback:
                callback(sample_key, False, str(e))
        finally:
            self.is_downloading = False
            self.current_download = None
    
    def _sample_exists(self, sample_key: str) -> bool:
        """Check if sample data already exists.
        
        Args:
            sample_key: Sample configuration key.
        
        Returns:
            True if sample exists, False otherwise.
        """
        if sample_key not in self.sample_configs:
            return False
        
        config = self.sample_configs[sample_key]
        output_dir = os.path.join(
            config_manager.config.get('output_dir', 'flutter_earth_downloads'),
            config['output_subdir']
        )
        output_filename = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
        output_path = os.path.join(output_dir, output_filename)
        
        return os.path.exists(output_path)
    
    def get_sample_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all sample configurations.
        
        Returns:
            Dictionary of sample configurations.
        """
        return self.sample_configs.copy()
    
    def get_sample_info(self, sample_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific sample.
        
        Args:
            sample_key: Sample configuration key.
        
        Returns:
            Sample configuration or None if not found.
        """
        if sample_key not in self.sample_configs:
            return None
        
        config = self.sample_configs[sample_key].copy()
        config['exists'] = self._sample_exists(sample_key)
        
        if config['exists']:
            output_dir = os.path.join(
                config_manager.config.get('output_dir', 'flutter_earth_downloads'),
                config['output_subdir']
            )
            output_filename = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
            output_path = os.path.join(output_dir, output_filename)
            config['file_path'] = output_path
            
            # Get file size
            try:
                config['file_size'] = os.path.getsize(output_path)
            except OSError:
                config['file_size'] = 0
        
        return config
    
    def get_sample_path(self, sample_key: str) -> Optional[str]:
        """Get the file path for a sample if it exists.
        
        Args:
            sample_key: Sample configuration key.
        
        Returns:
            File path if sample exists, None otherwise.
        """
        info = self.get_sample_info(sample_key)
        return info.get('file_path') if info else None
    
    def is_downloading_sample(self) -> bool:
        """Check if a sample is currently being downloaded.
        
        Returns:
            True if downloading, False otherwise.
        """
        return self.is_downloading
    
    def get_current_download(self) -> Optional[str]:
        """Get the currently downloading sample key.
        
        Returns:
            Sample key if downloading, None otherwise.
        """
        return self.current_download
    
    def get_queue_size(self) -> int:
        """Get the number of samples in the download queue.
        
        Returns:
            Number of queued downloads.
        """
        return self.download_queue.qsize()
    
    def clear_queue(self) -> None:
        """Clear the download queue."""
        while not self.download_queue.empty():
            try:
                self.download_queue.get_nowait()
            except queue.Empty:
                break
    
    def download_all_samples(self, callback: Optional[Callable[[str, bool, str], None]] = None) -> List[str]:
        """Queue all samples for download.
        
        Args:
            callback: Optional callback function for each download.
        
        Returns:
            List of queued sample keys.
        """
        queued_samples = []
        for sample_key in self.sample_configs:
            if self.queue_sample_download(sample_key, callback):
                queued_samples.append(sample_key)
        
        return queued_samples
    
    def download_missing_samples(self, callback: Optional[Callable[[str, bool, str], None]] = None) -> List[str]:
        """Queue only missing samples for download.
        
        Args:
            callback: Optional callback function for each download.
        
        Returns:
            List of queued sample keys.
        """
        queued_samples = []
        for sample_key in self.sample_configs:
            if not self._sample_exists(sample_key):
                if self.queue_sample_download(sample_key, callback):
                    queued_samples.append(sample_key)
        
        return queued_samples
    
    def delete_sample(self, sample_key: str) -> bool:
        """Delete a sample file.
        
        Args:
            sample_key: Sample configuration key.
        
        Returns:
            True if deleted successfully, False otherwise.
        """
        info = self.get_sample_info(sample_key)
        if not info or not info.get('exists'):
            return False
        
        try:
            os.remove(info['file_path'])
            self.logger.info(f"Deleted sample: {sample_key}")
            return True
        except OSError as e:
            self.logger.error(f"Failed to delete sample {sample_key}: {e}")
            return False
    
    def get_sample_statistics(self) -> Dict[str, Any]:
        """Get statistics about sample data.
        
        Returns:
            Dictionary with sample statistics.
        """
        total_samples = len(self.sample_configs)
        existing_samples = sum(1 for key in self.sample_configs if self._sample_exists(key))
        total_size = 0
        
        for sample_key in self.sample_configs:
            info = self.get_sample_info(sample_key)
            if info and info.get('exists'):
                total_size += info.get('file_size', 0)
        
        return {
            'total_samples': total_samples,
            'existing_samples': existing_samples,
            'missing_samples': total_samples - existing_samples,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'download_queue_size': self.get_queue_size(),
            'is_downloading': self.is_downloading
        }


# Global instance
sample_manager = SampleManager() 