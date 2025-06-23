"""Progress tracking for Flutter Earth."""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class ProgressTracker:
    """Tracks progress of operations."""
    
    def __init__(self):
        """Initialize the progress tracker."""
        self._logger = logging.getLogger(__name__)
        self._progress: Dict[str, float] = {}
        self._status: Dict[str, str] = {}
        self._start_times: Dict[str, datetime] = {}
        self._callbacks: Dict[str, Callable[[str, float], None]] = {}
    
    def start_tracking(self, task_id: str, callback: Optional[Callable[[str, float], None]] = None) -> None:
        """Start tracking progress for a task.
        
        Args:
            task_id: Task ID.
            callback: Optional callback function.
        """
        self._progress[task_id] = 0.0
        self._status[task_id] = "Starting..."
        self._start_times[task_id] = datetime.now()
        
        if callback:
            self._callbacks[task_id] = callback
        
        self._logger.debug(f"Started tracking task {task_id}")
    
    def update_progress(self, task_id: str, progress: float, status: Optional[str] = None) -> None:
        """Update progress for a task.
        
        Args:
            task_id: Task ID.
            progress: Progress value (0.0 to 1.0).
            status: Optional status message.
        """
        if task_id not in self._progress:
            self._logger.warning(f"Task {task_id} not being tracked")
            return
        
        # Clamp progress to valid range
        progress = max(0.0, min(1.0, progress))
        
        self._progress[task_id] = progress
        
        if status:
            self._status[task_id] = status
        
        # Call callback if registered
        if task_id in self._callbacks:
            try:
                self._callbacks[task_id](task_id, progress)
            except Exception as e:
                self._logger.error(f"Error in progress callback for {task_id}: {e}")
        
        self._logger.debug(f"Task {task_id} progress: {progress:.2%} - {self._status[task_id]}")
    
    def get_progress(self, task_id: str) -> Optional[float]:
        """Get progress for a task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Progress value or None if not found.
        """
        return self._progress.get(task_id)
    
    def get_status(self, task_id: str) -> Optional[str]:
        """Get status for a task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Status message or None if not found.
        """
        return self._status.get(task_id)
    
    def get_elapsed_time(self, task_id: str) -> Optional[float]:
        """Get elapsed time for a task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Elapsed time in seconds or None if not found.
        """
        if task_id not in self._start_times:
            return None
        
        elapsed = datetime.now() - self._start_times[task_id]
        return elapsed.total_seconds()
    
    def stop_tracking(self, task_id: str) -> None:
        """Stop tracking progress for a task.
        
        Args:
            task_id: Task ID.
        """
        if task_id in self._progress:
            del self._progress[task_id]
        
        if task_id in self._status:
            del self._status[task_id]
        
        if task_id in self._start_times:
            del self._start_times[task_id]
        
        if task_id in self._callbacks:
            del self._callbacks[task_id]
        
        self._logger.debug(f"Stopped tracking task {task_id}")
    
    def get_all_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get progress for all tracked tasks.
        
        Returns:
            Dictionary of task progress information.
        """
        result = {}
        
        for task_id in self._progress:
            result[task_id] = {
                "progress": self._progress[task_id],
                "status": self._status.get(task_id, "Unknown"),
                "elapsed_time": self.get_elapsed_time(task_id)
            }
        
        return result
    
    def clear_all(self) -> None:
        """Clear all progress tracking."""
        self._progress.clear()
        self._status.clear()
        self._start_times.clear()
        self._callbacks.clear()
        
        self._logger.debug("Cleared all progress tracking") 