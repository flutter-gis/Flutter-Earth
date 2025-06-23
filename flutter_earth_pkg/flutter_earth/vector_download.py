import os
import json
import logging
import requests
import shapefile  # pyshp
from typing import List, Dict, Any, Optional

def download_vector_data(aoi: List[float], query: str, output_path: str, output_format: str = 'GeoJSON') -> bool:
    """
    Download vector data from Overpass API for a given AOI and query.
    Args:
        aoi: [min_lon, min_lat, max_lon, max_lat]
        query: Overpass QL query string (should include {{bbox}} placeholder if needed)
        output_path: Path to save the output file
        output_format: 'GeoJSON' or 'Shapefile'
    Returns:
        True if successful, False otherwise
    """
    try:
        # Format query with AOI bbox
        bbox_str = f"{aoi[1]},{aoi[0]},{aoi[3]},{aoi[2]}"  # south,west,north,east
        if '{{bbox}}' in query:
            query = query.replace('{{bbox}}', bbox_str)
        overpass_url = "https://overpass-api.de/api/interpreter"
        response = requests.post(overpass_url, data={'data': query}, timeout=120)
        response.raise_for_status()
        data = response.json()
        # Save as GeoJSON
        if output_format.upper() == 'GEOJSON':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            logging.info(f"GeoJSON saved to {output_path}")
            return True
        # Save as Shapefile
        elif output_format.upper() == 'SHAPEFILE':
            features = data.get('features', [])
            if not features:
                logging.error("No features found in Overpass response.")
                return False
            shp_writer = shapefile.Writer(output_path)
            shp_writer.autoBalance = 1
            # Assume all features are polygons or points for simplicity
            first_geom = features[0]['geometry']['type']
            if first_geom == 'Polygon':
                shp_writer.shapeType = shapefile.POLYGON
            elif first_geom == 'Point':
                shp_writer.shapeType = shapefile.POINT
            else:
                logging.error(f"Unsupported geometry type: {first_geom}")
                return False
            # Add fields
            props = features[0]['properties']
            for key in props:
                shp_writer.field(key, 'C')
            # Add shapes
            for feat in features:
                geom = feat['geometry']
                props = feat['properties']
                if geom['type'] == 'Polygon':
                    shp_writer.poly([geom['coordinates'][0]])
                elif geom['type'] == 'Point':
                    shp_writer.point(*geom['coordinates'])
                else:
                    continue
                shp_writer.record(*[str(props.get(k, '')) for k in props])
            shp_writer.close()
            logging.info(f"Shapefile saved to {output_path}")
            return True
        else:
            logging.error(f"Unsupported output format: {output_format}")
            return False
    except Exception as e:
        logging.error(f"Vector download failed: {e}")
        return False 