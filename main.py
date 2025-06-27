"""Flutter Earth - A modern tool for downloading and processing satellite imagery."""
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
log_file = LOGS_DIR / f"flutter_earth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter(log_format))
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(log_format))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

def main():
    """Main entry point for Flutter Earth."""
    logging.info("=== Flutter Earth Application Started ===")
    logging.info(f"Log file: {log_file}")
    
    print("=" * 60)
    print("Flutter Earth - Desktop Application")
    print("=" * 60)
    print()
    print("This application now runs as an Electron desktop app.")
    print("To start the application:")
    print()
    print("1. Run: run_desktop.bat")
    print("   OR")
    print("2. Navigate to frontend/ and run: npm start")
    print()
    print("The Electron app provides a modern HTML/CSS/JS interface")
    print("that communicates directly with Python for Earth Engine operations.")
    print()
    print("For more information, see README.md")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
