"""Advanced GUI components for Flutter Earth."""
import os
import logging
from typing import List, Dict, Any, Optional
from PyQt6 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import json
import tempfile
import folium
import numpy

from .themes import ThemeManager, DEFAULT_THEME
from .satellite_info import SatelliteInfoManager, SATELLITE_DETAILS, SATELLITE_CATEGORIES


class SatelliteInfoTab(QtWidgets.QWidget):
    """Tab for displaying satellite information in a tree structure."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        """Initialize the satellite info tab."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.satellite_manager = SatelliteInfoManager()
        self.init_ui()
        self.populate_satellite_tree()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QHBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        
        # Left pane: Satellite Tree
        self.satellite_tree = QtWidgets.QTreeWidget()
        self.satellite_tree.setHeaderLabels(["Satellites & Categories"])
        self.satellite_tree.currentItemChanged.connect(self.display_satellite_info)
        self.splitter.addWidget(self.satellite_tree)
        
        # Right pane: Details Display
        self.details_display = QtWidgets.QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setAcceptRichText(True)  # Allow HTML for formatting
        self.splitter.addWidget(self.details_display)
        
        self.splitter.setSizes([250, 550])  # Initial sizes for panes
        layout.addWidget(self.splitter)
        self.setLayout(layout)
    
    def populate_satellite_tree(self):
        """Populate the satellite tree with categories and sensors."""
        self.satellite_tree.clear()
        for category, sensor_list in SATELLITE_CATEGORIES.items():
            category_item = QtWidgets.QTreeWidgetItem(self.satellite_tree, [category])
            category_item.setFlags(category_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)
            for sensor_key in sensor_list:
                if sensor_key in SATELLITE_DETAILS:
                    sensor_display_name = f"{sensor_key} ({SATELLITE_DETAILS[sensor_key].get('type', 'N/A')})"
                    sensor_item = QtWidgets.QTreeWidgetItem(category_item, [sensor_display_name])
                    sensor_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, sensor_key)
        self.satellite_tree.expandAll()
    
    def display_satellite_info(self, current_item, previous_item):
        """Display detailed information for the selected satellite."""
        if not current_item:
            self.details_display.clear()
            return
        
        sensor_key = current_item.data(0, QtCore.Qt.ItemDataRole.UserRole)
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
        else:
            self.details_display.setHtml(
                f"<p>Select a satellite from the list to view its details.</p>"
                f"<p><i>Category: {current_item.text(0)}</i></p>"
            )
    
    def apply_styles(self):
        """Apply themed styles to the components."""
        colors = self.theme_manager.colors
        self.satellite_tree.setStyleSheet(
            f"QTreeWidget {{ border: 1px solid {colors['ACCENT_BORDER']}; "
            f"background-color: {colors['INPUT_BG']}; color: {colors['INPUT_FG']}; }} "
            f"QHeaderView::section {{ background-color: {colors['BUTTON_LAVENDER_BG']}; "
            f"color: {colors['TEXT_COLOR']}; padding: 4px; border: none; }}"
        )
        self.details_display.setStyleSheet(
            f"QTextEdit {{ border: 1px solid {colors['ACCENT_BORDER']}; "
            f"background-color: {colors['INPUT_BG']}; color: {colors['INPUT_FG']}; padding: 5px; }}"
        )
    
    def update_theme(self, theme_manager: ThemeManager):
        """Update the theme for this component."""
        self.theme_manager = theme_manager
        self.apply_styles()


