"""Type definitions for Flutter Earth."""
from typing import TypedDict, List, Dict, Union, Optional, Tuple, Any, Literal, Callable
from datetime import datetime, date
from dataclasses import dataclass
import ee

__all__ = [
    'SatelliteDetails', 'ProcessingParams', 'TileDefinition',
    'ProcessingResult', 'AppConfig', 'BBox', 'Coordinates',
    'PolygonCoords', 'GeoJSON', 'EEImage', 'EEFeature', 'EEFeatureCollection',
    'Environment', 'Theme', 'ValidationRule'
]

# Environment and theme types
Environment = Literal['development', 'production', 'test']
Theme = Literal['system', 'light', 'dark']

# Type aliases with more specific definitions
BBox = Tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
Coordinates = Tuple[float, float]  # (lon, lat)
PolygonCoords = List[Coordinates]

# Additional type aliases for common operations
DateLike = Union[datetime, date, str]
BandList = List[str]
ScaleDict = Dict[str, float]

# Earth Engine types with proper typing
EEImage = ee.Image  # type: ignore
EEFeature = ee.Feature  # type: ignore
EEFeatureCollection = ee.FeatureCollection  # type: ignore
CloudMaskFunction = Callable[[EEImage], EEImage]
ProcessingFunction = Callable[[EEImage, 'ProcessingParams'], EEImage]

class ValidationRule:
    """Rule for validating configuration values."""
    def __init__(self, type: Union[type, Tuple[type, ...]], required: bool = False, min_value: Optional[Union[int, float]] = None,
                 max_value: Optional[Union[int, float]] = None, allowed_values: Optional[List[Any]] = None):
        self.type = type
        self.required = required
        self.min_value = min_value
        self.max_value = max_value
        self.allowed_values = allowed_values
    
    def validate(self, value: Any) -> bool:
        """Validate a value against this rule."""
        if value is None:
            return not self.required

        if isinstance(self.type, tuple):
            if not any(isinstance(value, t) for t in self.type):
                return False
        elif not isinstance(value, self.type):
            return False
            
        if self.min_value is not None and value < self.min_value:
            return False
            
        if self.max_value is not None and value > self.max_value:
            return False
            
        if self.allowed_values is not None and value not in self.allowed_values:
            return False
            
        return True

class SatelliteDetails(TypedDict):
    """Details about a satellite sensor."""
    name: str
    description: str
    resolution_nominal: str
    bands: List[str]
    start_date: str
    end_date: str
    cloud_cover: bool
    collection_id: str

class ProcessingParams(TypedDict, total=False):
    """Parameters for satellite data processing.
    
    Note: total=False means all fields are optional.
    """
    area_of_interest: Union[List[float], str]  # bbox or WKT string
    start_date: Union[datetime, date]
    end_date: Union[datetime, date]
    sensor_name: str
    output_dir: str
    cloud_mask: bool
    max_cloud_cover: float
    resolution: Optional[float]
    tile_size: float
    overlap: float
    bands: Optional[List[str]]
    scale_values: bool
    apply_mask: bool
    output_format: Literal['GeoTIFF', 'PNG', 'JPEG']
    projection: Optional[str]
    resampling: Literal['bilinear', 'bicubic', 'nearest']

class TileDefinition(TypedDict):
    """Definition of a tile for processing."""
    bbox: List[float]  # [min_lon, min_lat, max_lon, max_lat]
    index: int
    output_path: str
    overlap: Optional[Dict[str, float]]  # Overlap with adjacent tiles

class ProcessingResult(TypedDict, total=False):
    """Result of processing a tile.
    
    Note: total=False means all fields are optional except success.
    """
    success: bool  # Required
    message: str
    tile_index: int
    output_path: str
    error: Exception
    processing_time: float
    cloud_cover: float
    pixel_count: int
    bounds: BBox
    metadata: Dict[str, Any]

@dataclass
class AppConfig:
    """Application configuration."""
    output_dir: str
    tile_size: float
    max_workers: int
    cloud_mask: bool
    max_cloud_cover: float
    sensor_priority: List[str]
    recent_directories: List[str]
    theme: str

class GeoJSON(TypedDict):
    """GeoJSON object type."""
    type: Literal['Feature', 'FeatureCollection', 'Point', 'LineString', 'Polygon', 'MultiPoint', 'MultiLineString', 'MultiPolygon']
    geometry: Optional[Dict[str, Any]]
    properties: Optional[Dict[str, Any]]
    features: Optional[List['GeoJSON']]
    coordinates: Optional[Union[Coordinates, List[Coordinates], List[List[Coordinates]]]] 