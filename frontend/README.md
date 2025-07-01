# Flutter Earth Frontend

This directory contains the frontend components of Flutter Earth, built with Electron and modern web technologies.

## Structure

```
frontend/
├── flutter_earth.html      # Main application interface
├── flutter_earth.css       # Styles and theme definitions
├── flutter_earth.js        # Main application logic
├── main_electron.js        # Electron main process
├── preload.js             # Electron preload script
├── package.json           # Node.js dependencies
├── themes.json            # Theme definitions
├── generated_themes.js    # Auto-generated theme data
├── theme_converter.py     # Python theme converter
├── theme_showcase.html    # Theme showcase page
├── test_themes.html       # Theme testing interface
├── readme_page.html       # Application readme
└── map_selector.html      # Map selection interface
```

## Features

### 🎨 Theme System
- **30+ Custom Themes**: From professional to character-inspired
- **Dynamic Theme Switching**: Change themes on the fly
- **Theme Categories**: Professional, MLP, Minecraft, Pride themes
- **Customizable Options**: Animations, icons, catchphrases

### 🛰️ Satellite Data Interface
- **Interactive Map**: Select areas of interest
- **Satellite Catalog**: Browse available datasets
- **Download Management**: Monitor progress and status
- **Data Visualization**: Preview satellite imagery

### 🔧 Advanced Tools
- **Index Analysis**: Calculate NDVI, NDWI, and other indices
- **Vector Downloads**: Administrative boundaries and vector data
- **Batch Processing**: Multiple areas and time periods
- **Data Export**: Various output formats

## Development

### Prerequisites
- Node.js 16 or higher
- npm or yarn package manager

### Setup
1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

### Building
To build the application for distribution:
```bash
npm run build
```

## Theme Development

### Creating New Themes
1. Add theme definition to `themes.json`
2. Run theme converter:
   ```bash
   python theme_converter.py
   ```
3. Test theme in `test_themes.html`

### Theme Structure
```json
{
  "name": "theme_name",
  "display_name": "Theme Display Name",
  "category": "professional|mlp|minecraft|pride",
  "background": "#color",
  "primary": "#color",
  "emoji": "🎨",
  "splashEffect": "effect_name",
  "uiEffect": "ui_effect_name",
  "colors": {
    "background": "#color",
    "primary": "#color",
    // ... more color definitions
  },
  "catchphrases": {
    "app_title": "App Title",
    // ... more text customizations
  }
}
```

## Testing

### Theme Testing
- Use `test_themes.html` to test theme functionality
- Use `theme_showcase.html` to preview all themes

### UI Testing
- Manual testing through the main interface
- Check browser console for debug information

## Troubleshooting

### Common Issues
1. **Theme not loading**: Check `generated_themes.js` exists
2. **Electron not starting**: Verify Node.js installation
3. **Map not displaying**: Check internet connection

### Debug Mode
Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## Contributing

When contributing to the frontend:

1. Follow existing code style
2. Test themes in multiple browsers
3. Update documentation for new features
4. Ensure accessibility standards are met

## License

MIT License - see main project license for details. 