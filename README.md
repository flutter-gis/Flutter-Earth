# Flutter Earth Desktop (Electron + Python)

A modern, user-friendly desktop application for downloading and processing satellite imagery using Google Earth Engine. Now featuring a beautiful HTML/CSS/JS interface (via Electron) and a robust Python backend.

---

## Features
- **Modern Electron UI**: Responsive, animated, and themeable interface
- **Python Backend**: All Earth Engine operations and downloads handled by Python
- **Authentication Dialog**: Easy Google Earth Engine service account setup
- **Download Manager**: Advanced satellite imagery download with progress tracking
- **Settings & Theming**: Switch between light/dark themes and customize appearance
- **Help & Troubleshooting**: Built-in help, notifications, and error reporting
- **Logs**: All backend activity is logged for easy debugging

---

## Prerequisites
- **Python 3.8+** (with pip)
- **Node.js 18+** (with npm)
- **Google Earth Engine** account and service account credentials

---

## Installation & Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd Flutter-Earth
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Node.js dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Set up Google Earth Engine authentication
- Follow the step-by-step guide in [EARTH_ENGINE_SETUP.md](EARTH_ENGINE_SETUP.md) to create a service account and download your key file.
- The app will prompt you for your project ID and key file on first run if not already configured.

---

## How to Run

### Recommended: Use the Launcher
```bash
run_desktop.bat
```

### Or, run manually:
```bash
cd frontend
npm start
```

---

## Project Structure
```
Flutter-Earth/
├── frontend/           # Electron app (HTML/CSS/JS)
├── backend/            # Python backend scripts
├── flutter_earth_pkg/  # Original Python package (modular backend)
├── logs/               # Application logs
├── run_desktop.bat     # Launcher script
├── requirements.txt    # Python dependencies
├── README.md           # This file
```

---

## Development
- **Frontend**: Edit files in `frontend/` (HTML, CSS, JS)
- **Backend**: Edit `backend/earth_engine_processor.py` for Earth Engine logic
- **Add new features**: Extend the UI in HTML/JS and backend in Python
- **Logs**: Check the `logs/` directory for backend logs

---

## Troubleshooting
- **Electron won't start**: Check Node.js installation, run `npm install` in `frontend/`
- **Python errors**: Check Python version, run `pip install -r requirements.txt`
- **Authentication issues**: Follow [EARTH_ENGINE_SETUP.md](EARTH_ENGINE_SETUP.md) and use the in-app dialog
- **Debug logs**: See the latest file in `logs/` for backend errors and debug info

---

## License
MIT License. See repository for details.

---

**Flutter Earth** – Making satellite imagery accessible to everyone 🌍✨
