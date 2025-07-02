<div align="center">
  <style>
    /* Flutter Earth Enhanced README Styles */
    .flutter-earth-header {
      background: linear-gradient(135deg, #181A20 0%, #23272F 50%, #4A90E2 100%);
      border-radius: 20px;
      padding: 40px 20px;
      margin: 20px 0;
      box-shadow: 0 10px 30px rgba(74, 144, 226, 0.3);
      position: relative;
      overflow: hidden;
    }
    
    .flutter-earth-header::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(74, 144, 226, 0.1) 0%, transparent 70%);
      animation: rotate 20s linear infinite;
      pointer-events: none;
    }
    
    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    .logo-container {
      position: relative;
      z-index: 2;
    }
    
    .logo-container img {
      border-radius: 50%;
      box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
      transition: all 0.3s ease;
      animation: pulse 2s ease-in-out infinite alternate;
    }
    
    .logo-container img:hover {
      transform: scale(1.1) rotate(5deg);
      box-shadow: 0 12px 35px rgba(74, 144, 226, 0.6);
    }
    
    @keyframes pulse {
      from { transform: scale(1); }
      to { transform: scale(1.05); }
    }
    
    .title-gradient {
      background: linear-gradient(45deg, #4fc3f7, #e91e63, #43a047, #ffd600);
      background-size: 300% 300%;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: gradientShift 3s ease-in-out infinite;
      font-weight: bold;
      font-size: 2.5em;
      margin: 20px 0;
    }
    
    @keyframes gradientShift {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }
    
    .tagline {
      font-size: 1.2em;
      color: #E0E0E0;
      margin: 15px 0;
      text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .badge-container {
      display: flex;
      justify-content: center;
      gap: 10px;
      flex-wrap: wrap;
      margin: 20px 0;
    }
    
    .badge-container img {
      transition: transform 0.3s ease;
    }
    
    .badge-container img:hover {
      transform: translateY(-3px);
    }
    
    .quote-section {
      background: linear-gradient(135deg, #23272F 0%, #181A20 100%);
      border-left: 4px solid #4A90E2;
      padding: 20px;
      margin: 30px 0;
      border-radius: 0 15px 15px 0;
      position: relative;
    }
    
    .quote-section::before {
      content: '"';
      font-size: 4em;
      color: #4A90E2;
      position: absolute;
      top: -10px;
      left: 10px;
      opacity: 0.3;
    }
    
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin: 30px 0;
    }
    
    .feature-card {
      background: linear-gradient(135deg, #23272F 0%, #181A20 100%);
      border: 2px solid #4A90E2;
      border-radius: 15px;
      padding: 25px;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }
    
    .feature-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(74, 144, 226, 0.1), transparent);
      transition: left 0.5s ease;
    }
    
    .feature-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 25px rgba(74, 144, 226, 0.3);
      border-color: #50C878;
    }
    
    .feature-card:hover::before {
      left: 100%;
    }
    
    .feature-icon {
      font-size: 2em;
      margin-bottom: 15px;
      display: block;
    }
    
    .feature-title {
      color: #4A90E2;
      font-weight: bold;
      margin-bottom: 10px;
      font-size: 1.2em;
    }
    
    .feature-description {
      color: #E0E0E0;
      line-height: 1.6;
    }
    
    .code-block {
      background: linear-gradient(135deg, #181A20 0%, #23272F 100%);
      border: 2px solid #4A90E2;
      border-radius: 10px;
      padding: 20px;
      margin: 20px 0;
      position: relative;
      overflow: hidden;
    }
    
    .code-block::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #4A90E2, #50C878, #FFB347, #E57373);
      animation: rainbow 3s linear infinite;
    }
    
    @keyframes rainbow {
      0% { background-position: 0% 50%; }
      100% { background-position: 100% 50%; }
    }
    
    .screenshot-container {
      text-align: center;
      margin: 40px 0;
    }
    
    .screenshot-container img {
      border-radius: 15px;
      box-shadow: 0 10px 30px rgba(74, 144, 226, 0.4);
      transition: all 0.3s ease;
      max-width: 100%;
      height: auto;
    }
    
    .screenshot-container img:hover {
      transform: scale(1.02);
      box-shadow: 0 15px 40px rgba(74, 144, 226, 0.6);
    }
    
    .navigation-guide {
      background: linear-gradient(135deg, #23272F 0%, #181A20 100%);
      border-radius: 15px;
      padding: 25px;
      margin: 30px 0;
      border: 2px solid #4A90E2;
    }
    
    .nav-item {
      display: flex;
      align-items: center;
      margin: 15px 0;
      padding: 10px;
      border-radius: 8px;
      transition: all 0.3s ease;
    }
    
    .nav-item:hover {
      background: rgba(74, 144, 226, 0.1);
      transform: translateX(10px);
    }
    
    .nav-icon {
      font-size: 1.5em;
      margin-right: 15px;
      min-width: 30px;
    }
    
    .nav-text {
      color: #E0E0E0;
      flex: 1;
    }
    
    .nav-description {
      color: #A0A0A0;
      font-size: 0.9em;
      font-style: italic;
    }
    
    .theme-showcase {
      background: linear-gradient(135deg, #181A20 0%, #23272F 100%);
      border-radius: 15px;
      padding: 25px;
      margin: 30px 0;
      border: 2px solid #4A90E2;
    }
    
    .theme-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      margin-top: 20px;
    }
    
    .theme-item {
      background: rgba(74, 144, 226, 0.1);
      border: 1px solid #4A90E2;
      border-radius: 10px;
      padding: 15px;
      text-align: center;
      transition: all 0.3s ease;
    }
    
    .theme-item:hover {
      background: rgba(74, 144, 226, 0.2);
      transform: scale(1.05);
    }
    
    .theme-emoji {
      font-size: 2em;
      margin-bottom: 10px;
      display: block;
    }
    
    .theme-name {
      color: #4A90E2;
      font-weight: bold;
      margin-bottom: 5px;
    }
    
    .theme-category {
      color: #A0A0A0;
      font-size: 0.8em;
    }
    
    .footer {
      background: linear-gradient(135deg, #23272F 0%, #181A20 100%);
      border-radius: 15px;
      padding: 30px;
      margin: 40px 0 20px 0;
      text-align: center;
      border: 2px solid #4A90E2;
    }
    
    .footer-text {
      color: #E0E0E0;
      font-size: 1.1em;
      margin-bottom: 10px;
    }
    
    .footer-quote {
      color: #A0A0A0;
      font-style: italic;
      font-size: 0.9em;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
      .features-grid {
        grid-template-columns: 1fr;
      }
      
      .theme-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      }
      
      .title-gradient {
        font-size: 2em;
      }
    }
    
    /* Dark mode compatibility */
    @media (prefers-color-scheme: dark) {
      .flutter-earth-header {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #4A90E2 100%);
      }
    }
    
    /* Additional animations and effects */
    .theme-item {
      animation: fadeInUp 0.6s ease-out;
      animation-fill-mode: both;
    }
    
    .theme-item:nth-child(1) { animation-delay: 0.1s; }
    .theme-item:nth-child(2) { animation-delay: 0.2s; }
    .theme-item:nth-child(3) { animation-delay: 0.3s; }
    .theme-item:nth-child(4) { animation-delay: 0.4s; }
    .theme-item:nth-child(5) { animation-delay: 0.5s; }
    .theme-item:nth-child(6) { animation-delay: 0.6s; }
    .theme-item:nth-child(7) { animation-delay: 0.7s; }
    .theme-item:nth-child(8) { animation-delay: 0.8s; }
    .theme-item:nth-child(9) { animation-delay: 0.9s; }
    .theme-item:nth-child(10) { animation-delay: 1.0s; }
    .theme-item:nth-child(11) { animation-delay: 1.1s; }
    .theme-item:nth-child(12) { animation-delay: 1.2s; }
    .theme-item:nth-child(13) { animation-delay: 1.3s; }
    
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    /* Floating animation for emojis */
    .theme-emoji {
      animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-5px); }
    }
    
    /* Glowing effect for feature cards */
    .feature-card {
      box-shadow: 0 0 20px rgba(74, 144, 226, 0.1);
    }
    
    .feature-card:hover {
      box-shadow: 0 0 30px rgba(74, 144, 226, 0.3);
    }
    
    /* Typing effect for the title */
    .title-gradient {
      position: relative;
    }
    
    .title-gradient::after {
      content: '|';
      animation: blink 1s infinite;
      color: #4A90E2;
    }
    
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
  </style>

  <div class="flutter-earth-header">
    <div class="logo-container">
      <img src="logo.png" alt="Flutter Earth Logo" width="160" height="160" />
    </div>
    
    <h1 class="title-gradient">🌈 Flutter Earth 🛰️</h1>
    <p class="tagline"><b>The most <span style="color:#e91e63;">colorful</span>, <span style="color:#43a047;">fun</span>, and <span style="color:#ffd600;">powerful</span> way to explore satellite data and Earth Engine magic!</b></p>
    
    <div class="badge-container">
      <a href="#"><img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge"/></a>
      <a href="#"><img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge"/></a>
      <a href="#"><img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-ff69b4?style=for-the-badge"/></a>
    </div>
  </div>
