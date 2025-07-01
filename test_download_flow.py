#!/usr/bin/env python3
"""
Test script to verify the download functionality works end-to-end.
This script simulates the download process that should happen when the button is clicked.
"""

import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_download_flow():
    """Test the download flow by calling the backend directly."""
    
    # Test parameters (similar to what the frontend would send)
    test_params = {
        "area_of_interest": "[0, 0, 1, 1]",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "sensor_name": "landsat-8",
        "output_dir": "./test_downloads",
        "cloud_mask": True,
        "max_cloud_cover": 20,
        "best_resolution": True,
        "target_resolution": 30,
        "tiling_method": "grid",
        "num_subsections": 4,
        "overwrite_existing": False,
        "cleanup_tiles": True,
        "satellite_name": "Landsat 8",
        "crawler_data": True
    }
    
    print("Testing download flow with parameters:")
    print(json.dumps(test_params, indent=2))
    print()
    
    try:
        # Import the backend module
        from earth_engine_processor import start_download, get_progress
        
        print("1. Starting download...")
        result = start_download(test_params)
        print(f"Download start result: {result}")
        
        if result.get('status') == 'success':
            download_id = result.get('download_id')
            print(f"Download ID: {download_id}")
            
            print("\n2. Checking progress...")
            for i in range(5):  # Check progress 5 times
                progress = get_progress()
                print(f"Progress {i+1}: {progress}")
                
                if progress.get('completed'):
                    print("Download completed!")
                    break
                    
                import time
                time.sleep(1)  # Wait 1 second between checks
        else:
            print(f"Download failed to start: {result}")
            
    except ImportError as e:
        print(f"Error importing backend module: {e}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download_flow() 