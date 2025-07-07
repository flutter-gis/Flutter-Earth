# 🎨 Theme Effects Engine

Welcome to the **Theme Effects Engine**! This is where the magic happens for animated, interactive, and beautiful UI themes in Flutter Earth. ✨🖌️

---

## 🌈 What Does It Do?
- Powers all animated backgrounds and theme effects
- Handles confetti, sparkles, rainbows, and more
- Integrates with the theming system for seamless switching
- Makes the UI fun, lively, and unique!

---

## 🛠️ How It Works
1. **Listens for theme changes** from the UI
2. **Activates the right effect** (e.g., confetti, stars, rainbow)
3. **Animates backgrounds** using canvas, CSS, or DOM magic
4. **Cleans up** when switching themes or tabs

---

## 🚦 Usage
- Effects are defined in `theme_effects.js`
- Each effect is a function that can be triggered by a theme
- Add new effects by exporting a function and updating the theme config

---

## 🧑‍💻 Developer Tips
- Keep effects lightweight for smooth performance
- Use requestAnimationFrame for animations
- Clean up all DOM elements and listeners when switching effects
- Test effects with different themes and screen sizes

---

## 🧩 Integration
- Called automatically when a theme with effects is activated
- Works with the main theming engine and UI

---

## 📝 Example: Adding a New Effect
```js
// In theme_effects.js
export function sparkleEffect(container) {
  // Your animation code here!
}
// In themes.json
{
  "name": "Sparkle Party",
  "effect": "sparkleEffect"
}
```

---

## 🤓 For More Info
- See the main frontend README for theming architecture
- Check the code for effect templates and best practices

---

Happy theming! 🎨✨ 