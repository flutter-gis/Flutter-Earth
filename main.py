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
    'dateutil', 'ee', 'PySide6', 'PyQt6', 'tempfile', 'shutil', 'zipfile',
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
    from flutter_earth.src.flutter_earth.main import main as flutter_earth_main
    logging.info("Flutter Earth modules imported successfully")
except ImportError as e:
    logging.error(f"Error importing Flutter Earth modules: {e}")
    logging.error("Please ensure all required modules are in the correct directory structure")
    sys.exit(1)

def main():
    """Main entry point for Flutter Earth application."""
    try:
        logging.info("Starting Flutter Earth application...")
        # Run the main Flutter Earth application
        return flutter_earth_main()
    except Exception as e:
        logging.error(f"Failed to start Flutter Earth: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
