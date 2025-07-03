# 🎨 Theming System

Welcome to the **Theming System**! This is where you can make Flutter Earth look and feel exactly how you want. From professional to playful, the power is yours! 🌈🦄

---

## 🌟 What Does It Do?
- Lets you switch between 30+ beautiful themes
- Supports dark/light mode, animated backgrounds, and custom icons
- Makes the UI fun, accessible, and unique for every user

---

## 🛠️ How It Works
- Themes are defined in `themes.json`
- Each theme has colors, icons, effects, and options
- The UI loads and applies the selected theme instantly

---

## 🚦 Usage
- Switch themes in the Settings tab
- Add new themes by editing `themes.json`
- Preview changes live in the app

---

## 🧑‍💻 Developer Tips
- Use clear, descriptive names for your themes
- Include both light and dark variants for best results
- Add animated effects by linking to functions in `theme_effects.js`
- Test your theme on all tabs and screen sizes

---

## 🧩 Structure of themes.json
```json
{
  "name": "Rainbow Fun",
  "colors": {
    "background": "#fff",
    "primary": "#e91e63",
    "accent": "#ffd600"
  },
  "icons": {
    "map": "🗺️",
    "download": "📥"
  },
  "effect": "confettiEffect"
}
```

---

## 🤓 For More Info
- See the main frontend README for theming architecture
- Check `theme_effects.js` for available effects

---

Happy theming! 🎨🌟 