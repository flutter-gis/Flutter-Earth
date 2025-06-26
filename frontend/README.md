# Flutter Earth HTML Interface

This directory contains the HTML/CSS/JavaScript conversion of the original QML-based Flutter Earth interface.

## Overview

The QML interface has been completely converted to a modern web-based interface using:
- **HTML5** for structure
- **CSS3** with CSS variables for theming
- **JavaScript ES6+** for functionality
- **Responsive design** for mobile compatibility

## Files

### Core Files
- `flutter_earth.html` - Main HTML structure
- `flutter_earth.css` - Complete styling system with themes
- `flutter_earth.js` - JavaScript functionality and interactions

### Supporting Files
- `map_selector.html` - Map selection component
- `README.md` - This documentation

## Features Converted from QML

### Layout Components
- ✅ **Sidebar Navigation** - All navigation items with icons and labels
- ✅ **Top Bar** - Application title, version, and help button
- ✅ **Main Content Area** - Dynamic view switching
- ✅ **Status Bar** - Connection status and system information

### Views
- ✅ **Welcome View** - Home screen with animated logo
- ✅ **Download View** - Complete download form with all fields
- ✅ **Map View** - Placeholder for map integration
- ✅ **Settings View** - Theme selection and configuration
- ✅ **About View** - Application information
- ✅ **Progress View** - Download progress tracking
- ✅ **Index Analysis View** - Analysis tools interface
- ✅ **Vector Download View** - Vector data download interface
- ✅ **Data Viewer View** - Data visualization interface
- ✅ **Satellite Info View** - Satellite information display

### Modals and Dialogs
- ✅ **Authentication Dialog** - Google Earth Engine authentication
- ✅ **Help Popup** - Documentation and help information
- ✅ **Calendar Popup** - Date selection with full calendar
- ✅ **Map Selector Modal** - Area selection interface
- ✅ **Notification System** - Success, error, and info notifications

### Theming System
- ✅ **CSS Variables** - Complete theme system with light/dark modes
- ✅ **Dynamic Theme Switching** - Runtime theme changes
- ✅ **Responsive Design** - Mobile and tablet compatibility

## How to Run

### Option 1: Direct Browser Opening
1. Navigate to the `frontend` directory
2. Double-click `flutter_earth.html` to open in your default browser

### Option 2: Using the Batch File
1. Run `run_html_ui.bat` from the project root
2. The interface will automatically open in your default browser

### Option 3: Local Server (Recommended)
1. Install a local server (e.g., `python -m http.server` or Live Server extension)
2. Serve the `frontend` directory
3. Access via `http://localhost:8000/flutter_earth.html`

## Keyboard Shortcuts

- `Ctrl/Cmd + 1` - Switch to Home view
- `Ctrl/Cmd + 2` - Switch to Download view
- `Ctrl/Cmd + 3` - Switch to Map view
- `Ctrl/Cmd + 4` - Switch to Settings view
- `Ctrl/Cmd + H` - Show help popup
- `Ctrl/Cmd + Q` - Show authentication dialog
- `Escape` - Close any open modal

## Theme System

The interface supports multiple themes:

### Default Theme
- Pink-based color scheme matching the original QML design
- Light background with subtle shadows
- High contrast text for readability

### Dark Theme
- Dark background with blue accents
- Reduced eye strain for extended use
- Maintains accessibility standards

### Light Theme
- Clean white background
- Professional appearance
- Optimized for daytime use

## Responsive Design

The interface automatically adapts to different screen sizes:

### Desktop (>768px)
- Full sidebar with labels
- Complete top bar with version info
- Full-featured interface

### Tablet (768px - 480px)
- Compact sidebar with icons only
- Simplified top bar
- Optimized touch interactions

### Mobile (<480px)
- Bottom navigation bar
- Full-width content area
- Touch-optimized controls

## Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Customization

### Adding New Views
1. Add HTML structure to `flutter_earth.html`
2. Add corresponding CSS styles to `flutter_earth.css`
3. Add JavaScript functionality to `flutter_earth.js`

### Modifying Themes
1. Edit CSS variables in `:root` selector
2. Add new theme variants using `[data-theme="theme-name"]`
3. Update theme switching logic in JavaScript

### Adding New Features
1. Follow the existing code patterns
2. Use CSS variables for consistent styling
3. Implement responsive design considerations
4. Add keyboard shortcuts for accessibility

## Integration with Backend

The HTML interface is designed to work with the existing Python backend:

1. **Authentication** - Uses the same Google Earth Engine authentication flow
2. **Data Download** - Compatible with existing download functionality
3. **Map Integration** - Can integrate with existing map components
4. **Progress Tracking** - Real-time progress updates from backend

## Performance Optimizations

- CSS animations use `transform` and `opacity` for GPU acceleration
- JavaScript uses debouncing and throttling for smooth interactions
- Images and assets are optimized for web delivery
- Lazy loading for non-critical components

## Accessibility Features

- Keyboard navigation support
- Screen reader compatibility
- High contrast themes
- Focus indicators
- Semantic HTML structure

## Future Enhancements

- WebGL-based map rendering
- Real-time data streaming
- Advanced visualization tools
- Collaborative features
- Offline capability with service workers

## Troubleshooting

### Common Issues

1. **Interface not loading**
   - Check browser console for JavaScript errors
   - Ensure all files are in the correct directory structure
   - Try using a local server instead of file:// protocol

2. **Styling issues**
   - Clear browser cache
   - Check CSS file path
   - Verify CSS variables are supported

3. **JavaScript errors**
   - Check browser console for error messages
   - Ensure jQuery is loaded (if using CDN)
   - Verify all event listeners are properly attached

### Debug Mode

Enable debug mode by adding `?debug=true` to the URL:
```
flutter_earth.html?debug=true
```

This will show additional console logging and development tools.

## Contributing

When contributing to the HTML interface:

1. Follow the existing code style and patterns
2. Test on multiple browsers and devices
3. Ensure accessibility compliance
4. Update documentation for new features
5. Add appropriate keyboard shortcuts

## License

This HTML interface is part of the Flutter Earth project and follows the same licensing terms as the main application. 