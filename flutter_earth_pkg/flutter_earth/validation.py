import os
import datetime
from typing import List, Tuple, Optional

def validate_bbox(bbox: List[float]) -> bool:
    """Validate a bounding box: [min_lon, min_lat, max_lon, max_lat]."""
    if not isinstance(bbox, list) or len(bbox) != 4:
        return False
    min_lon, min_lat, max_lon, max_lat = bbox
    return (
        -180 <= min_lon < max_lon <= 180 and
        -90 <= min_lat < max_lat <= 90
    )

def validate_polygon(coords: List[List[float]]) -> bool:
    """Validate a polygon as a list of [lon, lat] pairs (at least 3 points, closed)."""
    if not isinstance(coords, list) or len(coords) < 4:
        return False
    if coords[0] != coords[-1]:
        return False  # Not closed
    for pt in coords:
        if not (isinstance(pt, list) and len(pt) == 2):
            return False
        lon, lat = pt
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            return False
    return True

def validate_dates(start: str, end: str) -> Tuple[str, str]:
    """Validate and return (start, end) as ISO date strings."""
    try:
        start_dt = datetime.datetime.fromisoformat(start)
        end_dt = datetime.datetime.fromisoformat(end)
        if start_dt > end_dt:
            raise ValueError("Start date must be before end date.")
        return start_dt.date().isoformat(), end_dt.date().isoformat()
    except Exception as e:
        raise ValueError(f"Invalid date(s): {e}")

def validate_file_path(path: str, must_exist: bool = False, allowed_exts: Optional[List[str]] = None) -> bool:
    """Validate a file path, optionally checking existence and extension."""
    if not isinstance(path, str) or not path:
        return False
    if must_exist and not os.path.exists(path):
        return False
    if allowed_exts:
        ext = os.path.splitext(path)[1].lower()
        if ext not in allowed_exts:
            return False
    return True

def validate_sensor_name(sensor: str, available: List[str]) -> bool:
    """Validate a sensor name against a list of available sensors."""
    return sensor in available 