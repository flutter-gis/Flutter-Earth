# Flutter Earth - QML Edition

<<<<<<< HEAD
A powerful, user-friendly tool for downloading and processing satellite imagery using the Google Earth Engine, now with a modern QML-based interface.

## Features

-   **Modern QML Interface**: A sleek and responsive user interface built with Qt for a better user experience.
-   **Modular Backend**: The application is now structured as a professional Python package for better maintainability and scalability.
-   **Theming Support**: Switch between 'Dark', 'Light', and 'Sanofi' themes.
-   **Advanced Downloading**: Download satellite imagery from multiple sensors like Landsat and Sentinel-2.
-   **On-the-fly Processing**: Includes cloud masking and other pre-processing capabilities.
-   **Robust Configuration**: A clear, class-based configuration system manages all settings.
-   **Comprehensive Satellite Info**: Browse detailed information about available satellites.

## Prerequisites

-   Python 3.8 or higher
-   A Google Earth Engine account with API access enabled.
-   Required Python packages (see `flutter_earth_pkg/requirements.txt`).

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Flutter-Earth
```

### 2. Install required packages

The dependencies are now managed within the `flutter_earth_pkg`.

```bash
pip install -r flutter_earth_pkg/requirements.txt
```

### 3. Set up Earth Engine Authentication

The application now primarily uses a **service account** for authentication with Google Earth Engine. You will need to:
1.  **Create a Google Cloud Project** and enable the Earth Engine API.
2.  **Create a Service Account** within your project and grant it the "Earth Engine Resource Viewer" or similar permissions.
3.  **Download the JSON key file** for your service account.

For detailed, step-by-step instructions, please refer to `EARTH_ENGINE_SETUP.md`.
=======
A modern, powerful tool for downloading and processing satellite imagery from Google Earth Engine with a beautiful Qt6-based interface.

## Features

- 🌍 **Interactive Map Selection**: Draw polygons and rectangles directly on the map
- 🛰️ **Multi-Satellite Support**: Access to Landsat, Sentinel, and other satellite collections
- 📊 **Advanced Processing**: NDVI, EVI, and other vegetation indices
- 🎨 **Modern Qt6 Interface**: Beautiful, responsive user interface
- 📁 **Multiple Output Formats**: GeoTIFF, JPEG, PNG with metadata
- 🔧 **Batch Processing**: Process multiple areas simultaneously
- 📈 **Real-time Progress**: Live progress tracking and status updates
- 🎯 **Precision Control**: Fine-tuned sensor selection and processing parameters

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Earth Engine account and authentication
- Qt6 runtime (included with PyQt6)

### Install Flutter Earth

```bash
# Clone the repository
git clone https://github.com/flutter-earth/flutter-earth.git
cd flutter-earth

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Earth Engine Setup

