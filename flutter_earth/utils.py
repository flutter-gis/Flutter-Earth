"""Utility functions for Flutter Earth."""
from typing import List, Dict, Any, Union, Tuple
from datetime import datetime, date
import os
import logging
from pathlib import Path
import rasterio
import ee
import requests
from PySide6.QtCore import QObject, Signal

def validate_bbox(bbox: List[float]) -> bool:
    """Validate bounding box coordinates."""
    if len(bbox) != 4:
        return False
    west, south, east, north = bbox
    return (-180 <= west <= 180 and
            -90 <= south <= 90 and
            -180 <= east <= 180 and
            -90 <= north <= 90 and
            west < east and
            south < north)

def validate_dates(start_date: Union[str, datetime, date],
                  end_date: Union[str, datetime, date]) -> Tuple[datetime, datetime]:
    """Validate and convert date strings to datetime objects."""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, datetime.min.time())
    if isinstance(end_date, date):
        end_date = datetime.combine(end_date, datetime.min.time())
    
    if start_date > end_date:
        raise ValueError("Start date must be before end date")
    if end_date > datetime.now():
        raise ValueError("End date cannot be in the future")
    
    return start_date, end_date

def create_output_dir(base_dir: str) -> str:
    """Create and return output directory path."""
    output_dir = Path(base_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)

def get_sensor_details(sensor_name: str) -> Dict[str, Any]:
    """Get details for a specific satellite sensor."""
    # This would typically come from a configuration file
    SENSOR_DETAILS = {
        'LANDSAT_9': {
            'collection_id': 'LANDSAT/LC09/C02/T1_L2',
            'resolution': 30,
            'bands': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
            'cloud_cover': True
        },
        'SENTINEL_2': {
            'collection_id': 'COPERNICUS/S2_SR_HARMONIZED',
            'resolution': 10,
            'bands': ['B2', 'B3', 'B4', 'B8'],
            'cloud_cover': True
        }
    }
    return SENSOR_DETAILS.get(sensor_name, {})

def process_image(image: ee.Image, params: Dict[str, Any]) -> ee.Image:
    """Process Earth Engine image according to parameters."""
    # Apply cloud masking if enabled
    if params.get('cloud_mask'):
        if params['sensor_name'] == 'LANDSAT_9':
            qa = image.select('QA_PIXEL')
            cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)
            shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)
            image = image.updateMask(cloud_mask.And(shadow_mask))
        elif params['sensor_name'] == 'SENTINEL_2':
            qa = image.select('QA60')
            cloud_mask = qa.bitwiseAnd(1 << 10).eq(0)
            image = image.updateMask(cloud_mask)
    
    return image

def save_image(image: ee.Image, output_path: str, bbox: List[float], 
               resolution: int) -> None:
    """Save Earth Engine image to file."""
    try:
        url = image.getDownloadURL({
            'region': bbox,
            'scale': resolution,
            'format': 'GeoTIFF'
        })
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
    except Exception as e:
        logging.error(f"Failed to save image: {e}")
        raise

def calculate_tiles(bbox: List[float], tile_size: float) -> List[Dict[str, Any]]:
    """Calculate tile definitions for a bounding box."""
    west, south, east, north = bbox
    tiles = []
    
    current_west = west
    while current_west < east:
        current_south = south
        while current_south < north:
            tile_east = min(current_west + tile_size, east)
            tile_north = min(current_south + tile_size, north)
            
            tiles.append({
                'bbox': [current_west, current_south, tile_east, tile_north],
                'index': len(tiles)
            })
            
            current_south = tile_north
        current_west = min(current_west + tile_size, east)
    
    return tiles

def merge_tiles(tile_paths: List[str], output_path: str) -> None:
    """Merge multiple GeoTIFF tiles into a single file."""
    try:
        sources = [rasterio.open(p) for p in tile_paths]
        
        # Merge tiles
        mosaic, transform = merge(sources)
        
        # Get metadata from first tile
        meta = sources[0].meta.copy()
        meta.update({
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": transform
        })
        
        # Write merged file
        with rasterio.open(output_path, "w", **meta) as dest:
            dest.write(mosaic)
            
    finally:
        for src in sources:
            src.close()

def cleanup_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files."""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logging.warning(f"Failed to remove temporary file {path}: {e}")

class QtLogHandler(QObject, logging.Handler):
    log_signal = Signal(str)

    def __init__(self, level=logging.INFO):
        QObject.__init__(self)
        logging.Handler.__init__(self, level)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

def setup_logging(log_file: str = 'flutter_earth.log', gui_handler: QtLogHandler = None, level=logging.INFO):
    """Configure logging for both file and GUI output."""
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # File handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # GUI handler
    if gui_handler is not None:
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
    # Also add a stream handler for console output
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger

# Usage in GUI:
# log_handler = QtLogHandler()
# log_handler.log_signal.connect(your_qtextedit_append_function)
# setup_logging(gui_handler=log_handler) 