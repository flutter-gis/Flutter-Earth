"""Advanced GUI interface for Flutter Earth."""
import os
import sys
import logging
from typing import Optional, Dict, Any, List
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
from .themes import ThemeManager
from .satellite_info import SatelliteInfoManager, SATELLITE_DETAILS, SATELLITE_CATEGORIES
from .gui_components import (
    SatelliteInfoTab, SensorPriorityDialog, QtLogHandler,
    create_help_button, create_form_label_with_help
)


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
        
        # Initialize map
        self._initialize_map()
        
        # Setup logging
        self._setup_logging()
    
    def _create_ui(self):
        """Create the advanced user interface."""
        # Create central widget and main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create main splitter
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
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
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
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
        """Create the post-processing tab."""
        post_processing_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(post_processing_widget)
        
        # Placeholder for post-processing features
        placeholder = QtWidgets.QLabel("Post-processing features coming soon...")
        placeholder.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        self.tab_widget.addTab(post_processing_widget, "📊 Post Processing")
    
    def _create_right_panel(self):
        """Create the right panel with map and additional info."""
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        
        # Map view
        self.map_view = QtWebEngineWidgets.QWebEngineView()
        right_layout.addWidget(self.map_view)
        
        return right_widget
    
    def _create_menu_bar(self):
        """Create the menu bar with themes and tools."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Tools menu
        tools_menu = menu_bar.addMenu(self.theme_manager.get_text("tools_menu_label"))
        
        satellite_info_action = QtWidgets.QAction(self.theme_manager.get_text("satellite_info_action_label"), self)
        satellite_info_action.triggered.connect(self._show_satellite_info)
        tools_menu.addAction(satellite_info_action)
        
        post_processing_action = QtWidgets.QAction(self.theme_manager.get_text("post_processing_action_label"), self)
        post_processing_action.triggered.connect(self._show_post_processing)
        tools_menu.addAction(post_processing_action)
        
        # Themes menu
        themes_menu = menu_bar.addMenu(self.theme_manager.get_text("themes_menu_text"))
        
        for theme_name in self.theme_manager.get_available_themes():
            theme_action = QtWidgets.QAction(theme_name, self)
            theme_action.setCheckable(True)
            theme_action.setChecked(theme_name == self.theme_manager.theme_name)
            theme_action.triggered.connect(lambda checked, name=theme_name: self._change_theme(name))
            themes_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menu_bar.addMenu(self.theme_manager.get_text("help_menu_text"))
        
        about_action = QtWidgets.QAction(self.theme_manager.get_text("about_menu_item_text"), self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
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
    
    def _change_theme(self, theme_name: str):
        """Change the application theme."""
        self.theme_manager.set_theme(theme_name)
        self._apply_theme()
        
        # Update theme menu checked state
        for action in self.menuBar().actions():
            if action.text() == self.theme_manager.get_text("themes_menu_text"):
                for theme_action in action.menu().actions():
                    theme_action.setChecked(theme_action.text() == theme_name)
                break
    
    def _initialize_map(self):
        """Initialize the map view."""
        # Create map centered on US
        m = folium.Map(
            location=[39.8283, -98.5795],
            zoom_start=4,
            control_scale=True
        )
        
        # Save map to temporary file
        temp_dir = tempfile.gettempdir()
        temp_html = os.path.join(temp_dir, "flutter_earth_map.html")
        m.save(temp_html)
        
        # Load map in web view
        self.map_view.setUrl(QtCore.QUrl.fromLocalFile(temp_html))
    
    def _open_map_selection(self):
        """Open the map selection dialog."""
        # TODO: Implement map selection dialog
        self.logger.info("Map selection dialog not implemented yet")
    
    def _import_shapefile(self):
        """Import shapefile for AOI."""
        # TODO: Implement shapefile import
        self.logger.info("Shapefile import not implemented yet")
    
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
        # TODO: Implement processing logic
        self.logger.info("Processing started")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.status_bar.showMessage(self.theme_manager.get_text("status_bar_processing_started"))
    
    def _cancel_processing(self):
        """Cancel the processing."""
        # TODO: Implement cancellation logic
        self.logger.info("Processing cancelled")
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_bar.showMessage(self.theme_manager.get_text("status_bar_cancellation_requested"))
    
    def _verify_satellites(self):
        """Verify satellite availability."""
        # TODO: Implement satellite verification
        self.logger.info("Satellite verification started")
        self.status_bar.showMessage("Verifying satellite availability...")
    
    def _show_satellite_info(self):
        """Show satellite information tab."""
        self.tab_widget.setCurrentIndex(1)  # Switch to satellite info tab
    
    def _show_post_processing(self):
        """Show post-processing tab."""
        self.tab_widget.setCurrentIndex(2)  # Switch to post-processing tab
    
    def _show_about_dialog(self):
        """Show about dialog."""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle(self.theme_manager.get_text("about_dialog_title"))
        msg.setText(self.theme_manager.get_text("about_dialog_tagline"))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_() 