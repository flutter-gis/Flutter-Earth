# Flutter Earth - Advanced GEE Downloader
# Version: 3.1.7 - Removed Interactive Authentication
# This version has all Tkinter and tkintermapview elements removed.
SCRIPT_VERSION = "3.1.7_no_tkinter"

import sys
import os
import logging
import subprocess # For package installation
import importlib.util # For checking package existence
import queue # Moved import earlier
from datetime import datetime, date
import shutil
import time
import concurrent.futures
import threading
import json
import base64
import socket
import re # For parsing resolution strings

# SciPy/ConvexHull related imports are removed.
SCIPY_AVAILABLE = False # Explicitly set to False as ConvexHull is removed
logging.info("ConvexHull functionality has been removed.")

try:
    from shapely.geometry import Polygon as ShapelyPolygon, box as ShapelyBox
except ImportError:
    ShapelyPolygon, ShapelyBox = None, None
    logging.warning("Shapely library not found. Advanced polygon tiling will be affected.")

# ==============================================
#        GLOBAL LOG QUEUE & EARLY LOGGING SETUP
# ==============================================
log_queue = queue.Queue()

class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """
    def __init__(self, logger_instance, log_level=logging.INFO):
        self.logger = logger_instance
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass # No-op

ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.INFO) # Set level on ROOT_LOGGER
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s', datefmt='%H:%M:%S')

# --- Fallback console logging ---
# This ensures that if file logging fails, messages still go to the console.
# This handler is added BEFORE attempting file logging.
_stderr_handler = logging.StreamHandler(sys.__stderr__) # Use original stderr
_stderr_handler.setFormatter(LOG_FORMATTER)
ROOT_LOGGER.addHandler(_stderr_handler)
ROOT_LOGGER.info("Root logger configured with StreamHandler to sys.__stderr__.") # Test message

# QueueHandler will be fully set up after its definition.
# For now, sys.stdout/stderr redirection will happen after that.

# ==============================================
#        EARLY FILE LOGGING SETUP (with enhanced debug prints)
# ==============================================
def setup_main_app_logging(output_dir_for_log, initial_setup=False):
    """Configures file logging for the main application process."""
    # These prints go to original stderr, good for debugging the logger itself.
    print(f"[DEBUG_LOGGER] setup_main_app_logging called. Output dir: {output_dir_for_log}, initial_setup: {initial_setup}", file=sys.__stderr__)

    # Remove any existing file handlers to avoid duplicate logs or writing to old files
    # Store file handlers to remove them after iteration to avoid modifying list while iterating
    handlers_to_remove = []
    for handler in ROOT_LOGGER.handlers:
        if isinstance(handler, logging.FileHandler):
            # Only remove if it's not the _stderr_handler (though that's a StreamHandler)
            # or if we are re-configuring for a *new* file.
            # For simplicity, if we are setting up a new FileHandler, remove all old FileHandlers.
            handlers_to_remove.append(handler)
            
    for handler in handlers_to_remove:
        print(f"[DEBUG_LOGGER] Removing existing FileHandler for: {getattr(handler, 'baseFilename', 'Unknown')}", file=sys.__stderr__)
        ROOT_LOGGER.removeHandler(handler)
        try:
            handler.close() # Ensure the file is closed
        except Exception as e_close:
            print(f"[DEBUG_LOGGER] Error closing handler: {e_close}", file=sys.__stderr__)


    try:
        os.makedirs(output_dir_for_log, exist_ok=True)
        print(f"[DEBUG_LOGGER] Ensured directory exists: {output_dir_for_log}", file=sys.__stderr__)
    except Exception as e_mkdir:
        print(f"[DEBUG_LOGGER] ERROR creating directory {output_dir_for_log}: {e_mkdir}", file=sys.__stderr__)
        ROOT_LOGGER.error(f"Failed to create log directory {output_dir_for_log}: {e_mkdir}") # Log via ROOT_LOGGER too
        return None # Indicate failure

    log_file_path = os.path.join(output_dir_for_log, "flutter_earth_processing_log.txt")
    print(f"[DEBUG_LOGGER] Attempting to create log file at: {log_file_path}", file=sys.__stderr__)

    # Use 'w' for overwrite on initial setup, 'a' for append otherwise (e.g., if called again by processing)
    file_mode = 'w' if initial_setup else 'a'
    try:
        file_handler = logging.FileHandler(log_file_path, mode=file_mode, encoding='utf-8')
        file_handler.setFormatter(LOG_FORMATTER)
        ROOT_LOGGER.addHandler(file_handler)
        # This message should be the first in the file if 'w' mode, or appended if 'a'
        ROOT_LOGGER.info(f"File logging configured (Mode: {file_mode}). Output to: {log_file_path}")
        file_handler.flush() # Explicitly flush after the first message
        print(f"[DEBUG_LOGGER] File handler added and flushed for {log_file_path}. First log message sent via ROOT_LOGGER.", file=sys.__stderr__)
    except Exception as e_fh:
        print(f"[DEBUG_LOGGER] ERROR creating/adding FileHandler for {log_file_path}: {e_fh}", file=sys.__stderr__)
        ROOT_LOGGER.error(f"Failed to create/add FileHandler for {log_file_path}: {e_fh}", exc_info=True)
        if 'file_handler' in locals() and file_handler: # Check if file_handler was assigned
            ROOT_LOGGER.removeHandler(handler)
            handler.close() # Ensure the file is closed
            try: file_handler.close()
            except: pass
        return None # Indicate failure
    return log_file_path

# ==============================================
#        DEFAULT CONFIGURATION (Early definitions needed for logging)
# ==============================================
# Define DEFAULT_OUTPUT_DIR early as it's needed for initial log setup
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), 'flutter_earth_downloads')

# ==============================================
#        PACKAGE CHECKING AND INSTALLATION
# ==============================================

def check_and_install_packages():
    """Checks for required packages and attempts to install them if missing."""
    required_packages = {
        "requests": "requests",
        "rasterio": "rasterio",
        "numpy": "numpy",
        "googleapiclient": "google-api-python-client",
        "google_auth_httplib2": "google-auth-httplib2",
        "google_auth_oauthlib": "google-auth-oauthlib",
        "ee": "earthengine-api",
        "dateutil": "python-dateutil",
        # "tkintermapview": "tkintermapview", # Removed
        "scipy": "scipy",
        "PIL": "Pillow",   # Pillow is a general imaging library, might be used by Qt or Matplotlib. Kept.
        "folium": "folium",
        "webview": "pywebview", # pywebview is listed but not explicitly used in the QtPy part. Kept for now.
        "shapely": "shapely",
        "matplotlib": "matplotlib",
        "qtpy": "qtpy",
        "PyQt5": "PyQt5", # Base Qt5 bindings
        "pyqtgraph": "pyqtgraph", # For native image viewing (though DataViewerTab switched to Matplotlib)
        "PyQtWebEngine": "PyQtWebEngine", # For QWebEngineView
        "shapefile": "pyshp" # For reading/writing shapefiles
        ,"overpass": "overpass" # For Overpass API queries
    }
    missing_packages_to_install = []
    
    logging.info("Starting package check...")
    for import_name, install_name in required_packages.items():
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                # pyqtgraph is no longer a direct dependency for DataViewerTab, but kept as optional
                if import_name == "pyqtgraph":
                    logging.info(f"Optional package '{import_name}' not found. Matplotlib is used for DataViewerTab.")
                    # continue # Don't strictly require it if Matplotlib is the primary viewer
                missing_packages_to_install.append(install_name)
            else:
                logging.debug(f"Package '{import_name}' found.")
        except Exception as e:
            logging.error(f"Error checking for package {import_name}: {e}")
            if install_name not in missing_packages_to_install:
                missing_packages_to_install.append(install_name)

    if missing_packages_to_install:
        logging.info(f"Attempting to install: {', '.join(missing_packages_to_install)}")
        # Filter out pyqtgraph if it ended up in the list due to an error but is not strictly needed
        # This logic might be too aggressive if pyqtgraph is intended as a fallback or for other features.
        # For now, let's keep it in the install list if it was deemed missing.
        # missing_packages_to_install = [pkg for pkg in missing_packages_to_install if pkg != "pyqtgraph"]
        # if not missing_packages_to_install: # If only pyqtgraph was missing
        #     logging.info("All strictly required packages appear to be installed.")
        #     return True
            
        print(f"\nFlutter Earth: Missing packages: {', '.join(missing_packages_to_install)}")
        print("Attempting installation... This may take a moment.")
        
        pip_ok = True
        for pkg_name in missing_packages_to_install:
            try:
                print(f"Installing {pkg_name}...")
                install_command = [sys.executable, "-m", "pip", "install", pkg_name]
                if pkg_name == "earthengine-api" or "google-api" in pkg_name or "google-auth" in pkg_name:
                    install_command.extend(["--upgrade", "--no-cache-dir"])
                subprocess.check_call(install_command)
                logging.info(f"Successfully installed {pkg_name}.")
                print(f"Successfully installed {pkg_name}.")
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install {pkg_name}. Error: {e}")
                print(f"ERROR: Failed to install {pkg_name}.")
                # Don't set pip_ok to False for individual package failures, allow others to try.
                # pip_ok = False 
            except FileNotFoundError:
                logging.error("'pip' not found. Ensure Python & pip are in PATH.")
                print("ERROR: 'pip' not found. Cannot install packages.")
                pip_ok = False # This is a critical failure for installation.
                break
        
        print("Package installation attempts complete.\n")
        if not pip_ok: # If pip itself was not found.
            return False
        # Re-check after installation attempt to confirm.
        # This is a simplified check; a full re-check might be needed for robustness.
        # For now, assume installation was successful if pip ran without error for all.
    else:
        logging.info("All required packages appear to be installed.")
    return True

# --- Early call to setup file logging ---
# This ensures that package checks and subsequent operations are logged to file from the start.
# The log file will be in the DEFAULT_OUTPUT_DIR and will be overwritten on each startup.
ROOT_LOGGER.info("Attempting initial file logging setup...") # Log this attempt via console handler
log_file_path_initial = setup_main_app_logging(DEFAULT_OUTPUT_DIR, initial_setup=True)

if not log_file_path_initial:
    # This message will go to sys.__stderr__ via the _stderr_handler
    ROOT_LOGGER.critical(f"Initial file logging setup FAILED. Log file may not be created in {DEFAULT_OUTPUT_DIR}. Check console for [DEBUG_LOGGER] messages.")
    # The print to sys.__stderr__ is also kept for belt-and-suspenders
    print(f"[CRITICAL DEBUG_LOGGER] Initial file logging setup FAILED. Log file may not be created in {DEFAULT_OUTPUT_DIR}. Check console for [DEBUG_LOGGER] messages.", file=sys.__stderr__)
    # The script will continue, but file logging might not work.
else:
    ROOT_LOGGER.info(f"Initial file logging setup successful. Log file: {log_file_path_initial}")
if not check_and_install_packages():
    print("Critical error during package check or installation. Flutter Earth may not run correctly.")
    # Consider exiting if critical packages are missing, though the script tries to proceed.

# --- Third-party imports moved here, after package check ---
import ee
import requests
import rasterio
from rasterio.merge import merge
from dateutil.relativedelta import relativedelta
import numpy
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import shapefile # For reading shapefiles
import matplotlib.patches # For drawing vector polygons
import overpass # For querying OpenStreetMap data

# Ensure numpy is available (it's listed in required_packages)
# import numpy # Already imported above

try:
    from shapely.geometry import Polygon as ShapelyPolygon, box as ShapelyBox
except ImportError:
    ShapelyPolygon, ShapelyBox = None, None # This was already here, kept for consistency
    logging.warning("Shapely library (post-check) not found. Advanced polygon tiling will be affected.")


# --- FLUTTERSHY THEME (Adapted for QtPy) ---
# These were specifically for the QtPy part and are kept.
FLUTTERSHY_COLORS = {
    "BG_MAIN": "#FEFEFA",
    "BG_FRAME": "#FFF5FA",
    "TEXT_COLOR": "#5D4037",
    "INPUT_BG": "#FFFCF5",
    "INPUT_FG": "#5D4037",
    "ACCENT_BORDER": "#E0B0E0",
    "PLACEHOLDER_FG": "#A98F84",
    "BUTTON_PINK_BG": "#FFC0CB",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFFFE0",
    "BUTTON_YELLOW_FG": "#8D6E63",
    "BUTTON_YELLOW_HOVER": "#FFFFF0",
    "BUTTON_LAVENDER_BG": "#F0E6FF",
    "BUTTON_LAVENDER_FG": "#4A4A6A",
    "BUTTON_LAVENDER_HOVER": "#E8DFFF",
    "PROGRESS_BG": "#FFF0F0",
    "PROGRESS_FG_OVERALL": "#FFC0CB", # Pink
    "PROGRESS_FG_MONTHLY": "#FFF41E", # Light Yellow (corrected from #FFF41E0)
    "CALENDAR_HEADER_BG": "#FFF5FA",
    "TEXT_LIGHT": "#755C51",
    "LOG_BG": "#FFFCF5",
    "LOG_FG": "#5D4037",
    "MAP_BUTTON_FG": "#8D6E63"
}

NIGHT_MODE_COLORS = {
    "BG_MAIN": "#1E1E1E",
    "BG_FRAME": "#252526",
    "TEXT_COLOR": "#D4D4D4",
    "INPUT_BG": "#3C3C3C",
    "INPUT_FG": "#D4D4D4",
    "ACCENT_BORDER": "#007ACC", # A nice blue accent
    "PLACEHOLDER_FG": "#7A7A7A",
    "BUTTON_PINK_BG": "#007ACC", # Using the blue accent for "pink"
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#4A4A4A", # Darker grey for "yellow"
    "BUTTON_YELLOW_FG": "#D4D4D4",
    "BUTTON_YELLOW_HOVER": "#5A5A5A",
    "BUTTON_LAVENDER_BG": "#333333", # Dark grey for "lavender"
    "BUTTON_LAVENDER_FG": "#D4D4D4",
    "BUTTON_LAVENDER_HOVER": "#404040",
    "PROGRESS_BG": "#2A2A2A",
    "PROGRESS_FG_OVERALL": "#007ACC",
    "PROGRESS_FG_MONTHLY": "#1E90FF", # Lighter blue (DodgerBlue)
    "CALENDAR_HEADER_BG": "#252526",
    "TEXT_LIGHT": "#A0A0A0",
    "LOG_BG": "#1E1E1E", "LOG_FG": "#D4D4D4", "MAP_BUTTON_FG": "#D4D4D4"
}

FLUTTERSHY_TEXTS = { # These are for the QtPy part
    "window_title_main": "💖 Flutter Earth - Gentle GEE Downloader 💖",
    "start_date_label": "Start Date for our adventure 🗓️:",
    "end_date_label": "End Date for our adventure 🗓️:",
    "output_dir_label": "A cozy place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like a blooming flower 🌷:",
    "log_console_label": "Whispers from the Earth Engine 👇:",
    "run_button": "🌸 Begin Download 🌸",
    "cancel_button": "🍃 Pause Gently 🍂",
    "run_button_processing": "Working softly... 🐾",
    "cancel_button_cancelling": "Pausing gently...",

    "verify_button_text_base": "Check Satellite Friends",
    "verify_satellites_button_icon": "🛰️",
    "verify_satellites_button_verifying": "Asking friends... 🛰️",
    "verify_satellites_status_start": "Checking in with our satellite friends...",
    "verify_satellites_status_done": "All satellite friends are accounted for! (Or see notes below)",
    "verify_satellites_title": "🦋 Checking In With Satellite Friends 🦋",

    "status_bar_ready": "Ready for some lovely downloads! ✨",
    "status_bar_ee_init_fail": "Oh dear, EE couldn't connect. Some magic might be missing.",
    "status_bar_ee_init_ok": "Earth Engine is all set! Ready for a magical journey! ✨",
    "status_bar_input_error_prefix": "Oopsie! Something's not quite right: ",
    "status_bar_processing_started": "Our gentle download has begun...",
    "status_bar_cancellation_requested": "Pausing our journey for now...",
    "status_bar_processing_finished": "Our adventure is complete! Check your treasures.",
    "sensor_priority_label": "Sensor Friends Order 💖:",
    "sensor_priority_edit_button": "Arrange Friends...",
    "sensor_priority_dialog_title": "Arrange Our Sensor Friends 🌸",
    "sensor_priority_instruction": "Drag & drop to change order, or use buttons. Topmost is most preferred!",
    "sensor_priority_add_button": "Invite Friend...",
    "sensor_priority_remove_button": "Say Goodbye",
    "sensor_priority_up_button": "Up ↑",
    "sensor_priority_down_button": "Down ↓",
    "about_dialog_title": "About Flutter Earth 🦋",
    "about_dialog_tagline": "Gently downloading GEE data with QtPy!",
    "help_menu_text": "&Help",
    "about_menu_item_text": "&About Flutter Earth",
    "themes_menu_text": "&Themes", # New
    "sensor_priority_add_dialog_title": "Invite a New Sensor Friend!",
    "sensor_priority_add_dialog_label": "Which friend to invite to our list?",
    "cleanup_tiles_label": "Tidy up individual tiles after stitching? 🧹:",
    "use_highest_resolution_cb": "Use Highest Sensor Resolution ✨", # Keep this for checkbox
    "tools_menu_label": "&Tools 🛠️", # New for Tools menu
    "satellite_info_action_label": "🛰️ Satellite Info", # New for menu action
    "post_processing_action_label": "📊 Post Processing", # New for menu action
    # vector_download_action_label will reuse vector_download_tab_title
    "application_guide_menu_item_text": "Application Guide 📖", # New text for the guide
    "target_resolution_auto_tooltip": "Resolution automatically set by 'Use Highest Sensor Resolution' option.",
    "target_resolution_manual_tooltip": "Target resolution in meters for the output mosaic (e.g., 10, 30).",
    "vector_download_tab_title": "🗺️ Vector Data Download",
    "vector_source_label": "Data Source (e.g., URL, Overpass Query):",
    "vector_type_label": "Source Type:",
    "vector_output_dir_label": "Save Vector Data To:",
    "vector_format_label": "Output Format:",
    "vector_start_download_button": "📥 Download Vector Data",
    "vector_osm_feature_type_label": "OSM Feature Type:",
    "vector_status_fetching": "Fetching vector data from {source}...",
    "vector_status_processing": "Processing vector data...",
    "vector_status_saving": "Saving vector data as {format} to {filename}...",
    "vector_status_success": "Vector data saved: {filename}",
    "vector_status_fail": "Vector data download/processing failed: {error}",
    "vector_aoi_missing_error": "AOI is required for Overpass API queries.",
    "vector_overpass_geojson_only_msg": "For Overpass API, data is saved as GeoJSON. Please convert to other formats manually if needed."
}

QT_FLUTTER_FONT_FAMILY = "Segoe UI"
QT_FLUTTER_FONT_SIZE_NORMAL = "11pt"

# ==============================================
#        DEFAULT CONFIGURATION
# ==============================================
DEFAULT_THEME_QT = "Fluttershy" 
EE_PROJECT = 'ee-jakobnewmandead' # Replace with your GEE Project if needed
DEFAULT_TILING_METHOD = "degree"
DEFAULT_NUM_SUBSECTIONS = 100
DEFAULT_BBOX_STR = '35.2, 30.5, 35.8, 32.0' # Example BBOX (Israel region)
DEFAULT_START_DATE = (datetime.now() - relativedelta(months=6)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), 'flutter_earth_downloads')
DEFAULT_TILE_SIZE_DEG = 0.02
DEFAULT_TARGET_RESOLUTION = 30
DEFAULT_MAX_WORKERS = 4
DEFAULT_MAX_TILE_RETRIES = 2
DEFAULT_MIN_VALID_PIXELS_TILE_VALIDATION = 100
DEFAULT_DOWNLOAD_TIMEOUT = 300
DEFAULT_USE_BEST_RESOLUTION = False
DEFAULT_CLEANUP_TILES = True
DEFAULT_OVERLAP_DEG = 0.002 # Moved here to keep related defaults together, though not strictly needed for the fix
DEFAULT_SENSOR_PRIORITY_ORDER = [
    'LANDSAT_9', 'LANDSAT_8', 'SENTINEL2', 'LANDSAT_7',
    'LANDSAT_5', 'LANDSAT_4', 'ERA5_TEMP', 'VIIRS', 'MODIS'
]
SENSOR_TIMELINE = {
    'LANDSAT_9': ('2021-09-27', None), 'LANDSAT_8': ('2013-04-11', None),
    'LANDSAT_7': ('1999-04-15', '2022-04-06'), 'LANDSAT_5': ('1984-03-01', '2013-06-05'),
    'LANDSAT_4': ('1982-07-16', '1993-12-14'), 'SENTINEL2': ('2015-06-23', None),
    'VIIRS': ('2012-01-18', None), 'MODIS': ('2000-02-24', None),
    'ERA5_TEMP': ('1950-01-01', None), # Adjusted ERA5 start based on common availability
}
DATA_COLLECTIONS = {
    'LANDSAT_9': ["LANDSAT/LC09/C02/T1_L2"], 'LANDSAT_8': ["LANDSAT/LC08/C02/T1_L2"],
    'LANDSAT_7': ["LANDSAT/LE07/C02/T1_L2"], 'LANDSAT_5': ["LANDSAT/LT05/C02/T1_L2"],
    'LANDSAT_4': ["LANDSAT/LT04/C02/T1_L2"], 'SENTINEL2': ["COPERNICUS/S2_SR_HARMONIZED"],
    'VIIRS': ["NOAA/VIIRS/001/VNP09GA"], 'MODIS': ["MODIS/061/MOD09GA"], # Using MOD09GA as example
    'ERA5_TEMP': ["ECMWF/ERA5_LAND/DAILY_AGGR"], # ERA5 Land for higher resolution temperature
}
SATELLITE_DETAILS = {
    'LANDSAT_9': {"description": "Operational Land Imager 2 (OLI-2) and Thermal Infrared Sensor 2 (TIRS-2). Successor to Landsat 8.", "type": "Optical/Thermal", "resolution_nominal": "15m (Pan), 30m (MS), 100m (Thermal)", "revisit_interval": "16 days", "common_uses": "Land cover, change detection, vegetation, water, thermal mapping.", "use_categories": ["Land Cover", "Change Detection", "Vegetation Health", "Water Resources", "Agriculture"]},
    'LANDSAT_8': {"description": "Operational Land Imager (OLI) and Thermal Infrared Sensor (TIRS).", "type": "Optical/Thermal", "resolution_nominal": "15m (Pan), 30m (MS), 100m (Thermal)", "revisit_interval": "16 days", "common_uses": "Land cover, change detection, vegetation, water, thermal mapping.", "use_categories": ["Forest Monitoring", "Coastal Zones", "Urban Studies", "Glacier Change", "Burn Severity"]},
    'LANDSAT_7': {"description": "Enhanced Thematic Mapper Plus (ETM+). Scan Line Corrector (SLC) failed in 2003, resulting in data gaps for L1 products. L2 products are often gap-filled.", "type": "Optical/Thermal", "resolution_nominal": "15m (Pan), 30m (MS), 60m (Thermal)", "revisit_interval": "16 days", "common_uses": "Historical land studies, gap-filled products often used.", "use_categories": ["Historical Analysis", "Land Use Change", "Environmental Monitoring", "Geology", "Natural Hazards"]},
    'LANDSAT_5': {"description": "Thematic Mapper (TM). Longest-operating Earth-observing satellite.", "type": "Optical/Thermal", "resolution_nominal": "30m (MS), 120m (Thermal)", "revisit_interval": "16 days", "common_uses": "Historical land cover and change analysis.", "use_categories": ["Long-term Trends", "Deforestation", "Resource Management", "Ecosystem Dynamics", "Drought Monitoring"]},
    'LANDSAT_4': {"description": "Thematic Mapper (TM). Predecessor to Landsat 5.", "type": "Optical/Thermal", "resolution_nominal": "30m (MS), 120m (Thermal)", "revisit_interval": "16 days", "common_uses": "Early historical land studies.", "use_categories": ["Baseline Data", "Early Remote Sensing", "Land Management", "Hydrology", "Soil Mapping"]},
    'SENTINEL2': {"description": "Copernicus Sentinel-2 (MSI - MultiSpectral Instrument). Twin satellites (S2A & S2B). SR Harmonized product used.", "type": "Optical", "resolution_nominal": "10m, 20m, 60m (depending on band)", "revisit_interval": "~5 days (combined constellation at equator)", "common_uses": "Vegetation, land cover, agriculture, coastal monitoring, emergency mapping.", "use_categories": ["Precision Agriculture", "Forest Health", "Water Quality", "Disaster Response", "Urban Expansion"]},
    'VIIRS': {"description": "Visible Infrared Imaging Radiometer Suite (on Suomi NPP and JPSS satellites). Surface Reflectance (VNP09GA).", "type": "Optical/Thermal", "resolution_nominal": "375m, 750m (depending on band)", "revisit_interval": "Daily (global)", "common_uses": "Weather, climate, oceanography, vegetation, fire detection, aerosols, nighttime lights.", "use_categories": ["Active Fires", "Nighttime Lights", "Sea Surface Temp.", "Aerosol Optical Depth", "Snow/Ice Cover"]},
    'MODIS': {"description": "Moderate Resolution Imaging Spectroradiometer (on Terra and Aqua satellites). Surface Reflectance (MOD09GA/MYD09GA).", "type": "Optical/Thermal", "resolution_nominal": "250m, 500m, 1km (depending on band)", "revisit_interval": "Daily (global, combined)", "common_uses": "Global dynamics, land/ocean/atmosphere products, vegetation indices, surface temperature, cloud/aerosol properties.", "use_categories": ["Global Vegetation Index", "Cloud Masking", "Ocean Productivity", "Atmospheric Correction", "Land Surface Temp."]},
    'ERA5_TEMP': {"description": "ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis. Provides mean 2m air temperature.", "type": "Reanalysis Model", "resolution_nominal": "0.1° x 0.1° (~9km)", "revisit_interval": "Daily (model output)", "common_uses": "Climate analysis, historical weather assessment, environmental modeling.", "use_categories": ["Climate Trends", "Weather Analysis", "Agricultural Modeling", "Hydrological Studies", "Environmental Science"]},
}
SATELLITE_CATEGORIES = {
    "Landsat Program": ['LANDSAT_9', 'LANDSAT_8', 'LANDSAT_7', 'LANDSAT_5', 'LANDSAT_4'],
    "Copernicus Sentinel": ['SENTINEL2'],
    "NASA EOS & NOAA": ['MODIS', 'VIIRS'],
    "Gridded Climate Products": ['ERA5_TEMP']
}
APP_CONFIG = {
    'TILE_SIZE_DEG': DEFAULT_TILE_SIZE_DEG, 'OVERLAP_DEG': DEFAULT_OVERLAP_DEG,
    'TARGET_RESOLUTION': DEFAULT_TARGET_RESOLUTION, 'MAX_WORKERS': DEFAULT_MAX_WORKERS,
    'MAX_TILE_RETRIES': DEFAULT_MAX_TILE_RETRIES,
    'MIN_VALID_PIXELS_TILE_VALIDATION': DEFAULT_MIN_VALID_PIXELS_TILE_VALIDATION,
    'DOWNLOAD_TIMEOUT': DEFAULT_DOWNLOAD_TIMEOUT, 'CLEANUP_TILES': DEFAULT_CLEANUP_TILES,
    'SENSOR_PRIORITY_ORDER': list(DEFAULT_SENSOR_PRIORITY_ORDER),
    'theme': DEFAULT_THEME_QT, # Theme preference stored here
    'output_dir': DEFAULT_OUTPUT_DIR,
    'start_date': DEFAULT_START_DATE, 'end_date': DEFAULT_END_DATE, 'overwrite': False,
    'TILING_METHOD': DEFAULT_TILING_METHOD,
    'NUM_SUBSECTIONS': DEFAULT_NUM_SUBSECTIONS,
    'USE_BEST_RESOLUTION': DEFAULT_USE_BEST_RESOLUTION,
    'bbox_str': DEFAULT_BBOX_STR # Ensure bbox_str is part of APP_CONFIG from the start
}

ALL_SAMPLE_CONFIGS = {
    "AMAZON_RAINFOREST_L9": {
        "area_name": "AMAZON_RAINFOREST_L9",
        "bbox": [-55.25, -5.25, -54.75, -4.75], # Approx 0.5x0.5 deg area in Brazilian Amazon
        "year": 2023,
        "month": 7, # Drier season month
        "sensor": "LANDSAT_9",
        "target_resolution": 30,
        "output_subdir": "flutter_earth_sample_data",
    },
    "SAHARA_DESERT_L9": {
        "area_name": "SAHARA_DESERT_L9",
        "bbox": [1.75, 26.75, 2.25, 27.25], # Approx 0.5x0.5 deg area in Algerian Sahara (dunes)
        "year": 2023,
        "month": 4, # Spring, generally less extreme heat
        "sensor": "LANDSAT_9",
        "target_resolution": 30,
        "output_subdir": "flutter_earth_sample_data",
    },
    "HIMALAYAS_NEPAL_L9": {
        "area_name": "HIMALAYAS_NEPAL_L9",
        "bbox": [86.65, 27.65, 87.15, 28.15], # Approx 0.5x0.5 deg area near Mt. Everest, Nepal
        "year": 2023,
        "month": 10, # Post-monsoon, clearer skies
        "sensor": "LANDSAT_9",
        "target_resolution": 30,
        "output_subdir": "flutter_earth_sample_data",
    },
    "SIBERIAN_TAIGA_L9": {
        "area_name": "SIBERIAN_TAIGA_L9",
        "bbox": [104.5, 59.75, 105.5, 60.25], # Approx 1.0x0.5 deg area in Siberian Taiga, Russia
        "year": 2023,
        "month": 7, # Summer
        "sensor": "LANDSAT_9",
        "target_resolution": 30,
        "output_subdir": "flutter_earth_sample_data",
    },
    "GREAT_BARRIER_REEF_L9": {
        "area_name": "GREAT_BARRIER_REEF_L9",
        "bbox": [145.75, -17.25, 146.25, -16.75], # Approx 0.5x0.5 deg area over GBR, Australia
        "year": 2023,
        "month": 9, # Drier season, good visibility
        "sensor": "LANDSAT_9",
        "target_resolution": 30,
        "output_subdir": "flutter_earth_sample_data",
    }
}
DEFAULT_SAMPLE_KEY = "AMAZON_RAINFOREST_L9" # Updated default sample key

AVAILABLE_INDICES = {
    "NDVI": {"name": "Normalized Difference Vegetation Index", "bands_needed": ["NIR", "Red"], "formula_desc": "(NIR - Red) / (NIR + Red)"},
    "EVI": {"name": "Enhanced Vegetation Index", "bands_needed": ["NIR", "Red", "Blue"], "formula_desc": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)"},
    "SAVI": {"name": "Soil Adjusted Vegetation Index", "bands_needed": ["NIR", "Red"], "formula_desc": "((NIR - Red) / (NIR + Red + L)) * (1 + L) (L=0.5)"},
    "NDWI_Gao": {"name": "Normalized Difference Water Index (Gao)", "bands_needed": ["NIR", "SWIR1"], "formula_desc": "(NIR - SWIR1) / (NIR + SWIR1)"},
    "MNDWI_Xu": {"name": "Modified Normalized Difference Water Index (Xu)", "bands_needed": ["Green", "SWIR1"], "formula_desc": "(Green - SWIR1) / (Green + SWIR1)"},
    "NDBI": {"name": "Normalized Difference Built-up Index", "bands_needed": ["SWIR1", "NIR"], "formula_desc": "(SWIR1 - NIR) / (SWIR1 + NIR)"},
    # Add more as needed, ensure band names match GEE conventions or your processing pipeline
}
# Config file path (used by QtPy part if it implements config saving/loading)

THEMES = { # Dictionary to hold all theme color palettes
    "Fluttershy": FLUTTERSHY_COLORS,
    "Night Mode": NIGHT_MODE_COLORS
}

CONFIG_FILE_PATH = "flutter_earth_config.json"

# ==============================================
#        AUTHENTICATION AND INITIALIZATION
# ==============================================
def check_internet_connection():
    """Checks for basic internet connectivity."""
    try:
        # Try connecting to a reliable host (Google's DNS server)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        logging.debug("Internet connection check: Successful.")
        return True
    except OSError as e:
        logging.warning(f"Internet connection check failed: {e}")
        return False

def initialize_earth_engine_with_retry():
    """
    Attempts to initialize Earth Engine. If authentication is required,
    it logs the information and prompts the user via QMessageBox.
    Returns True on success, False on failure.
    """
    logging.info("Attempting Earth Engine initialization...")
    # QtWidgets needs to be imported for QMessageBox
    # This import is deferred to avoid issues if QtPy is not yet fully available
    # or if this function is called from a non-GUI context initially.
    try:
        from qtpy import QtWidgets
    except ImportError:
        logging.error("QtPy.QtWidgets could not be imported for EE initialization messages.")
        # Fallback or re-raise might be needed if this is critical before GUI setup
        # For now, proceed, but QMessageBox won't work.
        QtWidgets = None # Ensure it's defined for later checks

    if not check_internet_connection():
        logging.error("Connection Error: No internet connection. Cannot initialize GEE.")
        if QtWidgets: # Check if QtWidgets was successfully imported
            QtWidgets.QMessageBox.critical(None, "Connection Error", "No internet connection. Cannot initialize GEE.")
        return False
    try:
        logging.info("Attempting EE initialization (high-volume)...")
        ee.Initialize(project=EE_PROJECT, opt_url='https://earthengine-highvolume.googleapis.com')
        # Perform a simple operation to confirm initialization
        ee.data.getAssetRoots() # Throws error if not initialized
        logging.info("Earth Engine initialized successfully (high-volume).")
        return True
    except ee.EEException as e_hv:
        logging.warning(f"High-volume EE initialization failed: {e_hv}. Trying default endpoint.")
        try:
            logging.info("Attempting EE initialization (default)...")
            ee.Initialize(project=EE_PROJECT)
            ee.data.getAssetRoots()
            logging.info("Earth Engine initialized successfully (default).")
            return True
        except ee.EEException as e_def:
            logging.error(f"Default EE initialization also failed: {e_def}")
            err_str = str(e_def).lower()
            if "authenticate" in err_str or "oauth" in err_str or "credentials" in err_str:
                message = (
                    "Earth Engine initialization failed due to an authentication issue.\n"
                    "Please ensure you have authenticated with Google Earth Engine.\n"
                    "You can typically do this by running:\n"
                    "earthengine authenticate\n"
                    "in your terminal or command prompt, and then restart this application.\n"
                    f"Error details: {e_def}"
                )
                logging.error(message)
                if QtWidgets:
                    QtWidgets.QMessageBox.critical(None, "EE Authentication Required", message)
            else:
                err_msg = f"Could not initialize Earth Engine:\n{e_def}"
                logging.error(err_msg)
                if QtWidgets:
                    QtWidgets.QMessageBox.critical(None, "EE Initialization Failed", err_msg)
            return False
        except Exception as e_gen_def: # Catch other potential errors during default init
            logging.error(f"General error during default EE initialization: {e_gen_def}", exc_info=True)
            if QtWidgets:
                QtWidgets.QMessageBox.critical(None, "EE Initialization Error", f"A general error occurred during EE initialization:\n{e_gen_def}")
            return False
    except Exception as e_gen_hv: # Catch other potential errors during high-volume init
        logging.error(f"General error during high-volume EE initialization: {e_gen_hv}", exc_info=True)
        if QtWidgets:
            QtWidgets.QMessageBox.critical(None, "EE Initialization Error", f"A general error occurred during EE initialization:\n{e_gen_hv}")
        return False

# ==============================================
#        LOGGING (Main Application)
# ==============================================
class QueueHandler(logging.Handler):
    def __init__(self, log_queue_ref):
        super().__init__()
        self.log_queue = log_queue_ref
    def emit(self, record):
        self.log_queue.put(self.format(record))

queue_log_handler = QueueHandler(log_queue)
queue_log_handler.setFormatter(LOG_FORMATTER)
ROOT_LOGGER.addHandler(queue_log_handler)

# Redirect stdout and stderr after the QueueHandler is fully set up
# This part is kept as it's general Python logging redirection.
# The QtPy GUI will need its own mechanism to display logs from the queue.
sys.stdout = StreamToLogger(logging.getLogger('STDOUT'), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger('STDERR'), logging.ERROR)

logging.info("Initial logging configured. stdout and stderr redirected to queue.")

# ==============================================
#        CORE PROCESSING (Data and Mosaics)
# ==============================================

def get_best_resolution_for_sensor(sensor_name):
    """Extracts the best (numerically smallest) resolution in meters from SATELLITE_DETAILS."""
    details = SATELLITE_DETAILS.get(sensor_name)
    if not details:
        logging.warning(f"No details found for sensor {sensor_name} to determine best resolution.")
        return None
    res_str = details.get("resolution_nominal")
    if not res_str:
        logging.warning(f"No 'resolution_nominal' string for sensor {sensor_name}.")
        return None

    resolutions_m = []
    # Regex to find numbers followed by 'm' (meters)
    matches_m = re.findall(r'(\d+)\s*m', res_str, re.IGNORECASE)
    if matches_m:
        resolutions_m.extend([int(m) for m in matches_m])
    
    # Regex to find numbers followed by 'km' (kilometers)
    matches_km = re.findall(r'(\d+)\s*km', res_str, re.IGNORECASE)
    if matches_km:
        resolutions_m.extend([int(km) * 1000 for km in matches_km])

    # Handle degree-based resolutions if no meter/km found, or if they are primary
    # This part is tricky as degree to meter conversion is latitude-dependent.
    # If "resolution_nominal" contains "°" and an approximate km like "~9km", use that.
    if "°" in res_str: # Check if degree symbol is present
        km_in_degree_str_match = re.search(r'~\s*(\d+)\s*km', res_str, re.IGNORECASE)
        if km_in_degree_str_match:
            # This is an approximation provided in the string itself
            resolutions_m.append(int(km_in_degree_str_match.group(1)) * 1000)
        elif not resolutions_m: # Only if no meter/km resolutions were found
            logging.warning(f"Sensor {sensor_name} has degree-based resolution '{res_str}' without a clear meter equivalent. Cannot determine best resolution in meters.")
            # Return None or a default if degree-based is primary and no fallback.
            return None 
            
    if resolutions_m:
        return min(resolutions_m)
    
    logging.warning(f"Could not parse any meter-based resolution from '{res_str}' for sensor {sensor_name}.")
    return None

def generate_tiles_from_bbox(bbox_list):
    """Generates a list of tile bounding boxes from a larger BBOX."""
    min_lon, min_lat, max_lon, max_lat = bbox_list
    if not all(isinstance(c, (int, float)) for c in bbox_list):
        raise ValueError("BBOX coordinates must be numbers.")
    if min_lon >= max_lon or min_lat >= max_lat:
        raise ValueError(f"Invalid BBOX: min_lon {min_lon} >= max_lon {max_lon} or min_lat {min_lat} >= max_lat {max_lat}")
    
    tiles = []
    tile_s = APP_CONFIG.get('TILE_SIZE_DEG', DEFAULT_TILE_SIZE_DEG)
    ovrlp = APP_CONFIG.get('OVERLAP_DEG', DEFAULT_OVERLAP_DEG)
    
    # Ensure step is positive and non-zero, even if overlap is large
    step = max(tile_s - ovrlp, 1e-9) # 1e-9 is a very small step to avoid infinite loop if tile_s <= ovrlp
    if step <= 0: # If tile size is less than or equal to overlap, step could be zero or negative.
        logging.warning(f"Tile size ({tile_s}) is less than or equal to overlap ({ovrlp}). Using a minimal step. This might result in excessive tiling or overlap.")
        step = tile_s * 0.1 # Use a small fraction of tile size as step to ensure progress.
        if step == 0 : step = 1e-9 # Absolute minimal if tile_s is also 0 (though unlikely)

    curr_lon = min_lon
    while curr_lon < max_lon:
        curr_lat = min_lat
        while curr_lat < max_lat:
            # Define tile max extents, ensuring they don't exceed the overall BBOX
            tm_lon = min(curr_lon + tile_s, max_lon)
            tm_lat = min(curr_lat + tile_s, max_lat)
            
            # Add tile only if it has a non-zero width and height
            if tm_lon > curr_lon and tm_lat > curr_lat: 
                tiles.append([curr_lon, curr_lat, tm_lon, tm_lat])
            
            curr_lat += step
            if curr_lat >= max_lat and curr_lat < max_lat + step / 2 : # Handle floating point precision at boundary
                 curr_lat = max_lat # Ensure last tile row is processed if very close
        
        curr_lon += step
        if curr_lon >= max_lon and curr_lon < max_lon + step / 2 : # Handle floating point precision at boundary
            curr_lon = max_lon # Ensure last tile col is processed

    # If no tiles were generated (e.g., BBOX is smaller than a single step)
    # but the BBOX itself is valid, add the BBOX as a single tile.
    if not tiles and (max_lon > min_lon and max_lat > min_lat): 
        tiles.append([min_lon, min_lat, max_lon, max_lat]) 
    elif not tiles:
        # This case should ideally not be reached if the BBOX is valid,
        # as the above condition should catch it.
        raise ValueError("No valid tiles generated. BBOX might be too small or invalid, or step calculation issue.")
        
    logging.info(f"Generated {len(tiles)} tiles (size: {tile_s}°, overlap: {ovrlp}°).")
    return tiles

def mask_clouds_landsat_sr_c2(image):
    """Cloud masking for Landsat Collection 2 Surface Reflectance."""
    qa = image.select('QA_PIXEL')
    # Bitwise flags for cloud, shadow, etc. (Refer to Landsat docs for QA_PIXEL bits)
    # dilated_cloud_mask = (qa.bitwiseAnd(1 << 1)).eq(0) # Dilated Cloud = 0 (clear)
    # cirrus_mask = (qa.bitwiseAnd(1 << 2)).eq(0)      # Cirrus = 0 (clear)
    # cloud_mask = (qa.bitwiseAnd(1 << 3)).eq(0)       # Cloud = 0 (clear)
    # shadow_mask = (qa.bitwiseAnd(1 << 4)).eq(0)      # Cloud Shadow = 0 (clear)
    
    # Simpler approach: mask if any of these are set (i.e., pixel is NOT clear for these conditions)
    # We want pixels where Dilated Cloud, Cirrus, Cloud, Cloud Shadow are ALL clear (0).
    # So, if any of these bits are 1, the pixel is bad.
    # Mask where: (Dilated Cloud is 0) AND (Cirrus is 0) AND (Cloud is 0) AND (Cloud Shadow is 0)
    
    # Bit 1: Dilated Cloud (0 = Not Dilated Cloud, 1 = Dilated Cloud)
    # Bit 2: Cirrus (0 = Not Cirrus, 1 = Cirrus)
    # Bit 3: Cloud (0 = Not Cloud, 1 = Cloud)
    # Bit 4: Cloud Shadow (0 = Not Cloud Shadow, 1 = Cloud Shadow)
    
    # We want to keep pixels where these bits are 0.
    # So, (QA_PIXEL & (1<<1)) == 0 means "Not Dilated Cloud"
    dilated_cloud_clear = qa.bitwiseAnd(1 << 1).eq(0)
    cirrus_clear = qa.bitwiseAnd(1 << 2).eq(0)
    cloud_clear = qa.bitwiseAnd(1 << 3).eq(0)
    shadow_clear = qa.bitwiseAnd(1 << 4).eq(0)
    
    final_mask = dilated_cloud_clear.And(cirrus_clear).And(cloud_clear).And(shadow_clear)
    return image.updateMask(final_mask)

def mask_clouds_sentinel2_sr(image):
    """Cloud masking for Sentinel-2 Surface Reflectance (using QA60 and SCL)."""
    qa = image.select('QA60')
    scl = image.select('SCL') # Scene Classification Layer
    
    # QA60: Opaque and Cirrus clouds bits (10 and 11)
    # We want pixels where both are 0 (clear)
    cloud_mask_qa60 = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
    
    # SCL: Mask out cloud shadows (3), clouds medium prob (8), clouds high prob (9), cirrus (10), snow/ice (11)
    # Keep: No Data (0 - but GEE usually masks this), Saturated/Defective (1), Dark Area Pixels (2),
    #       Vegetation (4), Not Vegetated (5), Water (6), Unclassified (7)
    # We want to EXCLUDE SCL values: 1 (Saturated/Defective), 2 (Dark Area - often shadows), 3 (Cloud Shadows), 
    #                                8 (Cloud Medium Prob), 9 (Cloud High Prob), 10 (Cirrus), 11 (Snow/Ice - optional)
    # Let's be conservative and mask more:
    scl_valid_mask = scl.neq(1).And(scl.neq(2)).And(scl.neq(3)).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
    # Optionally add .And(scl.neq(11)) if snow/ice should also be masked. For now, keep it.

    final_mask = cloud_mask_qa60.And(scl_valid_mask)
    return image.updateMask(final_mask)

CLOUD_MASKS = {
    'LANDSAT_9':mask_clouds_landsat_sr_c2, 'LANDSAT_8':mask_clouds_landsat_sr_c2,
    'LANDSAT_7':mask_clouds_landsat_sr_c2, 'LANDSAT_5':mask_clouds_landsat_sr_c2,
    'LANDSAT_4':mask_clouds_landsat_sr_c2, 'SENTINEL2':mask_clouds_sentinel2_sr,
    'VIIRS':lambda i:i, 'MODIS':lambda i:i, # No standard cloud mask applied by default for these
    'ERA5_TEMP': lambda i:i # No cloud mask for reanalysis temperature data
}

def process_landsat_c2_sr(image):
    """Applies scaling factors for Landsat Collection 2 SR data."""
    # Optical bands: multiply by 0.0000275, add -0.2
    # Thermal bands: multiply by 0.00341802, add 149.0
    optical_band_names = image.bandNames().filter(ee.Filter.stringStartsWith('item', 'SR_B'))
    optical_bands_selected = image.select(optical_band_names)
    optical_bands_scaled = optical_bands_selected.multiply(0.0000275).add(-0.2)
    
    thermal_band_names = image.bandNames().filter(ee.Filter.stringStartsWith('item', 'ST_B'))
    thermal_bands_selected = image.select(thermal_band_names)
    thermal_bands_scaled = thermal_bands_selected.multiply(0.00341802).add(149.0)
    
    # Add scaled bands back, overwriting original if names are the same (True for overwrite)
    image_with_optical = image.addBands(optical_bands_scaled, None, True)
    final_image = image_with_optical.addBands(thermal_bands_scaled, None, True)
    return final_image

def process_sentinel2_sr(image):
    """Applies scaling factor for Sentinel-2 SR data (divide by 10000)."""
    # Select bands starting with 'B' (optical bands) and QA/SCL bands
    bands_to_scale_names = image.bandNames().filter(ee.Filter.stringStartsWith('item', 'B'))
    bands_to_scale = image.select(bands_to_scale_names)
    scaled_bands = bands_to_scale.divide(10000.0) # Scale factor
    
    # Keep QA bands as they are (QA60, SCL)
    qa_band_names = image.bandNames().filter(ee.Filter.stringContains('item','QA').Or(ee.Filter.stringContains('item','SCL')))
    qa_bands = image.select(qa_band_names)
    
    # Add scaled optical bands, then QA bands, ensuring no duplication if names were same
    # Overwrite existing bands if names match
    image_with_scaled = image.addBands(scaled_bands, None, True) 
    # It's safer to select the bands explicitly after processing to avoid issues with original unscaled bands
    # final_image = image_with_scaled.addBands(qa_bands, None, True) # This might add QA bands if they weren't selected by 'B.*'
    
    # Construct the list of final band names we want to keep
    final_band_selection = scaled_bands.bandNames().cat(qa_band_names)
    
    # Return image with only the processed (scaled optical) and original QA/SCL bands
    return image_with_scaled.select(final_band_selection)


def process_era5_temp(image):
    """Converts ERA5 temperature from Kelvin to Celsius."""
    temp_k = image.select('temperature_2m') # Assuming this is the band name
    temp_c = temp_k.subtract(273.15).rename('temperature_2m_Celsius')
    # Return an image with only the Celsius band, or add it to the original
    return image.addBands(temp_c, None, True).select(['temperature_2m_Celsius'])


SENSOR_PROCESSORS = {
    'LANDSAT_9':process_landsat_c2_sr,'LANDSAT_8':process_landsat_c2_sr,
    'LANDSAT_7':process_landsat_c2_sr,'LANDSAT_5':process_landsat_c2_sr,
    'LANDSAT_4':process_landsat_c2_sr,'SENTINEL2':process_sentinel2_sr,
    'VIIRS':lambda i:i,'MODIS':lambda i:i, # No default processing for these
    'ERA5_TEMP': process_era5_temp
}

def get_available_sensors(target_date_obj):
    """Returns a list of sensors operational on the target_date_obj."""
    if isinstance(target_date_obj, datetime): # Ensure we're comparing date objects
        target_date_obj = target_date_obj.date()
        
    available_sensors_list = []
    for sensor_name, (start_date_str, end_date_str) in SENSOR_TIMELINE.items():
        try:
            start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
            
            is_operational = False
            if end_date_obj is None: # Still operational
                if target_date_obj >= start_date_obj:
                    is_operational = True
            else: # Has an end date
                if start_date_obj <= target_date_obj <= end_date_obj:
                    is_operational = True
            
            if is_operational:
                available_sensors_list.append(sensor_name)
        except ValueError as e:
            logging.error(f"Date format error for sensor {sensor_name} in SENSOR_TIMELINE: {e}")
    return available_sensors_list

def get_collection(sensor):
    """Gets the GEE ImageCollection for a given sensor, trying alternatives if defined."""
    if sensor not in DATA_COLLECTIONS:
        raise ValueError(f"Sensor {sensor} is not defined in DATA_COLLECTIONS.")
    
    collection_ids_for_sensor = DATA_COLLECTIONS[sensor]
    if not isinstance(collection_ids_for_sensor, list): # Ensure it's a list
        collection_ids_for_sensor = [collection_ids_for_sensor]

    for collection_id_str in collection_ids_for_sensor:
        try:
            ee_collection = ee.ImageCollection(collection_id_str)
            # Perform a small operation to check accessibility (e.g., get size of a limit(1) query)
            # limit(0) or limit(1).size() can be problematic if collection is empty or inaccessible.
            # A more robust check might be trying to get metadata or a single image.
            # For now, assume if ImageCollection() doesn't throw error, it's a starting point.
            # A .limit(1).size().getInfo() can be slow and error-prone if collection is huge or user lacks access.
            # A lighter check:
            # ee_collection.first() # This will be None if empty, or an image if not. Can still error.
            # A simple check for existence:
            # info = ee.data.getAsset(collection_id_str) # This checks if asset ID exists, but not if it's an ImageCollection
            # Simplest: just try to use it. If it fails later, the error handling there will catch it.
            # For now, let's assume ee.ImageCollection() is enough, and errors will be caught downstream.
            # However, a quick check for image presence is good:
            if ee_collection.limit(1).size().getInfo() >= 0: # Check if size can be retrieved (even if 0)
                logging.debug(f"Using collection: {collection_id_str} for sensor {sensor}")
                return ee_collection
        except Exception as e:
            logging.warning(f"Failed to access or verify {collection_id_str} for {sensor}: {e}. Trying next if available.")
            continue # Try the next collection ID if one fails
            
    raise ValueError(f"No accessible Earth Engine collection found for sensor {sensor} from options: {collection_ids_for_sensor}")

class DownloadManager:
    def __init__(self):
        self.session = requests.Session()
        # Configure retry strategy for downloads
        max_retries_for_download = APP_CONFIG.get('MAX_TILE_RETRIES', DEFAULT_MAX_TILE_RETRIES) + 1 # Total attempts
        retry_strategy_obj = Retry(
            total=max_retries_for_download,
            backoff_factor=1, # Exponential backoff factor (e.g., 1s, 2s, 4s)
            status_forcelist=[408, 429, 500, 502, 503, 504], # HTTP codes to retry on
            allowed_methods=["GET"] # Only retry GET requests
        )
        # Mount HTTPAdapter with the retry strategy for both http and https
        http_adapter = HTTPAdapter(
            max_retries=retry_strategy_obj,
            pool_connections=APP_CONFIG.get('MAX_WORKERS', DEFAULT_MAX_WORKERS) * 2, # More connections for pool
            pool_maxsize=APP_CONFIG.get('MAX_WORKERS', DEFAULT_MAX_WORKERS) * 2
        )
        self.session.mount("https://", http_adapter)
        self.session.mount("http://", http_adapter)

    def download_tile(self, mosaic_image, tile_bbox, output_path, tile_index, sensor_name_for_log):
        """Downloads a single tile using GEE's getDownloadURL."""
        temp_download_path = f"{output_path}.tmp" # Download to a temporary file first
        download_timeout_seconds = APP_CONFIG.get('DOWNLOAD_TIMEOUT', DEFAULT_DOWNLOAD_TIMEOUT)

        current_target_resolution = APP_CONFIG.get('TARGET_RESOLUTION', DEFAULT_TARGET_RESOLUTION)
        if APP_CONFIG.get('USE_BEST_RESOLUTION', False):
            best_res = get_best_resolution_for_sensor(sensor_name_for_log)
            if best_res:
                current_target_resolution = best_res
                logging.info(f"T{tile_index}({sensor_name_for_log}): Using best resolution for download: {best_res}m")
            else:
                logging.warning(f"T{tile_index}({sensor_name_for_log}): Could not determine best resolution, using configured: {current_target_resolution}m")

        try:
            selected_band_names = mosaic_image.bandNames().getInfo()
            if not selected_band_names:
                logging.error(f"T{tile_index}({sensor_name_for_log}): Mosaic has no bands for download.")
                return None # Indicate failure, not just False for validation
            
            download_params = {
                'bands': selected_band_names, # Ensure bands are specified
                'scale': current_target_resolution,
                'region': ee.Geometry.Rectangle(tile_bbox).toGeoJSONString(), # Region as GeoJSON
                'format': 'GeoTIFF',
                'crs': 'EPSG:4326', # Standard CRS
                'maxPixels': 1e13 # Allow large downloads
            }
            download_url = mosaic_image.getDownloadURL(download_params)
            logging.debug(f"T{tile_index}({sensor_name_for_log}): DL URL: {download_url[:100]}...") # Log only part of URL

            with self.session.get(download_url, stream=True, timeout=download_timeout_seconds) as response:
                response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                with open(temp_download_path, 'wb') as file_handle:
                    for chunk_data in response.iter_content(chunk_size=1024*1024): # 1MB chunks
                        if chunk_data: # filter out keep-alive new chunks
                            file_handle.write(chunk_data)
            
            # Validate the downloaded tile
            if self.validate_tile(temp_download_path, tile_index, tile_bbox, sensor_name_for_log):
                os.rename(temp_download_path, output_path) # Move to final path if valid
                logging.info(f"T{tile_index}({sensor_name_for_log}): DL & validation OK: {os.path.basename(output_path)}")
                return True # Success
            else:
                logging.warning(f"T{tile_index}({sensor_name_for_log}): Validation FAILED for {os.path.basename(temp_download_path)}")
                if os.path.exists(temp_download_path):
                    os.remove(temp_download_path)
                return False # Validation failed

        except requests.exceptions.HTTPError as http_err:
            # Log more details for HTTP errors, especially 400 from GEE
            logging.warning(f"T{tile_index}({sensor_name_for_log}): HTTPError: {http_err}. URL: {download_url[:100] if 'download_url' in locals() else 'N/A'}")
            if http_err.response and http_err.response.status_code == 400:
                # GEE often returns JSON with error details in the response body for 400 errors
                try:
                    error_details = http_err.response.json()
                    logging.error(f"T{tile_index}({sensor_name_for_log}): GEE export error details: {error_details}")
                except json.JSONDecodeError:
                    logging.error(f"T{tile_index}({sensor_name_for_log}): GEE export error (non-JSON response): {http_err.response.text[:500]}") # Log first 500 chars
            return None # Indicate download failure
        except Exception as general_err:
            logging.error(f"T{tile_index}({sensor_name_for_log}): DL error: {general_err}", exc_info=True)
            return None # Indicate download failure
        finally:
            # Ensure temp file is cleaned up if it still exists and final file wasn't created
            if os.path.exists(temp_download_path) and not os.path.exists(output_path):
                 os.remove(temp_download_path)

    def validate_tile(self, file_path_to_validate, tile_index, bbox_context, sensor_name_for_log):
        """Validates a downloaded GeoTIFF tile."""
        min_valid_pixels_threshold = APP_CONFIG.get('MIN_VALID_PIXELS_TILE_VALIDATION', DEFAULT_MIN_VALID_PIXELS_TILE_VALIDATION)
        
        if not os.path.exists(file_path_to_validate) or os.path.getsize(file_path_to_validate) < 1024: # Min size check (1KB)
            logging.warning(f"T{tile_index}({sensor_name_for_log}): File small/missing for validation: {os.path.basename(file_path_to_validate)}")
            return False
        try:
            with rasterio.open(file_path_to_validate) as raster_source:
                if raster_source.count == 0: # No bands
                    logging.warning(f"T{tile_index}({sensor_name_for_log}): No bands in raster: {os.path.basename(file_path_to_validate)}")
                    return False
                
                found_at_least_one_valid_band = False
                for band_number in range(1, raster_source.count + 1):
                    band_data_array = raster_source.read(band_number)
                    nodata_value_for_band = raster_source.nodatavals[band_number-1] if raster_source.nodatavals and raster_source.nodatavals[band_number-1] is not None else None
                    
                    if nodata_value_for_band is not None:
                        number_of_valid_pixels = numpy.sum(band_data_array != nodata_value_for_band)
                    else: # No explicit nodata, check for NaNs or all zeros (for optical)
                        is_not_nan = ~numpy.isnan(band_data_array)
                        # For optical sensors, assume 0 might be valid if not NaN, but often indicates no data after masking.
                        # For SAR/Thermal, 0 can be a valid measurement.
                        is_not_zero_for_optical = True # Default to true
                        if sensor_name_for_log not in ['SENTINEL1', 'MODIS_LST', 'ERA5_TEMP', 'CHIRTS_TEMP']: # Add other non-optical if needed
                             is_not_zero_for_optical = (band_data_array != 0)
                        
                        number_of_valid_pixels = numpy.sum(is_not_nan & is_not_zero_for_optical)

                    if number_of_valid_pixels >= min_valid_pixels_threshold:
                        logging.debug(f"T{tile_index}({sensor_name_for_log}): Band {band_number} has {number_of_valid_pixels} valid pixels (threshold: {min_valid_pixels_threshold}).")
                        found_at_least_one_valid_band = True
                        break # One valid band is enough
                        
                if not found_at_least_one_valid_band:
                    logging.warning(f"T{tile_index}({sensor_name_for_log}): Insufficient valid pixels across all bands in {os.path.basename(file_path_to_validate)} (threshold: {min_valid_pixels_threshold}).")
                    return False
                return True # Tile is valid
        except Exception as e:
            logging.error(f"T{tile_index}({sensor_name_for_log}): Validation error for {os.path.basename(file_path_to_validate)}: {e}", exc_info=True)
            return False

