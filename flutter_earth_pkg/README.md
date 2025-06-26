# Flutter Earth Package (`flutter_earth_pkg`)

This directory contains the core Python package for the Flutter Earth application. It is structured as a modern, installable Python package to encapsulate all backend logic and application-specific code.

## Package Architecture

The `flutter_earth` package is designed with a modular architecture to separate concerns and improve maintainability. The key modules are:

-   `__init__.py`: Initializes the package.
-   `main.py`: The primary entry point for launching the application.
-   `gui.py`: Manages the Qt/QML application window, sets up the application engine, and creates the `AppBackend` bridge to expose Python functions to the QML frontend.
-   `config.py`: Handles all application configuration, including satellite details, themes, and user preferences. It uses a `dataclass`-based approach for type-safe settings management.
-   `types.py`: Defines all custom data types, `TypedDict`s, and `dataclass`es used throughout the application for robust data contracts.
-   `earth_engine.py`: Contains all logic for interacting with the Google Earth Engine API, such as initializing the connection, fetching collections, and building mosaics.
-   `processing.py`: Implements the core data processing pipelines, including cloud masking and sensor-specific scaling.
-   `download_manager.py`: Manages the downloading of processed tiles from Earth Engine.
-   `satellite_info.py`: Provides detailed information about the available satellites and their properties.
-   `qml/`: This directory holds all the QML source code that defines the structure, appearance, and behavior of the user interface.

## Purpose

The primary purpose of this package is to provide a complete, self-contained system for the Flutter Earth application. By packaging the logic this way, we ensure that:
-   Dependencies are clearly defined and managed in `requirements.txt`.
-   The code is portable and can be easily installed in different environments.
-   The separation between the UI (QML) and the backend (Python) is clean, allowing for independent development and testing.

## Usage

While this package is primarily designed to be run via the top-level `main.py`, its components can also be used programmatically.

### Example: Using the ConfigManager
```python
from flutter_earth.config import ConfigManager

# Initialize the config manager
config = ConfigManager()

# Get a configuration value
max_workers = config.get('max_workers')
print(f"Max workers: {max_workers}")

# Set a new theme
config.set('theme', 'Light')
```

## Features

- Modern Qt-based GUI interface
- Support for multiple satellite data sources (Landsat, Sentinel-2, ERA5)
- Advanced cloud masking and image processing
- Vector data support (Shapefiles, GeoJSON)
- Interactive map selection
- Multi-threaded downloads
- Progress tracking and logging
- Theme customization

## Threading and Signal/Slot Best Practices

This codebase uses PySide6's `QThread` and `Signal`/`Slot` patterns for all long-running or parallel backend operations. This ensures safe, responsive GUI updates and robust background processing.

**Key Rules:**
- All threaded work must be done in a `QThread` subclass (e.g., `DownloadWorkerThread`, `SampleDownloadThread`).
- All communication with the GUI or main thread must use Qt `Signal`s. Never update the GUI directly from a worker thread.
- Always connect signals before starting a thread.
- To cancel a thread, call its `request_cancel()` method (if available).
- Use type-annotated signals for clarity and safety.

### Example: Using DownloadWorkerThread
```python
from flutter_earth.download_worker import DownloadWorkerThread

def on_progress(current, total):
    print(f"Progress: {current}/{total}")

def on_complete(success, message):
    print(f"Done: {success}, {message}")

thread = DownloadWorkerThread(tiles, params, earth_engine, config)
thread.progress_update.connect(on_progress)
thread.download_complete.connect(on_complete)
thread.start()
# To cancel:
thread.request_cancel()
```

### Example: Using SampleDownloadThread
```python
from flutter_earth.processing import SampleDownloadThread

def on_sample_finished(sample_key, success, message):
    print(f"Sample {sample_key} finished: {success}, {message}")

thread = SampleDownloadThread(sample_key, config, base_path, earth_engine, download_manager)
thread.sample_download_finished.connect(on_sample_finished)
thread.start()
# To cancel:
thread.request_cancel()
```

**Best Practices:**
- Never block the main thread with long-running work.
- Use signals to report progress, errors, and completion.
- Always check for cancellation in your thread's `run()` method.
- Document all threaded classes with usage examples and signal signatures.

