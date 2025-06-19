"""GUI interface for Flutter Earth."""
import os
import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import folium
import json
import tempfile

from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .progress_tracker import ProgressTracker
from .utils import validate_bbox, validate_dates, get_sensor_details

class FlutterEarthGUI(QtWidgets.QMainWindow):
    """Main window for Flutter Earth application."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        earth_engine: EarthEngineManager,
        download_manager: DownloadManager,
        progress_tracker: ProgressTracker
    ):
        """Initialize the GUI.
        
        Args:
            config_manager: Configuration manager instance.
            earth_engine: Earth Engine manager instance.
            download_manager: Download manager instance.
            progress_tracker: Progress tracker instance.
        """
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config_manager = config_manager
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        
        # Set window properties
        self.setWindowTitle("Flutter Earth")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create UI elements
        self._create_ui()
        
        # Connect signals
        self._connect_signals()
        
        # Initialize map
        self._initialize_map()
    
    def _create_ui(self):
        """Create user interface elements."""
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Create left panel (controls)
        left_panel = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        
        # Add control groups
        left_layout.addWidget(self._create_area_group())
        left_layout.addWidget(self._create_date_group())
        left_layout.addWidget(self._create_sensor_group())
        left_layout.addWidget(self._create_output_group())
        left_layout.addWidget(self._create_processing_group())
        left_layout.addStretch()
        
        # Create right panel (map and progress)
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        # Add map view
        self.map_view = QtWebEngineWidgets.QWebEngineView()
        right_layout.addWidget(self.map_view)
        
        # Add progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(True)
        right_layout.addWidget(self.progress_bar)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
    
    def _create_area_group(self) -> QtWidgets.QGroupBox:
        """Create area selection group."""
        group = QtWidgets.QGroupBox("Area of Interest")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Add coordinate inputs
        coord_layout = QtWidgets.QGridLayout()
        
        self.west_input = QtWidgets.QLineEdit()
        self.east_input = QtWidgets.QLineEdit()
        self.north_input = QtWidgets.QLineEdit()
        self.south_input = QtWidgets.QLineEdit()
        
        coord_layout.addWidget(QtWidgets.QLabel("West:"), 0, 0)
        coord_layout.addWidget(self.west_input, 0, 1)
        coord_layout.addWidget(QtWidgets.QLabel("East:"), 0, 2)
        coord_layout.addWidget(self.east_input, 0, 3)
        coord_layout.addWidget(QtWidgets.QLabel("North:"), 1, 0)
        coord_layout.addWidget(self.north_input, 1, 1)
        coord_layout.addWidget(QtWidgets.QLabel("South:"), 1, 2)
        coord_layout.addWidget(self.south_input, 1, 3)
        
        layout.addLayout(coord_layout)
        
        # Add buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        draw_button = QtWidgets.QPushButton("Draw on Map")
        draw_button.clicked.connect(self._enable_map_drawing)
        button_layout.addWidget(draw_button)
        
        import_button = QtWidgets.QPushButton("Import Shapefile")
        import_button.clicked.connect(self._import_shapefile)
        button_layout.addWidget(import_button)
        
        layout.addLayout(button_layout)
        
        return group
    
    def _create_date_group(self) -> QtWidgets.QGroupBox:
        """Create date selection group."""
        group = QtWidgets.QGroupBox("Date Range")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Add date inputs
        self.start_date = QtWidgets.QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QtCore.QDate.currentDate().addMonths(-1))
        
        self.end_date = QtWidgets.QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QtCore.QDate.currentDate())
        
        date_layout = QtWidgets.QFormLayout()
        date_layout.addRow("Start Date:", self.start_date)
        date_layout.addRow("End Date:", self.end_date)
        
        layout.addLayout(date_layout)
        
        return group
    
    def _create_sensor_group(self) -> QtWidgets.QGroupBox:
        """Create sensor selection group."""
        group = QtWidgets.QGroupBox("Satellite Sensor")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Add sensor selection
        self.sensor_combo = QtWidgets.QComboBox()
        self.sensor_combo.addItems(['LANDSAT_9', 'SENTINEL_2'])
        
        layout.addWidget(self.sensor_combo)
        
        # Add cloud cover options
        self.cloud_mask_check = QtWidgets.QCheckBox("Apply Cloud Masking")
        layout.addWidget(self.cloud_mask_check)
        
        cloud_cover_layout = QtWidgets.QHBoxLayout()
        cloud_cover_layout.addWidget(QtWidgets.QLabel("Max Cloud Cover:"))
        
        self.cloud_cover_spin = QtWidgets.QSpinBox()
        self.cloud_cover_spin.setRange(0, 100)
        self.cloud_cover_spin.setValue(20)
        self.cloud_cover_spin.setSuffix("%")
        cloud_cover_layout.addWidget(self.cloud_cover_spin)
        
        layout.addLayout(cloud_cover_layout)
        
        return group
    
    def _create_output_group(self) -> QtWidgets.QGroupBox:
        """Create output options group."""
        group = QtWidgets.QGroupBox("Output Options")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Add output directory selection
        dir_layout = QtWidgets.QHBoxLayout()
        
        self.output_dir = QtWidgets.QLineEdit()
        self.output_dir.setText(os.path.expanduser("~/Downloads"))
        dir_layout.addWidget(self.output_dir)
        
        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.clicked.connect(self._browse_output_dir)
        dir_layout.addWidget(browse_button)
        
        layout.addLayout(dir_layout)
        
        return group
    
    def _create_processing_group(self) -> QtWidgets.QGroupBox:
        """Create processing options group."""
        group = QtWidgets.QGroupBox("Processing")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Add processing buttons
        start_button = QtWidgets.QPushButton("Start Processing")
        start_button.clicked.connect(self._start_processing)
        layout.addWidget(start_button)
        
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self._cancel_processing)
        layout.addWidget(cancel_button)
        
        return group
    
    def _connect_signals(self):
        """Connect signal handlers."""
        # Connect coordinate input validators
        for input_field in [self.west_input, self.east_input,
                          self.north_input, self.south_input]:
            input_field.textChanged.connect(self._validate_coordinates)
        
        # Connect date validators
        self.start_date.dateChanged.connect(self._validate_dates)
        self.end_date.dateChanged.connect(self._validate_dates)
    
    def _initialize_map(self):
        """Initialize the map view."""
        # Create map centered on US
        m = folium.Map(
            location=[39.8283, -98.5795],
            zoom_start=4,
            control_scale=True
        )
        
        # Save map to temporary file in a writable directory
        temp_dir = tempfile.gettempdir()
        temp_html = os.path.join(temp_dir, "flutter_earth_map.html")
        m.save(temp_html)
        
        # Load map in web view
        self.map_view.setUrl(QtCore.QUrl.fromLocalFile(temp_html))
    
    def _enable_map_drawing(self):
        """Enable drawing mode on map."""
        # TODO: Implement map drawing functionality
        self.logger.info("Map drawing not implemented yet")
    
    def _import_shapefile(self):
        """Import area from shapefile."""
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Shapefile",
            "",
            "Shapefiles (*.shp);;All Files (*)"
        )
        
        if file_name:
            try:
                # TODO: Implement shapefile import
                self.logger.info(f"Importing shapefile: {file_name}")
            except Exception as e:
                self.logger.error(f"Failed to import shapefile: {e}")
                QtWidgets.QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import shapefile: {str(e)}"
                )
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir.text()
        )
        
        if directory:
            self.output_dir.setText(directory)
    
    def _validate_coordinates(self):
        """Validate coordinate inputs."""
        try:
            west = float(self.west_input.text() or 0)
            east = float(self.east_input.text() or 0)
            north = float(self.north_input.text() or 0)
            south = float(self.south_input.text() or 0)
            
            if validate_bbox([west, south, east, north]):
                self._update_map_bounds([west, south, east, north])
            
        except ValueError:
            pass
    
    def _validate_dates(self):
        """Validate date inputs."""
        try:
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            
            validate_dates(start, end)
            
        except ValueError as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid Dates",
                str(e)
            )
    
    def _update_map_bounds(self, bbox: list):
        """Update map bounds."""
        # TODO: Implement map bounds update
        self.logger.info(f"Updating map bounds: {bbox}")
    
    def _start_processing(self):
        """Start processing with current parameters."""
        try:
            # Get parameters
            params = {
                'area_of_interest': [
                    float(self.west_input.text()),
                    float(self.south_input.text()),
                    float(self.east_input.text()),
                    float(self.north_input.text())
                ],
                'start_date': self.start_date.date().toPyDate(),
                'end_date': self.end_date.date().toPyDate(),
                'sensor_name': self.sensor_combo.currentText(),
                'output_dir': self.output_dir.text(),
                'cloud_mask': self.cloud_mask_check.isChecked(),
                'max_cloud_cover': self.cloud_cover_spin.value()
            }
            
            # Validate parameters
            self._validate_processing_params(params)
            
            # Start processing
            self.download_manager.process_request(params)
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            QtWidgets.QMessageBox.critical(
                self,
                "Processing Error",
                f"Failed to start processing: {str(e)}"
            )
    
    def _cancel_processing(self):
        """Cancel current processing operation."""
        self.download_manager.request_cancel()
    
    def _validate_processing_params(self, params: Dict[str, Any]) -> None:
        """Validate processing parameters."""
        # Validate area
        if not validate_bbox(params['area_of_interest']):
            raise ValueError("Invalid area of interest")
        
        # Validate dates
        validate_dates(params['start_date'], params['end_date'])
        
        # Validate sensor
        if not get_sensor_details(params['sensor_name']):
            raise ValueError(f"Invalid sensor: {params['sensor_name']}")
        
        # Validate output directory
        if not os.path.isdir(params['output_dir']):
            raise ValueError(f"Invalid output directory: {params['output_dir']}")
    
    def _update_progress(self, progress: Dict[str, Any]) -> None:
        """Update progress display.
        
        Args:
            progress: Progress information from tracker.
        """
        if progress['status'] == 'running':
            self.progress_bar.setValue(int(progress['progress'] * 100))
            self.progress_bar.setFormat(
                f"{progress['operation']}: "
                f"{progress['completed']}/{progress['total']} "
                f"({progress['elapsed_time']} elapsed, "
                f"{progress['estimated_time']} remaining)"
            )
        elif progress['status'] == 'completed':
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Processing completed")
        elif progress['status'] == 'failed':
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat(f"Processing failed: {progress['error']}")
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Ready") 