import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

# Add the package to the Python path if it's not already
# This assumes main.py is in the root and flutter_earth_pkg is a sibling directory
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    from flutter_earth_pkg.flutter_earth.gui import QmlGUILauncher
    from flutter_earth_pkg.flutter_earth.utils import setup_logging, QtLogHandler
    # from flutter_earth_pkg.flutter_earth.config import ConfigManager # Not strictly needed for basic launch
except ImportError as e:
    print(f"Error importing Flutter Earth modules: {e}")
    print("Please ensure flutter_earth_pkg is in the correct directory and all dependencies are installed from flutter_earth_pkg/requirements.txt.")
    sys.exit(1)

if __name__ == "__main__":
    # Set an environment variable to tell Qt where to find QML plugins, if necessary.
    # This is often needed if the app isn't "installed" in a standard location.
    # os.environ["QT_PLUGIN_PATH"] = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "PySide6", "plugins")
    # os.environ["QML2_IMPORT_PATH"] = os.path.join(os.path.dirname(sys.executable), "Lib", "site-packages", "PySide6", "qml")
    # The above lines are examples and might need adjustment based on the environment.

    app = QApplication(sys.argv)

    # Setup logging (minimal for now, can be expanded with config)
    qt_log_handler = QtLogHandler()
    # In a real app, you'd connect qt_log_handler.log_signal to a QML item
    # For now, it will just allow utils.setup_logging to add it.
    logger = setup_logging(gui_handler=qt_log_handler)

    logger.info("Starting Flutter Earth QML Application...")

    launcher = QmlGUILauncher()
    launcher.launch()
    # launcher.launch() contains app.exec(), so no need for sys.exit(app.exec()) here

    logger.info("Flutter Earth QML Application finished.")
