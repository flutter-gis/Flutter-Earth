"""Flutter Earth - A modern tool for downloading and processing satellite imagery."""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import subprocess

# List of all required packages (as used in this script)
REQUIRED_PACKAGES = [
    'numpy', 'rasterio', 'shapefile', 'folium', 'webview', 'requests',
    'dateutil', 'ee', 'PySide6', 'PySide6-Addons', 'tempfile', 'shutil', 'zipfile',
    'hashlib', 'concurrent.futures', 'warnings', 'contextlib', 'logging',
    'json', 'queue', 'threading', 'pathlib'
]

missing = []
for pkg in REQUIRED_PACKAGES:
    try:
        if pkg == 'shapefile':
            __import__('shapefile')
        elif pkg == 'dateutil':
            __import__('dateutil.relativedelta')
        elif pkg == 'concurrent.futures':
            __import__('concurrent.futures')
        elif pkg == 'pathlib':
            __import__('pathlib')
        else:
            __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f"Missing packages detected: {missing}. Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])
    print("All required packages are now installed. Please restart the program if you see any issues.")

# --- EARLY LOGGING SETUP (MUST BE FIRST, BEFORE ANY OTHER IMPORTS) ---
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"flutter_earth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Set up logging to file (overwrite) and console
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(log_format))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

# Log the start of the application
logging.info("=== Flutter Earth Application Started ===")
logging.info(f"Log file: {log_file}")

# --- END EARLY LOGGING SETUP ---

# Now import all other modules
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
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any, Union, Tuple

import ee
from ee import data as ee_data

# Import additional required modules
import tempfile
import shutil
import zipfile
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
from contextlib import contextmanager

# Import local modules
try:
    from PySide6.QtWidgets import QApplication
    from flutter_earth_pkg.flutter_earth.gui import QmlGUILauncher
    logging.info("Flutter Earth QML GUI modules imported successfully")
except ImportError as e:
    logging.error(f"Error importing Flutter Earth QML GUI modules: {e}")
    logging.error("Please ensure all required modules are in the correct directory structure and PySide6 is installed.")
    sys.exit(1)

os.environ["QT_QUICK_CONTROLS_STYLE"] = "Fusion"

def main():
    """Main entry point for Flutter Earth QML application."""
    try:
        logging.info("Initializing QApplication...")
        # QApplication must be created before QML engine
        # The QmlGUILauncher.launch() method will call app.exec()
        # Ensure that only one QApplication instance exists.
        app = QApplication.instance()
        if not app: # Create QApplication if it doesn't exist
            app = QApplication(sys.argv)

        logging.info("Starting Flutter Earth QML GUI application...")
        launcher = QmlGUILauncher()
        launcher.launch() # This will eventually call app.exec() and block.
        # No explicit return value needed here as app.exec() handles termination.
        # sys.exit() will be called by the QApplication event loop.
        # However, if launch() somehow returns (e.g. QML fails to load critically),
        # we might want to return an error code.
        # For now, assume launch() blocks or handles its own critical errors.
        return 0 # Or handle return code from launcher.launch if it's designed to return one
    except Exception as e:
        logging.exception(f"Critical error starting Flutter Earth QML GUI: {e}")
        return 1

if __name__ == "__main__":
    # sys.exit(main()) # main() will now block until app exits.
    # The QApplication's exec() call handles the exit code.
    # So, we just call main and let the Qt event loop manage the process lifetime.
    exit_code = main()
    sys.exit(exit_code)
