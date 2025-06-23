"""Basic usage example for Flutter Earth."""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flutter_earth.core.types import (
    BoundingBox, ProcessingParams, OutputFormat, VegetationIndex
)
from flutter_earth.core.config_manager import ConfigManager
from flutter_earth.core.earth_engine_manager import EarthEngineManager
from flutter_earth.core.download_manager import DownloadManager
from flutter_earth.core.progress_tracker import ProgressTracker


def main():
    """Basic usage example."""
    print("Flutter Earth - Basic Usage Example")
    print("=" * 40)
    
    # Initialize components
    print("Initializing components...")
    config_manager = ConfigManager()
    earth_engine_manager = EarthEngineManager()
    download_manager = DownloadManager()
    progress_tracker = ProgressTracker()
    
    # Create a bounding box for New York City area
    bbox = BoundingBox(
        min_lon=-74.2591,
        min_lat=40.4774,
        max_lon=-73.7004,
        max_lat=40.9162
    )
    
    # Create processing parameters
    params = ProcessingParams(
        area_of_interest=bbox,
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        satellite_collections=["LANDSAT/LC08/C02/T1_L2"],
        output_format=OutputFormat.GEOTIFF,
        spatial_resolution=30.0,
        max_cloud_cover=20.0,
        vegetation_indices=[VegetationIndex.NDVI, VegetationIndex.EVI],
        filename_prefix="nyc_example"
    )
    
    print(f"Created processing parameters for area: {bbox}")
    print(f"Time period: {params.start_date.date()} to {params.end_date.date()}")
    print(f"Satellite collections: {params.satellite_collections}")
    print(f"Output format: {params.output_format.value}")
    print(f"Vegetation indices: {[idx.value for idx in params.vegetation_indices]}")
    
    # Start download manager
    print("\nStarting download manager...")
    download_manager.start()
    
    # Add download task
    print("Adding download task...")
    task_id = download_manager.add_task(params)
    print(f"Task ID: {task_id}")
    
    # Start progress tracking
    progress_tracker.start_tracking(task_id)
    
    # Simulate progress updates
    print("\nSimulating progress...")
    for i in range(5):
        progress = (i + 1) / 5
        progress_tracker.update_progress(task_id, progress, f"Step {i + 1}/5")
        print(f"Progress: {progress:.1%}")
    
    # Get task information
    task = download_manager.get_task(task_id)
    if task:
        print(f"\nTask status: {task.status.value}")
        print(f"Task progress: {task.progress:.1%}")
    
    # Cleanup
    print("\nCleaning up...")
    download_manager.stop()
    progress_tracker.clear_all()
    
    print("Example completed!")


if __name__ == "__main__":
    main() 