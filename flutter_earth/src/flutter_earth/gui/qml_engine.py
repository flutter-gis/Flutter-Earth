"""QML engine wrapper for Flutter Earth."""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtQml import QQmlApplicationEngine


class QMLEngine:
    """QML engine wrapper for Flutter Earth."""
    
    def __init__(self, parent=None):
        """Initialize the QML engine.
        
        Args:
            parent: Parent widget (optional).
        """
        self._logger = logging.getLogger(__name__)
        self._parent = parent
        self._engine: Optional[QQmlApplicationEngine] = None
        
        self._setup_engine()
    
    def _setup_engine(self) -> None:
        """Setup the QML engine."""
        try:
            # Create QML application engine
            self._engine = QQmlApplicationEngine()
            
            self._logger.debug("QML engine setup completed")
            
        except Exception as e:
            self._logger.error(f"Failed to setup QML engine: {e}")
            raise
    
    def load(self, qml_file: str) -> bool:
        """Load a QML file.
        
        Args:
            qml_file: Path to QML file.
            
        Returns:
            True if loading was successful.
        """
        try:
            if not Path(qml_file).exists():
                self._logger.error(f"QML file not found: {qml_file}")
                return False
            
            # Load QML file
            url = QUrl.fromLocalFile(qml_file)
            self._engine.load(url)
            
            # Check for errors
            if self._engine.rootObjects():
                self._logger.info(f"QML file loaded successfully: {qml_file}")
                return True
            else:
                self._logger.error(f"Failed to load QML file: {qml_file}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error loading QML file: {e}")
            return False
    
    def load_url(self, url: str) -> bool:
        """Load QML from URL.
        
        Args:
            url: QML URL.
            
        Returns:
            True if loading was successful.
        """
        try:
            qml_url = QUrl(url)
            self._engine.load(qml_url)
            
            if self._engine.rootObjects():
                self._logger.info(f"QML URL loaded successfully: {url}")
                return True
            else:
                self._logger.error(f"Failed to load QML URL: {url}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error loading QML URL: {e}")
            return False
    
    def root_context(self):
        """Get the root context.
        
        Returns:
            Root context.
        """
        return self._engine.rootContext()
    
    def root_objects(self):
        """Get root objects.
        
        Returns:
            List of root objects.
        """
        return self._engine.rootObjects()
    
    def add_import_path(self, path: str) -> None:
        """Add import path.
        
        Args:
            path: Import path.
        """
        self._engine.addImportPath(path)
    
    def set_import_path_list(self, paths: list) -> None:
        """Set import path list.
        
        Args:
            paths: List of import paths.
        """
        self._engine.setImportPathList(paths)
    
    def clear_component_cache(self) -> None:
        """Clear component cache."""
        self._engine.clearComponentCache()
    
    def quit(self) -> None:
        """Quit the QML engine."""
        if self._engine:
            self._engine.quit() 