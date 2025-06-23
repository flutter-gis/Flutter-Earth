"""Main entry point for Flutter Earth application."""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import os

# Set Fusion style for QML
os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Fusion'

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from .core.config_manager import ConfigManager
from .core.earth_engine_manager import EarthEngineManager
from .core.download_manager import DownloadManager
from .core.progress_tracker import ProgressTracker
from .gui.main_window import FlutterEarthMainWindow
from .utils.logging_setup import setup_logging


class FlutterEarthApp:
    """Main application class for Flutter Earth."""
    
    def __init__(self):
        """Initialize the Flutter Earth application."""
        self.app: Optional[QApplication] = None
        self.main_window: Optional[FlutterEarthMainWindow] = None
        
        # Setup logging first
        self.logger = setup_logging()
        
        # Initialize core components
        self.config_manager = ConfigManager()
        self.earth_engine_manager = EarthEngineManager()
        self.download_manager = DownloadManager()
        self.progress_tracker = ProgressTracker()
        
        self.logger.info("Flutter Earth application initialized")
    
    def start(self) -> int:
        """Start the Flutter Earth application.
        
        Returns:
            Exit code for the application.
        """
        try:
            # Create Qt application
            self.app = QApplication(sys.argv)
            
            # Set application properties
            self.app.setApplicationName("Flutter Earth")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Flutter Earth Project")
            self.app.setOrganizationDomain("flutterearth.org")
            
            # Set application icon
            icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
            
            # Create main window
            self.main_window = FlutterEarthMainWindow(
                config_manager=self.config_manager,
                earth_engine_manager=self.earth_engine_manager,
                download_manager=self.download_manager,
                progress_tracker=self.progress_tracker
            )
            
            # Show main window
            self.main_window.show()
            
            # Initialize Earth Engine after GUI is shown
            QTimer.singleShot(100, self._initialize_earth_engine)
            
            self.logger.info("Flutter Earth GUI started successfully")
            
            # Start event loop
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Failed to start Flutter Earth: {e}")
            return 1
    
    def _initialize_earth_engine(self):
        """Initialize Earth Engine with proper error handling."""
        try:
            if not self.earth_engine_manager.is_initialized():
                success = self.earth_engine_manager.initialize(parent=self.main_window)
                if success:
                    self.logger.info("Earth Engine initialized successfully")
                else:
                    self.logger.warning("Earth Engine initialization failed - user can retry later")
        except Exception as e:
            self.logger.error(f"Error during Earth Engine initialization: {e}")


def main():
    """Main entry point for Flutter Earth."""
    app = FlutterEarthApp()
    return app.start()


if __name__ == "__main__":
    sys.exit(main()) 