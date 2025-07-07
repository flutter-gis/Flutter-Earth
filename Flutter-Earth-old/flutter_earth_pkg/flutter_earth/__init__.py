"""Flutter Earth Package."""

__version__ = "6.19.0"

# Import key components to be available at the package level
from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager

__all__ = [
    "ConfigManager",
    "EarthEngineManager",
    "DownloadManager",
] 