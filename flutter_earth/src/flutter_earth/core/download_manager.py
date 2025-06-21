"""Download management for Flutter Earth."""

import logging
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

from .types import (
    DownloadTask, ProcessingParams, ProcessingResult, DownloadStatus,
    BoundingBox, Polygon, OutputFormat, VegetationIndex
)


class DownloadManager:
    """Manages download operations."""
    
    def __init__(self):
        """Initialize the download manager."""
        self._logger = logging.getLogger(__name__)
        self._tasks: Dict[str, DownloadTask] = {}
        self._task_queue = queue.Queue()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._max_concurrent_downloads = 3
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self._progress_callback: Optional[Callable[[str, float], None]] = None
        self._status_callback: Optional[Callable[[str, DownloadStatus], None]] = None
        self._completion_callback: Optional[Callable[[str, ProcessingResult], None]] = None
    
    def start(self, max_concurrent: int = 3) -> None:
        """Start the download manager.
        
        Args:
            max_concurrent: Maximum number of concurrent downloads.
        """
        if self._running:
            self._logger.warning("Download manager already running")
            return
        
        self._max_concurrent_downloads = max_concurrent
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self._running = True
        
        # Start worker thread
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        
        self._logger.info(f"Download manager started with {max_concurrent} workers")
    
    def stop(self) -> None:
        """Stop the download manager."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel all pending tasks
        for task_id in list(self._tasks.keys()):
            if self._tasks[task_id].status == DownloadStatus.PENDING:
                self._tasks[task_id].status = DownloadStatus.CANCELLED
                self._tasks[task_id].completed_at = datetime.now()
        
        # Shutdown executor
        if self._executor:
            self._executor.shutdown(wait=True)
        
        self._logger.info("Download manager stopped")
    
    def add_task(self, params: ProcessingParams) -> str:
        """Add a download task.
        
        Args:
            params: Processing parameters.
            
        Returns:
            Task ID.
        """
        task_id = f"task_{int(time.time() * 1000)}"
        
        task = DownloadTask(
            id=task_id,
            params=params
        )
        
        self._tasks[task_id] = task
        self._task_queue.put(task_id)
        
        self._logger.info(f"Added download task {task_id}")
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a download task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            True if task was cancelled.
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status in [DownloadStatus.PENDING, DownloadStatus.DOWNLOADING, DownloadStatus.PROCESSING]:
            task.status = DownloadStatus.CANCELLED
            task.completed_at = datetime.now()
            
            if self._status_callback:
                self._status_callback(task_id, DownloadStatus.CANCELLED)
            
            self._logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """Get a task by ID.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Task or None if not found.
        """
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[DownloadTask]:
        """Get all tasks.
        
        Returns:
            List of all tasks.
        """
        return list(self._tasks.values())
    
    def get_active_tasks(self) -> List[DownloadTask]:
        """Get active tasks.
        
        Returns:
            List of active tasks.
        """
        return [
            task for task in self._tasks.values()
            if task.status in [DownloadStatus.PENDING, DownloadStatus.DOWNLOADING, DownloadStatus.PROCESSING]
        ]
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Set progress callback.
        
        Args:
            callback: Progress callback function.
        """
        self._progress_callback = callback
    
    def set_status_callback(self, callback: Callable[[str, DownloadStatus], None]) -> None:
        """Set status callback.
        
        Args:
            callback: Status callback function.
        """
        self._status_callback = callback
    
    def set_completion_callback(self, callback: Callable[[str, ProcessingResult], None]) -> None:
        """Set completion callback.
        
        Args:
            callback: Completion callback function.
        """
        self._completion_callback = callback
    
    def _worker_loop(self) -> None:
        """Main worker loop."""
        while self._running:
            try:
                # Get next task
                task_id = self._task_queue.get(timeout=1.0)
                task = self._tasks[task_id]
                
                # Check if task was cancelled
                if task.status == DownloadStatus.CANCELLED:
                    continue
                
                # Submit task to executor
                future = self._executor.submit(self._process_task, task)
                future.add_done_callback(lambda f, tid=task_id: self._task_completed(tid, f))
                
            except queue.Empty:
                continue
            except Exception as e:
                self._logger.error(f"Error in worker loop: {e}")
    
    def _process_task(self, task: DownloadTask) -> ProcessingResult:
        """Process a download task.
        
        Args:
            task: Download task.
            
        Returns:
            Processing result.
        """
        start_time = time.time()
        
        try:
            # Update status
            task.status = DownloadStatus.DOWNLOADING
            task.started_at = datetime.now()
            
            if self._status_callback:
                self._status_callback(task.id, DownloadStatus.DOWNLOADING)
            
            # Validate parameters
            self._validate_params(task.params)
            
            # Create output directory
            output_dir = self._create_output_directory(task.params)
            
            # Download and process
            result = self._download_and_process(task.params, output_dir, task)
            
            # Update task
            task.status = DownloadStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 1.0
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            self._logger.info(f"Task {task.id} completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            # Update task
            task.status = DownloadStatus.FAILED
            task.completed_at = datetime.now()
            task.error_message = str(e)
            
            result = ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            task.result = result
            
            self._logger.error(f"Task {task.id} failed: {e}")
            return result
    
    def _task_completed(self, task_id: str, future) -> None:
        """Handle task completion.
        
        Args:
            task_id: Task ID.
            future: Future object.
        """
        try:
            result = future.result()
            
            if self._completion_callback:
                self._completion_callback(task_id, result)
            
        except Exception as e:
            self._logger.error(f"Error handling task completion for {task_id}: {e}")
    
    def _validate_params(self, params: ProcessingParams) -> None:
        """Validate processing parameters.
        
        Args:
            params: Processing parameters.
            
        Raises:
            ValueError: If parameters are invalid.
        """
        if not params.satellite_collections:
            raise ValueError("No satellite collections specified")
        
        if params.start_date >= params.end_date:
            raise ValueError("Start date must be before end date")
        
        if params.max_cloud_cover < 0 or params.max_cloud_cover > 100:
            raise ValueError("Cloud cover must be between 0 and 100")
    
    def _create_output_directory(self, params: ProcessingParams) -> Path:
        """Create output directory.
        
        Args:
            params: Processing parameters.
            
        Returns:
            Output directory path.
        """
        if params.output_directory:
            output_dir = params.output_directory
        else:
            output_dir = Path.home() / "flutter_earth_downloads"
        
        # Create subdirectory if enabled
        if params.filename_prefix:
            output_dir = output_dir / params.filename_prefix
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _download_and_process(
        self,
        params: ProcessingParams,
        output_dir: Path,
        task: DownloadTask
    ) -> ProcessingResult:
        """Download and process images.
        
        Args:
            params: Processing parameters.
            output_dir: Output directory.
            task: Download task.
            
        Returns:
            Processing result.
        """
        # This is a placeholder implementation
        # In a real implementation, this would:
        # 1. Search for images using Earth Engine
        # 2. Download images
        # 3. Process images (apply vegetation indices, etc.)
        # 4. Save results
        
        # Simulate progress
        for i in range(10):
            if task.status == DownloadStatus.CANCELLED:
                raise RuntimeError("Task cancelled")
            
            progress = (i + 1) / 10
            task.progress = progress
            
            if self._progress_callback:
                self._progress_callback(task.id, progress)
            
            time.sleep(0.5)  # Simulate work
        
        # Create dummy output file
        output_file = output_dir / f"{params.filename_prefix}_result.tif"
        output_file.touch()  # Create empty file
        
        return ProcessingResult(
            success=True,
            output_files=[output_file],
            metadata={
                "collection": params.satellite_collections[0],
                "start_date": params.start_date.isoformat(),
                "end_date": params.end_date.isoformat(),
                "cloud_cover": params.max_cloud_cover
            },
            file_size=output_file.stat().st_size
        ) 