#!/usr/bin/env python3
"""
Earth Engine Processor - Called directly from Electron
Handles all Earth Engine operations without HTTP server
"""
import sys
import json
import os
import logging
from pathlib import Path
from datetime import datetime

# Set up logging as the very first thing
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / f"earth_engine_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logging.getLogger(__name__).info("[TEST] Logging initialized at top of script.")

print("DEBUG: Script starting", file=sys.stderr)

# Add the flutter_earth_pkg to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'flutter_earth_pkg'))

print("DEBUG: About to import modules", file=sys.stderr)

try:
    from flutter_earth.earth_engine import EarthEngineManager
    from flutter_earth.download_manager import DownloadManager
    from flutter_earth.config import ConfigManager
    from flutter_earth.progress_tracker import ProgressTracker
    from flutter_earth.auth_setup import AuthManager
    print("DEBUG: All imports successful", file=sys.stderr)
except ImportError as e:
    print(f"DEBUG: Import error: {e}", file=sys.stderr)
    print(json.dumps({"error": f"Import error: {e}"}))
    sys.exit(1)

def setup_logging():
    """Setup logging for the processor"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"earth_engine_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("[TEST] Logging initialized and log file created.")
    return logger

def initialize_earth_engine(logger):
    """Initialize Earth Engine"""
    try:
        logger.debug("Starting Earth Engine initialization")
        config_manager = ConfigManager()
        logger.debug("ConfigManager created")
        progress_tracker = ProgressTracker()
        logger.debug("ProgressTracker created")
        download_manager = DownloadManager()
        logger.debug("DownloadManager created")
        earth_engine = EarthEngineManager()
        logger.debug("EarthEngineManager created")
        logger.debug("Calling earth_engine.initialize()")
        initialized = earth_engine.initialize()
        logger.debug(f"earth_engine.initialize() returned: {initialized}")
        
        if initialized:
            logger.info("Initialization successful")
            return {
                "status": "success",
                "message": "Earth Engine initialized successfully",
                "initialized": True
            }
        else:
            logger.warning("Initialization failed")
            return {
                "status": "error",
                "message": "Earth Engine initialization failed",
                "initialized": False
            }
    except Exception as e:
        logger.error(f"Exception in initialize_earth_engine: {e}")
        return {
            "status": "error",
            "message": f"Initialization error: {str(e)}",
            "initialized": False
        }

def start_download(params):
    """Start a download with the given parameters"""
    try:
        config_manager = ConfigManager()
        progress_tracker = ProgressTracker()
        download_manager = DownloadManager()
        earth_engine = EarthEngineManager()
        
        # Initialize if not already done
        if not earth_engine.initialized:
            earth_engine.initialize()
        
        # Start download
        result = download_manager.start_download(params)
        
        return {
            "status": "success",
            "message": "Download started",
            "download_id": result.get("download_id", "unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Download error: {str(e)}"
        }

def get_progress():
    """Get current download progress"""
    try:
        progress_tracker = ProgressTracker()
        progress = progress_tracker.get_progress()
        
        return {
            "status": "success",
            "progress": progress
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Progress error: {str(e)}"
        }

def set_auth_credentials(key_file, project_id):
    """Set authentication credentials"""
    try:
        auth_manager = AuthManager()
        auth_manager.save_credentials(project_id, key_file)
        
        return {
            "status": "success",
            "message": "Credentials saved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Auth error: {str(e)}"
        }

def main():
    """Main entry point for the processor"""
    logger = setup_logging()
    logger.info("Earth Engine Processor started")
    
    logger.debug("Script starting")
    
    if len(sys.argv) < 2:
        logger.error("No command specified")
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    command = sys.argv[1]
    logger.debug(f"Command received: {command}")
    
    try:
        if command == "init":
            logger.debug("Starting initialization")
            result = initialize_earth_engine(logger)
        elif command == "download":
            if len(sys.argv) < 3:
                result = {"status": "error", "message": "No download parameters provided"}
            else:
                params = json.loads(sys.argv[2])
                result = start_download(params)
        elif command == "progress":
            result = get_progress()
        elif command == "auth":
            if len(sys.argv) < 4:
                result = {"status": "error", "message": "Missing auth parameters"}
            else:
                key_file = sys.argv[2]
                project_id = sys.argv[3]
                result = set_auth_credentials(key_file, project_id)
        else:
            result = {"status": "error", "message": f"Unknown command: {command}"}
        
        logger.debug("About to print result")
        print(json.dumps(result))
        logger.debug("Result printed")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main() 