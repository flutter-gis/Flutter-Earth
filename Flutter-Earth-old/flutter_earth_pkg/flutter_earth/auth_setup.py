"""Authentication setup for Flutter Earth."""
import os
import json
import logging
import shutil
from typing import Optional, Dict, Tuple
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property
import sys

class AuthManager(QObject):
    """Manages Earth Engine authentication for Flutter Earth."""
    credentialsChanged = Signal()
    testResult = Signal(bool, str)
    errorOccurred = Signal(str)
    successOccurred = Signal(str)
    authStatusChanged = Signal(bool)  # True if authenticated, False if not

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._project_id = ""
        self._key_file = ""
        self._is_authenticated = False
        
        # Create FE Auth directory
        self.fe_auth_dir = self._get_fe_auth_directory()
        self.fe_auth_dir.mkdir(parents=True, exist_ok=True)
        
        # Auth file paths
        self.auth_config_file = self.fe_auth_dir / "auth_config.json"
        self.auth_status_file = self.fe_auth_dir / "auth_status.json"
        
        # Load credentials on initialization
        self.load_credentials()
        self._update_auth_status()

    def _get_fe_auth_directory(self) -> Path:
        """Get the FE Auth directory path based on the operating system."""
        if sys.platform == "win32":
            return Path("C:/FE Auth")
        elif sys.platform == "darwin":
            return Path.home() / "FE Auth"
        else:
            return Path.home() / "FE Auth"

    def getProjectId(self):
        return self._project_id

    def setProjectId(self, value):
        if self._project_id != value:
            self._project_id = value
            self.credentialsChanged.emit()

    projectId = Property(str, getProjectId, setProjectId, notify=credentialsChanged)

    def getKeyFile(self):
        return self._key_file

    def setKeyFile(self, value):
        if self._key_file != value:
            self._key_file = value
            self.credentialsChanged.emit()

    keyFile = Property(str, getKeyFile, setKeyFile, notify=credentialsChanged)

    @Slot()
    def load_credentials(self):
        """Load authentication credentials from the centralized auth config."""
        self.logger.debug(f"Loading credentials from: {self.auth_config_file}")
        
        # Try to load from auth config file
        if self.auth_config_file.exists():
            try:
                with open(self.auth_config_file, 'r') as f:
                    config = json.load(f)
                
                self._project_id = config.get('project_id', '')
                self._key_file = config.get('key_file', '')
                
                # Verify the key file still exists
                if self._key_file and not Path(self._key_file).exists():
                    self.logger.warning(f"Key file not found: {self._key_file}")
                    self._project_id = ""
                    self._key_file = ""
                
                self.credentialsChanged.emit()
                self.logger.debug(f"Loaded credentials: project={self._project_id}, key={self._key_file}")
                return
                
            except Exception as e:
                self.logger.error(f"Failed to load auth config: {e}")
        
        # Fallback to environment variables
        env_key_file = os.environ.get("FLUTTER_EARTH_KEY_FILE")
        env_project_id = os.environ.get("FLUTTER_EARTH_PROJECT_ID")
        
        if env_key_file and os.path.exists(env_key_file):
            self._key_file = env_key_file
            self._project_id = env_project_id or ''
            self.credentialsChanged.emit()
            self.logger.debug(f"Loaded from environment: project={self._project_id}, key={self._key_file}")
            return
        
        # No credentials found
        self._project_id = ""
        self._key_file = ""
        self.credentialsChanged.emit()
        self.logger.debug("No credentials found")

    @Slot(str, str)
    def save_credentials(self, project_id: str, key_file: str):
        """Save authentication credentials to the centralized auth system."""
        project_id = project_id.strip()
        key_file = key_file.strip()
        
        if not project_id or not key_file:
            self.errorOccurred.emit("Project ID and Key File are required.")
            return
            
        if not os.path.exists(key_file):
            self.errorOccurred.emit(f"The key file was not found: {key_file}")
            return
            
        try:
            # Copy the JSON key file to FE Auth folder
            source_key_path = Path(key_file)
            dest_key_path = self.fe_auth_dir / f"service_account_key.json"
            
            # If the file already exists, remove it first
            if dest_key_path.exists():
                dest_key_path.unlink()
                
            # Copy the file
            shutil.copy2(source_key_path, dest_key_path)
            
            # Save auth config
            config = {
                'project_id': project_id,
                'key_file': str(dest_key_path),
                'created_at': str(Path().cwd()),
                'version': '2.0'
            }
            
            with open(self.auth_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update internal state
            self._project_id = project_id
            self._key_file = str(dest_key_path)
            self.credentialsChanged.emit()
            
            # Update auth status
            self._update_auth_status()
            
            self.successOccurred.emit(f"Authentication settings saved successfully.")
            self.logger.info(f"Credentials saved: project={project_id}, key={dest_key_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save auth settings: {e}")
            self.errorOccurred.emit(f"Failed to save auth settings: {e}")

    def _update_auth_status(self):
        """Update the authentication status."""
        was_authenticated = self._is_authenticated
        self._is_authenticated = self.has_credentials()
        
        if was_authenticated != self._is_authenticated:
            self.authStatusChanged.emit(self._is_authenticated)
            
        # Save auth status
        status_data = {
            'is_authenticated': self._is_authenticated,
            'project_id': self._project_id,
            'last_updated': str(Path().cwd())
        }
        
        try:
            with open(self.auth_status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save auth status: {e}")

    @Slot(result=bool)
    def needs_authentication(self):
        """Check if authentication is needed."""
        return not self.has_credentials()

    @Slot(str, str)
    def test_connection(self, project_id: str, key_file: str):
        """Test the Earth Engine connection with provided credentials."""
        if not project_id or not key_file:
            self.testResult.emit(False, "Please provide both Project ID and Key File path.")
            return
            
        if not os.path.exists(key_file):
            self.testResult.emit(False, f"The key file was not found: {key_file}")
            return
            
        try:
            # Check if this is a test project
            if project_id == 'test-project-123':
                self.testResult.emit(False, "Test credentials detected. Please use real Google Cloud credentials for Earth Engine access.")
                return
            
            import ee
            credentials = ee.ServiceAccountCredentials('', key_file)
            ee.Initialize(credentials, project=project_id)
            
            # Test with a simple image
            test_image = ee.Image('USGS/SRTMGL1_003')
            _ = test_image.geometry().bounds().getInfo()
            
            self.testResult.emit(True, "Authentication test completed successfully.")
            self.logger.info("Earth Engine connection test successful")
            
        except Exception as e:
            error_msg = f"Earth Engine connection test failed: {str(e)}"
            self.testResult.emit(False, error_msg)
            self.logger.error(f"Earth Engine connection test failed: {e}")

    @Slot(result=bool)
    def has_credentials(self):
        """Check if valid credentials are available."""
        return bool(
            self._project_id and 
            self._key_file and 
            os.path.exists(self._key_file)
        )

    @Slot(result=dict)
    def get_credentials(self):
        """Get current credentials."""
        return {
            'project_id': self._project_id,
            'key_file': self._key_file
        }

    @Slot(result=bool)
    def is_authenticated(self):
        """Check if currently authenticated."""
        return self._is_authenticated

    def initialize_earth_engine(self) -> Tuple[bool, str]:
        """Initialize Earth Engine with current credentials.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.has_credentials():
                return False, "No valid credentials found"
            
            # Check if this is a test project
            if self._project_id == 'test-project-123':
                return False, "Test credentials detected. Please set up real Google Cloud credentials for Earth Engine access."
            
            import ee
            credentials = ee.ServiceAccountCredentials('', self._key_file)
            ee.Initialize(credentials, project=self._project_id)
            
            # Test the connection
            test_image = ee.Image('USGS/SRTMGL1_003')
            _ = test_image.geometry().bounds().getInfo()
            
            self._update_auth_status()
            self.logger.info("Earth Engine initialized successfully")
            return True, "Earth Engine initialized successfully"
            
        except Exception as e:
            error_msg = f"Failed to initialize Earth Engine: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    def clear_credentials(self):
        """Clear all stored credentials."""
        try:
            # Remove auth files
            if self.auth_config_file.exists():
                self.auth_config_file.unlink()
            if self.auth_status_file.exists():
                self.auth_status_file.unlink()
            
            # Clear internal state
            self._project_id = ""
            self._key_file = ""
            self._is_authenticated = False
            
            self.credentialsChanged.emit()
            self._update_auth_status()
            
            self.logger.info("Credentials cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear credentials: {e}")
            return False

    def get_auth_info(self) -> Dict:
        """Get comprehensive authentication information."""
        return {
            'is_authenticated': self._is_authenticated,
            'has_credentials': self.has_credentials(),
            'project_id': self._project_id,
            'key_file': self._key_file,
            'auth_dir': str(self.fe_auth_dir),
            'config_file': str(self.auth_config_file),
            'status_file': str(self.auth_status_file)
        } 