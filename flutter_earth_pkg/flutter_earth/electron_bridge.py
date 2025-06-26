import argparse
import json
import sys
import os

# Ensure the script can find other modules in flutter_earth_pkg
# This adds the parent directory of 'flutter_earth' (which is 'flutter_earth_pkg')
# and the 'flutter_earth' directory itself to the Python path.
current_script_path = os.path.dirname(os.path.abspath(__file__))
flutter_earth_pkg_dir = os.path.dirname(current_script_path) # This should be flutter_earth_pkg
sys.path.insert(0, flutter_earth_pkg_dir)
sys.path.insert(0, current_script_path) # To find sibling modules like config, theme_manager

try:
    from flutter_earth.config import ConfigManager
    from flutter_earth.themes import ThemeManager
    from flutter_earth.earth_engine import EarthEngineManager
    from flutter_earth.download_manager import DownloadManager
    from flutter_earth.progress_tracker import ProgressTracker # DownloadManager might use this
    # from flutter_earth.gui import AppBackend # We'll call managers directly
except ImportError as e:
    # Output error as JSON so Electron can try to parse it or catch it
    print(json.dumps({"success": False, "error": f"ImportError in bridge: {e}", "details": str(sys.path)}))
    sys.exit(1)

class ElectronBridge:
    def __init__(self):
        try:
            self.config_manager = ConfigManager()
            self.theme_manager = ThemeManager(config_manager=self.config_manager)
            self.earth_engine_manager = EarthEngineManager() # Initialize GEE
            # Initialize GEE. If it fails (e.g. no auth), many things won't work.
            # The original QML app shows an AuthDialog. Here, errors will bubble up.
            self.earth_engine_manager.initialize() # We might want to expose an 'is_gee_initialized' method

            self.progress_tracker = ProgressTracker() # Assuming DownloadManager needs this
            self.download_manager = DownloadManager(
                config_manager=self.config_manager,
                earth_engine_manager=self.earth_engine_manager,
                progress_tracker=self.progress_tracker
            )
            # Connect signals if DownloadManager emits them and we had a way to forward them
            # (not possible with current simple bridge, relies on polling get_download_status)

        except Exception as e:
            # This error will be caught by the main execution block if it happens during init
            raise Exception(f"Failed to initialize managers in ElectronBridge: {e}")


    def get_all_settings(self, args):
        return self.config_manager.getAllSettings()

    def get_available_themes(self, args):
        return self.theme_manager.get_available_themes_meta()

    def get_current_theme_data(self, args):
        return self.theme_manager.get_current_theme_data()

    def get_current_theme_name(self, args):
        return self.theme_manager.current_theme_name()

    def set_theme(self, args):
        theme_name = args.get('theme_name')
        if not theme_name:
            return {"success": False, "error": "theme_name not provided"}
        self.theme_manager.set_current_theme(theme_name)
        # self.config_manager.set('theme', theme_name) # ThemeManager should handle this
        return {"success": True, "message": f"Theme set to {theme_name}"}

    def get_setting(self, args):
        key = args.get('key')
        if key is None:
            return {"success": False, "error": "key for get_setting not provided"}
        # Return the value directly, not wrapped in a dict, to match QML behavior for simple gets
        # The main.js callPython will wrap this in JSON for transport.
        # If the setting might be complex (dict/list), it will be handled by json.dumps.
        # If setting is not found, ConfigManager.get should return a default (e.g., None or specified default).
        return self.config_manager.get(key)


    def set_setting(self, args):
        key = args.get('key')
        value = args.get('value') # Value will be a string from command line
        if key is None: # Value can be an empty string, but key must exist
            return {"success": False, "error": "key or value not provided for set_setting"}

        # Try to convert common string representations of bool/null if appropriate for the key
        if isinstance(value, str):
            if value.lower() == 'true':
                processed_value = True
            elif value.lower() == 'false':
                processed_value = False
            elif value.lower() == 'null' or value.lower() == 'none': # Allow 'none' as well
                processed_value = None
            else:
                processed_value = value # Keep as string if not a recognized bool/null
        else:
            processed_value = value # Should already be correctly typed if not string (e.g. from JSON parsing)


        theme_suboption_keys = ["use_character_catchphrases", "show_special_icons", "enable_animated_background"]
        if key in theme_suboption_keys:
            # Ensure booleans are actual booleans
            actual_bool_value = processed_value if isinstance(processed_value, bool) else (str(processed_value).lower() == 'true')

            current_suboptions = self.config_manager.get("theme_suboptions", {})
            if isinstance(current_suboptions, str):
                try:
                    current_suboptions = json.loads(current_suboptions)
                except (json.JSONDecodeError, TypeError):
                    current_suboptions = {}

            current_suboptions[key] = actual_bool_value
            self.config_manager.set("theme_suboptions", current_suboptions) # Save the whole dict
            self.theme_manager.set_suboptions(current_suboptions)
            return {"success": True, "message": f"Theme suboption {key} set to {actual_bool_value}"}
        elif key == "theme_suboptions":
            suboptions_dict_to_save = processed_value
            if isinstance(processed_value, str): # If it's a JSON string
                try:
                    suboptions_dict_to_save = json.loads(processed_value)
                except json.JSONDecodeError:
                    return {"success": False, "error": f"Invalid JSON for theme_suboptions: {processed_value}"}

            self.config_manager.set(key, suboptions_dict_to_save)
            self.theme_manager.set_suboptions(suboptions_dict_to_save)
            return {"success": True, "message": "Theme suboptions updated."}
        else:
            self.config_manager.set(key, processed_value)
            return {"success": True, "message": f"Setting {key} set to {processed_value}"}


    def reload_config(self, args):
        self.config_manager.reload_config()
        self.theme_manager.config_manager = self.config_manager
        self.theme_manager.load_themes()
        current_theme_name = self.config_manager.get('theme')
        if current_theme_name:
            self.theme_manager.set_current_theme(current_theme_name)
        return {"success": True, "message": "Configuration reloaded"}

    def clear_cache_and_logs(self, args):
        project_root_guess = os.path.dirname(os.path.dirname(flutter_earth_pkg_dir))

        log_dir_rel_to_bridge = os.path.join(current_script_path, '..', '..', 'logs')
        downloads_dir_rel_to_bridge = os.path.join(current_script_path, '..', '..', 'flutter_earth_downloads') # Example cache dir

        log_dir_abs = os.path.abspath(log_dir_rel_to_bridge)
        downloads_dir_abs = os.path.abspath(downloads_dir_rel_to_bridge)

        deleted_files_count = 0
        errors = []

        def _delete_path(path_to_delete):
            nonlocal deleted_files_count # Use nonlocal for Python 3
            try:
                if os.path.isfile(path_to_delete) or os.path.islink(path_to_delete):
                    os.unlink(path_to_delete)
                    deleted_files_count +=1
                elif os.path.isdir(path_to_delete):
                    import shutil
                    shutil.rmtree(path_to_delete)
                    deleted_files_count +=1
            except Exception as e:
                errors.append(f"Failed to delete {path_to_delete}: {e}")

        # Clean specified directories
        dirs_to_clean = [log_dir_abs, downloads_dir_abs] # Add other cache dirs as needed
        for directory in dirs_to_clean:
            if os.path.exists(directory):
                for item_name in os.listdir(directory):
                    _delete_path(os.path.join(directory, item_name))
            else:
                # Optional: log if a directory doesn't exist, or just skip
                pass

        if errors:
            return {"success": False, "message": f"Cache and logs partially cleared with errors: {'; '.join(errors)}. Deleted {deleted_files_count} items."}
        return {"success": True, "message": f"Cache and logs cleared. Deleted {deleted_files_count} items."}

    def get_changelog(self, args):
        # This should point to the actual CHANGELOG.md at the project root
        project_root = os.path.dirname(os.path.dirname(flutter_earth_pkg_dir)) # Assumes flutter_earth_pkg is one level down from root
        changelog_path = os.path.join(project_root, 'CHANGELOG.md')

        if not os.path.exists(changelog_path):
            return "CHANGELOG.md not found at expected location."
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                # QML version returned first 30 lines. We can do the same or return full.
                # For Electron, maybe more is fine, or it can be truncated in JS if needed.
                lines = f.readlines()
            return ''.join(lines[:30]) + ("..." if len(lines) > 30 else "") # Mimic QML behavior
        except Exception as e:
            return f"Error reading changelog: {e}"

    def get_connection_status(self, args):
        # This is a placeholder. In a real application, this would check
        # the actual status of Google Earth Engine initialization or other critical connections.
        # For now, we'll simulate it based on whether config_manager is available,
        # which is a very basic check.
        # A more robust check would involve self.earth_engine_manager.check_service_status() or similar
        if hasattr(self, 'earth_engine_manager') and self.earth_engine_manager and self.earth_engine_manager.initialized:
            return {"status": "online", "message": "Earth Engine connection is active."}
        elif self.config_manager: # Basic check that managers loaded
             # Simulate GEE not being initialized if we don't have earth_engine_manager fully set up here
            return {"status": "offline", "message": "Earth Engine connection is offline or not initialized."}
        else:
            return {"status": "offline", "message": "Backend services not fully initialized."}

    def get_download_status(self, args):
        # Placeholder: In a real app, this would query DownloadManager or ProgressTracker
        # For now, simulate some states. This would be polled by Electron.
        # To make it interesting, let's make it cycle through a few states.
        # This will now try to get real status from ProgressTracker.
        # The cycling simulation was just a placeholder.

        # Get actual progress from ProgressTracker
        progress_info = self.progress_tracker.get_progress() # This was used in AppBackend.getProgress

        # The original QML AppBackend.getDownloadStatus() returned progress_info.get('status', 'idle')
        # And DownloadView.qml listened to onDownloadProgressUpdated(current, total)
        # The ProgressTracker.get_progress() returns a dict like:
        # {'status': 'downloading', 'progress': 0.5, 'message': 'Downloading file 1 of 2',
        #  'current_task_progress': 0.5, 'total_tasks': 2, 'current_task_index': 1}
        # We need to adapt this to what the JS expects or adapt JS.
        # JS (renderer.js for status bar, download.js for its own bar) expects:
        # { status: 'idle'/'downloading'/'processing'/'complete'/'error', progress: 0-100, message: "..." }

        status = progress_info.get('status', 'idle')
        # Progress from tracker is 0.0-1.0, convert to 0-100
        progress_percent = int(progress_info.get('progress', 0.0) * 100)
        message = progress_info.get('message', 'No active downloads.')

        # If there's a more specific current task message, use it or append it
        if 'current_task_message' in progress_info and progress_info['current_task_message']:
            message = progress_info['current_task_message']
        elif 'detailed_status' in progress_info and progress_info['detailed_status']: # from DownloadManager
             message = progress_info['detailed_status']


        return {"status": status, "progress": progress_percent, "message": message}

    def get_all_sensors(self, args):
        # This mirrors AppBackend.getAllSensors()
        return [
            "LANDSAT_8", "LANDSAT_9", "SENTINEL_2", "SENTINEL_1",
            "MODIS", "VIIRS", "CBERS_4", "CBERS_4A"
        ]

    def start_download_with_params(self, args):
        # Args are expected to be a dictionary of parameters passed from Electron.
        # Electron's callPython sends them as --key value. Here they are parsed into args dict.

        # Basic check for GEE initialization
        if not self.earth_engine_manager.initialized:
            return {"success": False, "error": "Earth Engine not initialized. Please check authentication."}

        # Parameter names in 'args' should match what `download_manager.process_request` expects
        # or what `AppBackend.startDownloadWithParams` QML slot processed.
        # The QML slot did some parsing, e.g. for AOI string.
        # We need to replicate that parsing if JS sends strings for numbers/bools.

        params = {}
        try:
            raw_aoi = args.get('area_of_interest')
            if isinstance(raw_aoi, str):
                if '[' in raw_aoi: # JSON list
                    params['area_of_interest'] = json.loads(raw_aoi)
                else: # comma separated lon,lat,lon,lat
                    params['area_of_interest'] = [float(x.strip()) for x in raw_aoi.split(',')]
            elif isinstance(raw_aoi, list): # Already a list
                 params['area_of_interest'] = raw_aoi
            else:
                return {"success": False, "error": "Invalid AOI format. Expected string or list."}

            params['start_date'] = args.get('start_date')
            params['end_date'] = args.get('end_date')
            params['sensor_name'] = args.get('sensor_name')
            params['output_dir'] = args.get('output_dir')

            # Convert string "true"/"false" to boolean for checkboxes
            params['cloud_mask'] = str(args.get('cloud_mask', 'false')).lower() == 'true'
            params['use_best_resolution'] = str(args.get('use_best_resolution', 'true')).lower() == 'true'
            params['overwrite_existing'] = str(args.get('overwrite_existing', 'false')).lower() == 'true'
            params['cleanup_tiles'] = str(args.get('cleanup_tiles', 'true')).lower() == 'true'

            # Convert numbers
            params['max_cloud_cover'] = float(args.get('max_cloud_cover', 20))
            params['target_resolution'] = int(args.get('target_resolution', 30))
            params['num_subsections'] = int(args.get('num_subsections', 100))

            params['tiling_method'] = args.get('tiling_method', 'degree')

            # Validate required params (simple check)
            required_keys = ['area_of_interest', 'start_date', 'end_date', 'sensor_name', 'output_dir']
            for key in required_keys:
                if not params.get(key):
                    return {"success": False, "error": f"Missing required parameter: {key}"}

        except Exception as e:
            return {"success": False, "error": f"Parameter parsing error: {str(e)}"}

        try:
            # process_request might run in a thread if it's long-running.
            # The current bridge is synchronous, so if process_request blocks, Electron waits.
            # DownloadManager is designed to be somewhat asynchronous internally.
            result = self.download_manager.process_request(params)

            if result and result.get("status") == "error":
                return {"success": False, "error": result.get('message', "Unknown error during download processing.")}
            elif result: # Success or task submitted
                return {"success": True, "message": "Download request processed.", "details": result}
            else: # Should not happen if process_request always returns something
                return {"success": False, "error": "Download processing did not return a conclusive result."}

        except Exception as e:
            # Log the full traceback for debugging on the Python side might be useful
            # import traceback
            # traceback.print_exc()
            return {"success": False, "error": f"Error during download process: {str(e)}"}


    def cancel_download(self, args):
        try:
            self.download_manager.request_cancel()
            return {"success": True, "message": "Download cancellation requested."}
        except Exception as e:
            return {"success": False, "error": f"Error requesting download cancellation: {str(e)}"}

    def get_download_history(self, args):
        try:
            history = self.progress_tracker.get_history()
            # Ensure history items are JSON serializable (e.g., datetime objects converted to strings)
            # ProgressTracker.get_history() in QML backend likely already handles this.
            # If not, iterate and convert here. Assuming it's already fine.
            return history # Should be a list of dicts
        except Exception as e:
            return {"success": False, "error": f"Error fetching download history: {str(e)}", "history": []}

    def clear_download_history(self, args):
        try:
            self.progress_tracker.clear_history()
            return {"success": True, "message": "Download history cleared."}
        except Exception as e:
            return {"success": False, "error": f"Error clearing download history: {str(e)}"}

    def get_available_indices(self, args):
        # Mirrors AppBackend.getAvailableIndices()
        # This data can be directly returned as it's usually simple dicts/lists.
        # Make sure processing.py and other dependencies are available if it calls them.
        # For now, using the hardcoded list from AppBackend as an example
        # if the actual processing module is not easily callable here.
        # Ideally, this would call a method in a processing manager.
        return [
            {"name": "NDVI", "full_name": "Normalized Difference Vegetation Index", "formula": "(NIR - Red) / (NIR + Red)", "description": "Measures vegetation health and density", "range": "0 to 1", "bands_required": ["Red", "NIR"]},
            {"name": "EVI", "full_name": "Enhanced Vegetation Index", "formula": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)", "description": "Enhanced version of NDVI with atmospheric correction", "range": "0 to 1", "bands_required": ["Red", "NIR", "Blue"]},
            {"name": "SAVI", "full_name": "Soil Adjusted Vegetation Index", "formula": "1.5 * (NIR - Red) / (NIR + Red + 0.5)", "description": "NDVI adjusted for soil background", "range": "0 to 1", "bands_required": ["Red", "NIR"]},
            {"name": "NDWI", "full_name": "Normalized Difference Water Index", "formula": "(Green - NIR) / (Green + NIR)", "description": "Measures water content in vegetation", "range": "-1 to 1", "bands_required": ["Green", "NIR"]},
            {"name": "NDMI", "full_name": "Normalized Difference Moisture Index", "formula": "(NIR - SWIR1) / (NIR + SWIR1)", "description": "Measures vegetation moisture content", "range": "-1 to 1", "bands_required": ["NIR", "SWIR1"]},
            {"name": "NBR", "full_name": "Normalized Burn Ratio", "formula": "(NIR - SWIR2) / (NIR + SWIR2)", "description": "Measures burn severity and vegetation stress", "range": "-1 to 1", "bands_required": ["NIR", "SWIR2"]},
            {"name": "NDSI", "full_name": "Normalized Difference Snow Index", "formula": "(Green - SWIR1) / (Green + SWIR1)", "description": "Detects snow and ice", "range": "-1 to 1", "bands_required": ["Green", "SWIR1"]},
            {"name": "NDBI", "full_name": "Normalized Difference Built-up Index", "formula": "(SWIR1 - NIR) / (SWIR1 + NIR)", "description": "Detects built-up areas and urban development", "range": "-1 to 1", "bands_required": ["NIR", "SWIR1"]}
        ] # This should ideally come from a shared utility or the processing module itself.

    def start_index_analysis(self, args):
        try:
            from flutter_earth.processing import batch_index_analysis # Assuming this is the correct import

            input_files = args.get('input_files') # Expected to be a list of file paths
            output_dir = args.get('output_dir')
            index_type = args.get('index_type') # e.g., "NDVI"
            band_map_str = args.get('band_map') # Expected to be a JSON string of the band map dict, or already a dict

            if not all([input_files, output_dir, index_type, band_map_str]):
                return {"success": False, "error": "Missing parameters for index analysis."}

            # Ensure input_files is a list
            if isinstance(input_files, str):
                try:
                    input_files = json.loads(input_files) # If sent as JSON string list
                except json.JSONDecodeError:
                    return {"success": False, "error": "input_files parameter is not a valid JSON list string."}
            if not isinstance(input_files, list):
                 return {"success": False, "error": "input_files parameter must be a list."}


            band_map = {}
            if isinstance(band_map_str, str):
                try:
                    band_map = json.loads(band_map_str)
                except json.JSONDecodeError:
                     return {"success": False, "error": "band_map parameter is not a valid JSON string."}
            elif isinstance(band_map_str, dict):
                band_map = band_map_str # Already a dict
            else:
                return {"success": False, "error": "band_map parameter is not a valid dictionary or JSON string."}

            # Call the actual processing function
            # Note: batch_index_analysis might be CPU-intensive. For a responsive UI,
            # this should ideally be run in a separate thread/process in a more complex Python backend,
            # with progress reported back. The current bridge is synchronous.
            results = batch_index_analysis(input_files, output_dir, index_type, band_map)

            # batch_index_analysis from QML AppBackend returned a list of dicts like:
            # [{'file': 'path', 'success': True/False, 'output_path': 'path', 'error': 'msg'}]
            # We can return this directly, or summarize. For now, let's return a summary.
            success_count = sum(1 for r in results if r.get('success'))

            if success_count > 0:
                return {"success": True, "message": f"Index analysis for {index_type} completed. {success_count}/{len(results)} files processed.", "details": results}
            else:
                # Try to find an error message from results
                first_error = next((r.get('error') for r in results if not r.get('success') and r.get('error')), "Analysis failed for all files.")
                return {"success": False, "error": first_error, "details": results}

        except ImportError:
            return {"success": False, "error": "Processing module not found. Ensure 'flutter_earth.processing' is available."}
        except Exception as e:
            # import traceback; traceback.print_exc() # For server-side debugging
            return {"success": False, "error": f"Error during index analysis: {str(e)}"}

    def get_vector_data_sources(self, args):
        # Mirrors AppBackend.getVectorDataSources()
        return [
            {"name": "Overpass API (OSM)", "description": "OpenStreetMap data via Overpass API. Query is Overpass QL. {{bbox}} can be used for AOI."},
            {"name": "WFS", "description": "Web Feature Service. Query is the full GetFeature URL."},
            {"name": "GeoJSON URL", "description": "Direct GeoJSON file URL. Query is the URL itself."}
        ]

    def get_vector_output_formats(self, args):
        # Mirrors AppBackend.getVectorOutputFormats()
        return ["GeoJSON", "Shapefile", "KML"] # Make sure your vector_download.py supports these

    def get_current_aoi(self, args):
        # Mirrors AppBackend.getCurrentAOI() - this usually comes from a map interaction
        # For now, return a default or last set if available in config
        return self.config_manager.get('area_of_interest', []) # Example placeholder

    def start_vector_download(self, args):
        try:
            from flutter_earth.vector_download import download_vector_data # Assuming this is the one

            # Parse AOI:
            # JS sends 'aoi' as a list. It might be empty.
            aoi_list_str = args.get('aoi') # This will be a string representation of a list from CLI
            aoi_list = []
            if aoi_list_str and aoi_list_str != "[]": # Check if it's not an empty list string
                try:
                    aoi_list = json.loads(aoi_list_str)
                    if not isinstance(aoi_list, list): # Ensure it's a list after parsing
                        raise ValueError("AOI must be a list.")
                except (json.JSONDecodeError, ValueError) as e:
                    return {"success": False, "error": f"Invalid AOI format provided: {e}. Expected a list of numbers or empty."}

            query = args.get('query')
            output_path = args.get('output_path') # Full path including filename and extension
            output_format = args.get('output_format')

            if not all([query, output_path, output_format]):
                return {"success": False, "error": "Missing parameters for vector download (query, output_path, or output_format)."}

            # download_vector_data expects AOI as a list of floats or empty list
            # It handles the case where aoi_list is empty.
            success = download_vector_data(aoi_list, query, output_path, output_format)

            if success:
                return {"success": True, "message": f"Vector data downloaded to {output_path}"}
            else:
                # Try to get a more specific error from vector_download if it raises/returns one
                return {"success": False, "error": "Vector download failed. Check logs or query."}

        except ImportError:
            return {"success": False, "error": "Vector download module not found."}
        except Exception as e:
            # import traceback; traceback.print_exc()
            return {"success": False, "error": f"Error during vector download: {str(e)}"}

    def load_raster_data(self, args):
        file_path = args.get('file_path')
        if not file_path:
            return {"success": False, "error": "File path not provided for raster data."}
        try:
            # Placeholder - In real implementation, use rasterio or gdal to read metadata
            # For now, mimic the QML placeholder structure
            # Ensure this path is accessible by the Python script's environment
            if not os.path.exists(file_path):
                 return {"success": False, "error": f"Raster file not found: {file_path}"}

            # Basic simulated metadata
            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

            return {
                "success": True,
                "file_path": file_path,
                "file_size": f"{file_size_mb} MB", # Added file size
                "width": 1024, "height": 768, # Simulated
                "bands": ["Red", "Green", "Blue"], # Simulated
                "crs": "EPSG:4326 (Simulated)",
                "dtype": "uint8 (Simulated)",
                "nodata": 0, # Simulated
                "bounds": {"left": -180.0, "bottom": -90.0, "right": 180.0, "top": 90.0} # Simulated
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to load raster metadata: {str(e)}"}

    def load_vector_data(self, args):
        file_path = args.get('file_path')
        if not file_path:
            return {"success": False, "error": "File path not provided for vector data."}
        try:
            # Placeholder - In real implementation, use fiona, geopandas, or ogr to read metadata
            if not os.path.exists(file_path):
                 return {"success": False, "error": f"Vector file not found: {file_path}"}

            file_size_bytes = os.path.getsize(file_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

            return {
                "success": True,
                "file_path": file_path,
                "file_size": f"{file_size_mb} MB", # Added
                "feature_count": 150, # Simulated
                "geometry_types": ["Polygon"], # Simulated
                "crs": "EPSG:4326 (Simulated)",
                "bounds": [-122.5, 37.5, -122.0, 38.0], # Simulated [minx, miny, maxx, maxy]
                "columns": ["id", "name", "category"] # Simulated
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to load vector metadata: {str(e)}"}


    # open_external_url is handled by Electron's shell module, no Python bridge needed for the action itself,
    # but main.js has a handler for it. If Python needed to *initiate* opening a URL, it would be different.

def main():
    parser = argparse.ArgumentParser(description="Flutter Earth Electron Bridge")
    parser.add_argument("action", help="The action to perform")

    args, unknown_args = parser.parse_known_args()

    action_args = {}
    i = 0
    while i < len(unknown_args):
        if unknown_args[i].startswith('--'):
            key = unknown_args[i][2:]
            if i + 1 < len(unknown_args) and not unknown_args[i+1].startswith('--'):
                action_args[key] = unknown_args[i+1]
                i += 2
            else:
                action_args[key] = True # Treat as a flag if no value follows
                i += 1
        else:
            i += 1 # Skip non-key-value arguments for now

    bridge = ElectronBridge()

    if hasattr(bridge, args.action):
        method_to_call = getattr(bridge, args.action)
        result = method_to_call(action_args)
        # For actions that return simple strings (like get_changelog or get_setting for a string value),
        # we still need to ensure they are part of a JSON structure if Electron expects JSON.
        # However, if Electron's callPython can handle raw strings for certain calls, this might be fine.
        # To be safe, always return JSON. If result is already a dict/list, json.dumps handles it.
        # If it's a simple type (string, number, bool), json.dumps will correctly format it as JSON.
        print(json.dumps(result))
    else:
        print(json.dumps({"success": False, "error": f"Unknown action: {args.action}"}))
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(json.dumps({"success": False, "error": f"Critical ImportError in bridge: {e}", "details": str(sys.path)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Unhandled exception in bridge: {e}"}))
        sys.exit(1)
