"""Advanced GUI interface for Flutter Earth."""
import os
import sys
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from PyQt6 import QtCore, QtWidgets, QtGui
import folium
import json
import tempfile
import time

from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .progress_tracker import ProgressTracker
from .utils import validate_bbox, validate_dates, get_sensor_details
from .themes import ThemeManager
from .satellite_info import SatelliteInfoManager, SATELLITE_DETAILS, SATELLITE_CATEGORIES
from .gui_components import (
    SatelliteInfoTab, SensorPriorityDialog, QtLogHandler,
    create_help_button, create_form_label_with_help,
    MapSelectionDialog, IndexAnalysisPane, VectorDownloadTab, DataViewerTab, ThemeSelectionDialog
)
from PyQt6.QtGui import QAction


class FlutterEarthGUI(QtWidgets.QMainWindow):
    """Advanced main window for Flutter Earth application."""
    
    def __init__(
        self,
        config_manager: ConfigManager,
        earth_engine: EarthEngineManager,
        download_manager: DownloadManager,
        progress_tracker: ProgressTracker
    ):
        """Initialize the advanced GUI.
        
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
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.satellite_manager = SatelliteInfoManager()
        
        # Set window properties
        self.setWindowTitle(self.theme_manager.get_text("window_title_main"))
        self.setGeometry(100, 100, 1400, 900)
        
        # Create UI elements
        self._create_ui()
        self._create_menu_bar()
        self._connect_signals()
        
        # Apply theme
        self._apply_theme()
        
        # Create toolbar
        self._create_toolbar()
        
        # Setup logging
        self._setup_logging()
    
    def _create_ui(self):
        """Create the advanced user interface."""
        # Create central widget and main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create main splitter
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel with tabs
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel with map and progress
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([600, 800])
        
        # Status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.theme_manager.get_text("status_bar_ready"))
    
    def _create_left_panel(self):
        """Create the left panel with tabs."""
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        left_layout.addWidget(self.tab_widget)
        
        # Add tabs
        self._create_download_tab()
        self._create_satellite_info_tab()
        self._create_post_processing_tab()
        
        return left_widget
    
    def _create_download_tab(self):
        """Create the main download settings tab."""
        download_widget = QtWidgets.QWidget()
        
        # Create scroll area for the download tab
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        
        # Area and time settings
        area_time_group = self._create_area_time_group()
        content_layout.addWidget(area_time_group)
        
        # Processing and sensor settings
        processing_group = self._create_processing_group()
        content_layout.addWidget(processing_group)
        
        # Output settings
        output_group = self._create_output_group()
        content_layout.addWidget(output_group)
        
        # Processing controls
        controls_group = self._create_controls_group()
        content_layout.addWidget(controls_group)
        
        # Log console
        log_group = self._create_log_group()
        content_layout.addWidget(log_group)
        
        content_layout.addStretch()
        
        # Set the content widget
        scroll_area.setWidget(content_widget)
        
        # Create main layout for download tab
        download_layout = QtWidgets.QVBoxLayout(download_widget)
        download_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(download_widget, "Download Settings")
    
    def _create_area_time_group(self):
        """Create area and time settings group."""
        group = QtWidgets.QGroupBox("Area & Time Settings")
        layout = QtWidgets.QFormLayout(group)
        
        # AOI input with help
        aoi_label = create_form_label_with_help(
            "AOI (BBOX or Polygon GeoJSON):",
            "Area of Interest Help",
            ("Enter or import coordinates for your Area of Interest (AOI):\n\n"
             "1. Manual Input:\n"
             "   - Rectangle (BBOX): 'minLon,minLat,maxLon,maxLat' (e.g., 35.2,30.5,35.8,32.0).\n"
             "   - Polygon (GeoJSON): A list of [longitude, latitude] pairs forming a closed shape.\n\n"
             "2. Interactive Selection:\n"
             "   - Use the '🗺️ Map' button to draw a new polygon/rectangle.\n"
             "   - Use the '📂 SHP' button to import an Esri Shapefile."),
            group
        )
        
        self.aoi_input = QtWidgets.QLineEdit()
        self.aoi_input.setPlaceholderText("e.g., 35.2,30.5,35.8,32.0 or [[35,31],[35.5,31],[35.5,31.5],[35,31.5],[35,31]]")
        
        aoi_layout = QtWidgets.QHBoxLayout()
        aoi_layout.addWidget(self.aoi_input)
        
        map_button = QtWidgets.QPushButton("🗺️ Map")
        map_button.clicked.connect(self._open_map_selection)
        aoi_layout.addWidget(map_button)
        
        shp_button = QtWidgets.QPushButton("📂 SHP")
        shp_button.clicked.connect(self._import_shapefile)
        aoi_layout.addWidget(shp_button)
        
        layout.addRow(aoi_label, aoi_layout)
        
        # Date inputs
        self.start_date = QtWidgets.QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QtCore.QDate.currentDate().addMonths(-1))
        
        self.end_date = QtWidgets.QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QtCore.QDate.currentDate())
        
        start_label = QtWidgets.QLabel(self.theme_manager.get_text("start_date_label"))
        end_label = QtWidgets.QLabel(self.theme_manager.get_text("end_date_label"))
        
        layout.addRow(start_label, self.start_date)
        layout.addRow(end_label, self.end_date)
        
        return group
    
    def _create_processing_group(self):
        """Create processing and sensor settings group."""
        group = QtWidgets.QGroupBox("Processing & Sensor Settings")
        layout = QtWidgets.QFormLayout(group)
        
        # Sensor priority with edit button
        sensor_priority_label = QtWidgets.QLabel(self.theme_manager.get_text("sensor_priority_label"))
        
        sensor_layout = QtWidgets.QHBoxLayout()
        self.sensor_priority_combo = QtWidgets.QComboBox()
        self.sensor_priority_combo.addItems(['LANDSAT_9', 'SENTINEL2', 'LANDSAT_8'])
        sensor_layout.addWidget(self.sensor_priority_combo)
        
        edit_priority_button = QtWidgets.QPushButton(self.theme_manager.get_text("sensor_priority_edit_button"))
        edit_priority_button.clicked.connect(self._open_sensor_priority_dialog)
        sensor_layout.addWidget(edit_priority_button)
        
        layout.addRow(sensor_priority_label, sensor_layout)
        
        # Cloud cover
        self.cloud_mask_check = QtWidgets.QCheckBox("Apply Cloud Masking")
        layout.addRow("", self.cloud_mask_check)
        
        cloud_cover_layout = QtWidgets.QHBoxLayout()
        cloud_cover_layout.addWidget(QtWidgets.QLabel("Max Cloud Cover:"))
        
        self.cloud_cover_spin = QtWidgets.QSpinBox()
        self.cloud_cover_spin.setRange(0, 100)
        self.cloud_cover_spin.setValue(20)
        self.cloud_cover_spin.setSuffix("%")
        cloud_cover_layout.addWidget(self.cloud_cover_spin)
        
        layout.addRow("", cloud_cover_layout)
        
        # Resolution settings
        self.use_best_resolution_check = QtWidgets.QCheckBox(self.theme_manager.get_text("use_highest_resolution_cb"))
        layout.addRow("", self.use_best_resolution_check)
        
        target_res_label = create_form_label_with_help(
            "Target Resolution (m):",
            "Target Resolution Help",
            self.theme_manager.get_text("target_resolution_manual_tooltip"),
            group
        )
        
        self.target_resolution_spin = QtWidgets.QSpinBox()
        self.target_resolution_spin.setRange(1, 1000)
        self.target_resolution_spin.setValue(30)
        self.target_resolution_spin.setSuffix(" m")
        layout.addRow(target_res_label, self.target_resolution_spin)
        
        # Tiling method
        self.tiling_method_combo = QtWidgets.QComboBox()
        self.tiling_method_combo.addItems(['degree', 'pixel'])
        layout.addRow("Tiling Method:", self.tiling_method_combo)
        
        # Number of subsections
        self.num_subsections_spin = QtWidgets.QSpinBox()
        self.num_subsections_spin.setRange(1, 1000)
        self.num_subsections_spin.setValue(100)
        layout.addRow("Number of Subsections:", self.num_subsections_spin)
        
        return group
    
    def _create_output_group(self):
        """Create output settings group."""
        group = QtWidgets.QGroupBox("Output Settings")
        layout = QtWidgets.QFormLayout(group)
        
        # Output directory
        output_dir_label = QtWidgets.QLabel(self.theme_manager.get_text("output_dir_label"))
        
        output_dir_layout = QtWidgets.QHBoxLayout()
        self.output_dir = QtWidgets.QLineEdit()
        self.output_dir.setText(os.path.expanduser("~/Downloads"))
        output_dir_layout.addWidget(self.output_dir)
        
        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.setObjectName("browseButton")
        browse_button.clicked.connect(self._browse_output_dir)
        output_dir_layout.addWidget(browse_button)
        
        layout.addRow(output_dir_label, output_dir_layout)
        
        # Overwrite option
        self.overwrite_check = QtWidgets.QCheckBox(self.theme_manager.get_text("overwrite_label"))
        layout.addRow("", self.overwrite_check)
        
        # Cleanup tiles option
        self.cleanup_tiles_check = QtWidgets.QCheckBox(self.theme_manager.get_text("cleanup_tiles_label"))
        self.cleanup_tiles_check.setChecked(True)
        layout.addRow("", self.cleanup_tiles_check)
        
        return group
    
    def _create_controls_group(self):
        """Create processing controls group."""
        group = QtWidgets.QGroupBox("Processing Controls")
        layout = QtWidgets.QVBoxLayout(group)
        
        # Progress bars
        overall_progress_label = QtWidgets.QLabel(self.theme_manager.get_text("overall_progress_label"))
        layout.addWidget(overall_progress_label)
        
        self.overall_progress_bar = QtWidgets.QProgressBar()
        self.overall_progress_bar.setObjectName("overallProgressBar")
        self.overall_progress_bar.setTextVisible(True)
        layout.addWidget(self.overall_progress_bar)
        
        monthly_progress_label = QtWidgets.QLabel(self.theme_manager.get_text("monthly_progress_label"))
        layout.addWidget(monthly_progress_label)
        
        self.monthly_progress_bar = QtWidgets.QProgressBar()
        self.monthly_progress_bar.setObjectName("monthlyProgressBar")
        self.monthly_progress_bar.setTextVisible(True)
        layout.addWidget(self.monthly_progress_bar)
        
        # Control buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.start_button = QtWidgets.QPushButton(self.theme_manager.get_text("run_button"))
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self._start_processing)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QtWidgets.QPushButton(self.theme_manager.get_text("cancel_button"))
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self._cancel_processing)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        self.verify_button = QtWidgets.QPushButton(self.theme_manager.get_text("verify_button_text_base"))
        self.verify_button.setObjectName("verifyButton")
        self.verify_button.clicked.connect(self._verify_satellites)
        button_layout.addWidget(self.verify_button)
        
        layout.addLayout(button_layout)
        
        return group
    
    def _create_log_group(self):
        """Create log console group."""
        group = QtWidgets.QGroupBox(self.theme_manager.get_text("log_console_label"))
        layout = QtWidgets.QVBoxLayout(group)
        
        self.log_console = QtWidgets.QTextEdit()
        self.log_console.setObjectName("logConsole")
        self.log_console.setMaximumHeight(150)
        layout.addWidget(self.log_console)
        
        return group
    
    def _create_satellite_info_tab(self):
        """Create the satellite information tab."""
        satellite_tab = SatelliteInfoTab(self.theme_manager)
        self.tab_widget.addTab(satellite_tab, "🛰️ Satellite Info")
    
    def _create_post_processing_tab(self):
        """Create the post-processing tab with sub-tabs."""
        post_processing_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(post_processing_widget)
        
        # Create sub-tab widget for post-processing features
        self.post_processing_sub_tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.post_processing_sub_tabs)
        
        # Add sub-tabs
        self._create_index_analysis_tab()
        self._create_vector_download_tab()
        self._create_data_viewer_tab()
        
        self.tab_widget.addTab(post_processing_widget, "📊 Post Processing")
    
    def _create_index_analysis_tab(self):
        """Create the index analysis sub-tab."""
        index_tab = IndexAnalysisPane(self.theme_manager, self)
        self.post_processing_sub_tabs.addTab(index_tab, "🌱 Index Analysis")
    
    def _create_vector_download_tab(self):
        """Create the vector download sub-tab."""
        vector_tab = VectorDownloadTab(self.theme_manager, self)
        self.post_processing_sub_tabs.addTab(vector_tab, "🗺️ Vector Download")
    
    def _create_data_viewer_tab(self):
        """Create the data viewer sub-tab."""
        viewer_tab = DataViewerTab(self.theme_manager, self)
        self.post_processing_sub_tabs.addTab(viewer_tab, "📊 Data Viewer")
    
    def _create_right_panel(self):
        """Create the right panel with map and additional tools."""
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        # Map selection button (instead of showing map directly)
        map_button = QtWidgets.QPushButton("🗺️ Open Map Selection")
        map_button.setObjectName("mapButton")
        map_button.clicked.connect(self._open_map_selection)
        right_layout.addWidget(map_button)
        
        # Add some spacing and placeholder for future tools
        right_layout.addStretch(1)
        
        # Placeholder for additional tools
        tools_label = QtWidgets.QLabel("Additional tools will appear here")
        tools_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        tools_label.setStyleSheet("color: gray; font-style: italic;")
        right_layout.addWidget(tools_label)
        
        right_layout.addStretch(1)
        return right_panel
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Import shapefile action
        import_action = QAction("📁 Import Shapefile", self)
        import_action.setStatusTip("Import shapefile for area of interest")
        import_action.triggered.connect(self._import_shapefile)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("🚪 Exit", self)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools 🛠️")
        
        # Satellite info action
        satellite_action = QAction("🛰️ Satellite Info", self)
        satellite_action.setStatusTip("View satellite information and capabilities")
        satellite_action.triggered.connect(self._show_satellite_info)
        tools_menu.addAction(satellite_action)
        
        # Post processing action
        post_processing_action = QAction("📊 Post Processing", self)
        post_processing_action.setStatusTip("Open post-processing tools")
        post_processing_action.triggered.connect(self._show_post_processing)
        tools_menu.addAction(post_processing_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("ℹ️ About Flutter Earth", self)
        about_action.setStatusTip("About Flutter Earth")
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
        
        # Application guide action
        guide_action = QAction("📖 Application Guide", self)
        guide_action.setStatusTip("Open application guide")
        guide_action.triggered.connect(self._show_application_guide)
        help_menu.addAction(guide_action)
        
        # Theme selection action
        theme_action = QAction("🎨 Select Theme...", self)
        theme_action.setStatusTip("Select application theme")
        theme_action.triggered.connect(self._show_theme_selection)
        help_menu.addAction(theme_action)

    def _create_toolbar(self):
        """Create the main toolbar with essential tools only."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # Theme selection button
        theme_action = QAction("🎨", self)
        theme_action.setToolTip("Select Theme")
        theme_action.triggered.connect(self._show_theme_selection)
        toolbar.addAction(theme_action)
        
        toolbar.addSeparator()
        
        # Satellite info button
        satellite_action = QAction("🛰️", self)
        satellite_action.setToolTip("Satellite Information")
        satellite_action.triggered.connect(self._show_satellite_info)
        toolbar.addAction(satellite_action)
        
        # Post processing button
        post_action = QAction("📊", self)
        post_action.setToolTip("Post Processing Tools")
        post_action.triggered.connect(self._show_post_processing)
        toolbar.addAction(post_action)
        
        toolbar.addSeparator()
        
        # About button
        about_action = QAction("ℹ️", self)
        about_action.setToolTip("About Flutter Earth")
        about_action.triggered.connect(self._show_about_dialog)
        toolbar.addAction(about_action)

    def _connect_signals(self):
        """Connect signal handlers."""
        # Connect coordinate input validators
        self.aoi_input.textChanged.connect(self._validate_aoi)
        
        # Connect date validators
        self.start_date.dateChanged.connect(self._validate_dates)
        self.end_date.dateChanged.connect(self._validate_dates)
        
        # Connect resolution toggle
        self.use_best_resolution_check.toggled.connect(self._on_best_resolution_toggle)
        
        # Connect tiling method change
        self.tiling_method_combo.currentTextChanged.connect(self._on_tiling_method_change)
        
        # Connect processing buttons
        self.start_button.clicked.connect(self._start_processing)
        self.cancel_button.clicked.connect(self._cancel_processing)
        self.verify_button.clicked.connect(self._verify_satellites)
        
        # Connect browse buttons
        self.output_dir.textChanged.connect(self._browse_output_dir)
        self.sensor_priority_combo.currentTextChanged.connect(self._open_sensor_priority_dialog)
    
    def _setup_logging(self):
        """Setup logging to the GUI console."""
        log_handler = QtLogHandler(self.log_console)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        root_logger.setLevel(logging.INFO)
    
    def _apply_theme(self):
        """Apply the current theme to the application."""
        self.setStyleSheet(self.theme_manager.get_stylesheet())
    
    def _open_theme_dialog(self):
        """Open the theme selection dialog."""
        dialog = ThemeSelectionDialog(self.theme_manager, self)
        dialog.theme_applied.connect(self._apply_theme_with_suboptions)
        dialog.exec_()

    def _apply_theme_with_suboptions(self, theme_name: str, suboptions: dict):
        """Apply theme with suboptions and save to config."""
        self.theme_manager.set_theme(theme_name, suboptions)
        self._apply_theme()
        
        # Save to config
        self.config_manager.set('theme', theme_name)
        self.config_manager.set('theme_suboptions', suboptions)
        self.config_manager.save_config()
        
        # Update status
        self.status_bar.showMessage(f"Theme changed to: {theme_name}")
    
    def _change_theme(self, theme_name: str):
        """Change the application theme (legacy method)."""
        self.theme_manager.set_theme(theme_name)
        self._apply_theme()
        
        # Save to config
        self.config_manager.set('theme', theme_name)
        self.config_manager.save_config()
    
    def _open_map_selection(self):
        """Open the map selection dialog."""
        dialog = MapSelectionDialog(self, self.aoi_input.text())
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_coords = dialog.get_selected_polygon_coords_str()
            if selected_coords:
                self.aoi_input.setText(selected_coords)
                self.status_bar.showMessage("Area of interest updated from map selection")
    
    def _import_shapefile(self):
        """Import shapefile for AOI."""
        try:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select Shapefile", "", "Shapefiles (*.shp);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Import shapefile library
            try:
                import shapefile
            except ImportError:
                QtWidgets.QMessageBox.warning(
                    self, "Missing Dependency", 
                    "PyShp library is required for shapefile import. Please install it with: pip install pyshp"
                )
                return
            
            # Read shapefile
            with shapefile.Reader(file_path) as sf:
                if len(sf.shapes()) == 0:
                    QtWidgets.QMessageBox.warning(self, "Empty Shapefile", "The selected shapefile contains no geometries.")
                    return
                
                # Get the first shape (could be extended to handle multiple shapes)
                shape = sf.shapes()[0]
                
                if shape.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM]:
                    # Convert to GeoJSON format
                    coords = []
                    for part in shape.parts:
                        part_coords = []
                        for i in range(part, len(shape.points) if part == shape.parts[-1] else shape.parts[shape.parts.index(part) + 1]):
                            point = shape.points[i]
                            part_coords.append([point[0], point[1]])
                        coords.append(part_coords)
                    
                    # Convert to JSON string
                    aoi_json = json.dumps(coords)
                    self.aoi_input.setText(aoi_json)
                    self.status_bar.showMessage(f"Imported shapefile: {os.path.basename(file_path)}")
                    
                else:
                    QtWidgets.QMessageBox.warning(
                        self, "Unsupported Geometry", 
                        f"Shapefile contains {shape.shapeType} geometry. Only polygon geometries are supported."
                    )
                    
        except Exception as e:
            self.logger.error(f"Error importing shapefile: {e}")
            QtWidgets.QMessageBox.critical(self, "Import Error", f"Failed to import shapefile:\n{e}")
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.output_dir.text()
        )
        if dir_path:
            self.output_dir.setText(dir_path)
    
    def _open_sensor_priority_dialog(self):
        """Open the sensor priority dialog."""
        current_priority = [self.sensor_priority_combo.itemText(i) 
                          for i in range(self.sensor_priority_combo.count())]
        all_sensors = self.satellite_manager.get_available_sensors()
        
        dialog = SensorPriorityDialog(self, current_priority, all_sensors, self.theme_manager)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_priority = dialog.get_updated_priority_list()
            # Update the combo box
            self.sensor_priority_combo.clear()
            self.sensor_priority_combo.addItems(new_priority)
    
    def _validate_aoi(self):
        """Validate the AOI input."""
        aoi_text = self.aoi_input.text().strip()
        if not aoi_text:
            return
        
        try:
            # Try to parse as bbox
            if ',' in aoi_text:
                coords = [float(x.strip()) for x in aoi_text.split(',')]
                if len(coords) == 4:
                    validate_bbox(coords)
                    return
            
            # Try to parse as GeoJSON
            coords = json.loads(aoi_text)
            if isinstance(coords, list) and len(coords) > 2:
                # Validate polygon coordinates
                return
            
        except (ValueError, json.JSONDecodeError):
            self.status_bar.showMessage(
                self.theme_manager.get_text("status_bar_input_error_prefix") + "Invalid AOI format"
            )
    
    def _validate_dates(self):
        """Validate the date range."""
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        if start_date > end_date:
            self.status_bar.showMessage(
                self.theme_manager.get_text("status_bar_input_error_prefix") + "Start date must be before end date"
            )
    
    def _on_best_resolution_toggle(self, checked: bool):
        """Handle best resolution toggle."""
        self.target_resolution_spin.setEnabled(not checked)
        if checked:
            self.target_resolution_spin.setToolTip(self.theme_manager.get_text("target_resolution_auto_tooltip"))
        else:
            self.target_resolution_spin.setToolTip(self.theme_manager.get_text("target_resolution_manual_tooltip"))
    
    def _on_tiling_method_change(self, method: str):
        """Handle tiling method change."""
        if method == 'degree':
            self.num_subsections_spin.setSuffix(" tiles")
        else:
            self.num_subsections_spin.setSuffix(" pixels")
    
    def _start_processing(self):
        """Start the processing."""
        try:
            # Validate inputs
            if not self._validate_inputs():
                return
            
            # Get processing parameters
            params = self._get_processing_params()
            
            # Create tile definitions
            tiles_list = self._create_tile_definitions(params)
            
            # Start processing thread
            from .processing import ProcessingThread
            self.processing_thread = ProcessingThread(
                params=params,
                tiles_list=tiles_list,
                is_polygon_aoi=self._is_polygon_aoi(),
                earth_engine=self.earth_engine,
                download_manager=self.download_manager
            )
            
            # Connect signals
            self.processing_thread.status_update.connect(self._update_status)
            self.processing_thread.overall_progress_update.connect(self._update_overall_progress)
            self.processing_thread.tile_progress_update.connect(self._update_tile_progress)
            self.processing_thread.processing_finished_signal.connect(self._on_processing_finished)
            
            # Start processing
            self.processing_thread.start()
            
            # Update UI state
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.status_bar.showMessage("Processing started...")
            
        except Exception as e:
            self.logger.error(f"Error starting processing: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Processing Error", f"Failed to start processing:\n{e}")
    
    def _cancel_processing(self):
        """Cancel the current processing."""
        if hasattr(self, 'processing_thread') and self.processing_thread.isRunning():
            self.processing_thread.request_cancel()
            self.status_bar.showMessage("Cancelling processing...")
    
    def _verify_satellites(self):
        """Verify satellite data availability."""
        try:
            # Get AOI coordinates
            aoi_coords = self._get_aoi_coordinates()
            if not aoi_coords:
                QtWidgets.QMessageBox.warning(self, "Invalid AOI", "Please enter a valid Area of Interest.")
                return
            
            # Start verification thread
            from .processing import VerificationThread
            self.verification_thread = VerificationThread(
                aoi_coords=aoi_coords,
                is_aoi_polygon=self._is_polygon_aoi(),
                earth_engine=self.earth_engine
            )
            
            # Connect signals
            self.verification_thread.status_update.connect(self._update_status)
            self.verification_thread.verification_finished.connect(self._on_verification_finished)
            
            # Start verification
            self.verification_thread.start()
            self.status_bar.showMessage("Verifying satellite data...")
            
        except Exception as e:
            self.logger.error(f"Error starting verification: {e}", exc_info=True)
            QtWidgets.QMessageBox.critical(self, "Verification Error", f"Failed to start verification:\n{e}")
    
    def _validate_inputs(self) -> bool:
        """Validate all input fields."""
        # Validate AOI
        if not self.aoi_input.text().strip():
            QtWidgets.QMessageBox.warning(self, "Missing Input", "Please enter an Area of Interest.")
            return False
        
        # Validate dates
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        if start_date > end_date:
            QtWidgets.QMessageBox.warning(self, "Invalid Dates", "Start date must be before end date.")
            return False
        
        # Validate output directory
        if not self.output_dir.text().strip():
            QtWidgets.QMessageBox.warning(self, "Missing Input", "Please select an output directory.")
            return False
        
        return True
    
    def _get_processing_params(self):
        """Get processing parameters from UI."""
        from .types import ProcessingParams
        
        return ProcessingParams(
            area_of_interest=self.aoi_input.text().strip(),
            start_date=self.start_date.date().toPyDate(),
            end_date=self.end_date.date().toPyDate(),
            output_dir=self.output_dir.text().strip(),
            sensor_name=self.sensor_priority_combo.currentText(),
            target_resolution=self.target_resolution_spin.value(),
            use_best_resolution=self.use_best_resolution_check.isChecked(),
            tiling_method=self.tiling_method_combo.currentText(),
            num_subsections=self.num_subsections_spin.value(),
            overwrite_existing=self.overwrite_check.isChecked()
        )
    
    def _create_tile_definitions(self, params):
        """Create tile definitions based on parameters."""
        from .types import TileDefinition
        from .utils import calculate_tiles
        
        # Get AOI coordinates
        aoi_coords = self._get_aoi_coordinates()
        if not aoi_coords:
            raise ValueError("Invalid AOI coordinates")
        
        # Calculate tiles based on tiling method
        if params.get('tiling_method') == 'degree':
            # Use degree-based tiling
            tile_size = self.config_manager.get('tile_size', 1.0)
            tiles = calculate_tiles(aoi_coords, tile_size)
        else:
            # Use pixel-based tiling
            num_subsections = params.get('num_subsections', 100)
            # Calculate tile size based on AOI area and number of subsections
            if self._is_polygon_aoi():
                # For polygon, use bounding box
                bbox = self._get_bbox_from_polygon(aoi_coords)
            else:
                bbox = aoi_coords
            
            # Calculate tile dimensions
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            area = width * height
            tile_area = area / num_subsections
            tile_size = (tile_area ** 0.5) / 2  # Approximate square tiles
            
            tiles = calculate_tiles(bbox, tile_size)
        
        # Convert to TileDefinition objects
        tile_definitions = []
        for i, tile in enumerate(tiles):
            tile_def = TileDefinition(
                bbox=tile['bbox'],
                index=i,
                output_path=os.path.join(
                    params.get('output_dir', ''),
                    f"tile_{i:04d}.tif"
                )
            )
            tile_definitions.append(tile_def)
        
        return tile_definitions
    
    def _get_aoi_coordinates(self):
        """Get AOI coordinates from input."""
        aoi_text = self.aoi_input.text().strip()
        if not aoi_text:
            return None
        
        try:
            # Try to parse as bbox
            if ',' in aoi_text:
                coords = [float(x.strip()) for x in aoi_text.split(',')]
                if len(coords) == 4:
                    return coords
            
            # Try to parse as GeoJSON
            coords = json.loads(aoi_text)
            if isinstance(coords, list) and len(coords) > 2:
                return coords
            
        except (ValueError, json.JSONDecodeError):
            pass
        
        return None
    
    def _is_polygon_aoi(self) -> bool:
        """Check if AOI is polygon coordinates."""
        aoi_coords = self._get_aoi_coordinates()
        if not aoi_coords:
            return False
        
        # If it's a list of lists, it's likely polygon coordinates
        return isinstance(aoi_coords[0], list)
    
    def _update_status(self, message: str):
        """Update status message."""
        self.status_bar.showMessage(message)
        self.log_console.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def _update_overall_progress(self, current: int, total: int):
        """Update overall progress bar."""
        if hasattr(self, 'overall_progress_bar'):
            progress = (current / total) * 100 if total > 0 else 0
            self.overall_progress_bar.setValue(int(progress))
            self.overall_progress_bar.setFormat(f"Overall: {current}/{total} ({progress:.1f}%)")
    
    def _update_tile_progress(self, current: int, total: int):
        """Update tile progress bar."""
        if hasattr(self, 'tile_progress_bar'):
            progress = (current / total) * 100 if total > 0 else 0
            self.tile_progress_bar.setValue(int(progress))
            self.tile_progress_bar.setFormat(f"Tile: {current}/{total} ({progress:.1f}%)")
    
    def _on_processing_finished(self, message: str):
        """Handle processing finished."""
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_bar.showMessage(message)
        
        if "error" in message.lower() or "failed" in message.lower():
            QtWidgets.QMessageBox.warning(self, "Processing Result", message)
        else:
            self.bridge.showMessage.emit('info', 'Processing Complete', message)
    
    def _on_verification_finished(self, results: list, message: str):
        """Handle verification finished."""
        self.status_bar.showMessage(message)
        
        if results:
            # Show results in a dialog
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Satellite Data Verification Results")
            dialog.setModal(True)
            
            layout = QtWidgets.QVBoxLayout(dialog)
            
            # Create results table
            table = QtWidgets.QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Sensor", "Available", "Coverage"])
            table.setRowCount(len(results))
            
            for i, result in enumerate(results):
                table.setItem(i, 0, QtWidgets.QTableWidgetItem(result.get("sensor", "")))
                table.setItem(i, 1, QtWidgets.QTableWidgetItem("Yes" if result.get("available", False) else "No"))
                table.setItem(i, 2, QtWidgets.QTableWidgetItem(result.get("coverage", "")))
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # Close button
            close_button = QtWidgets.QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.exec_()
        else:
            QtWidgets.QMessageBox.warning(self, "Verification Result", message)
    
    def _show_satellite_info(self):
        """Show satellite information dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("🛰️ Satellite Information")
        msg.setText("Satellite information and capabilities")
        msg.setInformativeText("This feature will show detailed information about available satellites and their specifications.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def _show_post_processing(self):
        """Show post-processing tools dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("📊 Post Processing Tools")
        msg.setText("Post-processing tools")
        msg.setInformativeText("This feature will provide tools for calculating vegetation indices and other derived products.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def _show_application_guide(self):
        """Show application guide dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("📖 Application Guide")
        msg.setText("Flutter Earth Application Guide")
        msg.setInformativeText("This feature will provide a comprehensive guide to using Flutter Earth for satellite data download and processing.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    def _show_about_dialog(self):
        """Show the about dialog with theme-specific information."""
        about_info = self.theme_manager.get_about_info()
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(about_info["title"])
        dialog.setModal(True)
        dialog.resize(600, 500)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Title and subtitle
        title_label = QtWidgets.QLabel(about_info["title"])
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QtWidgets.QLabel(about_info["subtitle"])
        subtitle_label.setStyleSheet("font-size: 12pt; color: gray; margin-bottom: 20px;")
        subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Description
        description_text = QtWidgets.QTextEdit()
        description_text.setHtml(about_info["description"])
        description_text.setReadOnly(True)
        description_text.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(description_text)
        
        # Splash chime info
        chime_label = QtWidgets.QLabel(f"🎵 Splash Sound: {self.theme_manager.get_splash_chime()}")
        chime_label.setStyleSheet("font-style: italic; color: gray; margin-top: 10px;")
        chime_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(chime_label)
        
        # Close button
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def _show_theme_selection(self):
        """Show the theme selection dialog."""
        from .gui_components import ThemeSelectionDialog
        dialog = ThemeSelectionDialog(self, self.theme_manager)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self._apply_theme()

    def _get_bbox_from_polygon(self, polygon_coords):
        """Get bounding box from polygon coordinates."""
        if not polygon_coords or len(polygon_coords) == 0:
            return None
        
        # Handle nested polygon structure
        if isinstance(polygon_coords[0][0], list):
            # Multi-polygon or polygon with holes
            all_points = []
            for part in polygon_coords:
                all_points.extend(part)
        else:
            # Simple polygon
            all_points = polygon_coords
        
        if len(all_points) < 3:
            return None
        
        # Calculate bounding box
        lons = [p[0] for p in all_points]
        lats = [p[1] for p in all_points]
        
        return [min(lons), min(lats), max(lons), max(lats)] 