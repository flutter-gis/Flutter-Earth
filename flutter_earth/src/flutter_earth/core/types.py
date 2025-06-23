"""Core types and data models for Flutter Earth."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Tuple
from pathlib import Path


class DownloadStatus(Enum):
    """Status of a download operation."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputFormat(Enum):
    """Supported output formats."""
    GEOTIFF = "geotiff"
    JPEG = "jpeg"
    PNG = "png"
    SHAPEFILE = "shapefile"
    CSV = "csv"


class VegetationIndex(Enum):
    """Supported vegetation indices."""
    NDVI = "ndvi"
    EVI = "evi"
    SAVI = "savi"
    NDWI = "ndwi"
    NBR = "nbr"


@dataclass
class Coordinates:
    """Geographic coordinates."""
    longitude: float
    latitude: float
    
    def __post_init__(self):
        """Validate coordinates."""
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")


@dataclass
class BoundingBox:
    """Geographic bounding box."""
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    
    def __post_init__(self):
        """Validate bounding box."""
        if self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be less than max_lon")
        if self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be less than max_lat")
        if not -180 <= self.min_lon <= 180 or not -180 <= self.max_lon <= 180:
            raise ValueError("Longitude values must be between -180 and 180")
        if not -90 <= self.min_lat <= 90 or not -90 <= self.max_lat <= 90:
            raise ValueError("Latitude values must be between -90 and 90")
    
    @property
    def width(self) -> float:
        """Get the width of the bounding box in degrees."""
        return self.max_lon - self.min_lon
    
    @property
    def height(self) -> float:
        """Get the height of the bounding box in degrees."""
        return self.max_lat - self.min_lat
    
    @property
    def center(self) -> Coordinates:
        """Get the center coordinates of the bounding box."""
        return Coordinates(
            longitude=(self.min_lon + self.max_lon) / 2,
            latitude=(self.min_lat + self.max_lat) / 2
        )
    
    def to_list(self) -> List[float]:
        """Convert to list format [min_lon, min_lat, max_lon, max_lat]."""
        return [self.min_lon, self.min_lat, self.max_lon, self.max_lat]
    
    @classmethod
    def from_list(cls, coords: List[float]) -> "BoundingBox":
        """Create from list format [min_lon, min_lat, max_lon, max_lat]."""
        if len(coords) != 4:
            raise ValueError("Bounding box must have exactly 4 coordinates")
        return cls(coords[0], coords[1], coords[2], coords[3])


@dataclass
class Polygon:
    """Geographic polygon."""
    coordinates: List[Coordinates]
    
    def __post_init__(self):
        """Validate polygon."""
        if len(self.coordinates) < 3:
            raise ValueError("Polygon must have at least 3 coordinates")
        # Check if first and last coordinates are the same (closed polygon)
        if self.coordinates[0] != self.coordinates[-1]:
            self.coordinates.append(self.coordinates[0])
    
    @property
    def bounding_box(self) -> BoundingBox:
        """Get the bounding box of the polygon."""
        lons = [coord.longitude for coord in self.coordinates]
        lats = [coord.latitude for coord in self.coordinates]
        return BoundingBox(
            min_lon=min(lons),
            min_lat=min(lats),
            max_lon=max(lons),
            max_lat=max(lats)
        )


@dataclass
class SatelliteCollection:
    """Satellite collection information."""
    name: str
    display_name: str
    description: str
    spatial_resolution: float
    temporal_resolution: str
    bands: List[str] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cloud_cover_available: bool = True
    vegetation_indices_supported: bool = True
    
    def __post_init__(self):
        """Validate satellite collection."""
        if not self.name:
            raise ValueError("Satellite collection name cannot be empty")
        if self.spatial_resolution <= 0:
            raise ValueError("Spatial resolution must be positive")


@dataclass
class ProcessingParams:
    """Parameters for image processing."""
    # Area of interest
    area_of_interest: Union[BoundingBox, Polygon]
    
    # Time period
    start_date: datetime
    end_date: datetime
    
    # Satellite collections
    satellite_collections: List[str] = field(default_factory=list)
    
    # Processing options
    output_format: OutputFormat = OutputFormat.GEOTIFF
    spatial_resolution: Optional[float] = None
    max_cloud_cover: float = 20.0
    vegetation_indices: List[VegetationIndex] = field(default_factory=list)
    
    # Output settings
    output_directory: Optional[Path] = None
    filename_prefix: str = "flutter_earth"
    
    # Advanced options
    tiling_enabled: bool = False
    tile_size: int = 512
    compression: str = "lzw"
    
    def __post_init__(self):
        """Validate processing parameters."""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        if not self.satellite_collections:
            raise ValueError("At least one satellite collection must be specified")
        if self.max_cloud_cover < 0 or self.max_cloud_cover > 100:
            raise ValueError("Cloud cover must be between 0 and 100")
        if self.spatial_resolution is not None and self.spatial_resolution <= 0:
            raise ValueError("Spatial resolution must be positive")
        if self.tile_size <= 0:
            raise ValueError("Tile size must be positive")


@dataclass
class ProcessingResult:
    """Result of a processing operation."""
    success: bool
    output_files: List[Path] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    file_size: Optional[int] = None
    
    def __post_init__(self):
        """Validate processing result."""
        if self.success and not self.output_files:
            raise ValueError("Successful processing must have output files")
        if not self.success and not self.error_message:
            raise ValueError("Failed processing must have an error message")


@dataclass
class DownloadTask:
    """A download task."""
    id: str
    params: ProcessingParams
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    result: Optional[ProcessingResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate download task."""
        if not self.id:
            raise ValueError("Download task ID cannot be empty")


@dataclass
class AppConfig:
    """Application configuration."""
    # Earth Engine settings
    earth_engine_project: Optional[str] = None
    service_account_path: Optional[Path] = None
    
    # Processing defaults
    default_resolution: float = 30.0
    default_cloud_cover: float = 20.0
    default_output_format: OutputFormat = OutputFormat.GEOTIFF
    
    # Interface settings
    theme: str = "dark"
    language: str = "en"
    auto_save: bool = True
    max_concurrent_downloads: int = 3
    
    # Output settings
    default_output_directory: Optional[Path] = None
    create_subdirectories: bool = True
    
    # Advanced settings
    enable_logging: bool = True
    log_level: str = "INFO"
    cache_directory: Optional[Path] = None 