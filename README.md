<p align="center">
  <img src="logo.png" alt="Flutter Earth Logo" width="160" />
</p>

# 🌍 Flutter Earth

Welcome to **Flutter Earth** – your all-in-one, supercharged desktop app for downloading and processing satellite imagery from Google Earth Engine! 🚀

> **"Explore the world, pixel by pixel!"**

---

## ✨ Features

- **Modern Electron Interface:** Sleek, responsive, and beautiful UI for a seamless experience.
- **Modular Python Backend:** Professional, scalable, and robust.
- **Theming Support:** Switch between Dark, Light, and fun custom themes.
- **Advanced Downloading:** Grab imagery from Landsat, Sentinel-2, and more.
- **On-the-fly Processing:** Cloud masking, pre-processing, and more magic.
- **Robust Configuration:** All your settings, managed with style.
- **Comprehensive Satellite Info:** Browse and learn about satellites.
- **Offline Mode:** No credentials? No problem! Explore in limited offline mode.

---

## 🖼️ Screenshots

| Splash Screen | Main App |
|:------------:|:--------:|
| ![Logo](logo.png) | ![Logo](logo.png) |

*Add your own screenshots here!*

---

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 18+ (for Electron frontend)
- Google Earth Engine account (for full features)

### Get Started
```bash
git clone https://github.com/yourusername/flutter-earth.git
cd flutter-earth
```

#### Install Python dependencies
```bash
pip install -r requirements.txt
```

#### Install frontend dependencies
```bash
cd frontend
npm install
```

#### Run the app
```bash
cd ..
run_desktop.bat
```

---

## 🚦 Usage

1. **Start the app** – watch the Earth spin (or not!) on the splash screen.
2. **Sign in** with your Google Earth Engine account if prompted.
3. **Select your area of interest** and satellite data source.
4. **Configure options** and download imagery like a pro.
5. **Browse satellite info, tweak settings, and have fun!**

---

## 📴 Offline Mode

No credentials? Flutter Earth lets you explore in offline mode with limited features. You can:
- Browse the interface
- Check out satellite info
- Prepare downloads (but not fetch new imagery)

To unlock all features, just authenticate with your Earth Engine account!

---

## ❓ FAQ

**Q: Do I need a Google Earth Engine account?**  
A: For full power, yes! But you can still play around in offline mode.

**Q: Can I use this on Mac or Linux?**  
A: Designed for Windows, but may work elsewhere with a little elbow grease.

**Q: Where are downloads saved?**  
A: By default, in the app's working directory. Change it in settings!

**Q: How do I update?**  
A: Pull the latest from GitHub, then rerun `npm install` and `pip install -r requirements.txt` if needed.

---

## 🤝 Contributing

We love contributors! To help:
- Fork the repo
- Make your changes (keep it fun and clean!)
- Submit a pull request
- Add yourself to the credits below!

---

## 🏆 Credits

- **You!** (for using Flutter Earth)
- [Your Name Here]
- [All Contributors]
- [Google Earth Engine](https://earthengine.google.com/)

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

> Made with 💙 by the Flutter Earth Team. Happy exploring!
