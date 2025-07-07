# 🌍 Flutter Earth Enhanced v2.0 🚀

> **A modern, beautiful, and powerful Earth observation platform for everyone.**

---

## ✨ Overview

Flutter Earth Enhanced v2.0 is a next-generation desktop app for exploring, downloading, and analyzing satellite data. It combines a modern Python backend, a beautiful Electron/JavaScript frontend, and a powerful Google Earth Engine integration—all in a single, easy-to-use package.

- **Modern UI**: Responsive, themeable, and accessible
- **Advanced Web Crawler**: Extracts the latest satellite datasets from Google Earth Engine
- **Powerful Download Manager**: Customizable, reliable, and fast
- **Real-Time Progress & Logs**: See everything as it happens
- **Secure Authentication**: Easy GEE credential management
- **Open Source & Extensible**: Built for the community

---

## 🏗️ Architecture

```mermaid
graph TD;
  User-->|Electron UI|Frontend[Frontend (Electron/JS/HTML/CSS)]
  Frontend-->|REST/IPC|Backend[Backend (Python)]
  Backend-->|Earth Engine API|GEE[Google Earth Engine]
  Backend-->|Web Crawler|Crawler[Enhanced GEE Catalog Crawler]
  Backend-->|Local Storage|Data[Local Data/Thumbnails/Logs]
```

- **Frontend**: Electron app with modern JS, Bootstrap 5, Bulma, and custom CSS
- **Backend**: Python 3.8+, async, type-safe, robust error handling
- **Web Crawler**: Async, multi-threaded, extracts and updates satellite catalog
- **Data Storage**: Local JSON, thumbnails, logs, and user settings

---

## 🚦 Quick Start

### 🛠️ Prerequisites
- Python 3.8+
- Local Node.js (included in `node-v22.17.0-win-x64/`)
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
   cd frontend
   npm install
   cd ..
   ```
3. **Start the app**
   ```bash
   start.bat
   # Or manually:
   # Terminal 1: python main.py
   # Terminal 2: cd frontend && npm start
   ```

**Note:** The project includes a local Node.js installation (`node-v22.17.0-win-x64/`) that will be used automatically. No system-wide Node.js installation is required.

---

## 🎨 Theming & UI Customization

- 🌗 **Theme Switcher**: Toggle between Default, Dark, Nature, Ocean, Sunset, Minimal
- 🎉 **Particle Effects**: Dynamic backgrounds for select themes
- 🖼️ **Responsive Design**: Looks great on any screen
- ⚡ **Keyboard Shortcuts**: Fast navigation (see Settings > Advanced)

---

## 🛰️ Satellite Info & Web Crawler

### 🛰️ Satellite Info Tab
- Browse all available satellites, sensors, and datasets
- Filter, search, and view detailed info for each satellite
- See real-time stats: total satellites, datasets, publishers, last update
- Click any satellite for details, code snippets, and download options

### 🕷️ Web Crawler Integration
- **Fully integrated into Satellite Info tab**
- Start/stop the crawler, see live progress, and view logs
- Progress bar, step tracker, and ETA
- Dataset viewer: search, filter, and explore all extracted datasets
- Download thumbnails, metadata, and code snippets
- All crawler actions and results are visible in the Satellite Info view—no more modals!

---

## 🧭 Usage Guide

### 1️⃣ **Authenticate (Optional, for GEE features)**
- On first launch, upload your Google Cloud service account JSON key and project ID
- Credentials are stored securely in `C:\FE Auth`
- You can continue in offline mode for basic features

### 2️⃣ **Explore the Interface**
- Use the top toolbar to switch between Home, Map, Download, Satellite Info, Analysis, Vector, Data, Progress, and Settings
- Hover over any button for tooltips and dropdowns

### 3️⃣ **Satellite Info & Crawler**
- Go to the Satellite Info tab
- Click "Start Data Collection" to run the crawler
- Watch real-time progress, see logs, and view extracted datasets instantly
- Filter/search datasets, view details, and copy Earth Engine code

### 4️⃣ **Download Data**
- Go to the Download tab
- Select area, date range, sensor, and output options
- Start download and monitor progress in real time

### 5️⃣ **Settings & Customization**
- Change themes, font size, and advanced options in Settings
- Enable debug mode for detailed logs

---

## 🛠️ Development & Contribution

### 🐍 Backend (Python)
- All backend logic in `main.py`, `backend/earth_engine_processor_enhanced.py`, and `backend/gee_catalog_crawler_enhanced_v2.py`
- Uses async, dataclasses, and robust error handling
- Logs in `logs/` and progress in `backend/crawler_data/`

### 💻 Frontend (Electron/JS)
- Main UI in `frontend/flutter_earth_enhanced_v2.html`, logic in `frontend/flutter_earth_enhanced_v2.js`, styles in `frontend/flutter_earth_enhanced_v2.css`
- Modern ES6+, modular, and easy to extend
- Theming in `theme_effects_enhanced.js` and `generated_themes.js`

### 🤝 Contributing
- Fork, branch, and PRs welcome!
- Follow modern Python/JS style
- Document new features
- Test thoroughly

---

## 🐞 Troubleshooting & FAQ

- **Python/Node not found?**
  - Check your PATH and install the required versions
- **Electron app won't start?**
  - Run `npm install` in `frontend/`
- **Theme or UI glitches?**
  - Try clearing cache or restarting
- **Crawler errors?**
  - Check logs in `logs/` and progress in `backend/crawler_data/`
- **How do I update the satellite catalog?**
  - Go to Satellite Info and run the crawler
- **Where are my credentials stored?**
  - In `C:\FE Auth` (Windows only)

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

> **Empowering everyone to explore, analyze, and download satellite data with ease, beauty, and power.**

---

## 🏆 Special Thanks

- All contributors, testers, and users!
- The open-source community
- Google Earth Engine team

---

## 🚀 Get Started Now!

**Clone, install, and launch. The Earth is at your fingertips! 🌍✨** 