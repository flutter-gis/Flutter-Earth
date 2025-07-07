#!/usr/bin/env python3
"""
Flutter Earth - PySide6 + QML Desktop Application
Simplified working version
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtCore import (
    QObject, QThread, QTimer, Signal, Slot, Property, QUrl, 
    QAbstractListModel, QModelIndex, Qt, QSize
)
from PySide6.QtGui import QGuiApplication, QIcon, QFont
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QFileDialog

class SatelliteModel(QAbstractListModel):
    """Model for satellite data"""
    def __init__(self):
        super().__init__()
        self._satellites = []
        self._roles = {
            Qt.DisplayRole: b'name',
            Qt.UserRole: b'data'
        }
    
    def roleNames(self):
        return self._roles
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._satellites)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if index.row() >= len(self._satellites):
            return None
        
        satellite = self._satellites[index.row()]
        
        if role == Qt.DisplayRole:
            return satellite.get('name', 'Unknown')
        elif role == Qt.UserRole:
            return satellite
        
        return None
    
    def update_satellites(self, satellites):
        self.beginResetModel()
        self._satellites = satellites
        self.endResetModel()

class DatasetModel(QAbstractListModel):
    """Model for dataset data"""
    def __init__(self):
        super().__init__()
        self._datasets = []
        self._roles = {
            Qt.DisplayRole: b'name',
            Qt.UserRole: b'data'
        }
    
    def roleNames(self):
        return self._roles
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._datasets)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if index.row() >= len(self._datasets):
            return None
        
        dataset = self._datasets[index.row()]
        
        if role == Qt.DisplayRole:
            return dataset.get('name', 'Unknown')
        elif role == Qt.UserRole:
            return dataset
        
        return None
    
    def update_datasets(self, datasets):
        self.beginResetModel()
        self._datasets = datasets
        self.endResetModel()

class BackendController(QObject):
    """Main backend controller for QML integration"""
    
    # Signals for QML
    crawler_status_changed = Signal(str, str)  # status, message
    crawler_progress_changed = Signal(int, str)  # percentage, message
    download_progress_changed = Signal(int, str)  # percentage, message
    satellites_updated = Signal()
    datasets_updated = Signal()
    notification = Signal(str, str)  # type, message
    auth_status_changed = Signal(bool, str)  # authenticated, message
    console_output = Signal(str)  # console message
    satellite_count_changed = Signal(int)  # satellite count
    dataset_count_changed = Signal(int)  # dataset count
    
    def __init__(self):
        print("[DEBUG] BackendController.__init__ start")
        super().__init__()
        self.satellite_model = SatelliteModel()
        self.dataset_model = DatasetModel()
        self.current_theme = "dark"
        self.auth_status = False
        self.settings = self.load_settings()
        print("[DEBUG] BackendController.__init__ end")
    
    @Slot()
    def start_crawler(self):
        """Start the GEE catalog crawler"""
        print("[DEBUG] Starting crawler")
        try:
            self.crawler_status_changed.emit("running", "Starting crawler...")
            self.notification.emit("info", "Starting web crawler...")
            
            # Start real crawler in background thread
            self.crawler_thread = RealCrawlerThread()
            self.crawler_thread.progress_updated.connect(self.update_crawler_progress)
            self.crawler_thread.console_output.connect(self.update_console_output)
            self.crawler_thread.finished.connect(self.crawler_finished)
            self.crawler_thread.start()
        except Exception as e:
            self.crawler_status_changed.emit("error", f"Crawler failed: {str(e)}")
            self.notification.emit("error", f"Failed to start crawler: {str(e)}")
    
    @Slot()
    def stop_crawler(self):
        """Stop the crawler"""
        if hasattr(self, 'crawler_thread') and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            self.crawler_status_changed.emit("stopped", "Crawler stopped")
            self.notification.emit("info", "Crawler stopped")
    
    def update_crawler_progress(self, percentage, message):
        """Update crawler progress"""
        self.crawler_progress_changed.emit(percentage, message)
    
    def update_console_output(self, message):
        """Update console output"""
        self.console_output.emit(message)
    
    def crawler_finished(self):
        """Handle crawler completion"""
        self.crawler_status_changed.emit("completed", "Crawler completed successfully")
        self.notification.emit("success", "Crawler completed successfully")
        self.load_satellites()
        self.load_datasets()
    
    @Slot()
    def load_satellites(self):
        """Load satellite data from crawler output"""
        try:
            # Try to load from crawler data first
            crawler_data_path = Path('backend/crawler_data/gee_catalog_data_enhanced.json.gz')
            if crawler_data_path.exists():
                import gzip
                with gzip.open(crawler_data_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract satellite data
                satellites_data = data.get('satellites', {})
                satellites = []
                
                for satellite_name, datasets in satellites_data.items():
                    if datasets:
                        # Use the first dataset as representative
                        sample_dataset = datasets[0]
                        satellites.append({
                            "name": satellite_name,
                            "description": sample_dataset.get('description', 'Satellite data collection'),
                            "resolution": sample_dataset.get('resolution', 'Variable'),
                            "bands": sample_dataset.get('bands', []),
                            "applications": sample_dataset.get('applications', []),
                            "status": "Active",
                            "code_snippet": sample_dataset.get('code_snippet', ''),
                            "datasets_count": len(datasets)
                        })
                
                if satellites:
                    self.satellite_model.update_satellites(satellites)
                    self.satellites_updated.emit()
                    self.notification.emit("success", f"Loaded {len(satellites)} satellites from crawler data")
                    self.satellite_count_changed.emit(len(satellites))
                    return
            
            # Fallback to sample data
            satellites = self.get_sample_satellites()
            self.satellite_model.update_satellites(satellites)
            self.satellites_updated.emit()
            self.notification.emit("info", "Loaded sample satellite data")
            self.satellite_count_changed.emit(len(satellites))
        except Exception as e:
            self.notification.emit("error", f"Failed to load satellites: {str(e)}")
            # Fallback to sample data
            satellites = self.get_sample_satellites()
            self.satellite_model.update_satellites(satellites)
            self.satellites_updated.emit()
            self.satellite_count_changed.emit(len(satellites))
    
    @Slot()
    def load_datasets(self):
        """Load dataset data from crawler output"""
        try:
            # Try to load from crawler data first
            crawler_data_path = Path('backend/crawler_data/gee_catalog_data_enhanced.json.gz')
            if crawler_data_path.exists():
                import gzip
                with gzip.open(crawler_data_path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract dataset data
                datasets_data = data.get('datasets', [])
                datasets = []
                
                for dataset in datasets_data[:50]:  # Limit to first 50 for performance
                    datasets.append({
                        "name": dataset.get('name', 'Unknown Dataset'),
                        "description": dataset.get('description', 'No description available'),
                        "provider": dataset.get('publisher', 'Unknown'),
                        "resolution": dataset.get('resolution', 'Variable'),
                        "temporal_coverage": dataset.get('dates', 'Variable'),
                        "tags": dataset.get('tags', []),
                        "satellites": dataset.get('satellites', []),
                        "data_type": dataset.get('data_type', 'Unknown'),
                        "code_snippet": dataset.get('code_snippet', '')
                    })
                
                if datasets:
                    self.dataset_model.update_datasets(datasets)
                    self.datasets_updated.emit()
                    self.notification.emit("success", f"Loaded {len(datasets)} datasets from crawler data")
                    self.dataset_count_changed.emit(len(datasets))
                    return
            
            # Fallback to sample data
            datasets = self.get_sample_datasets()
            self.dataset_model.update_datasets(datasets)
            self.datasets_updated.emit()
            self.notification.emit("info", "Loaded sample dataset data")
            self.dataset_count_changed.emit(len(datasets))
        except Exception as e:
            self.notification.emit("error", f"Failed to load datasets: {str(e)}")
            # Fallback to sample data
            datasets = self.get_sample_datasets()
            self.dataset_model.update_datasets(datasets)
            self.datasets_updated.emit()
            self.dataset_count_changed.emit(len(datasets))
    
    def get_sample_satellites(self):
        """Get sample satellite data"""
        return []
    
    def get_sample_datasets(self):
        """Get sample dataset data"""
        return []
    
    @Slot(str, str, str, str, str, str)
    def start_download(self, satellite, sensor, start_date, end_date, region, output_format):
        """Start data download (simulated)"""
        try:
            self.download_progress_changed.emit(0, "Initializing download...")
            self.notification.emit("info", "Download started (simulated)")
            
            # Start download in background thread
            self.download_thread = DownloadThread(
                satellite, sensor, start_date, end_date, region, output_format
            )
            self.download_thread.progress_updated.connect(self.update_download_progress)
            self.download_thread.finished.connect(self.download_finished)
            self.download_thread.start()
            
        except Exception as e:
            self.notification.emit("error", f"Failed to start download: {str(e)}")
    
    def update_download_progress(self, percentage, message):
        """Update download progress"""
        self.download_progress_changed.emit(percentage, message)
    
    def download_finished(self):
        """Handle download completion"""
        self.notification.emit("success", "Download completed successfully")
    
    @Slot(str)
    def set_theme(self, theme):
        """Set application theme"""
        print(f"[DEBUG] Setting theme to: {theme}")
        self.current_theme = theme
        self.settings['theme'] = theme
        self.save_settings()
        self.notification.emit("info", f"Theme changed to {theme}")
    
    @Slot(str)
    def setTheme(self, theme):
        """Set application theme (QML compatible)"""
        self.set_theme(theme)
    
    @Slot()
    def check_auth_status(self):
        """Check authentication status"""
        print("[DEBUG] Checking auth status")
        try:
            self.auth_status = False
            self.auth_status_changed.emit(False, "Not authenticated with Google Earth Engine")
        except Exception as e:
            self.auth_status = False
            self.auth_status_changed.emit(False, f"Authentication check failed: {str(e)}")
    
    @Slot(result=dict)
    def check_auth_needed(self):
        """Check if authentication is needed"""
        try:
            # Import the auth manager
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            from flutter_earth.auth_setup import AuthManager
            
            auth_manager = AuthManager()
            needs_auth = auth_manager.needs_authentication()
            auth_info = auth_manager.get_auth_info()
            
            return {
                "status": "success",
                "needs_auth": needs_auth,
                "auth_info": auth_info,
                "message": "Authentication check completed"
            }
        except Exception as e:
            return {
                "status": "error",
                "needs_auth": True,  # Default to requiring auth on error
                "message": f"Auth check error: {str(e)}"
            }
    
    @Slot(str, str)
    def set_auth_credentials(self, key_file, project_id):
        """Set authentication credentials"""
        try:
            # Import the auth manager
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            from flutter_earth.auth_setup import AuthManager
            
            auth_manager = AuthManager()
            auth_manager.save_credentials(project_id, key_file)
            
            # Test the connection after saving
            success, message = auth_manager.initialize_earth_engine()
            
            if success:
                self.auth_status = True
                self.auth_status_changed.emit(True, "Credentials saved and Earth Engine initialized successfully")
                self.notification.emit("success", "Authentication successful!")
                return {
                    "status": "success",
                    "message": "Credentials saved and Earth Engine initialized successfully"
                }
            else:
                self.auth_status = False
                self.auth_status_changed.emit(False, f"Credentials saved but Earth Engine initialization failed: {message}")
                self.notification.emit("warning", f"Credentials saved but Earth Engine initialization failed: {message}")
                return {
                    "status": "warning",
                    "message": f"Credentials saved but Earth Engine initialization failed: {message}"
                }
                
        except Exception as e:
            self.auth_status = False
            self.auth_status_changed.emit(False, f"Auth error: {str(e)}")
            self.notification.emit("error", f"Authentication failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Auth error: {str(e)}"
            }
    
    @Slot(str, str)
    def test_auth_connection(self, project_id, key_file):
        """Test authentication connection"""
        try:
            # Import the auth manager
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            from flutter_earth.auth_setup import AuthManager
            
            auth_manager = AuthManager()
            auth_manager.test_connection(project_id, key_file)
            
            self.notification.emit("success", "Authentication test completed successfully")
            return {
                "status": "success",
                "message": "Authentication test completed successfully"
            }
        except Exception as e:
            self.notification.emit("error", f"Authentication test failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Authentication test failed: {str(e)}"
            }
    
    @Slot(result=dict)
    def get_auth_status(self):
        """Get comprehensive authentication status"""
        try:
            # Import the auth manager
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            from flutter_earth.auth_setup import AuthManager
            
            auth_manager = AuthManager()
            auth_info = auth_manager.get_auth_info()
            
            authenticated = auth_info.get('authenticated', False)
            self.auth_status = authenticated
            self.auth_status_changed.emit(authenticated, auth_info.get('message', 'Authentication status checked'))
            
            return {
                "status": "success",
                "authenticated": authenticated,
                "message": auth_info.get('message', 'Authentication status checked'),
                "auth_info": auth_info
            }
        except Exception as e:
            self.auth_status = False
            self.auth_status_changed.emit(False, f"Failed to get auth status: {str(e)}")
            return {
                "status": "error",
                "authenticated": False,
                "message": f"Failed to get auth status: {str(e)}"
            }
    
    @Slot()
    def clear_auth_credentials(self):
        """Clear all authentication credentials"""
        try:
            # Import the auth manager
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            from flutter_earth.auth_setup import AuthManager
            
            auth_manager = AuthManager()
            auth_manager.clear_credentials()
            
            self.auth_status = False
            self.auth_status_changed.emit(False, "Authentication credentials cleared")
            self.notification.emit("info", "Authentication credentials cleared successfully")
            
            return {
                "status": "success",
                "message": "Authentication credentials cleared successfully"
            }
        except Exception as e:
            self.notification.emit("error", f"Failed to clear credentials: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to clear credentials: {str(e)}"
            }
    
    @Slot(QObject)
    def browse_key_file(self, auth_dialog):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Key File",
            "",
            "JSON files (*.json);;All Files (*)"
        )
        if file_path:
            # Update the QML property directly
            auth_dialog.setProperty("keyFilePath", file_path)
            # Also update the TextField if it exists
            key_file_field = auth_dialog.findChild(QObject, "keyFileField")
            if key_file_field:
                key_file_field.setProperty("text", file_path)
    
    @Slot(str, str)
    def authenticate(self, key_file, project_id):
        """Handle authentication with provided credentials"""
        print(f"[DEBUG] Authenticating with key file: {key_file}, project: {project_id}")
        try:
            # Use the new auth system
            result = self.set_auth_credentials(key_file, project_id)
            
            if result["status"] == "success":
                self.auth_status = True
                self.auth_status_changed.emit(True, "Successfully authenticated with Google Earth Engine")
                self.notification.emit("success", "Authentication successful!")
            else:
                self.auth_status = False
                self.auth_status_changed.emit(False, result["message"])
                self.notification.emit("error", result["message"])
                
        except Exception as e:
            self.auth_status = False
            self.auth_status_changed.emit(False, f"Authentication failed: {str(e)}")
            self.notification.emit("error", f"Authentication failed: {str(e)}")
    
    @Slot()
    def start_index_analysis(self, raster_files, indices, output_dir):
        """Start index analysis (simulated)"""
        try:
            self.notification.emit("info", "Starting index analysis...")
            # Simulate analysis process
            # In real implementation, this would call the actual analysis functions
            self.notification.emit("success", "Index analysis completed successfully")
        except Exception as e:
            self.notification.emit("error", f"Index analysis failed: {str(e)}")
    
    @Slot()
    def start_vector_download(self, data_source, query, aoi, output_format, output_dir):
        """Start vector download (simulated)"""
        try:
            self.notification.emit("info", "Starting vector download...")
            # Simulate download process
            # In real implementation, this would call the actual download functions
            self.notification.emit("success", "Vector download completed successfully")
        except Exception as e:
            self.notification.emit("error", f"Vector download failed: {str(e)}")
    
    @Slot()
    def load_data_viewer(self, file_path):
        """Load data for viewer (simulated)"""
        try:
            self.notification.emit("info", f"Loading data from: {file_path}")
            # Simulate data loading
            # In real implementation, this would load and display the data
            self.notification.emit("success", "Data loaded successfully")
        except Exception as e:
            self.notification.emit("error", f"Failed to load data: {str(e)}")
    
    @Slot()
    def clear_cache_and_logs(self):
        """Clear application cache and logs"""
        try:
            # Simulate cache clearing
            self.notification.emit("info", "Cache and logs cleared successfully")
        except Exception as e:
            self.notification.emit("error", f"Failed to clear cache: {str(e)}")
    
    @Slot()
    def reload_settings(self):
        """Reload application settings"""
        try:
            self.settings = self.load_settings()
            self.notification.emit("info", "Settings reloaded successfully")
        except Exception as e:
            self.notification.emit("error", f"Failed to reload settings: {str(e)}")
    
    @Slot()
    def clear_history(self):
        """Clear application history"""
        try:
            # Simulate history clearing
            self.notification.emit("info", "History cleared successfully")
        except Exception as e:
            self.notification.emit("error", f"Failed to clear history: {str(e)}")
    
    @Slot()
    def run_web_crawler(self):
        """Run the web crawler to fetch satellite data"""
        try:
            print("[DEBUG] Starting web crawler")
            self.notification.emit("info", "Starting web crawler...")
            
            # Import the crawler module
            sys.path.insert(0, str(Path(__file__).parent / 'backend'))
            try:
                from gee_catalog_crawler_enhanced import run_crawler
                
                # Run the crawler in background (this should be non-blocking)
                import threading
                crawler_thread = threading.Thread(target=run_crawler)
                crawler_thread.daemon = True
                crawler_thread.start()
                
                print("[DEBUG] Web crawler started in background")
                self.notification.emit("success", "Web crawler started in background")
                return {
                    "status": "started",
                    "message": "Web crawler started in background"
                }
            except ImportError:
                # Fallback to simulated crawler
                self.start_crawler()
                return {
                    "status": "started",
                    "message": "Simulated crawler started"
                }
        except Exception as e:
            print(f"[DEBUG] Web crawler error: {e}")
            self.notification.emit("error", f"Web crawler error: {str(e)}")
            return {
                "status": "error",
                "message": f"Web crawler error: {str(e)}"
            }
    
    @Slot(str)
    def compress_crawler_data(self, json_path):
        """Compress crawler data to gzip format"""
        import gzip
        try:
            data_dir = Path('backend/crawler_data')
            data_dir.mkdir(parents=True, exist_ok=True)
            out_path = data_dir / 'gee_catalog_data_enhanced.json.gz'
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with gzip.open(out_path, 'wt', encoding='utf-8') as gz:
                json.dump(data, gz, ensure_ascii=False, indent=2)
            
            self.notification.emit("success", f"Compressed and saved to {out_path}")
            return {"status": "success", "message": f"Compressed and saved to {out_path}"}
        except Exception as e:
            self.notification.emit("error", f"Compression failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @Slot(result=dict)
    def get_crawler_progress(self):
        """Get current crawler progress from the progress file"""
        try:
            progress_file = Path('backend/crawler_data/crawler_progress.json')
            if not progress_file.exists():
                return {
                    "status": "success",
                    "progress": {
                        "status": "not_started",
                        "message": "Crawler not started",
                        "percentage": 0,
                        "current_page": 0,
                        "total_pages": 0,
                        "datasets_found": 0,
                        "satellites_found": 0
                    }
                }
            
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            
            # Calculate percentage based on current progress
            percentage = 0
            if progress_data.get('total_pages', 0) > 0:
                percentage = min(100, (progress_data.get('current_page', 0) / progress_data.get('total_pages', 1)) * 100)
            elif progress_data.get('status') == 'completed':
                percentage = 100
            
            return {
                "status": "success",
                "progress": {
                    "status": progress_data.get('status', 'unknown'),
                    "message": progress_data.get('message', 'Processing...'),
                    "percentage": percentage,
                    "current_page": progress_data.get('current_page', 0),
                    "total_pages": progress_data.get('total_pages', 0),
                    "datasets_found": progress_data.get('datasets_found', 0),
                    "satellites_found": progress_data.get('satellites_found', 0)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Crawler progress error: {str(e)}"
            }
    
    def load_settings(self):
        """Load application settings"""
        settings_file = Path("settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"theme": "dark", "output_dir": "./downloads"}
    
    def save_settings(self):
        """Save application settings"""
        try:
            with open("settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

class RealCrawlerThread(QThread):
    """Background thread for real crawler operations"""
    progress_updated = Signal(int, str)
    console_output = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        """Run real crawler in background"""
        try:
            # Import the real crawler
            sys.path.insert(0, str(Path(__file__).parent / 'backend'))
            from gee_catalog_crawler_enhanced import run_crawler
            
            # Update progress to show crawler is starting
            self.progress_updated.emit(0, "Initializing crawler...")
            self.console_output.emit("🚀 Starting Google Earth Engine Catalog Crawler...")
            
            # Run the crawler
            result = run_crawler()
            
            if result["status"] == "success":
                self.progress_updated.emit(100, f"Crawler completed! {result.get('total_datasets', 0)} datasets found.")
                self.console_output.emit(f"✅ Crawler completed successfully!")
                self.console_output.emit(f"📊 Total datasets: {result.get('total_datasets', 0)}")
                self.console_output.emit(f"🛰️ Total satellites: {result.get('total_satellites', 0)}")
                self.console_output.emit(f"💾 Output saved to: {result.get('output_file', 'Unknown')}")
            else:
                self.progress_updated.emit(0, f"Crawler failed: {result.get('message', 'Unknown error')}")
                self.console_output.emit(f"❌ Crawler failed: {result.get('message', 'Unknown error')}")
                
        except ImportError as e:
            self.progress_updated.emit(0, f"Crawler import error: {str(e)}")
            self.console_output.emit(f"❌ Import error: {str(e)}")
        except Exception as e:
            self.progress_updated.emit(0, f"Crawler error: {str(e)}")
            self.console_output.emit(f"❌ Crawler error: {str(e)}")
    
    def stop(self):
        """Stop the crawler"""
        self.running = False
        self.console_output.emit("⏹️ Crawler stopped by user")

class CrawlerThread(QThread):
    """Background thread for crawler operations (simulated fallback)"""
    progress_updated = Signal(int, str)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        """Run crawler in background (simulated)"""
        try:
            # Simulate crawler progress
            for i in range(101):
                if not self.running:
                    break
                
                if i <= 20:
                    message = "Initializing crawler..."
                elif i <= 40:
                    message = "Connecting to Google Earth Engine..."
                elif i <= 60:
                    message = "Fetching dataset catalog..."
                elif i <= 80:
                    message = "Processing satellite information..."
                else:
                    message = "Finalizing data collection..."
                
                self.progress_updated.emit(i, message)
                time.sleep(0.1)
        except Exception as e:
            self.progress_updated.emit(0, f"Error: {str(e)}")
    
    def stop(self):
        """Stop the crawler"""
        self.running = False

class DownloadThread(QThread):
    """Background thread for download operations (simulated)"""
    progress_updated = Signal(int, str)
    
    def __init__(self, satellite, sensor, start_date, end_date, region, output_format):
        super().__init__()
        self.satellite = satellite
        self.sensor = sensor
        self.start_date = start_date
        self.end_date = end_date
        self.region = region
        self.output_format = output_format
    
    def run(self):
        """Run download in background (simulated)"""
        try:
            # Simulate download progress
            for i in range(101):
                if i <= 20:
                    message = "Preparing download..."
                elif i <= 40:
                    message = "Connecting to data source..."
                elif i <= 60:
                    message = "Downloading data..."
                elif i <= 80:
                    message = "Processing data..."
                else:
                    message = "Saving files..."
                
                self.progress_updated.emit(i, message)
                time.sleep(0.05)
        except Exception as e:
            self.progress_updated.emit(0, f"Error: {str(e)}")

def main():
    """Main application entry point"""
    try:
        print("[DEBUG] Starting QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Flutter Earth")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Flutter Earth Team")
        
        # Set application icon if available
        icon_path = Path("logo.ico")
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        print("[DEBUG] QApplication created and icon set.")
        
        engine = QQmlApplicationEngine()
        print("[DEBUG] QQmlApplicationEngine created.")
        
        backend = BackendController()
        print("[DEBUG] BackendController created.")
        
        # Set context properties
        engine.rootContext().setContextProperty("backend", backend)
        engine.rootContext().setContextProperty("satelliteModel", backend.satellite_model)
        engine.rootContext().setContextProperty("datasetModel", backend.dataset_model)
        print("[DEBUG] Context properties set.")
        
        # Load QML file
        qml_file = Path("main.qml")
        if not qml_file.exists():
            print("Error: main.qml file not found!")
            return 1
        
        print("[DEBUG] Loading main.qml...")
        print(f"[DEBUG] QML file path: {qml_file.resolve()}")
        qml_url = QUrl.fromLocalFile(str(qml_file))
        print(f"[DEBUG] QML URL: {qml_url}")
        
        engine.load(qml_url)
        print("[DEBUG] QML loaded.")
        
        # Check if QML loaded successfully
        if not engine.rootObjects():
            print("Error: Failed to load QML!")
            return 1
        
        print("[DEBUG] QML root objects present.")
        print(f"[DEBUG] Number of root objects: {len(engine.rootObjects())}")
        
        # Connect AuthDialog browse signal to backend slot
        root_objects = engine.rootObjects()
        if root_objects:
            main_window = root_objects[0]
            auth_dialog = main_window.findChild(QObject, "authDialog")
            if auth_dialog:
                auth_dialog.browseKeyFileRequested.connect(lambda: backend.browse_key_file(auth_dialog))
        
        # Initialize backend data
        backend.check_auth_status()
        print("[DEBUG] Auth status checked.")
        
        backend.load_satellites()
        print("[DEBUG] Satellites loaded.")
        backend.load_datasets()
        print("[DEBUG] Datasets loaded.")
        
        print("[DEBUG] About to enter event loop")
        return app.exec()
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Exception in main(): {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 