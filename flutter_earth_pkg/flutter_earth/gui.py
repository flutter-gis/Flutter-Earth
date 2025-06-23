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

class AppBackend(QObject):
    """
    The backend object that will be exposed to QML.
    It provides the business logic and data access for the UI.
    """
    sensorPriorityChanged = Signal()
    themeChanged = Signal()
    downloadErrorOccurred = Signal(str, str)  # user_message, log_message
    downloadProgressUpdated = Signal(int, int)  # current, total
    sampleDownloadProgressUpdated = Signal(str, int, int)  # sample_key, current, total
    configChanged = Signal(dict)  # Emitted when config is changed or reloaded (QML)
    settingChanged = Signal(str, object)  # Emitted when a single setting is changed (QML)

    def __init__(self, config_manager: ConfigManager, earth_engine: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        self.satellite_manager = SatelliteInfoManager()
        # Connect error signals for user feedback
        self.download_manager.error_occurred.connect(self.onDownloadError)
        self.download_manager.progress_update.connect(self.onDownloadProgress)
        # Settings signals for QML
        self.config_manager.config_changed.connect(self.configChanged.emit)
        self.config_manager.settingChanged.connect(self.settingChanged.emit)
        # If you have a sample_manager, connect its progress here (pseudo-code):
        # self.sample_manager.sample_download_progress.connect(self.onSampleDownloadProgress)
    
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
        return self.satellite_manager.get_available_sensors()

    @Slot(result=dict)
    def getAvailableIndices(self):
        return self.satellite_manager.get_available_indices()
    
    @Slot(result=dict)
    def getCurrentThemeColors(self):
        return self.config_manager.get_current_theme_colors()

    @Slot(result=str)
    def getCurrentThemeName(self):
        return self.config_manager.get('theme', 'Default (Dark)')

    @Slot(result=list)
    def getAvailableThemes(self):
        return self.config_manager.get_available_themes()

    @Slot(str)
    def setTheme(self, theme_name: str):
        if theme_name in self.getAvailableThemes():
            self.config_manager.set('theme', theme_name)
            self.themeChanged.emit()
            print(f"Theme changed to: {theme_name}")

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

    @Slot()
    def startDownload(self):
        """Start a download with dummy parameters (to be replaced with real UI input)."""
        # Dummy parameters for demonstration
        params = {
            'area_of_interest': [0, 0, 1, 1],
            'start_date': '2022-01-01',
            'end_date': '2022-01-31',
            'sensor_name': 'LANDSAT_9',
            'output_dir': 'flutter_earth_downloads',
            'cloud_mask': True,
            'max_cloud_cover': 20.0
        }
        if not self.earth_engine.initialized:
            print("Earth Engine not initialized. Cannot start download.")
            return
        print("Starting download with params:", params)
        result = self.download_manager.process_request(params)
        print("Download result:", result)

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
        for d in [os.path.join(os.getcwd(), 'flutter_earth_downloads'), os.path.join(os.getcwd(), 'logs')]:
            if os.path.exists(d):
                for f in glob.glob(os.path.join(d, '*')):
                    try:
                        if os.path.isfile(f):
                            os.remove(f)
                            deleted_files += 1
                        elif os.path.isdir(f):
                            shutil.rmtree(f)
                            deleted_files += 1
                    except Exception as e:
                        print(f"[Cleanup Error] Could not delete {f}: {e}")
        print(f"[Cleanup] Deleted {deleted_files} files/folders from cache and logs.")

    @Slot()
    def reloadConfig(self):
        """Reload configuration from file and emit config_changed signal."""
        self.config_manager.reload_config()

    @Slot(str, result=object)
    def getSetting(self, key):
        """Get a single setting value by key."""
        return self.config_manager.get(key)

    @Slot(str, object)
    def setSetting(self, key, value):
        """Set a single setting value by key."""
        self.config_manager.set(key, value)

    @Slot(result=dict)
    def getAllSettings(self):
        """Get the full settings/config as a dict."""
        return self.config_manager.to_dict()

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
        # First, ensure Earth Engine can be initialized.
        gee_initialized = self.backend.earth_engine.initialize(parent=None)
        if not gee_initialized:
            # Try to show the auth dialog and allow skipping
            from .auth_setup import AuthManager
            auth_manager = AuthManager()
            credentials = auth_manager.setup_credentials(parent=None)
            if credentials:
                # Try initializing again with new credentials
                gee_initialized = self.backend.earth_engine.initialize(parent=None)
            if not gee_initialized:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setText("Earth Engine Authentication Not Set")
                msg_box.setInformativeText(
                    "Google Earth Engine authentication was not completed.\n\n"
                    "You can continue using the app, but GEE features will be disabled."
                )
                msg_box.setWindowTitle("GEE Authentication Skipped")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.exec()
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