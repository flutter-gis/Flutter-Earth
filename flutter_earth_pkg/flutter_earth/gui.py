"""
QML Application Host for Flutter Earth using PySide6.

This file is responsible for setting up the QQmlApplicationEngine,
loading the main QML file, and exposing the Python-based application
backend to the QML frontend.
"""
import os
import sys
from pathlib import Path
import tempfile
import folium
import shutil
import glob

from PySide6.QtCore import QObject, Slot, QUrl, Signal
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineWidgets import QWebEngineView 
from PySide6.QtWebEngineCore import QWebEnginePage

# Import backend managers
from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .progress_tracker import ProgressTracker
from .satellite_info import SatelliteInfoManager, SATELLITE_DETAILS, SATELLITE_CATEGORIES
from .themes import ThemeManager # Import ThemeManager

class AppBackend(QObject):
    """
    The backend object that will be exposed to QML.
    It provides the business logic and data access for the UI.
    """
    sensorPriorityChanged = Signal()
    themeChanged = Signal(str, dict) # Emits theme name and full theme data dict
    downloadErrorOccurred = Signal(str, str)  # user_message, log_message
    downloadProgressUpdated = Signal(int, int)  # current, total
    sampleDownloadProgressUpdated = Signal(str, int, int)  # sample_key, current, total
    configChanged = Signal(dict)  # Emitted when config is changed or reloaded (QML)
    settingChanged = Signal(str, object)  # Emitted when a single setting is changed (QML)
    auth_missing = Signal()  # Signal when authentication is missing

    def __init__(self, config_manager: ConfigManager, earth_engine: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        self.satellite_manager = SatelliteInfoManager()
        self.theme_manager = ThemeManager() # Instantiate ThemeManager

        # Connect error signals for user feedback
        self.download_manager.error_occurred.connect(self.onDownloadError)
        self.download_manager.progress_update.connect(self.onDownloadProgress)

        # Settings signals for QML
        self.config_manager.config_changed.connect(self.configChanged.emit)
        self.config_manager.settingChanged.connect(self.settingChanged.emit)

        # Theme signal
        self.theme_manager.theme_changed.connect(self.onThemeManagerThemeChanged)


        # If you have a sample_manager, connect its progress here (pseudo-code):
        # self.sample_manager.sample_download_progress.connect(self.onSampleDownloadProgress)

    @Slot(str, dict)
    def onThemeManagerThemeChanged(self, theme_name: str, theme_data: dict):
        """Relay ThemeManager's theme_changed signal to QML."""
        self.themeChanged.emit(theme_name, theme_data)
    
    @Slot(result=bool)
    def isGeeInitialized(self):
        return self.earth_engine.initialized

    @Slot(result=list)
    def getSensorPriority(self):
        return self.config_manager.get('sensor_priority', [])

    @Slot(list)
    def setSensorPriority(self, priority_list):
        self.config_manager.set('sensor_priority', list(priority_list))
        self.sensorPriorityChanged.emit()

    @Slot(result=list)
    def getAllSensors(self):
        """Get all available sensors for download."""
        return [
            "LANDSAT_8", "LANDSAT_9", "SENTINEL_2", "SENTINEL_1", 
            "MODIS", "VIIRS", "CBERS_4", "CBERS_4A"
        ]

    @Slot(result=list)
    def getAvailableIndices(self):
        """Get list of available vegetation indices."""
        return [
            {
                "name": "NDVI",
                "full_name": "Normalized Difference Vegetation Index",
                "formula": "(NIR - Red) / (NIR + Red)",
                "description": "Measures vegetation health and density",
                "range": "0 to 1",
                "bands_required": ["Red", "NIR"]
            },
            {
                "name": "EVI",
                "full_name": "Enhanced Vegetation Index",
                "formula": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)",
                "description": "Enhanced version of NDVI with atmospheric correction",
                "range": "0 to 1",
                "bands_required": ["Red", "NIR", "Blue"]
            },
            {
                "name": "SAVI",
                "full_name": "Soil Adjusted Vegetation Index",
                "formula": "1.5 * (NIR - Red) / (NIR + Red + 0.5)",
                "description": "NDVI adjusted for soil background",
                "range": "0 to 1",
                "bands_required": ["Red", "NIR"]
            },
            {
                "name": "NDWI",
                "full_name": "Normalized Difference Water Index",
                "formula": "(Green - NIR) / (Green + NIR)",
                "description": "Measures water content in vegetation",
                "range": "-1 to 1",
                "bands_required": ["Green", "NIR"]
            },
            {
                "name": "NDMI",
                "full_name": "Normalized Difference Moisture Index",
                "formula": "(NIR - SWIR1) / (NIR + SWIR1)",
                "description": "Measures vegetation moisture content",
                "range": "-1 to 1",
                "bands_required": ["NIR", "SWIR1"]
            },
            {
                "name": "NBR",
                "full_name": "Normalized Burn Ratio",
                "formula": "(NIR - SWIR2) / (NIR + SWIR2)",
                "description": "Measures burn severity and vegetation stress",
                "range": "-1 to 1",
                "bands_required": ["NIR", "SWIR2"]
            },
            {
                "name": "NDSI",
                "full_name": "Normalized Difference Snow Index",
                "formula": "(Green - SWIR1) / (Green + SWIR1)",
                "description": "Detects snow and ice",
                "range": "-1 to 1",
                "bands_required": ["Green", "SWIR1"]
            },
            {
                "name": "NDBI",
                "full_name": "Normalized Difference Built-up Index",
                "formula": "(SWIR1 - NIR) / (SWIR1 + NIR)",
                "description": "Detects built-up areas and urban development",
                "range": "-1 to 1",
                "bands_required": ["NIR", "SWIR1"]
            }
        ]

    @Slot(result=dict)
    def getCurrentThemeColors(self): # Still returns only colors for direct use, QML can use full data
        return self.config_manager.get_current_theme_colors()

    @Slot(result=dict)
    def getCurrentThemeData(self):
        """Get current theme data."""
        theme_data = self.theme_manager.get_current_theme_data()
        print(f"[DEBUG] AppBackend.getCurrentThemeData: {theme_data}")
        if not isinstance(theme_data, dict):
            print("[ERROR] getCurrentThemeData did not return a dict!")
            return {}
        return theme_data

    @Slot(result=str)
    def getCurrentThemeName(self):
        return self.theme_manager.current_theme_name()

    @Slot(result=list)
    def getAvailableThemes(self):
        """Get list of available themes from ThemeManager."""
        themes = self.theme_manager.get_available_themes_meta()
        print(f"[DEBUG] AppBackend.getAvailableThemes: {themes}")
        if not isinstance(themes, list):
            print("[ERROR] getAvailableThemes did not return a list!")
            return []
        return themes

    @Slot(str, result=bool)
    def setTheme(self, theme_name: str):
        """Set the current theme."""
        try:
            self.theme_manager.set_current_theme(theme_name)
            return True
        except Exception as e:
            print(f"Error setting theme: {e}")
            return False

    @Slot(result=dict)
    def getThemeOptions(self):
        """Get theme configuration options."""
        return {
            "use_character_catchphrases": True,
            "enable_animations": True,
            "show_tooltips": True,
            "font_size_adjustment": 0,
            "color_blind_friendly": False
        }

    @Slot(str, object)
    def setSetting(self, key, value):
        """Set a single setting value by key."""
        print(f"[DEBUG] setSetting called with key={key}, value={value}")
        
        # Handle individual theme suboption settings
        theme_suboption_keys = ["use_character_catchphrases", "show_special_icons", "enable_animated_background"]
        if key in theme_suboption_keys:
            # Convert string boolean to actual boolean if needed
            if isinstance(value, str):
                value = value.lower() == "true"
            
            # Get current theme suboptions
            current_suboptions = self.config_manager.get("theme_suboptions", {})
            if isinstance(current_suboptions, str):
                import json
                try:
                    current_suboptions = json.loads(current_suboptions)
                except (json.JSONDecodeError, TypeError):
                    current_suboptions = {}
            
            # Update the specific suboption
            current_suboptions[key] = value
            
            # Save the updated suboptions
            self.config_manager.set("theme_suboptions", current_suboptions)
            
            # Update theme manager
            self.theme_manager.set_suboptions(current_suboptions)
            self.themeChanged.emit(self.theme_manager.current_theme_name(), self.theme_manager.get_current_theme_data())
            return
        
        # Handle regular settings
        self.config_manager.set(key, value)
        if key == "theme_suboptions":
            print(f"[DEBUG] Updating theme suboptions in ThemeManager: {value}")
            # Parse JSON string if needed
            if isinstance(value, str):
                import json
                try:
                    suboptions_dict = json.loads(value)
                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to parse theme_suboptions JSON: {value}")
                    return
            else:
                suboptions_dict = value
            self.theme_manager.set_suboptions(suboptions_dict)
            self.themeChanged.emit(self.theme_manager.current_theme_name(), self.theme_manager.get_current_theme_data())

    @Slot(result=QUrl)
    def getMapUrl(self):
        """
        Generates a basic folium map and returns the URL to its temporary file.
        This provides a simple, interactive map view within the QML UI.
        """
        m = folium.Map(location=[45.5236, -122.6750], zoom_start=4)
        
        # Save to a temporary file
        # Note: delete=False is important, as the file must exist for the web view to load it.
        # The OS will handle cleanup of the temp directory.
        temp_file = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
        m.save(temp_file.name)
        
        return QUrl.fromLocalFile(temp_file.name)

    @Slot(dict)
    def startDownloadWithParams(self, params: dict):
        """
        Start a download with parameters from the QML frontend.
        Expected keys in params:
        - area_of_interest (list or str that can be parsed to list)
        - start_date (str, e.g., "YYYY-MM-DD")
        - end_date (str, e.g., "YYYY-MM-DD")
        - sensor_name (str)
        - output_dir (str)
        - cloud_mask (bool)
        - max_cloud_cover (float/int)
        """
        print(f"Received download request with params: {params}")

        if not self.earth_engine.initialized:
            print("Earth Engine not initialized. Cannot start download.")
            self.downloadErrorOccurred.emit("Earth Engine Not Initialized",
                                            "GEE must be authenticated and initialized to start downloads.")
            return

        # Basic validation and parsing (can be expanded)
        try:
            aoi_raw = params.get('area_of_interest')
            if isinstance(aoi_raw, str):
                # Attempt to parse from string if it's like "lon,lat,lon,lat" or JSON list
                if '[' in aoi_raw: # Likely JSON
                    import json
                    aoi = json.loads(aoi_raw)
                else: # Assuming comma separated lon,lat,lon,lat
                    aoi = [float(x.strip()) for x in aoi_raw.split(',')]
                params['area_of_interest'] = aoi
            elif not isinstance(aoi_raw, list):
                raise ValueError("Area of Interest (AOI) must be a list or a parseable string.")

            # Ensure other critical params exist (more validation can be added)
            required_keys = ['start_date', 'end_date', 'sensor_name', 'output_dir']
            for key in required_keys:
                if key not in params:
                    raise ValueError(f"Missing required parameter: {key}")

            # Ensure numeric types for relevant fields
            if 'max_cloud_cover' in params:
                params['max_cloud_cover'] = float(params['max_cloud_cover'])

        except Exception as e:
            error_msg = f"Invalid parameters for download: {e}"
            print(f"[ERROR] {error_msg}")
            self.downloadErrorOccurred.emit("Invalid Download Parameters", str(e))
            return

        print("Starting download processing with validated params:", params)
        # TODO: Consider running process_request in a separate thread if it's blocking
        # and can't be handled by the DownloadManager's internal threading.
        # For now, assuming DownloadManager handles threading appropriately.
        result = self.download_manager.process_request(params)

        if result and result.get("status") == "error":
            print(f"Download processing reported an error: {result.get('message')}")
            self.downloadErrorOccurred.emit("Download Error", result.get('message', "Unknown error during processing."))
        elif result:
            print(f"Download processing initiated/completed: {result}")
            # Success/progress messages should ideally come from DownloadManager signals
        else:
            print("Download processing did not return a conclusive result.")
            # self.downloadErrorOccurred.emit("Download Error", "Processing did not start or failed silently.")


    @Slot()
    def cancelDownload(self):
        """Cancel the current download."""
        print("Cancelling download...")
        self.download_manager.request_cancel()

    @Slot(result=float)
    def getProgress(self):
        """Return the current progress as a float (0.0–1.0) for QML progress bar."""
        progress_info = self.progress_tracker.get_progress()
        return float(progress_info.get('progress', 0.0))

    @Slot(str, str)
    def onDownloadError(self, user_message, log_message):
        print(f"[Download Error] {user_message}\nDetails: {log_message}")
        self.downloadErrorOccurred.emit(user_message, log_message)

    @Slot(int, int)
    def onDownloadProgress(self, current, total):
        self.downloadProgressUpdated.emit(current, total)

    @Slot(str, int, int)
    def onSampleDownloadProgress(self, sample_key, current, total):
        self.sampleDownloadProgressUpdated.emit(sample_key, current, total)

    @Slot()
    def clearCacheAndLogs(self):
        """Delete all files in the cache and logs directories."""
        deleted_files = 0
        
        # Get the project root directory (where main.py is located)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Define directories to clean up
        directories_to_clean = [
            os.path.join(project_root, 'logs'),
            os.path.join(project_root, 'flutter_earth_downloads'),
            os.path.join(os.getcwd(), 'logs'),
            os.path.join(os.getcwd(), 'flutter_earth_downloads')
        ]
        
        for directory in directories_to_clean:
            if os.path.exists(directory):
                try:
                    print(f"[Cleanup] Cleaning directory: {directory}")
                    for item in glob.glob(os.path.join(directory, '*')):
                        try:
                            if os.path.isfile(item):
                                os.remove(item)
                                deleted_files += 1
                                print(f"[Cleanup] Deleted file: {item}")
                            elif os.path.isdir(item):
                                shutil.rmtree(item)
                                deleted_files += 1
                                print(f"[Cleanup] Deleted directory: {item}")
                        except Exception as e:
                            print(f"[Cleanup Error] Could not delete {item}: {e}")
                except Exception as e:
                    print(f"[Cleanup Error] Could not access directory {directory}: {e}")
            else:
                print(f"[Cleanup] Directory does not exist: {directory}")
        
        print(f"[Cleanup] Deleted {deleted_files} files/folders from cache and logs.")

    @Slot()
    def reloadConfig(self):
        """Reload configuration from file and emit config_changed signal."""
        self.config_manager.reload_config()

    @Slot(str, result=object)
    def getSetting(self, key):
        """Get a single setting value by key."""
        return self.config_manager.get(key)

    @Slot(result=dict)
    def getAllSettings(self):
        """Get the full settings/config as a dict."""
        settings = self.config_manager.getAllSettings()
        print(f"[DEBUG] AppBackend.getAllSettings: {settings}")
        if not isinstance(settings, dict):
            print("[ERROR] getAllSettings did not return a dict!")
            return {}
        return settings

    # --- Index Analysis Methods ---
    @Slot(list, str, str, dict, result=bool)
    def startIndexAnalysis(self, input_files, output_dir, index_type, band_map):
        """Start index analysis on raster files."""
        try:
            from .processing import batch_index_analysis
            results = batch_index_analysis(input_files, output_dir, index_type, band_map)
            success_count = sum(1 for r in results if r['success'])
            if success_count > 0:
                print(f"Index analysis completed: {success_count}/{len(results)} files processed successfully")
                return True
            else:
                print("Index analysis failed for all files")
                return False
        except Exception as e:
            print(f"Index analysis error: {e}")
            return False

    # --- Vector Download Methods ---
    @Slot(list, str, str, str, result=bool)
    def startVectorDownload(self, aoi, query, output_path, output_format):
        """Start vector data download from Overpass API."""
        try:
            from .vector_download import download_vector_data
            success = download_vector_data(aoi, query, output_path, output_format)
            if success:
                print(f"Vector download completed: {output_path}")
            else:
                print("Vector download failed")
            return success
        except Exception as e:
            print(f"Vector download error: {e}")
            return False

    @Slot(result=list)
    def getVectorDataSources(self):
        """Get available vector data sources."""
        return [
            {"name": "Overpass API (OSM)", "description": "OpenStreetMap data via Overpass API"},
            {"name": "WFS", "description": "Web Feature Service"},
            {"name": "GeoJSON URL", "description": "Direct GeoJSON file URL"}
        ]

    @Slot(result=list)
    def getVectorOutputFormats(self):
        """Get available vector output formats."""
        return ["GeoJSON", "Shapefile", "KML"]

    # --- Data Viewer Methods ---
    @Slot(str, result=dict)
    def loadRasterData(self, file_path):
        """Load raster data for viewing."""
        try:
            # Placeholder implementation - would integrate with actual raster loading
            return {
                "success": True,
                "file_path": file_path,
                "file_size": "1.2 GB",
                "dimensions": [5120, 5120],
                "bands": [
                    {"name": "Blue", "min": 0, "max": 255, "mean": 127},
                    {"name": "Green", "min": 0, "max": 255, "mean": 127},
                    {"name": "Red", "min": 0, "max": 255, "mean": 127},
                    {"name": "NIR", "min": 0, "max": 255, "mean": 127}
                ],
                "projection": "EPSG:4326",
                "extent": [-180, -90, 180, 90]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @Slot(str, result=dict)
    def loadVectorData(self, file_path):
        """Load vector data for viewing."""
        try:
            # Placeholder implementation - would integrate with actual vector loading
            return {
                "success": True,
                "file_path": file_path,
                "file_size": "45 MB",
                "geometry_type": "Polygon",
                "feature_count": 1250,
                "attributes": [
                    {"name": "id", "type": "Integer"},
                    {"name": "name", "type": "String"},
                    {"name": "area", "type": "Float"},
                    {"name": "population", "type": "Integer"}
                ],
                "extent": [-122.5, 37.5, -122.0, 38.0]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @Slot(str, result=list)
    def getDataPreview(self, file_path):
        """Get preview data for a file."""
        try:
            # Placeholder implementation
            return [
                {"id": 1, "name": "Sample Feature 1", "area": 125.5, "population": 1000},
                {"id": 2, "name": "Sample Feature 2", "area": 89.2, "population": 750},
                {"id": 3, "name": "Sample Feature 3", "area": 234.1, "population": 1500},
                {"id": 4, "name": "Sample Feature 4", "area": 67.8, "population": 500},
                {"id": 5, "name": "Sample Feature 5", "area": 156.3, "population": 1200}
            ]
        except Exception as e:
            return []

    @Slot(str, result=dict)
    def getDataStatistics(self, file_path):
        """Get statistical information about the data."""
        try:
            # Placeholder implementation
            return {
                "summary": {
                    "total_features": 1250,
                    "valid_features": 1245,
                    "null_features": 5
                },
                "attributes": {
                    "area": {
                        "min": 0.1,
                        "max": 5000.0,
                        "mean": 245.6,
                        "std": 125.3,
                        "median": 180.2
                    },
                    "population": {
                        "min": 0,
                        "max": 50000,
                        "mean": 2500.5,
                        "std": 3500.2,
                        "median": 1200.0
                    }
                }
            }
        except Exception as e:
            return {"error": str(e)}

    # --- Map Integration Methods ---
    @Slot(list)
    def setAOIFromMap(self, coordinates):
        """Set Area of Interest from map selection."""
        self.config_manager.set('area_of_interest', coordinates)
        print(f"AOI set from map: {coordinates}")

    @Slot(result=list)
    def getCurrentAOI(self):
        """Get current Area of Interest."""
        return self.config_manager.get('area_of_interest', [])

    # --- Progress and History Methods ---
    @Slot(result=str)
    def getDownloadStatus(self):
        """Get current download status."""
        progress_info = self.progress_tracker.get_progress()
        return progress_info.get('status', 'idle')

    @Slot(result=list)
    def getDownloadHistory(self):
        """Get download history."""
        return self.progress_tracker.get_history()

    @Slot()
    def clearDownloadHistory(self):
        """Clear download history."""
        self.progress_tracker.clear_history()

    # --- Satellite Information Methods ---
    @Slot(result=dict)
    def getSatelliteCategories(self):
        """Get satellite categories and their sensors."""
        return {
            "Landsat": [
                {"id": "LANDSAT_8", "type": "Optical", "resolution": 30},
                {"id": "LANDSAT_9", "type": "Optical", "resolution": 30}
            ],
            "Sentinel": [
                {"id": "SENTINEL_2", "type": "Optical", "resolution": 10},
                {"id": "SENTINEL_1", "type": "Radar", "resolution": 5}
            ],
            "MODIS": [
                {"id": "MODIS", "type": "Optical", "resolution": 250}
            ],
            "VIIRS": [
                {"id": "VIIRS", "type": "Optical", "resolution": 375}
            ]
        }

    @Slot(str, result=dict)
    def getSatelliteDetails(self, sensor_name):
        """Get detailed information about a specific satellite sensor."""
        details = {
            "LANDSAT_8": {
                "name": "Landsat 8",
                "type": "Optical",
                "resolution": 30,
                "bands": ["Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2", "TIR1", "TIR2"],
                "coverage": "Global",
                "launch_date": "2013-02-11",
                "status": "Active",
                "band_info": [
                    {"name": "Blue", "wavelength": 452, "resolution": 30},
                    {"name": "Green", "wavelength": 512, "resolution": 30},
                    {"name": "Red", "wavelength": 671, "resolution": 30},
                    {"name": "NIR", "wavelength": 864, "resolution": 30},
                    {"name": "SWIR1", "wavelength": 1610, "resolution": 30},
                    {"name": "SWIR2", "wavelength": 2200, "resolution": 30}
                ],
                "applications": "Land cover mapping, vegetation monitoring, urban planning, agriculture"
            },
            "LANDSAT_9": {
                "name": "Landsat 9",
                "type": "Optical",
                "resolution": 30,
                "bands": ["Blue", "Green", "Red", "NIR", "SWIR1", "SWIR2", "TIR1", "TIR2"],
                "coverage": "Global",
                "launch_date": "2021-09-27",
                "status": "Active",
                "band_info": [
                    {"name": "Blue", "wavelength": 452, "resolution": 30},
                    {"name": "Green", "wavelength": 512, "resolution": 30},
                    {"name": "Red", "wavelength": 671, "resolution": 30},
                    {"name": "NIR", "wavelength": 864, "resolution": 30},
                    {"name": "SWIR1", "wavelength": 1610, "resolution": 30},
                    {"name": "SWIR2", "wavelength": 2200, "resolution": 30}
                ],
                "applications": "Land cover mapping, vegetation monitoring, urban planning, agriculture"
            },
            "SENTINEL_2": {
                "name": "Sentinel-2",
                "type": "Optical",
                "resolution": 10,
                "bands": ["Blue", "Green", "Red", "Red Edge", "NIR", "SWIR1", "SWIR2"],
                "coverage": "Global",
                "launch_date": "2015-06-23",
                "status": "Active",
                "band_info": [
                    {"name": "Blue", "wavelength": 490, "resolution": 10},
                    {"name": "Green", "wavelength": 560, "resolution": 10},
                    {"name": "Red", "wavelength": 665, "resolution": 10},
                    {"name": "NIR", "wavelength": 842, "resolution": 10},
                    {"name": "SWIR1", "wavelength": 1610, "resolution": 20},
                    {"name": "SWIR2", "wavelength": 2190, "resolution": 20}
                ],
                "applications": "High-resolution land monitoring, precision agriculture, forestry"
            },
            "SENTINEL_1": {
                "name": "Sentinel-1",
                "type": "Radar",
                "resolution": 5,
                "bands": ["C-Band"],
                "coverage": "Global",
                "launch_date": "2014-04-03",
                "status": "Active",
                "band_info": [
                    {"name": "C-Band", "wavelength": 5600, "resolution": 5}
                ],
                "applications": "All-weather monitoring, disaster management, maritime surveillance"
            },
            "MODIS": {
                "name": "MODIS",
                "type": "Optical",
                "resolution": 250,
                "bands": ["Red", "NIR", "Blue", "Green", "SWIR1", "SWIR2"],
                "coverage": "Global",
                "launch_date": "1999-12-18",
                "status": "Active",
                "band_info": [
                    {"name": "Red", "wavelength": 645, "resolution": 250},
                    {"name": "NIR", "wavelength": 858, "resolution": 250},
                    {"name": "Blue", "wavelength": 469, "resolution": 500},
                    {"name": "Green", "wavelength": 555, "resolution": 500},
                    {"name": "SWIR1", "wavelength": 1240, "resolution": 500},
                    {"name": "SWIR2", "wavelength": 1640, "resolution": 500}
                ],
                "applications": "Global monitoring, climate studies, large-scale vegetation analysis"
            },
            "VIIRS": {
                "name": "VIIRS",
                "type": "Optical",
                "resolution": 375,
                "bands": ["Red", "NIR", "Blue", "Green", "SWIR1", "SWIR2"],
                "coverage": "Global",
                "launch_date": "2011-10-28",
                "status": "Active",
                "band_info": [
                    {"name": "Red", "wavelength": 640, "resolution": 375},
                    {"name": "NIR", "wavelength": 865, "resolution": 375},
                    {"name": "Blue", "wavelength": 445, "resolution": 750},
                    {"name": "Green", "wavelength": 555, "resolution": 750},
                    {"name": "SWIR1", "wavelength": 1240, "resolution": 750},
                    {"name": "SWIR2", "wavelength": 1610, "resolution": 750}
                ],
                "applications": "Environmental monitoring, disaster response, climate research"
            }
        }
        return details.get(sensor_name, {})

    @Slot(str, str, str, result=dict)
    def calculateIndex(self, index_name, image_path, output_path):
        """Calculate a specific vegetation index for an image.
        
        Args:
            index_name: Name of the index to calculate
            image_path: Path to the input image
            output_path: Path for the output image
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # This would integrate with actual Earth Engine processing
            # For now, return a placeholder response
            return {
                "success": True,
                "message": f"Index {index_name} calculated successfully",
                "output_path": output_path,
                "statistics": {
                    "min": 0.1,
                    "max": 0.9,
                    "mean": 0.45,
                    "std": 0.15
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error calculating index: {str(e)}",
                "output_path": None,
                "statistics": None
            }

    @Slot(str, result=list)
    def getIndexStatistics(self, image_path):
        """Get statistics for an index image.
        
        Args:
            image_path: Path to the index image
            
        Returns:
            List of statistical measures
        """
        # Placeholder implementation
        return [
            {"name": "Minimum", "value": 0.1},
            {"name": "Maximum", "value": 0.9},
            {"name": "Mean", "value": 0.45},
            {"name": "Standard Deviation", "value": 0.15},
            {"name": "Median", "value": 0.43},
            {"name": "25th Percentile", "value": 0.32},
            {"name": "75th Percentile", "value": 0.58}
        ]

    # --- Utility Methods ---
    @Slot(str, result=bool)
    def validateCoordinates(self, coord_string):
        """Validate coordinate string format."""
        try:
            import json
            coords = json.loads(coord_string)
            if isinstance(coords, list) and len(coords) == 4:
                return all(isinstance(x, (int, float)) for x in coords)
            return False
        except:
            return False

    @Slot(str, result=bool)
    def validateDate(self, date_string):
        """Validate date string format."""
        try:
            from datetime import datetime
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except:
            return False

    @Slot(str, str)
    def setAuthCredentials(self, key_file, project_id):
        from .auth_setup import AuthManager
        auth_manager = AuthManager()
        auth_manager.save_credentials(project_id, key_file)
        print(f"[DEBUG] Credentials saved: {key_file}, {project_id}")
        # Optionally, re-initialize Earth Engine here

class QmlGUILauncher(QObject):
    """
    Manages the setup and execution of the QML application.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # QApplication is now created in main.py, do not create it here
        self.engine = QQmlApplicationEngine()

        # Setup backend managers
        self.config_manager = ConfigManager()
        self.progress_tracker = ProgressTracker()
        self.download_manager = DownloadManager()
        self.earth_engine = EarthEngineManager()
        self.backend = AppBackend(
            config_manager=self.config_manager,
            earth_engine=self.earth_engine,
            download_manager=self.download_manager,
            progress_tracker=self.progress_tracker
        )

    def _prepare_satellite_data(self):
        """Prepares the satellite data for the QML frontend."""
        processed_data = []
        categories = self.backend.satellite_manager.get_satellite_categories()
        for category_name, sensor_list in categories.items():
            category_obj = {"name": category_name, "sensors": []}
            for sensor_key in sensor_list:
                details = SATELLITE_DETAILS.get(sensor_key, {}).copy()
                details['id'] = sensor_key
                category_obj["sensors"].append(details)
            processed_data.append(category_obj)
        return processed_data

    def launch(self):
        """
        Loads the QML file, exposes the backend, and runs the application.
        """
        gee_initialized = self.backend.earth_engine.initialize(parent=None)
        if not gee_initialized:
            # Emit signal from backend to trigger auth dialog
            self.backend.auth_missing.emit()
        # Expose Python objects to the QML context
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("satelliteData", self._prepare_satellite_data())
        # Build the path to the main QML file
        qml_file = Path(__file__).parent / "qml" / "main.qml"
        print("[DEBUG] Loading QML file:", qml_file)
        # Load the QML file
        self.engine.load(QUrl.fromLocalFile(str(qml_file)))
        print("[DEBUG] Loaded QML, root objects:", self.engine.rootObjects())
        if not self.engine.rootObjects():
            print("[ERROR] Failed to load QML. Check for errors in the QML file or its path.")
            return  # Do not exit, just return
        QApplication.instance().exec() 

# Add slot to AppBackend to receive credentials from QML
def add_auth_slot_to_appbackend():
    def setAuthCredentials(self, key_file, project_id):
        from .auth_setup import AuthManager
        auth_manager = AuthManager()
        auth_manager.save_credentials(project_id, key_file)
        print(f"[DEBUG] Credentials saved: {key_file}, {project_id}")
        # Optionally, re-initialize Earth Engine here
    AppBackend.setAuthCredentials = Slot(str, str)(setAuthCredentials)
add_auth_slot_to_appbackend() 