"""Authentication setup for Flutter Earth."""
import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

class AuthSetupDialog(QtWidgets.QDialog):
    """Dialog for setting up Earth Engine authentication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.project_id = ""
        self.key_file_path = ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Earth Engine Authentication Setup")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout()
        
        # Header
        header_label = QtWidgets.QLabel("Earth Engine Authentication Required")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QtWidgets.QLabel(
            "Flutter Earth requires Google Earth Engine access. Please provide your "
            "Google Cloud project ID and service account key file."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin: 10px;")
        layout.addWidget(desc_label)
        
        # Project ID section
        project_group = QtWidgets.QGroupBox("Google Cloud Project")
        project_layout = QtWidgets.QVBoxLayout()
        
        project_label = QtWidgets.QLabel("Project ID:")
        self.project_edit = QtWidgets.QLineEdit()
        self.project_edit.setPlaceholderText("e.g., my-earth-engine-project")
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_edit)
        
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # Key file section
        key_group = QtWidgets.QGroupBox("Service Account Key File")
        key_layout = QtWidgets.QVBoxLayout()
        
        key_label = QtWidgets.QLabel("Service Account Key File (JSON):")
        key_layout.addWidget(key_label)
        
        key_file_layout = QtWidgets.QHBoxLayout()
        self.key_file_edit = QtWidgets.QLineEdit()
        self.key_file_edit.setPlaceholderText("Path to your service account key file")
        self.browse_button = QtWidgets.QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_key_file)
        key_file_layout.addWidget(self.key_file_edit)
        key_file_layout.addWidget(self.browse_button)
        key_layout.addLayout(key_file_layout)
        
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.help_button = QtWidgets.QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        
        self.test_button = QtWidgets.QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        
        self.save_button = QtWidgets.QPushButton("Save & Continue")
        self.save_button.clicked.connect(self.accept)
        self.save_button.setDefault(True)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.help_button)
        button_layout.addStretch()
        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Load existing settings
        self.load_existing_settings()
        
    def browse_key_file(self):
        """Open file dialog to select key file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Service Account Key File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.key_file_edit.setText(file_path)
            
    def show_help(self):
        """Show help dialog with setup instructions."""
        help_dialog = AuthHelpDialog(self)
        help_dialog.exec_()
        
    def test_connection(self):
        """Test the Earth Engine connection with provided credentials."""
        project_id = self.project_edit.text().strip()
        key_file = self.key_file_edit.text().strip()
        
        if not project_id or not key_file:
            QtWidgets.QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide both Project ID and Key File path."
            )
            return
            
        if not os.path.exists(key_file):
            QtWidgets.QMessageBox.warning(
                self,
                "File Not Found",
                f"The key file was not found:\n{key_file}"
            )
            return
            
        try:
            # Test Earth Engine connection
            import ee
            from ee import data as ee_data
            
            # Set credentials
            credentials = ee.ServiceAccountCredentials('', key_file)
            ee.Initialize(credentials, project=project_id)
            
            # Test basic functionality
            test_image = ee.Image('USGS/SRTMGL1_003')
            bounds = test_image.geometry().bounds().getInfo()
            
            QtWidgets.QMessageBox.information(
                self,
                "Connection Successful",
                f"Earth Engine connection test successful!\n\n"
                f"Project ID: {project_id}\n"
                f"Test image bounds: {bounds}"
            )
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Connection Failed",
                f"Earth Engine connection test failed:\n\n{str(e)}\n\n"
                "Please check your credentials and try again."
            )
            
    def load_existing_settings(self):
        """Load existing authentication settings, but only if they are valid."""
        config_file = Path("flutter_earth_auth.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Set project ID if it exists
                self.project_edit.setText(config.get('project_id', ''))
                
                # Only set key file path if it exists, otherwise leave it blank
                key_file_path = config.get('key_file', '')
                if key_file_path and os.path.exists(key_file_path):
                    self.key_file_edit.setText(key_file_path)
                else:
                    # If path is invalid, clear it to not show the user
                    self.key_file_edit.clear()

            except Exception as e:
                self.logger.warning(f"Failed to load existing auth settings: {e}")
                self.project_edit.clear()
                self.key_file_edit.clear()
                
    def save_settings(self):
        """Save authentication settings."""
        config = {
            'project_id': self.project_edit.text().strip(),
            'key_file': self.key_file_edit.text().strip()
        }
        
        try:
            with open("flutter_earth_auth.json", 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info("Authentication settings saved")
        except Exception as e:
            self.logger.error(f"Failed to save auth settings: {e}")
            
    def get_credentials(self) -> Dict[str, str]:
        """Get the entered credentials."""
        return {
            'project_id': self.project_edit.text().strip(),
            'key_file': self.key_file_edit.text().strip()
        }
        
    def accept(self):
        """Handle dialog acceptance."""
        credentials = self.get_credentials()
        
        if not credentials['project_id'] or not credentials['key_file']:
            QtWidgets.QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide both Project ID and Key File path."
            )
            return
            
        if not os.path.exists(credentials['key_file']):
            QtWidgets.QMessageBox.warning(
                self,
                "File Not Found",
                f"The key file was not found:\n{credentials['key_file']}"
            )
            return
            
        # Save settings
        self.save_settings()
        super().accept()


class AuthHelpDialog(QtWidgets.QDialog):
    """Help dialog with Earth Engine setup instructions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Earth Engine Setup Help")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the help interface."""
        layout = QtWidgets.QVBoxLayout()
        
        # Title
        title = QtWidgets.QLabel("Earth Engine Setup Instructions")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Text area with instructions
        self.text_area = QtWidgets.QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setHtml(self.get_help_text())
        layout.addWidget(self.text_area)
        
        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
    def get_help_text(self) -> str:
        """Get the help text content."""
        return """
        <h2>Setting up Google Earth Engine Access</h2>
        
        <h3>Step 1: Sign up for Earth Engine</h3>
        <ol>
            <li>Visit <a href="https://developers.google.com/earth-engine/guides/access">https://developers.google.com/earth-engine/guides/access</a></li>
            <li>Click "Sign up for Earth Engine"</li>
            <li>Fill out the application form</li>
            <li>Wait for approval (usually 1-2 business days)</li>
        </ol>
        
        <h3>Step 2: Create a Google Cloud Project</h3>
        <ol>
            <li>Go to <a href="https://console.cloud.google.com/">https://console.cloud.google.com/</a></li>
            <li>Click "Select a project" → "New Project"</li>
            <li>Give your project a name (e.g., "flutter-earth-project")</li>
            <li>Click "Create"</li>
        </ol>
        
        <h3>Step 3: Enable Earth Engine API</h3>
        <ol>
            <li>In your Google Cloud project, go to "APIs & Services" → "Library"</li>
            <li>Search for "Earth Engine API"</li>
            <li>Click on "Earth Engine API"</li>
            <li>Click "Enable"</li>
        </ol>
        
        <h3>Step 4: Create a Service Account</h3>
        <ol>
            <li>In your Google Cloud project, go to "IAM & Admin" → "Service Accounts"</li>
            <li>Click "Create Service Account"</li>
            <li>Give it a name (e.g., "flutter-earth-service")</li>
            <li>Click "Create and Continue"</li>
            <li>For roles, add "Earth Engine Resource Viewer" and "Earth Engine Resource User"</li>
            <li>Click "Done"</li>
        </ol>
        
        <h3>Step 5: Create and Download Key File</h3>
        <ol>
            <li>Click on your service account name</li>
            <li>Go to the "Keys" tab</li>
            <li>Click "Add Key" → "Create new key"</li>
            <li>Choose "JSON" format</li>
            <li>Click "Create" - this will download a JSON file</li>
            <li>Save this file securely (this is your key file)</li>
        </ol>
        
        <h3>Step 6: Configure Flutter Earth</h3>
        <ol>
            <li>Enter your Project ID (found in Google Cloud Console)</li>
            <li>Click "Browse" and select your downloaded JSON key file</li>
            <li>Click "Test Connection" to verify everything works</li>
            <li>Click "Save & Continue" to save your settings</li>
        </ol>
        
        <h3>Important Notes</h3>
        <ul>
            <li><strong>Keep your key file secure</strong> - don't share it or commit it to version control</li>
            <li><strong>Project ID</strong> is different from Project Name - it's usually in the format "project-name-123456"</li>
            <li><strong>Service accounts</strong> are the recommended way to authenticate for applications</li>
            <li>If you get permission errors, make sure your service account has the correct roles</li>
        </ul>
        
        <h3>Getting Help</h3>
        <p>If you're still having issues:</p>
        <ul>
            <li>Check the <a href="https://developers.google.com/earth-engine">Earth Engine documentation</a></li>
            <li>Visit the <a href="https://groups.google.com/g/google-earth-engine-developers">Earth Engine forum</a></li>
            <li>Make sure your Earth Engine access has been approved</li>
        </ul>
        """


class AuthManager:
    """Manages Earth Engine authentication."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auth_file = Path("flutter_earth_auth.json")
    
    def has_credentials(self) -> bool:
        """Check if authentication credentials exist."""
        return self.auth_file.exists()
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load authentication credentials, preferring environment variable if set."""
        # 1. Check environment variable for key file
        env_key_file = os.environ.get("FLUTTER_EARTH_KEY_FILE")
        env_project_id = os.environ.get("FLUTTER_EARTH_PROJECT_ID")
        if env_key_file and os.path.exists(env_key_file):
            self.logger.info("Loading Earth Engine credentials from environment variables.")
            return {
                'project_id': env_project_id or '',
                'key_file': env_key_file
            }

        # 2. Fallback to config file
        if not self.has_credentials():
            return None
        
        try:
            with open(self.auth_file, 'r') as f:
                config = json.load(f)
            
            key_file = config.get('key_file', '')
            project_id = config.get('project_id', '')

            if not key_file:
                self.logger.info("Earth Engine key file not configured in auth file. User will be prompted.")
                return None

            if os.path.exists(key_file):
                return {'project_id': project_id, 'key_file': key_file}
            else:
                self.logger.warning(
                    "The configured Earth Engine key file was not found at its stored path. "
                    "It may have been moved or deleted. Please select the file again."
                )
                return None
        except Exception as e:
            self.logger.error(f"Failed to load credentials from auth file: {e}")
            return None
    
    def setup_credentials(self, parent=None) -> Optional[Dict[str, str]]:
        """Show setup dialog and return credentials if successful."""
        from PySide6 import QtWidgets
        if QtWidgets.QApplication.instance() is None:
            raise RuntimeError("QApplication must be created before showing authentication dialogs. Please ensure QApplication is initialized before calling setup_credentials.")
        dialog = AuthSetupDialog(parent)
        if dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            return dialog.get_credentials()
        return None
    
    def initialize_earth_engine(self, parent=None) -> bool:
        """Initialize Earth Engine with stored or new credentials."""
        try:
            import ee
            from ee import data as ee_data
            
            # Try to load existing credentials
            credentials = self.load_credentials()
            
            if not credentials:
                # Show setup dialog
                credentials = self.setup_credentials(parent)
                if not credentials:
                    QtWidgets.QMessageBox.critical(
                        parent,
                        "Earth Engine Authentication Required",
                        "No valid Earth Engine key file found. Please provide your service account key file."
                    )
                    return False
            # Initialize with credentials
            service_account_creds = ee.ServiceAccountCredentials('', credentials['key_file'])
            ee.Initialize(service_account_creds, project=credentials['project_id'])
            # Test connection
            test_image = ee.Image('USGS/SRTMGL1_003')
            bounds = test_image.geometry().bounds().getInfo()
            self.logger.info("Earth Engine initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Earth Engine: {e}")
            if parent:
                QtWidgets.QMessageBox.critical(
                    parent,
                    "Earth Engine Initialization Failed",
                    f"Failed to initialize Earth Engine:\n\n{str(e)}\n\nPlease check your credentials and try again."
                )
            return False 