</div>

<div class="quote-section">
  <p style="color: #E0E0E0; font-size: 1.2em; margin: 0; padding-left: 30px;">
    <b>"Why just analyze the Earth, when you can do it in style?"</b>
  </p>
</div>

---

## ✨ What is Flutter Earth?

Flutter Earth is your all-in-one, supercharged, desktop playground for:
- 🛰️ **Exploring satellites** (with real-time data crawling!)
- 📥 **Downloading Earth Engine data** (with a beautiful progress bar!)
- 🌱 **Running index analysis** (NDVI, NDWI, and more!)
- 🎨 **Switching between 20+ wild themes** (from Minecraft to Pride!)
- 🌐 **Viewing and exporting raster/vector data**
- ⚡ **Having fun while doing serious science!**

---

## 🚀 Quickstart (It's Easy!)

<div class="code-block">
```bash
# 1. Clone the repo
$ git clone https://github.com/yourusername/flutter-earth.git
$ cd flutter-earth

# 2. Install dependencies
$ cd frontend && npm install
$ cd ../backend && pip install -r requirements.txt

# 3. Launch the app
$ cd .. && npm start
```
</div>

> 💡 **Pro Tip:** First time? Go to the 🛰️ Satellite Info tab and hit "Start Data Collection" to fill your app with satellite goodness!

