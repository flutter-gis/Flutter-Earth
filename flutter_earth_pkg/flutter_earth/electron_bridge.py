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
    # Import other necessary managers/modules from your package as needed
    # from flutter_earth.earth_engine import EarthEngineManager # Example
    # from flutter_earth.download_manager import DownloadManager # Example
    # from flutter_earth.progress_tracker import ProgressTracker # Example
    # from flutter_earth.gui import AppBackend # Or instantiate managers directly
except ImportError as e:
    # Output error as JSON so Electron can try to parse it or catch it
    print(json.dumps({"success": False, "error": f"ImportError in bridge: {e}", "details": str(sys.path)}))
    sys.exit(1)

class ElectronBridge:
    def __init__(self):
        try:
            self.config_manager = ConfigManager()
            self.theme_manager = ThemeManager(config_manager=self.config_manager) # ThemeManager might need config
            # self.earth_engine_manager = EarthEngineManager() # Initialize if needed for some actions
            # self.app_backend = AppBackend( # If you want to reuse AppBackend logic
            #     config_manager=self.config_manager,
            #     earth_engine=self.earth_engine_manager, # Dummy or real
            #     download_manager=None, # Dummy or real
            #     progress_tracker=None # Dummy or real
            # )
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
        if not hasattr(self, '_sim_download_state_idx'):
            self._sim_download_state_idx = 0
            self._sim_download_states = [
                {"status": "idle", "progress": 0, "message": "No active downloads."},
                {"status": "downloading", "progress": 25, "message": "Downloading imagery (1/4)..."},
                {"status": "downloading", "progress": 50, "message": "Downloading imagery (2/4)..."},
                {"status": "processing", "progress": 75, "message": "Processing downloaded files..."},
                {"status": "complete", "progress": 100, "message": "Download and processing complete."},
                {"status": "idle", "progress": 0, "message": "No active downloads."} # Back to idle
            ]

        current_sim_status = self._sim_download_states[self._sim_download_state_idx]
        self._sim_download_state_idx = (self._sim_download_state_idx + 1) % len(self._sim_download_states)
        return current_sim_status

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