class SensorPriorityDialog(QtWidgets.QDialog):
    """Dialog for editing sensor priority order."""
    
    def __init__(self, parent, current_priority_list: List[str], 
                 all_sensor_names_list: List[str], theme_manager: ThemeManager):
        """Initialize the sensor priority dialog."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_priority_list = list(current_priority_list)
        self.all_sensor_names = sorted(list(all_sensor_names_list))
        self.new_priority_list = None
        
        self.setWindowTitle(self.theme_manager.get_text("sensor_priority_dialog_title"))
        self.setMinimumSize(400, 500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Instruction label
        instruction_label = QtWidgets.QLabel(self.theme_manager.get_text("sensor_priority_instruction"))
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Table widget
        self.table_widget = QtWidgets.QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Order", "Sensor"])
        self.table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setStyleSheet(self._get_table_stylesheet())
        
        # Populate table
        for sensor_name in self.current_priority_list:
            if sensor_name in self.all_sensor_names:
                row_position = self.table_widget.rowCount()
                self.table_widget.insertRow(row_position)
                order_item = QtWidgets.QTableWidgetItem(str(row_position + 1))
                order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                sensor_item = QtWidgets.QTableWidgetItem(sensor_name)
                sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_position, 0, order_item)
                self.table_widget.setItem(row_position, 1, sensor_item)
        
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setVisible(False)
        layout.addWidget(self.table_widget, 1)
        
        # Button layout
        button_layout = QtWidgets.QHBoxLayout()
        self.up_button = QtWidgets.QPushButton(self.theme_manager.get_text("sensor_priority_up_button"))
        self.down_button = QtWidgets.QPushButton(self.theme_manager.get_text("sensor_priority_down_button"))
        self.add_button = QtWidgets.QPushButton(self.theme_manager.get_text("sensor_priority_add_button"))
        self.remove_button = QtWidgets.QPushButton(self.theme_manager.get_text("sensor_priority_remove_button"))
        
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.add_button.clicked.connect(self.add_sensor)
        self.remove_button.clicked.connect(self.remove_sensor)
        
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)
        
        # Dialog buttons
        self.dialog_buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.dialog_buttons.accepted.connect(self.accept_changes)
        self.dialog_buttons.rejected.connect(self.reject)
        
        # Style buttons
        colors = self.theme_manager.colors
        self.dialog_buttons.button(QtWidgets.QDialogButtonBox.Ok).setStyleSheet(
            f"background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']}; "
            f"font-weight: bold; padding: 5px 15px;"
        )
        self.dialog_buttons.button(QtWidgets.QDialogButtonBox.Cancel).setStyleSheet(
            f"background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']}; "
            f"padding: 5px 15px;"
        )
        
        layout.addWidget(self.dialog_buttons)
        self.setLayout(layout)
        self._renumber_order_column()
    
    def _get_table_stylesheet(self):
        """Get stylesheet for the table."""
        colors = self.theme_manager.colors
        return f"""
            QTableWidget {{
                background-color: {colors['INPUT_BG']}; color: {colors['INPUT_FG']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 5px;
                font-size: 11pt; gridline-color: {colors['ACCENT_BORDER']};
            }}
            QTableWidget::item {{ padding: 6px; }}
            QTableWidget::item:selected {{
                background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']};
            }}
            QHeaderView::section {{
                background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']};
                padding: 4px; border: 1px solid {colors['ACCENT_BORDER']};
                font-size: 11pt; font-weight: bold;
            }}"""
    
    def _renumber_order_column(self):
        """Renumber the order column after changes."""
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)
            if item:
                item.setText(str(row + 1))
            else:
                new_item = QtWidgets.QTableWidgetItem(str(row + 1))
                new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row, 0, new_item)
    
    def move_up(self):
        """Move selected row up."""
        current_row = self.table_widget.currentRow()
        if current_row > 0:
            sensor_item_text = self.table_widget.item(current_row, 1).text()
            self.table_widget.removeRow(current_row)
            self.table_widget.insertRow(current_row - 1)
            
            new_order_item = QtWidgets.QTableWidgetItem(str(current_row))
            new_order_item.setFlags(new_order_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            new_sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
            new_sensor_item.setFlags(new_sensor_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            
            self.table_widget.setItem(current_row - 1, 0, new_order_item)
            self.table_widget.setItem(current_row - 1, 1, new_sensor_item)
            self.table_widget.setCurrentRow(current_row - 1)
            self._renumber_order_column()
    
    def move_down(self):
        """Move selected row down."""
        current_row = self.table_widget.currentRow()
        if current_row < self.table_widget.rowCount() - 1:
            sensor_item_text = self.table_widget.item(current_row, 1).text()
            self.table_widget.removeRow(current_row)
            self.table_widget.insertRow(current_row + 1)
            
            new_order_item = QtWidgets.QTableWidgetItem(str(current_row + 2))
            new_order_item.setFlags(new_order_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            new_sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
            new_sensor_item.setFlags(new_sensor_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            
            self.table_widget.setItem(current_row + 1, 0, new_order_item)
            self.table_widget.setItem(current_row + 1, 1, new_sensor_item)
            self.table_widget.setCurrentRow(current_row + 1)
            self._renumber_order_column()
    
    def add_sensor(self):
        """Add a new sensor to the list."""
        available_sensors = [s for s in self.all_sensor_names if s not in self.get_current_sensor_list()]
        if not available_sensors:
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('info', 'No Sensors Available', 'No sensors are available for the selected category.')
            return
        
        sensor, ok = QtWidgets.QInputDialog.getItem(
            self, self.theme_manager.get_text("sensor_priority_add_dialog_title"),
            self.theme_manager.get_text("sensor_priority_add_dialog_label"),
            available_sensors, 0, False
        )
        
        if ok and sensor:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            order_item = QtWidgets.QTableWidgetItem(str(row_position + 1))
            order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            sensor_item = QtWidgets.QTableWidgetItem(sensor)
            sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.table_widget.setItem(row_position, 0, order_item)
            self.table_widget.setItem(row_position, 1, sensor_item)
            self._renumber_order_column()
    
    def remove_sensor(self):
        """Remove selected sensor from the list."""
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            self.table_widget.removeRow(current_row)
            self._renumber_order_column()
    
    def get_current_sensor_list(self):
        """Get the current list of sensors from the table."""
        sensor_list = []
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 1)
            if item:
                sensor_list.append(item.text())
        return sensor_list
    
    def accept_changes(self):
        """Accept changes and store the new priority list."""
        self.new_priority_list = self.get_current_sensor_list()
        self.accept()
    
    def get_updated_priority_list(self):
        """Get the updated priority list."""
        return self.new_priority_list if self.new_priority_list else self.current_priority_list


class MapSelectionDialog(QtWidgets.QDialog):
    """Dialog for interactive map selection of areas of interest."""
    
    def __init__(self, parent=None, initial_bbox_str=None, initial_polygon_coords=None):
        """Initialize the map selection dialog."""
        super().__init__(parent)
        self.setWindowTitle("Map Selection")
        self.setMinimumSize(800, 600)
        
        self.initial_bbox_str = initial_bbox_str
        self.initial_polygon_coords = initial_polygon_coords
        self.selected_polygon_coords = None
        
        self.init_ui()
        self.initialize_map()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Map view
        self.map_view = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(self.map_view)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.draw_button = QtWidgets.QPushButton("Draw Polygon")
        self.draw_button.clicked.connect(self.enable_drawing)
        button_layout.addWidget(self.draw_button)
        
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def initialize_map(self):
        """Initialize the map with OpenStreetMap."""
        # Create map centered on a default location
        m = folium.Map(
            location=[39.8283, -98.5795],  # Center of US
            zoom_start=4,
            control_scale=True
        )
        
        # Add drawing tools
        folium.plugins.Draw(
            export=True,
            position='topleft',
            draw_options={
                'polyline': False,
                'rectangle': True,
                'polygon': True,
                'circle': False,
                'marker': False,
            }
        ).add_to(m)
        
        # Save map to temporary file
        temp_dir = tempfile.gettempdir()
        temp_html = os.path.join(temp_dir, "flutter_earth_map_selection.html")
        m.save(temp_html)
        
        # Load map in web view
        self.map_view.setUrl(QtCore.QUrl.fromLocalFile(temp_html))
    
    def enable_drawing(self):
        """Enable drawing mode on the map."""
        # This would require JavaScript interaction with the map
        # For now, just show a message
        QtWidgets.QMessageBox.information(self, "Drawing Mode", 
                                        "Drawing mode enabled. Use the drawing tools on the map.")
    
    def clear_selection(self):
        """Clear the current selection."""
        self.selected_polygon_coords = None
        # This would require JavaScript interaction to clear the map
        QtWidgets.QMessageBox.information(self, "Clear", "Selection cleared.")
    
    def get_selected_polygon_coords_str(self):
        """Get the selected polygon coordinates as a string."""
        if self.selected_polygon_coords:
            return json.dumps(self.selected_polygon_coords)
        return None


class QtLogHandler(logging.Handler):
    """Custom log handler for Qt text widgets."""
    
    def __init__(self, text_widget: QtWidgets.QTextEdit):
        """Initialize the log handler."""
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        """Emit a log record to the text widget."""
        msg = self.format(record)
        self.text_widget.append(msg)
        # Auto-scroll to bottom
        self.text_widget.verticalScrollBar().setValue(
            self.text_widget.verticalScrollBar().maximum()
        )


def create_help_button(help_title: str, help_text: str, parent_widget: QtWidgets.QWidget) -> QtWidgets.QPushButton:
    """Create a help button with tooltip and click handler."""
    help_button = QtWidgets.QPushButton("?")
    help_button.setMaximumSize(20, 20)
    help_button.setToolTip(help_title)
    
    def show_help():
        msg = QtWidgets.QMessageBox(parent_widget)
        msg.setWindowTitle(help_title)
        msg.setText(help_text)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
    
    help_button.clicked.connect(show_help)
    return help_button


def create_form_label_with_help(base_text: str, help_title: str, help_text: str, 
                               parent_widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Create a label with help button for forms."""
    container = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    
    label = QtWidgets.QLabel(base_text)
    help_button = create_help_button(help_title, help_text, parent_widget)
    
    layout.addWidget(label)
    layout.addWidget(help_button)
    layout.addStretch()
    
    return container


class IndexAnalysisPane(QtWidgets.QWidget):
    """Pane for index analysis functionality."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        """Initialize the index analysis pane."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.selected_indices_checkboxes = {}
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout for IndexAnalysisPane will be a horizontal splitter
        pane_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        main_layout_for_pane = QtWidgets.QHBoxLayout(self)
        main_layout_for_pane.addWidget(pane_splitter)
        main_layout_for_pane.setContentsMargins(5, 5, 5, 5)
        
        # Internal Left Widget (for Inputs, Outputs, Start Button)
        internal_left_widget = QtWidgets.QWidget()
        internal_left_layout = QtWidgets.QVBoxLayout(internal_left_widget)
        internal_left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Input Selection Group
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
        self.selected_files_list_widget_ia.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.selected_files_list_widget_ia.setMinimumHeight(100)
        input_group_layout_ia.addWidget(self.selected_files_list_widget_ia, 1)
        
        self.remove_selected_button_ia = QtWidgets.QPushButton("Remove Selected")
        self.clear_list_button_ia = QtWidgets.QPushButton("Clear List")
        input_management_layout_ia = QtWidgets.QHBoxLayout()
        input_management_layout_ia.addWidget(self.remove_selected_button_ia)
        input_management_layout_ia.addWidget(self.clear_list_button_ia)
        input_management_layout_ia.addStretch()
        input_group_layout_ia.addLayout(input_management_layout_ia)
        internal_left_layout.addWidget(self.input_group_box_ia, 1)
        
        # Output Selection Group
        self.output_group_box_ia = QtWidgets.QGroupBox("Output Settings for Index Analysis")
        output_group_layout_ia = QtWidgets.QFormLayout(self.output_group_box_ia)
        self.index_output_dir_label_ia = QtWidgets.QLabel("Output Directory:")
        self.index_output_dir_input_ia = QtWidgets.QLineEdit()
        self.index_output_dir_input_ia.setPlaceholderText("Select folder for indices...")
        self.index_browse_button_ia = QtWidgets.QPushButton("Browse...")
        index_output_dir_layout_ia = QtWidgets.QHBoxLayout()
        index_output_dir_layout_ia.addWidget(self.index_output_dir_input_ia)
        index_output_dir_layout_ia.addWidget(self.index_browse_button_ia)
        output_group_layout_ia.addRow(self.index_output_dir_label_ia, index_output_dir_layout_ia)
        internal_left_layout.addWidget(self.output_group_box_ia)
        
        # Start Button
        self.start_index_analysis_button_ia = QtWidgets.QPushButton("🚀 Start Index Analysis")
        internal_left_layout.addWidget(self.start_index_analysis_button_ia, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        internal_left_layout.addStretch(0)
        
        pane_splitter.addWidget(internal_left_widget)
        
        # Internal Right Widget (for Index Selection Checkboxes)
        internal_right_widget = QtWidgets.QWidget()
        internal_right_layout = QtWidgets.QVBoxLayout(internal_right_widget)
        internal_right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Index Selection Group
        indices_group_box = QtWidgets.QGroupBox("Select Indices to Calculate")
        indices_group_layout = QtWidgets.QVBoxLayout(indices_group_box)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        # Available indices (placeholder - should be imported from a constants file)
        AVAILABLE_INDICES = {
            'NDVI': {'name': 'Normalized Difference Vegetation Index', 'formula_desc': '(NIR - Red) / (NIR + Red)'},
            'NDWI': {'name': 'Normalized Difference Water Index', 'formula_desc': '(Green - NIR) / (Green + NIR)'},
            'NDBI': {'name': 'Normalized Difference Built-up Index', 'formula_desc': '(SWIR - NIR) / (SWIR + NIR)'},
            'SAVI': {'name': 'Soil Adjusted Vegetation Index', 'formula_desc': '1.5 * (NIR - Red) / (NIR + Red + 0.5)'},
            'EVI': {'name': 'Enhanced Vegetation Index', 'formula_desc': '2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)'}
        }
        
        for key, info in AVAILABLE_INDICES.items():
            index_item_layout = QtWidgets.QHBoxLayout()
            index_item_layout.setContentsMargins(0, 0, 0, 0)
            index_item_layout.setSpacing(5)
            
            checkbox = QtWidgets.QCheckBox(f"{info.get('name', key)} ({key})")
            checkbox.setToolTip(info.get('formula_desc', 'No detailed formula description available.'))
            self.selected_indices_checkboxes[key] = checkbox
            index_item_layout.addWidget(checkbox)
            
            help_title = f"{key} - {info.get('name', 'Index Information')}"
            help_text = f"<b>{info.get('name', key)}</b>\n\nFormula: {info.get('formula_desc', 'Not specified')}"
            help_button = create_help_button(help_title, help_text, self)
            index_item_layout.addWidget(help_button)
            index_item_layout.addStretch(1)
            scroll_layout.addLayout(index_item_layout)
        
        scroll_area.setWidget(scroll_widget)
        indices_group_layout.addWidget(scroll_area)
        internal_right_layout.addWidget(indices_group_box, 1)
        pane_splitter.addWidget(internal_right_widget)
        
        # Set initial sizes for the internal splitter
        pane_splitter.setSizes([int(self.width() * 0.6) if self.width() > 0 else 300, 
                               int(self.width() * 0.4) if self.width() > 0 else 200])
    
    def get_selected_indices(self):
        """Get list of selected indices."""
        return [key for key, checkbox in self.selected_indices_checkboxes.items() if checkbox.isChecked()]
    
    def get_input_files(self):
        """Get list of input files."""
        return [self.selected_files_list_widget_ia.item(i).text() 
                for i in range(self.selected_files_list_widget_ia.count())]
    
    def get_output_dir(self):
        """Get output directory."""
        return self.index_output_dir_input_ia.text()


class VectorDownloadTab(QtWidgets.QWidget):
    """Tab for vector data download functionality."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        """Initialize the vector download tab."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        try:
            self._init_ui()
            self.apply_styles()
        except Exception as e:
            logging.error(f"Error during VectorDownloadTab initialization: {e}", exc_info=True)
            # Fallback UI within the tab if its own init fails
            fallback_layout = QtWidgets.QVBoxLayout(self)
            error_label_text = f"Error initializing Vector Data Download tab content:\n{str(e)[:150]}...\n\nCheck logs for details."
            error_label = QtWidgets.QLabel(error_label_text)
            error_label.setWordWrap(True)
            error_label.setStyleSheet("color: red; font-weight: bold;")
            fallback_layout.addWidget(error_label)
            self.setLayout(fallback_layout)
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        
        # Data Source Input
        self.source_input = QtWidgets.QLineEdit()
        self.source_input.setPlaceholderText("Enter Overpass API query, WFS URL, etc.")
        form_layout.addRow(QtWidgets.QLabel("Data Source:"), self.source_input)
        
        # AOI Input for Vector Data
        self.vector_aoi_label = QtWidgets.QLabel("Area of Interest (AOI):")
        self.vector_aoi_input = QtWidgets.QLineEdit()
        self.vector_aoi_input.setPlaceholderText("e.g., minLon,minLat,maxLon,maxLat or [[lon,lat],...]")
        self.vector_aoi_map_button = QtWidgets.QPushButton("🗺️ Select from Map")
        self.vector_aoi_map_button.clicked.connect(self._open_map_for_vector_aoi)
        aoi_layout = QtWidgets.QHBoxLayout()
        aoi_layout.addWidget(self.vector_aoi_input, 1)
        aoi_layout.addWidget(self.vector_aoi_map_button)
        form_layout.addRow(self.vector_aoi_label, aoi_layout)
        
        # Source Type Dropdown
        self.source_type_combo = QtWidgets.QComboBox()
        self.source_type_combo.addItems(["Overpass API (OSM)", "WFS (Web Feature Service)", "Direct GeoJSON URL"])
        form_layout.addRow(QtWidgets.QLabel("Source Type:"), self.source_type_combo)
        
        # Overpass Specific Options Group
        self.overpass_options_group = QtWidgets.QGroupBox("Overpass API Options")
        self.overpass_options_layout = QtWidgets.QVBoxLayout(self.overpass_options_group)
        
        # Radio buttons for Overpass query mode
        self.rb_group_overpass_mode = QtWidgets.QButtonGroup(self)
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
        
        # Add the Overpass options group to the main form layout
        form_layout.addRow(self.overpass_options_group)
        
        # Connect signals
        self.source_type_combo.currentTextChanged.connect(self._on_source_type_changed)
        self.rb_predefined_features.toggled.connect(self._on_overpass_query_mode_changed)
        
        # Output Directory
        output_dir_layout = QtWidgets.QHBoxLayout()
        self.output_dir_input_vd = QtWidgets.QLineEdit()
        self.output_dir_input_vd.setPlaceholderText("Select output directory for vector data...")
        self.output_dir_browse_button_vd = QtWidgets.QPushButton("Browse...")
        self.output_dir_browse_button_vd.clicked.connect(self._browse_output_dir_vd)
        output_dir_layout.addWidget(self.output_dir_input_vd, 1)
        output_dir_layout.addWidget(self.output_dir_browse_button_vd)
        form_layout.addRow(QtWidgets.QLabel("Output Directory:"), output_dir_layout)
        
        # Start Download Button
        self.start_vector_download_button = QtWidgets.QPushButton("🚀 Start Vector Download")
        self.start_vector_download_button.clicked.connect(self._start_vector_download_wrapper)
        form_layout.addRow(self.start_vector_download_button)
        
        layout.addLayout(form_layout)
        layout.addStretch()
    
    def _open_map_for_vector_aoi(self):
        """Open map selection dialog for vector AOI."""
        from .gui_components import MapSelectionDialog
        dialog = MapSelectionDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            coords_str = dialog.get_selected_polygon_coords_str()
            if coords_str:
                self.vector_aoi_input.setText(coords_str)
    
    def _browse_output_dir_vd(self):
        """Browse for vector download output directory."""
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Vector Output Directory", self.output_dir_input_vd.text()
        )
        if dir_path:
            self.output_dir_input_vd.setText(dir_path)
    
    def _on_source_type_changed(self, source_type_text):
        """Handle source type change."""
        if "Overpass" in source_type_text:
            self.overpass_options_group.setVisible(True)
            self.rb_predefined_features.setChecked(True)
        else:
            self.overpass_options_group.setVisible(False)
    
    def _on_overpass_query_mode_changed(self):
        """Handle overpass query mode change."""
        if self.rb_predefined_features.isChecked():
            self.predefined_features_group.setVisible(True)
            self.source_input.setEnabled(False)
        else:
            self.predefined_features_group.setVisible(False)
            self.source_input.setEnabled(True)
    
    def _start_vector_download_wrapper(self):
        """Wrapper to run the download in a thread."""
        try:
            # Get parameters from UI
            source_type = self.source_type_combo.currentText()
            source_url = self.source_input.text().strip()
            output_dir = self.output_dir_input_vd.text().strip()
            output_format = self.output_format_combo_vd.currentText()
            
            # Validate inputs
            if not source_url:
                QtWidgets.QMessageBox.warning(self, "Missing Input", "Please enter a source URL or query.")
                return
            
            if not output_dir:
                QtWidgets.QMessageBox.warning(self, "Missing Output", "Please select an output directory.")
                return
            
            # Get AOI if provided
            aoi_coords = None
            aoi_text = self.vector_aoi_input.text().strip()
            if aoi_text:
                try:
                    # Try to parse as bbox string
                    if ',' in aoi_text:
                        coords = [float(c.strip()) for c in aoi_text.split(',')]
                        if len(coords) == 4:
                            aoi_coords = aoi_text
                        else:
                            raise ValueError("Invalid bbox format")
                    else:
                        # Try to parse as JSON polygon
                        import json
                        aoi_coords = json.loads(aoi_text)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Invalid AOI", f"Invalid AOI format: {e}")
                    return
            
            # Get predefined features if using Overpass
            predefined_features = None
            if "Overpass" in source_type and self.rb_predefined_features.isChecked():
                predefined_features = []
                for i in range(self.predefined_features_list.count()):
                    item = self.predefined_features_list.item(i)
                    if item.isSelected():
                        predefined_features.append(item.text())
                
                if not predefined_features:
                    QtWidgets.QMessageBox.warning(self, "No Features Selected", "Please select at least one predefined feature.")
                    return
            
            # Create progress dialog
            progress_dialog = QtWidgets.QProgressDialog("Downloading vector data...", "Cancel", 0, 100, self)
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setAutoClose(False)
            
            # Import vector downloader
            from .vector_download import VectorDownloader
            
            # Create downloader instance
            downloader = VectorDownloader()
            
            # Start download in thread
            import threading
            download_thread = threading.Thread(
                target=self._download_vector_data_thread,
                args=(downloader, source_type, source_url, output_dir, output_format, 
                      aoi_coords, predefined_features, progress_dialog)
            )
            download_thread.daemon = True
            download_thread.start()
            
        except Exception as e:
            logging.error(f"Error starting vector download: {e}")
            QtWidgets.QMessageBox.critical(self, "Download Error", f"Failed to start download: {e}")
    
    def _download_vector_data_thread(self, downloader, source_type, source_url, output_dir, 
                                   output_format, aoi_coords, predefined_features, progress_dialog):
        """Thread function for vector data download."""
        try:
            def progress_callback(progress, message):
                progress_dialog.setValue(int(progress * 100))
                progress_dialog.setLabelText(message)
                if progress_dialog.wasCanceled():
                    downloader.request_cancel()
                    return False
                return True
            
            # Perform download
            result = downloader.download_vector_data(
                source_type=source_type,
                source_url=source_url,
                output_dir=output_dir,
                output_format=output_format,
                aoi_coords=aoi_coords,
                predefined_features=predefined_features,
                progress_callback=progress_callback
            )
            
            # Show result
            if result['success']:
                QtWidgets.QMessageBox.information(
                    self, "Download Complete", 
                    f"Successfully downloaded {result.get('feature_count', 0)} features.\n"
                    f"Files saved to: {output_dir}"
                )
            else:
                QtWidgets.QMessageBox.critical(
                    self, "Download Failed", 
                    f"Download failed: {result.get('message', 'Unknown error')}"
                )
                
        except Exception as e:
            logging.error(f"Vector download thread error: {e}")
            QtWidgets.QMessageBox.critical(self, "Download Error", f"Download failed: {e}")
        finally:
            progress_dialog.close()
    
    def apply_styles(self):
        """Apply themed styles to the components."""
        colors = self.theme_manager.colors
        self.setStyleSheet(
            f"QGroupBox {{ font-weight: bold; border: 1px solid {colors['ACCENT_BORDER']}; "
            f"border-radius: 5px; margin-top: 1ex; padding-top: 10px; }} "
            f"QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }}"
        )
    
    def update_theme(self, theme_manager: ThemeManager):
        """Update the theme for this component."""
        self.theme_manager = theme_manager
        self.apply_styles()


class DataViewerTab(QtWidgets.QWidget):
    """Tab for data visualization with matplotlib."""
    
    def __init__(self, theme_manager: ThemeManager, parent=None):
        """Initialize the data viewer tab."""
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_filepath = None
        self.canvas = None
        self.figure = None
        self.ax = None
        self.vector_layers_data = []
        
        try:
            # Try to import matplotlib components
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
            
            self.Figure = Figure
            self.FigureCanvas = FigureCanvas
            self.NavigationToolbar = NavigationToolbar
            
            self._init_ui()
        except ImportError as e:
            logging.error(f"Matplotlib not available: {e}")
            self._create_fallback_ui("Matplotlib is not installed. Please install matplotlib to use the data viewer.")
        except Exception as e:
            logging.error(f"Error during DataViewerTab initialization: {e}", exc_info=True)
            self._create_fallback_ui(f"Failed to initialize Data Viewer: {str(e)[:200]}")
    
    def _create_fallback_ui(self, message: str):
        """Create a fallback UI when matplotlib is not available."""
        fallback_layout = QtWidgets.QVBoxLayout(self)
        error_label = QtWidgets.QLabel(message)
        error_label.setWordWrap(True)
        error_label.setAlignment(QtCore.Qt.AlignCenter)
        error_label.setStyleSheet("color: red; font-weight: bold;")
        fallback_layout.addWidget(error_label)
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Matplotlib Figure and Canvas
        self.figure = self.Figure(figsize=(5, 4), dpi=100)
        self.canvas = self.FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_axis_off()
        
        try:
            if self.figure is not None:
                self.figure.tight_layout()
        except Exception as e_tight:
            logging.warning(f"Matplotlib tight_layout failed: {e_tight}")
        
        # Add Matplotlib Navigation Toolbar
        self.toolbar = self.NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        
        # Unified Data Loading Controls
        data_load_controls_layout = QtWidgets.QHBoxLayout()
        
        # Sample Site Selector
        self.sample_site_label = QtWidgets.QLabel("Quick Load Sample Site:")
        data_load_controls_layout.addWidget(self.sample_site_label)
        
        self.sample_site_selector_combo = QtWidgets.QComboBox()
        self.sample_site_selector_combo.addItem("Select a sample...")
        # Add sample configurations
        sample_configs = {
            "jerusalem_sample": "Jerusalem (Sentinel-2)",
            "tel_aviv_sample": "Tel Aviv (Landsat 8)", 
            "haifa_sample": "Haifa (Sentinel-2)",
            "dead_sea_sample": "Dead Sea (Landsat 8)"
        }
        
        for key, display_name in sample_configs.items():
            self.sample_site_selector_combo.addItem(display_name, key)
        
        self.sample_site_selector_combo.setToolTip("Load a pre-defined sample dataset if it has been downloaded.")
        self.sample_site_selector_combo.currentIndexChanged.connect(self._on_sample_site_selected)
        data_load_controls_layout.addWidget(self.sample_site_selector_combo)
        
        data_load_controls_layout.addSpacing(20)
        
        # Load Data Button with Menu
        self.load_data_button = QtWidgets.QPushButton("Load Custom Data Layer")
        self.load_data_button.setToolTip("Load a raster or vector data layer.")
        
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
        
        # Canvas Container
        canvas_container_frame = QtWidgets.QFrame()
        border_thickness = 2
        border_color = self.theme_manager.colors.get('ACCENT_BORDER', '#888888')
        canvas_container_frame.setStyleSheet(
            f"QFrame {{ border: {border_thickness}px solid {border_color}; border-radius: 3px; }}"
        )
        canvas_container_layout = QtWidgets.QVBoxLayout(canvas_container_frame)
        canvas_container_layout.setContentsMargins(0, 0, 0, 0)
        canvas_container_layout.addWidget(self.canvas)
        
        layout.addWidget(canvas_container_frame, 1)
        
        # Connect scroll event for zoom
        if self.canvas:
            self.canvas.mpl_connect('scroll_event', self._on_scroll_zoom)
    
    def _load_vector_layer_action(self):
        """Load vector layer from file."""
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Vector Layer", "",
            "Vector Files (*.shp *.geojson *.json);;Shapefiles (*.shp);;GeoJSON (*.geojson *.json);;All Files (*)"
        )
        if not filepath:
            return
        
        try:
            geometries = self._parse_vector_file(filepath)
            if geometries:
                style = {'edgecolor': 'cyan', 'facecolor': 'none', 'linewidth': 1.2, 'alpha': 0.75}
                self.vector_layers_data.append({'geometries': geometries, 'filepath': filepath, 'style': style})
                self._redraw_display()
                logging.info(f"Loaded and displayed vector layer: {os.path.basename(filepath)}")
            else:
                logging.warning(f"No geometries found or parsed from {filepath}")
                if hasattr(self, 'bridge'):
                    self.bridge.showMessage.emit('info', 'Empty Layer', f"No displayable geometries found in {os.path.basename(filepath)}.")
        except Exception as e:
            logging.error(f"Error loading vector layer {filepath}: {e}", exc_info=True)
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('error', 'Vector Load Error', f"Failed to load {os.path.basename(filepath)}:\n{e}")
    
    def _clear_vector_layers_action(self):
        """Clear existing vector layers and redraw."""
        self.vector_layers_data = []
        self._redraw_display()
        logging.info("Cleared all vector overlays.")
    
    def _on_sample_site_selected(self, index):
        """Handle sample site selection."""
        if index == 0:  # Placeholder "Select a sample..." is selected
            return
        
        selected_key = self.sample_site_selector_combo.itemData(index)
        if not selected_key:
            return
        
        # Implement sample loading logic
        try:
            from .sample_manager import SampleManager
            
            sample_manager = SampleManager()
            sample_path = sample_manager.get_sample_path(selected_key)
            
            if sample_path and os.path.exists(sample_path):
                # Load the sample data
                self.load_specific_raster(sample_path)
                logging.info(f"Loaded sample data: {selected_key}")
            else:
                # Offer to download the sample
                reply = QtWidgets.QMessageBox.question(
                    self, "Sample Not Found", 
                    f"Sample '{selected_key}' is not downloaded. Would you like to download it now?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                
                if reply == QtWidgets.QMessageBox.Yes:
                    self._download_sample_data(selected_key)
                    
        except Exception as e:
            logging.error(f"Error loading sample {selected_key}: {e}")
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('error', 'Sample Load Error', f"Failed to load sample: {e}")
    
    def _download_sample_data(self, sample_key):
        """Download sample data."""
        try:
            from .sample_manager import SampleManager
            
            sample_manager = SampleManager()
            
            def download_callback(sample_key, success, message):
                if success:
                    QtWidgets.QMessageBox.information(self, "Download Complete", f"Sample '{sample_key}' downloaded successfully.")
                    # Reload the sample
                    sample_path = sample_manager.get_sample_path(sample_key)
                    if sample_path and os.path.exists(sample_path):
                        self.load_specific_raster(sample_path)
                else:
                    QtWidgets.QMessageBox.critical(self, "Download Failed", f"Failed to download sample: {message}")
            
            # Queue the download
            sample_manager.queue_sample_download(sample_key, download_callback)
            
        except Exception as e:
            logging.error(f"Error downloading sample {sample_key}: {e}")
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('error', 'Download Error', f"Failed to start download: {e}")
    
    def _parse_vector_file(self, filepath):
        """Parse vector file and return geometries."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.shp':
            return self._parse_shapefile(filepath)
        elif ext in ['.geojson', '.json']:
            return self._parse_geojson(filepath)
        else:
            raise ValueError(f"Unsupported vector file type: {ext}")
    
    def _parse_shapefile(self, filepath):
        """Parse shapefile using pyshp."""
        try:
            import shapefile
            geometries = []
            with shapefile.Reader(filepath) as sf:
                for shape_rec in sf.iterShapes():
                    if shape_rec.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM, 5, 15, 25]:
                        part_indices = list(shape_rec.parts) + [len(shape_rec.points)]
                        for i in range(len(part_indices) - 1):
                            start = part_indices[i]
                            end = part_indices[i+1]
                            part_coords = shape_rec.points[start:end]
                            if len(part_coords) >= 3:
                                geometries.append(part_coords)
            return geometries
        except ImportError:
            raise ImportError("pyshp library is required to read shapefiles")
        except Exception as e:
            logging.error(f"Error reading shapefile {filepath}: {e}", exc_info=True)
            raise
    
    def _parse_geojson(self, filepath):
        """Parse GeoJSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            geometries = []
            if geojson_data.get('type') == 'FeatureCollection':
                for feature in geojson_data.get('features', []):
                    geom = feature.get('geometry', {})
                    if geom.get('type') == 'Polygon':
                        for ring in geom.get('coordinates', []):
                            geometries.append(ring)
            elif geojson_data.get('type') == 'Feature':
                geom = geojson_data.get('geometry', {})
                if geom.get('type') == 'Polygon':
                    for ring in geom.get('coordinates', []):
                        geometries.append(ring)
            elif geojson_data.get('type') == 'Polygon':
                for ring in geojson_data.get('coordinates', []):
                    geometries.append(ring)
            
            return geometries
        except Exception as e:
            logging.error(f"Error reading GeoJSON {filepath}: {e}", exc_info=True)
            raise
    
    def load_raster_file_action(self):
        """Load raster file action."""
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Raster Layer", "",
            "Raster Files (*.tif *.tiff *.img *.hdr);;GeoTIFF (*.tif *.tiff);;All Files (*)"
        )
        if filepath:
            self.load_specific_raster(filepath)
    
    def _on_scroll_zoom(self, event):
        """Handle scroll zoom event."""
        if event.inaxes != self.ax:
            return
        
        # Get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # Get event location
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
        
        # Get distance from the cursor
        base_scale = 0.9
        if event.button == 'up':
            # Zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # Zoom out
            scale_factor = base_scale
        else:
            # Something else happened
            scale_factor = 1
        
        # Set new limits
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        
        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        
        # Force redraw
        self.canvas.draw()
    
    def _scale_band_to_uint8(self, band_data, nodataval=None, band_name_for_log="band"):
        """Scale band data to uint8 for display."""
        try:
            if nodataval is not None:
                valid_mask = band_data != nodataval
                if not valid_mask.any():
                    logging.warning(f"{band_name_for_log}: No valid pixels found")
                    return None
                valid_data = band_data[valid_mask]
            else:
                valid_data = band_data.flatten()
            
            if len(valid_data) == 0:
                return None
            
            # Calculate percentiles for robust scaling
            p2, p98 = numpy.percentile(valid_data, (2, 98))
            
            if p2 == p98:
                logging.warning(f"{band_name_for_log}: No contrast in data (p2=p98={p2})")
                return None
            
            # Scale to 0-255
            scaled = numpy.clip((band_data - p2) / (p98 - p2) * 255, 0, 255).astype(numpy.uint8)
            
            if nodataval is not None:
                scaled[~valid_mask] = 0
            
            return scaled
        except Exception as e:
            logging.error(f"Error scaling {band_name_for_log}: {e}")
            return None
    
    def _redraw_display(self):
        """Redraw the display with current data."""
        if not self.ax:
            return
        
        self.ax.clear()
        self.ax.set_axis_off()
        
        # Draw raster if available
        if hasattr(self, 'current_raster_data') and self.current_raster_data is not None:
            self.ax.imshow(self.current_raster_data, cmap='viridis')
        
        # Draw vector layers
        for layer in self.vector_layers_data:
            for geometry in layer['geometries']:
                if len(geometry) >= 3:
                    coords = numpy.array(geometry)
                    self.ax.plot(coords[:, 0], coords[:, 1], 
                               color=layer['style']['edgecolor'],
                               linewidth=layer['style']['linewidth'],
                               alpha=layer['style']['alpha'])
        
        self.canvas.draw()
    
    def load_specific_raster(self, filepath):
        """Load a specific raster file."""
        if not filepath or not os.path.exists(filepath):
            self.current_filepath = None
            self.current_raster_data = None
            self._redraw_display()
            return
        
        try:
            import rasterio
            with rasterio.open(filepath) as src:
                # Read the first band for display
                band_data = src.read(1)
                nodataval = src.nodata
                
                # Scale to uint8 for display
                scaled_data = self._scale_band_to_uint8(band_data, nodataval, "raster")
                
                if scaled_data is not None:
                    self.current_raster_data = scaled_data
                    self.current_filepath = filepath
                    self._redraw_display()
                    logging.info(f"Loaded raster: {os.path.basename(filepath)}")
                else:
                    logging.warning(f"Failed to scale raster data: {filepath}")
                    
        except ImportError:
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('warning', 'Missing Dependency', "rasterio library is required to read raster files.")
        except Exception as e:
            logging.error(f"Error loading raster {filepath}: {e}", exc_info=True)
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('error', 'Raster Load Error', f"Failed to load {os.path.basename(filepath)}:\n{e}")


