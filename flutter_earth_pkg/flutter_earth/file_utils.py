import os
import tempfile
import shutil
from typing import Optional

def safe_write_file(path: str, data: bytes) -> bool:
    """Safely write bytes to a file, creating parent directories if needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"Failed to write file {path}: {e}")
        return False

def safe_read_file(path: str) -> Optional[bytes]:
    """Safely read bytes from a file."""
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read file {path}: {e}")
        return None

def create_temp_file(suffix: str = '', prefix: str = 'tmp', dir: Optional[str] = None) -> str:
    """Create a temporary file and return its path."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    os.close(fd)
    return path

def create_temp_dir(prefix: str = 'tmp', dir: Optional[str] = None) -> str:
    """Create a temporary directory and return its path."""
    return tempfile.mkdtemp(prefix=prefix, dir=dir)

def cleanup_file(path: str) -> bool:
    """Remove a file if it exists."""
    try:
        if os.path.exists(path):
            os.remove(path)
        return True
    except Exception as e:
        print(f"Failed to remove file {path}: {e}")
        return False

def cleanup_dir(path: str) -> bool:
    """Remove a directory and all its contents if it exists."""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        return True
    except Exception as e:
        print(f"Failed to remove directory {path}: {e}")
        return False

def ensure_dir_exists(path: str) -> bool:
    """Ensure a directory exists, creating it if needed."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {path}: {e}")
        return False

def file_exists_and_size(path: str, min_size: int = 1024) -> bool:
    """Check if a file exists and is at least min_size bytes."""
    return os.path.exists(path) and os.path.getsize(path) >= min_size 