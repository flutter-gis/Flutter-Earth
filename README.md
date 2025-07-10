# 🌍 Flutter Earth - Dear PyGui v2.0 🚀

> **A modern, beautiful, and powerful Earth observation platform built with Dear PyGui.**

---

## ✨ Overview

Flutter Earth v2.0 is a next-generation desktop application for exploring, downloading, and analyzing satellite data. It combines a powerful Python backend with a modern Dear PyGui interface and seamless Google Earth Engine integration—all in a single, easy-to-use package.

- **Modern UI**: Beautiful Dear PyGui interface with dark/light themes
- **Advanced Web Crawler**: Extracts the latest satellite datasets from Google Earth Engine
- **Powerful Download Manager**: Customizable, reliable, and fast
- **Real-Time Progress & Logs**: See everything as it happens
- **Secure Authentication**: Easy GEE credential management
- **Open Source & Extensible**: Built for the community

---

## 🏗️ Architecture

```mermaid
graph TD;
  User-->|Dear PyGui UI|GUI[Dear PyGui Interface]
  GUI-->|Python Backend|Backend[Backend (Python)]
  Backend-->|Earth Engine API|GEE[Google Earth Engine]
  Backend-->|Web Crawler|Crawler[Enhanced GEE Catalog Crawler]
  Backend-->|Local Storage|Data[Local Data/Thumbnails/Logs]
```

- **Frontend**: Dear PyGui with modern themes and responsive design
- **Backend**: Python 3.8+, async, type-safe, robust error handling
- **Web Crawler**: Async, multi-threaded, extracts and updates satellite catalog
- **Data Storage**: Local JSON, thumbnails, logs, and user settings

---

## 🚦 Quick Start

### 🛠️ Prerequisites
- Python 3.8+
- (Optional) Google Earth Engine account for full features

### ⚡ Installation & Startup

1. **Clone the repo**
   ```bash
   git clone <repository-url>
   cd Flutter-Earth
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app**
   ```bash
   # Windows
   start.bat
   # Or manually:
   python main.py
   ```

**Note:** The application uses Dear PyGui for the interface, so no additional GUI frameworks are required.

---

## 🎨 Features & UI

- 🌗 **Theme Switcher**: Toggle between Dark and Light themes
- 🎉 **Modern Interface**: Clean, responsive design with tabs and panels
- ⚡ **Real-time Updates**: Live progress tracking and status updates
- 🖼️ **Data Visualization**: Built-in charts and graphs with PyGraph
- 📊 **Dashboard**: Overview of system status and statistics

---

## 🛰️ Satellite Info & Web Crawler

### 🛰️ Satellite Info Tab
- Browse all available satellites, sensors, and datasets
- Filter, search, and view detailed info for each satellite
- See real-time stats: total satellites, datasets, publishers, last update
- Click any satellite for details, code snippets, and download options

### 🕷️ Web Crawler Integration
- **Fully integrated into the application**
- Start/stop the crawler, see live progress, and view logs
- Progress bar, step tracker, and ETA
- Dataset viewer: search, filter, and explore all extracted datasets
- Download thumbnails, metadata, and code snippets
- All crawler actions and results are visible in the interface

---

## 🧭 Usage Guide

### 1️⃣ **Authenticate (Optional, for GEE features)**
- Go to Settings tab and upload your Google Cloud service account JSON key and project ID
- Test the connection to ensure credentials work
- You can continue in offline mode for basic features

### 2️⃣ **Explore the Interface**
- Use the tab bar to switch between Dashboard, Satellites, Datasets, Download, Analysis, and Settings
- Each tab provides specific functionality and tools

### 3️⃣ **Satellite Info & Crawler**
- Go to the Satellites tab
- Click "Start Crawler" to run the data collection
- Watch real-time progress and view extracted datasets
- Filter/search datasets and view details

### 4️⃣ **Download Data**
- Go to the Download tab
- Select satellite, date range, region, and output options
- Start download and monitor progress in real time

### 5️⃣ **Data Analysis**
- Go to the Analysis tab
- Select input file and analysis type
- Run analysis and view results

### 6️⃣ **Settings & Customization**
- Change themes and application settings
- Manage authentication credentials
- Configure output directories and preferences

---

## 🛠️ Development & Contribution

### 🐍 Backend (Python)
- Main application logic in `main.py`
- Backend processing in `backend/earth_engine_processor_enhanced.py`
- Web crawler in `backend/gee_catalog_crawler_enhanced_v2.py`
- Uses async, dataclasses, and robust error handling
- Logs in `logs/` and progress in `backend/crawler_data/`

### 🖥️ Frontend (Dear PyGui)
- Main UI in `main.py` using Dear PyGui
- Modern themes and responsive design
- Tab-based interface with real-time updates

### 🤝 Contributing
- Fork, branch, and PRs welcome!
- Follow modern Python style
- Document new features
- Test thoroughly

---

## 🐞 Troubleshooting & FAQ

- **Python not found?**
  - Check your PATH and install Python 3.8+
- **Dear PyGui installation issues?**
  - Run `pip install dearpygui` manually
- **Theme or UI glitches?**
  - Try clearing cache or restarting
- **Crawler errors?**
  - Check logs in `logs/` and progress in `backend/crawler_data/`
- **How do I update the satellite catalog?**
  - Go to Satellites tab and run the crawler
- **Where are my credentials stored?**
  - In the application settings (securely)

---

## 📚 Documentation & Resources

- [Enhanced v2.0 Guide](ENHANCED_V2_README.md)
- [Authentication Guide](docs_md/AUTHENTICATION_GUIDE.md)
- [Earth Engine Setup](docs/EARTH_ENGINE_SETUP.md)
- [Changelog](docs_md/CHANGELOG.md)

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 💡 Project Vision

> **Empowering everyone to explore, analyze, and download satellite data with ease, beauty, and power using modern Python technologies.**

---

## 🏆 Special Thanks

- All contributors, testers, and users!
- The open-source community
- Google Earth Engine team
- Dear PyGui development team

---

## 🚀 Get Started Now!

**Clone, install, and launch. The Earth is at your fingertips! 🌍✨** 