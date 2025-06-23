import os
import logging
from PySide6.QtCore import QObject, Signal
from .processing import SampleDownloadThread

class SampleManager(QObject):
    sample_download_progress = Signal(str, int, int)  # sample_key, current, total
    sample_download_finished = Signal(str, bool, str)  # sample_key, success, message_or_path
    error_occurred = Signal(str, str)  # user_message, log_message

    def __init__(self):
        super().__init__()
        self.active_threads = {}

    def queue_sample_download(self, sample_key, config, base_path, earth_engine, download_manager, callback=None):
        """Start a threaded sample download. Calls callback(sample_key, success, message_or_path) on finish.
        Emits sample_download_progress(sample_key, current, total) for progress updates.
        """
        if sample_key in self.active_threads:
            logging.warning(f"Sample download already in progress for {sample_key}")
            return
        thread = SampleDownloadThread(sample_key, config, base_path, earth_engine, download_manager)
        thread.sample_download_finished.connect(lambda key, success, msg: self._on_sample_download_finished(key, success, msg, callback))
        thread.error_occurred.connect(self.error_occurred.emit)
        thread.sample_download_progress.connect(lambda current, total: self.sample_download_progress.emit(sample_key, current, total))
        self.active_threads[sample_key] = thread
        thread.start()

    def _on_sample_download_finished(self, sample_key, success, message_or_path, callback):
        self.sample_download_finished.emit(sample_key, success, message_or_path)
        if callback:
            callback(sample_key, success, message_or_path)
        if sample_key in self.active_threads:
            del self.active_threads[sample_key]

    def validate_sample(self, sample_key, base_path):
        """Check if sample data exists and is valid."""
        sample_path = self.get_sample_path(sample_key, base_path)
        return os.path.exists(sample_path) and os.path.getsize(sample_path) > 1024

    def get_sample_path(self, sample_key, base_path):
        """Return the expected path for a sample file."""
        return os.path.join(base_path, f"{sample_key}_sample.tif") 