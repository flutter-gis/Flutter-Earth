"""Progress tracking for Flutter Earth."""
import logging
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta

class ProgressTracker:
    """Tracks progress of long-running operations."""
    
    def __init__(self):
        """Initialize progress tracker."""
        self.logger = logging.getLogger(__name__)
        self.current_operation: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.total_items = 0
        self.completed_items = 0
        self.callback: Optional[Callable] = None
        self.status = "idle"
        self.error: Optional[str] = None
    
    def initialize(self) -> None:
        """Initialize or reset the tracker."""
        self.current_operation = None
        self.start_time = None
        self.total_items = 0
        self.completed_items = 0
        self.status = "idle"
        self.error = None
    
    def start_operation(
        self,
        operation_name: str,
        total_items: int,
        callback: Optional[Callable] = None
    ) -> None:
        """Start tracking a new operation.
        
        Args:
            operation_name: Name of the operation.
            total_items: Total number of items to process.
            callback: Optional callback for progress updates.
        """
        self.initialize()
        self.current_operation = operation_name
        self.start_time = datetime.now()
        self.total_items = total_items
        self.callback = callback
        self.status = "running"
        
        self._notify_progress()
    
    def update_progress(self, completed_items: int) -> None:
        """Update progress of current operation.
        
        Args:
            completed_items: Number of items completed.
        """
        if not self.current_operation:
            return
            
        self.completed_items = completed_items
        self._notify_progress()
    
    def complete_operation(self, success: bool = True, error: Optional[str] = None) -> None:
        """Mark current operation as complete.
        
        Args:
            success: Whether the operation completed successfully.
            error: Optional error message if operation failed.
        """
        if not self.current_operation:
            return
            
        self.completed_items = self.total_items if success else 0
        self.status = "completed" if success else "failed"
        self.error = error
        
        self._notify_progress()
        
        # Reset after notification
        self.initialize()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information.
        
        Returns:
            Dictionary containing progress information.
        """
        if not self.current_operation:
            return {
                'status': 'idle',
                'operation': None,
                'progress': 0,
                'elapsed_time': None,
                'estimated_time': None,
                'error': None
            }
        
        progress = self.completed_items / self.total_items if self.total_items > 0 else 0
        elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        # Calculate estimated time remaining
        if progress > 0:
            total_time = elapsed.total_seconds() / progress
            remaining = timedelta(seconds=total_time - elapsed.total_seconds())
        else:
            remaining = None
        
        return {
            'status': self.status,
            'operation': self.current_operation,
            'progress': progress,
            'completed': self.completed_items,
            'total': self.total_items,
            'elapsed_time': str(elapsed).split('.')[0],
            'estimated_time': str(remaining).split('.')[0] if remaining else None,
            'error': self.error
        }
    
    def _notify_progress(self) -> None:
        """Notify progress callback if set."""
        if self.callback:
            try:
                self.callback(self.get_progress())
            except Exception as e:
                self.logger.error(f"Error in progress callback: {e}") 