## Error Handling and User Feedback

All backend operations (especially threaded ones) emit robust error signals to provide both user-friendly and technical/log messages. This ensures that the GUI can display actionable feedback to users and log details for debugging.

**Key Pattern:**
- All threaded classes and managers emit `error_occurred: Signal(str, str)` (user_message, log_message).
- The GUI/backend bridge (e.g., `AppBackend`) connects to these signals and relays them to QML or logs them.
- The frontend can display user dialogs for user_message and log log_message for diagnostics.

### Example: Connecting Error Signals in the Backend
```python
# In your AppBackend or main window setup:
self.download_manager.error_occurred.connect(self.onDownloadError)

@Slot(str, str)
def onDownloadError(self, user_message, log_message):
    print(f"[Download Error] {user_message}\nDetails: {log_message}")
    # Optionally emit a QML signal or show a dialog
    self.downloadErrorOccurred.emit(user_message, log_message)
```

### Example: Handling Errors in QML
```qml
Connections {
    target: backend
    function onDownloadErrorOccurred(userMessage, logMessage) {
        // Show a dialog or notification
        errorDialog.text = userMessage + "\n" + logMessage;
        errorDialog.open();
    }
}
```

**Best Practices:**
- Always provide both a user-friendly and a technical message in error signals.
- Log all exceptions with `exc_info=True` for full tracebacks.
- Never show raw tracebacks to users; use user_message for dialogs and log_message for logs.
- Document all error signals and their usage in threaded classes and managers.

## Progress Tracking and User Feedback

All long-running operations (downloads, sample management, etc.) emit progress signals to provide real-time feedback to the GUI. This enables progress bars, status messages, and estimated time displays for users.

**Key Pattern:**
- All threaded classes and managers emit progress signals (e.g., `progress_update: Signal(int, int)` for downloads, `sample_download_progress: Signal(str, int, int)` for samples).
- The GUI/backend bridge (e.g., `AppBackend`) connects to these signals and relays them to QML.
- The frontend can display progress bars and status messages using these signals.

### Example: Connecting Progress Signals in the Backend
```python
# In your AppBackend or main window setup:
self.download_manager.progress_update.connect(self.onDownloadProgress)
self.sample_manager.sample_download_progress.connect(self.onSampleDownloadProgress)

@Slot(int, int)
def onDownloadProgress(self, current, total):
    self.downloadProgressUpdated.emit(current, total)

@Slot(str, int, int)
def onSampleDownloadProgress(self, sample_key, current, total):
    self.sampleDownloadProgressUpdated.emit(sample_key, current, total)
```

### Example: Handling Progress in QML
```qml
Connections {
    target: backend
    function onDownloadProgressUpdated(current, total) {
        progressBar.value = total > 0 ? current / total : 0;
    }
    function onSampleDownloadProgressUpdated(sampleKey, current, total) {
        // Update a per-sample progress bar or status
        sampleProgressBar.value = total > 0 ? current / total : 0;
    }
}
```

**Best Practices:**
- Always emit progress signals at meaningful steps (not too frequent, not too sparse).
- Use consistent signal signatures for all progress updates.
- Document all progress signals and their usage in threaded classes and managers.

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Authenticate with Google Earth Engine:
```bash
earthengine authenticate
```

## Usage

1. Run the application:
```bash
python flutter_earth_6-19.py
```

2. Select your area of interest using one of the following methods:
   - Draw on the interactive map
   - Import a shapefile
   - Enter coordinates manually

3. Choose your satellite data source and time range

4. Configure processing options:
   - Cloud masking
   - Resolution
   - Bands to download
   - Output format

5. Start the download process

## Configuration

The application stores its configuration in a JSON file. You can modify the following settings:
- Default output directory
- Tile size and overlap
- UI theme
- Processing parameters

## Troubleshooting

1. If you encounter authentication issues:
   - Ensure you've run `earthengine authenticate`
   - Check your internet connection
   - Verify your Google Earth Engine account is active

2. For performance issues:
   - Reduce the size of your area of interest
   - Increase tile size
   - Check available disk space

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 