class ThemeSelectionDialog(QtWidgets.QDialog):
    """Modal dialog for selecting and customizing themes."""
    theme_applied = QtCore.pyqtSignal(str, dict)

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Theme")
        self.setMinimumSize(600, 500)
        self.theme_manager = theme_manager
        self.selected_theme = theme_manager.theme_name
        self.selected_suboptions = theme_manager.suboptions.copy()
        self._init_ui()
        self._update_preview()

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        self.theme_buttons = {}
        for category in self.theme_manager.get_categories():
            tab = QtWidgets.QWidget()
            vbox = QtWidgets.QVBoxLayout(tab)
            theme_list = QtWidgets.QListWidget()
            theme_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            for theme_name in self.theme_manager.get_available_themes(category):
                meta = self.theme_manager.get_theme_metadata(theme_name)
                item = QtWidgets.QListWidgetItem(meta["display"])
                # Color swatch preview
                color = self.theme_manager.get_theme_colors(theme_name)["BG_MAIN"]
                pixmap = QtGui.QPixmap(32, 32)
                pixmap.fill(QtGui.QColor(color))
                item.setIcon(QtGui.QIcon(pixmap))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, theme_name)
                theme_list.addItem(item)
                if theme_name == self.selected_theme:
                    theme_list.setCurrentItem(item)
            theme_list.currentItemChanged.connect(self._on_theme_selected)
            vbox.addWidget(theme_list)
            self.theme_buttons[category] = theme_list
            tab.setLayout(vbox)
            self.tabs.addTab(tab, category)
        layout.addWidget(self.tabs)

        # Sub-options
        self.suboptions_group = QtWidgets.QGroupBox("Theme Options")
        suboptions_layout = QtWidgets.QVBoxLayout()
        self.cb_catchphrases = QtWidgets.QCheckBox("Use character catchphrases")
        self.cb_icons = QtWidgets.QCheckBox("Show special icons")
        self.cb_animated = QtWidgets.QCheckBox("Enable animated background")
        suboptions_layout.addWidget(self.cb_catchphrases)
        suboptions_layout.addWidget(self.cb_icons)
        suboptions_layout.addWidget(self.cb_animated)
        self.suboptions_group.setLayout(suboptions_layout)
        layout.addWidget(self.suboptions_group)
        self.cb_catchphrases.setChecked(self.selected_suboptions.get("catchphrases", False))
        self.cb_icons.setChecked(self.selected_suboptions.get("special_icons", False))
        self.cb_animated.setChecked(self.selected_suboptions.get("animated_background", False))
        self.cb_catchphrases.stateChanged.connect(self._on_suboption_changed)
        self.cb_icons.stateChanged.connect(self._on_suboption_changed)
        self.cb_animated.stateChanged.connect(self._on_suboption_changed)

        # Live preview
        self.preview_group = QtWidgets.QGroupBox("Live Preview")
        preview_layout = QtWidgets.QVBoxLayout()
        self.preview_widget = QtWidgets.QLabel()
        self.preview_widget.setMinimumHeight(80)
        self.preview_widget.setAlignment(QtCore.Qt.AlignCenter)
        preview_layout.addWidget(self.preview_widget)
        self.preview_group.setLayout(preview_layout)
        layout.addWidget(self.preview_group)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_apply = QtWidgets.QPushButton("Apply")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_reset = QtWidgets.QPushButton("Reset to Default")
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_reset)
        layout.addLayout(btn_layout)
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self._on_reset)

    def _on_theme_selected(self, current, previous):
        if current:
            theme_name = current.data(QtCore.Qt.ItemDataRole.UserRole)
            self.selected_theme = theme_name
            self._update_preview()

    def _on_suboption_changed(self):
        self.selected_suboptions["catchphrases"] = self.cb_catchphrases.isChecked()
        self.selected_suboptions["special_icons"] = self.cb_icons.isChecked()
        self.selected_suboptions["animated_background"] = self.cb_animated.isChecked()
        self._update_preview()

    def _update_preview(self):
        # Show a color swatch, display name, and character-specific information
        colors = self.theme_manager.get_theme_colors(self.selected_theme)
        meta = self.theme_manager.get_theme_metadata(self.selected_theme)
        bg_pattern = self.theme_manager.get_background_pattern(self.selected_theme)
        
        # Create preview pixmap with theme colors
        pixmap = QtGui.QPixmap(300, 80)
        painter = QtGui.QPainter(pixmap)
        
        # Fill with theme background
        if bg_pattern:
            # For now, just fill with BG_MAIN (Qt can't parse CSS gradients directly)
            painter.fillRect(pixmap.rect(), QtGui.QColor(colors["BG_MAIN"]))
        else:
            painter.fillRect(pixmap.rect(), QtGui.QColor(colors["BG_MAIN"]))
        
        # Add some theme-specific decorations
        if self.selected_theme == "Rainbow Dash":
            # Draw rainbow stripes
            for i in range(6):
                color = QtGui.QColor(["#E3F2FD", "#BBDEFB", "#FFF176", "#FF9800", "#9C27B0", "#E3F2FD"][i])
                painter.fillRect(0, i * 13, 300, 13, color)
        elif self.selected_theme == "Pinkie Pie":
            # Draw confetti dots
            for i in range(10):
                x = (i * 30) % 300
                y = ((i * 17) % 80)
                painter.fillEllipse(x, y, 8, 8, QtGui.QColor("#F06292"))
        elif self.selected_theme == "Creeper":
            # Draw pixelated pattern
            for i in range(0, 300, 20):
                for j in range(0, 80, 20):
                    color = QtGui.QColor("#4CAF50") if (i + j) % 40 == 0 else QtGui.QColor("#388E3C")
                    painter.fillRect(i, j, 20, 20, color)
        
        painter.end()
        self.preview_widget.setPixmap(pixmap)
        
        # Add display name and character information
        text = f"<b>{meta['display']}</b>"
        
        # Add catchphrase if enabled
        if self.selected_suboptions.get("catchphrases"):
            catchphrase = self.theme_manager.get_catchphrase("greeting")
            if catchphrase:
                text += f"<br><i>{catchphrase}</i>"
        
        # Add special features
        if self.selected_suboptions.get("special_icons"):
            text += "<br><i>✨ Special icons enabled</i>"
        
        if self.selected_suboptions.get("animated_background"):
            if self.selected_theme == "Twilight Sparkle":
                text += "<br><i>✨ Sparkle animations</i>"
            elif self.selected_theme == "Pinkie Pie":
                text += "<br><i>🎉 Confetti animations</i>"
            elif self.selected_theme == "Rainbow Dash":
                text += "<br><i>⚡ Rainbow animations</i>"
            elif self.selected_theme == "Creeper":
                text += "<br><i>💥 Explosion animations</i>"
            elif self.selected_theme == "Enderman":
                text += "<br><i>👁️ Teleport animations</i>"
            else:
                text += "<br><i>🎬 Animated background</i>"
        
        # Add background pattern info
        if bg_pattern:
            if "rainbow" in bg_pattern.lower():
                text += "<br><i>🌈 Rainbow gradient</i>"
            elif "confetti" in bg_pattern.lower():
                text += "<br><i>🎉 Confetti pattern</i>"
            elif "pixel" in bg_pattern.lower():
                text += "<br><i>🧱 Pixelated pattern</i>"
            elif "radial" in bg_pattern.lower():
                text += "<br><i>🌟 Radial gradient</i>"
            else:
                text += "<br><i>🎨 Custom background</i>"
        
        self.preview_widget.setText(text)

    def _on_apply(self):
        self.theme_applied.emit(self.selected_theme, self.selected_suboptions.copy())
        self.accept()

    def _on_reset(self):
        self.selected_theme = DEFAULT_THEME
        self.selected_suboptions = ThemeManager.DEFAULT_SUBOPTIONS.copy()
        # Update UI
        for cat, theme_list in self.theme_buttons.items():
            for i in range(theme_list.count()):
                item = theme_list.item(i)
                if item.data(QtCore.Qt.ItemDataRole.UserRole) == self.selected_theme:
                    theme_list.setCurrentItem(item)
        self.cb_catchphrases.setChecked(False)
        self.cb_icons.setChecked(False)
        self.cb_animated.setChecked(False)
        self._update_preview() 