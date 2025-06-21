"""Validation utility functions for Flutter Earth."""

from datetime import datetime
from typing import Union, List, Tuple


def validate_coordinates(longitude: float, latitude: float) -> bool:
    """Validate geographic coordinates.
    
    Args:
        longitude: Longitude value.
        latitude: Latitude value.
        
    Returns:
        True if coordinates are valid.
    """
    return -180 <= longitude <= 180 and -90 <= latitude <= 90


def validate_bbox(min_lon: float, min_lat: float, max_lon: float, max_lat: float) -> bool:
    """Validate bounding box coordinates.
    
    Args:
        min_lon: Minimum longitude.
        min_lat: Minimum latitude.
        max_lon: Maximum longitude.
        max_lat: Maximum latitude.
        
    Returns:
        True if bounding box is valid.
    """
    if not all(validate_coordinates(lon, lat) for lon, lat in [(min_lon, min_lat), (max_lon, max_lat)]):
        return False
    
    if min_lon >= max_lon or min_lat >= max_lat:
        return False
    
    return True


def validate_dates(start_date: Union[str, datetime], end_date: Union[str, datetime]) -> bool:
    """Validate date range.
    
    Args:
        start_date: Start date.
        end_date: End date.
        
    Returns:
        True if date range is valid.
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
        
        return start_date < end_date
    except (ValueError, TypeError):
        return False


def validate_polygon(coordinates: List[Tuple[float, float]]) -> bool:
    """Validate polygon coordinates.
    
    Args:
        coordinates: List of (longitude, latitude) coordinate pairs.
        
    Returns:
        True if polygon is valid.
    """
    if len(coordinates) < 3:
        return False
    
    # Check if all coordinates are valid
    for lon, lat in coordinates:
        if not validate_coordinates(lon, lat):
            return False
    
    # Check if polygon is closed (first and last points are the same)
    if coordinates[0] != coordinates[-1]:
        return False
    
    return True


def validate_satellite_collection(collection_name: str) -> bool:
    """Validate satellite collection name.
    
    Args:
        collection_name: Collection name.
        
    Returns:
        True if collection name is valid.
    """
    valid_collections = [
        "LANDSAT/LC08/C02/T1_L2",
        "LANDSAT/LE07/C02/T1_L2",
        "COPERNICUS/S2_SR_HARMONIZED",
        "MODIS/006/MOD13Q1"
    ]
    
    return collection_name in valid_collections


def validate_output_format(format_name: str) -> bool:
    """Validate output format.
    
    Args:
        format_name: Output format name.
        
    Returns:
        True if format is valid.
    """
    valid_formats = ["geotiff", "jpeg", "png", "shapefile", "csv"]
    return format_name.lower() in valid_formats


def validate_vegetation_index(index_name: str) -> bool:
    """Validate vegetation index name.
    
    Args:
        index_name: Vegetation index name.
        
    Returns:
        True if index is valid.
    """
    valid_indices = ["ndvi", "evi", "savi", "ndwi", "nbr"]
    return index_name.lower() in valid_indices


def validate_cloud_cover(cloud_cover: float) -> bool:
    """Validate cloud cover percentage.
    
    Args:
        cloud_cover: Cloud cover percentage.
        
    Returns:
        True if cloud cover is valid.
    """
    return 0 <= cloud_cover <= 100


def validate_resolution(resolution: float) -> bool:
    """Validate spatial resolution.
    
    Args:
        resolution: Spatial resolution in meters.
        
    Returns:
        True if resolution is valid.
    """
    return resolution > 0 and resolution <= 1000 