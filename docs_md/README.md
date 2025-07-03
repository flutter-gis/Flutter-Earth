# 🌍 Flutter Earth: The Ultimate Desktop Geo Playground

![Flutter Earth Logo](logo.png)

> **"Explore, analyze, and download satellite data with style!"**

---

## 🚀 Overview

**Flutter Earth** is a modern, cross-platform desktop app for exploring, analyzing, and downloading satellite imagery and geospatial data. Built with Electron and pure web tech, it brings a beautiful, themeable, and fun experience to Earth Engine workflows—no browser required!

- **No servers. No cloud. 100% local.**
- **Supercharged with themes, effects, and a playful UI.**
- **Designed for researchers, students, and geo-nerds alike!**

---

## ✨ Features

- 🗺️ **Interactive Map**: Browse, select AOIs, and preview data.
- 📥 **Download Manager**: Queue, monitor, and manage satellite downloads.
- 🛰️ **Satellite Info**: Explore detailed info on supported satellites and sensors.
- 🌱 **Index Analysis**: Run NDVI and other index analyses on your data.
- 🌐 **Vector Download**: Download and preview vector datasets.
- 📊 **Data Viewer**: Inspect and visualize your results.
- 🔄 **Progress Tracking**: Real-time logs and progress bars for all operations.
- 🎨 **Theme System**: Switch between dozens of beautiful, animated themes.
- 🧰 **Toolbox & Bookmarks**: Quick access to your favorite tools and places.
- ⚡ **Offline-First**: Works entirely offline—no web server, no cloud required.
- 🦄 **Fun Effects**: Confetti, rainbows, and more. Because why not?

---

## 🖼️ Screenshots & Diagrams

> _"A picture is worth a thousand words!"_

| Home View | Map View | Download Manager |
|---|---|---|
| ![Home](docs/screenshots/home.png) | ![Map](docs/screenshots/map.png) | ![Download](docs/screenshots/download.png) |

> _More diagrams and UI flows coming soon!_

---

## 🛠️ Getting Started (Electron Only!)

### 1. **Install Node.js & Python**
- Node.js v18+ (bundled in `node-v22.17.0-win-x64/` for Windows users)
- Python 3.8+

### 2. **Install Dependencies**
```bash
cd frontend
npm install  # or use the bundled node/npm
```

### 3. **Run the App (Electron Mode)**
```bash
cd frontend
npx electron .
```
Or use the provided scripts:
- `run_desktop.bat` (Windows)
- `run_desktop.ps1` (PowerShell)

> **No web server needed!**

---

## 👩‍💻 Developer Guide

### Project Structure
```
FE Repo/
  frontend/         # Electron app (HTML, JS, CSS, themes)
  backend/          # Python scripts for Earth Engine
  Flutter-Earth/    # (Optional) Embedded repo for advanced features
  docs/             # Guides, screenshots, and documentation
  ...
```

### Key Files
- `frontend/flutter_earth.html` — Main app UI
- `frontend/flutter_earth.js` — App logic (Vanilla JS)
- `frontend/main_electron.js` — Electron main process
- `frontend/generated_themes.js` — Auto-generated themes
- `frontend/themes.json` — Source for theme generation
- `backend/earth_engine_processor.py` — Python backend

### Debugging
- Open **DevTools** in Electron: `Ctrl+Shift+I`
- Check the **console** for `[DEBUG]` messages
- Use `TAB_DEBUG_SUMMARY.md` for a log of all major debug sessions
- Try `frontend/test_tabs_simple.html` for isolated tab testing

---

## 🎨 Theme System

- Themes are defined in `themes.json` and compiled to `generated_themes.js`
- Switch themes in the **Settings** tab
- Each theme can have:
  - Custom colors
  - Emojis/icons
  - Animated splash and UI effects
- Want to add your own? Edit `themes.json` and run the theme converter script!

---

## 🐞 Debugging Tips

- If tabs don't work, check for `.sidebar-item` vs `.toolbar-item` mismatches
- Make sure all scripts and CSS are loaded (no 404s in DevTools)
- Use the **simple tab test** (`test_tabs_simple.html`) to isolate UI bugs
- For Python/Earth Engine issues, check the logs in `/logs/`
- See `TAB_DEBUG_SUMMARY.md` for a history of fixes

---

## 🤝 Contributing

1. **Fork the repo**
2. **Create a feature branch**
3. **Make your changes (and add a theme if you want!)**
4. **Open a pull request**

> All contributions, big or small, are welcome! Add a theme, fix a bug, or just make the UI more fun.

---

## ❓ FAQ

**Q: Do I need to run a server?**
> Nope! Just use Electron. No servers, no cloud, no nonsense.

**Q: Can I use this on Mac/Linux?**
> Yes! Just install Node.js and Python, then run Electron as above.

**Q: Where are my downloads stored?**
> Set your output directory in the Download Manager or Settings tab.

**Q: How do I add a new satellite or theme?**
> Edit `themes.json` or the relevant backend Python files, then rebuild.

**Q: Why is there confetti everywhere?**
> Because science should be fun! 🎉

---

## 🎉 Fun & Quirky Stuff

- Try clicking the app title for an Easter egg!
- Some themes have unique splash effects (rainbows, magic, etc.)
- The app is fully keyboard-navigable (try arrow keys and shortcuts)
- Add your own emoji to a theme and see it in the UI
- The more you use it, the more surprises you'll find!

---

## 📢 Shoutouts

- Thanks to all contributors, testers, and the open-source geospatial community!
- Special thanks to the [Google Earth Engine](https://earthengine.google.com/) team for making global data accessible.

---

## 🏁 License

MIT License. Use, remix, and share!

---

> _"Flutter Earth: Because the world is too interesting for boring software."_
