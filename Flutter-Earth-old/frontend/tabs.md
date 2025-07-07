# 🗂️ Tab System

Welcome to the **Tab System**! This is the navigation backbone of Flutter Earth's frontend, letting you jump between maps, downloads, satellite info, and more. 🏷️🗺️

---

## 📑 What Tabs Exist?
- **Map**: Select and preview your area of interest
- **Download**: Configure and start satellite imagery downloads
- **Satellite Info**: Browse and search the full satellite catalog
- **Index**: Explore index datasets and metadata
- **Vector**: Work with vector data and overlays
- **Settings**: Tweak themes, authentication, and advanced options
- **About**: Learn about the app and credits

---

## 🛠️ How Navigation Works
- Tabs are defined in the main HTML and JS files
- Clicking a tab shows its panel and hides others
- Active tab is highlighted for clarity
- Keyboard navigation is supported for accessibility

---

## 🚦 Usage
- Add new tabs by editing `flutter_earth.html` and `flutter_earth.js`
- Each tab has a unique ID and content panel
- Update the tab list and navigation logic to include your new tab

---

## 🧑‍💻 Developer Tips
- Keep tab content modular for easy maintenance
- Use clear IDs and class names for each tab
- Test navigation with mouse and keyboard
- Add tooltips or icons for extra clarity

---

## 🧩 Integration
- Tabs interact with the backend for data, downloads, and settings
- Theming and effects apply to all tabs

---

## 📝 Example: Adding a New Tab
```html
<!-- In flutter_earth.html -->
<li id="tab-newfeature">New Feature</li>
<div id="panel-newfeature" class="tab-panel">Your content here!</div>
```
```js
// In flutter_earth.js
// Add logic to show/hide the new tab panel
```

---

## 🤓 For More Info
- See the main frontend README for UI architecture
- Check the code for tab templates and best practices

---

Happy tabbing! 🗂️✨ 