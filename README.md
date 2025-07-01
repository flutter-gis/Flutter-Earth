# 🌍 Flutter Earth

**A powerful desktop application for Earth Engine data access, satellite information, and geospatial analysis built with Electron and Python.**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/flutter-earth)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/flutter-earth)

## ✨ Features

### 🛰️ **Satellite Information System**
- **Comprehensive Database**: Access detailed information about 100+ satellites and sensors
- **Real-time Crawling**: Web crawler to collect latest satellite data from Google Earth Engine
- **Smart Search**: Filter satellites by type (Optical, Radar, Thermal, Multispectral)
- **Code Generation**: Auto-generate Earth Engine code snippets for each satellite
- **Visual Thumbnails**: Satellite imagery and dataset previews

### 📥 **Advanced Download Manager**
- **Multi-Sensor Support**: Landsat, Sentinel, MODIS, and more
- **Flexible AOI**: Support for coordinates, GeoJSON, and interactive map selection
- **Cloud Processing**: Built-in cloud masking and filtering
- **High Resolution**: Configurable resolution settings and tiling options
- **Progress Tracking**: Real-time progress monitoring with speed graphs

### 🌱 **Index Analysis Tools**
- **Vegetation Indices**: NDVI, NDWI, EVI calculations
- **Multi-band Analysis**: Support for various spectral indices
- **Batch Processing**: Process multiple raster files simultaneously
- **Visualization**: Interactive charts and analysis results

### 🌐 **Vector Data Download**
- **Multiple Sources**: Access to various vector datasets
- **Format Support**: GeoJSON, Shapefile, KML export options
- **Area Selection**: Interactive area of interest selection
- **Metadata Extraction**: Comprehensive dataset information

### 📊 **Data Viewer**
- **Raster Support**: View and analyze satellite imagery
- **Vector Support**: Display and interact with vector data
- **Metadata Display**: Detailed file information and properties
- **Export Options**: Multiple format export capabilities

### 🎨 **Beautiful Theming System**
- **Multiple Themes**: 20+ carefully crafted themes including:
  - 🌍 **Basic**: Clean, professional themes
  - 🦄 **My Little Pony**: Colorful, playful themes
  - ⛏️ **Minecraft**: Blocky, pixelated themes
  - 🏳️‍🌈 **Queer Pride**: Pride flag-inspired themes
  - 🤝 **Unity Pride**: Community-focused themes
- **Animated Backgrounds**: Dynamic theme effects and animations
- **Customizable**: Theme options and character catchphrases
- **Smooth Transitions**: Beautiful theme switching animations

### ⚙️ **Professional Interface**
- **Modern UI**: Clean, intuitive interface design
- **Responsive Layout**: Adapts to different screen sizes
- **Keyboard Shortcuts**: Power user shortcuts for efficiency
- **Progress Monitoring**: Real-time status updates and logging
- **Offline Capable**: Works without internet connection

## 🚀 Quick Start

### Prerequisites
- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **Google Earth Engine Account** (optional, for full functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/flutter-earth.git
   cd flutter-earth
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   cd frontend
   npm install
   
   # Install Python dependencies
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   # From the project root
   npm start
   # or
   cd frontend && npm start
   ```

### First Time Setup

1. **Launch Flutter Earth**
2. **Navigate to Satellite Info** (🛰️ tab)
3. **Click "Start Data Collection"** to populate satellite database
4. **Wait 2-5 minutes** for initial data collection
5. **Start exploring!** 🎉

## 📖 Usage Guide

### Satellite Information
- **Browse Satellites**: View comprehensive satellite database
- **Search & Filter**: Find specific satellites by name, type, or application
- **Get Code Snippets**: Copy ready-to-use Earth Engine code
- **View Details**: Access resolution, bands, and application information

### Data Download
1. **Select Area**: Use coordinates, GeoJSON, or map selector
2. **Choose Dates**: Set start and end dates for data collection
3. **Pick Sensor**: Select from available satellites and sensors
4. **Configure Settings**: Adjust cloud cover, resolution, and processing options
5. **Start Download**: Monitor progress with real-time updates

### Index Analysis
1. **Add Raster Files**: Select satellite imagery for analysis
2. **Choose Indices**: Pick from NDVI, NDWI, EVI, and more
3. **Set Parameters**: Configure analysis settings
4. **Run Analysis**: Process and visualize results

### Theme Customization
1. **Open Settings** (⚙️ tab)
2. **Browse Themes**: Explore different theme categories
3. **Customize Options**: Adjust animations and effects
4. **Apply Changes**: See immediate visual updates

## 🏗️ Architecture

```
Flutter Earth/
├── frontend/                 # Electron application
│   ├── flutter_earth.html   # Main interface
│   ├── flutter_earth.js     # Application logic
│   ├── flutter_earth.css    # Styling and themes
│   └── package.json         # Node.js dependencies
├── backend/                  # Python backend
│   ├── earth_engine.py      # Earth Engine integration
│   ├── download_manager.py  # Download processing
│   ├── crawler.py           # Web crawler
│   └── requirements.txt     # Python dependencies
├── assets/                   # Static assets
├── docs/                     # Documentation
└── scripts/                  # Utility scripts
```

### Technology Stack
- **Frontend**: Electron, HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.8+, Google Earth Engine API
- **Data Processing**: NumPy, Pandas, GDAL
- **UI Framework**: Custom CSS with CSS Variables
- **Build System**: npm, pip

## 🔧 Configuration

### Earth Engine Setup
1. **Create Account**: Sign up at [earthengine.google.com](https://earthengine.google.com)
2. **Enable API**: Enable Earth Engine API in Google Cloud Console
3. **Download Credentials**: Download service account key
4. **Configure**: Place credentials in `backend/` directory

### Custom Themes
Create custom themes by adding to `frontend/themes.json`:
```json
{
  "name": "my_theme",
  "display_name": "My Custom Theme",
  "category": "custom",
  "background": "#1a1a1a",
  "primary": "#4CAF50",
  "text": "#ffffff",
  "splashEffect": "confetti"
}
```

## 📊 Performance

- **Fast Startup**: Optimized loading times
- **Efficient Processing**: Multi-threaded data processing
- **Memory Management**: Smart caching and cleanup
- **Offline Support**: Core functionality without internet

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Install development dependencies
npm install --dev

# Run in development mode
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 📝 Changelog

### Version 1.0.0
- ✨ Initial release
- 🛰️ Satellite information system
- 📥 Advanced download manager
- 🌱 Index analysis tools
- 🎨 Beautiful theming system
- ⚙️ Professional interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Earth Engine** for providing satellite data access
- **Electron** for the desktop application framework
- **Open Source Community** for various libraries and tools
- **Contributors** who helped make this project possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/flutter-earth/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/flutter-earth/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/flutter-earth/wiki)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/flutter-earth&type=Date)](https://star-history.com/#yourusername/flutter-earth&Date)

---

**Made with ❤️ by the Flutter Earth Team**

*Empowering geospatial analysis with beautiful, accessible tools.*
