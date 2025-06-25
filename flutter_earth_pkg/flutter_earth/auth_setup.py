"""Authentication setup for Flutter Earth."""
import os
import json
import logging
from typing import Optional, Dict
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property

class AuthManager(QObject):
    """Manages Earth Engine authentication for QML."""
    credentialsChanged = Signal()
    testResult = Signal(bool, str)
    errorOccurred = Signal(str)
    successOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self._project_id = ""
        self._key_file = ""
        # Store auth file in user home directory under .flutter_earth
        home_dir = Path.home()
        config_dir = home_dir / ".flutter_earth"
        config_dir.mkdir(parents=True, exist_ok=True)
        self.auth_file = config_dir / "flutter_earth_auth.json"
        self.txt_file = config_dir / "flutter_earth_auth.txt"
        self.load_credentials()

    def getProjectId(self):
        return self._project_id

    def setProjectId(self, value):
        if self._project_id != value:
            self._project_id = value
            self.credentialsChanged.emit()

    projectId = Property(str, getProjectId, setProjectId, notify=credentialsChanged)  # type: ignore

    def getKeyFile(self):
        return self._key_file

    def setKeyFile(self, value):
        if self._key_file != value:
            self._key_file = value
            self.credentialsChanged.emit()

    keyFile = Property(str, getKeyFile, setKeyFile, notify=credentialsChanged)  # type: ignore

    @Slot()
    def load_credentials(self):
        """Load authentication credentials from text file, JSON config, or environment."""
        print(f"[DEBUG] Loading credentials from: {self.txt_file} or {self.auth_file}")
        env_key_file = os.environ.get("FLUTTER_EARTH_KEY_FILE")
        env_project_id = os.environ.get("FLUTTER_EARTH_PROJECT_ID")
        if env_key_file and os.path.exists(env_key_file):
            self._key_file = env_key_file
            self._project_id = env_project_id or ''
            self.credentialsChanged.emit()
            return
        # Prefer text file if it exists
        if self.txt_file.exists():
            try:
                with open(self.txt_file, 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if line.startswith('project_id='):
                        self._project_id = line.split('=', 1)[1].strip()
                    elif line.startswith('key_file='):
                        self._key_file = line.split('=', 1)[1].strip()
                self.credentialsChanged.emit()
                return
            except Exception as e:
                self.logger.warning(f"Failed to load auth from txt: {e}")
        # Fallback to JSON config
        if self.auth_file.exists():
            try:
                with open(self.auth_file, 'r') as f:
                    config = json.load(f)
                self._project_id = config.get('project_id', '')
                self._key_file = config.get('key_file', '')
                self.credentialsChanged.emit()
            except Exception as e:
                self.logger.warning(f"Failed to load existing auth settings: {e}")
                self._project_id = ''
                self._key_file = ''
                self.credentialsChanged.emit()

    @Slot(str, str)
    def save_credentials(self, project_id, key_file):
        """Save authentication credentials to both JSON and text file, but do not copy the key file."""
        config = {
            'project_id': project_id.strip(),
            'key_file': key_file.strip()
        }
        try:
            # Save JSON config
            with open(self.auth_file, 'w') as f:
                json.dump(config, f, indent=2)
            # Save text file
            with open(self.txt_file, 'w') as txtf:
                txtf.write(f"project_id={config['project_id']}\nkey_file={config['key_file']}\n")
            self._project_id = config['project_id']
            self._key_file = config['key_file']
            self.credentialsChanged.emit()
            self.successOccurred.emit("Authentication settings saved.")
            self.load_credentials()  # Always reload after saving
        except Exception as e:
            print(f"[ERROR] Failed to save auth settings: {e}")
            self.logger.error(f"Failed to save auth settings: {e}")
            self.errorOccurred.emit(f"Failed to save auth settings: {e}")

    @Slot(str, str)
    def test_connection(self, project_id, key_file):
        """Test the Earth Engine connection with provided credentials."""
        if not project_id or not key_file:
            self.testResult.emit(False, "Please provide both Project ID and Key File path.")
            return
        if not os.path.exists(key_file):
            self.testResult.emit(False, f"The key file was not found: {key_file}")
            return
        try:
            import ee  # type: ignore
            credentials = ee.ServiceAccountCredentials('', key_file)  # type: ignore
            ee.Initialize(credentials, project=project_id)  # type: ignore
            test_image = ee.Image('USGS/SRTMGL1_003')  # type: ignore
            _ = test_image.geometry().bounds().getInfo()  # type: ignore
            self.testResult.emit(True, "Authentication completed successfully.")
        except Exception as e:
            self.testResult.emit(False, f"Earth Engine connection test failed: {str(e)}")

    @Slot(result=bool)
    def has_credentials(self):
        return bool(self._project_id and self._key_file and os.path.exists(self._key_file))

    @Slot(result=dict)
    def get_credentials(self):
        return {
            'project_id': self._project_id,
            'key_file': self._key_file
        }

    def setup_credentials(self, parent=None):
        """Interactive setup of credentials. Returns credentials dict if successful, None otherwise."""
        try:
            # For now, just return existing credentials if they exist
            if self.has_credentials():
                return self.get_credentials()
            
            # If no credentials exist, return None to allow the app to continue
            # In a full implementation, this would show a dialog for credential setup
            self.logger.warning("No credentials found. Please set up Earth Engine authentication manually.")
            return None
        except Exception as e:
            self.logger.error(f"Error in setup_credentials: {e}")
            return None

    def initialize_earth_engine(self, parent=None):
        """Initialize Earth Engine with current credentials. Returns True if successful."""
        try:
            if not self.has_credentials():
                return False
            
            import ee  # type: ignore
            credentials = ee.ServiceAccountCredentials('', self._key_file)  # type: ignore
            ee.Initialize(credentials, project=self._project_id)  # type: ignore
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Earth Engine: {e}")
            return False 