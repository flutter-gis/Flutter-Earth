"""
Flutter Earth - Main Application Entry Point
"""
import sys
import os
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Add the flutter_earth_pkg directory to sys.path
sys.path.insert(0, str(Path(__file__).parent / "flutter_earth_pkg"))

def install_dependencies():
    """
    Installs all packages from the requirements.txt file using pip.
    This is triggered if an ImportError occurs, suggesting missing dependencies.
    """
    logger = logging.getLogger(__name__)
    # Correctly locate the requirements.txt inside the package directory
    requirements_path = Path(__file__).parent / "flutter_earth_pkg" / "requirements.txt"
    
    if not requirements_path.exists():
        msg = f"Could not find requirements.txt at {requirements_path}. Cannot install dependencies."
        logger.error(msg)
        print(f"ERROR: {msg}")
        return

    print("\nOne or more required packages seem to be missing.")
    print("Attempting to install them now using pip...")
    logger.info(f"Attempting to install dependencies from {requirements_path}")
    
    try:
        # Use sys.executable to ensure pip from the correct python environment is used.
        # The '--quiet' flag reduces the verbosity of the output.
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', '-r', str(requirements_path)])
        
        logger.info("Successfully installed packages via pip.")
        print("\nDependencies have been installed successfully.")
        print("Please restart the application to continue.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install packages using pip: {e}", exc_info=True)
        print(f"\nERROR: Could not install required packages automatically.")
        print(f"Please try to install them manually by running the following command in your terminal:")
        print(f"pip install -r \"{requirements_path}\"")

def setup_logging():
    """Configure logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"flutter_earth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress verbose logging from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)

def main():
    """
    Checks for dependencies, then initializes and runs the QML GUI for Flutter Earth.
    """
    # Setup logging first to capture all messages.
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # We try to import the main GUI class. If it fails due to a missing
        # dependency, we'll catch the ImportError and try to fix it.
        from flutter_earth.gui import QmlGUILauncher
    except ImportError as e:
        logger.warning(f"Failed to import application modules: {e}. This is often caused by missing packages.")
        install_dependencies()
        # Exit after attempting installation. The user needs to restart the app
        # for the new packages to be recognized.
        sys.exit(0)

    try:
        logger.info("Starting Flutter Earth QML Application")
        
        # The QmlGUILauncher now manages its own backend components.
        launcher = QmlGUILauncher()
        launcher.launch()

    except Exception as e:
        logger.critical(f"A critical error occurred, and the application cannot start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
