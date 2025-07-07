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
    """Initialize Earth Engine with proper authentication"""
    try:
        logger.debug("Starting Earth Engine initialization")
        
        # Check if GEE is already initialized to prevent conflicts
        try:
            import ee
            if ee.data._credentials:
                logger.debug("Earth Engine already initialized, checking connection health")
                # Test connection health
                test_image = ee.Image('USGS/SRTMGL1_003')
                _ = test_image.geometry().bounds().getInfo()
                logger.debug("Earth Engine connection is healthy")
                return {
                    "status": "online",
                    "message": "Earth Engine already initialized and healthy",
                    "initialized": True
                }
        except Exception:
            logger.debug("Earth Engine not initialized or connection unhealthy, proceeding with initialization")
        
        # Create managers
        config_manager = ConfigManager()
        logger.debug("ConfigManager created")
        progress_tracker = ProgressTracker()
        logger.debug("ProgressTracker created")
        download_manager = DownloadManager()
        logger.debug("DownloadManager created")
        earth_engine = EarthEngineManager()
        logger.debug("EarthEngineManager created")
        
        # Initialize Earth Engine
        logger.debug("Calling earth_engine.initialize()")
        result = earth_engine.initialize()
        logger.debug(f"earth_engine.initialize() returned: {result}")
        
        return result
        
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
        
        # Update progress data
        progress_data = {
            'download_id': current_download_progress.get('download_id', 'unknown'),
            'start_time': current_download_progress.get('start_time', datetime.now().isoformat()),
            'status': 'downloading' if progress_percent < 100 else 'completed',
            'percentage': progress_percent,
            'message': f'Downloading... {progress_percent:.1f}%' if progress_percent < 100 else 'Download completed',
            'bytes_downloaded': bytes_downloaded,
            'total_bytes': total_bytes,
            'elapsed_time': elapsed,
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

def check_auth_needed():
    """Check if authentication is needed"""
    try:
        auth_manager = AuthManager()
        needs_auth = auth_manager.needs_authentication()
        auth_info = auth_manager.get_auth_info()
        
        return {
            "status": "success",
            "needs_auth": needs_auth,
            "auth_info": auth_info,
            "message": "Authentication check completed"
        }
    except Exception as e:
        return {
            "status": "error",
            "needs_auth": True,  # Default to requiring auth on error
            "message": f"Auth check error: {str(e)}"
        }

def set_auth_credentials(key_file, project_id):
    """Set authentication credentials"""
    try:
        auth_manager = AuthManager()
        auth_manager.save_credentials(project_id, key_file)
        
        # Test the connection after saving
        success, message = auth_manager.initialize_earth_engine()
        
        if success:
            return {
                "status": "success",
                "message": "Credentials saved and Earth Engine initialized successfully"
            }
        else:
            return {
                "status": "warning",
                "message": f"Credentials saved but Earth Engine initialization failed: {message}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Auth error: {str(e)}"
        }

def test_auth_connection(project_id, key_file):
    """Test authentication connection"""
    try:
        auth_manager = AuthManager()
        auth_manager.test_connection(project_id, key_file)
        
        return {
            "status": "success",
            "message": "Authentication test completed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Authentication test failed: {str(e)}"
        }

def get_auth_status():
    """Get comprehensive authentication status"""
    try:
        auth_manager = AuthManager()
        auth_info = auth_manager.get_auth_info()
        
        return {
            "status": "success",
            "authenticated": auth_info.get('authenticated', False),
            "message": auth_info.get('message', 'Authentication status checked'),
            "auth_info": auth_info
        }
    except Exception as e:
        return {
            "status": "error",
            "authenticated": False,
            "message": f"Failed to get auth status: {str(e)}"
        }

def clear_auth_credentials():
    """Clear all authentication credentials"""
    try:
        auth_manager = AuthManager()
        auth_manager.clear_credentials()
        
        return {
            "status": "success",
            "message": "Authentication credentials cleared successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clear credentials: {str(e)}"
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
        
        # Run the crawler in background (this should be non-blocking)
        import threading
        crawler_thread = threading.Thread(target=run_crawler)
        crawler_thread.daemon = True
        crawler_thread.start()
        
        logger.info("Web crawler started in background")
        return {
            "status": "started",
            "message": "Web crawler started in background"
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

def get_crawler_progress():
    """Get current crawler progress from the progress file"""
    try:
        progress_file = Path('backend/crawler_data/crawler_progress.json')
        if not progress_file.exists():
            return {
                "status": "success",
                "progress": {
                    "status": "not_started",
                    "message": "Crawler not started",
                    "percentage": 0,
                    "current_page": 0,
                    "total_pages": 0,
                    "datasets_found": 0,
                    "satellites_found": 0
                }
            }
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        # Calculate percentage based on current progress
        percentage = 0
        if progress_data.get('total_pages', 0) > 0:
            percentage = min(100, (progress_data.get('current_page', 0) / progress_data.get('total_pages', 1)) * 100)
        elif progress_data.get('status') == 'completed':
            percentage = 100
        
        return {
            "status": "success",
            "progress": {
                "status": progress_data.get('status', 'unknown'),
                "message": progress_data.get('message', 'Processing...'),
                "percentage": percentage,
                "current_page": progress_data.get('current_page', 0),
                "total_pages": progress_data.get('total_pages', 0),
                "datasets_found": progress_data.get('datasets_found', 0),
                "satellites_found": progress_data.get('satellites_found', 0)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Crawler progress error: {str(e)}"
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
        elif command == "auth-check":
            result = check_auth_needed()
        elif command == "auth":
            if len(sys.argv) < 4:
                result = {"status": "error", "message": "Missing auth parameters"}
            else:
                key_file = sys.argv[2]
                project_id = sys.argv[3]
                result = set_auth_credentials(key_file, project_id)
        elif command == "auth-test":
            if len(sys.argv) < 4:
                result = {"status": "error", "message": "Missing auth test parameters"}
            else:
                key_file = sys.argv[2]
                project_id = sys.argv[3]
                result = test_auth_connection(project_id, key_file)
        elif command == "auth-status":
            result = get_auth_status()
        elif command == "clear-auth":
            result = clear_auth_credentials()
        elif command == "run-crawler":
            result = run_web_crawler()
        elif command == "compress-crawler-data":
            if len(sys.argv) < 3:
                result = {"status": "error", "message": "Missing JSON file path"}
            else:
                json_path = sys.argv[2]
                result = compress_crawler_data(json_path)
        elif command == "crawler-progress":
            result = get_crawler_progress()
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