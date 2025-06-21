"""Basic tests for Flutter Earth."""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flutter_earth.core.types import BoundingBox, Coordinates, OutputFormat, VegetationIndex
from flutter_earth.utils.validation import validate_bbox, validate_coordinates


def test_bounding_box_creation():
    """Test bounding box creation and validation."""
    bbox = BoundingBox(min_lon=-74.0, min_lat=40.0, max_lon=-73.0, max_lat=41.0)
    
    assert bbox.min_lon == -74.0
    assert bbox.min_lat == 40.0
    assert bbox.max_lon == -73.0
    assert bbox.max_lat == 41.0
    assert bbox.width == 1.0
    assert bbox.height == 1.0


def test_coordinates_validation():
    """Test coordinate validation."""
    assert validate_coordinates(0, 0) == True
    assert validate_coordinates(180, 90) == True
    assert validate_coordinates(-180, -90) == True
    assert validate_coordinates(181, 0) == False
    assert validate_coordinates(0, 91) == False


def test_bbox_validation():
    """Test bounding box validation."""
    assert validate_bbox(-74.0, 40.0, -73.0, 41.0) == True
    assert validate_bbox(-74.0, 40.0, -74.0, 41.0) == False  # Same longitude
    assert validate_bbox(-74.0, 40.0, -73.0, 40.0) == False   # Same latitude
    assert validate_bbox(-73.0, 40.0, -74.0, 41.0) == False   # Wrong order


def test_output_format_enum():
    """Test output format enum."""
    assert OutputFormat.GEOTIFF.value == "geotiff"
    assert OutputFormat.JPEG.value == "jpeg"
    assert OutputFormat.PNG.value == "png"


def test_vegetation_index_enum():
    """Test vegetation index enum."""
    assert VegetationIndex.NDVI.value == "ndvi"
    assert VegetationIndex.EVI.value == "evi"
    assert VegetationIndex.SAVI.value == "savi"


if __name__ == "__main__":
    pytest.main([__file__]) 