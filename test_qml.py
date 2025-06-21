#!/usr/bin/env python3
"""Test script for QML interface."""

import sys
import logging
from pathlib import Path
import os

# Set the Fusion style for QtQuick Controls
os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

# Add the flutter_earth directory to the path
sys.path.insert(0, str(Path(__file__).parent / "flutter_earth"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from flutter_earth.src.flutter_earth.core.config_manager import ConfigManager
from flutter_earth.src.flutter_earth.core.earth_engine_manager import EarthEngineManager
from flutter_earth.src.flutter_earth.core.download_manager import DownloadManager
from flutter_earth.src.flutter_earth.core.progress_tracker import ProgressTracker
from flutter_earth.src.flutter_earth.gui.main_window import FlutterEarthMainWindow

def main():
    """Test the QML interface."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Flutter Earth Test")
        
        # Create managers
        config_manager = ConfigManager()
        earth_engine_manager = EarthEngineManager()
        download_manager = DownloadManager()
        progress_tracker = ProgressTracker()
        
        # Create main window
        main_window = FlutterEarthMainWindow(
            config_manager=config_manager,
            earth_engine_manager=earth_engine_manager,
            download_manager=download_manager,
            progress_tracker=progress_tracker
        )
        
        # Test bridge methods
        bridge = main_window.bridge
        
        # Test application info
        app_info = bridge.get_application_info()
        logger.info(f"Application info: {app_info}")
        
        # Test logging
        bridge.log_message("Test message from Python")
        
        # Test status update
        bridge.updateStatusBar.emit("Test status message")
        
        # Test progress update
        bridge.updateProgress.emit("overall", 0.5)
        bridge.updateProgress.emit("monthly", 0.8)
        
        # Test message dialog
        bridge.showMessage.emit("info", "Test Dialog", "This is a test message")
        
        logger.info("QML interface test completed successfully")
        
        # Keep the application running for a few seconds to see the interface
        QTimer.singleShot(5000, app.quit)
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 