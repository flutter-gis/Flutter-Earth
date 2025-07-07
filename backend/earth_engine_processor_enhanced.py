#!/usr/bin/env python3
"""
Enhanced Earth Engine Processor - Modern implementation with improved architecture
Handles all Earth Engine operations with enhanced error handling and logging
"""
import sys
import json
import os
import logging
import time
from pathlib import Path
from datetime import datetime
import gzip
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import traceback

# Enhanced logging setup
def setup_enhanced_logging() -> logging.Logger:
    """Setup enhanced logging with structured output and rotation"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f"earth_engine_processor_enhanced_{timestamp}.log"
    
    # Create formatter with enhanced structure
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Setup root logger
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, console_handler],
        force=True
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Enhanced Earth Engine Processor initialized")
    return logger

# Data structures for better type safety
@dataclass
class DownloadProgress:
    """Structured download progress tracking"""
    download_id: str
    start_time: str
    status: str
    percentage: float
    message: str
    bytes_downloaded: int
    total_bytes: int
    elapsed_time: float
    completed: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DownloadParams:
    """Structured download parameters"""
    area_of_interest: str
    start_date: str
    end_date: str
    sensor_name: str
    output_dir: str
    cloud_mask: bool = False
    cloud_cover: int = 20
    resolution: Optional[int] = None
    tiling_method: str = "degree"
    satellite_name: Optional[str] = None
    code_snippet: Optional[str] = None

class EnhancedEarthEngineProcessor:
    """Enhanced Earth Engine processor with modern architecture"""
    
    def __init__(self):
        self.logger = setup_enhanced_logging()
        self.current_downloads: Dict[str, DownloadProgress] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Add flutter_earth_pkg to path
        flutter_earth_path = Path(__file__).parent.parent / 'flutter_earth_pkg'
        if flutter_earth_path.exists():
            sys.path.insert(0, str(flutter_earth_path))
        
        # Import required modules with fallback
        try:
            from flutter_earth.earth_engine import EarthEngineManager
            from flutter_earth.download_manager import DownloadManager
            from flutter_earth.config import ConfigManager
            from flutter_earth.progress_tracker import ProgressTracker
            from flutter_earth.auth_setup import AuthManager
            
            self.earth_engine = EarthEngineManager()
            self.download_manager = DownloadManager()
            self.config_manager = ConfigManager()
            self.progress_tracker = ProgressTracker()
            self.auth_manager = AuthManager()
            
            self.logger.info("All Earth Engine modules imported successfully")
        except ImportError as e:
            self.logger.warning(f"Some Earth Engine modules not available: {e}")
            # Create placeholder objects for missing modules
            self.earth_engine = None
            self.download_manager = None
            self.config_manager = None
            self.progress_tracker = None
            self.auth_manager = None

    def initialize_earth_engine(self) -> Dict[str, Any]:
        """Initialize Earth Engine with enhanced error handling"""
        try:
            self.logger.info("Starting enhanced Earth Engine initialization")
            
            # Check if GEE is already initialized
            try:
                import ee
                if hasattr(ee, 'data') and hasattr(ee.data, '_credentials') and ee.data._credentials:
                    self.logger.info("Earth Engine already initialized, testing connection")
                    test_image = ee.Image('USGS/SRTMGL1_003')
                    _ = test_image.geometry().bounds().getInfo()
                    self.logger.info("Earth Engine connection verified")
                    return {
                        "status": "online",
                        "message": "Earth Engine already initialized and healthy",
                        "initialized": True,
                        "timestamp": datetime.now().isoformat()
                    }
            except Exception as e:
                self.logger.warning(f"Earth Engine not initialized or unhealthy: {e}")
            
            # Initialize Earth Engine if available
            if self.earth_engine:
                result = self.earth_engine.initialize()
                self.logger.info(f"Earth Engine initialization result: {result}")
                
                return {
                    **result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "Earth Engine modules not available",
                    "initialized": False,
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"Earth Engine initialization failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Initialization error: {str(e)}",
                "initialized": False,
                "timestamp": datetime.now().isoformat(),
                "traceback": traceback.format_exc()
            }

    def start_download(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a download with enhanced parameter validation and progress tracking"""
        try:
            self.logger.info(f"Starting enhanced download with params: {params}")
            
            # Validate and structure parameters
            download_params = self._validate_download_params(params)
            
            # Handle satellite-specific downloads
            if download_params.satellite_name:
                self._process_satellite_download(download_params)
            
            # Create download progress tracker
            download_id = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            progress = DownloadProgress(
                download_id=download_id,
                start_time=datetime.now().isoformat(),
                status="initializing",
                percentage=0.0,
                message="Validating parameters and preparing download...",
                bytes_downloaded=0,
                total_bytes=0,
                elapsed_time=0.0,
                completed=False
            )
            
            self.current_downloads[download_id] = progress
            
            # Start download in background thread
            self.executor.submit(self._execute_download, download_id, download_params)
            
            self.logger.info(f"Download {download_id} started successfully")
            return {
                "status": "success",
                "message": "Download started successfully",
                "download_id": download_id,
                "params": asdict(download_params)
            }
            
        except Exception as e:
            self.logger.error(f"Download start failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Download error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _validate_download_params(self, params: Dict[str, Any]) -> DownloadParams:
        """Validate and structure download parameters"""
        required_fields = ['area_of_interest', 'start_date', 'end_date', 'sensor_name', 'output_dir']
        missing_fields = [field for field in required_fields if field not in params]
        
        if missing_fields:
            raise ValueError(f"Missing required parameters: {', '.join(missing_fields)}")
        
        return DownloadParams(
            area_of_interest=params['area_of_interest'],
            start_date=params['start_date'],
            end_date=params['end_date'],
            sensor_name=params['sensor_name'],
            output_dir=params['output_dir'],
            cloud_mask=params.get('cloud_mask', False),
            cloud_cover=params.get('cloud_cover', 20),
            resolution=params.get('resolution'),
            tiling_method=params.get('tiling_method', 'degree'),
            satellite_name=params.get('satellite_name'),
            code_snippet=params.get('code_snippet')
        )

    def _process_satellite_download(self, params: DownloadParams):
        """Process satellite-specific download parameters"""
        if not params.satellite_name:
            return
            
        crawler_data_path = Path('backend/crawler_data/gee_catalog_data_enhanced.json.gz')
        if crawler_data_path.exists():
            try:
                with gzip.open(crawler_data_path, 'rt', encoding='utf-8') as f:
                    crawler_data = json.load(f)
                
                satellite_data = crawler_data.get('satellites', {}).get(params.satellite_name, [])
                if satellite_data:
                    # Use the first dataset's code snippet
                    code_snippet = satellite_data[0].get('code_snippet', '')
                    if code_snippet:
                        params.code_snippet = code_snippet
                        params.sensor_name = params.satellite_name.lower()
                        self.logger.info(f"Using code snippet for {params.satellite_name}")
            except Exception as e:
                self.logger.warning(f"Failed to load satellite data: {e}")

    def _execute_download(self, download_id: str, params: DownloadParams):
        """Execute the actual download in background thread"""
        try:
            progress = self.current_downloads[download_id]
            progress.status = "downloading"
            progress.message = "Starting data download..."
            
            # Simulate download progress (replace with actual implementation)
            for i in range(101):
                progress.percentage = i
                progress.message = f"Downloading data... {i}%"
                progress.elapsed_time = (datetime.now() - datetime.fromisoformat(progress.start_time)).total_seconds()
                time.sleep(0.1)  # Simulate work
            
            progress.status = "completed"
            progress.percentage = 100.0
            progress.message = "Download completed successfully"
            progress.completed = True
            
            self.logger.info(f"Download {download_id} completed successfully")
            
        except Exception as e:
            progress = self.current_downloads[download_id]
            progress.status = "error"
            progress.error = str(e)
            progress.message = f"Download failed: {str(e)}"
            self.logger.error(f"Download {download_id} failed: {e}", exc_info=True)

    def get_progress(self, download_id: Optional[str] = None) -> Dict[str, Any]:
        """Get download progress with enhanced structure"""
        try:
            if download_id:
                progress = self.current_downloads.get(download_id)
                if progress:
                    return asdict(progress)
                else:
                    return {"error": f"Download {download_id} not found"}
            else:
                # Return all active downloads
                return {
                    "downloads": [asdict(progress) for progress in self.current_downloads.values()],
                    "total_active": len(self.current_downloads)
                }
        except Exception as e:
            self.logger.error(f"Error getting progress: {e}")
            return {"error": str(e)}

    def check_auth_needed(self) -> Dict[str, Any]:
        """Check if authentication is needed with enhanced status"""
        try:
            if self.auth_manager:
                auth_status = self.auth_manager.check_auth_status()
                return {
                    **auth_status,
                    "timestamp": datetime.now().isoformat(),
                    "enhanced": True
                }
            else:
                return {
                    "status": "error",
                    "message": "Auth manager not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Auth check failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def set_auth_credentials(self, key_file: str, project_id: str) -> Dict[str, Any]:
        """Set authentication credentials with enhanced validation"""
        try:
            if self.auth_manager:
                result = self.auth_manager.set_credentials(key_file, project_id)
                return {
                    **result,
                    "timestamp": datetime.now().isoformat(),
                    "enhanced": True
                }
            else:
                return {
                    "status": "error",
                    "message": "Auth manager not available",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Auth setup failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def run_web_crawler(self) -> Dict[str, Any]:
        """Run the enhanced web crawler"""
        try:
            self.logger.info("Starting enhanced web crawler")
            
            # Import and run the enhanced crawler
            from gee_catalog_crawler_enhanced_v2 import run_enhanced_crawler
            result = run_enhanced_crawler()
            
            return {
                "status": "success",
                "message": "Web crawler completed successfully",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Web crawler failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global processor instance
processor = None

def get_processor() -> EnhancedEarthEngineProcessor:
    """Get or create the global processor instance"""
    global processor
    if processor is None:
        processor = EnhancedEarthEngineProcessor()
    return processor

# Main function for command line usage
def main():
    """Main function for command line usage and service mode"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Enhanced Earth Engine Processor")
    parser.add_argument("--action", choices=["init", "download", "progress", "auth", "service"], 
                       help="Action to perform")
    parser.add_argument("--params", type=str, help="JSON parameters")
    parser.add_argument("--service", action="store_true", help="Run as service mode")
    
    args = parser.parse_args()
    
    # If no arguments provided, run as service
    if len(sys.argv) == 1:
        args.service = True
    
    if args.service:
        run_as_service()
    else:
        run_command_line(args)

def run_as_service():
    """Run the processor as a service for Electron communication"""
    logger = setup_enhanced_logging()
    logger.info("Starting Enhanced Earth Engine Processor as service...")
    
    try:
        # Initialize processor
        proc = get_processor()
        logger.info("Processor initialized successfully")
        
        # Initialize Earth Engine
        logger.info("Initializing Earth Engine...")
        init_result = proc.initialize_earth_engine()
        logger.info(f"Earth Engine initialization: {init_result}")
        
        print("=" * 60)
        print("Enhanced Earth Engine Processor v2.0")
        print("=" * 60)
        print(f"Status: {init_result.get('status', 'unknown')}")
        print(f"Message: {init_result.get('message', 'No message')}")
        print(f"Enhanced: {init_result.get('enhanced', True)}")
        print("=" * 60)
        print()
        print("Processor is running as a service.")
        print("The Electron frontend will communicate with this processor.")
        print()
        print("Press Ctrl+C to stop the service.")
        print("=" * 60)
        
        # Keep the service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
            print("\nService stopped.")
            
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1
    
    return 0

def run_command_line(args):
    """Run the processor with command line arguments"""
    proc = get_processor()
    
    if args.action == "init":
        result = proc.initialize_earth_engine()
    elif args.action == "download":
        params = json.loads(args.params) if args.params else {}
        result = proc.start_download(params)
    elif args.action == "progress":
        result = proc.get_progress()
    elif args.action == "auth":
        result = proc.check_auth_needed()
    else:
        print("Invalid action. Use --help for usage information.")
        return 1
    
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 