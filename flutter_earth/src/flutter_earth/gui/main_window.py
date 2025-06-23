"""Main window for Flutter Earth application."""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, QObject

from ..core.config_manager import ConfigManager
from ..core.earth_engine_manager import EarthEngineManager
from ..core.download_manager import DownloadManager
from ..core.progress_tracker import ProgressTracker
from .qml_engine import QMLEngine


class FlutterEarthBridge(QObject):
    """Bridge between QML and Python backend."""
    
    # Signals to QML
    progress_updated = pyqtSignal(str, float)  # task_id, progress
    status_updated = pyqtSignal(str, str)      # task_id, status
    task_completed = pyqtSignal(str, bool)     # task_id, success
    earth_engine_status_changed = pyqtSignal(bool)  # initialized
    showMessage = pyqtSignal(str, str, str)  # type, title, text
    
    # New UI signals
    updateStatusBar = pyqtSignal(str)  # status message
    updateProgress = pyqtSignal(str, float)  # progress_type, value (0-100)
    updateWindowTitle = pyqtSignal(str)  # new title
    showFileDialog = pyqtSignal(str, str)  # dialog_type, title
    fileDialogResult = pyqtSignal(str, str)  # dialog_type, selected_path
    showInputDialog = pyqtSignal(str, str, str)  # dialog_type, title, default_value
    inputDialogResult = pyqtSignal(str, str)  # dialog_type, result
    
    def __init__(self, config_manager: ConfigManager, earth_engine_manager: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker):
        """Initialize the bridge.
        
        Args:
            config_manager: Configuration manager.
            earth_engine_manager: Earth Engine manager.
            download_manager: Download manager.
            progress_tracker: Progress tracker.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__)
        
        self.config_manager = config_manager
        self.earth_engine_manager = earth_engine_manager
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks for managers."""
        # Download manager callbacks
        self.download_manager.set_progress_callback(self._on_progress_update)
        self.download_manager.set_status_callback(self._on_status_update)
        self.download_manager.set_completion_callback(self._on_task_completion)
    
    def _on_progress_update(self, task_id: str, progress: float) -> None:
        """Handle progress updates.
        
        Args:
            task_id: Task ID.
            progress: Progress value.
        """
        self.progress_updated.emit(task_id, progress)
    
    def _on_status_update(self, task_id: str, status) -> None:
        """Handle status updates.
        
        Args:
            task_id: Task ID.
            status: Status message.
        """
        # Convert status to string if it's a DownloadStatus enum
        status_str = str(status) if hasattr(status, 'value') else str(status)
        self.status_updated.emit(task_id, status_str)
    
    def _on_task_completion(self, task_id: str, result) -> None:
        """Handle task completion.
        
        Args:
            task_id: Task ID.
            result: Processing result.
        """
        self.task_completed.emit(task_id, result.success)
    
    # QML callable methods
    def initialize_earth_engine(self) -> bool:
        """Initialize Earth Engine.
        
        Returns:
            True if initialization was successful.
        """
        try:
            success = self.earth_engine_manager.initialize()
            self.earth_engine_status_changed.emit(success)
            return success
        except Exception as e:
            self._logger.error(f"Failed to initialize Earth Engine: {e}")
            return False
    
    def get_satellite_collections(self) -> list:
        """Get available satellite collections.
        
        Returns:
            List of satellite collections.
        """
        collections = self.earth_engine_manager.get_collections()
        return [
            {
                "name": name,
                "display_name": collection.display_name,
                "description": collection.description,
                "spatial_resolution": collection.spatial_resolution,
                "temporal_resolution": collection.temporal_resolution,
                "bands": collection.bands
            }
            for name, collection in collections.items()
        ]
    
    def start_download(self, params: dict) -> str:
        """Start a download task.
        
        Args:
            params: Processing parameters.
            
        Returns:
            Task ID.
        """
        try:
            # Convert params to ProcessingParams object
            from ..core.types import ProcessingParams, BoundingBox, OutputFormat, VegetationIndex
            from datetime import datetime
            
            # Parse area of interest
            if "bbox" in params:
                bbox_data = params["bbox"]
                area = BoundingBox(
                    min_lon=bbox_data["min_lon"],
                    min_lat=bbox_data["min_lat"],
                    max_lon=bbox_data["max_lon"],
                    max_lat=bbox_data["max_lat"]
                )
            else:
                # Handle polygon case
                from ..core.types import Polygon, Coordinates
                coords = [Coordinates(lon, lat) for lon, lat in params["polygon"]]
                area = Polygon(coords)
            
            # Parse dates
            start_date = datetime.fromisoformat(params["start_date"])
            end_date = datetime.fromisoformat(params["end_date"])
            
            # Parse output format
            output_format = OutputFormat(params["output_format"])
            
            # Parse vegetation indices
            vegetation_indices = [VegetationIndex(idx) for idx in params.get("vegetation_indices", [])]
            
            # Create ProcessingParams
            processing_params = ProcessingParams(
                area_of_interest=area,
                start_date=start_date,
                end_date=end_date,
                satellite_collections=params["satellite_collections"],
                output_format=output_format,
                spatial_resolution=params.get("spatial_resolution"),
                max_cloud_cover=params.get("max_cloud_cover", 20.0),
                vegetation_indices=vegetation_indices,
                output_directory=Path(params["output_directory"]) if params.get("output_directory") else None,
                filename_prefix=params.get("filename_prefix", "flutter_earth")
            )
            
            # Start download
            task_id = self.download_manager.add_task(processing_params)
            
            # Start progress tracking
            self.progress_tracker.start_tracking(task_id)
            
            return task_id
            
        except Exception as e:
            self._logger.error(f"Failed to start download: {e}")
            raise
    
    def cancel_download(self, task_id: str) -> bool:
        """Cancel a download task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            True if task was cancelled.
        """
        try:
            success = self.download_manager.cancel_task(task_id)
            if success:
                self.progress_tracker.stop_tracking(task_id)
            return success
        except Exception as e:
            self._logger.error(f"Failed to cancel download: {e}")
            return False
    
    def get_config(self, key: str):
        """Get configuration value.
        
        Args:
            key: Configuration key.
            
        Returns:
            Configuration value.
        """
        return self.config_manager.get(key)
    
    def set_config(self, key: str, value) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value.
        """
        self.config_manager.set(key, value)
    
    # QML callable methods for UI interactions
    def show_file_dialog(self, dialog_type: str, title: str) -> None:
        """Show a file dialog.
        
        Args:
            dialog_type: Type of dialog ("open" or "save").
            title: Dialog title.
        """
        try:
            from PyQt6.QtWidgets import QFileDialog, QWidget
            
            # Create a temporary widget for the dialog
            parent = QWidget()
            
            if dialog_type == "open":
                file_path, _ = QFileDialog.getOpenFileName(
                    parent, title, "", "All Files (*.*)"
                )
            elif dialog_type == "save":
                file_path, _ = QFileDialog.getSaveFileName(
                    parent, title, "", "All Files (*.*)"
                )
            elif dialog_type == "directory":
                file_path = QFileDialog.getExistingDirectory(parent, title)
            else:
                self._logger.error(f"Unknown dialog type: {dialog_type}")
                return
            
            if file_path:
                self.fileDialogResult.emit(dialog_type, file_path)
                
        except Exception as e:
            self._logger.error(f"Failed to show file dialog: {e}")
    
    def show_input_dialog(self, dialog_type: str, title: str, default_value: str = "") -> None:
        """Show an input dialog.
        
        Args:
            dialog_type: Type of dialog ("text", "number", "password").
            title: Dialog title.
            default_value: Default value.
        """
        try:
            from PyQt6.QtWidgets import QInputDialog, QWidget
            
            # Create a temporary widget for the dialog
            parent = QWidget()
            
            if dialog_type == "text":
                text, ok = QInputDialog.getText(parent, title, "Enter value:", text=default_value)
            elif dialog_type == "number":
                number, ok = QInputDialog.getInt(parent, title, "Enter number:", int(default_value) if default_value else 0)
                text = str(number) if ok else ""
            elif dialog_type == "password":
                text, ok = QInputDialog.getText(parent, title, "Enter password:", QInputDialog.Password, default_value)
            else:
                self._logger.error(f"Unknown dialog type: {dialog_type}")
                return
            
            if ok and text:
                self.inputDialogResult.emit(dialog_type, text)
                
        except Exception as e:
            self._logger.error(f"Failed to show input dialog: {e}")
    
    def log_message(self, message: str) -> None:
        """Log a message to the console.
        
        Args:
            message: Message to log.
        """
        self._logger.info(f"QML Log: {message}")
    
    def get_application_info(self) -> dict:
        """Get application information.
        
        Returns:
            Dictionary with application info.
        """
        return {
            "name": "Flutter Earth",
            "version": "1.0.0",
            "description": "A modern tool for downloading and processing satellite imagery"
        }


class FlutterEarthMainWindow(QObject):
    """Main window manager for Flutter Earth application."""
    
    def __init__(self, config_manager: ConfigManager, earth_engine_manager: EarthEngineManager,
                 download_manager: DownloadManager, progress_tracker: ProgressTracker):
        """Initialize the main window.
        
        Args:
            config_manager: Configuration manager.
            earth_engine_manager: Earth Engine manager.
            download_manager: Download manager.
            progress_tracker: Progress tracker.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__)
        
        # Store managers
        self.config_manager = config_manager
        self.earth_engine_manager = earth_engine_manager
        self.download_manager = download_manager
        self.progress_tracker = progress_tracker
        
        # Create bridge
        self.bridge = FlutterEarthBridge(
            config_manager, earth_engine_manager, download_manager, progress_tracker
        )
        
        # Setup QML
        self._setup_qml()
        
        # Start download manager
        self.download_manager.start()
    
    def _setup_qml(self) -> None:
        """Setup QML engine and load main QML file."""
        try:
            # Create QML engine
            self.qml_engine = QMLEngine()
            
            # Add QML directory to import path
            qml_dir = Path(__file__).parent / "qml"
            self.qml_engine.add_import_path(str(qml_dir))
            
            # Register bridge
            self.qml_engine.root_context().setContextProperty("flutterEarth", self.bridge)
            
            # Load main QML file
            qml_file = Path(__file__).parent / "qml" / "main.qml"
            if qml_file.exists():
                success = self.qml_engine.load(str(qml_file))
                if success:
                    self._logger.info("QML interface loaded successfully")
                    # Update window title
                    self.bridge.updateWindowTitle.emit("Flutter Earth")
                else:
                    self._logger.error(f"Failed to load QML file: {qml_file}")
            else:
                self._logger.error(f"QML file not found: {qml_file}")
                
        except Exception as e:
            self._logger.error(f"Failed to setup QML: {e}")
    
    def show(self) -> None:
        """Show the window (no-op since QML manages the window)."""
        pass
    
    def hide(self) -> None:
        """Hide the window (no-op since QML manages the window)."""
        pass
    
    def close(self) -> None:
        """Close the application."""
        try:
            # Stop download manager
            self.download_manager.stop()
            
            # Clear progress tracking
            self.progress_tracker.clear_all()
            
            # Quit QML engine
            if hasattr(self, 'qml_engine'):
                self.qml_engine.quit()
            
            self._logger.info("Flutter Earth application closing")
            
        except Exception as e:
            self._logger.error(f"Error during application shutdown: {e}") 