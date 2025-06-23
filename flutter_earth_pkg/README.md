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