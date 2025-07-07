"""Custom exceptions and error handling utilities for Flutter Earth."""
from typing import Optional, Any, Dict
import logging
from functools import wraps
import traceback

class FlutterEarthError(Exception):
    """Base exception for Flutter Earth application."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class EarthEngineError(FlutterEarthError):
    """Raised when Earth Engine operations fail."""
    pass

class ProcessingError(FlutterEarthError):
    """Raised when image processing operations fail."""
    pass

class ValidationError(FlutterEarthError):
    """Raised when input validation fails."""
    pass

class ConfigurationError(FlutterEarthError):
    """Raised when configuration is invalid or missing."""
    pass

class NetworkError(FlutterEarthError):
    """Raised when network operations fail."""
    pass

def handle_errors(logger: Optional[logging.Logger] = None):
    """Decorator for handling errors in functions.
    
    Args:
        logger: Optional logger instance. If not provided, uses root logger.
    
    Returns:
        Decorated function that handles errors gracefully.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or logging.getLogger()
            try:
                return func(*args, **kwargs)
            except FlutterEarthError as e:
                log.error(f"{func.__name__} failed: {str(e)}")
                log.debug(f"Error details: {e.details}")
                raise
            except Exception as e:
                log.error(f"Unexpected error in {func.__name__}: {str(e)}")
                log.debug(f"Traceback: {traceback.format_exc()}")
                raise FlutterEarthError(
                    f"Unexpected error in {func.__name__}",
                    details={"original_error": str(e), "traceback": traceback.format_exc()}
                ) from e
        return wrapper
    return decorator

def validate_bbox(bbox: list) -> None:
    """Validates a bounding box.
    
    Args:
        bbox: List of [min_lon, min_lat, max_lon, max_lat]
    
    Raises:
        ValidationError: If bbox is invalid.
    """
    if len(bbox) != 4:
        raise ValidationError("Bounding box must have exactly 4 coordinates")
    
    min_lon, min_lat, max_lon, max_lat = bbox
    
    if not all(isinstance(x, (int, float)) for x in bbox):
        raise ValidationError("All bbox coordinates must be numbers")
    
    if min_lon >= max_lon:
        raise ValidationError(f"Invalid longitude range: {min_lon} >= {max_lon}")
    
    if min_lat >= max_lat:
        raise ValidationError(f"Invalid latitude range: {min_lat} >= {max_lat}")
    
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise ValidationError("Longitude must be between -180 and 180 degrees")
    
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise ValidationError("Latitude must be between -90 and 90 degrees")

def validate_date_range(start_date: str, end_date: str) -> None:
    """Validates a date range.
    
    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
    
    Raises:
        ValidationError: If date range is invalid.
    """
    from datetime import datetime
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(f"Invalid date format: {str(e)}")
    
    if start > end:
        raise ValidationError(f"Start date {start_date} is after end date {end_date}")
    
    if end > datetime.now():
        raise ValidationError(f"End date {end_date} is in the future") 