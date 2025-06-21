# Flutter Earth

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

- **GeoTIFF**: High-quality raster with geospatial metadata
- **JPEG/PNG**: Quick preview images
- **Shapefile**: Vector boundaries and metadata
- **CSV**: Tabular data and statistics

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

# Lint code
flake8 .

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