#!/usr/bin/env python3
"""
Startup Coordinator for Flutter Earth
Ensures proper initialization sequence for Dear PyGui application.
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
    """Coordinates startup processes for Dear PyGui application."""
    
    def __init__(self):
        self.lock_file = Path("startup.lock")
        self.coordinator_log = Path("logs/startup_coordinator.log")
        self.initialization_status = {
            "dearpygui_initialized": False,
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
                    "coordinator": True,
                    "app_type": "dearpygui"
                }, f)
            
            self.logger.info("Startup lock acquired for Dear PyGui application")
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
        
        # Check if GEE is initialized multiple times
        if self.initialization_status["gee_initialized"]:
            # Check for multiple GEE initialization attempts
            pass
        
        return conflicts
    
    def coordinate_dearpygui_startup(self):
        """Coordinate Dear PyGui startup process."""
        self.logger.info("Coordinating Dear PyGui startup")
        
        if not self.acquire_lock():
            self.logger.warning("Could not acquire lock, another instance may be running")
            return False
        
        try:
            # Update status
            self.update_status("dearpygui", True, {
                "pid": os.getpid(),
                "startup_time": datetime.now().isoformat(),
                "gui_framework": "dearpygui"
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
            self.logger.error(f"Error in Dear PyGui coordination: {e}")
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
            self.logger.info("Initializing authentication system")
            
            # Check if auth credentials exist
            auth_file = Path("auth_credentials.json")
            if auth_file.exists():
                with open(auth_file, 'r') as f:
                    auth_data = json.load(f)
                
                # Validate credentials
                if auth_data.get("project_id") and auth_data.get("key_file"):
                    self.logger.info("Auth credentials found")
                    return {
                        "auth_ready": True,
                        "project_id": auth_data.get("project_id"),
                        "key_file": auth_data.get("key_file")
                    }
            
            self.logger.info("No valid auth credentials found")
            return {"auth_ready": False, "reason": "no_credentials"}
            
        except Exception as e:
            self.logger.error(f"Error initializing auth system: {e}")
            return {"auth_ready": False, "error": str(e)}
    
    def cleanup_temp_files(self):
        """Clean up temporary files and directories."""
        try:
            temp_dirs = ["temp", "__pycache__"]
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    import shutil
                    shutil.rmtree(temp_path)
                    temp_path.mkdir(exist_ok=True)
                    self.logger.info(f"Cleaned up {temp_dir}")
            
            # Clean up old log files (older than 7 days)
            logs_dir = Path("logs")
            if logs_dir.exists():
                current_time = time.time()
                for log_file in logs_dir.glob("*.log"):
                    if current_time - log_file.stat().st_mtime > 604800:  # 7 days
                        log_file.unlink()
                        self.logger.info(f"Removed old log file: {log_file}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up temp files: {e}")
    
    def cleanup(self):
        """Cleanup on exit."""
        try:
            self.release_lock()
            self.logger.info("Startup coordinator cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def main():
    """Main entry point for startup coordination."""
    coordinator = StartupCoordinator()
    
    # Coordinate Dear PyGui startup
    if coordinator.coordinate_dearpygui_startup():
        print("Startup coordination completed successfully")
        return True
    else:
        print("Startup coordination failed")
        return False

if __name__ == "__main__":
    main() 