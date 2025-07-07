# Flutter Earth

Flutter Earth is an open-source platform for exploring, downloading, and analyzing satellite data. It provides a user-friendly interface for interacting with Google Earth Engine, managing satellite catalogs, and downloading imagery with advanced options.

## Features
- Browse and search satellite catalogs
- Download satellite imagery with advanced options
- Visual map-based area selection
- Theming and UI customization
- Authentication for Google Earth Engine
- Real-time progress and logs

## Project Structure
- `backend/` - Python backend for crawling, processing, and downloading
- `frontend/` - Electron/JavaScript frontend for the user interface
- `flutter_earth_pkg/` - Core Python package
- `docs/` and `docs_md/` - Documentation
- `scripts/` - Batch scripts and utilities
- `tests/` - Test files

## Getting Started

### 1. Install Dependencies

```
pip install -r requirements.txt
cd frontend
npm install
```

### 2. Run the Application

```
./run_desktop.bat
# or
cd frontend && npm start
```

## Usage
- Use the tabs to navigate between Map, Download, Satellite Info, and other features.
- Authenticate with your Google Earth Engine credentials in the Settings tab.
- Use the Download tab to select an area, choose a satellite, and download imagery.
- View logs and progress in real time.

## Documentation
See the `docs/` and `docs_md/` folders for detailed guides and technical documentation.

## Contributing
Pull requests and issues are welcome. See the documentation for guidelines.

## License
MIT License 