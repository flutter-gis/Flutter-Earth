"""
Advanced GIS System for Flutter Earth

This module implements all the advanced GIS features including:
- Dockable side panels
- Multiple map views with synchronization
- Tabbed map interface
- Workspace layouts
- Zen mode
- Floating widget windows
- Global search/command palette
- Interactive onboarding
- Advanced map tools
- Layer management
- And much more
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
import time
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal, QTimer, QThread, QMutex, QWaitCondition
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtGui import QAction, QKeySequence, QShortcut

# Import existing modules
from .config import ConfigManager
from .earth_engine import EarthEngineManager
from .download_manager import DownloadManager
from .progress_tracker import ProgressTracker


class PanelType(Enum):
    """Types of dockable panels"""
    LAYER_LIST = "layer_list"
    ATTRIBUTE_TABLE = "attribute_table"
    TOOLBOX = "toolbox"
    SEARCH = "search"
    BOOKMARKS = "bookmarks"
    MEASUREMENT = "measurement"
    TIME_SLIDER = "time_slider"
    COORDINATE_DISPLAY = "coordinate_display"
    SCALE_BAR = "scale_bar"
    MAGNIFIER = "magnifier"
    NOTIFICATION_CENTER = "notification_center"
    TASK_MANAGER = "task_manager"
    HELP_PANEL = "help_panel"
    STYLE_MANAGER = "style_manager"
    STATISTICS = "statistics"


class MapViewType(Enum):
    """Types of map views"""
    MAIN = "main"
    COMPARISON = "comparison"
    OVERVIEW = "overview"
    DETAIL = "detail"
    TEMPORAL = "temporal"


class ToolType(Enum):
    """Types of GIS tools"""
    ZOOM = "zoom"
    PAN = "pan"
    SELECT = "select"
    MEASURE = "measure"
    IDENTIFY = "identify"
    SWIPE = "swipe"
    ROTATE = "rotate"
    TILT = "tilt"
    MAGNIFIER = "magnifier"
    BOOKMARK = "bookmark"
    SNAP = "snap"
    GRID = "grid"
    GO_TO_COORDINATE = "go_to_coordinate"


@dataclass
class PanelState:
    """State of a dockable panel"""
    panel_type: PanelType
    visible: bool = True
    docked: bool = True
    position: str = "left"  # left, right, top, bottom, floating
    size: Tuple[int, int] = (250, 400)
    position_coords: Tuple[int, int] = (0, 0)
    z_order: int = 0


@dataclass
class MapViewState:
    """State of a map view"""
    view_id: str
    view_type: MapViewType
    center: Tuple[float, float] = (0.0, 0.0)
    zoom_level: float = 10.0
    rotation: float = 0.0
    tilt: float = 0.0
    layers: List[str] = field(default_factory=list)
    synchronized: bool = False
    visible: bool = True
    tab_title: str = ""


@dataclass
class WorkspaceLayout:
    """Complete workspace layout"""
    name: str
    description: str
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    panels: List[PanelState] = field(default_factory=list)
    map_views: List[MapViewState] = field(default_factory=list)
    active_tab: str = ""
    zen_mode: bool = False


@dataclass
class LayerInfo:
    """Information about a map layer"""
    layer_id: str
    name: str
    source: str
    type: str  # raster, vector, wms, etc.
    visible: bool = True
    opacity: float = 1.0
    min_scale: Optional[float] = None
    max_scale: Optional[float] = None
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    group: Optional[str] = None
    expanded: bool = True


@dataclass
class Bookmark:
    """Map bookmark"""
    name: str
    description: str
    center: Tuple[float, float]
    zoom_level: float
    rotation: float = 0.0
    created: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)


@dataclass
class Measurement:
    """Measurement result"""
    type: str  # distance, area, angle
    value: float
    unit: str
    coordinates: List[Tuple[float, float]] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)


class AdvancedGISManager(QObject):
    """
    Main manager for all advanced GIS features
    """
    
    # Signals for QML integration
    panelStateChanged = Signal(str, dict)  # panel_type, state_dict
    mapViewStateChanged = Signal(str, dict)  # view_id, state_dict
    layerStateChanged = Signal(str, dict)  # layer_id, state_dict
    workspaceLayoutChanged = Signal(str)  # layout_name
    bookmarkAdded = Signal(dict)  # bookmark_dict
    measurementCompleted = Signal(dict)  # measurement_dict
    notificationAdded = Signal(str, str, str)  # type, title, message
    taskProgressUpdated = Signal(str, int, str)  # task_id, progress, status
    toolActivated = Signal(str)  # tool_type
    searchResultFound = Signal(str, dict)  # query, result
    
    def __init__(self, config_manager: ConfigManager, earth_engine: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker):
        super().__init__()
        
        self.config_manager = config_manager
        self.earth_engine = earth_engine
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        
        # Core state
        self.panels: Dict[str, PanelState] = {}
        self.map_views: Dict[str, MapViewState] = {}
        self.layers: Dict[str, LayerInfo] = {}
        self.bookmarks: List[Bookmark] = []
        self.measurements: List[Measurement] = []
        self.workspace_layouts: Dict[str, WorkspaceLayout] = {}
        self.current_layout: Optional[str] = None
        self.active_tool: Optional[ToolType] = None
        self.zen_mode: bool = False
        
        # Threading
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
        # Initialize default state
        self._initialize_default_state()
        self._load_saved_state()
        
        # Start background tasks
        self._start_background_tasks()
    
    def _initialize_default_state(self):
        """Initialize default panels and map views"""
        
        # Default panels
        default_panels = [
            PanelState(PanelType.LAYER_LIST, True, True, "left", (250, 400)),
            PanelState(PanelType.TOOLBOX, False, True, "left", (250, 300)),
            PanelState(PanelType.SEARCH, False, True, "top", (400, 50)),
            PanelState(PanelType.BOOKMARKS, False, True, "right", (250, 300)),
            PanelState(PanelType.ATTRIBUTE_TABLE, False, True, "bottom", (600, 200)),
            PanelState(PanelType.COORDINATE_DISPLAY, False, True, "bottom", (200, 30)),
            PanelState(PanelType.SCALE_BAR, False, True, "bottom", (150, 30)),
            PanelState(PanelType.NOTIFICATION_CENTER, False, True, "right", (300, 400)),
            PanelState(PanelType.TASK_MANAGER, False, True, "right", (300, 300)),
        ]
        
        for panel in default_panels:
            self.panels[panel.panel_type.value] = panel
        
        # Default map views
        default_map_views = [
            MapViewState("main", MapViewType.MAIN, (0.0, 0.0), 10.0, layers=[]),
            MapViewState("overview", MapViewType.OVERVIEW, (0.0, 0.0), 5.0, layers=[], visible=False),
        ]
        
        for view in default_map_views:
            self.map_views[view.view_id] = view
        
        # Default workspace layout
        default_layout = WorkspaceLayout(
            name="Default",
            description="Default workspace layout",
            created=datetime.now(),
            modified=datetime.now(),
            panels=default_panels,
            map_views=default_map_views,
            active_tab="main"
        )
        
        self.workspace_layouts["Default"] = default_layout
        self.current_layout = "Default"
    
    def _load_saved_state(self):
        """Load saved workspace layouts and settings"""
        try:
            layouts_file = Path("workspace_layouts.json")
            if layouts_file.exists():
                with open(layouts_file, 'r') as f:
                    data = json.load(f)
                    
                # Load workspace layouts
                for layout_data in data.get("layouts", []):
                    # Convert dicts to dataclass instances for panels and map_views
                    panels = [PanelState(**p) if not isinstance(p, PanelState) else p for p in layout_data.get("panels", [])]
                    map_views = [MapViewState(**v) if not isinstance(v, MapViewState) else v for v in layout_data.get("map_views", [])]
                    active_tab = layout_data.get("active_tab") or "main"
                    layout = WorkspaceLayout(
                        name=layout_data.get("name", "Unnamed"),
                        description=layout_data.get("description", ""),
                        created=layout_data.get("created", datetime.now()),
                        modified=layout_data.get("modified", datetime.now()),
                        panels=panels,
                        map_views=map_views,
                        active_tab=active_tab,
                        zen_mode=layout_data.get("zen_mode", False)
                    )
                    self.workspace_layouts[layout.name] = layout
                
                # Load bookmarks
                for bookmark_data in data.get("bookmarks", []):
                    bookmark = Bookmark(**bookmark_data)
                    self.bookmarks.append(bookmark)
                
                # Load measurements
                for measurement_data in data.get("measurements", []):
                    measurement = Measurement(**measurement_data)
                    self.measurements.append(measurement)
                    
        except Exception as e:
            logging.error(f"Error loading saved state: {e}")
    
    def _save_state(self):
        """Save current state to file"""
        try:
            data = {
                "layouts": [asdict(layout) for layout in self.workspace_layouts.values()],
                "bookmarks": [asdict(bookmark) for bookmark in self.bookmarks],
                "measurements": [asdict(measurement) for measurement in self.measurements],
                "saved_at": datetime.now().isoformat()
            }
            
            with open("workspace_layouts.json", 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logging.error(f"Error saving state: {e}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Coordinate display update timer
        self.coord_timer = QTimer()
        self.coord_timer.timeout.connect(self._update_coordinate_display)
        self.coord_timer.start(100)  # Update every 100ms
        
        # Task monitoring timer
        self.task_timer = QTimer()
        self.task_timer.timeout.connect(self._monitor_tasks)
        self.task_timer.start(1000)  # Update every second
    
    # Panel Management
    def get_panel_state(self, panel_type: str) -> dict:
        """Get current state of a panel"""
        panel = self.panels.get(panel_type)
        if panel:
            return asdict(panel)
        return {}
    
    def set_panel_state(self, panel_type: str, state: dict):
        """Update panel state"""
        if panel_type in self.panels:
            panel = self.panels[panel_type]
            for key, value in state.items():
                if hasattr(panel, key):
                    setattr(panel, key, value)
            
            self.panelStateChanged.emit(panel_type, asdict(panel))
            self._save_state()
    
    def toggle_panel_visibility(self, panel_type: str):
        """Toggle panel visibility"""
        if panel_type in self.panels:
            panel = self.panels[panel_type]
            panel.visible = not panel.visible
            self.panelStateChanged.emit(panel_type, asdict(panel))
            self._save_state()
    
    def undock_panel(self, panel_type: str):
        """Undock a panel to make it floating"""
        if panel_type in self.panels:
            panel = self.panels[panel_type]
            panel.docked = False
            panel.position = "floating"
            self.panelStateChanged.emit(panel_type, asdict(panel))
            self._save_state()
    
    def dock_panel(self, panel_type: str, position: str):
        """Dock a panel to a specific position"""
        if panel_type in self.panels:
            panel = self.panels[panel_type]
            panel.docked = True
            panel.position = position
            self.panelStateChanged.emit(panel_type, asdict(panel))
            self._save_state()
    
    # Map View Management
    def get_map_view_state(self, view_id: str) -> dict:
        """Get current state of a map view"""
        view = self.map_views.get(view_id)
        if view:
            return asdict(view)
        return {}
    
    def set_map_view_state(self, view_id: str, state: dict):
        """Update map view state"""
        if view_id in self.map_views:
            view = self.map_views[view_id]
            for key, value in state.items():
                if hasattr(view, key):
                    setattr(view, key, value)
            
            self.mapViewStateChanged.emit(view_id, asdict(view))
            
            # Synchronize with other views if needed
            if view.synchronized:
                self._synchronize_map_views(view_id, state)
            
            self._save_state()
    
    def create_map_view(self, view_type: str, title: str = "") -> str:
        """Create a new map view"""
        view_id = f"map_{len(self.map_views) + 1}"
        view = MapViewState(
            view_id=view_id,
            view_type=MapViewType(view_type),
            tab_title=title or f"Map {len(self.map_views) + 1}"
        )
        
        self.map_views[view_id] = view
        self.mapViewStateChanged.emit(view_id, asdict(view))
        self._save_state()
        
        return view_id
    
    def remove_map_view(self, view_id: str):
        """Remove a map view"""
        if view_id in self.map_views:
            del self.map_views[view_id]
            self._save_state()
    
    def synchronize_map_views(self, view_ids: List[str]):
        """Synchronize multiple map views"""
        for view_id in view_ids:
            if view_id in self.map_views:
                self.map_views[view_id].synchronized = True
    
    def _synchronize_map_views(self, source_view_id: str, state: dict):
        """Synchronize other views with the source view"""
        source_view = self.map_views[source_view_id]
        
        for view_id, view in self.map_views.items():
            if view_id != source_view_id and view.synchronized:
                # Sync center and zoom
                if 'center' in state:
                    view.center = state['center']
                if 'zoom_level' in state:
                    view.zoom_level = state['zoom_level']
                if 'rotation' in state:
                    view.rotation = state['rotation']
                
                self.mapViewStateChanged.emit(view_id, asdict(view))
    
    # Layer Management
    def add_layer(self, layer_info: dict) -> str:
        """Add a new layer"""
        layer_id = f"layer_{len(self.layers) + 1}"
        layer = LayerInfo(layer_id=layer_id, **layer_info)
        
        self.layers[layer_id] = layer
        self.layerStateChanged.emit(layer_id, asdict(layer))
        self._save_state()
        
        return layer_id
    
    def remove_layer(self, layer_id: str):
        """Remove a layer"""
        if layer_id in self.layers:
            del self.layers[layer_id]
            self._save_state()
    
    def update_layer_visibility(self, layer_id: str, visible: bool):
        """Update layer visibility"""
        if layer_id in self.layers:
            self.layers[layer_id].visible = visible
            self.layerStateChanged.emit(layer_id, asdict(self.layers[layer_id]))
            self._save_state()
    
    def update_layer_opacity(self, layer_id: str, opacity: float):
        """Update layer opacity"""
        if layer_id in self.layers:
            self.layers[layer_id].opacity = max(0.0, min(1.0, opacity))
            self.layerStateChanged.emit(layer_id, asdict(self.layers[layer_id]))
            self._save_state()
    
    def group_layers(self, layer_ids: List[str], group_name: str):
        """Group multiple layers"""
        for layer_id in layer_ids:
            if layer_id in self.layers:
                self.layers[layer_id].group = group_name
                self.layerStateChanged.emit(layer_id, asdict(self.layers[layer_id]))
        
        self._save_state()
    
    def isolate_layer(self, layer_id: str):
        """Show only one layer, hide all others"""
        for lid, layer in self.layers.items():
            layer.visible = (lid == layer_id)
            self.layerStateChanged.emit(lid, asdict(layer))
        
        self._save_state()
    
    # Bookmark Management
    def add_bookmark(self, name: str, description: str, center: Tuple[float, float], 
                    zoom_level: float, tags: List[str] = None):
        """Add a new bookmark"""
        bookmark = Bookmark(
            name=name,
            description=description,
            center=center,
            zoom_level=zoom_level,
            created=datetime.now(),
            tags=tags or []
        )
        
        self.bookmarks.append(bookmark)
        self.bookmarkAdded.emit(asdict(bookmark))
        self._save_state()
    
    def remove_bookmark(self, name: str):
        """Remove a bookmark"""
        self.bookmarks = [b for b in self.bookmarks if b.name != name]
        self._save_state()
    
    def get_bookmarks(self) -> List[dict]:
        """Get all bookmarks"""
        return [asdict(b) for b in self.bookmarks]
    
    # Measurement Tools
    def start_measurement(self, measurement_type: str):
        """Start a measurement operation"""
        self.active_tool = ToolType.MEASURE
        self.toolActivated.emit(measurement_type)
    
    def add_measurement_point(self, coordinates: Tuple[float, float]):
        """Add a point to the current measurement"""
        # This would be implemented with the actual measurement logic
        pass
    
    def complete_measurement(self, measurement_type: str, coordinates: List[Tuple[float, float]]) -> dict:
        """Complete a measurement and return results"""
        if measurement_type == "distance":
            value = self._calculate_distance(coordinates)
            unit = "meters"
        elif measurement_type == "area":
            value = self._calculate_area(coordinates)
            unit = "square meters"
        else:
            value = 0.0
            unit = "unknown"
        
        measurement = Measurement(
            type=measurement_type,
            value=value,
            unit=unit,
            coordinates=coordinates,
            created=datetime.now()
        )
        
        self.measurements.append(measurement)
        self.measurementCompleted.emit(asdict(measurement))
        self._save_state()
        
        return asdict(measurement)
    
    def _calculate_distance(self, coordinates: List[Tuple[float, float]]) -> float:
        """Calculate distance between coordinates"""
        if len(coordinates) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(coordinates) - 1):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]
            
            # Haversine formula for great circle distance
            import math
            R = 6371000  # Earth radius in meters
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_lat / 2) ** 2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            total_distance += R * c
        
        return total_distance
    
    def _calculate_area(self, coordinates: List[Tuple[float, float]]) -> float:
        """Calculate area of a polygon"""
        if len(coordinates) < 3:
            return 0.0
        
        # Shoelace formula for polygon area
        area = 0.0
        n = len(coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[j]
            area += lon1 * lat2
            area -= lon2 * lat1
        
        area = abs(area) / 2.0
        
        # Convert to square meters (approximate)
        return area * 111320 * 111320  # Rough conversion
    
    # Workspace Layout Management
    def save_workspace_layout(self, name: str, description: str = ""):
        """Save current workspace as a named layout"""
        layout = WorkspaceLayout(
            name=name,
            description=description,
            created=datetime.now(),
            modified=datetime.now(),
            panels=[asdict(p) for p in self.panels.values()],
            map_views=[asdict(v) for v in self.map_views.values()],
            active_tab=self.current_layout,
            zen_mode=self.zen_mode
        )
        
        self.workspace_layouts[name] = layout
        self._save_state()
    
    def load_workspace_layout(self, name: str):
        """Load a saved workspace layout"""
        if name in self.workspace_layouts:
            layout = self.workspace_layouts[name]
            
            # Restore panels
            self.panels.clear()
            for panel_data in layout.panels:
                panel = PanelState(**panel_data)
                self.panels[panel.panel_type.value] = panel
                self.panelStateChanged.emit(panel.panel_type.value, asdict(panel))
            
            # Restore map views
            self.map_views.clear()
            for view_data in layout.map_views:
                view = MapViewState(**view_data)
                self.map_views[view.view_id] = view
                self.mapViewStateChanged.emit(view.view_id, asdict(view))
            
            self.current_layout = name
            self.zen_mode = layout.zen_mode
            self.workspaceLayoutChanged.emit(name)
    
    def get_workspace_layouts(self) -> List[dict]:
        """Get all available workspace layouts"""
        return [asdict(layout) for layout in self.workspace_layouts.values()]
    
    def delete_workspace_layout(self, name: str):
        """Delete a workspace layout"""
        if name in self.workspace_layouts:
            del self.workspace_layouts[name]
            self._save_state()
    
    # Zen Mode
    def toggle_zen_mode(self):
        """Toggle zen mode (hide all panels)"""
        self.zen_mode = not self.zen_mode
        
        if self.zen_mode:
            # Hide all panels
            for panel in self.panels.values():
                panel.visible = False
                self.panelStateChanged.emit(panel.panel_type.value, asdict(panel))
        else:
            # Restore panel visibility from current layout
            if self.current_layout and self.current_layout in self.workspace_layouts:
                layout = self.workspace_layouts[self.current_layout]
                for panel_data in layout.panels:
                    panel_type = panel_data['panel_type']
                    if panel_type in self.panels:
                        self.panels[panel_type].visible = panel_data['visible']
                        self.panelStateChanged.emit(panel_type, asdict(self.panels[panel_type]))
    
    # Global Search
    def search(self, query: str) -> List[dict]:
        """Global search across layers, bookmarks, tools, etc."""
        results = []
        
        # Search layers
        for layer_id, layer in self.layers.items():
            if query.lower() in layer.name.lower():
                results.append({
                    "type": "layer",
                    "id": layer_id,
                    "name": layer.name,
                    "description": f"Layer: {layer.name}"
                })
        
        # Search bookmarks
        for bookmark in self.bookmarks:
            if query.lower() in bookmark.name.lower() or query.lower() in bookmark.description.lower():
                results.append({
                    "type": "bookmark",
                    "name": bookmark.name,
                    "description": bookmark.description,
                    "center": bookmark.center,
                    "zoom_level": bookmark.zoom_level
                })
        
        # Search tools
        for tool in ToolType:
            if query.lower() in tool.value.lower():
                results.append({
                    "type": "tool",
                    "name": tool.value,
                    "description": f"Tool: {tool.value}"
                })
        
        return results
    
    # Notifications
    def add_notification(self, notification_type: str, title: str, message: str):
        """Add a notification"""
        self.notificationAdded.emit(notification_type, title, message)
    
    def clear_notifications(self):
        """Clear all notifications"""
        # Implementation would depend on how notifications are stored
        pass
    
    # Task Management
    def add_task(self, task_id: str, description: str):
        """Add a new background task"""
        # This would integrate with the existing progress tracker
        pass
    
    def update_task_progress(self, task_id: str, progress: int, status: str):
        """Update task progress"""
        self.taskProgressUpdated.emit(task_id, progress, status)
    
    def remove_task(self, task_id: str):
        """Remove a completed task"""
        # Implementation would depend on task storage
        pass
    
    # Background task methods
    def _update_coordinate_display(self):
        """Update coordinate display (called by timer)"""
        # This would get mouse coordinates from the map view
        pass
    
    def _monitor_tasks(self):
        """Monitor background tasks (called by timer)"""
        # This would check task status and update progress
        pass
    
    # Utility methods for QML integration
    def get_all_panels(self) -> List[dict]:
        """Get all panel states for QML"""
        return [asdict(panel) for panel in self.panels.values()]
    
    def get_all_map_views(self) -> List[dict]:
        """Get all map view states for QML"""
        return [asdict(view) for view in self.map_views.values()]
    
    def get_all_layers(self) -> List[dict]:
        """Get all layer states for QML"""
        return [asdict(layer) for layer in self.layers.values()]
    
    def get_all_measurements(self) -> List[dict]:
        """Get all measurements for QML"""
        return [asdict(measurement) for measurement in self.measurements]
    
    def get_current_state(self) -> dict:
        """Get complete current state for QML"""
        return {
            "panels": self.get_all_panels(),
            "map_views": self.get_all_map_views(),
            "layers": self.get_all_layers(),
            "bookmarks": self.get_bookmarks(),
            "measurements": self.get_all_measurements(),
            "workspace_layouts": self.get_workspace_layouts(),
            "current_layout": self.current_layout,
            "zen_mode": self.zen_mode,
            "active_tool": self.active_tool.value if self.active_tool else None
        }
