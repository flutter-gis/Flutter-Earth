"""Vector data download module for Flutter Earth."""
import os
import logging
import json
import requests
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import tempfile
import zipfile

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams
from .config import config_manager

try:
    import overpass
    OVERPASS_AVAILABLE = True
except ImportError:
    OVERPASS_AVAILABLE = False
    logging.warning("Overpass library not available. Vector download features will be limited.")


class VectorDownloader:
    """Handles vector data downloads from various sources."""
    
    def __init__(self):
        """Initialize the vector downloader."""
        self.logger = logging.getLogger(__name__)
        self.current_task: Optional[str] = None
        self.cancel_requested = False
        
        # Initialize Overpass API if available
        if OVERPASS_AVAILABLE:
            try:
                self.overpass_api = overpass.API(timeout=300)
            except Exception as e:
                logging.warning(f"Failed to initialize Overpass API: {e}")
                self.overpass_api = None
        else:
            self.overpass_api = None
    
    def request_cancel(self) -> None:
        """Request cancellation of current processing task."""
        self.cancel_requested = True
        logging.info("Vector download cancellation requested.")
    
    @handle_errors()
    def download_vector_data(
        self,
        source_type: str,
        source_url: str,
        output_dir: str,
        output_format: str,
        aoi_coords: Optional[Union[str, List[List[float]]]] = None,
        predefined_features: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Download vector data from various sources.
        
        Args:
            source_type: Type of data source ("Overpass API", "WFS", "GeoJSON URL").
            source_url: Source URL or query.
            output_dir: Output directory.
            output_format: Output format ("GeoJSON", "Shapefile", "KML", "GPKG").
            aoi_coords: Area of interest coordinates.
            predefined_features: List of predefined OSM features.
            progress_callback: Optional progress callback.
        
        Returns:
            Download result.
        """
        self.cancel_requested = False
        self.current_task = f"Downloading {source_type}"
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            if source_type == "Overpass API (OSM)":
                return self._download_overpass_data(
                    source_url, output_dir, output_format, 
                    aoi_coords, predefined_features, progress_callback
                )
            elif source_type == "WFS (Web Feature Service)":
                return self._download_wfs_data(
                    source_url, output_dir, output_format, 
                    aoi_coords, progress_callback
                )
            elif source_type == "Direct GeoJSON URL":
                return self._download_geojson_url(
                    source_url, output_dir, output_format, 
                    progress_callback
                )
            else:
                raise ProcessingError(f"Unsupported source type: {source_type}")
                
        finally:
            self.current_task = None
    
    def _download_overpass_data(
        self,
        query: str,
        output_dir: str,
        output_format: str,
        aoi_coords: Optional[Union[str, List[List[float]]]] = None,
        predefined_features: Optional[List[str]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Download data from Overpass API.
        
        Args:
            query: Overpass query or None for predefined features.
            output_dir: Output directory.
            output_format: Output format.
            aoi_coords: Area of interest coordinates.
            predefined_features: List of predefined features.
            progress_callback: Progress callback.
        
        Returns:
            Download result.
        """
        if not OVERPASS_AVAILABLE or not self.overpass_api:
            raise ProcessingError("Overpass API not available")
        
        try:
            # Build query if using predefined features
            if predefined_features:
                query = self._build_predefined_query(predefined_features, aoi_coords)
            
            # Replace bbox placeholder if present
            if query and "{{bbox}}" in query and aoi_coords:
                bbox_param = self._format_bbox_for_overpass(aoi_coords)
                query = query.replace("{{bbox}}", bbox_param)
            
            if progress_callback:
                progress_callback(0.2, "Executing Overpass query...")
            
            # Execute query
            geojson_data = self.overpass_api.get(
                query, 
                build=True, 
                verbosity='geom', 
                responseformat="geojson"
            )
            
            if progress_callback:
                progress_callback(0.6, "Processing results...")
            
            # Save as GeoJSON (primary format for Overpass)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            feature_name = "_".join(predefined_features) if predefined_features else "custom_query"
            base_filename = f"osm_{feature_name}_{timestamp}"
            
            geojson_path = os.path.join(output_dir, f"{base_filename}.geojson")
            
            with open(geojson_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2)
            
            if progress_callback:
                progress_callback(0.8, "Converting format...")
            
            # Convert to other formats if requested
            output_files = [geojson_path]
            if output_format != "GeoJSON":
                converted_path = self._convert_geojson_to_format(
                    geojson_path, output_dir, output_format, base_filename
                )
                if converted_path:
                    output_files.append(converted_path)
            
            if progress_callback:
                progress_callback(1.0, "Download complete")
            
            return {
                'success': True,
                'message': f"Successfully downloaded {len(geojson_data.get('features', []))} features",
                'output_files': output_files,
                'feature_count': len(geojson_data.get('features', [])),
                'error': None
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Overpass download failed: {str(e)}",
                details={"error": str(e), "query": query}
            )
    
    def _build_predefined_query(
        self, 
        features: List[str], 
        aoi_coords: Optional[Union[str, List[List[float]]]] = None
    ) -> str:
        """Build Overpass query for predefined features.
        
        Args:
            features: List of feature types.
            aoi_coords: Area of interest coordinates.
        
        Returns:
            Overpass query string.
        """
        bbox_param = self._format_bbox_for_overpass(aoi_coords) if aoi_coords else ""
        
        feature_queries = []
        for feature in features:
            if feature == "roads":
                feature_queries.append(f'way["highway"]{bbox_param};')
            elif feature == "buildings":
                feature_queries.append(f'way["building"]{bbox_param};')
            elif feature == "waterways":
                feature_queries.append(f'way["waterway"]{bbox_param};')
            elif feature == "landuse":
                feature_queries.append(f'way["landuse"]{bbox_param};')
            elif feature == "natural":
                feature_queries.append(f'way["natural"]{bbox_param};')
        
        if not feature_queries:
            raise ProcessingError("No valid predefined features selected")
        
        way_queries_str = "\n  ".join(feature_queries)
        return f"""(
  {way_queries_str}
  node(w);
);"""
    
    def _format_bbox_for_overpass(
        self, 
        aoi_coords: Union[str, List[List[float]]]
    ) -> str:
        """Format AOI coordinates for Overpass API.
        
        Args:
            aoi_coords: AOI coordinates as string or list.
        
        Returns:
            Formatted bbox string for Overpass.
        """
        if isinstance(aoi_coords, str):
            # Parse bbox string "minLon,minLat,maxLon,maxLat"
            try:
                coords = [float(c.strip()) for c in aoi_coords.split(',')]
                if len(coords) == 4:
                    return f"({coords[1]},{coords[0]},{coords[3]},{coords[2]})"
            except (ValueError, TypeError):
                pass
        
        elif isinstance(aoi_coords, list) and len(aoi_coords) >= 3:
            # Polygon coordinates [[lon,lat], [lon,lat], ...]
            try:
                lons = [p[0] for p in aoi_coords]
                lats = [p[1] for p in aoi_coords]
                return f'(poly:"{" ".join([f"{lat} {lon}" for lon, lat in zip(lons, lats)])}")'
            except (IndexError, TypeError):
                pass
        
        raise ProcessingError("Invalid AOI coordinates format")
    
    def _download_wfs_data(
        self,
        wfs_url: str,
        output_dir: str,
        output_format: str,
        aoi_coords: Optional[Union[str, List[List[float]]]] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Download data from WFS service.
        
        Args:
            wfs_url: WFS service URL.
            output_dir: Output directory.
            output_format: Output format.
            aoi_coords: Area of interest coordinates.
            progress_callback: Progress callback.
        
        Returns:
            Download result.
        """
        try:
            if progress_callback:
                progress_callback(0.1, "Connecting to WFS service...")
            
            # Parse WFS URL and extract service parameters
            from urllib.parse import urlparse, parse_qs
            
            parsed_url = urlparse(wfs_url)
            params = parse_qs(parsed_url.query)
            
            # Get WFS parameters
            service = params.get('SERVICE', ['WFS'])[0]
            version = params.get('VERSION', ['1.1.0'])[0]
            request = params.get('REQUEST', ['GetFeature'])[0]
            type_name = params.get('TYPENAME', [''])[0]
            
            if not type_name:
                raise ProcessingError("TYPENAME parameter is required for WFS requests")
            
            # Build WFS request
            wfs_params = {
                'SERVICE': service,
                'VERSION': version,
                'REQUEST': request,
                'TYPENAME': type_name,
                'OUTPUTFORMAT': 'application/json' if output_format == 'GeoJSON' else 'GML2'
            }
            
            # Add BBOX filter if AOI is provided
            if aoi_coords:
                if isinstance(aoi_coords, str):
                    # Parse bbox string
                    coords = [float(c.strip()) for c in aoi_coords.split(',')]
                    bbox = f"{coords[0]},{coords[1]},{coords[2]},{coords[3]}"
                else:
                    # Polygon coordinates - use bounding box
                    lons = [p[0] for p in aoi_coords]
                    lats = [p[1] for p in aoi_coords]
                    bbox = f"{min(lons)},{min(lats)},{max(lons)},{max(lats)}"
                
                wfs_params['BBOX'] = bbox
            
            if progress_callback:
                progress_callback(0.3, "Executing WFS request...")
            
            # Make WFS request
            response = requests.get(wfs_url, params=wfs_params, timeout=300)
            response.raise_for_status()
            
            if progress_callback:
                progress_callback(0.6, "Processing WFS response...")
            
            # Parse response
            content_type = response.headers.get('content-type', '')
            
            if 'json' in content_type or output_format == 'GeoJSON':
                # GeoJSON response
                geojson_data = response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"wfs_{type_name}_{timestamp}"
                
                geojson_path = os.path.join(output_dir, f"{base_filename}.geojson")
                
                with open(geojson_path, 'w', encoding='utf-8') as f:
                    json.dump(geojson_data, f, indent=2)
                
                output_files = [geojson_path]
                feature_count = len(geojson_data.get('features', []))
                
            else:
                # GML response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"wfs_{type_name}_{timestamp}"
                
                gml_path = os.path.join(output_dir, f"{base_filename}.gml")
                
                with open(gml_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                output_files = [gml_path]
                feature_count = 0  # Would need to parse GML to count features
            
            if progress_callback:
                progress_callback(1.0, "WFS download complete")
            
            return {
                'success': True,
                'message': f"Successfully downloaded WFS data from {type_name}",
                'output_files': output_files,
                'feature_count': feature_count,
                'error': None
            }
            
        except Exception as e:
            raise ProcessingError(
                f"WFS download failed: {str(e)}",
                details={"error": str(e), "wfs_url": wfs_url}
            )
    
    def _download_geojson_url(
        self,
        url: str,
        output_dir: str,
        output_format: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Download GeoJSON from URL.
        
        Args:
            url: GeoJSON URL.
            output_dir: Output directory.
            output_format: Output format.
            progress_callback: Progress callback.
        
        Returns:
            Download result.
        """
        try:
            if progress_callback:
                progress_callback(0.3, "Downloading GeoJSON...")
            
            # Download the file
            response = requests.get(url, timeout=300)
            response.raise_for_status()
            
            geojson_data = response.json()
            
            if progress_callback:
                progress_callback(0.6, "Processing data...")
            
            # Save as GeoJSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"geojson_download_{timestamp}"
            
            geojson_path = os.path.join(output_dir, f"{base_filename}.geojson")
            
            with open(geojson_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2)
            
            if progress_callback:
                progress_callback(0.8, "Converting format...")
            
            # Convert to other formats if requested
            output_files = [geojson_path]
            if output_format != "GeoJSON":
                converted_path = self._convert_geojson_to_format(
                    geojson_path, output_dir, output_format, base_filename
                )
                if converted_path:
                    output_files.append(converted_path)
            
            if progress_callback:
                progress_callback(1.0, "Download complete")
            
            return {
                'success': True,
                'message': f"Successfully downloaded {len(geojson_data.get('features', []))} features",
                'output_files': output_files,
                'feature_count': len(geojson_data.get('features', [])),
                'error': None
            }
            
        except Exception as e:
            raise ProcessingError(
                f"GeoJSON download failed: {str(e)}",
                details={"error": str(e), "url": url}
            )
    
    def _convert_geojson_to_format(
        self,
        geojson_path: str,
        output_dir: str,
        target_format: str,
        base_filename: str
    ) -> Optional[str]:
        """Convert GeoJSON to other formats.
        
        Args:
            geojson_path: Path to GeoJSON file.
            output_dir: Output directory.
            target_format: Target format.
            base_filename: Base filename.
        
        Returns:
            Path to converted file or None if conversion failed.
        """
        try:
            if target_format == "Shapefile":
                return self._convert_to_shapefile(geojson_path, output_dir, base_filename)
            elif target_format == "KML":
                return self._convert_to_kml(geojson_path, output_dir, base_filename)
            elif target_format == "GPKG":
                return self._convert_to_gpkg(geojson_path, output_dir, base_filename)
            else:
                logging.warning(f"Unsupported conversion format: {target_format}")
                return None
        except Exception as e:
            logging.error(f"Format conversion failed: {e}")
            return None
    
    def _convert_to_shapefile(
        self, 
        geojson_path: str, 
        output_dir: str, 
        base_filename: str
    ) -> str:
        """Convert GeoJSON to Shapefile."""
        try:
            import geopandas as gpd
            
            # Read GeoJSON
            gdf = gpd.read_file(geojson_path)
            
            # Save as Shapefile
            shp_path = os.path.join(output_dir, f"{base_filename}.shp")
            gdf.to_file(shp_path)
            
            return shp_path
            
        except ImportError:
            logging.warning("Geopandas not available for Shapefile conversion")
            return None
        except Exception as e:
            logging.error(f"Shapefile conversion failed: {e}")
            return None
    
    def _convert_to_kml(
        self, 
        geojson_path: str, 
        output_dir: str, 
        base_filename: str
    ) -> str:
        """Convert GeoJSON to KML."""
        try:
            import geopandas as gpd
            
            # Read GeoJSON
            gdf = gpd.read_file(geojson_path)
            
            # Save as KML
            kml_path = os.path.join(output_dir, f"{base_filename}.kml")
            gdf.to_file(kml_path, driver='KML')
            
            return kml_path
            
        except ImportError:
            logging.warning("Geopandas not available for KML conversion")
            return None
        except Exception as e:
            logging.error(f"KML conversion failed: {e}")
            return None
    
    def _convert_to_gpkg(
        self, 
        geojson_path: str, 
        output_dir: str, 
        base_filename: str
    ) -> str:
        """Convert GeoJSON to GeoPackage."""
        try:
            import geopandas as gpd
            
            # Read GeoJSON
            gdf = gpd.read_file(geojson_path)
            
            # Save as GeoPackage
            gpkg_path = os.path.join(output_dir, f"{base_filename}.gpkg")
            gdf.to_file(gpkg_path, driver='GPKG')
            
            return gpkg_path
            
        except ImportError:
            logging.warning("Geopandas not available for GeoPackage conversion")
            return None
        except Exception as e:
            logging.error(f"GeoPackage conversion failed: {e}")
            return None
    
    def get_available_formats(self) -> List[str]:
        """Get available output formats.
        
        Returns:
            List of available formats.
        """
        return ["GeoJSON", "Shapefile", "KML", "GPKG"]
    
    def get_predefined_features(self) -> List[str]:
        """Get available predefined OSM features.
        
        Returns:
            List of predefined features.
        """
        return ["roads", "buildings", "waterways", "landuse", "natural"]
    
    def is_overpass_available(self) -> bool:
        """Check if Overpass API is available.
        
        Returns:
            True if Overpass API is available.
        """
        return OVERPASS_AVAILABLE and self.overpass_api is not None


# Global instance
vector_downloader = VectorDownloader() 