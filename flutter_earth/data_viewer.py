"""Data viewer module for Flutter Earth."""
import os
import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams
from .config import config_manager

try:
    import rasterio
    from rasterio.merge import merge
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    logging.warning("Rasterio not available. Raster viewing features will be limited.")

try:
    import shapefile
    SHAPEFILE_AVAILABLE = True
except ImportError:
    SHAPEFILE_AVAILABLE = False
    logging.warning("PyShp not available. Shapefile viewing features will be limited.")

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available. Data viewing features will be limited.")


class DataViewer:
    """Handles raster and vector data visualization."""
    
    def __init__(self):
        """Initialize the data viewer."""
        self.logger = logging.getLogger(__name__)
        self.current_raster_path: Optional[str] = None
        self.vector_layers: List[Dict[str, Any]] = []
        self.figure: Optional[Figure] = None
        self.axes: Optional[matplotlib.axes.Axes] = None
        self.canvas: Optional[FigureCanvas] = None
        
        # Sample data configurations
        self.sample_configs = {
            "jerusalem_sample": {
                "area_name": "Jerusalem",
                "sensor": "SENTINEL2",
                "year": 2024,
                "month": 6,
                "bbox": [35.2, 31.7, 35.3, 31.8],
                "output_subdir": "samples/jerusalem",
                "target_resolution": 10
            },
            "tel_aviv_sample": {
                "area_name": "Tel Aviv",
                "sensor": "LANDSAT_8",
                "year": 2024,
                "month": 6,
                "bbox": [34.7, 32.0, 34.8, 32.1],
                "output_subdir": "samples/tel_aviv",
                "target_resolution": 30
            }
        }
    
    def create_canvas(self, parent=None) -> Optional[FigureCanvas]:
        """Create a matplotlib canvas for data visualization.
        
        Args:
            parent: Parent widget.
        
        Returns:
            Matplotlib canvas or None if matplotlib is not available.
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
        
        try:
            # Create figure and canvas
            self.figure = Figure(figsize=(8, 6), dpi=100)
            self.axes = self.figure.add_subplot(111)
            self.canvas = FigureCanvas(self.figure)
            
            # Set up the canvas
            self.canvas.setParent(parent)
            self.canvas.setFocusPolicy(2)  # Qt.StrongFocus
            self.canvas.setFocus()
            
            # Connect mouse events for zooming
            self.canvas.mpl_connect('scroll_event', self._on_scroll_zoom)
            
            return self.canvas
            
        except Exception as e:
            self.logger.error(f"Failed to create matplotlib canvas: {e}")
            return None
    
    def load_raster(self, filepath: str) -> bool:
        """Load a raster file for visualization.
        
        Args:
            filepath: Path to raster file.
        
        Returns:
            True if successful, False otherwise.
        """
        if not RASTERIO_AVAILABLE:
            self.logger.error("Rasterio not available for raster loading")
            return False
        
        if not os.path.exists(filepath):
            self.logger.error(f"Raster file not found: {filepath}")
            return False
        
        try:
            self.current_raster_path = filepath
            self._redraw_display()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load raster {filepath}: {e}")
            return False
    
    def load_vector(self, filepath: str, style: Optional[Dict[str, Any]] = None) -> bool:
        """Load a vector file for visualization.
        
        Args:
            filepath: Path to vector file.
            style: Optional styling parameters.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            geometries = self._parse_vector_file(filepath)
            if geometries:
                # Default style if none provided
                if style is None:
                    style = {
                        'edgecolor': 'cyan',
                        'facecolor': 'none',
                        'linewidth': 1.2,
                        'alpha': 0.75
                    }
                
                self.vector_layers.append({
                    'geometries': geometries,
                    'filepath': filepath,
                    'style': style
                })
                
                self._redraw_display()
                return True
            else:
                self.logger.warning(f"No geometries found in {filepath}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load vector {filepath}: {e}")
            return False
    
    def clear_vectors(self) -> None:
        """Clear all vector layers."""
        self.vector_layers.clear()
        self._redraw_display()
    
    def clear_all(self) -> None:
        """Clear all data (raster and vectors)."""
        self.current_raster_path = None
        self.vector_layers.clear()
        self._redraw_display()
    
    def _parse_vector_file(self, filepath: str) -> List[List[List[float]]]:
        """Parse vector file and extract geometries.
        
        Args:
            filepath: Path to vector file.
        
        Returns:
            List of polygon coordinates.
        """
        ext = Path(filepath).suffix.lower()
        
        if ext == '.shp':
            return self._parse_shapefile(filepath)
        elif ext in ['.geojson', '.json']:
            return self._parse_geojson(filepath)
        else:
            raise ProcessingError(f"Unsupported vector file type: {ext}")
    
    def _parse_shapefile(self, filepath: str) -> List[List[List[float]]]:
        """Parse shapefile and extract geometries.
        
        Args:
            filepath: Path to shapefile.
        
        Returns:
            List of polygon coordinates.
        """
        if not SHAPEFILE_AVAILABLE:
            raise ProcessingError("PyShp not available for shapefile parsing")
        
        geometries = []
        try:
            with shapefile.Reader(filepath) as sf:
                for shape_rec in sf.iterShapes():
                    # We are interested in POLYGON types
                    if shape_rec.shapeType in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM, 5, 15, 25]:
                        part_indices = list(shape_rec.parts) + [len(shape_rec.points)]
                        for i in range(len(part_indices) - 1):
                            start = part_indices[i]
                            end = part_indices[i + 1]
                            part_coords = shape_rec.points[start:end]  # List of [x,y]
                            if len(part_coords) >= 3:  # Need at least 3 points for a polygon
                                geometries.append(part_coords)
        except Exception as e:
            raise ProcessingError(f"Error reading shapefile {filepath}: {e}")
        
        return geometries
    
    def _parse_geojson(self, filepath: str) -> List[List[List[float]]]:
        """Parse GeoJSON and extract geometries.
        
        Args:
            filepath: Path to GeoJSON file.
        
        Returns:
            List of polygon coordinates.
        """
        geometries = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            features_to_process = []
            if geojson_data.get("type") == "FeatureCollection":
                features_to_process = geojson_data.get("features", [])
            elif geojson_data.get("type") == "Feature":
                features_to_process = [geojson_data]
            elif geojson_data.get("type") in ["Polygon", "MultiPolygon"]:
                features_to_process = [{"geometry": geojson_data}]
            
            for feature in features_to_process:
                geom = feature.get("geometry")
                if not geom:
                    continue
                
                geom_type = geom.get("type")
                coordinates = geom.get("coordinates")
                if not coordinates:
                    continue
                
                if geom_type == "Polygon":
                    # Exterior ring: coordinates[0] which is a list of [x,y] points
                    if coordinates and len(coordinates[0]) >= 3:
                        geometries.append(coordinates[0])
                elif geom_type == "MultiPolygon":
                    # List of Polygons; each polygon is a list of rings
                    for polygon_coords_set in coordinates:
                        if polygon_coords_set and len(polygon_coords_set[0]) >= 3:
                            geometries.append(polygon_coords_set[0])
                            
        except Exception as e:
            raise ProcessingError(f"Error parsing GeoJSON {filepath}: {e}")
        
        return geometries
    
    def _scale_band_to_uint8(
        self, 
        band_data: np.ndarray, 
        nodataval: Optional[float] = None, 
        band_name: str = "band"
    ) -> np.ndarray:
        """Scale a band to uint8 for display.
        
        Args:
            band_data: Input band data.
            nodataval: No-data value.
            band_name: Band name for logging.
        
        Returns:
            Scaled uint8 array.
        """
        # Create a mask of valid pixels
        if nodataval is not None:
            valid_pixels_mask = (band_data != nodataval) & np.isfinite(band_data)
        else:
            valid_pixels_mask = np.isfinite(band_data)
        
        valid_pixels = band_data[valid_pixels_mask]
        
        if valid_pixels.size == 0:
            self.logger.debug(f"No valid pixels in {band_name}")
            return np.zeros_like(band_data, dtype=np.uint8)
        
        # Use 2nd and 98th percentiles for robust contrast stretch
        p2, p98 = np.percentile(valid_pixels, (2, 98))
        
        # Handle case where p2 and p98 are equal
        if np.isclose(p2, p98):
            scaled_norm = np.zeros_like(band_data, dtype=float)
            scaled_norm[valid_pixels_mask] = 0.5  # Mid-gray for valid pixels
        else:
            # Apply clipping and scaling
            data_clipped = np.clip(band_data, p2, p98)
            scaled_norm = (data_clipped - p2) / (p98 - p2)
        
        # Convert to uint8
        scaled_uint8 = (np.nan_to_num(scaled_norm, nan=0.0) * 255).astype(np.uint8)
        
        return scaled_uint8
    
    def _redraw_display(self) -> None:
        """Redraw the display with current data."""
        if not self.axes or not self.canvas:
            return
        
        self.axes.clear()
        
        # Draw raster if available
        if self.current_raster_path and os.path.exists(self.current_raster_path):
            try:
                with rasterio.open(self.current_raster_path) as src:
                    if src.count == 0:
                        self.axes.text(0.5, 0.5, "No bands in raster", 
                                     ha='center', va='center', transform=self.axes.transAxes)
                    elif src.count >= 3:
                        # RGB display
                        r_band_raw = src.read(1).astype(np.float32)
                        g_band_raw = src.read(2).astype(np.float32)
                        b_band_raw = src.read(3).astype(np.float32)
                        
                        r_band = self._scale_band_to_uint8(
                            r_band_raw, 
                            src.nodatavals[0] if src.nodatavals and len(src.nodatavals) > 0 else None, 
                            "R"
                        )
                        g_band = self._scale_band_to_uint8(
                            g_band_raw, 
                            src.nodatavals[1] if src.nodatavals and len(src.nodatavals) > 1 else None, 
                            "G"
                        )
                        b_band = self._scale_band_to_uint8(
                            b_band_raw, 
                            src.nodatavals[2] if src.nodatavals and len(src.nodatavals) > 2 else None, 
                            "B"
                        )
                        
                        rgb_image = np.dstack((r_band, g_band, b_band))
                        self.axes.imshow(rgb_image)
                        
                    else:
                        # Grayscale display
                        band_data_raw = src.read(1).astype(np.float32)
                        nodataval = src.nodatavals[0] if src.nodatavals and len(src.nodatavals) > 0 else None
                        scaled_band = self._scale_band_to_uint8(band_data_raw, nodataval, "Grayscale")
                        self.axes.imshow(scaled_band, cmap='gray')
                    
                    self.axes.set_title(Path(self.current_raster_path).name, fontsize=10)
                    
            except Exception as e:
                self.logger.error(f"Error displaying raster: {e}")
                self.axes.text(0.5, 0.5, f"Error displaying raster:\n{str(e)[:50]}...", 
                             color='r', ha='center', va='center', transform=self.axes.transAxes, fontsize=9)
        else:
            self.axes.set_title("Data Viewer", fontsize=10)
        
        # Draw vector overlays
        for layer_data in self.vector_layers:
            style = layer_data.get('style', {
                'edgecolor': 'blue', 
                'facecolor': 'none', 
                'linewidth': 1
            })
            
            for polygon_coords in layer_data['geometries']:
                if polygon_coords and len(polygon_coords) >= 3:
                    poly_patch = patches.Polygon(
                        np.array(polygon_coords), 
                        closed=True, 
                        **style
                    )
                    self.axes.add_patch(poly_patch)
        
        self.axes.set_axis_off()
        
        # Adjust view limits
        if self.current_raster_path:
            # Raster extent is handled by imshow
            pass
        elif self.vector_layers:
            self.axes.autoscale_view()
            self.axes.set_title(f"{len(self.vector_layers)} vector layer(s) loaded", fontsize=10)
        
        self.canvas.draw_idle()
    
    def _on_scroll_zoom(self, event) -> None:
        """Handle mouse scroll event for zooming."""
        if event.inaxes != self.axes or self.axes is None:
            return
        
        zoom_factor = 1.1
        if event.button == 'up':  # Scroll up (zoom in)
            scale_factor = 1 / zoom_factor
        elif event.button == 'down':  # Scroll down (zoom out)
            scale_factor = zoom_factor
        else:
            return
        
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            xdata = (cur_xlim[0] + cur_xlim[1]) / 2
            ydata = (cur_ylim[0] + cur_ylim[1]) / 2
        
        new_xlim = [
            xdata - (xdata - cur_xlim[0]) * scale_factor,
            xdata + (cur_xlim[1] - xdata) * scale_factor
        ]
        new_ylim = [
            ydata - (ydata - cur_ylim[0]) * scale_factor,
            ydata + (cur_ylim[1] - ydata) * scale_factor
        ]
        
        self.axes.set_xlim(new_xlim)
        self.axes.set_ylim(new_ylim)
        self.canvas.draw_idle()
    
    def get_sample_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get available sample configurations.
        
        Returns:
            Dictionary of sample configurations.
        """
        return self.sample_configs.copy()
    
    def load_sample_data(self, sample_key: str, base_path: str) -> Optional[str]:
        """Load sample data if available.
        
        Args:
            sample_key: Sample configuration key.
            base_path: Base path for sample data.
        
        Returns:
            Path to sample file if found, None otherwise.
        """
        if sample_key not in self.sample_configs:
            return None
        
        config = self.sample_configs[sample_key]
        sample_dir = os.path.join(base_path, config["output_subdir"])
        sample_filename = f"{config['area_name']}_{config['sensor']}_{config['year']}-{config['month']:02d}.tif"
        sample_path = os.path.join(sample_dir, sample_filename)
        
        if os.path.exists(sample_path):
            if self.load_raster(sample_path):
                return sample_path
        
        return None
    
    def is_matplotlib_available(self) -> bool:
        """Check if matplotlib is available.
        
        Returns:
            True if matplotlib is available.
        """
        return MATPLOTLIB_AVAILABLE
    
    def is_rasterio_available(self) -> bool:
        """Check if rasterio is available.
        
        Returns:
            True if rasterio is available.
        """
        return RASTERIO_AVAILABLE
    
    def is_shapefile_available(self) -> bool:
        """Check if shapefile library is available.
        
        Returns:
            True if shapefile library is available.
        """
        return SHAPEFILE_AVAILABLE


# Global instance
data_viewer = DataViewer() 