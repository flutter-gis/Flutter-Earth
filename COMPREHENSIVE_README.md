# Flutter Earth - Comprehensive Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Technical Details](#technical-details)
7. [Troubleshooting](#troubleshooting)
8. [Development](#development)
9. [API Reference](#api-reference)
10. [Contributing](#contributing)

## Overview

**Flutter Earth** is a sophisticated desktop application that provides comprehensive satellite imagery processing and Earth Engine data management capabilities. Built with a modern Electron frontend and Python backend, it offers an intuitive interface for downloading, processing, and analyzing satellite data from Google Earth Engine.

### Key Capabilities
- **Satellite Data Processing**: Download and process imagery from multiple satellite sources
- **Earth Engine Integration**: Direct access to Google Earth Engine's vast data catalog
- **Advanced Analytics**: Cloud masking, atmospheric corrections, and spectral indices
- **Data Management**: Comprehensive dataset browsing and organization
- **Offline Operation**: Full offline capability with local data storage
- **Modern UI**: Responsive, themeable interface with real-time progress tracking

## Architecture

### Frontend (Electron)
- **Technology Stack**: HTML5, CSS3, JavaScript (ES6+)
- **Framework**: Electron for cross-platform desktop deployment
- **UI Components**: Custom-built responsive components with CSS Grid/Flexbox
- **State Management**: Class-based architecture with event-driven updates
- **Theming**: Dynamic theme system with 50+ pre-built themes

### Backend (Python)
- **Core Engine**: Google Earth Engine API integration
- **Processing Pipeline**: Multi-threaded download and processing system
- **Data Management**: Local storage with JSON metadata and thumbnail caching
- **Authentication**: Secure credential management for Earth Engine access
- **Error Handling**: Comprehensive error tracking and recovery

### Communication
- **IPC**: Electron-Python inter-process communication
- **Real-time Updates**: Progress tracking and status synchronization
- **File System**: Shared access to local data directories
- **Logging**: Centralized logging system with rotation

## Features

### 1. Satellite Information System

#### Satellite Catalog
- **Comprehensive Database**: 50+ satellite systems with detailed specifications
- **Interactive Grid**: Visual satellite cards with thumbnails and metadata
- **Search & Filter**: Real-time search by name, type, resolution, or application
- **Detailed Views**: Grid and list view modes with customizable layouts

#### Satellite Details Panel
- **Technical Specifications**: Resolution, coverage, temporal frequency
- **Band Information**: Spectral bands with wavelength ranges and applications
- **Use Cases**: Pre-defined applications and analysis workflows
- **Code Generation**: Ready-to-use Earth Engine code snippets
- **Integration**: Direct integration with download system

#### Supported Satellites
- **Landsat Series**: Landsat 8, 9 (30m resolution, multispectral)
- **Sentinel Series**: Sentinel-1 (SAR), Sentinel-2 (10m optical)
- **MODIS**: Daily global coverage (250m-1km resolution)
- **Commercial**: PlanetScope, RapidEye, WorldView series
- **Specialized**: SMAP (soil moisture), GRACE (gravity), GPM (precipitation)

### 2. Web Crawler & Data Collection

#### Earth Engine Catalog Crawler
- **Automated Discovery**: Scans Earth Engine catalog for available datasets
- **Metadata Extraction**: Collects comprehensive dataset information
- **Thumbnail Generation**: Downloads and caches dataset previews
- **Progress Tracking**: Real-time progress with detailed status updates
- **Error Recovery**: Robust error handling with retry mechanisms

#### Data Processing Pipeline
- **Collection Analysis**: Identifies satellite sources and temporal coverage
- **Quality Assessment**: Evaluates data quality and cloud coverage
- **Categorization**: Organizes datasets by type, application, and region
- **Code Generation**: Creates Earth Engine code for each dataset
- **Local Storage**: Efficient JSON storage with compression

#### Crawler Features
- **Incremental Updates**: Only downloads new or changed datasets
- **Background Operation**: Non-blocking operation with progress indicators
- **Log Management**: Detailed logging with export capabilities
- **Data Validation**: Ensures data integrity and completeness
- **Performance Optimization**: Multi-threaded downloads with rate limiting

### 3. Dataset Viewer

#### Dataset Browser
- **Comprehensive Listing**: All discovered datasets with metadata
- **Advanced Search**: Search by name, description, tags, or publisher
- **Filtering System**: Filter by satellite, data type, resolution, or date range
- **Sorting Options**: Sort by relevance, date, size, or popularity
- **View Modes**: Grid and list views with customizable layouts

#### Dataset Details
- **Complete Metadata**: Full dataset information and specifications
- **Temporal Coverage**: Date ranges and update frequency
- **Spatial Coverage**: Geographic extent and resolution
- **Quality Metrics**: Cloud coverage, data quality indicators
- **Usage Examples**: Sample applications and use cases

#### Integration Features
- **Direct Download**: One-click integration with download system
- **Bookmarking**: Save datasets for later use
- **Sharing**: Export dataset information and code snippets
- **Code Generation**: Ready-to-use Earth Engine code
- **Batch Operations**: Process multiple datasets simultaneously

### 4. Download & Processing System

#### Area of Interest Selection
- **Interactive Map**: Draw polygons, rectangles, or import shapefiles
- **Coordinate Input**: Manual coordinate entry with validation
- **File Import**: Support for GeoJSON, KML, and Shapefile formats
- **Predefined Areas**: Built-in administrative boundaries and regions
- **Area Validation**: Automatic validation of selected areas

#### Satellite Selection
- **Multi-Source Support**: Choose from available satellite systems
- **Band Selection**: Select specific spectral bands for download
- **Temporal Range**: Define start and end dates for data collection
- **Quality Filters**: Set cloud coverage and data quality thresholds
- **Resolution Options**: Choose output resolution and processing level

#### Processing Options
- **Cloud Masking**: Advanced cloud detection and masking algorithms
- **Atmospheric Correction**: Radiometric and atmospheric corrections
- **Spectral Indices**: Automatic calculation of NDVI, EVI, NDWI, etc.
- **Tiling System**: Automatic tiling for large area processing
- **Format Options**: Export to GeoTIFF, JPEG, or PNG formats

#### Download Management
- **Progress Tracking**: Real-time progress with detailed status
- **Queue Management**: Multiple download queue with priority settings
- **Pause/Resume**: Ability to pause and resume downloads
- **Error Recovery**: Automatic retry with exponential backoff
- **Resource Management**: Memory and CPU usage optimization

### 5. Authentication & Security

#### Earth Engine Authentication
- **Service Account**: Secure service account key management
- **Project Configuration**: Google Cloud project setup and validation
- **Credential Storage**: Encrypted local storage of credentials
- **Access Validation**: Automatic validation of Earth Engine access
- **Error Handling**: Comprehensive error messages and recovery

#### Security Features
- **Local Storage**: All data stored locally with no cloud dependencies
- **Credential Protection**: Encrypted storage of sensitive information
- **Access Control**: User-based access control and permissions
- **Audit Logging**: Complete audit trail of all operations
- **Data Privacy**: No data transmission to external servers

### 6. User Interface

#### Modern Design
- **Responsive Layout**: Adapts to different screen sizes and resolutions
- **Theme System**: 50+ pre-built themes with custom theme support
- **Dark/Light Modes**: Automatic and manual theme switching
- **Accessibility**: High contrast modes and keyboard navigation
- **Internationalization**: Multi-language support framework

#### Navigation System
- **Tabbed Interface**: Organized sections for different functions
- **Breadcrumb Navigation**: Clear navigation hierarchy
- **Search Functionality**: Global search across all features
- **Keyboard Shortcuts**: Power user shortcuts for common actions
- **Context Menus**: Right-click context menus for quick actions

#### Progress & Status
- **Real-time Updates**: Live progress indicators for all operations
- **Status Notifications**: Toast notifications for important events
- **Error Reporting**: Detailed error messages with recovery suggestions
- **Log Viewer**: Integrated log viewer with filtering and search
- **Performance Metrics**: System resource usage and performance indicators

### 7. Settings & Configuration

#### Application Settings
- **Output Directory**: Configurable default download location
- **Processing Options**: Default processing parameters and algorithms
- **Performance Settings**: Thread count, memory limits, and timeouts
- **Interface Preferences**: Theme, font size, and layout options
- **Notification Settings**: Customizable notification preferences

#### Advanced Configuration
- **API Settings**: Earth Engine API configuration and limits
- **Cache Management**: Local cache size and cleanup policies
- **Logging Configuration**: Log levels and rotation settings
- **Security Settings**: Authentication and encryption options
- **Backup Settings**: Automatic backup and recovery options

## Installation

### Prerequisites
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Python 3.8 or higher
- **Node.js**: Node.js 16 or higher (for Electron)
- **Google Earth Engine**: Active Earth Engine account with API access
- **Storage**: Minimum 10GB free space for data and cache

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/flutter-earth.git
cd flutter-earth
```

#### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### 4. Earth Engine Authentication
```bash
# Install Earth Engine Python API
pip install earthengine-api

# Authenticate with Earth Engine
earthengine authenticate
```

#### 5. Build Application
```bash
# Build Electron application
npm run build

# Or run in development mode
npm start
```

### Quick Start Scripts
- **Windows**: `start.bat` or `start.ps1`
- **macOS/Linux**: `./start.sh`
- **Development**: `npm run dev`

## Usage

### Getting Started

#### 1. Launch Application
```bash
# Windows
start.bat

# macOS/Linux
./start.sh

# Development
npm start
```

#### 2. Initial Setup
- Configure Earth Engine authentication
- Set default output directory
- Choose preferred theme and interface options
- Run initial data collection (optional)

#### 3. Basic Workflow
1. **Select Area**: Use interactive map or import coordinates
2. **Choose Satellite**: Select satellite system and bands
3. **Set Parameters**: Configure processing options and quality filters
4. **Start Download**: Begin data collection and processing
5. **Monitor Progress**: Track progress and handle any issues
6. **Access Results**: Find processed data in output directory

### Advanced Usage

#### Batch Processing
```python
# Example batch processing script
from flutter_earth import DownloadManager, ConfigManager

config = ConfigManager()
manager = DownloadManager(config)

# Process multiple areas
areas = [
    {"name": "Area1", "coordinates": [...]},
    {"name": "Area2", "coordinates": [...]}
]

for area in areas:
    manager.process_area(area)
```

#### Custom Processing Pipeline
```python
# Custom processing with advanced options
from flutter_earth import EarthEngineProcessor

processor = EarthEngineProcessor()

# Custom processing parameters
params = {
    "cloud_mask": True,
    "atmospheric_correction": "DOS",
    "spectral_indices": ["NDVI", "EVI", "NDWI"],
    "output_resolution": 10,
    "tile_size": 512
}

result = processor.process_dataset(dataset_id, params)
```

## Technical Details

### File Structure
```
flutter-earth/
├── frontend/                 # Electron frontend
│   ├── flutter_earth_enhanced_v2.html
│   ├── flutter_earth_enhanced_v2.js
│   ├── flutter_earth_enhanced_v2.css
│   ├── tabs.js              # Tab management system
│   └── package.json
├── backend/                  # Python backend
│   ├── earth_engine_processor.py
│   ├── gee_catalog_crawler_enhanced_v2.py
│   └── crawler_data/        # Collected data
├── flutter_earth_pkg/        # Core Python package
│   ├── flutter_earth/
│   │   ├── auth_setup.py
│   │   ├── config.py
│   │   ├── download_manager.py
│   │   ├── earth_engine.py
│   │   └── utils.py
│   └── setup.py
├── main.py                   # Application entry point
├── startup_coordinator.py    # Startup management
└── requirements.txt
```

### Data Flow
1. **User Input**: Interface captures user selections and parameters
2. **Validation**: Input validation and parameter checking
3. **Processing**: Python backend processes requests
4. **Earth Engine**: API calls to Google Earth Engine
5. **Local Storage**: Results stored in local file system
6. **UI Updates**: Frontend updated with results and progress
7. **User Feedback**: Notifications and status updates

### Performance Optimization
- **Multi-threading**: Parallel processing for downloads and analysis
- **Caching**: Local cache for frequently accessed data
- **Compression**: Data compression for storage efficiency
- **Memory Management**: Efficient memory usage and cleanup
- **Progress Tracking**: Real-time progress updates without blocking

### Error Handling
- **Graceful Degradation**: Application continues with reduced functionality
- **Error Recovery**: Automatic retry mechanisms for transient failures
- **User Feedback**: Clear error messages with recovery suggestions
- **Logging**: Comprehensive logging for debugging and support
- **Validation**: Input validation to prevent common errors

## Troubleshooting

### Common Issues

#### Authentication Problems
**Problem**: Earth Engine authentication fails
**Solution**: 
1. Verify service account key is valid
2. Check Google Cloud project permissions
3. Ensure Earth Engine API is enabled
4. Run `earthengine authenticate` again

#### Download Failures
**Problem**: Downloads fail or timeout
**Solution**:
1. Check internet connection
2. Verify Earth Engine quota limits
3. Reduce area size or temporal range
4. Check available disk space

#### Performance Issues
**Problem**: Application is slow or unresponsive
**Solution**:
1. Reduce concurrent download threads
2. Clear cache and temporary files
3. Check system resources (CPU, memory)
4. Update to latest version

#### UI Issues
**Problem**: Interface elements not working correctly
**Solution**:
1. Clear browser cache and cookies
2. Check for JavaScript errors in console
3. Try different theme or reset settings
4. Reinstall application

### Debug Mode
Enable debug mode for detailed logging:
```bash
# Set debug environment variable
export FLUTTER_EARTH_DEBUG=1

# Or modify config file
echo '{"debug": true}' > config.json
```

### Log Files
Log files are stored in the `logs/` directory:
- `flutter_earth_YYYYMMDD_HHMMSS.log`: Main application log
- `crawler_YYYYMMDD_HHMMSS.log`: Web crawler log
- `download_YYYYMMDD_HHMMSS.log`: Download operations log

## Development

### Development Environment Setup
```bash
# Clone repository
git clone https://github.com/your-username/flutter-earth.git
cd flutter-earth

# Install development dependencies
pip install -r requirements-dev.txt
npm install --dev

# Setup pre-commit hooks
pre-commit install
```

### Code Structure
- **Frontend**: Modular JavaScript with ES6+ features
- **Backend**: Object-oriented Python with type hints
- **Testing**: Unit tests for both frontend and backend
- **Documentation**: Comprehensive inline documentation

### Contributing Guidelines
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes with tests
4. Run test suite: `npm test && python -m pytest`
5. Submit pull request with description

### Testing
```bash
# Run all tests
npm test
python -m pytest

# Run specific test suites
npm run test:unit
npm run test:integration
python -m pytest tests/unit/
python -m pytest tests/integration/
```

## API Reference

### Frontend API

#### Core Application Class
```javascript
class FlutterEarthEnhancedV2 {
    constructor()
    switchView(viewName)
    switchSubtab(subtabName)
    startDownload()
    loadSatellites()
    startCrawler()
}
```

#### Event System
```javascript
// Tab switching
app.switchView('satelliteInfo')
app.switchSubtab('crawler')

// Download operations
app.startDownload()
app.validateParameters()

// Data management
app.loadSatellites()
app.loadDatasets()
```

### Backend API

#### Core Classes
```python
class AuthManager:
    def authenticate(self, key_path: str, project_id: str) -> bool
    def get_auth_info(self) -> dict
    def has_credentials(self) -> bool

class DownloadManager:
    def process_area(self, area: dict, params: dict) -> bool
    def get_progress(self) -> dict
    def cancel_download(self, download_id: str) -> bool

class EarthEngineProcessor:
    def process_dataset(self, dataset_id: str, params: dict) -> dict
    def get_collections(self) -> list
    def validate_parameters(self, params: dict) -> bool
```

#### Configuration
```python
class ConfigManager:
    def get(self, key: str) -> Any
    def set(self, key: str, value: Any) -> None
    def save(self) -> None
    def load(self) -> None
```

### IPC Communication
```javascript
// Frontend to Backend
window.electronAPI.getCrawlerStatus()
window.electronAPI.startDownload(params)
window.electronAPI.getDatasets()

// Backend to Frontend
ipcMain.handle('get-crawler-status', async () => {})
ipcMain.handle('start-download', async (event, params) => {})
ipcMain.handle('get-datasets', async () => {})
```

## Contributing

### Development Workflow
1. **Issue Reporting**: Use GitHub issues for bug reports and feature requests
2. **Code Review**: All changes require code review and approval
3. **Testing**: Ensure all tests pass before submitting
4. **Documentation**: Update documentation for new features
5. **Release Process**: Follow semantic versioning for releases

### Code Standards
- **JavaScript**: ESLint configuration with Prettier formatting
- **Python**: Black formatting with flake8 linting
- **Documentation**: JSDoc for JavaScript, docstrings for Python
- **Testing**: Minimum 80% code coverage required

### Release Process
1. Update version numbers in package.json and setup.py
2. Update CHANGELOG.md with new features and fixes
3. Create release tag: `git tag v1.2.3`
4. Build and test release packages
5. Publish to GitHub releases

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- **Documentation**: [Wiki](https://github.com/your-username/flutter-earth/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-username/flutter-earth/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/flutter-earth/discussions)
- **Email**: support@flutter-earth.com

## Acknowledgments

- Google Earth Engine team for the powerful API
- Electron team for the desktop framework
- Open source community for various dependencies
- Contributors and beta testers for feedback and improvements

---

*Last updated: January 2025*
*Version: 2.0.0* 