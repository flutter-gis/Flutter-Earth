"""Flutter Earth - A tool for downloading and processing satellite imagery."""
import os
import sys
import logging
import json
import time
import queue
import threading
import numpy
import rasterio
import shapefile
import folium
import webview
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any, Union, Tuple
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

import ee
from ee import data as ee_data

# Import additional required modules
from pathlib import Path
import tempfile
import shutil
import zipfile
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from contextlib import contextmanager

# Import local modules
try:
    from dead_the_third.types import (
        SatelliteDetails, ProcessingParams, TileDefinition,
        ProcessingResult, AppConfig, BBox, Coordinates,
        PolygonCoords, GeoJSON, Environment, Theme
    )
    from dead_the_third.earth_engine import EarthEngineManager
    from dead_the_third.config import ConfigManager
    from dead_the_third.errors import EarthEngineError, handle_errors
    from dead_the_third.utils import (
        validate_bbox, validate_dates, create_output_dir,
        get_sensor_details, process_image, save_image,
        calculate_tiles, merge_tiles, cleanup_temp_files
    )
    from dead_the_third.gui import FlutterEarthGUI
    from dead_the_third.download_manager import DownloadManager
    from dead_the_third.progress_tracker import ProgressTracker
except ImportError as e:
    print(f"Error importing local modules: {e}")
    print("Please ensure all required modules are in the same directory")
    sys.exit(1)

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"flutter_earth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress verbose logging from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Main application class
class FlutterEarth:
    """Main application class for Flutter Earth."""
    
    def __init__(self):
        """Initialize the Flutter Earth application."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.earth_engine = EarthEngineManager()
        self.download_manager = DownloadManager()
        self.progress_tracker = ProgressTracker()
        self.gui = None
        
        # Get configuration (already loaded in ConfigManager constructor)
        self.config = self.config_manager.config
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all application components."""
        try:
            # Initialize Earth Engine - will show auth dialog if needed
            if not self.earth_engine.initialized:
                # We'll initialize Earth Engine after GUI is created
                # so we can show the auth dialog if needed
                pass
            
            # Initialize download manager - convert AppConfig to dict
            config_dict = dict(self.config)
            self.download_manager.initialize(config_dict)
            
            # Initialize progress tracker
            self.progress_tracker.initialize()
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def start_gui(self):
        """Start the GUI application."""
        try:
            app = QtWidgets.QApplication(sys.argv)
            
            # Set application properties
            app.setApplicationName("Flutter Earth")
            app.setApplicationVersion("6.19")
            app.setOrganizationName("Flutter Earth Project")
            
            # Create and show GUI
            self.gui = FlutterEarthGUI(
                config_manager=self.config_manager,
                earth_engine=self.earth_engine,
                download_manager=self.download_manager,
                progress_tracker=self.progress_tracker
            )
            
            # Initialize Earth Engine after GUI is created (so we can show auth dialog)
            if not self.earth_engine.initialized:
                if not self.earth_engine.initialize(parent=self.gui):
                    self.logger.error("Failed to initialize Earth Engine")
                    # Continue anyway - user can retry later
            
            self.gui.show()
            
            # Start event loop
            sys.exit(app.exec_())
            
        except Exception as e:
            self.logger.error(f"Failed to start GUI: {e}")
            raise
    
    def run_cli(self, params: Dict[str, Any]):
        """Run the application in CLI mode."""
        try:
            self.logger.info("Starting CLI mode")
            
            # Validate parameters
            self._validate_cli_params(params)
            
            # Process the request
            result = self.download_manager.process_request(params)
            
            self.logger.info(f"Processing completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"CLI mode failed: {e}")
            raise

    def _validate_cli_params(self, params: Dict[str, Any]):
        """Validate CLI parameters."""
        if not params.get('area_of_interest'):
            raise ValueError("Area of interest is required")
        
        if not params.get('start_date') or not params.get('end_date'):
            raise ValueError("Start and end dates are required")
        
        if not params.get('sensor_name'):
            raise ValueError("Sensor name is required")
        
        if not params.get('output_dir'):
            raise ValueError("Output directory is required")

# Error handling and utilities
def handle_application_errors(func):
    """Decorator to handle application errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EarthEngineError as e:
            logging.error(f"Earth Engine error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
    return wrapper

@contextmanager
def temporary_directory():
    """Context manager for temporary directories."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# Main entry point
def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Flutter Earth application")
        
        # Create application instance
        app = FlutterEarth()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            # CLI mode
            if sys.argv[1] == '--cli':
                # Parse CLI parameters
                try:
                    # Convert coordinates to float list
                    coords = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None
                    
                    # Convert dates to datetime objects
                    start = datetime.strptime(sys.argv[3], "%Y-%m-%d") if len(sys.argv) > 3 else None
                    end = datetime.strptime(sys.argv[4], "%Y-%m-%d") if len(sys.argv) > 4 else None
                    
                    params = {
                        'area_of_interest': coords,
                        'start_date': start,
                        'end_date': end,
                        'sensor_name': sys.argv[5] if len(sys.argv) > 5 else None,
                        'output_dir': sys.argv[6] if len(sys.argv) > 6 else None
                    }
                    app.run_cli(params)
                except (ValueError, IndexError) as e:
                    logger.error(f"Invalid CLI parameters: {e}")
                    print("\nUsage: python flutter_earth_6-19.py --cli west,south,east,north YYYY-MM-DD YYYY-MM-DD sensor_name output_dir")
                    print("\nExample: python flutter_earth_6-19.py --cli -122.4,37.7,-122.3,37.8 2023-01-01 2023-12-31 LANDSAT_9 ./output")
                    sys.exit(1)
            else:
                logger.info("Starting GUI mode")
                app.start_gui()
        else:
            # GUI mode (default)
            logger.info("Starting GUI mode")
            app.start_gui()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)

# Run the application if this file is executed directly
if __name__ == "__main__":
    main()