1. **Create a Google Earth Engine account**:
   - Visit [Earth Engine Signup](https://signup.earthengine.google.com/)
   - Sign up with your Google account

2. **Authenticate with Earth Engine**:
   ```bash
   # Run the authentication setup
   python -c "import ee; ee.Initialize(); print('Earth Engine ready!')"
   ```

3. **Verify installation**:
   ```bash
   # Test Earth Engine connection
   python -c "import ee; ee.Initialize(); print('Earth Engine ready!')"
   ```

## Quick Start

### Launch the Application

```bash
# Start Flutter Earth
python main.py
```

### Basic Usage

1. **Select Area of Interest**:
   - Use the map interface to draw a polygon
   - Or enter coordinates manually
   - Or import a shapefile

2. **Choose Time Period**:
   - Set start and end dates
   - Use predefined periods (last month, last year, etc.)

3. **Select Satellites**:
   - Choose from available satellite collections
   - Set cloud cover thresholds
   - Configure sensor priorities

4. **Configure Processing**:
   - Select output format and resolution
   - Choose vegetation indices
   - Set tiling options

5. **Start Download**:
   - Review settings and start processing
   - Monitor progress in real-time
   - Download results when complete

## Advanced Features

### Vegetation Indices

- **NDVI** (Normalized Difference Vegetation Index)
- **EVI** (Enhanced Vegetation Index)
- **SAVI** (Soil-Adjusted Vegetation Index)
- **NDWI** (Normalized Difference Water Index)

### Output Formats
>>>>>>> be259fa1a1f5c8571d423145995d33dfec88b40a

- **GeoTIFF**: High-quality raster with geospatial metadata
- **JPEG/PNG**: Quick preview images
- **Shapefile**: Vector boundaries and metadata
- **CSV**: Tabular data and statistics

<<<<<<< HEAD
You can run the application using the main script or the provided batch/powershell files.

### Using the Python main script:
```bash
python main.py
```

### Using the run scripts (Windows):
```bash
# Using PowerShell
./run.ps1

# Or using Command Prompt
run.bat
```
Upon first launch, you may be prompted to configure your Earth Engine credentials if they are not already set up.

## Configuration

The application uses a configuration file (`flutter_earth_config.json`) that is automatically created in the root directory on first run. You can modify settings such as:

-   Default output directory
-   UI Theme (`Default (Dark)`, `Light`, `Sanofi`)
-   Tile size for downloads
-   Maximum cloud cover percentage
-   Default sensor priority

## Project Structure

The project has been refactored into a more robust and modular structure:

```
Flutter-Earth/
├── flutter_earth_pkg/
│   └── flutter_earth/      # Main Python package source
│       ├── __init__.py
│       ├── qml/            # QML source files for the UI
│       │   ├── main.qml
│       │   └── ...
│       ├── config.py       # Application configuration and themes
│       ├── gui.py          # PyQt/QML application launcher and backend bridge
│       ├── earth_engine.py # Core Earth Engine interactions
│       ├── processing.py   # Data processing logic
│       └── ...             # Other backend modules
├── main.py                 # Main application entry point
├── run.bat                 # Windows batch script to run the app
├── run.ps1                 # Windows PowerShell script to run the app
├── EARTH_ENGINE_SETUP.md   # Detailed GEE setup instructions
├── requirements.txt        # Top-level dependencies (if any)
└── README.md               # This file
```

## Development

### Adding New Sensors

1.  Add the sensor's metadata to the `SATELLITE_DETAILS` dictionary in `flutter_earth_pkg/flutter_earth/config.py`.
2.  If the new sensor requires unique processing steps, implement them in `flutter_earth_pkg/flutter_earth/processing.py`.
3.  The satellite information view will automatically pick up the new sensor data.

### Modifying the UI

The user interface is defined in the `.qml` files located in `flutter_earth_pkg/flutter_earth/qml/`. You can edit these files to change the UI layout and behavior. The Python backend is exposed to QML via the `AppBackend` class in `flutter_earth_pkg/flutter_earth/gui.py`.
=======
### Batch Processing

- Process multiple areas simultaneously
- Queue management and priority control
- Resume interrupted downloads
- Export processing logs

## Configuration

Flutter Earth uses a configuration file for persistent settings. The configuration is automatically created on first run.

## Development

### Project Structure

```
flutter_earth/
├── main.py              # Main entry point
├── flutter_earth/       # Core package
│   ├── __init__.py
│   ├── types.py         # Data types and models
│   ├── config.py        # Configuration management
│   ├── earth_engine.py  # Earth Engine operations
│   ├── gui.py           # Main GUI interface
│   ├── gui_components.py # GUI components
│   ├── download_manager.py # Download management
│   ├── progress_tracker.py # Progress tracking
│   ├── themes.py        # UI themes
│   ├── utils.py         # Utility functions
│   └── errors.py        # Error handling
├── requirements.txt     # Dependencies
├── setup.py            # Package setup
└── README.md           # This file
```

### Running Tests

```bash
# Run basic tests
python -m pytest tests/
```

### Code Quality

```bash
# Format code
black .
>>>>>>> be259fa1a1f5c8571d423145995d33dfec88b40a

# Lint code
flake8 .

<<<<<<< HEAD
This project is licensed under the MIT License.

## Support

For issues and questions:
1.  Ensure your Earth Engine service account is correctly set up as per `EARTH_ENGINE_SETUP.md`.
2.  Check the application logs stored in the `logs/` directory.
3.  If you encounter a bug, please open an issue on the project's GitHub page. 
=======
# Type checking
mypy .
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://flutter-earth.readthedocs.io](https://flutter-earth.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/flutter-earth/flutter-earth/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flutter-earth/flutter-earth/discussions)

## Acknowledgments

- Google Earth Engine team for the powerful API
- Qt team for the excellent Qt6 framework
- Open source community for the amazing libraries

---

**Flutter Earth** - Making satellite imagery accessible to everyone 🌍✨ 
>>>>>>> be259fa1a1f5c8571d423145995d33dfec88b40a