def get_valid_pixel_percentage(image_to_check, region_of_interest, target_scale, sensor_name):
    """Calculates the percentage of valid (unmasked) pixels in an image for a region."""
    try:
        scale_to_use = target_scale
        if APP_CONFIG.get('USE_BEST_RESOLUTION', False):
            best_res_for_sensor = get_best_resolution_for_sensor(sensor_name)
            if best_res_for_sensor:
                scale_to_use = best_res_for_sensor
                logging.debug(f"{sensor_name}: Using best resolution for valid pixel check: {scale_to_use}m")
            else:
                logging.debug(f"{sensor_name}: Could not determine best res for valid pixel check, using configured: {scale_to_use}m")

        available_bands = image_to_check.bandNames().getInfo()
        if not available_bands:
            logging.warning(f"{sensor_name}: No bands available in image for valid pixel check.")
            return 0.0

        # For SAR or climate data, mask might not be the primary quality indicator.
        # Assume high quality if data exists.
        if sensor_name in ['SENTINEL1', 'ERA5_TEMP', 'CHIRTS_TEMP']: # Add other non-optical types if needed
            # Check if there's any data at all by reducing a band.
            first_band_selected = image_to_check.select(0) # Select the first band
            stats_dictionary = first_band_selected.reduceRegion(
                reducer=ee.Reducer.mean(), # Can be any reducer that requires unmasked pixels
                geometry=region_of_interest, 
                scale=scale_to_use, 
                maxPixels=1e7, # Reduced maxPixels for this check
                tileScale=2 # Use a tileScale for better performance with reduceRegion
            ).getInfo()
            first_band_name_str = first_band_selected.bandNames().get(0).getInfo() # Get name of the first band
            if stats_dictionary and first_band_name_str in stats_dictionary and stats_dictionary.get(first_band_name_str) is not None:
                logging.debug(f"{sensor_name}: SAR/Climate data detected in ROI, assuming high valid pixel percentage for quality score.")
                return 99.0 # Assign a high score if any data exists
            return 0.0 # No data found

        # For optical data, calculate based on mask
        ones_image = ee.Image(1).rename('v') # Create an image of ones
        image_mask = image_to_check.mask().reduce(ee.Reducer.firstNonNull()) # Get a single mask band
        masked_ones_image = ones_image.updateMask(image_mask) # Apply the image's mask to the ones image
        
        stats_result = masked_ones_image.reduceRegion(
            reducer=ee.Reducer.mean(), # Mean of 1s and 0s (masked) gives fraction of unmasked
            geometry=region_of_interest, 
            scale=target_scale, # Use the originally passed target_scale for consistency
            maxPixels=1e9, # Allow large computation
            tileScale=4 # Higher tileScale for reduceRegion can improve performance
        )
        valid_fraction = stats_result.get('v').getInfo() # Get the mean value
        return (valid_fraction * 100.0) if valid_fraction is not None else 0.0
    except Exception as e:
        logging.warning(f"GEE error in get_valid_pixel_percentage for {sensor_name}: {e}. Assuming 0%.")
        return 0.0

def build_mosaic(sensor_name, target_year, target_month, roi_geometry, tile_log_index, cancel_processing_event):
    """Builds a monthly median mosaic for a sensor and ROI."""
    # Define a 3-month window centered on the target month for more data
    # E.g., for July, use June 15 to August 15.
    # More robust: Use start of month before, end of month after.
    # Example: For July (month 7), window is June 1 to August 31.
    # For more data, a wider window like +/- 1 month from the 15th is reasonable.
    # Let's use a window from 1 month before the 15th to 1 month after the 15th.
    # This gives roughly a 2-month window centered around the target month's 15th.
    # Example: target month July (7). start_date = June 15th, end_date = August 15th.
    # This might be too narrow. Let's try a fixed 60-day window around the 15th.
    # Or, more simply, use the start of the target month to the end of the target month,
    # and if quality is low, the calling function can try a wider range or different sensor.
    # For now, let's stick to a window that is roughly the target month +/- 15 days,
    # or more simply, a 45-day window around the 15th of the month.
    # Or, as originally: 15th of prev month to 15th of next month.
    # This makes it a ~2 month window.
    
    # Using a window from 1 month prior to the 15th, to 1 month after the 15th of the target month.
    # E.g., Target July: Start June 15, End August 15. This is a ~60 day window.
    # A simpler and often effective approach: +/- 45 days from the 15th of the target month.
    # Let's refine the date range to be more specific for monthly composites:
    # Target month: e.g., July. Range: July 1 to July 31.
    # If we want to include data from adjacent months for better coverage:
    # e.g., for July, use June 1 to August 31 (3-month window).
    # The original code used: 15th of (Month M-1) to 15th of (Month M+1). This is a ~60 day window.
    # Let's use a slightly wider window: start of (Month M-1) to end of (Month M+1) for more chances.
    # No, this might be too wide and average out seasonal changes.
    # Let's use a window of +/- 30 days around the 15th of the target month.
    center_date = datetime(target_year, target_month, 15)
    start_date_obj = center_date - relativedelta(days=30)
    end_date_obj = center_date + relativedelta(days=30)

    ee_start_date_str = ee.Date(start_date_obj.strftime('%Y-%m-%d'))
    ee_end_date_str = ee.Date(end_date_obj.strftime('%Y-%m-%d'))
    
    logging.info(f"T{tile_log_index}({sensor_name}): Building mosaic for period {start_date_obj:%Y-%m-%d} to {end_date_obj:%Y-%m-%d} for target month {target_year}-{target_month:02d}")
    
    max_retries = APP_CONFIG.get('MAX_TILE_RETRIES', DEFAULT_MAX_TILE_RETRIES) # Max retries for mosaic building itself
    
    for attempt_num in range(max_retries + 1): # +1 for initial attempt
        if cancel_processing_event.is_set(): return None, 0.0
        try:
            image_collection = get_collection(sensor_name) # Get base collection
            filtered_collection = image_collection.filterDate(ee_start_date_str, ee_end_date_str).filterBounds(roi_geometry)
            
            initial_image_count = filtered_collection.size().getInfo()
            if initial_image_count == 0:
                logging.info(f"T{tile_log_index}({sensor_name}): No images found in collection for the period/ROI.")
                return None, 0.0 # No images, so quality is 0

            masking_function = CLOUD_MASKS.get(sensor_name, lambda img: img) # Get cloud mask func
            processing_function = SENSOR_PROCESSORS.get(sensor_name, lambda img: img) # Get sensor-specific processing

            # Apply masking and processing safely
            def safe_processing_and_masking(input_image):
                try:
                    masked_image = masking_function(input_image)
                    processed_image = processing_function(masked_image)
                    # Add a property to ensure mapping worked, helps filter out nulls if processing fails
                    return processed_image.set('fe_processing_check', 1) 
                except Exception as e_map:
                    logging.warning(f"T{tile_log_index}({sensor_name}): Error in map function (processing/masking): {e_map}. Image will be skipped.")
                    return None # Return None if error in map, GEE map will skip it if .filter(ee.Filter.neq('fe_processing_check', None)) is used.
                                # Or, more robustly, have the function return an image with no bands or a specific flag.
                                # For now, rely on fe_processing_check.

            # Map functions and filter out any images that failed processing
            processed_collection = filtered_collection.map(safe_processing_and_masking).filter(ee.Filter.neq('fe_processing_check', None))
            
            count_after_processing = processed_collection.size().getInfo()
            if count_after_processing == 0:
                logging.warning(f"T{tile_log_index}({sensor_name}): All {initial_image_count} images were masked out or failed processing.")
                return None, 0.0
            
            logging.info(f"T{tile_log_index}({sensor_name}): {count_after_processing} images available for mosaic after processing.")
            
            # Create median composite and clip to ROI
            median_mosaic = processed_collection.median().clip(roi_geometry)
            
            # Check if mosaic has bands (it might not if all pixels were masked in all images)
            mosaic_band_names = median_mosaic.bandNames().getInfo()
            if not mosaic_band_names:
                logging.warning(f"T{tile_log_index}({sensor_name}): Resulting median mosaic has no bands (all pixels masked).")
                return None, 0.0

            # Calculate quality score (e.g., percentage of valid pixels)
            quality_score_percentage = get_valid_pixel_percentage(median_mosaic, roi_geometry, APP_CONFIG.get('TARGET_RESOLUTION', DEFAULT_TARGET_RESOLUTION), sensor_name)
            logging.info(f"T{tile_log_index}({sensor_name}): Mosaic built. Valid pixel score: {quality_score_percentage:.2f}%")

            # Define a minimum quality threshold (e.g., 0.5% valid pixels for optical)
            min_quality_threshold = 0.5 if sensor_name not in ['SENTINEL1', 'ERA5_TEMP', 'CHIRTS_TEMP'] else 0.01 # Lower for SAR/Climate
            if quality_score_percentage < min_quality_threshold:
                logging.warning(f"T{tile_log_index}({sensor_name}): Low valid pixel score ({quality_score_percentage:.2f}% < {min_quality_threshold}%). Discarding mosaic.")
                return None, quality_score_percentage # Return score even if discarded

            return median_mosaic, quality_score_percentage

        except ee.EEException as gee_error:
            logging.warning(f"T{tile_log_index}({sensor_name}): EEException during mosaic build (Attempt {attempt_num + 1}/{max_retries + 1}): {str(gee_error)[:250]}") # Log only part of error
            # Handle specific GEE errors that might benefit from retry with backoff
            if "Too many concurrent aggregations" in str(gee_error) or \
               "User memory limit exceeded" in str(gee_error) or \
               "Computation timed out" in str(gee_error) or \
               "Too many requests" in str(gee_error): # Common resource-related errors
                
                logging.error(f"T{tile_log_index}({sensor_name}): GEE resource limit hit: {gee_error}")
                if "User memory limit exceeded" in str(gee_error) or "Computation timed out" in str(gee_error) and attempt_num >= max_retries:
                    # These are often fatal for the current request complexity
                    logging.error(f"T{tile_log_index}({sensor_name}): Fatal GEE error, cannot recover this mosaic attempt.")
                    return None, 0.0 
                if attempt_num < max_retries:
                    sleep_time = 30 * (attempt_num + 1) # Exponential backoff
                    logging.info(f"T{tile_log_index}({sensor_name}): Waiting {sleep_time}s before retrying mosaic build...")
                    time.sleep(sleep_time)
                else: # Max retries reached for this type of error
                    logging.error(f"T{tile_log_index}({sensor_name}): Max retries reached for GEE resource error.")
                    return None, 0.0 # Failed after retries
            elif attempt_num < max_retries: # Other GEE errors, try a shorter wait
                time.sleep(5 * (attempt_num + 1))
            else: # Max retries for other GEE errors
                 logging.error(f"T{tile_log_index}({sensor_name}): Max mosaic build attempts failed due to persistent EEException.")
                 return None, 0.0 # Failed after retries
        except Exception as general_error:
            logging.error(f"T{tile_log_index}({sensor_name}): Unexpected error during mosaic build (Attempt {attempt_num + 1}): {general_error}", exc_info=True)
            if attempt_num < max_retries:
                time.sleep(5 * (attempt_num + 1)) # Short wait for general errors
            else:
                return None, 0.0 # Failed after retries
    
    logging.error(f"T{tile_log_index}({sensor_name}): Mosaic build failed after all attempts.")
    return None, 0.0 # Should be caught by attempt loop return

