import os
import logging
import rasterio
import shapefile  # pyshp
import json
from typing import Any, Dict, Optional

def load_raster_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a raster file (GeoTIFF) and return data and metadata."""
    try:
        with rasterio.open(filepath) as src:
            data = src.read()
            meta = src.meta.copy()
        return {'data': data, 'meta': meta}
    except Exception as e:
        logging.error(f"Failed to load raster file {filepath}: {e}")
        return None

def load_vector_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a vector file (Shapefile or GeoJSON) and return features and metadata."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in ['.shp']:
            sf = shapefile.Reader(filepath)
            fields = [f[0] for f in sf.fields[1:]]
            features = []
            for sr in sf.shapeRecords():
                geom = sr.shape.__geo_interface__
                props = dict(zip(fields, sr.record))
                features.append({'geometry': geom, 'properties': props})
            return {'features': features, 'type': 'Shapefile'}
        elif ext in ['.geojson', '.json']:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {'features': data.get('features', []), 'type': 'GeoJSON'}
        else:
            logging.error(f"Unsupported vector file type: {ext}")
            return None
    except Exception as e:
        logging.error(f"Failed to load vector file {filepath}: {e}")
        return None

def get_file_metadata(filepath: str) -> Optional[Dict[str, Any]]:
    """Extract metadata from a raster or vector file."""
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in ['.tif', '.tiff']:
            with rasterio.open(filepath) as src:
                return src.meta.copy()
        elif ext in ['.shp']:
            sf = shapefile.Reader(filepath)
            return {'num_features': len(sf), 'fields': sf.fields[1:]}
        elif ext in ['.geojson', '.json']:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {'num_features': len(data.get('features', [])), 'crs': data.get('crs', None)}
        else:
            logging.error(f"Unsupported file type for metadata: {ext}")
            return None
    except Exception as e:
        logging.error(f"Failed to extract metadata from {filepath}: {e}")
        return None 