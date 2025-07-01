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
import gzip

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

# Global variable for download progress tracking
current_download_progress = {}

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
        logger = logging.getLogger(__name__)
        logger.info(f"Starting download with params: {params}")
        
        # If this is a satellite download from crawler data, we need to extract the code snippet
        if 'satellite_name' in params and 'crawler_data' in params:
            # Load crawler data to get the code snippet
            import gzip
            from pathlib import Path
            
            crawler_data_path = Path('backend/crawler_data/gee_catalog_data_enhanced.json.gz')
            if crawler_data_path.exists():
                with gzip.open(crawler_data_path, 'rt', encoding='utf-8') as f:
                    crawler_data = json.load(f)
                
                satellite_name = params['satellite_name']
                if satellite_name in crawler_data.get('satellites', {}):
                    satellite_data = crawler_data['satellites'][satellite_name]
                    if satellite_data and len(satellite_data) > 0:
                        # Use the code snippet from the first dataset
                        code_snippet = satellite_data[0].get('code_snippet', '')
                        if code_snippet:
                            # Extract sensor name from code snippet (usually the first part)
                            sensor_name = satellite_name.lower()
                            params['sensor_name'] = sensor_name
                            params['code_snippet'] = code_snippet
                            logger.info(f"Using code snippet for {satellite_name}: {code_snippet[:100]}...")
        
        # Ensure we have the required parameters
        required_params = ['area_of_interest', 'start_date', 'end_date', 'sensor_name', 'output_dir']
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            return {
                "status": "error",
                "message": f"Missing required parameters: {', '.join(missing_params)}"
            }
        
        # Initialize download progress tracking
        download_id = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        download_progress = {
            'download_id': download_id,
            'start_time': datetime.now().isoformat(),
            'status': 'starting',
            'percentage': 0,
            'message': 'Initializing download...',
            'bytes_downloaded': 0,
            'total_bytes': 0,
            'elapsed_time': 0,
            'completed': False,
            'error': None
        }
        
        # Store progress in a global variable (in a real implementation, this would be in a database or file)
        global current_download_progress
        current_download_progress = download_progress
        
        # For now, simulate download progress (actual download will be implemented later)
        logger.info("Download parameters validated successfully")
        logger.info(f"Download ID: {download_id}")
        logger.info(f"Parameters: {json.dumps(params, indent=2)}")
        
        return {
            "status": "success",
            "message": "Download started successfully",
            "download_id": download_id,
            "params": params
        }
            
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Download error: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Download error: {str(e)}"
        }

def get_progress():
    """Get current download progress"""
    try:
        global current_download_progress
        
        if not hasattr(get_progress, 'simulation_start_time'):
            get_progress.simulation_start_time = datetime.now()
            get_progress.simulation_progress = 0
        
        # Simulate download progress for testing
        elapsed = (datetime.now() - get_progress.simulation_start_time).total_seconds()
        
        # Simulate progress from 0 to 100% over 30 seconds
        progress_percent = min(100, (elapsed / 30) * 100)
        
        # Simulate bytes downloaded (assuming 100MB total)
        total_bytes = 100 * 1024 * 1024  # 100MB
        bytes_downloaded = int((progress_percent / 100) * total_bytes)
        
        # Simulate speed variations
        base_speed = 2 * 1024 * 1024  # 2 MB/s base speed
        speed_variation = 1 + 0.5 * (elapsed % 5) / 5  # Vary speed every 5 seconds
        current_speed = base_speed * speed_variation
        
        # Update progress
        get_progress.simulation_progress = progress_percent
        
        progress_data = {
            'download_id': current_download_progress.get('download_id', 'unknown'),
            'status': 'downloading' if progress_percent < 100 else 'completed',
            'percentage': progress_percent,
            'message': f'Downloading satellite data... {progress_percent:.1f}%',
            'bytes_downloaded': bytes_downloaded,
            'total_bytes': total_bytes,
            'elapsed_time': elapsed,
            'current_speed': current_speed,
            'completed': progress_percent >= 100,
            'error': None
        }
        
        # Update global progress
        current_download_progress = progress_data
        
        return {
            "status": "success",
            "progress": progress_data
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

def run_web_crawler():
    """Run the web crawler to fetch satellite data"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("Starting web crawler")
        
        # Import the crawler module
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from gee_catalog_crawler_enhanced import run_crawler
        
        # Run the crawler
        result = run_crawler()
        
        logger.info("Web crawler completed successfully")
        return {
            "status": "success",
            "message": "Web crawler completed successfully",
            "data_file": "gee_catalog_data_enhanced.json"
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Web crawler error: {e}")
        return {
            "status": "error",
            "message": f"Web crawler error: {str(e)}"
        }

def compress_crawler_data(json_path):
    import shutil
    from pathlib import Path
    import json
    try:
        data_dir = Path('backend/crawler_data')
        data_dir.mkdir(parents=True, exist_ok=True)
        out_path = data_dir / 'gee_catalog_data_enhanced.json.gz'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with gzip.open(out_path, 'wt', encoding='utf-8') as gz:
            json.dump(data, gz, ensure_ascii=False, indent=2)
        return {"status": "success", "message": f"Compressed and saved to {out_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
        elif command == "run-crawler":
            result = run_web_crawler()
        elif command == "compress-crawler-data":
            if len(sys.argv) < 3:
                result = {"status": "error", "message": "Missing JSON file path"}
            else:
                json_path = sys.argv[2]
                result = compress_crawler_data(json_path)
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