"""Flutter Earth - A modern tool for downloading and processing satellite imagery."""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"flutter_earth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(log_format))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

def initialize_auth_system():
    """Initialize the authentication system on startup.
    
    Note: This is now a non-blocking initialization that doesn't interfere
    with the Electron app's GEE initialization process.
    """
    try:
        # Add the flutter_earth_pkg to the path
        sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
        
        # Lazy import to reduce startup time
        try:
            from flutter_earth.auth_setup import AuthManager
        except ImportError as e:
            logging.warning(f"Could not import AuthManager: {e}")
            return {
                "status": "error",
                "message": f"Auth system import failed: {e}",
                "initialized": False,
                "auth_ready": False
            }
        
        # Initialize auth manager only (don't initialize GEE here)
        try:
            auth_manager = AuthManager()
            logging.info("AuthManager initialized successfully")
        except Exception as e:
            logging.warning(f"AuthManager initialization failed: {e}")
            return {
                "status": "error",
                "message": f"AuthManager initialization failed: {e}",
                "initialized": False,
                "auth_ready": False
            }
        
        # Check auth status without initializing GEE
        try:
            auth_info = auth_manager.get_auth_info()
            logging.info(f"Auth status: {auth_info}")
        except Exception as e:
            logging.warning(f"Could not get auth info: {e}")
            auth_info = {}
        
        # Return auth status without forcing GEE initialization
        if auth_manager.has_credentials():
            return {
                "status": "auth_ready",
                "message": "Authentication credentials available - GEE will be initialized by Electron app",
                "initialized": False,
                "auth_ready": True
            }
        else:
            logging.info("No authentication credentials found - user will need to set up auth")
            return {
                "status": "auth_required",
                "message": "Authentication required",
                "initialized": False,
                "auth_ready": False
            }
            
    except Exception as e:
        logging.error(f"Error initializing auth system: {e}")
        return {
            "status": "error",
            "message": f"Auth system initialization failed: {e}",
            "initialized": False,
            "auth_ready": False
        }

def cleanup_temp_files():
    """Clean up temporary files and old logs."""
    try:
        logs_dir = Path("logs")
        if logs_dir.exists():
            # Keep only the 5 most recent log files for each type
            log_files = list(logs_dir.glob("*.log"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Group by log type
            log_types = {}
            for log_file in log_files:
                base_name = log_file.stem.split('_')[0]  # Get base name like 'flutter_earth'
                if base_name not in log_types:
                    log_types[base_name] = []
                log_types[base_name].append(log_file)
            
            # Keep only 5 most recent of each type
            for log_type, files in log_types.items():
                if len(files) > 5:
                    for old_file in files[5:]:
                        try:
                            old_file.unlink()
                            logging.info(f"Cleaned up old log file: {old_file}")
                        except Exception as e:
                            logging.warning(f"Could not delete old log file {old_file}: {e}")
        
        # Clean up any temporary files in crawler_data
        crawler_data_dir = Path("backend/crawler_data")
        if crawler_data_dir.exists():
            temp_files = list(crawler_data_dir.glob("*_tmp.*"))
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                    logging.info(f"Cleaned up temp file: {temp_file}")
                except Exception as e:
                    logging.warning(f"Could not delete temp file {temp_file}: {e}")
        
        logging.info("Temporary file cleanup completed")
        
    except Exception as e:
        logging.error(f"Error during temp file cleanup: {e}")

def main():
    """Main entry point for Flutter Earth."""
    logging.info("=== Flutter Earth Application Started ===")
    logging.info(f"Log file: {log_file}")
    
    # Use startup coordinator to prevent conflicts
    try:
        from startup_coordinator import StartupCoordinator
        coordinator = StartupCoordinator()
        
        if not coordinator.coordinate_main_py_startup():
            logging.warning("Startup coordination failed, continuing with basic initialization")
            # Fallback to basic initialization
            cleanup_temp_files()
            auth_result = initialize_auth_system()
        else:
            # Get auth result from coordinator
            auth_result = coordinator.initialization_status.get("auth_details", {
                "status": "unknown",
                "message": "Auth status unknown",
                "initialized": False,
                "auth_ready": False
            })
            
    except ImportError:
        logging.warning("Startup coordinator not available, using basic initialization")
        # Fallback to basic initialization
        cleanup_temp_files()
        auth_result = initialize_auth_system()
    
    logging.info(f"Auth initialization result: {auth_result}")
    
    print("=" * 60)
    print("Flutter Earth - Desktop Application")
    print("=" * 60)
    print()
    print("This application now runs as an Electron desktop app.")
    print("To start the application:")
    print()
    print("1. Run: run_desktop.bat")
    print("   OR")
    print("2. Navigate to frontend/ and run: npm start")
    print()
    print("The Electron app provides a modern HTML/CSS/JS interface")
    print("that communicates directly with Python for Earth Engine operations.")
    print()
    
    # Display auth status
    if auth_result.get("status") == "auth_ready":
        print("✅ Earth Engine authentication: READY")
        print("   GEE will be initialized by the Electron app when needed.")
    elif auth_result.get("status") == "auth_required":
        print("⚠️  Earth Engine authentication: REQUIRED")
        print("   Please set up authentication in the application.")
    else:
        print("❌ Earth Engine authentication: FAILED")
        print(f"   Error: {auth_result.get('message', 'Unknown error')}")
    
    print()
    print("For more information, see README.md")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
