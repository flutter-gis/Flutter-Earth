"""Advanced GUI components for Flutter Earth."""
import os
import logging
from typing import List, Dict, Any, Optional
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import json
import tempfile
import folium

from .themes import ThemeManager
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
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        
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
            category_item.setFlags(category_item.flags() & ~QtCore.Qt.ItemIsSelectable)
            for sensor_key in sensor_list:
                if sensor_key in SATELLITE_DETAILS:
                    sensor_display_name = f"{sensor_key} ({SATELLITE_DETAILS[sensor_key].get('type', 'N/A')})"
                    sensor_item = QtWidgets.QTreeWidgetItem(category_item, [sensor_display_name])
                    sensor_item.setData(0, QtCore.Qt.UserRole, sensor_key)
        self.satellite_tree.expandAll()
    
    def display_satellite_info(self, current_item, previous_item):
        """Display detailed information for the selected satellite."""
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
                order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable)
                sensor_item = QtWidgets.QTableWidgetItem(sensor_name)
                sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
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
                new_item.setFlags(new_item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.table_widget.setItem(row, 0, new_item)
    
    def move_up(self):
        """Move selected row up."""
        current_row = self.table_widget.currentRow()
        if current_row > 0:
            sensor_item_text = self.table_widget.item(current_row, 1).text()
            self.table_widget.removeRow(current_row)
            self.table_widget.insertRow(current_row - 1)
            
            new_order_item = QtWidgets.QTableWidgetItem(str(current_row))
            new_order_item.setFlags(new_order_item.flags() & ~QtCore.Qt.ItemIsEditable)
            new_sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
            new_sensor_item.setFlags(new_sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
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
            new_order_item.setFlags(new_order_item.flags() & ~QtCore.Qt.ItemIsEditable)
            new_sensor_item = QtWidgets.QTableWidgetItem(sensor_item_text)
            new_sensor_item.setFlags(new_sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
            
            self.table_widget.setItem(current_row + 1, 0, new_order_item)
            self.table_widget.setItem(current_row + 1, 1, new_sensor_item)
            self.table_widget.setCurrentRow(current_row + 1)
            self._renumber_order_column()
    
    def add_sensor(self):
        """Add a new sensor to the list."""
        available_sensors = [s for s in self.all_sensor_names if s not in self.get_current_sensor_list()]
        if not available_sensors:
            QtWidgets.QMessageBox.information(self, "No Sensors Available", 
                                            "All sensors are already in the priority list.")
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
            order_item.setFlags(order_item.flags() & ~QtCore.Qt.ItemIsEditable)
            sensor_item = QtWidgets.QTableWidgetItem(sensor)
            sensor_item.setFlags(sensor_item.flags() & ~QtCore.Qt.ItemIsEditable)
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