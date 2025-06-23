"""Logging setup for Flutter Earth."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """Setup logging for Flutter Earth.
    
    Args:
        level: Logging level.
        log_file: Optional log file path.
        console_output: Whether to output to console.
        
    Returns:
        Configured logger.
    """
    # Create logger
    logger = logging.getLogger("flutter_earth")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_default_log_file() -> Path:
    """Get default log file path.
    
    Returns:
        Default log file path.
    """
    logs_dir = Path.home() / ".flutter_earth" / "logs"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return logs_dir / f"flutter_earth_{timestamp}.log"


def setup_application_logging() -> logging.Logger:
    """Setup logging for the Flutter Earth application.
    
    Returns:
        Configured logger.
    """
    log_file = get_default_log_file()
    return setup_logging(
        level="INFO",
        log_file=log_file,
        console_output=True
    ) 