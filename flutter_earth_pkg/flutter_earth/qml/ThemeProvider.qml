import QtQuick 2.15

pragma Singleton

QtObject {
    id: themeProvider

    // Properties to hold the current theme data
    // Initialize with default values and update when backend is available
    property var currentTheme: ({}) // Start with empty object
    property var colors: ({})
    property var fonts: ({})
    property var styles: ({})
    property var paths: ({})
    property var catchphrases: ({})
    property var options: ({})
    property var metadata: ({})

    function updateThemeData() {
        try {
            if (typeof backend !== 'undefined' && backend.getCurrentThemeData) {
                currentTheme = backend.getCurrentThemeData() || {};
                colors = currentTheme.colors || {};
                fonts = currentTheme.fonts || {};
                styles = currentTheme.styles || {};
                paths = currentTheme.paths || {};
                catchphrases = currentTheme.catchphrases || {};
                metadata = currentTheme.metadata || {};
                
                // Initialize options from backend config (theme_suboptions) or theme defaults
                var loadedSubOptions = backend.getSetting("theme_suboptions");
                if (loadedSubOptions && typeof loadedSubOptions === 'object') {
                    options = loadedSubOptions;
                    // Also ensure currentTheme reflects these persisted suboptions
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
                console.log("ThemeProvider: Theme data updated successfully");
            } else {
                console.log("ThemeProvider: Backend not available yet");
            }
        } catch (e) {
            console.error("ThemeProvider: Error updating theme data:", e);
            // Set fallback values
            setFallbackValues();
        }
    }

    function setFallbackValues() {
        colors = {
            "primary": "#f8bbd0",
            "background": "#fff3e0", 
            "text": "#212121",
            "text_subtle": "#757575",
            "widget_bg": "#ffffff",
            "widget_border": "#e0e0e0",
            "button_bg": "#f5f5f5",
            "button_fg": "#ffffff",
            "text_on_primary": "#ffffff",
            "accent": "#e65100",
            "success": "#388e3c",
            "error": "#b71c1c"
        };
        fonts = {
            "title": { family: "Arial", pixelSize: 24, bold: true },
            "body": { family: "Arial", pixelSize: 14, bold: false },
            "button": { family: "Arial", pixelSize: 14, bold: true }
        };
        styles = {
            "button_default": { backgroundColorKey: "button_bg", textColorKey: "text", borderColorKey: "widget_border", radius: 8, borderWidth: 1 },
            "text_input": { backgroundColorKey: "widget_bg", textColorKey: "text", borderColorKey: "widget_border", radius: 6 }
        };
        catchphrases = {
            "view_SettingsView": "Settings",
            "settings_group_theme": "Appearance",
            "settings_group_general": "General",
            "settings_group_actions": "Actions",
            "settings_label_theme_options": "Theme Options:",
            "settings_opt_catchphrases": "Use Character Catchphrases",
            "settings_opt_icons": "Show Special Icons", 
            "settings_opt_animations": "Enable Animated Backgrounds",
            "settings_label_output_dir": "Output Directory:",
            "action_reload_settings": "Reload Settings",
            "action_clear_cache": "Clear Cache and Logs",
            "dialog_title_cleanup_complete": "Cleanup Complete",
            "dialog_msg_cleanup_complete": "All cache and log files have been cleared."
        };
        options = { use_character_catchphrases: false, show_special_icons: false, enable_animated_background: false };
        metadata = { name: "Default", category: "Default" };
    }

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

    Component.onCompleted: {
        console.log("ThemeProvider initialized");
        // Set fallback values initially
        setFallbackValues();
        // Try to update with backend data
        updateThemeData();
    }
}
