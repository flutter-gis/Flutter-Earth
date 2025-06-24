# Flutter Earth - QML Edition

A powerful, user-friendly tool for downloading and processing satellite imagery using the Google Earth Engine, now with a modern QML-based interface.

## Features

-   **Modern QML Interface**: A sleek and responsive user interface built with Qt for a better user experience.
-   **Modular Backend**: The application is now structured as a professional Python package for better maintainability and scalability.
-   **Theming Support**: Switch between 'Dark', 'Light', and 'Sanofi' themes.
-   **Advanced Downloading**: Download satellite imagery from multiple sensors like Landsat and Sentinel-2.
-   **On-the-fly Processing**: Includes cloud masking and other pre-processing capabilities.
-   **Robust Configuration**: A clear, class-based configuration system manages all settings.
-   **Comprehensive Satellite Info**: Browse detailed information about available satellites.
-   **Interactive Map Selection**: Draw polygons and rectangles directly on the map (via QML MapView).
-   **Vegetation Indices**: Calculation for NDVI, EVI available post-download.

## Prerequisites

-   Python 3.8 or higher
-   A Google Earth Engine account with API access enabled.
-   Required Python packages (see `flutter_earth_pkg/requirements.txt`).

## Installation

### 1. Clone the repository

```bash
git clone <repository-url> # Replace <repository-url> with the actual URL
cd Flutter-Earth
```

### 2. Install required packages

The dependencies are managed within the `flutter_earth_pkg`.

```bash
pip install -r flutter_earth_pkg/requirements.txt
```

### 3. Set up Earth Engine Authentication

The application primarily uses a **service account** for authentication with Google Earth Engine. You will need to:
1.  **Create a Google Cloud Project** and enable the Earth Engine API.
2.  **Create a Service Account** within your project and grant it appropriate permissions (e.g., "Earth Engine Resource Viewer").
3.  **Download the JSON key file** for your service account.

For detailed, step-by-step instructions, please refer to `EARTH_ENGINE_SETUP.md`.
Alternatively, traditional `earthengine authenticate` can be used if service account setup is not preferred, though the application is geared towards service accounts.

## Quick Start

### Launch the Application

```bash
python main.py
```
Or use the provided run scripts if available (e.g., `run.bat` or `run.ps1` on Windows).

Upon first launch, or if credentials are not found, you might be guided through the Earth Engine authentication setup via the application's UI if a service account key is not already configured in `flutter_earth_auth.json` or via environment variables.

### Basic Usage (QML Interface)

1.  **Home View**: Check Earth Engine status.
2.  **Map View**: Select an Area of Interest (AOI) by drawing a rectangle. Click "Set AOI for Download".
3.  **Download View**:
    *   The AOI from the map should ideally be pre-filled (current implementation might require manual entry or fixing).
    *   Set start and end dates.
    *   Choose a sensor.
    *   Configure cloud mask and max cloud cover.
    *   Specify an output directory.
    *   Click "Start Download".
4.  **Progress View**: Monitor download progress.
5.  **Settings View**:
    *   Change UI theme.
    *   Update default output directory.
    *   Clear cache and logs.

## Configuration

The application uses a configuration file (`flutter_earth_config.json`) managed by `flutter_earth_pkg/flutter_earth/config.py`. This file is typically created/updated in the root directory of the project on first run or when settings are changed. Key settings include:

-   Default output directory
-   UI Theme (`Default (Dark)`, `Light`, `Sanofi`)
-   Default sensor priority
-   Cloud masking preferences and cloud cover limits

## Project Structure

The project is structured as follows:

```
Flutter-Earth/
├── flutter_earth_pkg/
│   └── flutter_earth/      # Main Python package source
│       ├── __init__.py
│       ├── qml/            # QML source files for the UI (main.qml, views, etc.)
│       │   ├── main.qml
│       │   └── ...
│       ├── auth_setup.py   # Earth Engine authentication logic
│       ├── config.py       # Application configuration (AppConfig, themes)
│       ├── download_manager.py # Handles download orchestration
│       ├── download_worker.py  # Thread for actual download tasks
│       ├── earth_engine.py # Core Earth Engine interactions
│       ├── gui.py          # PySide6/QML application launcher and AppBackend bridge
│       ├── processing.py   # Image processing utilities, index calculations
│       ├── satellite_info.py # Satellite metadata
│       ├── themes.py       # Theme management
│       ├── types.py        # Custom data types and type hints
│       ├── utils.py        # General utility functions
│       └── ...             # Other backend modules (errors, progress_tracker, etc.)
├── main.py                 # Main application entry point script
├── EARTH_ENGINE_SETUP.md   # Detailed GEE service account setup instructions
├── flutter_earth_pkg/requirements.txt # Python dependencies for the package
├── README.md               # This file
└── ...                     # Other miscellaneous files (e.g. .gitignore)
```

(Note: Older `flutter_earth/` directory containing a Qt Widgets version might exist and is planned for cleanup.)

## Development

### Adding New Sensors

1.  Add the sensor's metadata to `SATELLITE_DETAILS` in `flutter_earth_pkg/flutter_earth/satellite_info.py`.
2.  Update `DATA_COLLECTIONS` and `SENSOR_TIMELINE` in the same file.
3.  If the new sensor requires unique processing or cloud masking, add corresponding functions to `flutter_earth_pkg/flutter_earth/processing.py` (see `CLOUD_MASKS` and `SENSOR_PROCESSORS` dictionaries) or `flutter_earth_pkg/flutter_earth/earth_engine.py`.
4.  Ensure the `AppBackend` in `gui.py` and relevant QML views (e.g., `DownloadView.qml` for sensor selection) can access the new sensor.

### Modifying the UI (QML)

The user interface is defined in the `.qml` files located in `flutter_earth_pkg/flutter_earth/qml/`.
-   Edit these files to change UI layout, appearance, and behavior.
-   The Python backend (`AppBackend` class in `flutter_earth_pkg/flutter_earth/gui.py`) is exposed to QML. Use its slots and properties to interact with Python logic, and connect to its signals for updates from Python.

## License

This project is licensed under the MIT License. (Assuming, please verify and add a LICENSE file).

## Support

For issues and questions:
1.  Ensure your Earth Engine service account is correctly set up as per `EARTH_ENGINE_SETUP.md` or that you have authenticated via other means.
2.  Check the application logs (e.g., `flutter_earth.log` in the root directory or console output).
3.  If you encounter a bug, please open an issue on the project's GitHub page.
