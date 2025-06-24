import QtQuick 2.15

pragma Singleton

QtObject {
    id: themeProvider

    // Properties to hold the current theme data
    // Initialize with default values or fetch from backend on component completion
    property var currentTheme: backend.getCurrentThemeData() // Initial load

    // Expose parts of the theme for easier access
    property var colors: currentTheme.colors || {}
    property var fonts: currentTheme.fonts || {}
    property var styles: currentTheme.styles || {}
    property var paths: currentTheme.paths || {}
    property var catchphrases: currentTheme.catchphrases || {}
    property var options: currentTheme.options || {}
    property var metadata: currentTheme.metadata || {}

    function getCatchphrase(viewKey, defaultText) {
        if (options.use_character_catchphrases && catchphrases.hasOwnProperty("char_" + viewKey)) {
            return catchphrases["char_" + viewKey];
        }
        if (catchphrases.hasOwnProperty(viewKey)) {
            return catchphrases[viewKey];
        }
        return defaultText || viewKey; // Fallback to default text or the key itself
    }

    // Function to get a specific color, with fallback
    function getColor(key, defaultColor) {
        return colors[key] || defaultColor || "magenta"; // Magenta indicates missing color
    }

    // Function to get a specific font object, with fallback
    function getFont(key) { // key e.g. 'body', 'title'
        var defaultFont = { family: "Arial", pixelSize: 14, bold: false };
        var fontSet = fonts[key] || defaultFont;

        // Ensure all parts of a font object are present
        return {
            family: fontSet.family || defaultFont.family,
            pixelSize: fontSet.pixelSize || defaultFont.pixelSize,
            bold: fontSet.bold !== undefined ? fontSet.bold : defaultFont.bold
            // Add other font properties as needed: italic, weight, etc.
        };
    }

    // Function to get a specific style object from theme.styles
    function getStyle(styleKey) { // e.g., 'button_default', 'text_input'
        return styles[styleKey] || {};
    }


    Connections {
        target: backend
        function onThemeChanged(themeName, newThemeData) {
            console.log("ThemeProvider: Theme changed to " + themeName);
            currentTheme = newThemeData;
            // Update exposed properties
            colors = currentTheme.colors || {};
            fonts = currentTheme.fonts || {};
            styles = currentTheme.styles || {};
            paths = currentTheme.paths || {};
            catchphrases = currentTheme.catchphrases || {};
            options = currentTheme.options || {};
            metadata = currentTheme.metadata || {};
        }
        function onSettingChanged(key, value) {
            if (key === "theme_suboptions") {
                 var newOpts = value;
                 // Value from backend.setSetting might already be a JS object/dict if set from QML directly as such
                 // If it were coming from Python as a JSON string, parsing would be needed.
                 // For now, assume 'value' is the correct object or QML handles type conversion.
                 if (typeof value === 'string') {
                    try { newOpts = JSON.parse(value); }
                    catch (e) { console.error("ThemeProvider: Error parsing theme_suboptions JSON", e); return; }
                 }

                 if (typeof newOpts === 'object' && newOpts !== null) {
                    options = newOpts;
                    // Ensure currentTheme.options is also updated if other parts of ThemeProvider rely on it directly
                    // and not just the 'options' property.
                    if (currentTheme && typeof currentTheme === 'object') {
                         currentTheme.options = newOpts;
                    }
                    console.log("ThemeProvider: Theme suboptions updated via onSettingChanged:", JSON.stringify(options));
                 } else {
                    console.warn("ThemeProvider: Received theme_suboptions is not a valid object:", newOpts);
                    // Fallback to current theme's default options if value is invalid
                    if (currentTheme && currentTheme.options) {
                        options = currentTheme.options;
                    } else {
                        options = { use_character_catchphrases: false, show_special_icons: false, enable_animated_background: false };
                    }
                 }
            }
        }
    }

    Component.onCompleted: {
        console.log("ThemeProvider initialized. Current theme name:", backend.getCurrentThemeName());

        // Initialize options from backend config (theme_suboptions) or theme defaults
        var loadedSubOptions = backend.getSetting("theme_suboptions");
        if (loadedSubOptions && typeof loadedSubOptions === 'object') {
            options = loadedSubOptions;
             // Also ensure currentTheme (loaded initially) reflects these persisted suboptions
            if (currentTheme && typeof currentTheme === 'object') {
                currentTheme.options = loadedSubOptions;
            }
        } else if (currentTheme && currentTheme.options) {
            // Fallback to options defined within the current theme data if not in settings
            options = currentTheme.options;
        } else {
            // Absolute fallback if nothing is defined
            options = { use_character_catchphrases: false, show_special_icons: false, enable_animated_background: false };
        }
        console.log("ThemeProvider: Initial effective suboptions:", JSON.stringify(options));
    }
}
