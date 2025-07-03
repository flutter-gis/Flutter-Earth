# Frontend (Electron/JS)

This directory contains the Electron-based frontend for Flutter Earth, providing a modern, themeable UI for satellite data exploration and download.

## Main Components
- **flutter_earth.html**: Main UI
- **flutter_earth.js**: UI logic and backend communication
- **flutter_earth.css**: Styles and themes
- **main_electron.js**: Electron entry point
- **themes.json**: Theme definitions

## Features
- Tabbed interface: Map, Download, Satellite Info, Index, Vector, Settings, About
- 30+ themes, dark/light mode, animated backgrounds
- Real-time progress, logs, and notifications
- Form validation and user-friendly feedback

## Setup
```
cd frontend
npm install
```

## Running
```
npm start
```

## Customization
- Add or edit themes in `themes.json`
- Modify UI in `flutter_earth.html` and `flutter_earth.js`

## Developer Notes
- Communicates with the Python backend via Electron bridge
- See the main project README for architecture and workflow

---

## 🚦 What's in Here?

- The **Electron app** (HTML, CSS, JS)
- All the themes, icons, and UI magic
- The bridge to the Python backend
- The place where the fun happens!

---

## 🎨 Themes Galore

- 🌍 Basic (clean, professional)
- 🦄 My Little Pony (rainbows and sparkles!)
- ⛏️ Minecraft (blocky fun)
- 🏳️‍🌈 Pride (show your colors)
- 🤝 Unity Pride (community vibes)
- ...and more!

Add your own in `themes.json` and see them instantly!

---

## 🧩 Structure

```
frontend/
├── flutter_earth.html   # Main UI
├── flutter_earth.js     # All the logic
├── flutter_earth.css    # All the style
├── generated_themes.js  # Theme magic
├── main_electron.js     # Electron entry
├── preload.js           # Secure bridge
├── themes.json          # Theme definitions
└── ...
```

---

## 🦄 Fun Facts

- The UI is fully themeable and animated
- You can drag, resize, and even use keyboard shortcuts
- The sidebar icons are all emoji (because why not?)
- The progress bars are actually fun to watch

---

## 🧑‍🎨 Want to Hack?

- Fork, clone, and run `npm start`
- Edit `flutter_earth.html`, `flutter_earth.js`, or `flutter_earth.css`
- Add a theme, a button, or a new effect!
- PRs and ideas welcome!

---

## 📄 License

MIT. Remix, share, and have fun!

---

<div align="center">
  <b>Made with 💙 by the Flutter Earth Team</b>
</div> 