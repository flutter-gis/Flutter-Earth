"""Flutter Earth Package."""

__version__ = "6.19.0"

# Import key components to be available at the package level
from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .processing import image_processor
from .gui import QmlGUILauncher

__all__ = [
    "ConfigManager",
    "EarthEngineManager",
    "DownloadManager",
    "image_processor",
    "QmlGUILauncher",
] 