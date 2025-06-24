"""Earth Engine management for Flutter Earth."""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

import ee
from PyQt6.QtWidgets import QWidget, QMessageBox, QInputDialog, QFileDialog, QLineEdit

from .types import SatelliteCollection, BoundingBox, Polygon


class EarthEngineManager:
    """Manages Earth Engine operations."""
    
    def __init__(self):
        """Initialize the Earth Engine manager."""
        self._logger = logging.getLogger(__name__)
        self._initialized = False
        self._project_id: Optional[str] = None
        self._service_account_path: Optional[Path] = None
        
        # Available satellite collections
        self._collections: Dict[str, SatelliteCollection] = {
            "LANDSAT/LC08/C02/T1_L2": SatelliteCollection(
                name="LANDSAT/LC08/C02/T1_L2",
                display_name="Landsat 8 Collection 2 Level 2",
                description="Landsat 8 surface reflectance data",
                spatial_resolution=30.0,
                temporal_resolution="16 days",
                bands=["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7"],
                start_date=datetime(2013, 4, 11),
                cloud_cover_available=True,
                vegetation_indices_supported=True
            ),
            "LANDSAT/LE07/C02/T1_L2": SatelliteCollection(
                name="LANDSAT/LE07/C02/T1_L2",
                display_name="Landsat 7 Collection 2 Level 2",
                description="Landsat 7 surface reflectance data",
                spatial_resolution=30.0,
                temporal_resolution="16 days",
                bands=["SR_B1", "SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B7"],
                start_date=datetime(1999, 4, 15),
                end_date=datetime(2021, 12, 31),
                cloud_cover_available=True,
                vegetation_indices_supported=True
            ),
            "COPERNICUS/S2_SR_HARMONIZED": SatelliteCollection(
                name="COPERNICUS/S2_SR_HARMONIZED",
                display_name="Sentinel-2 Surface Reflectance",
                description="Sentinel-2 surface reflectance data",
                spatial_resolution=10.0,
                temporal_resolution="5 days",
                bands=["B2", "B3", "B4", "B8", "B11", "B12"],
                start_date=datetime(2017, 3, 28),
                cloud_cover_available=True,
                vegetation_indices_supported=True
            ),
            "MODIS/006/MOD13Q1": SatelliteCollection(
                name="MODIS/006/MOD13Q1",
                display_name="MODIS Vegetation Indices",
                description="MODIS 16-day vegetation indices",
                spatial_resolution=250.0,
                temporal_resolution="16 days",
                bands=["NDVI", "EVI", "NIR_reflectance", "red_reflectance"],
                start_date=datetime(2000, 2, 18),
                cloud_cover_available=False,
                vegetation_indices_supported=True
            )
        }
    
    def is_initialized(self) -> bool:
        """Check if Earth Engine is initialized."""
        return self._initialized
    
    def initialize(self, parent: Optional[QWidget] = None) -> bool:
        """Initialize Earth Engine.
        
        Args:
            parent: Parent widget for dialogs.
            
        Returns:
            True if initialization was successful.
        """
        try:
            if self._initialized:
                self._logger.info("Earth Engine already initialized")
                return True
            
            # Try to initialize Earth Engine
            ee.Initialize()
            self._initialized = True
            self._logger.info("Earth Engine initialized successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize Earth Engine: {e}")
            
            if parent:
                # Show authentication dialog
                return self._show_auth_dialog(parent)
            
            if hasattr(self, 'bridge'):
                self.bridge.showMessage.emit('error', 'Earth Engine Error', 'Earth Engine initialization failed. Please check your credentials and try again.')
            
            return False
    
    def _show_auth_dialog(self, parent: QWidget) -> bool:
        """Show authentication dialog.
        
        Args:
            parent: Parent widget.
            
        Returns:
            True if authentication was successful.
        """
        try:
            title = "Earth Engine Authentication"
            text = "Earth Engine authentication required."
            informative_text = (
                "Please authenticate with Google Earth Engine to continue.\n\n"
                "You can either:\n"
                "1. Use service account authentication\n"
                "2. Use interactive authentication\n\n"
                "Would you like to set up authentication now?"
            )

            # Constructing the full text for the question dialog
            full_text = f"{text}\n\n{informative_text}"

            reply = QMessageBox.question(
                parent,
                title,
                full_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No  # Default button
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                return self._setup_authentication(parent)
            
            # User chose No or closed the dialog
            self._logger.info("User declined Earth Engine authentication.")
            # The application should continue and allow GUI to open.
            # The initialize method, which calls this, will return False.
            # The main application logic should handle this to open GUI anyway.
            # Emitting a message via bridge if available:
            if hasattr(self, 'bridge') and self.bridge is not None:
                 # Assuming 'bridge' is set on this manager instance if used with GUI
                 # and 'showMessage' is a signal: (type, title, message)
                 self.bridge.showMessage.emit('warning', 'Earth Engine Not Initialized',
                                              'Earth Engine is not initialized. Some features may be unavailable.')
            else:
                 self._logger.warning("User declined EE auth. Bridge not available for UI message.")
            return False # Indicates auth was not completed, but not an error in dialog display
            
        except Exception as e:
            self._logger.error(f"Error showing auth dialog: {e}")
            if hasattr(self, 'bridge') and self.bridge is not None:
                 self.bridge.showMessage.emit('error', 'Dialog Error', f'Could not display authentication dialog: {e}')
            # Still return False, so GUI can attempt to load.
            return False
    
    def _setup_authentication(self, parent: QWidget) -> bool:
        """Setup Earth Engine authentication.
        
        Args:
            parent: Parent widget.
            
        Returns:
            True if authentication setup was successful.
        """
        try:
            # Ask user for authentication method
            auth_method, ok = QInputDialog.getItem(
                parent,
                "Authentication Method",
                "Choose authentication method:",
                ["Service Account", "Interactive Authentication"],
                0,
                False
            )
            
            if not ok:
                return False
            
            if auth_method == "Service Account":
                return self._setup_service_account_auth(parent)
            else:
                return self._setup_interactive_auth(parent)
                
        except Exception as e:
            self._logger.error(f"Error setting up authentication: {e}")
            return False
    
    def _setup_service_account_auth(self, parent: QWidget) -> bool:
        """Setup service account authentication.
        
        Args:
            parent: Parent widget.
            
        Returns:
            True if setup was successful.
        """
        try:
            # Ask for service account file
            file_path, _ = QFileDialog.getOpenFileName(
                parent,
                "Select Service Account JSON File",
                str(Path.home()),
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return False
            
            service_account_path = Path(file_path)
            
            # Ask for project ID
            project_id, ok = QInputDialog.getText(
                parent,
                "Project ID",
                "Enter your Google Cloud Project ID:"
            )
            
            if not ok or not project_id:
                return False
            
            # Initialize with service account
            credentials = ee.ServiceAccountCredentials(
                service_account_path=service_account_path,
                key_file=str(service_account_path)
            )
            ee.Initialize(credentials, project=project_id)
            
            self._initialized = True
            self._project_id = project_id
            self._service_account_path = service_account_path
            
            self._logger.info("Service account authentication successful")
            return True
            
        except Exception as e:
            self._logger.error(f"Service account authentication failed: {e}")
            QMessageBox.critical(
                parent,
                "Authentication Failed",
                f"Service account authentication failed:\n{str(e)}"
            )
            return False
    
    def _setup_interactive_auth(self, parent: QWidget) -> bool:
        """Setup interactive authentication.
        
        Args:
            parent: Parent widget.
            
        Returns:
            True if setup was successful.
        """
        try:
            # Show instructions
            QMessageBox.information(
                parent,
                "Interactive Authentication",
                "Interactive authentication will open a web browser.\n\n"
                "Please follow the instructions in your browser to authenticate.\n\n"
                "You may need to close this dialog and restart the application after authentication."
            )
            
            # Initialize interactive authentication
            # This may open a browser window if credentials are not found or are expired.
            # After authentication, ee.Initialize still needs to be called.
            # The ee.Authenticate() call is more explicit for triggering auth flow,
            # but ee.Initialize() often does this implicitly if needed.

            try:
                # Attempt to initialize. This might use existing credentials from a previous
                # ee.Authenticate() or gcloud session, or trigger a new auth flow.
                self._logger.info("Attempting interactive Earth Engine initialization...")
                ee.Initialize()
                self._initialized = True
                self._project_id = ee.data.get_project_id() # Try to get project ID if auto-detected
                self._logger.info(f"Earth Engine initialized successfully via interactive flow (project: {self._project_id or 'auto-detected'}).")
                return True
            except Exception as e_init:
                # Check if the error is specifically about a missing project ID
                if "no project found" in str(e_init).lower() or \
                   "project id" in str(e_init).lower() or \
                   "Set a project ID" in str(e_init): # Common phrases in EE errors
                    self._logger.warning(f"Interactive ee.Initialize() failed to find a project: {e_init}")

                    project_id_str, ok = QInputDialog.getText(
                        parent,
                        "Project ID Required",
                        "Authentication seems successful, but Earth Engine requires a Google Cloud Project ID.\n"
                        "Please enter your Project ID:",
                        QLineEdit.EchoMode.Normal,
                        self._project_id or ""  # Suggest previously stored project ID, if any
                    )

                    if ok and project_id_str:
                        try:
                            # Retry initialization with the provided project ID
                            # Credentials should be cached from the ee.Authenticate() or previous ee.Initialize() attempt
                            ee.Initialize(project=project_id_str)
                            self._initialized = True
                            self._project_id = project_id_str # Store the successfully used project ID
                            self._logger.info(f"Interactive authentication successful with specified project ID: {project_id_str}")
                            # Consider saving this project_id to config for future use (e.g., self.config_manager.set_value(...))
                            return True
                        except Exception as e_proj_init:
                            self._logger.error(f"Interactive authentication with specified project ID '{project_id_str}' failed: {e_proj_init}")
                            QMessageBox.critical(
                                parent,
                                "Initialization Failed",
                                f"Failed to initialize Earth Engine with Project ID '{project_id_str}':\n{str(e_proj_init)}"
                            )
                            return False
                    else:
                        self._logger.warning("User cancelled or did not provide a Project ID for interactive authentication.")
                        QMessageBox.warning(
                            parent,
                            "Project ID Required",
                            "A Google Cloud Project ID is necessary to use Earth Engine. Initialization was cancelled."
                        )
                        return False
                else:
                    # Other type of error during the initial ee.Initialize() attempt
                    self._logger.error(f"Interactive authentication failed: {e_init}")
                    QMessageBox.critical(
                        parent,
                        "Authentication Failed",
                        f"Interactive authentication failed:\n{str(e_init)}"
                    )
                    return False

        except Exception as e: # Catch-all for unexpected errors in this method
            self._logger.error(f"An unexpected error occurred during interactive authentication setup: {e}")
            QMessageBox.critical(
                parent,
                "Authentication Error",
                f"An unexpected error occurred during interactive authentication:\n{str(e)}"
            )
            return False
    
    def get_collections(self) -> Dict[str, SatelliteCollection]:
        """Get available satellite collections.
        
        Returns:
            Dictionary of available collections.
        """
        return self._collections.copy()
    
    def get_collection(self, name: str) -> Optional[SatelliteCollection]:
        """Get a specific satellite collection.
        
        Args:
            name: Collection name.
            
        Returns:
            Satellite collection or None if not found.
        """
        return self._collections.get(name)
    
    def search_images(
        self,
        collection: str,
        area: Union[BoundingBox, Polygon],
        start_date: datetime,
        end_date: datetime,
        max_cloud_cover: float = 20.0
    ) -> List[Dict[str, Any]]:
        """Search for images in a collection.
        
        Args:
            collection: Collection name.
            area: Area of interest.
            start_date: Start date.
            end_date: End date.
            max_cloud_cover: Maximum cloud cover percentage.
            
        Returns:
            List of image metadata.
        """
        if not self._initialized:
            raise RuntimeError("Earth Engine not initialized")
        
        try:
            # Convert area to Earth Engine geometry
            if isinstance(area, BoundingBox):
                geometry = ee.Geometry.Rectangle(area.to_list())
            else:
                coords = [[coord.longitude, coord.latitude] for coord in area.coordinates]
                geometry = ee.Geometry.Polygon(coords)
            
            # Get collection
            ee_collection = ee.ImageCollection(collection)
            
            # Filter by date and area
            filtered = ee_collection.filterDate(start_date, end_date).filterBounds(geometry)
            
            # Filter by cloud cover if available
            collection_info = self._collections.get(collection)
            if collection_info and collection_info.cloud_cover_available:
                filtered = filtered.filter(ee.Filter.lt('CLOUD_COVER', max_cloud_cover))
            
            # Get image list
            image_list = filtered.toList(filtered.size())
            
            # Convert to Python list
            images = []
            for i in range(image_list.size().getInfo()):
                image = ee.Image(image_list.get(i))
                metadata = image.getInfo()
                images.append(metadata)
            
            self._logger.info(f"Found {len(images)} images in collection {collection}")
            return images
            
        except Exception as e:
            self._logger.error(f"Error searching images: {e}")
            raise
    
    def get_image(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID.
        
        Args:
            image_id: Image ID.
            
        Returns:
            Image metadata or None if not found.
        """
        if not self._initialized:
            raise RuntimeError("Earth Engine not initialized")
        
        try:
            image = ee.Image(image_id)
            return image.getInfo()
        except Exception as e:
            self._logger.error(f"Error getting image {image_id}: {e}")
            return None
    
    def calculate_vegetation_index(
        self,
        image: ee.Image,
        index_type: str,
        bands: Optional[Dict[str, str]] = None
    ) -> ee.Image:
        """Calculate vegetation index.
        
        Args:
            image: Earth Engine image.
            index_type: Type of vegetation index.
            bands: Band mapping for the index.
            
        Returns:
            Image with vegetation index.
        """
        if not self._initialized:
            raise RuntimeError("Earth Engine not initialized")
        
        try:
            if index_type.lower() == "ndvi":
                return image.normalizedDifference([bands.get('nir', 'B5'), bands.get('red', 'B4')])
            elif index_type.lower() == "evi":
                return image.expression(
                    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
                    {
                        'NIR': image.select(bands.get('nir', 'B5')),
                        'RED': image.select(bands.get('red', 'B4')),
                        'BLUE': image.select(bands.get('blue', 'B2'))
                    }
                )
            elif index_type.lower() == "savi":
                L = 0.5  # Soil brightness correction factor
                return image.expression(
                    f'1.5 * ((NIR - RED) / (NIR + RED + {L}))',
                    {
                        'NIR': image.select(bands.get('nir', 'B5')),
                        'RED': image.select(bands.get('red', 'B4'))
                    }
                )
            elif index_type.lower() == "ndwi":
                return image.normalizedDifference([bands.get('nir', 'B5'), bands.get('swir', 'B6')])
            else:
                raise ValueError(f"Unsupported vegetation index: {index_type}")
                
        except Exception as e:
            self._logger.error(f"Error calculating vegetation index: {e}")
            raise 