---

## 🌟 Features (With Extra Sparkle)

<div class="features-grid">
  <div class="feature-card">
    <span class="feature-icon">🛰️</span>
    <div class="feature-title">Satellite Explorer</div>
    <div class="feature-description">Real-time crawling, search, code snippets, and thumbnails!</div>
  </div>
  
  <div class="feature-card">
    <span class="feature-icon">📥</span>
    <div class="feature-title">Download Manager</div>
    <div class="feature-description">Multi-sensor, AOI, cloud masking, and a progress bar that's actually fun to watch!</div>
  </div>
  
  <div class="feature-card">
    <span class="feature-icon">🌱</span>
    <div class="feature-title">Index Analysis</div>
    <div class="feature-description">NDVI, NDWI, EVI, batch processing, and instant charts!</div>
  </div>
  
  <div class="feature-card">
    <span class="feature-icon">🌐</span>
    <div class="feature-title">Vector Download</div>
    <div class="feature-description">GeoJSON, Shapefile, KML, and interactive AOI!</div>
  </div>
  
  <div class="feature-card">
    <span class="feature-icon">📊</span>
    <div class="feature-title">Data Viewer</div>
    <div class="feature-description">Raster & vector support, metadata, and export!</div>
  </div>
  
  <div class="feature-card">
    <span class="feature-icon">🎨</span>
    <div class="feature-title">Themes Galore</div>
    <div class="feature-description">20+ themes: Basic, MLP, Minecraft, Pride, and more!</div>
  </div>
</div>

---

## 🎉 Screenshots

<div class="screenshot-container">
  <img src="logo.png" width="80" alt="Flutter Earth Screenshot"/>
  <br><b style="color: #E0E0E0;">Welcome to Flutter Earth!</b>
</div>

> _Want your screenshot here? Open a PR with your favorite theme!_

---

## 🛠️ Setup & Configuration

