"""File utility functions for Flutter Earth."""

import os
from pathlib import Path
from typing import Union, List, Tuple, Optional
from datetime import datetime, date


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path.
        
    Returns:
        Path object for the directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        File size in bytes.
    """
    return Path(file_path).stat().st_size


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes.
        
    Returns:
        Formatted file size string.
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def get_unique_filename(base_path: Path, filename: str) -> Path:
    """Get a unique filename by appending a number if necessary.
    
    Args:
        base_path: Base directory path.
        filename: Base filename.
        
    Returns:
        Unique file path.
    """
    file_path = base_path / filename
    
    if not file_path.exists():
        return file_path
    
    # Split filename and extension
    stem = file_path.stem
    suffix = file_path.suffix
    
    counter = 1
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = base_path / new_filename
        
        if not new_path.exists():
            return new_path
        
        counter += 1


def cleanup_temp_files(temp_dir: Path) -> None:
    """Clean up temporary files in a directory.
    
    Args:
        temp_dir: Temporary directory path.
    """
    if not temp_dir.exists():
        return
    
    try:
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                cleanup_temp_files(file_path)
                file_path.rmdir()
    except Exception:
        # Ignore errors during cleanup
        pass


def validate_bbox(bbox: List[float]) -> bool:
    """Validate bounding box coordinates.
    
    Args:
        bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
        
    Returns:
        True if valid, False otherwise
    """
    if len(bbox) != 4:
        return False
    
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Check coordinate ranges
    if not (-180 <= min_lon <= 180) or not (-180 <= max_lon <= 180):
        return False
    if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
        return False
    
    # Check logical order
    if min_lon >= max_lon or min_lat >= max_lat:
        return False
    
    return True


def validate_dates(start_date: Union[str, date], end_date: Union[str, date]) -> None:
    """Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Raises:
        ValueError: If dates are invalid
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")
    
    if start_date < date(1972, 1, 1):  # Landsat 1 launch
        raise ValueError("Start date too early - no satellite data available")
    
    if end_date > date.today():
        raise ValueError("End date cannot be in the future")


def create_output_dir(output_path: Union[str, Path]) -> Path:
    """Create output directory if it doesn't exist.
    
    Args:
        output_path: Output directory path
        
    Returns:
        Path object for the output directory
    """
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def get_sensor_details(sensor_name: str) -> Optional[dict]:
    """Get sensor details by name.
    
    Args:
        sensor_name: Name of the sensor
        
    Returns:
        Sensor details dictionary or None if not found
    """
    # Define available sensors
    sensors = {
        'LANDSAT_8': {
            'name': 'LANDSAT_8',
            'display_name': 'Landsat 8',
            'spatial_resolution': 30,
            'temporal_resolution': 16,
            'bands': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
        },
        'LANDSAT_9': {
            'name': 'LANDSAT_9',
            'display_name': 'Landsat 9',
            'spatial_resolution': 30,
            'temporal_resolution': 16,
            'bands': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
        },
        'SENTINEL_2': {
            'name': 'SENTINEL_2',
            'display_name': 'Sentinel-2',
            'spatial_resolution': 10,
            'temporal_resolution': 5,
            'bands': ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']
        }
    }
    
    return sensors.get(sensor_name.upper())


def process_image(image_data: bytes, output_path: Path) -> bool:
    """Process image data and save to file.
    
    Args:
        image_data: Raw image data
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(output_path, 'wb') as f:
            f.write(image_data)
        return True
    except Exception:
        return False


def save_image(image_data: bytes, output_path: Path) -> bool:
    """Save image data to file.
    
    Args:
        image_data: Raw image data
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    return process_image(image_data, output_path)


def calculate_tiles(bbox: List[float], tile_size: int = 256) -> List[Tuple[int, int, int, int]]:
    """Calculate tile definitions for a bounding box.
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        tile_size: Size of each tile in pixels
        
    Returns:
        List of tile definitions (x, y, width, height)
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Calculate number of tiles needed
    width = max_lon - min_lon
    height = max_lat - min_lat
    
    num_tiles_x = int(width / (tile_size / 1000)) + 1  # Rough approximation
    num_tiles_y = int(height / (tile_size / 1000)) + 1
    
    tiles = []
    for x in range(num_tiles_x):
        for y in range(num_tiles_y):
            tiles.append((x, y, tile_size, tile_size))
    
    return tiles


def merge_tiles(tile_paths: List[Path], output_path: Path) -> bool:
    """Merge multiple tile files into a single output file.
    
    Args:
        tile_paths: List of tile file paths
        output_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Simple concatenation for now - in practice you'd want proper image stitching
        with open(output_path, 'wb') as outfile:
            for tile_path in tile_paths:
                if tile_path.exists():
                    with open(tile_path, 'rb') as infile:
                        outfile.write(infile.read())
        return True
    except Exception:
        return False 