def process_tile(args):
    """Processes a single tile: finds best sensor, builds mosaic, downloads."""
    tile_log_index, tile_bbox, target_year, target_month, temp_storage_dir, cancel_event, gui_status_update_callback = args
    
    if cancel_event.is_set():
        if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: Cancelled")
        return tile_log_index, None, 0.0, None # tile_index, path, quality, sensor

    # Initialize EE in each thread/worker if not already initialized for this process
    # This is important as EE state is not always shared well across processes/threads.
    try:
        # Try high-volume first, as it's preferred for batch tasks
        ee.Initialize(project=EE_PROJECT, opt_url='https://earthengine-highvolume.googleapis.com')
        ee.data.getAssetRoots() # Verify
    except Exception: # If high-volume fails, try default
        try: 
            ee.Initialize(project=EE_PROJECT)
            ee.data.getAssetRoots() # Verify
        except Exception as e_init_thread:
            logging.error(f"T{tile_log_index}: EE Initialization Failed in thread: {e_init_thread}")
            if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: EE Fail")
            return tile_log_index, None, 0.0, None

    region_of_interest = ee.Geometry.Rectangle(tile_bbox)
    date_for_sensor_check = datetime(target_year, target_month, 15).date() # Mid-month for sensor availability check
    
    best_mosaic_data = {'mosaic': None, 'quality': -1.0, 'sensor_name': None}
    
    sensor_priority_list = APP_CONFIG.get('SENSOR_PRIORITY_ORDER', DEFAULT_SENSOR_PRIORITY_ORDER)
    sensors_available_on_date = get_available_sensors(date_for_sensor_check)
    
    # Filter priority list by sensors available on the target date
    sensors_to_evaluate = [s_name for s_name in sensor_priority_list if s_name in sensors_available_on_date]
    
    if not sensors_to_evaluate:
        logging.warning(f"T{tile_log_index}: No sensors from priority list are available for {date_for_sensor_check}.")
        if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: No Sensors")
        return tile_log_index, None, 0.0, None

    logging.info(f"T{tile_log_index}: Evaluating sensors for {target_year}-{target_month:02d} in order: {sensors_to_evaluate}")

    for sensor_eval_index, current_sensor_name in enumerate(sensors_to_evaluate):
        if cancel_event.is_set(): break
        
        if gui_status_update_callback:
            gui_status_update_callback(f"T{tile_log_index}: Eval {current_sensor_name} ({sensor_eval_index+1}/{len(sensors_to_evaluate)})...")
        
        current_mosaic_image, current_quality_score = build_mosaic(current_sensor_name, target_year, target_month, region_of_interest, tile_log_index, cancel_event)
        
        if current_mosaic_image and current_quality_score > best_mosaic_data['quality']:
            logging.info(f"T{tile_log_index}: New best mosaic from {current_sensor_name} (Q:{current_quality_score:.2f}%) replacing {best_mosaic_data['sensor_name']} (Q:{best_mosaic_data['quality']:.2f}%)")
            best_mosaic_data = {'mosaic': current_mosaic_image, 'quality': current_quality_score, 'sensor_name': current_sensor_name}
        elif current_mosaic_image: # Mosaic built, but not better quality
            logging.info(f"T{tile_log_index}: Mosaic from {current_sensor_name} (Q:{current_quality_score:.2f}%) not better than current best from {best_mosaic_data['sensor_name']} (Q:{best_mosaic_data['quality']:.2f}%).")
        
        # Small delay to avoid overwhelming GEE, especially if many sensors are tried quickly
        time.sleep(0.05) 

    if cancel_event.is_set() or not best_mosaic_data['mosaic']:
        status_message = "Cancelled" if cancel_event.is_set() else "No suitable mosaic found"
        logging.info(f"T{tile_log_index}: {status_message} after evaluating all sensors.")
        if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: {status_message}")
        return tile_log_index, None, best_mosaic_data['quality'], best_mosaic_data['sensor_name']

    selected_sensor_for_download = best_mosaic_data['sensor_name']
    logging.info(f"T{tile_log_index}: Best mosaic selected from {selected_sensor_for_download} (Q:{best_mosaic_data['quality']:.2f}%). Proceeding to download.")
    if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: DL {selected_sensor_for_download}...")
    
    # Define tile filename based on selected sensor and other params
    tile_file_name = f"{selected_sensor_for_download}_tile_{target_year}_{target_month:02d}_{tile_log_index:04d}.tif"
    tile_output_path = os.path.join(temp_storage_dir, tile_file_name)
    
    download_manager_instance = DownloadManager() # Create a new manager for each tile or reuse one? For now, new.
    download_successful = download_manager_instance.download_tile(
        best_mosaic_data['mosaic'], tile_bbox, tile_output_path, tile_log_index, selected_sensor_for_download
    )
    
    if download_successful is True: # Explicitly check for True (success)
        if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: OK ({selected_sensor_for_download})")
        return tile_log_index, tile_output_path, best_mosaic_data['quality'], selected_sensor_for_download
    else: 
        # download_successful could be False (validation failed) or None (download error)
        download_status_log = "Validation Fail" if download_successful is False else "DL Fail/Error"
        logging.warning(f"T{tile_log_index}: {download_status_log} for {selected_sensor_for_download}.")
        if gui_status_update_callback: gui_status_update_callback(f"T{tile_log_index}: {download_status_log}({selected_sensor_for_download})")
        if os.path.exists(tile_output_path): # Clean up failed/invalid partial download
            os.remove(tile_output_path)
        return tile_log_index, None, best_mosaic_data['quality'], selected_sensor_for_download


def process_month(year, month, out_dir, tiles_definition_list, overwrite_existing, cancel_ev, gui_tile_prog_f, gui_stat_f):
    """Processes all tiles for a given month and stitches them."""
    month_string_for_files = f"{year}-{month:02d}"
    month_output_directory = os.path.join(out_dir, month_string_for_files)
    
    # Path for a generic mosaic name, used for early skip if overwrite is False.
    # The actual mosaic will be named with the sensor.
    preliminary_final_mosaic_path_generic = os.path.join(month_output_directory, f"mosaic_{month_string_for_files}.tif") # Generic name
    
    # If not overwriting and a generic mosaic exists, we might skip.
    # However, the new logic names mosaics by sensor. So, this check needs refinement.
    # For now, if *any* mosaic exists for this month and overwrite is false, it's complex.
    # Let's assume if overwrite is false, we check for sensor-specific mosaic later.
    # This generic check is less useful now.
    # if not overwrite_existing and os.path.exists(preliminary_final_mosaic_path_generic):
    #     logging.info(f"Found existing generic mosaic for {month_string_for_files}. Specific sensor check will occur later if needed.")
        # No early exit here, proceed to tile processing, then check specific sensor mosaic.

    if cancel_ev.is_set(): return False, 0 # success_flag, num_tiles_processed
    
    temp_tile_storage_dir = os.path.join(month_output_directory, "tiles")
    os.makedirs(temp_tile_storage_dir, exist_ok=True)
    
    tasks_for_executor = [
        (idx, tile_bbox, year, month, temp_tile_storage_dir, cancel_ev, gui_stat_f) 
        for idx, tile_bbox in enumerate(tiles_definition_list)
    ]
    
    tile_results_map = {} # Stores (tile_path, quality, sensor_name) keyed by original_tile_idx
    processed_tiles_this_month_count = 0
    
    # Max workers from APP_CONFIG
    max_workers_for_tiles = APP_CONFIG.get('MAX_WORKERS', DEFAULT_MAX_WORKERS)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers_for_tiles,
                                               thread_name_prefix=f"TileProc-{month_string_for_files}") as executor:
        # Map future objects to their original tile index for easier result tracking
        future_to_tile_index = {executor.submit(process_tile, task_args): task_args[0] for task_args in tasks_for_executor}
        
        total_tiles_for_month = len(tasks_for_executor)
        completed_tiles_count_for_progress = 0
        
        for future_obj in concurrent.futures.as_completed(future_to_tile_index):
            if cancel_ev.is_set(): # Check for cancellation before processing result
                # Attempt to cancel pending futures
                for f_to_cancel in future_to_tile_index.keys(): 
                    if not f_to_cancel.done(): f_to_cancel.cancel() 
                break # Exit the loop over completed futures
            
            original_tile_idx = future_to_tile_index[future_obj]
            try: 
                # process_tile returns: tile_log_index, tile_output_path, quality_score, sensor_name_used
                _, tile_path_result, quality_score, sensor_name_used = future_obj.result() 
                tile_results_map[original_tile_idx] = (tile_path_result, quality_score, sensor_name_used)
                if tile_path_result: # If a path was returned, it means download (and validation if applicable) was successful
                    processed_tiles_this_month_count += 1
            except concurrent.futures.CancelledError:
                logging.info(f"Tile {original_tile_idx} processing was cancelled for {month_string_for_files}.")
                tile_results_map[original_tile_idx] = (None, 0.0, "Cancelled") # Store cancellation status
            except Exception as exc: # Catch any other exception from process_tile
                logging.error(f"Tile {original_tile_idx} for {month_string_for_files} generated an exception: {exc}", exc_info=True)
                tile_results_map[original_tile_idx] = (None, 0.0, "Error") # Store error status
            
            completed_tiles_count_for_progress += 1
            if gui_tile_prog_f: 
                gui_tile_prog_f(completed_tiles_count_for_progress, total_tiles_for_month) # Update GUI progress
            time.sleep(0.01) # Small sleep to allow GUI to update / other threads to breathe

    # Collect all successfully downloaded tile paths
    successfully_downloaded_tile_paths = [res[0] for res in tile_results_map.values() if res and res[0] is not None]
    
    if cancel_ev.is_set(): # Final check after loop
        logging.info(f"Processing for {month_string_for_files} was cancelled. Stitching will be skipped.")
        if gui_stat_f: gui_stat_f(f"{month_string_for_files}: Cancelled, no stitch")
        if APP_CONFIG.get('CLEANUP_TILES',DEFAULT_CLEANUP_TILES) and os.path.exists(temp_tile_storage_dir):
            shutil.rmtree(temp_tile_storage_dir,ignore_errors=True)
        return False, processed_tiles_this_month_count

    if not successfully_downloaded_tile_paths:
        logging.error(f"Month {month_string_for_files}: No tiles were successfully downloaded. No mosaic will be created.")
        if gui_stat_f: gui_stat_f(f"{month_string_for_files}: No tiles, no stitch")
        # Clean up empty tile directory if it exists and cleanup is enabled
        if APP_CONFIG.get('CLEANUP_TILES',DEFAULT_CLEANUP_TILES) and os.path.exists(temp_tile_storage_dir) and not os.listdir(temp_tile_storage_dir):
            try:
                shutil.rmtree(temp_tile_storage_dir) # Remove if empty
            except OSError as e_rmdir:
                logging.warning(f"Could not remove empty tile directory {temp_tile_storage_dir}: {e_rmdir}")
        return False, processed_tiles_this_month_count

    # Determine the sensor used for the majority/best tiles for naming the mosaic
    # This assumes all successful tiles for a month will be from the same sensor,
    # which is the current logic of process_tile (it picks one best sensor per tile attempt).
    # A more robust way: get sensor from the first valid tile.
    first_tile_info = next((res for res in tile_results_map.values() if res and res[0] is not None), None)
    inferred_sensor_for_mosaic = "UnknownSensor"
    if first_tile_info and first_tile_info[2] and first_tile_info[2] not in ["Cancelled", "Error"]:
        inferred_sensor_for_mosaic = first_tile_info[2]
    
    final_mosaic_path = os.path.join(month_output_directory, f"{inferred_sensor_for_mosaic}_mosaic_{month_string_for_files}.tif")

    # Check if this specific sensor mosaic already exists and if overwrite is False
    if os.path.exists(final_mosaic_path) and not overwrite_existing:
        logging.info(f"Skipping {month_string_for_files} (Sensor: {inferred_sensor_for_mosaic}): Sensor-specific mosaic already exists and overwrite is false.")
        if gui_stat_f: gui_stat_f(f"{month_string_for_files} ({inferred_sensor_for_mosaic}): Skipped (exists)")
        # Clean up tiles if required, as we are skipping stitching
        if APP_CONFIG.get('CLEANUP_TILES',DEFAULT_CLEANUP_TILES) and os.path.exists(temp_tile_storage_dir):
            shutil.rmtree(temp_tile_storage_dir,ignore_errors=True)
        return True, processed_tiles_this_month_count # Success (skipped), tiles processed

    logging.info(f"{month_string_for_files}: Downloaded {len(successfully_downloaded_tile_paths)}/{total_tiles_for_month} tiles (Primary Sensor: {inferred_sensor_for_mosaic}).")
    if gui_stat_f: gui_stat_f(f"{month_string_for_files}: Stitching {len(successfully_downloaded_tile_paths)} tiles...")
    
    if stitch_mosaic(successfully_downloaded_tile_paths, final_mosaic_path):
        logging.info(f"{month_string_for_files}: Mosaic created successfully: {final_mosaic_path}")
        if gui_stat_f: gui_stat_f(f"{month_string_for_files}: Mosaic OK!")
        if APP_CONFIG.get('CLEANUP_TILES',DEFAULT_CLEANUP_TILES) and os.path.exists(temp_tile_storage_dir):
            shutil.rmtree(temp_tile_storage_dir,ignore_errors=True)
        return True, processed_tiles_this_month_count
    else:
        logging.error(f"{month_string_for_files}: Stitching FAILED for {final_mosaic_path}.")
        if gui_stat_f: gui_stat_f(f"{month_string_for_files}: Stitch FAILED!")
        # Do not delete tiles if stitching failed, user might want to inspect them.
        return False, processed_tiles_this_month_count

def stitch_mosaic(tile_paths_list, output_mosaic_path):
    """Stitches a list of GeoTIFF tile paths into a single mosaic."""
    if not tile_paths_list: 
        logging.warning("No tile paths provided for stitching.")
        return False
        
    src_files_to_mosaic = []
    try:
        for tile_p in tile_paths_list:
            if tile_p and os.path.exists(tile_p) and os.path.getsize(tile_p) > 0: # Check path, existence, and size
                try:
                    src_raster = rasterio.open(tile_p)
                    if src_raster.count > 0: # Ensure raster has bands
                        src_files_to_mosaic.append(src_raster)
                    else:
                        logging.warning(f"Tile {os.path.basename(tile_p)} has no bands, skipping from stitch.")
                        src_raster.close() # Close if not used
                except rasterio.errors.RasterioIOError as e_rio:
                    logging.error(f"Error opening tile {os.path.basename(tile_p)} for stitching: {e_rio}. Skipping.")
                    # Ensure raster_source is closed if it was partially opened or failed
                    if 'src_raster' in locals() and not src_raster.closed: src_raster.close()
            else:
                logging.warning(f"Invalid or empty tile path skipped for stitching: {tile_p}")

        if not src_files_to_mosaic:
            logging.error("No valid source tiles found for stitching.")
            return False

        logging.info(f"Stitching {len(src_files_to_mosaic)} valid tiles to {os.path.basename(output_mosaic_path)}...")
        os.makedirs(os.path.dirname(output_mosaic_path), exist_ok=True) # Ensure output directory exists
        
        # Merge function from rasterio
        # Using 'first' method: pixels from subsequent rasters overwrite earlier ones where they overlap.
        # Nodata=0: pixels with value 0 will be treated as nodata. This might be problematic if 0 is valid data.
        # Consider using the nodata value from the source rasters if consistent, or a more distinct value.
        # For now, using 0 as per original. If issues arise, this is a point for refinement.
        mosaic_array, output_transform = merge(src_files_to_mosaic, method='first', nodata=0, precision=7)
        
        # Get profile from the first source raster and update it for the mosaic
        output_profile = src_files_to_mosaic[0].profile.copy()
        output_profile.update({
            "driver": "GTiff",
            "height": mosaic_array.shape[1], # Array shape is (bands, height, width)
            "width": mosaic_array.shape[2],
            "transform": output_transform,
            "compress": "lzw", # LZW compression is lossless and common
            "nodata": 0 # Ensure nodata is set in the output profile
        })

        with rasterio.open(output_mosaic_path, "w", **output_profile) as dst_mosaic:
            dst_mosaic.write(mosaic_array)
            # Try to write band descriptions if available from the first source
            if src_files_to_mosaic[0].descriptions and len(src_files_to_mosaic[0].descriptions) == dst_mosaic.count:
                dst_mosaic.descriptions = src_files_to_mosaic[0].descriptions
                logging.info(f"Wrote {len(dst_mosaic.descriptions)} band descriptions to stitched mosaic: {os.path.basename(output_mosaic_path)}")
        
        logging.info(f"Stitched mosaic saved successfully: {os.path.basename(output_mosaic_path)}")
        return True
    except Exception as e_stitch:
        logging.error(f"Stitching process failed: {e_stitch}", exc_info=True)
        return False
    finally:
        # Ensure all opened rasterio source files are closed
        for src_raster_obj in src_files_to_mosaic:
            if src_raster_obj and not src_raster_obj.closed:
                src_raster_obj.close()

