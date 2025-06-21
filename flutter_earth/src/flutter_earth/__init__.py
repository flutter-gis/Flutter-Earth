"""Flutter Earth - A modern tool for downloading and processing satellite imagery."""

__version__ = "1.0.0"
__author__ = "Flutter Earth Project"
__email__ = "contact@flutterearth.org"

from .core.earth_engine_manager import EarthEngineManager
from .core.download_manager import DownloadManager
from .core.config_manager import ConfigManager
from .core.progress_tracker import ProgressTracker
from .gui.main_window import FlutterEarthMainWindow

__all__ = [
    "EarthEngineManager",
    "DownloadManager", 
    "ConfigManager",
    "ProgressTracker",
    "FlutterEarthMainWindow",
] 