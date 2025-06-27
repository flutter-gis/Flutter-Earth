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

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of recent changes, bug fixes, and new features. The changelog is automatically updated with each major release and important fix.

### Recent Major Changes
- Scroll wheel now works in the Download page (QML layout fix)
- Authentication dialog now uses the key file path and prevents duplicate key files
- Status bar color now updates for online/offline status
- Download page layout and usability improved
- Error handling and user feedback improved throughout the app

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

This project is licensed under the MIT License.

## Support

For issues and questions:
1.  Ensure your Earth Engine service account is correctly set up as per `EARTH_ENGINE_SETUP.md`.
2.  Check the application logs stored in the `logs/` directory.
3.  If you encounter a bug, please open an issue on the project's GitHub page.

---

**Flutter Earth** - Making satellite imagery accessible to everyone 🌍✨

# Flutter Earth Desktop (Electron + Python)

A modern desktop application for downloading and processing satellite imagery using Google Earth Engine.

## Architecture

- **Frontend**: Electron app with HTML/CSS/JS interface (converted from QML)
- **Backend**: Python scripts called directly by Electron (no HTTP server)
- **Communication**: Electron ↔ Python via child processes (stdin/stdout)
- **Offline**: Fully offline except for actual satellite data downloads

## Requirements

- **Python 3.8+** with required packages (see requirements.txt)
- **Node.js 18+** and npm
- **Google Earth Engine** account and credentials

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies** (when you first run the app):
   ```bash
   cd frontend
   npm install
   ```

## How to Run

### Option 1: Using the Launcher (Recommended)
```bash
run_desktop.bat
```

### Option 2: Manual Start
```bash
cd frontend
npm start
```

## Features

### Converted from QML to HTML/JS
- ✅ **Sidebar Navigation** - All navigation items with icons and labels
- ✅ **Download Manager** - Complete download form with validation
- ✅ **Settings View** - Theme selection and configuration
- ✅ **Progress Tracking** - Real-time download progress
- ✅ **Authentication** - Google Earth Engine credentials setup
- ✅ **Help System** - Documentation and help information
- ✅ **Responsive Design** - Works on different screen sizes

### Python Backend Integration
- **Earth Engine Initialization** - Automatic setup and authentication
- **Download Management** - Start, monitor, and cancel downloads
- **Progress Tracking** - Real-time progress updates
- **Error Handling** - Comprehensive error reporting

## Project Structure

```
Flutter-Earth/
├── frontend/                    # Electron app
│   ├── flutter_earth.html      # Main HTML interface
│   ├── flutter_earth.css       # Styling and themes
│   ├── flutter_earth.js        # Frontend logic
│   ├── main_electron.js        # Electron main process
│   ├── preload.js              # IPC bridge
│   └── package.json            # Node.js dependencies
├── backend/
│   └── earth_engine_processor.py  # Python backend script
├── flutter_earth_pkg/          # Original Python package
├── logs/                       # Application logs
├── run_desktop.bat            # Launcher script
└── requirements.txt           # Python dependencies
```

## Development

### Frontend (HTML/CSS/JS)
- Edit `frontend/flutter_earth.html` for UI structure
- Edit `frontend/flutter_earth.css` for styling
- Edit `frontend/flutter_earth.js` for functionality

### Backend (Python)
- Edit `backend/earth_engine_processor.py` for Earth Engine operations
- Add new commands by extending the `main()` function

### Adding New Features
1. **Frontend**: Add UI elements in HTML, style in CSS, add logic in JS
2. **Backend**: Add new command in `earth_engine_processor.py`
3. **Communication**: Add IPC handler in `main_electron.js` and expose in `preload.js`

## Troubleshooting

### Common Issues

1. **Electron won't start**
   - Check Node.js installation: `node --version`
   - Run `npm install` in frontend directory
   - Check for missing dependencies

2. **Python communication fails**
   - Verify Python installation: `python --version`
   - Install requirements: `pip install -r requirements.txt`
   - Check Python path in `main_electron.js`

3. **Earth Engine authentication**
   - Ensure you have a Google Earth Engine account
   - Download service account key file
   - Use the authentication dialog in the app

### Debug Mode

Enable debug logging by checking the browser console (F12) in the Electron app.

## License

See the repository for license details.