- **Node.js** v16+ and **Python** 3.8+
- (Optional) [Google Earth Engine](https://earthengine.google.com) account for full power
- Place your Earth Engine credentials in `backend/`

### Custom Themes? Heck Yes!
Add your own to `frontend/themes.json`:
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

---

## 🧭 Navigation Guide

<div class="navigation-guide">
  <div class="nav-item">
    <span class="nav-icon">🏠</span>
    <div>
      <div class="nav-text"><b>Home</b></div>
      <div class="nav-description">See the logo, feel the vibes</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">🗺️</span>
    <div>
      <div class="nav-text"><b>Map</b></div>
      <div class="nav-description">(Coming soon!)</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">📥</span>
    <div>
      <div class="nav-text"><b>Download</b></div>
      <div class="nav-description">Grab satellite data with style</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">🛰️</span>
    <div>
      <div class="nav-text"><b>Satellite Info</b></div>
      <div class="nav-description">Crawl, search, and learn about satellites</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">🌱</span>
    <div>
      <div class="nav-text"><b>Index Analysis</b></div>
      <div class="nav-description">Run NDVI, NDWI, and more</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">🌐</span>
    <div>
      <div class="nav-text"><b>Vector Download</b></div>
      <div class="nav-description">Get vector data in your favorite format</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">📊</span>
    <div>
      <div class="nav-text"><b>Data Viewer</b></div>
      <div class="nav-description">See your data, your way</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">⚙️</span>
    <div>
      <div class="nav-text"><b>Settings</b></div>
      <div class="nav-description">Pick a theme, tweak options, and more</div>
    </div>
  </div>
  
  <div class="nav-item">
    <span class="nav-icon">ℹ️</span>
    <div>
      <div class="nav-text"><b>About</b></div>
      <div class="nav-description">Meet the devs and see what's next</div>
    </div>
  </div>
</div>

---

## 🎨 Available Themes

<div class="theme-showcase">
  <h3 style="color: #4A90E2; margin-bottom: 20px;">Choose Your Adventure!</h3>
  <div class="theme-grid">
    <div class="theme-item">
      <span class="theme-emoji">🌑</span>
      <div class="theme-name">Default Dark</div>
      <div class="theme-category">Professional</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌞</span>
      <div class="theme-name">Light</div>
      <div class="theme-category">Professional</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🤝</span>
      <div class="theme-name">Unity Pride</div>
      <div class="theme-category">Pride</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🦄</span>
      <div class="theme-name">MLP</div>
      <div class="theme-category">Fun</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">⚡</span>
      <div class="theme-name">Cyberpunk</div>
      <div class="theme-category">Sci-Fi</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌊</span>
      <div class="theme-name">Ocean Depths</div>
      <div class="theme-category">Nature</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌅</span>
      <div class="theme-name">Sunset Vibes</div>
      <div class="theme-category">Warm</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌲</span>
      <div class="theme-name">Forest Mist</div>
      <div class="theme-category">Nature</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌈</span>
      <div class="theme-name">Neon Dreams</div>
      <div class="theme-category">Vibrant</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🌌</span>
      <div class="theme-name">Aurora Borealis</div>
      <div class="theme-category">Mystical</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🏳️‍🌈</span>
      <div class="theme-name">Pride</div>
      <div class="theme-category">Celebration</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">⛏️</span>
      <div class="theme-name">Minecraft</div>
      <div class="theme-category">Gaming</div>
    </div>
    <div class="theme-item">
      <span class="theme-emoji">🎮</span>
      <div class="theme-name">Retro Gaming</div>
      <div class="theme-category">Nostalgic</div>
    </div>
  </div>
</div>

---

## 💡 Did You Know?

- You can switch themes instantly—try the 🦄 MLP or 🏳️‍🌈 Pride themes for a surprise!
- The crawler is multi-threaded and can fetch 100+ satellites in minutes
- You can copy Earth Engine code snippets for any satellite
- The app works offline for most features

---

## 🤩 Why Flutter Earth?

- **It's fun.**
- **It's beautiful.**
- **It's powerful.**
- **It's open source.**
- **It's made for YOU!**

---

## 🧑‍💻 Contributing

We love contributors! Open an issue, make a PR, or just say hi in Discussions. All skill levels welcome.

---

## 📄 License

MIT. Use it, remix it, share it, just don't sell it as your own!

---

<div class="footer">
  <div class="footer-text">
    <b>Made with ❤️ by the Flutter Earth Team</b>
  </div>
  <div class="footer-quote">
    "Empowering geospatial analysis with beautiful, accessible tools."
  </div>
</div>
