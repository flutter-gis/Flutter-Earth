## Theming Guide for Flutter Earth

Flutter Earth features a flexible theming system that allows customization of the application's appearance, including colors, fonts, styles, and even character-specific elements like catchphrases and splash screens.

### Theme Structure

Themes are defined in `flutter_earth_pkg/flutter_earth/config.py` within the `THEMES` dictionary. Each theme is a dictionary identified by a unique internal name (e.g., 'Twilight Sparkle', 'Default (Dark)').

A theme dictionary has the following structure:

```python
'ThemeInternalName': {
    'metadata': {
        'display_name': 'User-Friendly Theme Name', # Shown in settings
        'category': 'Theme Category',             # e.g., 'Professional', 'MLP', 'Minecraft'
        'author': 'Theme Author'
    },
    'colors': { # Defines all color keys used in the QML UI
        'background': '#RRGGBB',
        'foreground': '#RRGGBB',
        'primary': '#RRGGBB',
        'secondary': '#RRGGBB',
        'accent': '#RRGGBB',
        'error': '#RRGGBB',
        'success': '#RRGGBB',
        'text': '#RRGGBB',
        'text_subtle': '#RRGGBB',
        'text_on_primary': '#RRGGBB', # For text on 'primary' colored backgrounds
        'disabled': '#RRGGBB',
        'widget_bg': '#RRGGBB',      # Background for general widgets/dialogs
        'widget_border': '#RRGGBB',
        'button_bg': '#RRGGBB',      # Default button background
        'button_fg': '#RRGGBB',      # Default button text color
        'button_hover_bg': '#RRGGBB',
        'entry_bg': '#RRGGBB',       # Background for TextField, ComboBox, SpinBox
        'entry_fg': '#RRGGBB',       # Text color for entry fields
        'entry_border': '#RRGGBB',
        'list_bg': '#RRGGBB',        # Background for list popups (e.g., ComboBox dropdown)
        'list_fg': '#RRGGBB',        # Text color for list items
        'list_selected_bg': '#RRGGBB',
        'list_selected_fg': '#RRGGBB',
        'tooltip_bg': '#RRGGBB',
        'tooltip_fg': '#RRGGBB',
        'progressbar_bg': '#RRGGBB',
        'progressbar_fg': '#RRGGBB'
    },
    'fonts': { # Defines font families and sizes for different UI text roles
        'body': {'family': 'FontName, Fallback, sans-serif', 'pixelSize': 14, 'bold': False},
        'title': {'family': 'FontName, Fallback, sans-serif', 'pixelSize': 20, 'bold': True},
        'button': {'family': 'FontName, Fallback, sans-serif', 'pixelSize': 13, 'bold': False},
        'monospace': {'family': 'MonospaceFont, Fallback, monospace', 'pixelSize': 13},
        'character_specific': {'family': 'OptionalSpecialFont', 'pixelSize': 14} # For character themes
    },
    'styles': { # Defines more complex styling attributes for specific QML components/groups
        # Keys here reference color keys from the 'colors' section above
        'button_default': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'button_bg', 'borderWidth': 1},
        'button_primary': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 1}, # Example for a primary action button
        'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 3},
        # Styles for specific components like SideBar buttons
        'sidebar_button_color': '#HEXCOLOR_OR_COLORKEY',
        'sidebar_button_text_color': '#HEXCOLOR_OR_COLORKEY',
        # ... etc.
    },
    'paths': { # Paths to theme-specific assets (use qrc:/ for Qt Resource System paths)
        'splash_screen_image': 'qrc:/assets/images/splash_themename.png',
        'window_icon': 'qrc:/assets/icons/app_icon_themename.png'
        # Add paths for particle images, background patterns, etc. as needed
        # e.g., 'particle_sparkle': 'qrc:/assets/particles/sparkle_themename.png'
    },
    'catchphrases': { # Theme-specific text for UI elements. Keys correspond to QML usage.
        'app_title': "App Title for this Theme",
        'view_HomeView': "Home View Title",
        # ... many other keys for different views, dialogs, actions ...
        # For character themes, a 'char_' prefix can be used for sub-option specific versions
        # e.g., 'char_view_HomeView_Welcome': "Twilight's Special Welcome!"
    },
    'options': { # Default state for theme-specific sub-options
        'use_character_catchphrases': False, # Set to True for character themes
        'show_special_icons': False,         # For theme-specific icons in UI
        'enable_animated_background': False  # For particle effects or other animations
    }
}
```

### Adding a New Theme

1.  **Define Theme Data**: In `flutter_earth_pkg/flutter_earth/config.py`, add a new entry to the `THEMES` dictionary. Use an existing theme as a template.
    *   Choose a unique internal name (e.g., `'MyCoolTheme'`).
    *   Fill in all the sections: `metadata`, `colors`, `fonts`, `styles`, `paths`, `catchphrases`, and `options`.
    *   For `paths`, ensure your image assets (splash screen, icon, particle images) are added to the project, preferably via the Qt Resource System (`.qrc` file), and use the correct `qrc:/` paths.
    *   For custom `fonts`, ensure the font files (.ttf, .otf) are bundled with the application and loaded (e.g., using `QFontDatabase.addApplicationFont()` in Python).
2.  **Update Catchphrases**: If your theme uses unique catchphrases (`options.use_character_catchphrases: True`), ensure all relevant keys used in the QML files are present in your theme's `catchphrases` dictionary. Refer to the `ThemeProvider.getCatchphrase()` calls in QML files to see which keys are used.
3.  **Test**: Launch the application, go to Settings -> Appearance, and select your new theme. Verify all UI elements display correctly.

### Customizing QML Components for Theming

QML components access theme properties via the `ThemeProvider` singleton:

-   **Colors**: `Rectangle { color: ThemeProvider.getColor("primary", "blue") }`
-   **Fonts**: `Text { text: "Hello"; font: ThemeProvider.getFont("body") }`
-   **Specific Font Properties**: `Text { text: "Title"; font.family: ThemeProvider.fonts.title.family; font.pixelSize: ThemeProvider.fonts.title.pixelSize }`
-   **Styles**: `Button { background: Rectangle { radius: ThemeProvider.getStyle("button_default").radius } }` (Note: `getStyle` returns the style object; you then access its properties).
-   **Catchphrases**: `Label { text: ThemeProvider.getCatchphrase("view_HomeView", "Default Home Title") }`
-   **Conditional Visibility (e.g., for effects)**: `Item { visible: ThemeProvider.options.enable_animated_background && ThemeProvider.metadata.name === 'MyCoolTheme' }`

When adding new stylable QML components, ensure their visual properties are bound to `ThemeProvider` properties or use new keys defined in the theme structure.

### Theme Sub-Options

The `options` dictionary in a theme definition (`use_character_catchphrases`, `show_special_icons`, `enable_animated_background`) controls optional features.
- These are toggled in the Settings view.
- Their state is saved in the application configuration under the key `"theme_suboptions"`.
- `ThemeProvider.qml` listens for changes to these options and makes them available via `ThemeProvider.options`.
- QML components can check `ThemeProvider.options.optionName` to conditionally enable features.
- The `ThemeProvider.getCatchphrase()` function automatically checks `ThemeProvider.options.use_character_catchphrases` and attempts to use character-specific phrases (e.g., `char_view_HomeView`) before falling back to generic ones.