# ==============================================
#        MAIN EXECUTION (QtPy part)
# ==============================================
if __name__ == "__main__":
    # --- QtPy Imports ---
    # These need to be available before any Qt-dependent classes are defined.
    try:
        from qtpy import QtWidgets, QtCore, QtGui
        from qtpy.QtCore import Qt # For alignment flags
        from qtpy.QtWebEngineWidgets import QWebEngineView # Still needed for MapSelectionDialog
        # from qtpy import QtWebEngineCore # Not directly used, QWebChannel is separate
        # import pyqtgraph as pg # REMOVED as primary viewer, kept as optional install
        # pg.setConfigOptions(imageAxisOrder='col-major') # REMOVED
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
        from matplotlib.figure import Figure
        from qtpy.QtWebChannel import QWebChannel # For JS interaction in QWebEngineView
    except ImportError as e:
        # This is a critical failure if QtPy or a backend isn't installed.
        logging.critical(f"QtPy import failed: {e}. Please ensure QtPy and a backend (e.g., PyQt5 or PySide6) are installed.")
        # Attempt to show a message box if possible, otherwise print and exit.
        try:
            # Try a minimal import for QMessageBox if the main ones failed partially
            from PyQt5 import QtWidgets as PyQt5Widgets # Example for PyQt5
            app_temp = PyQt5Widgets.QApplication(sys.argv)
            PyQt5Widgets.QMessageBox.critical(None, "Fatal Error",
                                             f"Failed to load Qt libraries: {e}\n"
                                             "Please ensure QtPy and a Qt backend (PyQt5 or PySide6) are installed.\n"
                                             "Try: pip install qtpy PyQt5")
        except Exception: # Fallback to print if even minimal Qt fails
            print(f"CRITICAL ERROR: QtPy (or a compatible Qt binding like PyQt5/PySide6) is not installed. Flutter Earth cannot start.\n"
                  f"Error: {e}\n"
                  f"Please try running: pip install qtpy PyQt5")
        sys.exit(1) # Exit if GUI components can't be loaded.

    # --- Satellite Info Tab Widget ---
    def get_current_theme_colors():
        theme_name = APP_CONFIG.get('theme', DEFAULT_THEME_QT)
        return THEMES.get(theme_name, FLUTTERSHY_COLORS) # Default to Fluttershy if name is invalid


    class SatelliteInfoTab(QtWidgets.QWidget):
        def __init__(self, colors, parent=None):
            super().__init__(parent)
            self.colors = colors
            self.init_ui()
            self.populate_satellite_tree()
            self.apply_styles()

        def init_ui(self):
            layout = QtWidgets.QHBoxLayout(self)
            self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

            # Left pane: Satellite Tree
            self.satellite_tree = QtWidgets.QTreeWidget()
            self.satellite_tree.setHeaderLabels(["Satellites & Categories"])
            self.satellite_tree.currentItemChanged.connect(self.display_satellite_info)
            self.splitter.addWidget(self.satellite_tree)

            # Right pane: Details Display
            self.details_display = QtWidgets.QTextEdit()
            self.details_display.setReadOnly(True)
            self.details_display.setAcceptRichText(True) # Allow HTML for formatting
            self.splitter.addWidget(self.details_display)

            self.splitter.setSizes([250, 550]) # Initial sizes for panes
            layout.addWidget(self.splitter)
            self.setLayout(layout)

        def populate_satellite_tree(self):
            self.satellite_tree.clear()
            for category, sensor_list in SATELLITE_CATEGORIES.items():
                category_item = QtWidgets.QTreeWidgetItem(self.satellite_tree, [category])
                category_item.setFlags(category_item.flags() & ~QtCore.Qt.ItemIsSelectable) # Make category itself not selectable for details
                for sensor_key in sensor_list:
                    if sensor_key in SATELLITE_DETAILS:
                        sensor_display_name = f"{sensor_key} ({SATELLITE_DETAILS[sensor_key].get('type', 'N/A')})"
                        sensor_item = QtWidgets.QTreeWidgetItem(category_item, [sensor_display_name])
                        sensor_item.setData(0, QtCore.Qt.UserRole, sensor_key) # Store actual key
            self.satellite_tree.expandAll()

        def display_satellite_info(self, current_item, previous_item):
            if not current_item:
                self.details_display.clear()
                return

            sensor_key = current_item.data(0, QtCore.Qt.UserRole)
            if sensor_key and sensor_key in SATELLITE_DETAILS:
                details = SATELLITE_DETAILS[sensor_key]
                html_content = f"<h3>{sensor_key}</h3>"
                html_content += f"<p><b>Description:</b> {details.get('description', 'N/A')}</p>"
                html_content += f"<p><b>Type:</b> {details.get('type', 'N/A')}</p>"
                html_content += f"<p><b>Nominal Resolution:</b> {details.get('resolution_nominal', 'N/A')}</p>"
                html_content += f"<p><b>Revisit Interval:</b> {details.get('revisit_interval', 'N/A')}</p>"
                html_content += f"<p><b>Common Uses:</b> {details.get('common_uses', 'N/A')}</p>"
                
                use_categories = details.get('use_categories', [])
                if use_categories:
                    html_content += "<p><b>Use Categories:</b><ul>"
                    for cat in use_categories:
                        html_content += f"<li>{cat}</li>"
                    html_content += "</ul></p>"
                self.details_display.setHtml(html_content)
            else: # If a category header or non-sensor item is clicked (though categories are unselectable)
                self.details_display.setHtml(f"<p>Select a satellite from the list to view its details.</p><p><i>Category: {current_item.text(0)}</i></p>")


        def apply_styles(self):
            # Basic styling, can be expanded based on theme colors
            self.satellite_tree.setStyleSheet(f"QTreeWidget {{ border: 1px solid {self.colors['ACCENT_BORDER']}; background-color: {self.colors['INPUT_BG']}; color: {self.colors['INPUT_FG']}; }} QHeaderView::section {{ background-color: {self.colors['BUTTON_LAVENDER_BG']}; color: {self.colors['TEXT_COLOR']}; padding: 4px; border: none; }}")
            self.details_display.setStyleSheet(f"QTextEdit {{ border: 1px solid {self.colors['ACCENT_BORDER']}; background-color: {self.colors['INPUT_BG']}; color: {self.colors['INPUT_FG']}; padding: 5px; }}")
            # Splitter handle might need more specific styling if desired

        def update_theme(self, new_colors):
            self.colors = new_colors
            self.apply_styles()

    class SensorPriorityDialogQt(QtWidgets.QDialog):
        def __init__(self, parent, current_priority_list, all_sensor_names_list, colors):
            super().__init__(parent)
            self.setWindowTitle(FLUTTERSHY_TEXTS.get("sensor_priority_dialog_title", "Edit Sensor Priority"))
            self.setMinimumSize(400, 500)
            self.colors = colors # Store the passed colors
            self.current_priority_list = list(current_priority_list) # Work with a copy
            self.all_sensor_names = sorted(list(all_sensor_names_list))
            self.new_priority_list = None # Will store the result

            # Main layout
            layout = QtWidgets.QVBoxLayout(self)
            layout.setSpacing(10)
            layout.setContentsMargins(15, 15, 15, 15)

            instruction_label = QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("sensor_priority_instruction", "Drag to reorder..."))
            instruction_label.setWordWrap(True)
            layout.addWidget(instruction_label)

            self.table_widget = QtWidgets.QTableWidget()
            self.table_widget.setColumnCount(2)
            self.table_widget.setHorizontalHeaderLabels(["Order", "Sensor"])
            self.table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.table_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove) # Allows row drag-and-drop
            self.table_widget.setAlternatingRowColors(True) # Improves readability
            self.table_widget.setStyleSheet(self._get_table_stylesheet()) # Apply themed style

            # Populate table with current priority list
            for sensor_name in self.current_priority_list:
                if sensor_name in self.all_sensor_names: # Ensure sensor is known
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)
                    order_item = QtWidgets.QTableWidgetItem(str(row_position + 1))
                    order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable) # Not editable
                    sensor_item = QtWidgets.QTableWidgetItem(sensor_name)
                    sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable) # Not editable
                    self.table_widget.setItem(row_position, 0, order_item)
                    self.table_widget.setItem(row_position, 1, sensor_item)

            self.table_widget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch) # Sensor column stretches
            self.table_widget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # Order column fits content
            self.table_widget.verticalHeader().setVisible(False) # Hide vertical row numbers
            layout.addWidget(self.table_widget, 1) # Give table stretch factor

            # Button layout (horizontal)
            button_layout = QtWidgets.QHBoxLayout()
            self.up_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("sensor_priority_up_button", "Up"))
            self.down_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("sensor_priority_down_button", "Down"))
            self.add_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("sensor_priority_add_button", "Add..."))
            self.remove_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("sensor_priority_remove_button", "Remove"))

            self.up_button.clicked.connect(self.move_up)
            self.down_button.clicked.connect(self.move_down)
            self.add_button.clicked.connect(self.add_sensor)
            self.remove_button.clicked.connect(self.remove_sensor)

            button_layout.addWidget(self.up_button)
            button_layout.addWidget(self.down_button)
            button_layout.addStretch(1) # Push Add/Remove to the right
            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.remove_button)
            layout.addLayout(button_layout)
            
            # Dialog buttons (OK/Cancel)
            self.dialog_buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            self.dialog_buttons.accepted.connect(self.accept_changes)
            self.dialog_buttons.rejected.connect(self.reject)
            
            # Style OK/Cancel buttons from theme
            self.dialog_buttons.button(QtWidgets.QDialogButtonBox.Ok).setObjectName("okButtonSensorDialog")
            self.dialog_buttons.button(QtWidgets.QDialogButtonBox.Ok).setStyleSheet(
                f"background-color: {self.colors['BUTTON_PINK_BG']}; color: {self.colors['BUTTON_PINK_FG']}; font-weight: bold; padding: 5px 15px;"
            )
            self.dialog_buttons.button(QtWidgets.QDialogButtonBox.Cancel).setStyleSheet(
                f"background-color: {self.colors['BUTTON_LAVENDER_BG']}; color: {self.colors['TEXT_COLOR']}; padding: 5px 15px;"
            )

            layout.addWidget(self.dialog_buttons)
            self.setLayout(layout)
            self._renumber_order_column() # Initial numbering

        def _get_table_stylesheet(self):
            return f"""
                QTableWidget {{
                    background-color: {self.colors['INPUT_BG']}; color: {self.colors['INPUT_FG']};
                    border: 1px solid {self.colors['ACCENT_BORDER']}; border-radius: 4px; padding: 5px;
                    font-size: {QT_FLUTTER_FONT_SIZE_NORMAL};
                    gridline-color: {self.colors['ACCENT_BORDER']};
                }}
                QTableWidget::item {{ padding: 6px; }}
                QTableWidget::item:selected {{
                    background-color: {self.colors['BUTTON_PINK_BG']}; color: {self.colors['BUTTON_PINK_FG']};
                }}
                QHeaderView::section {{
                    background-color: {self.colors['BUTTON_LAVENDER_BG']}; color: {self.colors['TEXT_COLOR']};
                    padding: 4px; border: 1px solid {self.colors['ACCENT_BORDER']};
                    font-size: {QT_FLUTTER_FONT_SIZE_NORMAL}; font-weight: bold;
                }}"""

        def _renumber_order_column(self):
            for row in range(self.table_widget.rowCount()):
                item = self.table_widget.item(row, 0)
                if item:
                    item.setText(str(row + 1))
                else: # Should not happen if rows are populated correctly
                    new_item = QtWidgets.QTableWidgetItem(str(row + 1))
                    new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
                    self.table_widget.setItem(row, 0, new_item)

        def move_up(self):
            current_row = self.table_widget.currentRow()
            if current_row > 0:
                # Store contents of current row
                sensor_item_text = self.table_widget.item(current_row, 1).text()
                # Remove current row
                self.table_widget.removeRow(current_row)
                # Insert new row at previous position
                self.table_widget.insertRow(current_row - 1)
                # Create and set items for the new row
                order_item = QtWidgets.QTableWidgetItem() # Text will be set by renumber
                order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable)
                sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
                sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table_widget.setItem(current_row - 1, 0, order_item)
                self.table_widget.setItem(current_row - 1, 1, sensor_item)
                self._renumber_order_column()
                self.table_widget.setCurrentCell(current_row - 1, 0) # Reselect moved item

        def move_down(self):
            current_row = self.table_widget.currentRow()
            if current_row < self.table_widget.rowCount() - 1 and current_row != -1: # Ensure valid row and not last
                sensor_item_text = self.table_widget.item(current_row, 1).text()
                self.table_widget.removeRow(current_row)
                self.table_widget.insertRow(current_row + 1) # Insert after original position
                order_item = QtWidgets.QTableWidgetItem()
                order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable)
                sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
                sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table_widget.setItem(current_row + 1, 0, order_item)
                self.table_widget.setItem(current_row + 1, 1, sensor_item)
                self._renumber_order_column()
                self.table_widget.setCurrentCell(current_row + 1, 0) # Reselect moved item

        def add_sensor(self):
            current_sensors_in_list = [self.table_widget.item(i, 1).text() for i in range(self.table_widget.rowCount())]
            available_to_add = [s for s in self.all_sensor_names if s not in current_sensors_in_list]
            
            if not available_to_add:
                QtWidgets.QMessageBox.information(self, "All Friends Here!", "All available sensor friends are already in the list!", QtWidgets.QMessageBox.Ok)
                return

            sensor_to_add, ok = QtWidgets.QInputDialog.getItem(self,
                                                               FLUTTERSHY_TEXTS.get("sensor_priority_add_dialog_title", "Add Sensor"),
                                                               FLUTTERSHY_TEXTS.get("sensor_priority_add_dialog_label", "Select sensor to add:"),
                                                               available_to_add, 0, False) # editable=False
            if ok and sensor_to_add:
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                order_item = QtWidgets.QTableWidgetItem() # Text set by renumber
                order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable)
                sensor_item = QtWidgets.QTableWidgetItem(sensor_to_add)
                sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table_widget.setItem(row_position, 0, order_item)
                self.table_widget.setItem(row_position, 1, sensor_item)
                self._renumber_order_column()

        def remove_sensor(self):
            current_row = self.table_widget.currentRow()
            if current_row != -1: # If a row is selected
                sensor_name = self.table_widget.item(current_row, 1).text()
                reply = QtWidgets.QMessageBox.question(self, "Confirm Removal",
                                                       f"Are you sure you want to remove {sensor_name} from the priority list, sweetie?",
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.table_widget.removeRow(current_row)
                    self._renumber_order_column()

        def accept_changes(self):
            self._renumber_order_column() # Ensure order column is correct before extracting
            self.new_priority_list = [self.table_widget.item(i, 1).text() for i in range(self.table_widget.rowCount())]
            self.accept() # Close dialog with QDialog.Accepted status

        def get_updated_priority_list(self):
            return self.new_priority_list
    # --- Global state variables moved here for QtPy GUI ---

    # --- Index Analysis Pane (for the right side of the splitter) ---
    class IndexAnalysisPane(QtWidgets.QWidget):
        def __init__(self, colors, parent=None):
            super().__init__(parent)
            self.colors = colors # Store for potential future styling
            self.selected_indices_checkboxes = {}
            self._init_ui()
            # self.apply_styles() # If specific styling is needed for this pane

        def _init_ui(self):
            # Main layout for IndexAnalysisPane will be a horizontal splitter
            pane_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
            main_layout_for_pane = QtWidgets.QHBoxLayout(self) # Main layout to hold the splitter
            main_layout_for_pane.addWidget(pane_splitter)
            main_layout_for_pane.setContentsMargins(5, 5, 5, 5) # Small margins for the pane itself

            # --- Internal Left Widget (for Inputs, Outputs, Start Button) ---
            internal_left_widget = QtWidgets.QWidget()
            internal_left_layout = QtWidgets.QVBoxLayout(internal_left_widget)
            internal_left_layout.setContentsMargins(5,5,5,5)

            # 1. Input Selection Group (moves to internal left)
            self.input_group_box_ia = QtWidgets.QGroupBox("Input Rasters for Index Analysis")
            input_group_layout_ia = QtWidgets.QVBoxLayout(self.input_group_box_ia)
            input_buttons_layout_ia = QtWidgets.QHBoxLayout()
            self.add_files_button_ia = QtWidgets.QPushButton("Add Raster File(s)...")
            self.add_folder_button_ia = QtWidgets.QPushButton("Add Raster Folder...")
            input_buttons_layout_ia.addWidget(self.add_files_button_ia)
            input_buttons_layout_ia.addWidget(self.add_folder_button_ia)
            input_buttons_layout_ia.addStretch()
            input_group_layout_ia.addLayout(input_buttons_layout_ia)
            self.selected_files_list_widget_ia = QtWidgets.QListWidget()
            self.selected_files_list_widget_ia.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.selected_files_list_widget_ia.setMinimumHeight(100) # Adjusted min height
            input_group_layout_ia.addWidget(self.selected_files_list_widget_ia, 1) # Give list widget stretch
            self.remove_selected_button_ia = QtWidgets.QPushButton("Remove Selected") # Shorter text
            self.clear_list_button_ia = QtWidgets.QPushButton("Clear List")
            input_management_layout_ia = QtWidgets.QHBoxLayout()
            input_management_layout_ia.addWidget(self.remove_selected_button_ia)
            input_management_layout_ia.addWidget(self.clear_list_button_ia)
            input_management_layout_ia.addStretch()
            input_group_layout_ia.addLayout(input_management_layout_ia)
            internal_left_layout.addWidget(self.input_group_box_ia, 1) # Allow vertical stretch

            # 2. Output Selection Group (moves to internal left)
            self.output_group_box_ia = QtWidgets.QGroupBox("Output Settings for Index Analysis")
            output_group_layout_ia = QtWidgets.QFormLayout(self.output_group_box_ia)
            self.index_output_dir_label_ia = QtWidgets.QLabel("Output Directory:") # Shorter label
            self.index_output_dir_input_ia = QtWidgets.QLineEdit()
            self.index_output_dir_input_ia.setPlaceholderText("Select folder for indices...")
            self.index_browse_button_ia = QtWidgets.QPushButton("Browse...")
            index_output_dir_layout_ia = QtWidgets.QHBoxLayout()
            index_output_dir_layout_ia.addWidget(self.index_output_dir_input_ia)
            index_output_dir_layout_ia.addWidget(self.index_browse_button_ia)
            output_group_layout_ia.addRow(self.index_output_dir_label_ia, index_output_dir_layout_ia)
            internal_left_layout.addWidget(self.output_group_box_ia)

            # 3. Start Button (moves to internal left)
            self.start_index_analysis_button_ia = QtWidgets.QPushButton("🚀 Start Index Analysis")
            internal_left_layout.addWidget(self.start_index_analysis_button_ia, 0, QtCore.Qt.AlignRight)
            internal_left_layout.addStretch(0) # Minimal stretch at the bottom of left pane

            pane_splitter.addWidget(internal_left_widget)

            # --- Internal Right Widget (for Index Selection Checkboxes) ---
            internal_right_widget = QtWidgets.QWidget()
            internal_right_layout = QtWidgets.QVBoxLayout(internal_right_widget)
            internal_right_layout.setContentsMargins(5,5,5,5)

            # 4. Index Selection Group (moves to internal right)
            indices_group_box = QtWidgets.QGroupBox("Select Indices to Calculate")
            indices_group_layout = QtWidgets.QVBoxLayout(indices_group_box)
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QtWidgets.QWidget()
            scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
            scroll_layout.setAlignment(QtCore.Qt.AlignTop)

            for key, info in AVAILABLE_INDICES.items():
                # Create a layout for the checkbox and its help button
                index_item_layout = QtWidgets.QHBoxLayout()
                index_item_layout.setContentsMargins(0,0,0,0)
                index_item_layout.setSpacing(5)

                checkbox = QtWidgets.QCheckBox(f"{info.get('name', key)} ({key})")
                # Tooltip can still be useful for quick hover info
                checkbox.setToolTip(info.get('formula_desc', 'No detailed formula description available.'))
                self.selected_indices_checkboxes[key] = checkbox
                index_item_layout.addWidget(checkbox)

                help_title = f"{key} - {info.get('name', 'Index Information')}"
                help_text = f"<b>{info.get('name', key)}</b>\n\nFormula: {info.get('formula_desc', 'Not specified')}"
                help_button = create_help_q_button(help_title, help_text, self) # self is parent_widget
                index_item_layout.addWidget(help_button)
                index_item_layout.addStretch(1) # Push checkbox and help button to the left
                scroll_layout.addLayout(index_item_layout) # Add the combined layout
            scroll_area.setWidget(scroll_widget)
            indices_group_layout.addWidget(scroll_area)
            # indices_group_box.setMinimumHeight(200) # No longer needed as it will fill its pane
            internal_right_layout.addWidget(indices_group_box, 1) # Allow vertical stretch
            pane_splitter.addWidget(internal_right_widget)

            # Set initial sizes for the internal splitter (e.g., 60% for left, 40% for right)
            pane_splitter.setSizes([int(self.width() * 0.6) if self.width() > 0 else 300, 
                                    int(self.width() * 0.4) if self.width() > 0 else 200])


        def get_selected_indices(self):
            return [key for key, checkbox in self.selected_indices_checkboxes.items() if checkbox.isChecked()]

        def get_input_files(self):
            return [self.selected_files_list_widget_ia.item(i).text() for i in range(self.selected_files_list_widget_ia.count())]

        def get_output_dir(self):
            return self.index_output_dir_input_ia.text()

    class VectorDownloadTab(QtWidgets.QWidget):
        def __init__(self, colors, parent=None):
            super().__init__(parent)
            self.colors = colors
            try:
                self._init_ui()
                self.apply_styles() # Apply initial styles
            except Exception as e:
                logging.error(f"Error during VectorDownloadTab initialization: {e}", exc_info=True)
                # Fallback UI within the tab if its own init fails
                fallback_layout = QtWidgets.QVBoxLayout(self)
                error_label_text = f"Error initializing Vector Data Download tab content:\n{str(e)[:150]}...\n\nCheck logs for details. This might be due to issues with PyQtWebEngine system dependencies if the map functionality is also affected."
                error_label = QtWidgets.QLabel(error_label_text)
                error_label.setWordWrap(True)
                error_label.setStyleSheet("color: red; font-weight: bold;")
                fallback_layout.addWidget(error_label)
                self.setLayout(fallback_layout)
        def _init_ui(self):
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            form_layout = QtWidgets.QFormLayout()
            form_layout.setSpacing(10)
            form_layout.setLabelAlignment(QtCore.Qt.AlignRight) # Align labels to the right

            # Data Source Input
            self.source_input = QtWidgets.QLineEdit()
            self.source_input.setPlaceholderText("Enter Overpass API query, WFS URL, etc.")
            form_layout.addRow(QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("vector_source_label", "Data Source:")), self.source_input)

            # Source Type Dropdown
            # AOI Input for Vector Data
            self.vector_aoi_label = QtWidgets.QLabel("Area of Interest (AOI):")
            self.vector_aoi_input = QtWidgets.QLineEdit()
            self.vector_aoi_input.setPlaceholderText("e.g., minLon,minLat,maxLon,maxLat or [[lon,lat],...]")
            self.vector_aoi_map_button = QtWidgets.QPushButton("🗺️ Select from Map")
            self.vector_aoi_map_button.clicked.connect(self._open_map_for_vector_aoi)
            aoi_layout = QtWidgets.QHBoxLayout()
            aoi_layout.addWidget(self.vector_aoi_input, 1); aoi_layout.addWidget(self.vector_aoi_map_button)
            form_layout.addRow(self.vector_aoi_label, aoi_layout)
            self.source_type_combo = QtWidgets.QComboBox()
            self.source_type_combo.addItems(["Overpass API (OSM)", "WFS (Web Feature Service)", "Direct GeoJSON URL"]) # Add more as needed
            form_layout.addRow(QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("vector_type_label", "Source Type:")), self.source_type_combo)
            # Set "Custom Overpass Query" as the default to enable source and AOI inputs initially for Overpass
            # self.osm_feature_type_combo.setCurrentText("Custom Overpass Query") # Will be handled by radio buttons

            # --- Overpass Specific Options Group (initially hidden or managed by _on_source_type_changed) ---
            self.overpass_options_group = QtWidgets.QGroupBox("Overpass API Options")
            self.overpass_options_layout = QtWidgets.QVBoxLayout(self.overpass_options_group)

            # Radio buttons for Overpass query mode
            self.rb_group_overpass_mode = QtWidgets.QButtonGroup(self) # Exclusive selection
            self.rb_predefined_features = QtWidgets.QRadioButton("Select Predefined Features")
            self.rb_custom_query = QtWidgets.QRadioButton("Enter Custom Query")
            self.rb_group_overpass_mode.addButton(self.rb_predefined_features)
            self.rb_group_overpass_mode.addButton(self.rb_custom_query)
            
            overpass_mode_layout = QtWidgets.QHBoxLayout()
            overpass_mode_layout.addWidget(self.rb_predefined_features)
            overpass_mode_layout.addWidget(self.rb_custom_query)
            self.overpass_options_layout.addLayout(overpass_mode_layout)

            # Checkboxes for predefined features
            self.predefined_features_group = QtWidgets.QGroupBox("Predefined OSM Features")
            predefined_features_layout = QtWidgets.QVBoxLayout(self.predefined_features_group)
            self.cb_osm_roads = QtWidgets.QCheckBox("Roads (highway=*)")
            self.cb_osm_buildings = QtWidgets.QCheckBox("Buildings (building=*)")
            self.cb_osm_waterways = QtWidgets.QCheckBox("Waterways (waterway=*)")
            predefined_features_layout.addWidget(self.cb_osm_roads)
            predefined_features_layout.addWidget(self.cb_osm_buildings)
            predefined_features_layout.addWidget(self.cb_osm_waterways)
            self.overpass_options_layout.addWidget(self.predefined_features_group)

            # Add the Overpass options group to the main form layout (it will be shown/hidden)
            form_layout.addRow(self.overpass_options_group)

            # Connect signals for radio buttons and source type combo
            self.source_type_combo.currentTextChanged.connect(self._on_source_type_changed)
            self.rb_predefined_features.toggled.connect(self._on_overpass_query_mode_changed)
            # self.rb_custom_query.toggled.connect(self._on_overpass_query_mode_changed) # Only one radio needs to trigger

            # Output Directory
            output_dir_layout = QtWidgets.QHBoxLayout()
            self.output_dir_input_vd = QtWidgets.QLineEdit()
            self.output_dir_input_vd.setPlaceholderText("Select directory to save vector data...")
            self.output_dir_input_vd.setText(APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR)) # Default to main output
            browse_button_vd = QtWidgets.QPushButton("Browse...")
            browse_button_vd.setObjectName("browseButtonVector") # For specific styling if needed
            browse_button_vd.clicked.connect(self._browse_output_dir_vd)
            output_dir_layout.addWidget(self.output_dir_input_vd)
            output_dir_layout.addWidget(browse_button_vd)
            form_layout.addRow(QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("vector_output_dir_label", "Output Directory:")), output_dir_layout)

            # Output Format Dropdown
            self.output_format_combo = QtWidgets.QComboBox()
            self.output_format_combo.addItems(["GeoJSON", "Shapefile", "KML", "GPKG"]) # Common vector formats
            form_layout.addRow(QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("vector_format_label", "Output Format:")), self.output_format_combo)

            layout.addLayout(form_layout)
            layout.addStretch(1) # Push controls to the top

            # Start Download Button
            self.start_vector_download_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("vector_start_download_button", "Download Vectors"))
            self.start_vector_download_button.setObjectName("startButtonVector") # For specific styling
            self.start_vector_download_button.clicked.connect(self._start_vector_download_wrapper)
            layout.addWidget(self.start_vector_download_button, 0, QtCore.Qt.AlignRight)

            self._on_source_type_changed(self.source_type_combo.currentText()) # Initial UI state
            self.rb_custom_query.setChecked(True) # Default to custom query mode for Overpass

        def _open_map_for_vector_aoi(self):
            # Logic to open MapSelectionDialog and update self.vector_aoi_input
            # Similar to open_map_selection_dialog in the main app, but targets vector_aoi_input
            current_aoi_text = self.vector_aoi_input.text()
            initial_polygon_for_map = None
            initial_bbox_str_for_map = current_aoi_text # Assume it's a BBOX string by default for centering

            if current_aoi_text:
                try:
                    # Try to parse as polygon JSON first
                    parsed_coords = json.loads(current_aoi_text)
                    if isinstance(parsed_coords, list) and \
                       all(isinstance(p, list) and len(p) == 2 for p in parsed_coords) and \
                       len(parsed_coords) >= 3:
                        initial_polygon_for_map = parsed_coords # It's a polygon
                        # If it's a polygon, initial_bbox_str_for_map can be cleared or derived from polygon for better fit
                        lons = [p[0] for p in parsed_coords]
                        lats = [p[1] for p in parsed_coords]
                        initial_bbox_str_for_map = f"{min(lons)},{min(lats)},{max(lons)},{max(lats)}"
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass # Not a polygon JSON, initial_bbox_str_for_map (original text) will be used

            dialog = MapSelectionDialog(self, initial_bbox_str=initial_bbox_str_for_map, initial_polygon_coords_to_draw=initial_polygon_for_map)
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                selected_aoi_str = dialog.get_selected_polygon_coords_str() # This returns the JSON string of [[lon,lat],...]
                if selected_aoi_str:
                    self.vector_aoi_input.setText(selected_aoi_str)
                    logging.info(f"Vector AOI selected from map: {selected_aoi_str}")
        
        def _browse_output_dir_vd(self):
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory for Vector Data", self.output_dir_input_vd.text() or APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR))
            if directory:
                self.output_dir_input_vd.setText(directory)

        def _on_source_type_changed(self, source_type_text):
            is_overpass = (source_type_text == "Overpass API (OSM)")
            self.overpass_options_group.setVisible(is_overpass)

            if is_overpass:
                self._on_overpass_query_mode_changed() # Update internal Overpass UI state
            else: # Not Overpass API
                self.source_input.setEnabled(True)
                self.source_input.setPlaceholderText("Enter WFS URL, GeoJSON URL, etc.")
                self.vector_aoi_input.setEnabled(True)
                self.vector_aoi_map_button.setEnabled(True)
                self.vector_aoi_input.setPlaceholderText("e.g., minLon,minLat,maxLon,maxLat or [[lon,lat],...]")
        
        def _on_overpass_query_mode_changed(self):
            # This method is called when either radio button for Overpass mode is toggled,
            # or when the source type changes to Overpass.
            is_predefined_mode = self.rb_predefined_features.isChecked()
            is_custom_mode = self.rb_custom_query.isChecked()

            self.predefined_features_group.setEnabled(is_predefined_mode)
            
            self.source_input.setEnabled(is_custom_mode)
            if is_custom_mode:
                self.source_input.setPlaceholderText("Enter your full Overpass QL query here (use {{bbox}} for AOI)...")
            else:
                self.source_input.setPlaceholderText("Query will be auto-generated for predefined features.")
                self.source_input.clear()

            self.vector_aoi_input.setEnabled(is_custom_mode) # AOI input only for custom query
            self.vector_aoi_map_button.setEnabled(is_custom_mode)
            if is_custom_mode:
                self.vector_aoi_input.setPlaceholderText("AOI for custom query (e.g., minLon,minLat,maxLon,maxLat or [[lon,lat],...])")
            else:
                self.vector_aoi_input.setPlaceholderText("Uses Main Application BBOX for predefined features.")
                self.vector_aoi_input.clear()

        def _start_vector_download_wrapper(self):
            # Wrapper to run the download in a thread to keep UI responsive
            # For simplicity, this example runs it directly. For long tasks, use QThread.
            try:
                self._perform_vector_download()
            except Exception as e:
                logging.error(f"Vector download GUI error: {e}", exc_info=True)
                QtWidgets.QMessageBox.critical(self, "Download Error", f"An unexpected error occurred: {e}")
                status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_fail", "Vector download failed: {error}").format(error=str(e)))


        def _perform_vector_download(self):
            source_type = self.source_type_combo.currentText()
            data_source_text = self.source_input.text().strip()
            output_dir = self.output_dir_input_vd.text().strip()
            output_format = self.output_format_combo.currentText() # e.g., "GeoJSON"

            if not output_dir:
                QtWidgets.QMessageBox.warning(self, "Output Directory Missing", "Please specify an output directory.")
                return
            os.makedirs(output_dir, exist_ok=True)
            
            overpass_query = ""
            api_call_build_param = True # Default is True, library builds the query

            if source_type == "Overpass API (OSM)":
                aoi_param_for_overpass = ""
                
                if self.rb_custom_query.isChecked():
                    api_call_build_param = False # User provides full query
                    custom_query_text = self.source_input.text().strip()
                    if not custom_query_text:
                        QtWidgets.QMessageBox.warning(self, "Query Missing", "Please enter your custom Overpass QL query.")
                        return

                    aoi_text_custom = self.vector_aoi_input.text().strip()
                    # Only parse AOI if {{bbox}} is in the query, otherwise it's optional
                    if "{{bbox}}" in custom_query_text:
                        if not aoi_text_custom:
                            QtWidgets.QMessageBox.warning(self, "AOI Missing", FLUTTERSHY_TEXTS.get("vector_aoi_missing_error", "AOI is required for custom Overpass API queries that use {{bbox}}."))
                            return
                        try: # Try parsing as BBOX: "minLon,minLat,maxLon,maxLat"
                            coords = [float(c.strip()) for c in aoi_text_custom.split(',')]
                            if len(coords) == 4: 
                                aoi_param_for_overpass = f"({coords[1]},{coords[0]},{coords[3]},{coords[2]})" # (S,W,N,E)
                            else: raise ValueError("BBOX needs 4 coordinates.")
                        except (ValueError, TypeError):
                            try: # Try parsing as Polygon JSON: "[[lon,lat], [lon,lat], ...]"
                                poly_coords_lon_lat = json.loads(aoi_text_custom)
                                if isinstance(poly_coords_lon_lat, list) and len(poly_coords_lon_lat) >=3 and \
                                   all(isinstance(p, list) and len(p) == 2 for p in poly_coords_lon_lat):
                                    aoi_param_for_overpass = f'(poly:"{" ".join([f"{p[1]} {p[0]}" for p in poly_coords_lon_lat])}")' # lat lon space separated
                                else: raise ValueError("Polygon JSON needs list of [lon,lat] pairs.")
                            except (json.JSONDecodeError, ValueError, TypeError) as e_poly:
                                QtWidgets.QMessageBox.critical(self, "Invalid AOI", f"Could not parse AOI for custom query: {aoi_text_custom}. Error: {e_poly}")
                                return
                    overpass_query = custom_query_text.replace("{{bbox}}", aoi_param_for_overpass)

                elif self.rb_predefined_features.isChecked():
                    api_call_build_param = True # Library will build meta statements
                    aoi_text_main_app = APP_CONFIG.get('bbox_str', DEFAULT_BBOX_STR)
                    if not aoi_text_main_app:
                        QtWidgets.QMessageBox.warning(self, "AOI Missing", "Main application BBOX is not set. Please set it in 'Download Settings'.")
                        return
                    try: 
                        coords = [float(c.strip()) for c in aoi_text_main_app.split(',')]
                        if len(coords) == 4:
                            aoi_param_for_overpass = f"({coords[1]},{coords[0]},{coords[3]},{coords[2]})" # minLat,minLon,maxLat,maxLon for Overpass
                        else:
                            raise ValueError("Main BBOX needs 4 coordinates.")
                    except (ValueError, TypeError) as e_main_bbox:
                        QtWidgets.QMessageBox.critical(self, "Invalid Main BBOX", f"Could not parse main application BBOX '{aoi_text_main_app}'. Error: {e_main_bbox}")
                        return

                    selected_feature_queries = []
                    feature_name_parts = []
                    if self.cb_osm_roads.isChecked():
                        selected_feature_queries.append(f'way["highway"]{aoi_param_for_overpass};')
                        feature_name_parts.append("roads")
                    if self.cb_osm_buildings.isChecked():
                        selected_feature_queries.append(f'way["building"]{aoi_param_for_overpass};')
                        feature_name_parts.append("buildings")
                    if self.cb_osm_waterways.isChecked():
                        selected_feature_queries.append(f'way["waterway"]{aoi_param_for_overpass};')
                        feature_name_parts.append("waterways")
                    
                    if not selected_feature_queries:
                        QtWidgets.QMessageBox.warning(self, "No Features Selected", "Please select at least one predefined OSM feature type.")
                        return

                    way_queries_str = "\n  ".join(selected_feature_queries)
                    overpass_query = f"""(
                      {way_queries_str}
                      node(w);
                    );"""
                else: # No Overpass mode selected
                    QtWidgets.QMessageBox.warning(self, "Mode Not Selected", "Please select an Overpass query mode (Predefined or Custom).")
                    return
                
                status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_fetching", "Fetching...").format(source="Overpass API"))
                logging.info(f"Overpass Query (using 'overpass' library): {overpass_query[:200]}...")
                
                try:
                    # Initialize Overpass API client. Timeout is for the HTTP request.
                    # The [timeout:XX] in the query itself is for the server-side processing.
                    api = overpass.API(timeout=APP_CONFIG.get('DOWNLOAD_TIMEOUT', DEFAULT_DOWNLOAD_TIMEOUT))

                    # Use api_call_build_param to control how api.get is called
                    geojson_fc = api.get(overpass_query, build=api_call_build_param, verbosity='geom', responseformat="geojson")
                    
                    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_processing", "Processing..."))
                    # The result from api.get(..., responseformat="geojson") is already a GeoJSON dict.

                    # For Overpass, primarily save as GeoJSON
                    filename_feature_part = "_".join(feature_name_parts) if self.rb_predefined_features.isChecked() else "custom_query"
                    base_filename = f"osm_{filename_feature_part}_{datetime.now():%Y%m%d%H%M%S}"

                    output_filepath = os.path.join(output_dir, f"{base_filename}.geojson")
                    
                    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_saving", "Saving...").format(format="GeoJSON", filename=os.path.basename(output_filepath)))
                    with open(output_filepath, 'w', encoding='utf-8') as f:
                        json.dump(geojson_fc, f, indent=2) # geojson_fc is already the GeoJSON dict
                    
                    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_success", "Saved: {filename}").format(filename=os.path.basename(output_filepath)))
                    logging.info(f"Saved Overpass data as GeoJSON using 'overpass' library: {output_filepath}")
                    
                    if output_format != "GeoJSON":
                        QtWidgets.QMessageBox.information(self, "Format Note", FLUTTERSHY_TEXTS.get("vector_overpass_geojson_only_msg", "Data saved as GeoJSON."))
                except overpass.errors.OverpassError as e_op_lib: # Catch specific overpass library errors
                    logging.error(f"Overpass library error: {e_op_lib}", exc_info=True)
                    QtWidgets.QMessageBox.critical(self, "Overpass Library Error", f"Failed to fetch/process data using Overpass library: {e_op_lib}")
                    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_fail", "Failed: {error}").format(error=str(e_op_lib)))
                except Exception as e_proc:
                    logging.error(f"Error processing Overpass data: {e_proc}", exc_info=True)
                    QtWidgets.QMessageBox.critical(self, "Processing Error", f"Failed to process data: {e_proc}")
                    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("vector_status_fail", "Failed: {error}").format(error=str(e_proc)))

            elif source_type == "WFS (Web Feature Service)":
                # TODO: Implement WFS download logic
                QtWidgets.QMessageBox.information(self, "Not Implemented", "WFS download is not yet implemented.")
                logging.warning("WFS download attempted but not implemented.")
            elif source_type == "Direct GeoJSON URL":
                # TODO: Implement direct GeoJSON URL download
                QtWidgets.QMessageBox.information(self, "Not Implemented", "Direct GeoJSON URL download is not yet implemented.")
                logging.warning("Direct GeoJSON URL download attempted but not implemented.")

        def apply_styles(self):
            current_colors = get_current_theme_colors() # Get current theme colors
            self.colors = current_colors # Update internal colors
            self.output_dir_input_vd.setStyleSheet(f"color: {self.colors.get('INPUT_FG', '#000')}; background-color: {self.colors.get('INPUT_BG', '#FFF')};")
            self.source_input.setStyleSheet(f"color: {self.colors.get('INPUT_FG', '#000')}; background-color: {self.colors.get('INPUT_BG', '#FFF')};")
            # Add more specific styling if QComboBox, QPushButton need it beyond global styles.

        def update_theme(self, new_colors):
            self.colors = new_colors
            self.apply_styles()
        
        def _overpass_json_to_geojson(self, osm_json):
            features = []
            nodes_coords = {} # Store node_id: [lon, lat]

            for element in osm_json.get("elements", []):
                if element.get("type") == "node":
                    nodes_coords[element["id"]] = [element["lon"], element["lat"]]
            
            for element in osm_json.get("elements", []):
                props = element.get("tags", {})
                props["osm_id"] = element.get("id")
                props["osm_type"] = element.get("type")

                if element.get("type") == "way":
                    way_nodes_ids = element.get("nodes", [])
                    coordinates = []
                    for node_id in way_nodes_ids:
                        if node_id in nodes_coords:
                            coordinates.append(nodes_coords[node_id])
                    
                    if not coordinates: continue

                    geom_type = "LineString"
                    # Basic check if it's a closed way to make it a Polygon (for buildings, areas)
                    if len(coordinates) >= 4 and coordinates[0] == coordinates[-1] and \
                       ("building" in props or "area" in props or "landuse" in props or "natural" in props): # Heuristic
                        geom_type = "Polygon"
                        coordinates = [coordinates] # GeoJSON Polygons have an array of rings

                    if (geom_type == "LineString" and len(coordinates) >= 2) or \
                       (geom_type == "Polygon" and len(coordinates[0]) >= 4):
                        features.append({"type": "Feature", "properties": props, "geometry": {"type": geom_type, "coordinates": coordinates}})
            
            return {"type": "FeatureCollection", "features": features}

    # --- Data Viewer Tab (for Post Processing) ---
    class DataViewerTab(QtWidgets.QWidget):
        def __init__(self, colors, parent=None):
            super().__init__(parent)
            self.colors = colors
            self.current_filepath = None
            self.canvas = None # Will hold the Matplotlib FigureCanvas
            self.figure = None # Matplotlib Figure
            self.ax = None # Matplotlib Axes

            self.vector_layers_data = [] # To store loaded vector data
            try:
                self._init_ui()
            except Exception as e:
                logging.error(f"Error during DataViewerTab._init_ui(): {e}", exc_info=True)
                # Fallback UI if Matplotlib fails
                error_label = QtWidgets.QLabel(f"Failed to initialize Data Viewer (Matplotlib) UI:\n{str(e)[:200]}")
                error_label.setWordWrap(True)
                error_label.setAlignment(QtCore.Qt.AlignCenter)
                fallback_layout = QtWidgets.QVBoxLayout(self)
                fallback_layout.addWidget(error_label)
            
            if self.canvas: # Ensure canvas was created before connecting events
                self.canvas.mpl_connect('scroll_event', self._on_scroll_zoom)

        def _init_ui(self):
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0) # Use full space

            # Matplotlib Figure and Canvas
            self.figure = Figure(figsize=(5, 4), dpi=100) # Adjust figsize and dpi as needed
            self.canvas = FigureCanvas(self.figure)
            self.ax = self.figure.add_subplot(111)
            self.ax.set_axis_off() # Turn off axis numbers and ticks by default
            try: # tight_layout can sometimes fail with certain backends or figure states
                # Add a check for self.figure before calling tight_layout
                if self.figure is None:
                    logging.error("DataViewerTab: self.figure is None before tight_layout. UI initialization might have failed.")
                    # Optionally, re-initialize figure and ax here if it makes sense,
                    # or ensure _init_ui correctly sets them up even on partial failure.
                    return # Cannot proceed without a figure
                self.figure.tight_layout() 
            except Exception as e_tight:
                logging.warning(f"Matplotlib tight_layout failed: {e_tight}")


            # Add Matplotlib Navigation Toolbar
            self.toolbar = NavigationToolbar(self.canvas, self) # 'self' is the parent QWidget for toolbar
            layout.addWidget(self.toolbar)

            # --- Unified Data Loading Controls ---
            data_load_controls_layout = QtWidgets.QHBoxLayout()

            # New: Sample Site Selector
            self.sample_site_label = QtWidgets.QLabel("Quick Load Sample Site:")
            data_load_controls_layout.addWidget(self.sample_site_label)

            self.sample_site_selector_combo = QtWidgets.QComboBox()
            self.sample_site_selector_combo.addItem("Select a sample...") # Placeholder item at index 0
            for sample_key in ALL_SAMPLE_CONFIGS.keys():
                self.sample_site_selector_combo.addItem(sample_key)
            self.sample_site_selector_combo.setToolTip("Load a pre-defined sample dataset if it has been downloaded.")
            self.sample_site_selector_combo.currentIndexChanged.connect(self._on_sample_site_selected)
            data_load_controls_layout.addWidget(self.sample_site_selector_combo)

            data_load_controls_layout.addSpacing(20) # Add some visual separation

            self.load_data_button = QtWidgets.QPushButton("Load Custom Data Layer") # Renamed for clarity
            self.load_data_button.setToolTip("Load a raster or vector data layer.")
            
            # Create a menu for the button
            load_data_menu = QtWidgets.QMenu(self.load_data_button)
            
            load_raster_action = load_data_menu.addAction("Load Custom Raster Layer...")
            load_raster_action.setToolTip("Load a GeoTIFF (.tif, .tiff) raster layer.")
            load_raster_action.triggered.connect(self.load_raster_file_action)
            
            load_vector_action = load_data_menu.addAction("Load Vector Layer...")
            load_vector_action.setToolTip("Load a Shapefile (.shp) or GeoJSON (.geojson) layer.")
            load_vector_action.triggered.connect(self._load_vector_layer_action)
            
            self.load_data_button.setMenu(load_data_menu)
            data_load_controls_layout.addWidget(self.load_data_button)
            
            self.clear_vectors_button = QtWidgets.QPushButton("Clear Vector Layers")
            self.clear_vectors_button.setToolTip("Remove all loaded vector layers from the map.")
            self.clear_vectors_button.clicked.connect(self._clear_vector_layers_action)
            data_load_controls_layout.addWidget(self.clear_vectors_button)
            data_load_controls_layout.addStretch()
            layout.addLayout(data_load_controls_layout)

            # Create a QFrame to act as a bordered container for the canvas
            canvas_container_frame = QtWidgets.QFrame() # Frame for canvas
            border_thickness = 2
            border_color = self.colors.get('ACCENT_BORDER', '#888888')
            canvas_container_frame.setStyleSheet(
                f"QFrame {{ border: {border_thickness}px solid {border_color}; border-radius: 3px; }}"
            )
            canvas_container_layout = QtWidgets.QVBoxLayout(canvas_container_frame)
            canvas_container_layout.setContentsMargins(0, 0, 0, 0) 
            canvas_container_layout.addWidget(self.canvas)

            layout.addWidget(canvas_container_frame, 1) # Add the bordered frame (containing canvas)

        def _load_vector_layer_action(self):
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Load Vector Layer",
                APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR),
                "Vector Files (*.shp *.geojson *.json);;Shapefiles (*.shp);;GeoJSON (*.geojson *.json);;All Files (*)"
            )
            if not filepath:
                return

            try:
                geometries = self._parse_vector_file(filepath)
                if geometries:
                    # Simple default style for now, can be expanded
                    style = {'edgecolor': 'cyan', 'facecolor': 'none', 'linewidth': 1.2, 'alpha': 0.75}
                    self.vector_layers_data.append({'geometries': geometries, 'filepath': filepath, 'style': style})
                    self._redraw_display() # Redraw to show new layer
                    logging.info(f"Loaded and displayed vector layer: {os.path.basename(filepath)}")
                else:
                    logging.warning(f"No geometries found or parsed from {filepath}")
                    QtWidgets.QMessageBox.information(self, "Empty Layer", f"No displayable geometries found in {os.path.basename(filepath)}.")
            except Exception as e:
                logging.error(f"Error loading vector layer {filepath}: {e}", exc_info=True)
                QtWidgets.QMessageBox.critical(self, "Vector Load Error", f"Failed to load {os.path.basename(filepath)}:\n{e}")

        def _clear_vector_layers_action(self):
            # Clear existing vector layers and redraw
            self.vector_layers_data = []
            self._redraw_display() # Redraw (will draw raster if present, but no vectors)
            logging.info("Cleared all vector overlays.")

        def _on_sample_site_selected(self, index):
            if index == 0: # Placeholder "Select a sample..." is selected
                # Optionally, you could clear the display here if desired,
                # or simply do nothing and wait for another action.
                # self.load_specific_raster(None) # Uncomment to clear raster when placeholder is chosen
                return

            selected_key = self.sample_site_selector_combo.currentText()
            if not selected_key or selected_key not in ALL_SAMPLE_CONFIGS:
                logging.warning(f"Invalid sample key '{selected_key}' from dropdown.")
                return

            config = ALL_SAMPLE_CONFIGS[selected_key]
            
            sample_output_dir = os.path.join(SCRIPT_BASE_PATH, config["output_subdir"])
            sample_file_name = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
            expected_sample_filepath = os.path.join(sample_output_dir, sample_file_name)

            if os.path.exists(expected_sample_filepath):
                self.load_specific_raster(expected_sample_filepath)
                logging.info(f"Loaded sample site '{selected_key}' from dropdown: {expected_sample_filepath}")
            else:
                self.load_specific_raster(None) # Clear display if sample not found
                logging.warning(f"Sample file for '{selected_key}' not found at: {expected_sample_filepath}")
                QtWidgets.QMessageBox.information(
                    self, 
                    "Sample Data Not Found", 
                    f"The sample data for '{config['area_name']}' ('{os.path.basename(expected_sample_filepath)}') has not been downloaded yet.\n\n"
                    "It might be downloadable on application startup if you choose 'Yes' when prompted, "
                    "or if the application is restarted with this sample as the default."
                )

        def _parse_vector_file(self, filepath):
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.shp':
                return self._parse_shapefile(filepath)
            elif ext in ['.geojson', '.json']:
                return self._parse_geojson(filepath)
            else:
                raise ValueError(f"Unsupported vector file type: {ext}")

        def _parse_shapefile(self, filepath):
            # Uses global `shapefile` (pyshp)
            geometries = []
            try:
                with shapefile.Reader(filepath) as sf:
                    for shape_rec in sf.iterShapes():
                        # We are interested in POLYGON, POLYGONZ, POLYGONM
                        if shape_rec.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM, 5, 15, 25]:
                            part_indices = list(shape_rec.parts) + [len(shape_rec.points)]
                            for i in range(len(part_indices) - 1):
                                start = part_indices[i]
                                end = part_indices[i+1]
                                part_coords = shape_rec.points[start:end] # List of [x,y]
                                if len(part_coords) >= 3: # Need at least 3 points for a polygon
                                     geometries.append(part_coords)
            except Exception as e:
                logging.error(f"Error reading shapefile {filepath} with pyshp: {e}", exc_info=True)
                raise
            return geometries

        def _parse_geojson(self, filepath):
            # Uses global `json`
            geometries = []
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)

                features_to_process = []
                if geojson_data.get("type") == "FeatureCollection":
                    features_to_process = geojson_data.get("features", [])
                elif geojson_data.get("type") == "Feature":
                    features_to_process = [geojson_data]
                elif geojson_data.get("type") in ["Polygon", "MultiPolygon"]:
                    features_to_process = [{"geometry": geojson_data}]

                for feature in features_to_process:
                    geom = feature.get("geometry")
                    if not geom: continue
                    geom_type = geom.get("type")
                    coordinates = geom.get("coordinates")
                    if not coordinates: continue

                    if geom_type == "Polygon":
                        # Exterior ring: coordinates[0] which is a list of [x,y] points
                        if coordinates and len(coordinates[0]) >= 3:
                            geometries.append(coordinates[0])
                    elif geom_type == "MultiPolygon":
                        # List of Polygons; each polygon is a list of rings
                        for polygon_coords_set in coordinates:
                            if polygon_coords_set and len(polygon_coords_set[0]) >= 3:
                                geometries.append(polygon_coords_set[0])
            except Exception as e:
                logging.error(f"Error parsing GeoJSON {filepath}: {e}", exc_info=True)
                raise
            return geometries

        def load_raster_file_action(self): # Renamed from load_raster_file to avoid conflict
            initial_dir = APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR)
            filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Raster File", initial_dir, "GeoTIFF Files (*.tif *.tiff);;All Files (*)")
            if filepath:
                self.load_specific_raster(filepath)

        def _on_scroll_zoom(self, event):
            """Handle mouse scroll event for zooming on Matplotlib canvas."""
            if event.inaxes != self.ax or self.ax is None:
                return

            zoom_factor = 1.1
            if event.button == 'up': # Scroll up (zoom in)
                 scale_factor = 1 / zoom_factor
            elif event.button == 'down': # Scroll down (zoom out)
                 scale_factor = zoom_factor
            else: # Other scroll event or no step
                return

            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()

            xdata = event.xdata # Mouse x position in data coords
            ydata = event.ydata # Mouse y position in data coords

            if xdata is None or ydata is None: # If mouse is outside plot area, zoom to center
                xdata = (cur_xlim[0] + cur_xlim[1]) / 2
                ydata = (cur_ylim[0] + cur_ylim[1]) / 2

            new_xlim = [
                xdata - (xdata - cur_xlim[0]) * scale_factor,
                xdata + (cur_xlim[1] - xdata) * scale_factor
            ]
            new_ylim = [
                ydata - (ydata - cur_ylim[0]) * scale_factor,
                ydata + (cur_ylim[1] - ydata) * scale_factor
            ]

            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.canvas.draw_idle()

        def _scale_band_to_uint8(self, band_data, nodataval=None, band_name_for_log="band"):
            """Scales a single band to 0-255 uint8 for display, handling NaNs and nodata."""
            # Create a mask of valid pixels
            if nodataval is not None:
                # If nodata is present, also consider NaNs as invalid if they exist
                valid_pixels_mask = (band_data != nodataval) & numpy.isfinite(band_data)
            else:
                valid_pixels_mask = numpy.isfinite(band_data) # Only check for NaNs/Infs
            
            valid_pixels = band_data[valid_pixels_mask]
            
            if valid_pixels.size == 0:
                logging.debug(f"Scale_uint8 ({band_name_for_log}): No valid pixels after masking. Returning zeros.")
                return numpy.zeros_like(band_data, dtype=numpy.uint8)
            
            # Use 2nd and 98th percentiles for robust contrast stretch
            p2, p98 = numpy.percentile(valid_pixels, (2, 98))
            logging.debug(f"Scale_uint8 ({band_name_for_log}): "
                          f"p2={p2:.4f}, p98={p98:.4f}, "
                          f"min_valid={valid_pixels.min():.4f}, max_valid={valid_pixels.max():.4f}, "
                          f"nodataval_used={nodataval}")
            
            # Clip data to p2-p98 range, then scale to 0-1
            # Handle case where p2 and p98 are equal (or very close) to avoid division by zero
            if numpy.isclose(p2, p98):
                # If range is effectively zero, map all valid pixels to mid-gray (128)
                # and others (nodata/nan) to 0.
                scaled_norm = numpy.zeros_like(band_data, dtype=float)
                scaled_norm[valid_pixels_mask] = 0.5 # Mid-gray for valid pixels
            else:
                # Apply clipping and scaling
                data_clipped = numpy.clip(band_data, p2, p98)
                scaled_norm = (data_clipped - p2) / (p98 - p2)
            
            # Convert scaled 0-1 data to 0-255 uint8
            # Pixels outside valid_pixels_mask (NaNs, nodata) will become 0 after nan_to_num if they were NaN in scaled_norm.
            # If they were nodata and became 0 due to clipping to p2 (if p2=0), they remain 0.
            scaled_uint8 = (numpy.nan_to_num(scaled_norm, nan=0.0) * 255).astype(numpy.uint8)
            
            logging.debug(f"Scale_uint8 ({band_name_for_log}): Output uint8 min={scaled_uint8.min()}, "
                          f"max={scaled_uint8.max()}, mean={scaled_uint8.mean():.2f}")
            return scaled_uint8

        def _redraw_display(self):
            if not self.ax or not self.canvas:
                logging.error("DataViewerTab: Matplotlib canvas/axes not initialized. Cannot redraw.")
                return

            self.ax.clear() # Clear everything: raster, old vector patches

            # 1. Draw Raster
            if self.current_filepath and os.path.exists(self.current_filepath):
                logging.info(f"DataViewerTab: Redrawing raster {os.path.basename(self.current_filepath)}")
                try:
                    with rasterio.open(self.current_filepath) as src:
                        if src.count == 0:
                            logging.warning(f"Raster {os.path.basename(self.current_filepath)} has no bands.")
                            self.ax.text(0.5, 0.5, "No bands in raster", ha='center', va='center', transform=self.ax.transAxes)
                        elif src.count >= 3:
                            r_band_raw = src.read(1).astype(numpy.float32) # Read as float32 for scaling
                            g_band_raw = src.read(2).astype(numpy.float32)
                            b_band_raw = src.read(3).astype(numpy.float32)

                            r_band = self._scale_band_to_uint8(r_band_raw, src.nodatavals[0] if src.nodatavals and len(src.nodatavals)>0 else None, "R")
                            g_band = self._scale_band_to_uint8(g_band_raw, src.nodatavals[1] if src.nodatavals and len(src.nodatavals)>1 else None, "G")
                            b_band = self._scale_band_to_uint8(b_band_raw, src.nodatavals[2] if src.nodatavals and len(src.nodatavals)>2 else None, "B")
                            rgb_image_display = numpy.dstack((r_band, g_band, b_band)) # Use dstack for (H, W, C)
                            self.ax.imshow(rgb_image_display)
                            logging.info(f"Displayed RGB raster (bands 1,2,3): {os.path.basename(self.current_filepath)}")
                        else: # Single band (or 2 bands, display first)
                            band_data_raw = src.read(1).astype(numpy.float32)
                            nodataval = src.nodatavals[0] if src.nodatavals and len(src.nodatavals)>0 else None
                            # Use the _scale_band_to_uint8 method for consistent display
                            # This method handles nodata, NaNs, and scales to 0-255 uint8.
                            scaled_gray_band = self._scale_band_to_uint8(band_data_raw, nodataval, "Grayscale")
                            self.ax.imshow(scaled_gray_band, cmap='gray') # Display the scaled uint8 band
                            logging.info(f"Displayed grayscale raster (band 1): {os.path.basename(self.current_filepath)}")
                    self.ax.set_title(os.path.basename(self.current_filepath), fontsize=10)
                except Exception as e_display:
                    logging.error(f"Error displaying raster {os.path.basename(self.current_filepath)}: {e_display}", exc_info=True)
                    self.ax.text(0.5, 0.5, f"Error displaying raster:\n{str(e_display)[:50]}...", color='r', ha='center', va='center', transform=self.ax.transAxes, fontsize=9)
            else: # No raster loaded or path invalid
                self.ax.set_title("Data Viewer", fontsize=10) # Default title

            # 2. Draw Vector Overlays
            # Storing patches is useful if we want to remove them individually later,
            # but since ax.clear() is called, we just need to redraw them.
            for layer_data in self.vector_layers_data:
                style = layer_data.get('style', {'edgecolor': 'blue', 'facecolor': 'none', 'linewidth': 1})
                for polygon_coords in layer_data['geometries']:
                    if polygon_coords and len(polygon_coords) >= 3:
                        poly_patch = matplotlib.patches.Polygon(
                            numpy.array(polygon_coords), closed=True, **style
                        )
                        self.ax.add_patch(poly_patch)

            self.ax.set_axis_off()

            # Adjust view limits
            if self.current_filepath:
                # If raster is shown, its extent is primary. Matplotlib imshow handles this.
                pass
            elif self.vector_layers_data: # Only vectors are loaded
                self.ax.autoscale_view()
                self.ax.set_title(f"{len(self.vector_layers_data)} vector layer(s) loaded", fontsize=10)

            self.canvas.draw_idle()

        def load_specific_raster(self, filepath):
            """Sets the current raster file and triggers a full redraw of the display."""
            if filepath and os.path.exists(filepath):
                self.current_filepath = filepath
                logging.info(f"DataViewerTab: Set raster to {os.path.basename(filepath)}.")
            else:
                self.current_filepath = None
                logging.warning(f"DataViewerTab: Invalid raster path: {filepath}. Raster display will be cleared.")
            
            # Synchronize the sample site selector dropdown
            if filepath and os.path.exists(filepath):
                found_match_in_samples = False
                for key, config in ALL_SAMPLE_CONFIGS.items():
                    sample_output_dir_check = os.path.join(SCRIPT_BASE_PATH, config["output_subdir"])
                    sample_file_name_check = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
                    expected_sample_filepath_check = os.path.join(sample_output_dir_check, sample_file_name_check)
                    
                    if os.path.normpath(filepath) == os.path.normpath(expected_sample_filepath_check):
                        index_to_select = self.sample_site_selector_combo.findText(key)
                        if index_to_select != -1:
                            self.sample_site_selector_combo.blockSignals(True)
                            self.sample_site_selector_combo.setCurrentIndex(index_to_select)
                            self.sample_site_selector_combo.blockSignals(False)
                        found_match_in_samples = True
                        break 
                if not found_match_in_samples: # Loaded a custom raster not in samples
                    if self.sample_site_selector_combo.currentIndex() != 0: # If not already on placeholder
                        self.sample_site_selector_combo.blockSignals(True)
                        self.sample_site_selector_combo.setCurrentIndex(0) # Set to "Select a sample..."
                        self.sample_site_selector_combo.blockSignals(False)
            elif filepath is None: # Raster display was cleared
                if self.sample_site_selector_combo.currentIndex() != 0: # If not already on placeholder
                    self.sample_site_selector_combo.blockSignals(True)
                    self.sample_site_selector_combo.setCurrentIndex(0) # Reset to placeholder
                    self.sample_site_selector_combo.blockSignals(False)

            self._redraw_display()

    is_processing_qt = False
    cancel_requested_qt = False # UI cancellation request flag
    is_verifying_qt = False
    processing_thread_instance = None
    verification_thread_instance = None
    samples_to_download_queue_qt = [] # Queue for pending sample downloads

    sample_download_thread_instance = None # For the sample data download

    # --- Determine script base path ---
    # Handles bundled (frozen) and normal script execution paths
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        SCRIPT_BASE_PATH = sys._MEIPASS
    else:
        # Normal execution
        SCRIPT_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()


    # --- End Global state variables ---
    app = QtWidgets.QApplication(sys.argv)

    # --- Helper function for creating help buttons ---
    def create_help_q_button(help_title, help_text, parent_widget):
        help_btn = QtWidgets.QPushButton("❓") # Using an emoji for help
        help_btn.setObjectName("HelpButton") 
        help_btn.setToolTip("Click for help")
        # Stylesheet will be applied globally via get_stylesheet_qt
        help_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        help_btn.setFixedSize(24, 24) # Make it small and square-ish
        help_btn.setStyleSheet("QPushButton#HelpButton { font-size: 10pt; padding: 0px; margin: 0px; border-radius: 12px; }") # More specific style
        
        def show_help():
            # Create a QMessageBox for better control over styling and word wrap
            dialog = QtWidgets.QDialog(parent_widget)
            dialog.setWindowTitle(help_title)
            
            layout = QtWidgets.QVBoxLayout(dialog)
            text_browser = QtWidgets.QTextBrowser()

            # Set larger font for the text browser
            font = text_browser.font()
            try:
                # QT_FLUTTER_FONT_SIZE_NORMAL is like "11pt"
                base_font_size = int(QT_FLUTTER_FONT_SIZE_NORMAL.replace('pt', ''))
                font.setPointSize(base_font_size + 2) # e.g., 11pt -> 13pt
            except ValueError: # Fallback if parsing fails
                font.setPointSize(13) # Default to 13pt
            text_browser.setFont(font)

            text_browser.setHtml(help_text) # QTextBrowser handles HTML well
            text_browser.setOpenExternalLinks(True)
            layout.addWidget(text_browser)
            
            # Apply theme to OK button
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
            ok_button = button_box.button(QtWidgets.QDialogButtonBox.Ok)
            current_colors_for_dialog = get_current_theme_colors()
            ok_button.setStyleSheet(
                f"background-color: {current_colors_for_dialog['BUTTON_PINK_BG']};"
                f"color: {current_colors_for_dialog['BUTTON_PINK_FG']};"
                f"padding: 5px 15px; font-weight: bold;")
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout) # Ensure layout is set
            dialog.adjustSize()      # Adjust dialog size to content
            
            # Optional: Set a maximum size to prevent overly large dialogs
            if parent_widget and parent_widget.screen(): # Check if parent_widget and its screen are valid
                screen_geo = parent_widget.screen().availableGeometry()
                dialog.setMaximumWidth(int(screen_geo.width() * 0.7))  # 70% of screen width
                dialog.setMaximumHeight(int(screen_geo.height() * 0.8)) 
            
            dialog.exec_()

        help_btn.clicked.connect(show_help)
        return help_btn

    # --- Helper function for creating a label with a help button and a colon ---
    def create_form_label_with_help_qt(base_text_with_or_without_colon, help_title, help_text, parent_widget):
        label_text_no_colon = base_text_with_or_without_colon.rstrip(': ')
        
        container_widget = QtWidgets.QWidget() 
        label_widget = QtWidgets.QLabel(label_text_no_colon)
        help_button = create_help_q_button(help_title, help_text, parent_widget)
        colon_widget = QtWidgets.QLabel(":") 
        
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0) 
        layout.setSpacing(3) 
        layout.addWidget(label_widget)
        layout.addWidget(help_button)
        layout.addWidget(colon_widget)
        layout.addStretch(1) 
        container_widget.setLayout(layout) 
        return container_widget 

    # --- "About" Dialog Function ---
    def show_about_dialog_qt():
        current_colors = get_current_theme_colors() 
        title = FLUTTERSHY_TEXTS.get("about_dialog_title", "About Flutter Earth")
        
        version_info = f"Version: {SCRIPT_VERSION}"
        tagline = FLUTTERSHY_TEXTS.get("about_dialog_tagline", "Gently downloading GEE data with QtPy!")
        features_header = "\nMajor Features:"
        features_list = [
            "🌸 Multi-sensor support with priority",
            "🌼 Cloud masking & quality mosaics",
            "🦋 Interactive map for BBOX/Polygon selection (via Leaflet)",
            "☀️ Configurable processing parameters",
            "🛰️ Satellite connectivity verification",
            "🎨 Themed interface (Fluttershy & Night Mode)"
        ]
        closing_remark = "\n\nMay your downloads be swift and your data clear!"
        
        about_text = f"{version_info}\n{tagline}\n{features_header}\n" + "\n".join(features_list) + closing_remark
        
        dialog = QtWidgets.QDialog(main_window) # Parent to main_window
        dialog.setWindowTitle(title) # Title is set
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        text_browser = QtWidgets.QTextBrowser()
        # Set larger font for the text browser
        font = text_browser.font()
        try:
            base_font_size = int(QT_FLUTTER_FONT_SIZE_NORMAL.replace('pt', ''))
            font.setPointSize(base_font_size + 2) # e.g., 11pt -> 13pt
        except ValueError: # Fallback if parsing fails
            font.setPointSize(13) # Default to 13pt
        text_browser.setFont(font)

        text_browser.setPlainText(about_text) # Use setPlainText for simple text with newlines
        text_browser.setOpenExternalLinks(True) # If any links were present
        layout.addWidget(text_browser)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        ok_button = button_box.button(QtWidgets.QDialogButtonBox.Ok)
        ok_button.setStyleSheet( # Use current_colors from the scope of show_about_dialog_qt
            f"background-color: {get_current_theme_colors()['BUTTON_PINK_BG']};"
            f"color: {get_current_theme_colors()['BUTTON_PINK_FG']};"
            f"padding: 5px 15px; font-weight: bold;") # Corrected to use get_current_theme_colors()
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout) # Ensure layout is set
        dialog.adjustSize()      # Adjust dialog size to content
        # Optional: Set a maximum size (similar to help dialog, using main_window.screen())
        if main_window and main_window.screen():
            screen_geo = main_window.screen().availableGeometry()
            dialog.setMaximumWidth(int(screen_geo.width() * 0.75)) 
            dialog.setMaximumHeight(int(screen_geo.height() * 0.8)) # 80% of screen height
        dialog.exec_()

    # --- Application Guide Dialog Function ---
    # --- Create and Show Splash Screen ---
    splash_pixmap_width = 650  # Define width
    splash_pixmap_height = 400 # Define height
    splash_pixmap = QtGui.QPixmap(splash_pixmap_width, splash_pixmap_height) # Use defined variables
    splash_pixmap.fill(Qt.transparent) 

    splash_colors = FLUTTERSHY_COLORS 
    painter = QtGui.QPainter(splash_pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)

    gradient = QtGui.QLinearGradient(0, 0, 0, splash_pixmap_height)
    gradient.setColorAt(0.0, QtGui.QColor(splash_colors.get("BG_FRAME", "#FFF5FA")))
    gradient.setColorAt(1.0, QtGui.QColor(splash_colors.get("BG_MAIN", "#FEFEFA")))
    painter.fillRect(splash_pixmap.rect(), gradient)

    painter.setPen(QtGui.QPen(QtGui.QColor(splash_colors.get("ACCENT_BORDER", "#E0B0E0")), 2))
    painter.drawRoundedRect(splash_pixmap.rect().adjusted(1, 1, -1, -1), 15, 15)

    splash_font_title = QtGui.QFont(QT_FLUTTER_FONT_FAMILY, 24, QtGui.QFont.Bold) # Larger for title
    splash_font_subtitle = QtGui.QFont(QT_FLUTTER_FONT_FAMILY, 14, QtGui.QFont.Normal) # Smaller for subtitle
    
    title_text = "Flutter Earth 🌍"
    subtitle_texts = ["Exploring the World.", "Downloading the World."]
    
    painter.setFont(splash_font_title)
    painter.setPen(QtGui.QColor(splash_colors.get("TEXT_COLOR", "#5D4037")))
    
    # Calculate positions
    title_rect = painter.fontMetrics().boundingRect(title_text)
    title_y_pos = splash_pixmap_height // 3 # Position title higher
    painter.drawText(QtCore.QRectF((splash_pixmap_width - title_rect.width()) / 2, title_y_pos - title_rect.height() / 2, title_rect.width(), title_rect.height()), title_text)

    painter.setFont(splash_font_subtitle)
    current_y_subtitle = title_y_pos + title_rect.height() + 20 # Start subtitles below title
    
    for line in subtitle_texts:
        line_rect = painter.fontMetrics().boundingRect(line)
        painter.drawText(QtCore.QRectF((splash_pixmap_width - line_rect.width()) / 2, current_y_subtitle, line_rect.width(), line_rect.height()), line)
        current_y_subtitle += line_rect.height() + 10

    painter.end()
    splash = QtWidgets.QSplashScreen(splash_pixmap)
    splash.show()
    app.processEvents() 

    main_window = QtWidgets.QMainWindow()
    main_window.setWindowTitle(FLUTTERSHY_TEXTS["window_title_main"])
    
    # Dynamically set window size based on screen
    try:
        screen_geometry = app.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        width = int(screen_width * 0.8)    # 80% of screen width
        height = int(screen_height * 0.85) # 85% of screen height
        x_offset = (screen_width - width) // 2
        y_offset = (screen_height - height) // 2
        main_window.setGeometry(x_offset, y_offset, width, height)
    except Exception as e_geom:
        logging.warning(f"Could not dynamically set window geometry: {e_geom}. Falling back to default.")
        main_window.setGeometry(100, 100, 950, 750) # Fallback default size

    central_widget = QtWidgets.QWidget()
    main_window.setCentralWidget(central_widget)
    main_v_layout = QtWidgets.QVBoxLayout(central_widget) 

    # --- Load APP_CONFIG from JSON file ---
    def load_app_config_qt():
        global APP_CONFIG 
        default_cfg_copy = APP_CONFIG.copy() 
        
        config_full_path = os.path.join(SCRIPT_BASE_PATH, CONFIG_FILE_PATH) # Use base path
        logging.info(f"Attempting to load config from: {config_full_path}")

        if os.path.exists(config_full_path):
            try:
                with open(config_full_path, 'r') as f:
                    loaded_config = json.load(f)
                
                loaded_priority = loaded_config.pop('SENSOR_PRIORITY_ORDER', None)
                default_cfg_copy.update(loaded_config) 
                default_cfg_copy['bbox_str'] = loaded_config.get('bbox_str', DEFAULT_BBOX_STR) 
                
                if loaded_priority and isinstance(loaded_priority, list):
                    final_priority = list(loaded_priority) # Start with loaded
                    # Add any sensors from script's default that are not in loaded, preserving loaded order first
                    for sensor in DEFAULT_SENSOR_PRIORITY_ORDER: 
                        if sensor not in final_priority:
                            final_priority.append(sensor)
                    default_cfg_copy['SENSOR_PRIORITY_ORDER'] = final_priority
                else: 
                    default_cfg_copy['SENSOR_PRIORITY_ORDER'] = list(DEFAULT_SENSOR_PRIORITY_ORDER)
                
                APP_CONFIG = default_cfg_copy 
                logging.info(f"Loaded and merged config from {config_full_path}")

            except Exception as e:
                logging.warning(f"Could not load or parse config from {config_full_path}: {e}. Using script defaults.")
                # Ensure SENSOR_PRIORITY_ORDER is reset to default if loading failed badly
                APP_CONFIG['SENSOR_PRIORITY_ORDER'] = list(DEFAULT_SENSOR_PRIORITY_ORDER)
        else:
            logging.info(f"Config file {config_full_path} not found. Using script defaults and creating it.")
            APP_CONFIG['SENSOR_PRIORITY_ORDER'] = list(DEFAULT_SENSOR_PRIORITY_ORDER) # Ensure default priority on first run
        
        # Save (potentially updated or default) config back
        try:
            with open(config_full_path, 'w') as f:
                json.dump(APP_CONFIG, f, indent=4) 
            logging.info(f"Config file saved/updated at {config_full_path}")
        except Exception as e_save:
            logging.error(f"Could not save config file {config_full_path}: {e_save}")

    load_app_config_qt() 

    # --- Setup logging to QTextEdit ---
    class QtLogHandler(logging.Handler):
        def __init__(self, text_widget):
            super().__init__()
            self.widget = text_widget
            self.widget.setReadOnly(True)
        
        def emit(self, record):
            msg = self.format(record)
            # Use QMetaObject.invokeMethod for thread-safe updates to the GUI widget
            QtCore.QMetaObject.invokeMethod(self.widget, "append", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, msg))

    log_console = QtWidgets.QTextEdit() 
    qt_log_handler = QtLogHandler(log_console)
    qt_log_handler.setFormatter(LOG_FORMATTER) 
    ROOT_LOGGER.addHandler(qt_log_handler)
    # --- End logging setup ---

    # --- Sample Data Download Thread ---
    class SampleDownloadThread(QtCore.QThread):
        # Signal: sample_key, success, message_or_filepath
        sample_download_finished = QtCore.Signal(str, bool, str)

        def __init__(self, sample_key, config, base_path_for_sample):
            super().__init__()
            self.config = config
            self.sample_key = sample_key
            self.base_path = base_path_for_sample

        def run(self):
            output_dir = os.path.join(self.base_path, self.config["output_subdir"])
            os.makedirs(output_dir, exist_ok=True)
            
            file_name = f"{self.config['area_name']}_{self.config['sensor']}_{self.config['year']}-{self.config['month']:02d}.tif"
            output_filepath = os.path.join(output_dir, file_name)

            logging.info(f"SampleDownloadThread: Starting download for {file_name} to {output_filepath}")

            try:
                if not (ee.data._credentials if hasattr(ee, 'data') and hasattr(ee.data, '_credentials') else False): # Check EE init status
                    logging.error("SampleDownloadThread: EE not initialized. Cannot download sample.")
                    self.sample_download_finished.emit(self.sample_key, False, "EE Not Initialized for Sample")
                    return

                roi_geometry = ee.Geometry.Rectangle(self.config["bbox"])
                
                start_date_obj = datetime(self.config["year"], self.config["month"], 1)
                ee_start_date_str = ee.Date(start_date_obj.strftime('%Y-%m-%d'))
                ee_end_date_str = ee.Date((start_date_obj + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d'))

                sensor_name = self.config["sensor"]
                logging.info(f"SampleDownloadThread: Building mosaic for {sensor_name} {self.config['year']}-{self.config['month']:02d}")

                image_collection = get_collection(sensor_name)
                filtered_collection = image_collection.filterDate(ee_start_date_str, ee_end_date_str).filterBounds(roi_geometry)
                
                if filtered_collection.size().getInfo() == 0:
                    logging.warning(f"SampleDownloadThread: No images found for {sensor_name} in the period/ROI for sample.")
                    self.sample_download_finished.emit(self.sample_key, False, f"No images for {sensor_name} ({self.sample_key}) sample")
                    return

                masking_function = CLOUD_MASKS.get(sensor_name, lambda img: img)
                processing_function = SENSOR_PROCESSORS.get(sensor_name, lambda img: img)
                
                def safe_processing_and_masking_sample(input_image):
                    masked_image = masking_function(input_image)
                    processed_image = processing_function(masked_image)
                    return processed_image.set('fe_check_sample', 1)

                processed_collection_for_sample = filtered_collection.map(safe_processing_and_masking_sample).filter(ee.Filter.neq('fe_check_sample', None))
                
                if processed_collection_for_sample.size().getInfo() == 0:
                    logging.warning(f"SampleDownloadThread: All images masked out for {sensor_name} sample.")
                    self.sample_download_finished.emit(self.sample_key, False, f"All images masked for {sensor_name} ({self.sample_key}) sample")
                    return

                initial_mosaic_image = processed_collection_for_sample.median().clip(roi_geometry)
                
                all_bands_in_initial_mosaic = initial_mosaic_image.bandNames().getInfo()
                if not all_bands_in_initial_mosaic:
                    logging.warning(f"SampleDownloadThread: Initial median mosaic for {sensor_name} ({self.sample_key}) has no bands. Aborting sample.")
                    self.sample_download_finished.emit(self.sample_key, False, f"Initial mosaic no bands for {sensor_name} ({self.sample_key})")
                    return

                selected_bands_for_download = []

                if sensor_name == "SENTINEL2":
                    s2_optical_bands = [b for b in all_bands_in_initial_mosaic if b.startswith('B') and b not in ['B8A', 'B9']] # Common optical bands
                    
                    tcc_bands = ['B4', 'B3', 'B2'] # Target TCC
                    if all(b in all_bands_in_initial_mosaic for b in tcc_bands):
                        test_image_tcc = initial_mosaic_image.select(tcc_bands)
                        if test_image_tcc.bandNames().getInfo():
                            selected_bands_for_download = tcc_bands
                            logging.info(f"SampleDownloadThread: Using TCC bands {tcc_bands} for {sensor_name} sample.")
                    
                    if not selected_bands_for_download and len(s2_optical_bands) >= 3:
                        potential_bands = s2_optical_bands[:3] # e.g., B1, B2, B3 if available
                        test_image_3opt = initial_mosaic_image.select(potential_bands)
                        if test_image_3opt.bandNames().getInfo():
                            selected_bands_for_download = potential_bands
                            logging.info(f"SampleDownloadThread: TCC failed/invalid. Using first 3 optical bands {selected_bands_for_download} for {sensor_name} sample.")
                    
                    if not selected_bands_for_download and len(s2_optical_bands) >= 1:
                        potential_band = [s2_optical_bands[0]] # e.g., B1
                        test_image_1opt = initial_mosaic_image.select(potential_band)
                        if test_image_1opt.bandNames().getInfo():
                            selected_bands_for_download = potential_band
                            logging.info(f"SampleDownloadThread: 3-band failed/invalid. Using first optical band {selected_bands_for_download} for {sensor_name} sample (grayscale).")

                # General fallback if no bands selected yet (e.g. non-S2 sensor, or S2 fallbacks failed)
                if not selected_bands_for_download:
                    if len(all_bands_in_initial_mosaic) >= 3:
                        selected_bands_for_download = all_bands_in_initial_mosaic[:3]
                        logging.info(f"SampleDownloadThread: Using first 3 available bands {selected_bands_for_download} for {sensor_name} sample.")
                    elif all_bands_in_initial_mosaic: # At least one band
                        selected_bands_for_download = [all_bands_in_initial_mosaic[0]]
                        logging.info(f"SampleDownloadThread: Using first available band {selected_bands_for_download} for {sensor_name} sample (grayscale).")
                
                if not selected_bands_for_download:
                    logging.error(f"SampleDownloadThread: Could not select any valid bands for download for {sensor_name} ({self.sample_key}) sample. Initial bands were: {all_bands_in_initial_mosaic}")
                    self.sample_download_finished.emit(self.sample_key, False, f"No valid bands to download for {sensor_name} ({self.sample_key})")
                    return

                mosaic_image_for_download = initial_mosaic_image.select(selected_bands_for_download)

                logging.info(f"SampleDownloadThread: Mosaic built for {sensor_name} sample. Proceeding to download.")
                download_manager = DownloadManager()
                
                original_use_best_res = APP_CONFIG.get('USE_BEST_RESOLUTION')
                original_target_res = APP_CONFIG.get('TARGET_RESOLUTION')
                APP_CONFIG['USE_BEST_RESOLUTION'] = False 
                APP_CONFIG['TARGET_RESOLUTION'] = self.config["target_resolution"]

                download_successful = download_manager.download_tile(
                    mosaic_image_for_download, self.config["bbox"], output_filepath, 0, sensor_name )
                
                APP_CONFIG['USE_BEST_RESOLUTION'] = original_use_best_res # Restore
                APP_CONFIG['TARGET_RESOLUTION'] = original_target_res   # Restore

                if download_successful:
                    logging.info(f"SampleDownloadThread: Sample data downloaded successfully to {output_filepath}")
                    self.sample_download_finished.emit(self.sample_key, True, output_filepath)
                else:
                    logging.error(f"SampleDownloadThread: Failed to download sample data for {sensor_name} ({self.sample_key}).")
                    self.sample_download_finished.emit(self.sample_key, False, f"Download failed for {sensor_name} ({self.sample_key}) sample")

            except Exception as e: 
                logging.error(f"SampleDownloadThread: Error during sample download for {self.sample_key}: {e}", exc_info=True)
                self.sample_download_finished.emit(self.sample_key, False, f"Error ({self.sample_key}): {str(e)[:100]}")

    # --- Stylesheet generation function ---
    def get_stylesheet_qt(colors):
        input_bg_lighter = QtGui.QColor(colors['INPUT_BG']).lighter(105).name() if colors['INPUT_BG'] != FLUTTERSHY_COLORS['INPUT_BG'] else "#FEFEFC"
        log_bg_lighter = QtGui.QColor(colors['LOG_BG']).lighter(105).name() if colors['LOG_BG'] != FLUTTERSHY_COLORS['LOG_BG'] else "#FEFEF8"
        
        progress_overall_lighter = QtGui.QColor(colors['PROGRESS_FG_OVERALL']).lighter(120).name()
        progress_monthly_lighter = QtGui.QColor(colors['PROGRESS_FG_MONTHLY']).lighter(120).name()

        button_pink_hover = QtGui.QColor(colors['BUTTON_PINK_BG']).lighter(110).name()
        button_pink_pressed = QtGui.QColor(colors['BUTTON_PINK_BG']).darker(110).name()
        button_lavender_hover = colors.get('BUTTON_LAVENDER_HOVER', QtGui.QColor(colors['BUTTON_LAVENDER_BG']).lighter(110).name())
        button_lavender_pressed = QtGui.QColor(colors['BUTTON_LAVENDER_BG']).darker(110).name()
        button_yellow_hover = colors.get('BUTTON_YELLOW_HOVER', QtGui.QColor(colors['BUTTON_YELLOW_BG']).lighter(110).name())
        button_yellow_pressed = QtGui.QColor(colors['BUTTON_YELLOW_BG']).darker(110).name()

        # Ensure font size is a string with 'pt'
        font_size_normal_str = str(QT_FLUTTER_FONT_SIZE_NORMAL)
        if not font_size_normal_str.endswith('pt'): font_size_normal_str += "pt"
        
        font_size_small_str = str(int(font_size_normal_str.replace('pt','')) - 1) + "pt" # e.g., 10pt if normal is 11pt
        font_size_log_str = str(int(font_size_normal_str.replace('pt','')) - 1) + "pt" # e.g., 10pt for log

        return f"""
            QMainWindow, QWidget {{
                background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.7, fx:0.5, fy:0.5,
                                    stop:0 {colors['BG_MAIN']},
                                    stop:0.5 {colors['BG_FRAME']},
                                    stop:1 {colors['BG_MAIN']});
                font-family: '{QT_FLUTTER_FONT_FAMILY}';
            }}
            QLabel {{ color: {colors['TEXT_COLOR']}; font-size: {font_size_normal_str}; padding-top: 4px; padding-bottom: 4px; }}
            QLineEdit, QDateEdit, QComboBox {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['INPUT_BG']}, stop:1 {input_bg_lighter});
                color: {colors['INPUT_FG']}; border: 1px solid {colors['ACCENT_BORDER']};
                border-radius: 5px; padding: 7px; font-size: {font_size_normal_str}; min-height: 20px;
            }}
            QLineEdit::placeholder {{ color: {colors['PLACEHOLDER_FG']}; }}
            QDateEdit::drop-down, QComboBox::drop-down {{ 
                subcontrol-origin: padding; subcontrol-position: top right; width: 20px;
                border-left-width: 1px; border-left-color: {colors['ACCENT_BORDER']}; border-left-style: solid;
                border-top-right-radius: 3px; border-bottom-right-radius: 3px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['INPUT_BG']}, stop:1 {colors['BG_MAIN']});
            }}
            QDateEdit::down-arrow, QComboBox::down-arrow {{ image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-down-arrow.png); }} /* Standard Qt arrow */
            QComboBox QAbstractItemView {{ /* Dropdown list */
                background-color: {colors['INPUT_BG']}; color: {colors['INPUT_FG']};
                selection-background-color: {colors['BUTTON_PINK_BG']}; selection-color: {colors['BUTTON_PINK_FG']};
                border: 1px solid {colors['ACCENT_BORDER']};
            }}
            QCalendarWidget QWidget {{ alternate-background-color: {colors['INPUT_BG']}; background-color: {colors['BG_MAIN']}; color: {colors['TEXT_COLOR']}; }} 
            QCalendarWidget QAbstractItemView:enabled {{ color: {colors['INPUT_FG']};
                selection-background-color: {colors['BUTTON_PINK_BG']}; selection-color: {colors['BUTTON_PINK_FG']}; font-size: {font_size_small_str};
            }}
            QCalendarWidget QToolButton {{ color: {colors['TEXT_COLOR']}; background-color: {colors['CALENDAR_HEADER_BG']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 3px; padding: 5px; font-size: {font_size_normal_str};
            }}
            QCalendarWidget QToolButton:hover {{ background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']}; }}
            QTextEdit#logConsole {{ /* Specific ID for log console if needed, or general QTextEdit */
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['LOG_BG']}, stop:1 {log_bg_lighter});
                color: {colors['LOG_FG']}; border: 1px solid {colors['ACCENT_BORDER']};
                border-radius: 4px; font-family: 'Consolas', '{QT_FLUTTER_FONT_FAMILY}', monospace; font-size: {font_size_log_str}; padding: 3px;
            }}
            QProgressBar {{ border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 5px; text-align: center;
                background-color: {colors['PROGRESS_BG']}; color: {colors['TEXT_COLOR']};
                font-size: {font_size_small_str}; height: 24px;
            }}
            QProgressBar#overallProgressBar::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['PROGRESS_FG_OVERALL']}, stop:1 {progress_overall_lighter}); border-radius: 4px; margin: 1px; }}
            QProgressBar#monthlyProgressBar::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['PROGRESS_FG_MONTHLY']}, stop:1 {progress_monthly_lighter}); border-radius: 4px; margin: 1px; }}
            QCheckBox {{ spacing: 7px; color: {colors['TEXT_COLOR']}; font-size: {font_size_normal_str}; padding-top: 4px; padding-bottom: 4px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; background-color: {colors['INPUT_BG']}; }}
            QCheckBox::indicator:checked {{ background-color: {colors['BUTTON_PINK_BG']}; }}
            QCheckBox::indicator:hover {{ border: 1px solid {colors['BUTTON_PINK_BG']}; }}
            
            QPushButton#browseButton, QPushButton#indexBrowseButton {{ 
                background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 5px 10px; font-size: {font_size_normal_str}; min-height: 20px;
            }}
            QPushButton#browseButton:hover, QPushButton#indexBrowseButton:hover {{ background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']}; }}
            QPushButton#browseButton:pressed, QPushButton#indexBrowseButton:pressed {{ background-color: {button_pink_pressed}; }}
            
            QPushButton#startButton, QPushButton#startIndexAnalysisButton {{ 
                background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 7px 15px; font-size: {font_size_normal_str}; font-weight: bold;
            }}
            QPushButton#startButton:hover, QPushButton#startIndexAnalysisButton:hover {{ background-color: {button_pink_hover}; }} 
            QPushButton#startButton:pressed, QPushButton#startIndexAnalysisButton:pressed {{ background-color: {button_pink_pressed}; }}
            QPushButton#startButton:disabled, QPushButton#startIndexAnalysisButton:disabled {{ 
                background-color: #555555; color: #AAAAAA; border-color: #666666; 
            }}
            
            QPushButton#cancelButton {{ 
                background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 6px 12px; font-size: {font_size_normal_str};
            }}
            QPushButton#cancelButton:hover {{ background-color: {button_lavender_hover}; }} 
            QPushButton#cancelButton:pressed {{ background-color: {button_lavender_pressed}; }}
            QPushButton#cancelButton:disabled {{ background-color: #555555; color: #AAAAAA; border-color: #666666; }}
            
            QPushButton#verifyButton {{ 
                background-color: {colors['BUTTON_YELLOW_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 6px 12px; font-size: {font_size_normal_str};
            }}
            QPushButton#verifyButton:hover {{ background-color: {button_yellow_hover}; }} 
            QPushButton#verifyButton:pressed {{ background-color: {button_yellow_pressed}; }}
            QPushButton#verifyButton:disabled {{ background-color: #555555; color: #AAAAAA; border-color: #666666; }}
            
            QGroupBox {{ border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 5px; margin-top: 1ex; padding: 5px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: {colors['TEXT_COLOR']}; font-weight: bold; }}
            
            QMenuBar {{ background-color: {colors.get('BG_FRAME', '#252526')}; color: {colors.get('TEXT_COLOR', '#D4D4D4')}; font-size: {font_size_normal_str}; }}
            QMenuBar::item:selected {{ background-color: {colors.get('BUTTON_YELLOW_HOVER', '#5A5A5A')}; }}
            QMenu {{ background-color: {colors.get('BG_FRAME', '#252526')}; color: {colors.get('TEXT_COLOR', '#D4D4D4')}; border: 1px solid {colors['ACCENT_BORDER']}; }}
            QMenu::item:selected {{ background-color: {colors.get('BUTTON_YELLOW_HOVER', '#5A5A5A')}; }}

            QTabWidget::pane {{ border-top: 1px solid {colors['ACCENT_BORDER']}; margin-top: -1px; }}
            QTabBar::tab {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['BG_FRAME']}, stop:1 {colors['BG_MAIN']});
                border: 1px solid {colors['ACCENT_BORDER']}; border-bottom-color: {colors['ACCENT_BORDER']}; 
                border-top-left-radius: 4px; border-top-right-radius: 4px;
                min-width: 8ex; padding: 8px 12px; margin-right: 2px; color: {colors['TEXT_COLOR']};
            }}
            QTabBar::tab:selected {{ 
                background: {colors['BG_MAIN']}; border-bottom-color: {colors['BG_MAIN']}; /* Make selected tab blend with pane */
                color: {colors['TEXT_COLOR']}; font-weight: bold;
            }}
            QTabBar::tab:!selected:hover {{ background: {colors['BUTTON_LAVENDER_HOVER']}; }}
            QSplitter::handle {{ background-color: {colors['ACCENT_BORDER']}; height: 3px; width: 3px; }}
            QSplitter::handle:horizontal {{ height: 3px; }}
            QSplitter::handle:vertical {{ width: 3px; }}
        """
    # Removed the duplicated and incomplete get_stylesheet_qt function that was here.

    # --- Main Splitter Layout ---
    splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
    main_v_layout.addWidget(splitter, 1) 

    # --- Left Pane for Tabs ---
    left_pane_widget = QtWidgets.QWidget()
    left_pane_layout = QtWidgets.QVBoxLayout(left_pane_widget)
    left_pane_layout.setContentsMargins(0,0,0,0) 

    # --- Main Tab Widget ---
    main_tab_widget = QtWidgets.QTabWidget()
    left_pane_layout.addWidget(main_tab_widget) 
    
    index_analysis_pane = IndexAnalysisPane(get_current_theme_colors())
    
    # Instantiate the new VectorDownloadTab
    vector_download_tab_instance = VectorDownloadTab(get_current_theme_colors())

    data_viewer_tab = None 
    try:
        data_viewer_tab = DataViewerTab(get_current_theme_colors()) 
        logging.info(f"DataViewerTab instantiated successfully: {data_viewer_tab}")
        if data_viewer_tab is None: 
            logging.error("DataViewerTab instantiation resulted in None object unexpectedly!")
    except Exception as e_inst:
        logging.error(f"CRITICAL ERROR during DataViewerTab instantiation: {e_inst}", exc_info=True)

    splitter.addWidget(left_pane_widget)


    # --- Tab 1: Download Settings ---
    settings_tab_widget = QtWidgets.QWidget()
    # Create a main layout for the settings_tab_widget page
    page_main_layout = QtWidgets.QVBoxLayout(settings_tab_widget)
    page_main_layout.setContentsMargins(0,0,0,0) # Use full space of the page

    # Create a QScrollArea
    scroll_area = QtWidgets.QScrollArea()
    scroll_area.setWidgetResizable(True) # Crucial for the content widget to resize properly
    scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded) # Show horizontal scrollbar if needed
    scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)   # Show vertical scrollbar if needed
    page_main_layout.addWidget(scroll_area) # Add scroll area to the page's main layout

    # Create a content widget for the scroll area, and set the settings_tab_layout on this content widget
    scroll_content_widget = QtWidgets.QWidget()
    scroll_area.setWidget(scroll_content_widget)
    settings_tab_layout = QtWidgets.QVBoxLayout(scroll_content_widget) # Main layout for the tab's content

    area_time_groupbox = QtWidgets.QGroupBox("Area & Time Settings")
    area_time_form_layout = QtWidgets.QFormLayout(area_time_groupbox)
    # ... (rest of area_time_groupbox setup remains the same) ...

    processing_sensor_groupbox = QtWidgets.QGroupBox("Processing & Sensor Settings")
    processing_sensor_form_layout = QtWidgets.QFormLayout(processing_sensor_groupbox)
    # ... (rest of processing_sensor_groupbox setup remains the same) ...

    bbox_label_text_with_colon = "AOI (BBOX or Polygon GeoJSON):"
    bbox_help_text = ("Enter or import coordinates for your Area of Interest (AOI):\n\n"
                      "<b>1. Manual Input:</b>\n"
                      "   - <b>Rectangle (BBOX)</b>: 'minLon,minLat,maxLon,maxLat' (e.g., 35.2,30.5,35.8,32.0).\n"
                      "   - <b>Polygon (GeoJSON)</b>: A list of [longitude, latitude] pairs forming a closed shape. "
                      "     Example: '[[35,31],[35.5,31],[35.5,31.5],[35,31.5],[35,31]]'.\n"
                      "     The first and last points must be the same if manually entered.\n\n"
                      "<b>2. Interactive Selection/Import:</b>\n"
                      "   - Use the '<b>🗺️ Map</b>' button to draw a new polygon/rectangle or edit an existing one. "
                      "     The input field will be populated with the polygon's JSON representation.\n"
                      "   - Use the '<b>📂 SHP</b>' button to import an Esri Shapefile (.shp). The first polygon feature "
                      "     found in the shapefile will be loaded into the map view. You can then inspect, edit, and use this shape. "
                      "     Ensure the shapefile is in WGS84 (lat/lon) projection for best results with GEE."
                     )
    bbox_label_with_help_widget = create_form_label_with_help_qt(bbox_label_text_with_colon, "Area of Interest (AOI) Help", bbox_help_text, main_window)

    bbox_field_layout = QtWidgets.QHBoxLayout()
    bbox_field_layout.setSpacing(6) # Adjust spacing between input field and buttons

    bbox_input = QtWidgets.QLineEdit()
    bbox_input.setPlaceholderText("e.g., 35.2,30.5,35.8,32.0 or [[lon,lat],...]")
    bbox_input.setText(APP_CONFIG.get('bbox_str', DEFAULT_BBOX_STR))
    bbox_field_layout.addWidget(bbox_input, 1)

    import_shp_button = QtWidgets.QPushButton("📂") # Icon only
    import_shp_button.setObjectName("aoiImportShpButton")
    import_shp_button.setToolTip("Import AOI from a Shapefile (.shp)")
    import_shp_button.setFixedSize(32, 32) # Compact square button

    select_bbox_from_map_button = QtWidgets.QPushButton("🗺️") # Icon only
    select_bbox_from_map_button.setObjectName("aoiSelectMapButton")
    select_bbox_from_map_button.setToolTip("Open map to draw/select AOI polygon")
    select_bbox_from_map_button.setFixedSize(32, 32) # Compact square button

    bbox_field_layout.addWidget(import_shp_button)
    bbox_field_layout.addWidget(select_bbox_from_map_button)
    area_time_form_layout.addRow(bbox_label_with_help_widget, bbox_field_layout)

    start_date_label = QtWidgets.QLabel(FLUTTERSHY_TEXTS["start_date_label"])
    start_date_input = QtWidgets.QDateEdit()
    start_date_input.setCalendarPopup(True)
    start_date_input.setDisplayFormat("yyyy-MM-dd")
    initial_start_qdate = QtCore.QDate.fromString(APP_CONFIG.get('start_date', DEFAULT_START_DATE), "yyyy-MM-dd")
    start_date_input.setDate(initial_start_qdate if initial_start_qdate.isValid() else QtCore.QDate.currentDate().addMonths(-6) )
    area_time_form_layout.addRow(start_date_label, start_date_input)

    end_date_label = QtWidgets.QLabel(FLUTTERSHY_TEXTS["end_date_label"])
    end_date_input = QtWidgets.QDateEdit()
    end_date_input.setCalendarPopup(True)
    end_date_input.setDisplayFormat("yyyy-MM-dd")
    initial_end_qdate = QtCore.QDate.fromString(APP_CONFIG.get('end_date', DEFAULT_END_DATE), "yyyy-MM-dd")
    end_date_input.setDate(initial_end_qdate if initial_end_qdate.isValid() else QtCore.QDate.currentDate())
    area_time_form_layout.addRow(end_date_label, end_date_input)

    output_dir_label = QtWidgets.QLabel(FLUTTERSHY_TEXTS["output_dir_label"])
    output_dir_input = QtWidgets.QLineEdit()
    output_dir_input.setText(APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR))
    browse_button = QtWidgets.QPushButton("Browse...")
    browse_button.setObjectName("browseButton")
    output_dir_layout = QtWidgets.QHBoxLayout()
    output_dir_layout.addWidget(output_dir_input)
    output_dir_layout.addWidget(browse_button)
    area_time_form_layout.addRow(output_dir_label, output_dir_layout)

    overwrite_checkbox = QtWidgets.QCheckBox(FLUTTERSHY_TEXTS["overwrite_label"])
    overwrite_checkbox.setChecked(APP_CONFIG.get('overwrite', False))
    area_time_form_layout.addRow(overwrite_checkbox)

    cleanup_fluttershy_text_with_colon = FLUTTERSHY_TEXTS.get("cleanup_tiles_label", "Cleanup individual tiles after stitch? 🧹:")
    cleanup_label_text_no_colon = cleanup_fluttershy_text_with_colon.rstrip(': ')
    
    cleanup_label_for_checkbox = QtWidgets.QLabel(cleanup_label_text_no_colon)
    cleanup_help_text = ("If checked, individual downloaded image tiles will be deleted after they are "
                         "successfully stitched into the monthly mosaic. This saves disk space.\n\n"
                         "Uncheck to keep the individual tiles for inspection or other uses. "
                         "Tiles are stored in a 'tiles' subdirectory within each month's output folder.")
    cleanup_help_button = create_help_q_button("Cleanup Tiles Help", cleanup_help_text, main_window)

    cleanup_label_part_layout = QtWidgets.QHBoxLayout()
    cleanup_label_part_layout.setContentsMargins(0,0,0,0); cleanup_label_part_layout.setSpacing(3)
    cleanup_label_part_layout.addWidget(cleanup_label_for_checkbox)
    cleanup_label_part_layout.addWidget(cleanup_help_button)
    cleanup_label_part_layout.addStretch(1)
    
    cleanup_label_widget_container = QtWidgets.QWidget()
    cleanup_label_widget_container.setLayout(cleanup_label_part_layout)

    cleanup_tiles_checkbox = QtWidgets.QCheckBox("") 
    cleanup_tiles_checkbox.setChecked(APP_CONFIG.get('CLEANUP_TILES', DEFAULT_CLEANUP_TILES))
    area_time_form_layout.addRow(cleanup_label_widget_container, cleanup_tiles_checkbox)

    tiling_method_label_text_with_colon = "Tiling Method:"
    tiling_method_help_text = ("Choose how the Area of Interest is divided into smaller tiles for processing:\n\n"
                               "- '<b>Tile Size by Degree</b>': Specify the width/height of each tile in decimal degrees. "
                               "Good for consistent geographic tiling across different areas.\n\n"
                               "- '<b>Tile Count (Approx N)</b>': Specify an approximate number of tiles. The area will be "
                               "divided to achieve roughly N tiles. Useful if you prefer to control the total number "
                               "of processing units, especially for very large or irregularly shaped AOIs.")
    tiling_method_label_with_help_widget = create_form_label_with_help_qt(tiling_method_label_text_with_colon, "Tiling Method Help", tiling_method_help_text, main_window)

    tiling_method_combo = QtWidgets.QComboBox()
    tiling_method_combo.addItems(["Tile Size by Degree", "Tile Count (Approx N)"]) # Add items
    tiling_method_combo.setCurrentText("Tile Size by Degree" if APP_CONFIG.get('TILING_METHOD', DEFAULT_TILING_METHOD) == "degree" else "Tile Count (Approx N)")
    processing_sensor_form_layout.addRow(tiling_method_label_with_help_widget, tiling_method_combo)


    tile_size_deg_label_text_with_colon = "Tile Size (degrees):"
    tile_size_help_text = ("Set the approximate side length of each square tile in decimal degrees (e.g., 0.1 for a 0.1° x 0.1° tile).\n"
                           "This is active when 'Tile Size by Degree' method is selected.")
    tile_size_deg_label_with_help_widget = create_form_label_with_help_qt(tile_size_deg_label_text_with_colon, "Tile Size (Degrees) Help", tile_size_help_text, main_window)
    
    tile_size_deg_input = QtWidgets.QLineEdit()
    tile_size_deg_input.setValidator(QtGui.QDoubleValidator(0.0001, 360.0, 5)) 
    tile_size_deg_input.setText(str(APP_CONFIG.get('TILE_SIZE_DEG', DEFAULT_TILE_SIZE_DEG)))
    processing_sensor_form_layout.addRow(tile_size_deg_label_with_help_widget, tile_size_deg_input)


    num_subsections_label_text_with_colon = "Number of Tiles (approx N):"
    num_subsections_help_text = ("Set the approximate total number of tiles the Area of Interest should be divided into (e.g., 100).\n"
                                 "The actual number might vary slightly to best fit the area. This is active when 'Tile Count (Approx N)' method is selected.")
    num_subsections_label_with_help_widget = create_form_label_with_help_qt(num_subsections_label_text_with_colon, "Number of Tiles Help", num_subsections_help_text, main_window)

    num_subsections_input = QtWidgets.QLineEdit()
    num_subsections_input.setValidator(QtGui.QIntValidator(1, 100000)) 
    num_subsections_input.setText(str(APP_CONFIG.get('NUM_SUBSECTIONS', DEFAULT_NUM_SUBSECTIONS)))
    processing_sensor_form_layout.addRow(num_subsections_label_with_help_widget, num_subsections_input)

    overlap_deg_label_text_with_colon = "Overlap (degrees):"
    overlap_help_text = ("Specify the overlap between adjacent tiles in decimal degrees (e.g., 0.002).\n"
                         "A small overlap (e.g., 5-10% of tile size) helps prevent gaps or edge artifacts in the "
                         "final stitched mosaic due to minor projection or georeferencing discrepancies.")
    overlap_deg_label_with_help_widget = create_form_label_with_help_qt(overlap_deg_label_text_with_colon, "Tile Overlap Help", overlap_help_text, main_window)

    overlap_deg_input = QtWidgets.QLineEdit()
    overlap_deg_input.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 5)) 
    overlap_deg_input.setText(str(APP_CONFIG.get('OVERLAP_DEG', DEFAULT_OVERLAP_DEG)))
    processing_sensor_form_layout.addRow(overlap_deg_label_with_help_widget, overlap_deg_input)


    use_best_res_fluttershy_text = FLUTTERSHY_TEXTS.get("use_highest_resolution_cb", "Use Highest Sensor Resolution ✨")
    use_best_res_label_for_checkbox = QtWidgets.QLabel(use_best_res_fluttershy_text)
    best_res_help_text = ("If checked, Flutter Earth will attempt to download data at the best native resolution "
                          "available for the selected sensor (e.g., 10m for Sentinel-2, 30m for Landsat).\n"
                          "This will override the 'Target Resolution' setting below.\n\n"
                          "If unchecked, the 'Target Resolution' setting will be used, and data may be resampled.")
    best_res_help_button = create_help_q_button("Highest Resolution Help", best_res_help_text, main_window)

    use_best_res_label_part_layout = QtWidgets.QHBoxLayout()
    use_best_res_label_part_layout.setContentsMargins(0,0,0,0); use_best_res_label_part_layout.setSpacing(3)
    use_best_res_label_part_layout.addWidget(use_best_res_label_for_checkbox)
    use_best_res_label_part_layout.addWidget(best_res_help_button)
    use_best_res_label_part_layout.addStretch(1)

    use_best_res_widget_container = QtWidgets.QWidget()
    use_best_res_widget_container.setLayout(use_best_res_label_part_layout)

    use_best_resolution_checkbox = QtWidgets.QCheckBox("") 
    use_best_resolution_checkbox.setChecked(APP_CONFIG.get('USE_BEST_RESOLUTION', DEFAULT_USE_BEST_RESOLUTION))
    processing_sensor_form_layout.addRow(use_best_res_widget_container, use_best_resolution_checkbox)


    target_resolution_label_text_with_colon = "Target Resolution (meters):"
    target_res_help_text = ("Desired ground resolution of the output imagery in meters (e.g., 10, 30).\n"
                            "This is active if 'Use Highest Sensor Resolution' is UNCHECKED.\n"
                            "Data from GEE will be requested at this scale. If the native sensor resolution is "
                            "coarser, the data will be upsampled by GEE. If finer, it will be downsampled.")
    target_resolution_label_with_help_widget = create_form_label_with_help_qt(target_resolution_label_text_with_colon, "Target Resolution Help", target_res_help_text, main_window)

    target_resolution_input = QtWidgets.QLineEdit()
    target_resolution_input.setValidator(QtGui.QIntValidator(1, 5000)) 
    target_resolution_input.setText(str(APP_CONFIG.get('TARGET_RESOLUTION', DEFAULT_TARGET_RESOLUTION)))
    processing_sensor_form_layout.addRow(target_resolution_label_with_help_widget, target_resolution_input)


    max_workers_label_text_with_colon = "Max Workers (threads):"
    max_workers_help_text = ("Maximum number of parallel threads for downloading and processing GEE tiles (e.g., 4).\n"
                             "Higher values can speed up downloads for large areas but consume more local resources "
                             "(CPU, network) and may increase the chance of hitting Google Earth Engine's concurrent "
                             "request limits, leading to temporary errors.\n\n"
                             "Recommended: Start with 2-4 and adjust based on performance and stability for your "
                             "connection and AOI size.")
    max_workers_label_with_help_widget = create_form_label_with_help_qt(max_workers_label_text_with_colon, "Max Workers Help", max_workers_help_text, main_window)

    max_workers_input = QtWidgets.QLineEdit()
    max_workers_input.setValidator(QtGui.QIntValidator(1, 32)) 
    max_workers_input.setText(str(APP_CONFIG.get('MAX_WORKERS', DEFAULT_MAX_WORKERS)))
    processing_sensor_form_layout.addRow(max_workers_label_with_help_widget, max_workers_input)

    sensor_priority_label_widget = QtWidgets.QLabel(FLUTTERSHY_TEXTS.get("sensor_priority_label", "Sensor Priority:"))
    sensor_priority_display_label = QtWidgets.QLabel(", ".join(APP_CONFIG.get('SENSOR_PRIORITY_ORDER', DEFAULT_SENSOR_PRIORITY_ORDER)))
    sensor_priority_display_label.setWordWrap(True)
    edit_sensor_priority_button = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("sensor_priority_edit_button", "Edit Priority..."))
    processing_sensor_form_layout.addRow(sensor_priority_label_widget, sensor_priority_display_label)
    processing_sensor_form_layout.addRow("", edit_sensor_priority_button)
    
    # Create a horizontal splitter for the top part of the settings tab
    top_settings_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
    top_settings_splitter.addWidget(area_time_groupbox)
    top_settings_splitter.addWidget(processing_sensor_groupbox)
    
    # Set initial sizes for the splitter (e.g., 50/50 or adjust as needed)
    top_settings_splitter.setSizes([main_window.width() // 4, main_window.width() // 4]) # Example sizing

    settings_tab_layout.addWidget(top_settings_splitter)
    settings_tab_layout.addStretch(1) # Add stretch to push content to the top

    # Tab Order Adjustment: Vector Download Tab will be added last.
    main_tab_widget.addTab(settings_tab_widget, "⚙️ Download Settings")

    post_processing_main_tab = QtWidgets.QWidget() 
    post_processing_main_layout = QtWidgets.QVBoxLayout(post_processing_main_tab)
    post_processing_main_layout.setContentsMargins(0,0,0,0) 

    post_processing_sub_tabs = QtWidgets.QTabWidget() 
    post_processing_main_layout.addWidget(post_processing_sub_tabs)
    post_processing_sub_tabs.addTab(index_analysis_pane, "📈 Index Analysis")
    
    if data_viewer_tab:
        post_processing_sub_tabs.addTab(data_viewer_tab, "🖼️ Data Viewer") 
        logging.info("DataViewerTab added to post_processing_sub_tabs.")
    else:
        logging.error("DataViewerTab was NOT added to post_processing_sub_tabs because it failed to instantiate or was None.")
        # Add a placeholder tab if DataViewerTab failed
        placeholder_viewer_tab = QtWidgets.QLabel("Data Viewer could not be initialized.")
        placeholder_viewer_tab.setAlignment(Qt.AlignCenter)
        post_processing_sub_tabs.addTab(placeholder_viewer_tab, "🖼️ Data Viewer (Error)")


    satellite_info_tab_instance = SatelliteInfoTab(get_current_theme_colors()) 
    main_tab_widget.addTab(satellite_info_tab_instance, "🛰️ Satellite Info")

    main_tab_widget.addTab(post_processing_main_tab, "📊 Post Processing") 

    # Add VectorDownloadTab last
    main_tab_widget.addTab(vector_download_tab_instance, FLUTTERSHY_TEXTS.get("vector_download_tab_title", "🗺️ Vector Download"))
    # Attempt to explicitly enable the tab. This is mostly a diagnostic step;
    # if the tab is disabled due to a deeper issue, this might not override it.
    vector_tab_index = main_tab_widget.indexOf(vector_download_tab_instance)
    if vector_tab_index != -1:
        main_tab_widget.setTabEnabled(vector_tab_index, True)

    overall_progress_label_widget = QtWidgets.QLabel(FLUTTERSHY_TEXTS["overall_progress_label"])
    overall_progress_bar = QtWidgets.QProgressBar() 
    overall_progress_bar.setObjectName("overallProgressBar") # For stylesheet
    overall_progress_bar.setRange(0, 100); overall_progress_bar.setValue(0)
    progress_overall_layout = QtWidgets.QHBoxLayout()
    progress_overall_layout.addWidget(overall_progress_label_widget); progress_overall_layout.addWidget(overall_progress_bar)
    
    monthly_progress_label_widget = QtWidgets.QLabel(FLUTTERSHY_TEXTS["monthly_progress_label"]) 
    monthly_progress_bar = QtWidgets.QProgressBar()
    monthly_progress_bar.setObjectName("monthlyProgressBar") # For stylesheet
    monthly_progress_bar.setRange(0, 100); monthly_progress_bar.setValue(0)
    progress_monthly_layout = QtWidgets.QHBoxLayout()
    progress_monthly_layout.addWidget(monthly_progress_label_widget); progress_monthly_layout.addWidget(monthly_progress_bar)

    progress_bars_container = QtWidgets.QWidget()
    progress_bars_container_layout = QtWidgets.QVBoxLayout(progress_bars_container)
    progress_bars_container_layout.setContentsMargins(0,0,0,0) 
    progress_bars_container_layout.addLayout(progress_overall_layout)
    progress_bars_container_layout.addLayout(progress_monthly_layout)
    
    main_v_layout.addWidget(progress_bars_container)

    log_console_label_widget = QtWidgets.QLabel(FLUTTERSHY_TEXTS["log_console_label"])
    main_v_layout.addWidget(log_console_label_widget)
    log_console.setObjectName("logConsole") # For specific styling if needed
    main_v_layout.addWidget(log_console, 1) 


    buttons_layout = QtWidgets.QHBoxLayout()
    start_button_qt = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("run_button", "🌸 Start Download 🌸"))
    start_button_qt.setObjectName("startButton")
    cancel_button_qt = QtWidgets.QPushButton(FLUTTERSHY_TEXTS.get("cancel_button", "🍃 Cancel 🍂"))
    cancel_button_qt.setObjectName("cancelButton")
    cancel_button_qt.setEnabled(False) 
    verify_button_qt = QtWidgets.QPushButton(
        FLUTTERSHY_TEXTS.get("verify_satellites_button_icon", "🛰️") + " " +
        FLUTTERSHY_TEXTS.get("verify_button_text_base", "Verify Satellite Friends"))
    verify_button_qt.setObjectName("verifyButton")
    buttons_layout.addWidget(start_button_qt); buttons_layout.addWidget(cancel_button_qt)
    buttons_layout.addStretch(1); buttons_layout.addWidget(verify_button_qt)
    main_v_layout.addLayout(buttons_layout)

    status_bar_qt = QtWidgets.QStatusBar(main_window) 
    main_window.setStatusBar(status_bar_qt)
    status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_ready", "Ready! ✨"))

    menu_bar = main_window.menuBar()

    # File Menu
    file_menu_text = FLUTTERSHY_TEXTS.get("file_menu_text", "&File") # Assuming a key like this might be added or use default
    file_menu = menu_bar.addMenu(file_menu_text)
    # ... (add actions to file_menu: save_config_action, theme_menu, exit_action etc.)

    # New Tools Menu
    tools_menu_label_text = FLUTTERSHY_TEXTS.get("tools_menu_label", "&Tools 🛠️")
    tools_menu = menu_bar.addMenu(tools_menu_label_text)

    sat_info_action_text = FLUTTERSHY_TEXTS.get("satellite_info_action_label", "🛰️ Satellite Info")
    sat_info_action = QtWidgets.QAction(sat_info_action_text, main_window)
    sat_info_action.triggered.connect(lambda: main_tab_widget.setCurrentWidget(satellite_info_tab_instance))
    tools_menu.addAction(sat_info_action)

    post_proc_action_text = FLUTTERSHY_TEXTS.get("post_processing_action_label", "📊 Post Processing")
    post_proc_action = QtWidgets.QAction(post_proc_action_text, main_window)
    post_proc_action.triggered.connect(lambda: main_tab_widget.setCurrentWidget(post_processing_main_tab))
    tools_menu.addAction(post_proc_action)

    vector_dl_action_text = FLUTTERSHY_TEXTS.get("vector_download_tab_title", "🗺️ Vector Download") # Reusing tab title
    vector_dl_action = QtWidgets.QAction(vector_dl_action_text, main_window)
    vector_dl_action.triggered.connect(lambda: main_tab_widget.setCurrentWidget(vector_download_tab_instance))
    tools_menu.addAction(vector_dl_action)

    # Help Menu (ensure it's added after Tools)
    def browse_output_dir_qt():
        initial_dir = output_dir_input.text() or APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR)
        directory = QtWidgets.QFileDialog.getExistingDirectory(main_window, "Select Output Directory, sweetie 🎀", initial_dir)
        if directory:
            output_dir_input.setText(directory)
            APP_CONFIG['output_dir'] = directory 
            logging.info(f"Output directory selected: {directory}")
            update_and_save_app_config_qt() # Save change immediately

    # --- Populate File Menu ---
    # Example: Save Configuration (if you want to add it back)
    # save_config_action = QtWidgets.QAction("💾 Save Configuration", main_window)
    # save_config_action.triggered.connect(update_and_save_app_config_qt) # update_and_save_app_config_qt already saves
    # file_menu.addAction(save_config_action)

    # Themes submenu (already part of your existing logic, ensure it's added to file_menu)
    theme_menu_text = FLUTTERSHY_TEXTS.get("themes_menu_text", "&Themes") # Get themed text
    actual_theme_menu = file_menu.addMenu(theme_menu_text) # Add as submenu to File
    theme_action_group = QtWidgets.QActionGroup(main_window)
    theme_action_group.setExclusive(True)
    # ... (fluttershy_action, night_mode_action added to actual_theme_menu and theme_action_group) ...

    file_menu.addSeparator()
    exit_action = QtWidgets.QAction("👋 Exit Flutter Earth", main_window)
    exit_action.triggered.connect(main_window.close) # Or app.quit
    file_menu.addAction(exit_action)

    browse_button.clicked.connect(browse_output_dir_qt)

    def open_sensor_priority_dialog_qt():
        global APP_CONFIG 
        current_priority = APP_CONFIG.get('SENSOR_PRIORITY_ORDER', list(DEFAULT_SENSOR_PRIORITY_ORDER))
        all_sensors = list(SENSOR_TIMELINE.keys()) 
        current_colors = get_current_theme_colors()
        dialog = SensorPriorityDialogQt(main_window, current_priority, all_sensors, current_colors)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_priority = dialog.get_updated_priority_list()
            if new_priority is not None:
                APP_CONFIG['SENSOR_PRIORITY_ORDER'] = new_priority
                sensor_priority_display_label.setText(", ".join(new_priority))
                update_and_save_app_config_qt() 
                logging.info(f"Sensor priority updated to: {new_priority}")
    edit_sensor_priority_button.clicked.connect(open_sensor_priority_dialog_qt)

    def add_raster_files_for_index():
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(main_window, "Select Raster Files", APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR), "GeoTIFF Files (*.tif *.tiff);;All Files (*)")
        if files:
            index_analysis_pane.selected_files_list_widget_ia.addItems(files)
            logging.info(f"Added files for index analysis: {files}")

    def add_raster_folder_for_index():
        folder = QtWidgets.QFileDialog.getExistingDirectory(main_window, "Select Folder Containing Rasters", APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR))
        if folder:
            # Scan for .tif or .tiff files
            raster_files_in_folder = []
            for filename in os.listdir(folder):
                if filename.lower().endswith((".tif", ".tiff")):
                    raster_files_in_folder.append(os.path.join(folder, filename))
            if raster_files_in_folder:
                index_analysis_pane.selected_files_list_widget_ia.addItems(raster_files_in_folder)
                logging.info(f"Added {len(raster_files_in_folder)} rasters from folder: {folder}")
            else:
                QtWidgets.QMessageBox.information(main_window, "No Rasters Found", f"No .tif or .tiff files found in {folder}.")


    def remove_selected_files_from_list():
        for item in index_analysis_pane.selected_files_list_widget_ia.selectedItems():
            index_analysis_pane.selected_files_list_widget_ia.takeItem(index_analysis_pane.selected_files_list_widget_ia.row(item))
        logging.info("Removed selected items from index analysis input list.")

    def clear_files_list_for_index():
        index_analysis_pane.selected_files_list_widget_ia.clear()
        logging.info("Cleared all items from index analysis input list.")

    def browse_index_output_dir():
        initial_dir_ia = index_analysis_pane.index_output_dir_input_ia.text() or APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR)
        directory = QtWidgets.QFileDialog.getExistingDirectory(main_window, "Select Output Directory for Indices", initial_dir_ia)
        if directory:
            index_analysis_pane.index_output_dir_input_ia.setText(directory)
            logging.info(f"Index analysis output directory selected: {directory}")

    def start_index_analysis_processing():
        input_items_str = index_analysis_pane.get_input_files() # List of file paths
        output_dir_str = index_analysis_pane.get_output_dir()
        selected_indices_list = index_analysis_pane.get_selected_indices() # List of index keys like "NDVI"

        if not input_items_str:
            QtWidgets.QMessageBox.warning(main_window, "Input Missing", "Please add raster files for index analysis.")
            return
        if not output_dir_str:
            QtWidgets.QMessageBox.warning(main_window, "Output Missing", "Please specify an output directory for indices.")
            return
        if not selected_indices_list:
            QtWidgets.QMessageBox.warning(main_window, "Indices Missing", "Please select at least one index to calculate.")
            return
        
        os.makedirs(output_dir_str, exist_ok=True)
        logging.info(f"Starting index analysis with inputs: {len(input_items_str)} files, output: {output_dir_str}, indices: {selected_indices_list}")
        # TODO: Implement actual index calculation logic here or in a separate thread.
        # This would involve:
        # 1. Iterating through input_items_str.
        # 2. For each file, opening with rasterio.
        # 3. For each selected_index in selected_indices_list:
        #    a. Identifying required bands (e.g., NIR, Red for NDVI) from AVAILABLE_INDICES[selected_index]["bands_needed"].
        #    b. Mapping these generic band names to actual band numbers in the raster (this is the tricky part, needs band metadata or assumptions).
        #    c. Reading the band data.
        #    d. Calculating the index using the formula.
        #    e. Saving the resulting index raster to output_dir_str.
        QtWidgets.QMessageBox.information(main_window, "Index Analysis", "Index analysis started (placeholder - check logs). Actual calculation logic needs implementation.")


    def apply_theme_qt(theme_name):
        global APP_CONFIG
        
        colors_to_apply = THEMES.get(theme_name, FLUTTERSHY_COLORS)
        
        new_stylesheet = get_stylesheet_qt(colors_to_apply)
        app.setStyleSheet(new_stylesheet) # Apply to whole application
        
        if APP_CONFIG.get('theme') != theme_name:
            APP_CONFIG['theme'] = theme_name
            update_and_save_app_config_qt() 
        
        if satellite_info_tab_instance: 
            satellite_info_tab_instance.update_theme(colors_to_apply)
        if index_analysis_pane: 
            index_analysis_pane.colors = colors_to_apply 
            # index_analysis_pane.apply_styles() # If it has a specific apply_styles method
        if data_viewer_tab: # Update DataViewerTab colors if it uses them
            data_viewer_tab.colors = colors_to_apply
            # data_viewer_tab.apply_styles() # If it has one
        if vector_download_tab_instance: # Update new tab's theme
            vector_download_tab_instance.update_theme(colors_to_apply)
        update_theme_menu_checked_state()

    theme_menu = menu_bar.addMenu(FLUTTERSHY_TEXTS.get("themes_menu_text", "&Themes"))
    theme_action_group = QtWidgets.QActionGroup(main_window)
    theme_action_group.setExclusive(True)

    fluttershy_action = QtWidgets.QAction("Fluttershy (Light)", main_window, checkable=True)
    fluttershy_action.triggered.connect(lambda: apply_theme_qt("Fluttershy"))
    theme_menu.addAction(fluttershy_action)
    theme_action_group.addAction(fluttershy_action)

    night_mode_action = QtWidgets.QAction("Night Mode", main_window, checkable=True)
    night_mode_action.triggered.connect(lambda: apply_theme_qt("Night Mode"))
    theme_menu.addAction(night_mode_action)
    theme_action_group.addAction(night_mode_action)

    def update_and_save_app_config_qt():
        global APP_CONFIG
        selected_tiling_method_text = tiling_method_combo.currentText()
        if selected_tiling_method_text == "Tile Size by Degree":
            APP_CONFIG['TILING_METHOD'] = "degree"
        elif selected_tiling_method_text == "Tile Count (Approx N)":
            APP_CONFIG['TILING_METHOD'] = "count"

        try: APP_CONFIG['TILE_SIZE_DEG'] = float(tile_size_deg_input.text())
        except ValueError: APP_CONFIG['TILE_SIZE_DEG'] = DEFAULT_TILE_SIZE_DEG
        try: APP_CONFIG['NUM_SUBSECTIONS'] = int(num_subsections_input.text())
        except ValueError: APP_CONFIG['NUM_SUBSECTIONS'] = DEFAULT_NUM_SUBSECTIONS
        try: APP_CONFIG['OVERLAP_DEG'] = float(overlap_deg_input.text())
        except ValueError: APP_CONFIG['OVERLAP_DEG'] = DEFAULT_OVERLAP_DEG
        try: APP_CONFIG['TARGET_RESOLUTION'] = int(target_resolution_input.text())
        except ValueError: APP_CONFIG['TARGET_RESOLUTION'] = DEFAULT_TARGET_RESOLUTION
        try: APP_CONFIG['MAX_WORKERS'] = int(max_workers_input.text())
        except ValueError: APP_CONFIG['MAX_WORKERS'] = DEFAULT_MAX_WORKERS
        
        APP_CONFIG['USE_BEST_RESOLUTION'] = use_best_resolution_checkbox.isChecked()
        APP_CONFIG['CLEANUP_TILES'] = cleanup_tiles_checkbox.isChecked()
        if APP_CONFIG['OVERLAP_DEG'] < 0: APP_CONFIG['OVERLAP_DEG'] = 0.0 # Ensure non-negative overlap

        APP_CONFIG['bbox_str'] = bbox_input.text() or DEFAULT_BBOX_STR
        APP_CONFIG['start_date'] = start_date_input.date().toString("yyyy-MM-dd")
        APP_CONFIG['end_date'] = end_date_input.date().toString("yyyy-MM-dd")
        APP_CONFIG['output_dir'] = output_dir_input.text() or DEFAULT_OUTPUT_DIR
        APP_CONFIG['overwrite'] = overwrite_checkbox.isChecked()
        
        config_full_path_save = os.path.join(SCRIPT_BASE_PATH, CONFIG_FILE_PATH)
        try:
            with open(config_full_path_save, 'w') as f:
                json.dump(APP_CONFIG, f, indent=4)
            logging.info(f"Saved config to {config_full_path_save}")
        except Exception as e:
            logging.error(f"Could not save config to {config_full_path_save}: {e}")

    def update_theme_menu_checked_state():
        current_theme_name = APP_CONFIG.get('theme', DEFAULT_THEME_QT)
        if current_theme_name == "Night Mode":
            night_mode_action.setChecked(True)
        else: 
            fluttershy_action.setChecked(True)

    def on_tiling_method_change_qt():
        selected_method_text = tiling_method_combo.currentText()
        is_degree_method = (selected_method_text == "Tile Size by Degree")
        
        tile_size_deg_input.setEnabled(is_degree_method)
        num_subsections_input.setEnabled(not is_degree_method)
        
        # Enable/disable labels associated with these inputs for clarity
        # Assuming tile_size_deg_label_with_help_widget and num_subsections_label_with_help_widget are the QWidget containers
        tile_size_deg_label_with_help_widget.setEnabled(is_degree_method)
        num_subsections_label_with_help_widget.setEnabled(not is_degree_method)
        
        update_and_save_app_config_qt() 

    def on_best_resolution_toggle_qt():
        is_checked = use_best_resolution_checkbox.isChecked()
        target_resolution_input.setEnabled(not is_checked)
        auto_tooltip = FLUTTERSHY_TEXTS.get("target_resolution_auto_tooltip", "Resolution automatically set.")
        manual_tooltip = FLUTTERSHY_TEXTS.get("target_resolution_manual_tooltip", "Target resolution in meters.")

        target_resolution_input.setToolTip(auto_tooltip if is_checked else manual_tooltip)
        update_and_save_app_config_qt()

    tiling_method_combo.currentTextChanged.connect(on_tiling_method_change_qt)
    on_tiling_method_change_qt() 

    def update_main_layout_for_viewer_mode(index): # index is of the current sub-tab in post_processing_sub_tabs
        if not post_processing_sub_tabs or \
           progress_bars_container is None or \
           log_console_label_widget is None or \
           log_console is None:
            logging.warning("update_main_layout_for_viewer_mode: One or more UI elements are None.")
            return
        
        current_sub_tab_widget = post_processing_sub_tabs.widget(index)
        
        is_data_viewer_active = (data_viewer_tab and current_sub_tab_widget is data_viewer_tab)
        
        progress_bars_container.setVisible(not is_data_viewer_active)
        log_console_label_widget.setVisible(not is_data_viewer_active)
        log_console.setVisible(not is_data_viewer_active)


    post_processing_sub_tabs.currentChanged.connect(update_main_layout_for_viewer_mode)

    use_best_resolution_checkbox.toggled.connect(on_best_resolution_toggle_qt)
    on_best_resolution_toggle_qt() 

    class MapInteractionHandler(QtCore.QObject):
        polygonCoordinatesSelected = QtCore.Signal(list) # list of [lon, lat]
        saveShapeRequested = QtCore.Signal(list, str) # list of [lat,lon] from JS, suggested_filename_base
        nominatimSearchResults = QtCore.Signal(str) # Signal to send search results (JSON string) to JS

        @QtCore.Slot(list) 
        def onPolygonCoordinatesSelected(self, coords_list_lat_lng_js):
            logging.info(f"Polygon coordinates received from JS (lat,lon order from JS): {coords_list_lat_lng_js}")
            # Convert to [[lon, lat], ...] for GEE and internal use
            coords_for_gee = [[coord[1], coord[0]] for coord in coords_list_lat_lng_js] 
            # Ensure polygon is closed for GEE if it's not already (Leaflet draw might not auto-close for pyHandler)
            if len(coords_for_gee) >= 3:
                first_pt = coords_for_gee[0]
                last_pt = coords_for_gee[-1]
                # Check if first and last points are different (within a small tolerance)
                if abs(first_pt[0] - last_pt[0]) > 1e-9 or abs(first_pt[1] - last_pt[1]) > 1e-9:
                    coords_for_gee.append(list(first_pt)) # Close the polygon
                    logging.info(f"Polygon closed for GEE. Now: {coords_for_gee}")
            self.polygonCoordinatesSelected.emit(coords_for_gee)

        @QtCore.Slot(list, str)
        def onSaveShapeAsShpRequested(self, coords_list_lat_lng_js, suggested_filename_base):
            # Pass through the coordinates (still lat,lon from JS) and filename base
            self.saveShapeRequested.emit(coords_list_lat_lng_js, suggested_filename_base)

        @QtCore.Slot(str)
        def requestNominatimSearch(self, query_string):
            """Called by JS to perform a Nominatim search from Python."""
            logging.info(f"MapInteractionHandler: Received Nominatim search request for: '{query_string}'")
            try:
                headers = {'User-Agent': f'FlutterEarth/{SCRIPT_VERSION} (QtPy App)'}
                # Use a slightly different endpoint or add more parameters if needed, e.g., for structured search
                url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(query_string)}&format=jsonv2&addressdetails=1&limit=7"
                response = requests.get(url, timeout=10, headers=headers)
                response.raise_for_status()
                results_json_str = response.text # Send as text to avoid double parsing issues
                self.nominatimSearchResults.emit(results_json_str)
                logging.info(f"MapInteractionHandler: Emitted Nominatim search results for '{query_string}'")
            except requests.RequestException as e:
                logging.error(f"MapInteractionHandler: Nominatim search HTTP error for '{query_string}': {e}")
                self.nominatimSearchResults.emit("[]") # Emit empty list on error
            except Exception as e:
                logging.error(f"MapInteractionHandler: Unexpected error in Nominatim search for '{query_string}': {e}", exc_info=True)
                self.nominatimSearchResults.emit("[]") # Emit empty list on error

    class MapSelectionDialog(QtWidgets.QDialog):
        def __init__(self, parent=None, initial_bbox_str=None, initial_polygon_coords_to_draw=None): # Added initial_polygon_coords_to_draw
            super().__init__(parent)
            self.setWindowTitle("Select AOI Polygon from Map 🦋")
            self.setMinimumSize(800, 600)
            self.selected_polygon_coords = None 
            self.initial_bbox_str = initial_bbox_str # For fallback map centering if no polygon
            self.initial_polygon_coords_to_draw = initial_polygon_coords_to_draw # For pre-drawing
            
            layout = QtWidgets.QVBoxLayout(self)
            self.web_view = QWebEngineView()
            layout.addWidget(self.web_view)

            self.channel = QWebChannel()
            self.interaction_handler = MapInteractionHandler()
            self.interaction_handler.polygonCoordinatesSelected.connect(self.handle_polygon_coords_from_js)
            self.interaction_handler.saveShapeRequested.connect(self.handle_save_shape_request_from_js)
            self.channel.registerObject("pyHandler", self.interaction_handler)
            self.web_view.page().setWebChannel(self.channel)

            # initialize_map_view will now use self.initial_bbox_str and self.initial_polygon_coords_to_draw
            self.web_view.page().loadFinished.connect(lambda ok: self.initialize_map_view(ok))
            
            html_content = """\
            <!DOCTYPE html>
            <html>
            <head>
                <title>Map AOI Selector</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
                <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
                <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.7.5/proj4.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/proj4leaflet/1.0.2/proj4leaflet.js"></script>
                <link rel="stylesheet" href="https://unpkg.com/leaflet-geosearch@3.8.0/dist/geosearch.css" />
                <script src="https://unpkg.com/leaflet-geosearch@3.8.0/dist/geosearch.umd.js"></script>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <style>
                    html, body { margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }
                    body { display: flex; flex-direction: column; }
                    #map { flex-grow: 1; background-color: #f0f0f0; }
                    .controls { padding: 8px; background-color: #f8f8f8; text-align: center; border-top: 1px solid #ccc; }
                    .controls button { margin: 4px; padding: 8px 12px; font-size: 13px; cursor: pointer; border-radius: 4px; border: 1px solid #bbb; }
                    .controls button:hover { background-color: #e0e0e0; }
                    #instruction { margin-left: 15px; font-style: italic; color: #555; }
                </style>
            </head>
            <body>
                <div class="controls">
                    <button onclick="sendSelectedPolygonToPython()" id="sendButton" disabled>Use This Polygon</button>
                        <button onclick="saveCurrentShapeAsShp()" id="saveShpButton" disabled>Save as SHP</button>
                    <span id="instruction">Draw a polygon or rectangle on the map.</span>
                </div>
                <div id="map"></div>
                <script>
                    var map = L.map('map', { preferCanvas: true }).setView([20, 0], 2); // Default global view
                    var pyHandler;
                    new QWebChannel(qt.webChannelTransport, function (channel) {
                        pyHandler = channel.objects.pyHandler;
                        // Connect Python signal to JS function
                        if (pyHandler && pyHandler.nominatimSearchResults) {
                            pyHandler.nominatimSearchResults.connect(handleNominatimResultsFromPython);
                        }
                        if (!pyHandler) console.error("Python handler (pyHandler) not found.");
                    });

                    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '&copy; OpenStreetMap contributors', maxZoom: 19
                    }).addTo(map);
                    var esriImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community', maxZoom: 18
                    });
                     var baseLayers = { "OpenStreetMap": osmLayer, "ESRI Imagery": esriImagery };
                    L.control.layers(baseLayers).addTo(map);

                    // Custom provider that uses our Python backend via pyHandler
                    const PythonNominatimProvider = {
                        search: async function({ query }) { // query is a string
                            if (pyHandler && pyHandler.requestNominatimSearch) {
                                console.log("JS: Requesting search from Python for:", query);
                                pyHandler.requestNominatimSearch(query); // Python will emit results via signal
                            } else { console.error("pyHandler or requestNominatimSearch not available."); }
                            return []; // GeoSearch expects a promise, but results are handled by signal
                        }
                    };

                    const searchControl = new GeoSearch.GeoSearchControl({
                        provider: PythonNominatimProvider, style: 'bar', showMarker: true, autoClose: true, retainZoomLevel: false, keepResult: true,
                    });
                    map.addControl(searchControl);

                    var drawnItems = new L.FeatureGroup();
                    map.addLayer(drawnItems);

                    var drawControl = new L.Control.Draw({
                        edit: { featureGroup: drawnItems, remove: true },
                        draw: { polygon: true, rectangle: true, polyline: false, circle: false, marker: false, circlemarker: false }
                    });
                    map.addControl(drawControl);
                    var currentSelectedLayer = null;

                    map.on(L.Draw.Event.CREATED, function (event) {
                        var layer = event.layer;
                        drawnItems.clearLayers(); // Clear previous drawings
                        drawnItems.addLayer(layer);
                        currentSelectedLayer = layer;
                        document.getElementById('sendButton').disabled = false;
                        document.getElementById('saveShpButton').disabled = false;
                        document.getElementById('instruction').textContent = "Polygon/Rectangle drawn. Click 'Use This Polygon'.";
                    });
                    map.on(L.Draw.Event.EDITED, function (event) {
                        // If features are edited, currentSelectedLayer might need update if multiple layers were somehow present
                        // For simplicity, assume one edited layer is the one we care about
                        if (drawnItems.getLayers().length > 0) {
                           currentSelectedLayer = drawnItems.getLayers()[0]; // Update to the (potentially new) layer object
                           document.getElementById('sendButton').disabled = false;
                           document.getElementById('saveShpButton').disabled = false;
                        } else { 
                            currentSelectedLayer = null; 
                            document.getElementById('sendButton').disabled = true;
                            document.getElementById('saveShpButton').disabled = true;
                        }
                    });
                     map.on(L.Draw.Event.DELETED, function (event) {
                        currentSelectedLayer = null;
                        document.getElementById('saveShpButton').disabled = true;
                        document.getElementById('sendButton').disabled = true;
                        document.getElementById('instruction').textContent = "Shape deleted. Draw a new polygon or rectangle.";
                    });

                    var searchResultMarkers = L.featureGroup().addTo(map);

                    function handleNominatimResultsFromPython(resultsJsonString) {
                        console.log("JS: Received Nominatim results from Python:", resultsJsonString.substring(0,100) + "...");
                        searchResultMarkers.clearLayers(); // Clear previous search markers
                        try {
                            const results = JSON.parse(resultsJsonString);
                            if (results && results.length > 0) {
                                const firstResult = results[0]; // Focus on the first result for simplicity
                                const lat = parseFloat(firstResult.lat);
                                const lon = parseFloat(firstResult.lon);
                                map.setView([lat, lon], 13); // Zoom to the first result
                                L.marker([lat, lon]).addTo(searchResultMarkers)
                                    .bindPopup(firstResult.display_name).openPopup();
                                console.log("JS: Map view set to first result:", firstResult.display_name);
                            } else {
                                console.log("JS: No results from Python search or empty results.");
                            }
                        } catch (e) {
                            console.error("JS: Error parsing Nominatim results from Python:", e, "Raw string:", resultsJsonString);
                        }
                    }

                    function sendSelectedPolygonToPython() {
                        if (!pyHandler) { alert("Error: Connection to Python application lost."); return; }
                        if (!currentSelectedLayer) { alert("No polygon selected or drawn."); return; }
                        
                        var latLngs;
                        if (currentSelectedLayer instanceof L.Polygon || currentSelectedLayer instanceof L.Rectangle) {
                            // For L.Polygon and L.Rectangle, getLatLngs()[0] gives the outer ring.
                            latLngs = currentSelectedLayer.getLatLngs()[0];
                        } else {
                            alert("Selected layer is not a polygon or rectangle."); return;
                        }

                        if (!latLngs || latLngs.length < 3) { alert("Invalid polygon (less than 3 points)."); return; }
                        
                        // Leaflet draw often doesn't close the polygon for the array it returns,
                        // GEE needs it closed (first and last point same).
                        var coordsForPy = latLngs.map(latlng => [latlng.lat, latlng.lng]); // Send as [[lat,lng],...]
                        
                        // The onPolygonCoordinatesSelected in Python will handle closing if needed.
                        pyHandler.onPolygonCoordinatesSelected(coordsForPy);
                        document.getElementById('instruction').textContent = "Polygon sent! You can close this window.";
                        // Optionally, disable button after sending or close dialog via JS if possible (more complex)
                    }

                    function saveCurrentShapeAsShp() {
                        if (!pyHandler) { alert("Error: Connection to Python application lost."); return; }
                        if (!currentSelectedLayer) { alert("No polygon selected or drawn to save."); return; }

                        var latLngs;
                        if (currentSelectedLayer instanceof L.Polygon || currentSelectedLayer instanceof L.Rectangle) {
                            latLngs = currentSelectedLayer.getLatLngs()[0];
                        } else {
                            alert("Selected layer is not a polygon or rectangle."); return;
                        }

                        if (!latLngs || latLngs.length < 3) { alert("Invalid polygon (less than 3 points)."); return; }
                        
                        var coordsForPy = latLngs.map(latlng => [latlng.lat, latlng.lng]); // Send as [[lat,lng],...]
                        var filenameBase = "drawn_aoi"; // Python side will add .shp

                        pyHandler.onSaveShapeAsShpRequested(coordsForPy, filenameBase);
                        // User will be prompted by Python for save location.
                    }

                    function drawInitialPolygonAndFit(coords_lat_lon_array_outer) {
                        // coords_lat_lon_array_outer is [[lat, lon], [lat, lon], ...]
                        if (!coords_lat_lon_array_outer || coords_lat_lon_array_outer.length < 3) {
                            console.error("Cannot draw initial polygon: not enough coordinates.");
                            return;
                        }
                        var latLngsForLeaflet = coords_lat_lon_array_outer.map(p => L.latLng(p[0], p[1]));
                        var polygon = L.polygon(latLngsForLeaflet);
                        
                        drawnItems.clearLayers(); // Clear any previous drawings
                        drawnItems.addLayer(polygon);
                        currentSelectedLayer = polygon;
                        
                        document.getElementById('sendButton').disabled = false;
                        document.getElementById('saveShpButton').disabled = false;
                        document.getElementById('instruction').textContent = "Imported shape loaded. Edit if needed, then 'Use This Polygon'.";
                        map.fitBounds(polygon.getBounds());
                    }

                    function setInitialMapPosition(minLon, minLat, maxLon, maxLat) {
                        if (minLon != null && minLat != null && maxLon != null && maxLat != null) {
                           try { map.fitBounds([[minLat, minLon], [maxLat, maxLon]]); } 
                           catch (e) { console.error("Error setting initial map bounds:", e); }
                        }
                    }
                </script>
            </body>
            </html>
            """ 
            self.web_view.setHtml(html_content, baseUrl=QtCore.QUrl("qrc:/")) # qrc:/ for qwebchannel.js

        def initialize_map_view(self, success):
            if not success:
                logging.error("MapSelectionDialog: Web page failed to load.")
                # Display an error message directly in the dialog if the page fails to load.
                if hasattr(self, 'web_view') and self.web_view:
                    self.web_view.hide() # Hide the (presumably blank) web view
                
                # Check if an error label already exists to avoid adding multiple
                if not hasattr(self, 'map_error_label'):
                    self.map_error_label = QtWidgets.QLabel("Map content failed to load.\n- Check internet connection for map resources (OpenStreetMap, ESRI, Leaflet CDNs).\n- Ensure PyQtWebEngine is correctly installed and its dependencies are met.\n- Check application logs for more details.")
                    self.map_error_label.setWordWrap(True)
                    self.map_error_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
                    self.map_error_label.setAlignment(Qt.AlignCenter)
                    self.layout().insertWidget(0, self.map_error_label) # Add error label to the dialog's layout
                return

            if self.initial_polygon_coords_to_draw: # These are [[lon,lat],...]
                # Convert to [[lat,lon],...] for JS Leaflet
                coords_for_js_lat_lon = [[p[1], p[0]] for p in self.initial_polygon_coords_to_draw]
                js_command = f"drawInitialPolygonAndFit({json.dumps(coords_for_js_lat_lon)});"
                self.web_view.page().runJavaScript(js_command)
                logging.info(f"MapSelectionDialog: Initializing map with polygon: {self.initial_polygon_coords_to_draw[:3]}...") # Log first few points
            elif self.initial_bbox_str: # Fallback to BBOX string for map positioning if no polygon
                logging.info(f"MapSelectionDialog: Initializing map with BBOX string for bounds: {self.initial_bbox_str}")
                try: # Try parsing initial_bbox_str as polygon JSON first for bounds
                    initial_coords_data = json.loads(self.initial_bbox_str)
                    if isinstance(initial_coords_data, list) and \
                       all(isinstance(p, list) and len(p) == 2 and all(isinstance(coord, (float, int)) for coord in p) for p in initial_coords_data) and \
                       len(initial_coords_data) >= 3:
                        lons = [p[0] for p in initial_coords_data]
                        lats = [p[1] for p in initial_coords_data]
                        self.web_view.page().runJavaScript(f"setInitialMapPosition({min(lons)}, {min(lats)}, {max(lons)}, {max(lats)});")
                        return 
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass # Not a polygon JSON, try as BBOX string

                try: # Try parsing as BBOX string: "minLon,minLat,maxLon,maxLat"
                    coords = [float(c.strip()) for c in self.initial_bbox_str.split(',')]
                    if len(coords) == 4:
                        self.web_view.page().runJavaScript(f"setInitialMapPosition({coords[0]}, {coords[1]}, {coords[2]}, {coords[3]});")
                except Exception as e_bbox_parse:
                    logging.warning(f"MapSelectionDialog: Failed to parse initial_bbox_str '{self.initial_bbox_str}' for map positioning: {e_bbox_parse}")
            else:
                logging.info("MapSelectionDialog: No initial polygon or BBOX string provided for map positioning. Map will use default view.")
            
            # Attempt to set focus to the map to enable keyboard shortcuts (zoom, pan)
            self.web_view.page().runJavaScript("document.getElementById('map').focus();")


        def handle_polygon_coords_from_js(self, polygon_coords_lon_lat): # Receives [[lon,lat],...]
            self.selected_polygon_coords = polygon_coords_lon_lat
            self.accept() 

        def get_selected_polygon_coords_str(self):
            if self.selected_polygon_coords:
                return json.dumps(self.selected_polygon_coords) 
            return None
        
        def handle_save_shape_request_from_js(self, coords_list_lat_lng_js, suggested_filename_base):
            # coords_list_lat_lng_js is [[lat,lng],...]
            if not coords_list_lat_lng_js or len(coords_list_lat_lng_js) < 3:
                QtWidgets.QMessageBox.warning(self, "Save Error", "Not enough points to form a polygon.")
                return

            save_file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Save Shapefile",
                os.path.join(APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR), f"{suggested_filename_base}.shp"),
                "Shapefiles (*.shp)"
            )

            if not save_file_path:
                return # User cancelled

            # Ensure filename ends with .shp
            if not save_file_path.lower().endswith(".shp"):
                save_file_path += ".shp"

            try:
                # Convert to [[lon,lat],...] for pyshp
                points_for_shp = [[coord[1], coord[0]] for coord in coords_list_lat_lng_js]

                # Ensure polygon is closed for pyshp
                if len(points_for_shp) >= 3:
                    first_pt_shp = points_for_shp[0]
                    last_pt_shp = points_for_shp[-1]
                    # Check if first and last points are different (within a small tolerance)
                    if abs(first_pt_shp[0] - last_pt_shp[0]) > 1e-9 or abs(first_pt_shp[1] - last_pt_shp[1]) > 1e-9:
                        points_for_shp.append(list(first_pt_shp)) # Close the polygon

                with shapefile.Writer(save_file_path, shapeType=shapefile.POLYGON) as w:
                    w.field('ID', 'N', 9, 0) # Add a simple ID field, ensure size and decimal are integers
                    w.record(1) # Record for the ID field
                    w.poly([points_for_shp]) # Add the polygon geometry AFTER the record

                logging.info(f"Drawn shape saved as shapefile: {save_file_path}")
                QtWidgets.QMessageBox.information(self, "Shapefile Saved", f"The drawn shape was successfully saved to:\n{save_file_path}")

            except shapefile.ShapefileException as e_shp:
                QtWidgets.QMessageBox.critical(self, "Shapefile Save Error", f"Error writing shapefile '{os.path.basename(save_file_path)}':\n{e_shp}")
                logging.error(f"Error writing shapefile {save_file_path}: {e_shp}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Save Error", f"An unexpected error occurred while saving the shapefile:\n{e}")
                logging.error(f"Unexpected error saving shapefile {save_file_path}: {e}", exc_info=True)

    def open_map_selection_dialog(initial_polygon_coords=None): # Added optional arg
        current_aoi_str_for_fallback_bounds = bbox_input.text() # Keep this for map centering if no polygon
        dialog = MapSelectionDialog(
            main_window,
            initial_bbox_str=current_aoi_str_for_fallback_bounds, # For centering if no polygon is drawn/imported
            initial_polygon_coords_to_draw=initial_polygon_coords # The new parameter for pre-drawing
        )
        if dialog.exec_() == QtWidgets.QDialog.Accepted: 
            # This part is reached when "Use This Polygon" is clicked in the map dialog
            selected_polygon_json_str = dialog.get_selected_polygon_coords_str()
            # Determine which input field to update based on the dialog's parent or a passed target
            # For now, this function is only called by the main settings' map button.
            # If called from VectorDownloadTab, that tab would have its own similar function.
            # This specific instance updates the main bbox_input.
            if selected_polygon_json_str and hasattr(main_window, 'bbox_input'): # Check if main_window.bbox_input exists
                bbox_input.setText(selected_polygon_json_str)
                update_and_save_app_config_qt() # Save the new AOI

    select_bbox_from_map_button.clicked.connect(open_map_selection_dialog)

    def import_shapefile_to_aoi_qt():
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            main_window, 
            "Select Shapefile for AOI", 
            APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR), 
            "Shapefiles (*.shp)"
        )
        if not file_path:
            return

        try:
            sf = shapefile.Reader(file_path)
            first_polygon_points = None
            
            for shape_record in sf.iterShapeRecords():
                # Check for polygon types (POLYGON, POLYGONZ, POLYGONM)
                if shape_record.shape.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM, 5, 15, 25]: # Added numeric types for robustness
                    points = shape_record.shape.points
                    parts = shape_record.shape.parts

                    if not points or not parts: # Should not happen for valid polygon
                        continue

                    # Extract coordinates of the first part of this polygon feature
                    start_index = parts[0]
                    end_index = parts[1] if len(parts) > 1 else len(points)
                    
                    first_part_coords_raw = points[start_index:end_index]
                    
                    # Ensure the polygon part is closed for GeoJSON-like representation
                    # pyshp points are [x,y] (lon,lat)
                    if first_part_coords_raw[0][0] != first_part_coords_raw[-1][0] or \
                       first_part_coords_raw[0][1] != first_part_coords_raw[-1][1]:
                        first_part_coords_raw.append(list(first_part_coords_raw[0])) # Append a copy of the first point

                    first_polygon_points = [[p[0], p[1]] for p in first_part_coords_raw]
                    break # Use the first polygon feature found
            
            if first_polygon_points:
                if len(first_polygon_points) >= 3: # Ensure at least 3 points for a valid polygon
                    logging.info(f"Shapefile '{os.path.basename(file_path)}' read. Opening map to display/edit polygon ({len(first_polygon_points)} points). Using first part of first polygon feature. Ensure WGS84 projection.")
                    # Call open_map_selection_dialog with these coordinates
                    # The bbox_input.setText and config save will happen if user clicks "Use This Polygon" in the map dialog
                    open_map_selection_dialog(initial_polygon_coords=first_polygon_points)
                else:
                    QtWidgets.QMessageBox.warning(main_window, "Invalid Polygon", f"The first polygon feature found in '{os.path.basename(file_path)}' has {len(first_polygon_points)} points (less than 3) and cannot be displayed on the map.")
                    logging.warning(f"Shapefile '{os.path.basename(file_path)}': first polygon part has < 3 points ({len(first_polygon_points)}).")
            else:
                QtWidgets.QMessageBox.warning(main_window, "No Polygon Found", "No polygon features found in the selected shapefile.")
        except shapefile.ShapefileException as e_shp:
            QtWidgets.QMessageBox.critical(main_window, "Shapefile Error", f"Error reading shapefile '{os.path.basename(file_path)}':\n{e_shp}")
            logging.error(f"Error reading shapefile {file_path}: {e_shp}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(main_window, "Import Error", f"An unexpected error occurred during shapefile import:\n{e}")
            logging.error(f"Unexpected error importing shapefile {file_path}: {e}", exc_info=True)

    class ProcessingThread(QtCore.QThread):
        status_update = QtCore.Signal(str)
        overall_progress_update = QtCore.Signal(int, int) 
        tile_progress_update = QtCore.Signal(int, int)    
        processing_finished_signal = QtCore.Signal(str) 
        message_box_signal = QtCore.Signal(str, str) 

        def __init__(self, params, tiles_list, is_polygon_aoi): # is_polygon_aoi indicates if params['area_of_interest'] is polygon coords
            super().__init__()
            self.params = params
            self.tiles_list = tiles_list # This is always a list of BBOXes for tiling, even if AOI was polygon
            self.is_polygon_aoi = is_polygon_aoi 
            self.cancel_event = threading.Event() 

        def run(self):
            try:
                start_tm = time.time()
                months_to_proc = []
                curr_dt = self.params['start_date'] # datetime object
                while curr_dt <= self.params['end_date']:
                    months_to_proc.append((curr_dt.year, curr_dt.month))
                    curr_dt = (curr_dt.replace(day=1) + relativedelta(months=1))
                
                total_m_count = len(months_to_proc)
                logging.info(f"Thread: Period: {self.params['start_date']:%Y-%m-%d} to {self.params['end_date']:%Y-%m-%d} ({total_m_count} months)")
                
                m_processed_ok, m_attempted = 0, 0

                def gui_tile_progress_callback(c, t): self.tile_progress_update.emit(c, t)
                def gui_status_callback(msg): self.status_update.emit(msg)

                for year, month in months_to_proc:
                    if self.cancel_event.is_set():
                        logging.info("Thread: Processing stopped by user.")
                        self.status_update.emit("Downloads paused by user.")
                        break
                    
                    m_attempted += 1
                    self.status_update.emit(f"Working on {year}-{month:02d} ({m_attempted}/{total_m_count})...")
                    self.tile_progress_update.emit(0, 1) 
                    
                    logging.info(f"\n🌸🌸🌸 Thread: Month {year}-{month:02d} ({m_attempted}/{total_m_count}) 🌸🌸🌸")
                    
                    # process_month expects tiles_definition_list, which is self.tiles_list
                    success, _ = process_month(year, month, self.params['output_dir'], self.tiles_list,
                                               self.params['overwrite'], self.cancel_event,
                                               gui_tile_progress_callback, gui_status_callback)
                    if success: m_processed_ok += 1
                    elif not self.cancel_event.is_set():
                        logging.error(f"Thread: Month {year}-{month:02d} encountered an issue.")
                    
                    self.overall_progress_update.emit(m_attempted, total_m_count)
                
                elapsed = time.time() - start_tm
                final_status_msg = "Processing cancelled by user." if self.cancel_event.is_set() else "Processing finished."
                summary_msg = (f"{final_status_msg}\n"
                               f"Total months to check: {total_m_count}\n"
                               f"Months attempted: {m_attempted}\n"
                               f"Months successful/skipped: {m_processed_ok}\n"
                               f"Total time: {elapsed:.2f} seconds")
                
                logging.info(f"\n{'='*15} THREAD: {final_status_msg.upper()} {'='*15}\n{summary_msg}")
                self.processing_finished_signal.emit(summary_msg)

            except Exception as e:
                logging.error(f"Thread: Critical processing error: {e}", exc_info=True)
                self.processing_finished_signal.emit(f"An unexpected error occurred in processing thread:\n{e}")
        
        def request_cancel_thread(self): 
            self.cancel_event.set()

    def start_download_qt():
        global is_processing_qt, cancel_requested_qt, processing_thread_instance
        if is_processing_qt:
            QtWidgets.QMessageBox.warning(main_window, "Busy Bee!", "Processing already happening, one moment please!")
            return

        parsed_aoi_coords = None
        is_polygon_aoi_flag = False
        try:
            # Get values from APP_CONFIG as it should be the source of truth after GUI updates
            bbox_str_val = APP_CONFIG.get('bbox_str', DEFAULT_BBOX_STR)
            start_d_str = APP_CONFIG.get('start_date', DEFAULT_START_DATE)
            end_d_str = APP_CONFIG.get('end_date', DEFAULT_END_DATE)
            start_d_val = datetime.strptime(start_d_str, "%Y-%m-%d")
            end_d_val = datetime.strptime(end_d_str, "%Y-%m-%d")

            if start_d_val > end_d_val: raise ValueError("Start Date should be before or same as End Date!")
            out_dir_val = APP_CONFIG.get('output_dir', DEFAULT_OUTPUT_DIR)
            if not out_dir_val: raise ValueError("Output Directory is needed.")
            
            if not bbox_str_val: raise ValueError("Area of Interest (BBOX or Polygon JSON) is required.")
            try:
                parsed_aoi_coords = json.loads(bbox_str_val) # Try Polygon JSON first
                if not (isinstance(parsed_aoi_coords, list) and
                        all(isinstance(p, list) and len(p) == 2 and all(isinstance(coord, (float, int)) for coord in p) for p in parsed_aoi_coords) and
                        len(parsed_aoi_coords) >= 3): 
                    raise ValueError("Invalid polygon JSON structure. Expected list of [lon, lat] pairs.")
                is_polygon_aoi_flag = True
                logging.info(f"Using Polygon AOI: {parsed_aoi_coords}")
            except (json.JSONDecodeError, ValueError, TypeError): # If not valid JSON or not polygon structure, try BBOX
                try:
                    bbox_val_parsed = [float(c.strip()) for c in bbox_str_val.split(',')]
                    if not (len(bbox_val_parsed) == 4 and 
                            -180 <= bbox_val_parsed[0] <= 180 and -90 <= bbox_val_parsed[1] <= 90 and
                            -180 <= bbox_val_parsed[2] <= 180 and -90 <= bbox_val_parsed[3] <= 90 and
                            bbox_val_parsed[0] < bbox_val_parsed[2] and bbox_val_parsed[1] < bbox_val_parsed[3]): # minLon < maxLon, minLat < maxLat
                        raise ValueError("Invalid BBOX format or values. Expected 'minLon,minLat,maxLon,maxLat' with valid ranges and order.")
                    parsed_aoi_coords = bbox_val_parsed
                    is_polygon_aoi_flag = False
                    logging.info(f"Using BBOX AOI: {parsed_aoi_coords}")
                except (ValueError, TypeError) as e_bbox_parse:
                    raise ValueError(f"Invalid AOI string. Not a valid BBOX ('lon,lat,lon,lat') or Polygon JSON ('[[lon,lat],...]'). Error: {e_bbox_parse}")

            params_for_thread = {
                'area_of_interest': parsed_aoi_coords, 
                'start_date': start_d_val, 'end_date': end_d_val,
                'output_dir': out_dir_val,
                'overwrite': APP_CONFIG.get('overwrite', False)
            }
        except ValueError as e_val:
            QtWidgets.QMessageBox.critical(main_window, "Input Error", str(e_val))
            status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_input_error_prefix", "Error: ") + str(e_val))
            return
        
        try:
            os.makedirs(params_for_thread['output_dir'], exist_ok=True)
            # Log file setup should happen once, or be reconfigurable if output dir changes.
            # For simplicity, ensure it's set up for the current output dir.
            setup_main_app_logging(params_for_thread['output_dir'], initial_setup=False) # initial_setup=False here, as it's for a specific run
        except Exception as e_log_setup:
            logging.error(f"Log setup error: {e_log_setup}", exc_info=True)
            QtWidgets.QMessageBox.critical(main_window, "Log Error", f"Log setup failed: {e_log_setup}")
            return

        if not initialize_earth_engine_with_retry(): # Re-check EE init before run
            logging.error("EE re-initialization failed before starting download.")
            status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_ee_init_fail", "EE Init Failed."))
            return
        
        try:
            aoi_for_tiling_generation = params_for_thread['area_of_interest']
            if is_polygon_aoi_flag: # If AOI is a polygon, get its bounding box for tiling
                lons = [p[0] for p in aoi_for_tiling_generation]
                lats = [p[1] for p in aoi_for_tiling_generation]
                bbox_of_polygon_for_tiling = [min(lons), min(lats), max(lons), max(lats)]
                tiles_list_val = generate_tiles_from_bbox(bbox_of_polygon_for_tiling)
            else: # AOI is already a BBOX list
                tiles_list_val = generate_tiles_from_bbox(aoi_for_tiling_generation)
            if not tiles_list_val: raise ValueError("Tile generation resulted in an empty list.")
        except ValueError as e_tile_gen:
            logging.error(f"Tile generation error: {e_tile_gen}", exc_info=True)
            QtWidgets.QMessageBox.critical(main_window, "Tile Generation Error", f"Could not generate tiles: {e_tile_gen}")
            return

        is_processing_qt = True
        cancel_requested_qt = False 
        status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_processing_started", "Processing started..."))
        start_button_qt.setEnabled(False)
        start_button_qt.setText(FLUTTERSHY_TEXTS.get("run_button_processing", "Working Gently... 🐾"))
        cancel_button_qt.setEnabled(True)
        cancel_button_qt.setText(FLUTTERSHY_TEXTS.get("cancel_button", "🍃 Cancel 🍂"))
        verify_button_qt.setEnabled(False) # Disable verify during main processing
        overall_progress_bar.setValue(0)
        monthly_progress_bar.setValue(0)

        processing_thread_instance = ProcessingThread(params_for_thread, tiles_list_val, is_polygon_aoi_flag)
        processing_thread_instance.status_update.connect(status_bar_qt.showMessage)
        processing_thread_instance.overall_progress_update.connect(lambda c, t: overall_progress_bar.setValue(int((c/t)*100) if t > 0 else 0))
        processing_thread_instance.tile_progress_update.connect(lambda c, t: monthly_progress_bar.setValue(int((c/t)*100) if t > 0 else 0))
        processing_thread_instance.processing_finished_signal.connect(on_processing_finished_qt)
        processing_thread_instance.start()


    def on_processing_finished_qt(final_message):
        global is_processing_qt
        final_status_text_key = "status_bar_processing_finished"
        if "cancelled" in final_message.lower() or "paused" in final_message.lower():
            final_status_text_key = "status_bar_cancellation_requested"
        
        status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get(final_status_text_key, "Processing ended."))
        is_processing_qt = False
        start_button_qt.setEnabled(True)
        start_button_qt.setText(FLUTTERSHY_TEXTS.get("run_button", "🌸 Start Download 🌸"))
        cancel_button_qt.setEnabled(False)
        cancel_button_qt.setText(FLUTTERSHY_TEXTS.get("cancel_button", "🍃 Cancel 🍂"))
        verify_button_qt.setEnabled(True) # Re-enable verify
        
        if "cancelled" not in final_message.lower() and overall_progress_bar.value() < 100 and overall_progress_bar.maximum() > 0 :
             overall_progress_bar.setValue(100) # Ensure 100% if not cancelled and finished
             monthly_progress_bar.setValue(100) 

        QtWidgets.QMessageBox.information(main_window, "Download Status", final_message)


    def cancel_download_qt():
        global cancel_requested_qt, is_processing_qt, processing_thread_instance
        if is_processing_qt and processing_thread_instance:
            reply = QtWidgets.QMessageBox.question(main_window, "Confirm Cancel", 
                                         FLUTTERSHY_TEXTS.get("confirm_cancel_message", "Are you sure you want to stop the current downloads, sweetie?"),
                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                cancel_requested_qt = True 
                processing_thread_instance.request_cancel_thread() 
                status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_cancellation_requested", "Cancellation requested..."))
                cancel_button_qt.setEnabled(False) # Disable until process confirms stop
                cancel_button_qt.setText(FLUTTERSHY_TEXTS.get("cancel_button_cancelling", "Pausing..."))
        else:
            logging.info("Cancel requested but no process running or thread not active.")
    
    class VerificationThread(QtCore.QThread):
        verification_finished = QtCore.Signal(list, str) 
        status_update = QtCore.Signal(str)

        def __init__(self, aoi_coords_arg, is_aoi_polygon_arg):
            super().__init__()
            self.aoi_coords = aoi_coords_arg
            self.cancel_event = threading.Event() 
            self.is_aoi_polygon = is_aoi_polygon_arg

        def run(self):
            results = []
            if not initialize_earth_engine_with_retry(): 
                results.append("Critical: Earth Engine initialization failed during verification.")
                self.verification_finished.emit(results, "EE Init Failed during verification.")
                return

            sensor_priority_list = APP_CONFIG.get('SENSOR_PRIORITY_ORDER', DEFAULT_SENSOR_PRIORITY_ORDER)
            
            try:
                if self.is_aoi_polygon:
                    roi_geometry = ee.Geometry.Polygon([self.aoi_coords]) # GEE Polygon needs list of list of lists for exterior
                else: 
                    roi_geometry = ee.Geometry.Rectangle(self.aoi_coords)
                logging.info(f"VerificationThread: ROI type: {'Polygon' if self.is_aoi_polygon else 'Rectangle'}")
            except Exception as e_roi:
                logging.error(f"VerificationThread: Error creating ROI geometry: {e_roi}")
                results.append(f"Critical: Could not form ROI for verification: {e_roi}")
                self.verification_finished.emit(results, "ROI Error for verification.")
                return


            for i, sensor_name in enumerate(sensor_priority_list):
                if self.cancel_event.is_set():
                    results.append("Verification cancelled by user.")
                    break
                self.status_update.emit(f"Verifying {sensor_name} ({i+1}/{len(sensor_priority_list)})...")
                logging.info(f"Verifying connectivity for {sensor_name} in AOI...")
                try:
                    collection = get_collection(sensor_name)
                    # A light check: filter by bounds and try to get size of limit 1.
                    image_count = collection.filterBounds(roi_geometry).limit(1).size().getInfo()
                    if image_count > 0:
                        results.append(f"✅ {sensor_name}: Connected (found images in AOI)")
                        logging.info(f"Successfully connected to {sensor_name} and found images in AOI.")
                    else:
                        results.append(f"⚠️ {sensor_name}: Connected (NO images found in AOI for this sensor)")
                        logging.warning(f"Connected to {sensor_name} but no images found in AOI.")
                except ValueError as ve: # From get_collection if sensor not defined
                    results.append(f"❌ {sensor_name}: Failed (Collection definition error: {ve})")
                    logging.error(f"Failed to get collection for {sensor_name}: {ve}")
                except ee.EEException as eee:
                    results.append(f"❌ {sensor_name}: Failed (GEE error: {str(eee)[:100]})") # Short error
                    logging.error(f"GEE error verifying {sensor_name}: {eee}")
                except Exception as e: # Catch any other unexpected error
                    results.append(f"❌ {sensor_name}: Failed (Unexpected error: {type(e).__name__})")
                    logging.error(f"Unexpected error verifying {sensor_name}: {e}", exc_info=True)
            
            self.verification_finished.emit(results, FLUTTERSHY_TEXTS.get("verify_satellites_status_done", "Satellite verification complete."))

        def request_cancel(self): 
            self.cancel_event.set()

    def verify_satellites_qt():
        global is_verifying_qt, verification_thread_instance
        if is_processing_qt:
             QtWidgets.QMessageBox.warning(main_window, "Busy", "Main download process is running. Please wait before verifying.")
             return
        
        parsed_aoi_coords_verify = None
        is_polygon_aoi_verify_flag = False
        try:
            bbox_str_val_verify = APP_CONFIG.get('bbox_str', DEFAULT_BBOX_STR) # Use config
            if not bbox_str_val_verify: raise ValueError("Area of Interest (BBOX or Polygon JSON) is required for verification.")
            
            try: 
                parsed_aoi_coords_verify = json.loads(bbox_str_val_verify)
                if not (isinstance(parsed_aoi_coords_verify, list) and
                        all(isinstance(p, list) and len(p) == 2 and all(isinstance(coord, (float, int)) for coord in p) for p in parsed_aoi_coords_verify) and
                        len(parsed_aoi_coords_verify) >= 3):
                    raise ValueError("Invalid polygon JSON structure for verification")
                is_polygon_aoi_verify_flag = True
            except (json.JSONDecodeError, ValueError, TypeError): 
                try:
                    bbox_val_parsed_verify = [float(c.strip()) for c in bbox_str_val_verify.split(',')]
                    if not (len(bbox_val_parsed_verify) == 4 and 
                            bbox_val_parsed_verify[0] < bbox_val_parsed_verify[2] and 
                            bbox_val_parsed_verify[1] < bbox_val_parsed_verify[3]):
                        raise ValueError("Invalid BBOX format for verification (minLon,minLat,maxLon,maxLat).")
                    parsed_aoi_coords_verify = bbox_val_parsed_verify
                    is_polygon_aoi_verify_flag = False
                except (ValueError, TypeError) as e_bbox_v:
                    raise ValueError(f"Invalid AOI string for verification. Not BBOX or Polygon JSON. Error: {e_bbox_v}")
        except ValueError as e_val_v:
            QtWidgets.QMessageBox.critical(main_window, "Input Error", f"Cannot verify satellites: {e_val_v}")
            status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_input_error_prefix", "Error: ") + f"Cannot verify: {e_val_v}")
            return

        status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("verify_satellites_status_start", "Verifying satellite connectivity..."))
        is_verifying_qt = True
        verify_button_qt.setEnabled(False)
        verify_button_qt.setText(FLUTTERSHY_TEXTS.get("verify_satellites_button_verifying", "Verifying... 📡"))
        start_button_qt.setEnabled(False) # Disable start during verification

        verification_thread_instance = VerificationThread(parsed_aoi_coords_verify, is_polygon_aoi_verify_flag)
        verification_thread_instance.status_update.connect(status_bar_qt.showMessage)
        verification_thread_instance.verification_finished.connect(on_verification_finished_qt)
        verification_thread_instance.start()

    def on_verification_finished_qt(results_list, status_message_override):
        global is_verifying_qt
        status_bar_qt.showMessage(status_message_override)
        is_verifying_qt = False
        verify_button_qt.setEnabled(True)
        verify_button_qt.setText(
            FLUTTERSHY_TEXTS.get("verify_satellites_button_icon", "🛰️") + " " +
            FLUTTERSHY_TEXTS.get("verify_button_text_base", "Verify Satellite Friends"))
        start_button_qt.setEnabled(True) # Re-enable start button
        
        # Display results in a message box
        results_text = "\n".join(results_list) if results_list else "No results from verification process."
        msg_box_verify = QtWidgets.QMessageBox(main_window)
        msg_box_verify.setWindowTitle(FLUTTERSHY_TEXTS.get("verify_satellites_title", "Satellite Connectivity Check"))
        msg_box_verify.setText(results_text)
        msg_box_verify.setIcon(QtWidgets.QMessageBox.Information)
        ok_btn_verify = msg_box_verify.addButton(QtWidgets.QMessageBox.Ok)
        # Style OK button from theme
        current_colors_for_dialog_verify = get_current_theme_colors()
        ok_btn_verify.setStyleSheet(
            f"background-color: {current_colors_for_dialog_verify['BUTTON_PINK_BG']};"
            f"color: {current_colors_for_dialog_verify['BUTTON_PINK_FG']};"
            f"padding: 5px 15px; font-weight: bold;")
        msg_box_verify.exec_()


    start_button_qt.clicked.connect(start_download_qt)
    cancel_button_qt.clicked.connect(cancel_download_qt)
    tile_size_deg_input.textChanged.connect(update_and_save_app_config_qt)
    num_subsections_input.textChanged.connect(update_and_save_app_config_qt)
    bbox_input.textChanged.connect(update_and_save_app_config_qt) 
    overwrite_checkbox.stateChanged.connect(update_and_save_app_config_qt)
    cleanup_tiles_checkbox.stateChanged.connect(update_and_save_app_config_qt)
    overlap_deg_input.textChanged.connect(update_and_save_app_config_qt)
    target_resolution_input.textChanged.connect(update_and_save_app_config_qt)
    max_workers_input.textChanged.connect(update_and_save_app_config_qt)
    output_dir_input.textChanged.connect(update_and_save_app_config_qt) # Save output dir on change
    start_date_input.dateChanged.connect(update_and_save_app_config_qt) # Save dates on change
    end_date_input.dateChanged.connect(update_and_save_app_config_qt)   # Save dates on change

    import_shp_button.clicked.connect(import_shapefile_to_aoi_qt)

    index_analysis_pane.add_files_button_ia.clicked.connect(add_raster_files_for_index)
    index_analysis_pane.add_folder_button_ia.clicked.connect(add_raster_folder_for_index)
    index_analysis_pane.remove_selected_button_ia.clicked.connect(remove_selected_files_from_list)
    index_analysis_pane.clear_list_button_ia.clicked.connect(clear_files_list_for_index)
    index_analysis_pane.index_browse_button_ia.clicked.connect(browse_index_output_dir)
    index_analysis_pane.start_index_analysis_button_ia.clicked.connect(start_index_analysis_processing)
    index_analysis_pane.index_output_dir_input_ia.textChanged.connect(lambda: APP_CONFIG.update({'index_analysis_output_dir': index_analysis_pane.index_output_dir_input_ia.text()})) # Quick save for this field if needed in APP_CONFIG

    
    verify_button_qt.clicked.connect(verify_satellites_qt)

    def on_sample_download_finished(sample_key_from_signal, success, message_or_filepath):
        global sample_download_thread_instance
        splash_message_color = QtGui.QColor(FLUTTERSHY_COLORS.get("TEXT_LIGHT", "grey"))
        if success:
            splash_msg_text = f"Sample data ready: {os.path.basename(message_or_filepath)}"
            logging.info(f"Sample data download successful: {message_or_filepath}")
            if data_viewer_tab: 
                data_viewer_tab.load_specific_raster(filepath=message_or_filepath)
                if main_tab_widget and post_processing_main_tab and post_processing_sub_tabs:
                    main_tab_widget.setCurrentWidget(post_processing_main_tab)
                    post_processing_sub_tabs.setCurrentWidget(data_viewer_tab)
        else:
            area_name_for_msg = sample_key_from_signal
            if sample_key_from_signal in ALL_SAMPLE_CONFIGS:
                area_name_for_msg = ALL_SAMPLE_CONFIGS[sample_key_from_signal].get("area_name", sample_key_from_signal)
            splash_msg_text = f"Sample '{area_name_for_msg}' download failed: {message_or_filepath}"
            splash_message_color = QtGui.QColor("red")
            logging.error(f"Sample data download failed for '{sample_key_from_signal}': {message_or_filepath}")
        
        if splash.isVisible(): # Only update splash if it's still visible
            splash.showMessage(splash_msg_text, Qt.AlignBottom | Qt.AlignHCenter, splash_message_color)
            app.processEvents() # Allow splash to update
        else: # If splash is gone, use status bar or a dialog
            # Re-fetch area_name_for_msg for non-splash messages if not already set for failure case
            if success: # success case already has a good splash_msg_text
                pass
            elif 'area_name_for_msg' not in locals(): # Ensure area_name_for_msg is defined for failure message box
                area_name_for_msg = sample_key_from_signal
            status_bar_qt.showMessage(splash_msg_text, 5000) # Show for 5 seconds
            if not success:
                QtWidgets.QMessageBox.warning(main_window, "Sample Data Download", splash_msg_text)


        sample_download_thread_instance = None 

    def start_next_queued_sample_download_qt():
        global sample_download_thread_instance, samples_to_download_queue_qt

        if sample_download_thread_instance is not None and sample_download_thread_instance.isRunning():
            logging.info("start_next_queued_sample_download_qt: Another sample download is already in progress.")
            return

        if not samples_to_download_queue_qt:
            logging.info("start_next_queued_sample_download_qt: No more samples in the download queue.")
            if splash.isVisible():
                 splash.showMessage("All pending sample downloads complete or queue empty.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
                 app.processEvents()
            return

        sample_key, config_to_download, base_path_for_sample = samples_to_download_queue_qt.pop(0)

        area_name_display = config_to_download.get('area_name', sample_key)
        logging.info(f"Starting download for queued sample: {sample_key} ('{area_name_display}')")
        if splash.isVisible():
            splash.showMessage(f"Downloading sample: {area_name_display} ({len(samples_to_download_queue_qt)+1} left in queue)...",
                               Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
        app.processEvents()

        sample_download_thread_instance = SampleDownloadThread(sample_key, config_to_download, base_path_for_sample)
        sample_download_thread_instance.sample_download_finished.connect(on_sample_download_finished)
        sample_download_thread_instance.start()

    def check_and_download_sample_data_on_startup():
        global samples_to_download_queue_qt

        if not ALL_SAMPLE_CONFIGS:
            logging.error("ALL_SAMPLE_CONFIGS is empty. Cannot check or download sample data.")
            if splash.isVisible(): splash.showMessage("Error: Sample data configurations missing.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor("red"))
            app.processEvents()
            return

        default_sample_loaded_on_startup = False

        for sample_key, current_sample_config in ALL_SAMPLE_CONFIGS.items():
            area_name_display = current_sample_config.get('area_name', sample_key)
            sample_output_dir = os.path.join(SCRIPT_BASE_PATH, current_sample_config["output_subdir"])
            sample_file_name = f"{area_name_display}_{current_sample_config['sensor']}_{current_sample_config['year']}-{current_sample_config['month']:02d}.tif"
            expected_sample_filepath = os.path.join(sample_output_dir, sample_file_name)

            logging.info(f"Checking for sample data: {expected_sample_filepath} (Key: {sample_key})")

            if os.path.exists(expected_sample_filepath):
                logging.info(f"Sample data for '{area_name_display}' found at: {expected_sample_filepath}.")
                if splash.isVisible():
                    splash.showMessage(f"Sample '{area_name_display}' found.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
                    app.processEvents()

                if sample_key == DEFAULT_SAMPLE_KEY and data_viewer_tab and not default_sample_loaded_on_startup:
                    data_viewer_tab.load_specific_raster(filepath=expected_sample_filepath)
                    if main_tab_widget and post_processing_main_tab and post_processing_sub_tabs:
                        main_tab_widget.setCurrentWidget(post_processing_main_tab)
                        post_processing_sub_tabs.setCurrentWidget(data_viewer_tab)
                    default_sample_loaded_on_startup = True
            else:
                logging.info(f"Sample data for '{area_name_display}' not found. Will prompt user.")
                if splash.isVisible():
                    splash.showMessage(f"Checking for optional sample: {area_name_display}...", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
                app.processEvents()

                reply = QtWidgets.QMessageBox.question(
                    main_window,
                    f"Optional Sample: {area_name_display}",
                    f"Flutter Earth can download the sample dataset: {area_name_display}.\n"
                    "This is optional and allows you to test processing features.\n\n"
                    f"Download '{area_name_display}' now? (Requires internet & EE auth).",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )

                if reply == QtWidgets.QMessageBox.Yes:
                    logging.info(f"User opted to download sample data for key '{sample_key}'. Adding to queue.")
                    samples_to_download_queue_qt.append((sample_key, current_sample_config, SCRIPT_BASE_PATH))
                else:
                    logging.info(f"User declined to download sample data for key '{sample_key}'.")
                    if splash.isVisible():
                        splash.showMessage(f"Sample download for '{area_name_display}' skipped.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
                    app.processEvents()

        if samples_to_download_queue_qt:
            logging.info(f"Starting download for {len(samples_to_download_queue_qt)} queued samples.")
            start_next_queued_sample_download_qt()
        elif default_sample_loaded_on_startup:
             if splash.isVisible(): splash.showMessage(f"Default sample '{ALL_SAMPLE_CONFIGS.get(DEFAULT_SAMPLE_KEY, {}).get('area_name', DEFAULT_SAMPLE_KEY)}' loaded. No new downloads.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
        else:
            if splash.isVisible(): splash.showMessage("No new sample downloads. Startup checks complete.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
            app.processEvents()

    if splash.isVisible(): splash.showMessage("Initializing Earth Engine, please wait warmly... ✨", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey")))
    app.processEvents()
    
    apply_theme_qt(APP_CONFIG.get('theme', DEFAULT_THEME_QT)) # Apply loaded or default theme

    ee_initialized_main = initialize_earth_engine_with_retry()

    if not ee_initialized_main:
        status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_ee_init_fail", "EE Init Failed."))
        start_button_qt.setEnabled(False) # Disable start if EE fails
        verify_button_qt.setEnabled(False) # Disable verify if EE fails
        if splash.isVisible(): splash.showMessage("EE Init Failed. Download/Verify features disabled.", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor("red"))
    else:
        status_bar_qt.showMessage(FLUTTERSHY_TEXTS.get("status_bar_ee_init_ok", "EE Connected! ✨"))
        # Only check for sample data if EE is initialized
        check_and_download_sample_data_on_startup() 
    
    app.processEvents() # Ensure splash messages from check_and_download_sample_data_on_startup are processed

    def on_main_window_close(event):
        update_and_save_app_config_qt() 
        if is_processing_qt and processing_thread_instance and processing_thread_instance.isRunning():
            reply = QtWidgets.QMessageBox.question(main_window, 'Confirm Exit', 
                                                   "Processing is ongoing. Are you sure you want to exit, sweetie?", 
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                                   QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                processing_thread_instance.request_cancel_thread()
                # Give a very short time for thread to acknowledge, then quit.
                # A more robust solution would be thread.wait(timeout), but can hang UI.
                QtCore.QTimer.singleShot(200, app.quit) 
                event.ignore() 
                return
            else:
                event.ignore()
                return
        if sample_download_thread_instance and sample_download_thread_instance.isRunning():
            logging.info("Sample download thread is still running. It will be terminated on exit.")
            # sample_download_thread_instance.request_cancel() # If it had cancel logic
            # sample_download_thread_instance.wait(1000) # Wait briefly
        event.accept()

    main_window.closeEvent = on_main_window_close

    help_menu_text = FLUTTERSHY_TEXTS.get("help_menu_text", "&Help")
    help_menu = menu_bar.addMenu(help_menu_text)
    
    about_action_text = FLUTTERSHY_TEXTS.get("about_menu_item_text", "&About Flutter Earth")
    about_action = QtWidgets.QAction(about_action_text, main_window)
    about_action.triggered.connect(show_about_dialog_qt)

    # Removed Application Guide menu item
    help_menu.addAction(about_action)
    
    main_window.showMaximized() 
    if splash.isVisible():
        splash.showMessage("Earth Engine ready! Loading interface... 🌸", Qt.AlignBottom | Qt.AlignHCenter, QtGui.QColor(FLUTTERSHY_TEXTS.get("TEXT_LIGHT", "grey"))) 
        splash.finish(main_window) 
    
    # Ensure the "Download Settings" tab (index 0) is active on startup
    if main_tab_widget:
        main_tab_widget.setCurrentIndex(0)
    update_main_layout_for_viewer_mode(post_processing_sub_tabs.currentIndex())
    sys.exit(app.exec_())
