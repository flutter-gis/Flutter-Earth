#!/usr/bin/env python3
"""
Startup Coordinator for Flutter Earth
Ensures proper initialization sequence and prevents conflicts between different startup paths.
"""
import os
import sys
import json
import logging
import time
from pathlib import Path
from datetime import datetime
import threading
import atexit

class StartupCoordinator:
    """Coordinates startup processes to prevent conflicts."""
    
    def __init__(self):
        self.lock_file = Path("startup.lock")
        self.coordinator_log = Path("logs/startup_coordinator.log")
        self.initialization_status = {
            "main_py_initialized": False,
            "electron_initialized": False,
            "gee_initialized": False,
            "auth_ready": False,
            "startup_time": None,
            "last_activity": None
        }
        
        # Ensure logs directory exists
        self.coordinator_log.parent.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.coordinator_log, mode='a', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def acquire_lock(self):
        """Acquire startup lock to prevent multiple instances."""
        try:
            if self.lock_file.exists():
                # Check if lock is stale (older than 5 minutes)
                lock_age = time.time() - self.lock_file.stat().st_mtime
                if lock_age > 300:  # 5 minutes
                    self.logger.warning(f"Removing stale lock file (age: {lock_age:.1f}s)")
                    self.lock_file.unlink()
                else:
                    return False
            
            # Create lock file
            with open(self.lock_file, 'w') as f:
                json.dump({
                    "pid": os.getpid(),
                    "startup_time": datetime.now().isoformat(),
                    "coordinator": True
                }, f)
            
            self.logger.info("Startup lock acquired")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to acquire lock: {e}")
            return False
    
    def release_lock(self):
        """Release startup lock."""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                self.logger.info("Startup lock released")
        except Exception as e:
            self.logger.error(f"Failed to release lock: {e}")
    
    def update_status(self, component, status=True, details=None):
        """Update initialization status for a component."""
        self.initialization_status[f"{component}_initialized"] = status
        self.initialization_status["last_activity"] = datetime.now().isoformat()
        
        if details:
            self.initialization_status[f"{component}_details"] = details
        
        # Save status to file
        status_file = Path("logs/startup_status.json")
        try:
            with open(status_file, 'w') as f:
                json.dump(self.initialization_status, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save status: {e}")
        
        self.logger.info(f"Status updated: {component} = {status}")
    
    def check_conflicts(self):
        """Check for potential initialization conflicts."""
        conflicts = []
        
        # Check if both main.py and Electron are trying to initialize GEE
        if (self.initialization_status["main_py_initialized"] and 
            self.initialization_status["electron_initialized"]):
            conflicts.append("Both main.py and Electron initialized - potential GEE conflict")
        
        # Check if GEE is initialized multiple times
        if self.initialization_status["gee_initialized"]:
            # Check for multiple GEE initialization attempts
            pass
        
        return conflicts
    
    def coordinate_main_py_startup(self):
        """Coordinate main.py startup process."""
        self.logger.info("Coordinating main.py startup")
        
        if not self.acquire_lock():
            self.logger.warning("Could not acquire lock, another instance may be running")
            return False
        
        try:
            # Update status
            self.update_status("main_py", True, {
                "pid": os.getpid(),
                "startup_time": datetime.now().isoformat()
            })
            
            # Check for conflicts
            conflicts = self.check_conflicts()
            if conflicts:
                for conflict in conflicts:
                    self.logger.warning(f"Conflict detected: {conflict}")
            
            # Clean up temp files
            self.cleanup_temp_files()
            
            # Initialize auth system (non-blocking)
            auth_result = self.initialize_auth_system()
            self.update_status("auth", auth_result.get("auth_ready", False), auth_result)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in main.py coordination: {e}")
            return False
    
    def coordinate_electron_startup(self):
        """Coordinate Electron app startup process."""
        self.logger.info("Coordinating Electron startup")
        
        try:
            # Update status
            self.update_status("electron", True, {
                "pid": os.getpid(),
                "startup_time": datetime.now().isoformat()
            })
            
            # Check for conflicts
            conflicts = self.check_conflicts()
            if conflicts:
                for conflict in conflicts:
                    self.logger.warning(f"Conflict detected: {conflict}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in Electron coordination: {e}")
            return False
    
    def coordinate_gee_initialization(self):
        """Coordinate GEE initialization to prevent conflicts."""
        self.logger.info("Coordinating GEE initialization")
        
        try:
            # Check if GEE is already initialized
            import ee
            if hasattr(ee, 'data') and ee.data._credentials:
                self.logger.info("GEE already initialized, skipping")
                self.update_status("gee", True, {"status": "already_initialized"})
                return True
            
            # Initialize GEE
            self.update_status("gee", True, {"status": "initializing"})
            
            # The actual GEE initialization will be done by the processor
            return True
            
        except Exception as e:
            self.logger.error(f"Error in GEE coordination: {e}")
            self.update_status("gee", False, {"error": str(e)})
            return False
    
    def initialize_auth_system(self):
        """Initialize authentication system (non-blocking)."""
        try:
            # Add the flutter_earth_pkg to the path
            sys.path.insert(0, str(Path(__file__).parent / 'flutter_earth_pkg'))
            
            from flutter_earth.auth_setup import AuthManager
            
            # Initialize auth manager only (don't initialize GEE here)
            auth_manager = AuthManager()
            self.logger.info("AuthManager initialized successfully")
            
            # Check auth status without initializing GEE
            auth_info = auth_manager.get_auth_info()
            self.logger.info(f"Auth status: {auth_info}")
            
            # Return auth status without forcing GEE initialization
            if auth_manager.has_credentials():
                return {
                    "status": "auth_ready",
                    "message": "Authentication credentials available - GEE will be initialized by Electron app",
                    "initialized": False,
                    "auth_ready": True
                }
            else:
                self.logger.info("No authentication credentials found - user will need to set up auth")
                return {
                    "status": "auth_required",
                    "message": "Authentication required",
                    "initialized": False,
                    "auth_ready": False
                }
                
        except Exception as e:
            self.logger.error(f"Error initializing auth system: {e}")
            return {
                "status": "error",
                "message": f"Auth system initialization failed: {e}",
                "initialized": False,
                "auth_ready": False
            }
    
    def cleanup_temp_files(self):
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
                                self.logger.info(f"Cleaned up old log file: {old_file}")
                            except Exception as e:
                                self.logger.warning(f"Could not delete old log file {old_file}: {e}")
            
            # Clean up any temporary files in crawler_data
            crawler_data_dir = Path("backend/crawler_data")
            if crawler_data_dir.exists():
                temp_files = list(crawler_data_dir.glob("*_tmp.*"))
                for temp_file in temp_files:
                    try:
                        temp_file.unlink()
                        self.logger.info(f"Cleaned up temp file: {temp_file}")
                    except Exception as e:
                        self.logger.warning(f"Could not delete temp file {temp_file}: {e}")
            
            self.logger.info("Temporary file cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during temp file cleanup: {e}")
    
    def cleanup(self):
        """Cleanup on exit."""
        self.release_lock()
        self.logger.info("Startup coordinator cleanup completed")

def main():
    """Main entry point for startup coordination."""
    coordinator = StartupCoordinator()
    
    print("=" * 60)
    print("Flutter Earth - Startup Coordinator")
    print("=" * 60)
    print()
    
    # Coordinate main.py startup
    if coordinator.coordinate_main_py_startup():
        print("✅ Main.py startup coordinated successfully")
    else:
        print("❌ Main.py startup coordination failed")
    
    print()
    print("Startup coordination completed!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 