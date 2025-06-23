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

from PySide6.QtCore import QObject, Slot, QUrl, Signal, QVariant
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

    def __init__(self, config_manager: ConfigManager, earth_engine: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        self.satellite_manager = SatelliteInfoManager()
    
    @Slot(result=bool)
    def isGeeInitialized(self):
        return self.earth_engine.initialized

    @Slot(result='QVariantList')
    def getSensorPriority(self):
        return self.config_manager.get('sensor_priority', [])

    @Slot('QVariantList')
    def setSensorPriority(self, priority_list):
        self.config_manager.set('sensor_priority', list(priority_list))
        self.sensorPriorityChanged.emit()

    @Slot(result='QVariantList')
    def getAllSensors(self):
        return self.satellite_manager.get_available_sensors()

    @Slot(result='QVariantMap')
    def getAvailableIndices(self):
        return self.satellite_manager.get_available_indices()
    
    @Slot(result='QVariantMap')
    def getCurrentThemeColors(self):
        return self.config_manager.get_current_theme_colors()

    @Slot(result=str)
    def getCurrentThemeName(self):
        return self.config_manager.get('theme', 'Default (Dark)')

    @Slot(result='QVariantList')
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

class QmlGUILauncher(QObject):
    """
    Manages the setup and execution of the QML application.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine()

        # Setup backend managers
        self.config_manager = ConfigManager()
        self.progress_tracker = ProgressTracker()
        self.download_manager = DownloadManager(self.progress_tracker)
        self.earth_engine = EarthEngineManager(self.config_manager)
        
        self.backend = AppBackend(
            config_manager=self.config_manager,
            earth_engine=self.earth_engine,
            download_manager=self.download_manager,
            progress_tracker=self.progress_tracker
        )

    def _prepare_satellite_data(self) -> QVariant:
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
        return QVariant(processed_data)

    def launch(self):
        """
        Loads the QML file, exposes the backend, and runs the application.
        """
        # First, ensure Earth Engine can be initialized.
        if not self.backend.earth_engine.initialize():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Earth Engine Initialization Failed")
            msg_box.setInformativeText(
                "Could not initialize the Google Earth Engine API.\n\n"
                "The application will open, but features requiring GEE will be disabled."
            )
            msg_box.setWindowTitle("GEE Initialization Warning")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        # Expose Python objects to the QML context
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("satelliteData", self._prepare_satellite_data())

        # Build the path to the main QML file
        qml_file = Path(__file__).parent / "qml" / "main.qml"
        
        # Load the QML file
        self.engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not self.engine.rootObjects():
            sys.exit(-1)
            
        sys.exit(self.app.exec()) 