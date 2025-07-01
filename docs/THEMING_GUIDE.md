# Flutter Earth Theming Guide

This guide explains how to create and customize themes for the Flutter Earth application.

## Overview

Flutter Earth features a comprehensive theming system with 30+ unique themes across multiple categories:
- **Professional Themes**: Clean, modern designs for serious work
- **My Little Pony Themes**: Fun, character-inspired themes
- **Minecraft Themes**: Blocky, adventurous designs
- **Pride Themes**: Inclusive themes celebrating diversity
- **Unity Themes**: Special themes promoting global solidarity

## Theme Structure

### Basic Theme Properties
```json
{
  "name": "theme_name",
  "display_name": "Theme Display Name",
  "category": "professional|mlp|minecraft|pride|unity",
  "background": "#color",
  "primary": "#color",
  "emoji": "🎨",
  "icon": "🎨",
  "splashEffect": "effect_name",
  "uiEffect": "ui_effect_name",
  "welcomeMessage": "Welcome message",
  "splashText": "Splash screen text",
  "notificationMessage": "Notification text"
}
```

### Color Definitions
```json
{
  "colors": {
    "background": "#2E2E2E",
    "foreground": "#FFFFFF",
    "primary": "#5A9BD5",
    "secondary": "#7AC043",
    "accent": "#F4B183",
    "error": "#FF5555",
    "success": "#77DD77",
    "text": "#F0F0F0",
    "text_subtle": "#B0B0B0",
    "disabled": "#555555",
    "widget_bg": "#3C3C3C",
    "widget_border": "#505050",
    "text_on_primary": "#FFFFFF",
    "button_bg": "#5A9BD5",
    "button_fg": "#FFFFFF",
    "button_hover_bg": "#7FBCE9",
    "entry_bg": "#252525",
    "entry_fg": "#FFFFFF",
    "entry_border": "#505050",
    "list_bg": "#333333",
    "list_fg": "#FFFFFF",
    "list_selected_bg": "#5A9BD5",
    "list_selected_fg": "#FFFFFF",
    "tooltip_bg": "#333333",
    "tooltip_fg": "#FFFFFF",
    "progressbar_bg": "#555555",
    "progressbar_fg": "#5A9BD5"
  }
}
```

### Catchphrases
```json
{
  "catchphrases": {
    "app_title": "Flutter Earth",
    "view_HomeView": "Home",
    "view_MapView": "Map",
    "view_DownloadView": "Download",
    "view_SatelliteInfoView": "Satellite Info",
    "view_IndexAnalysisView": "Index Analysis",
    "view_VectorDownloadView": "Vector Download",
    "view_DataViewerView": "Data Viewer",
    "view_ProgressView": "Progress",
    "view_SettingsView": "Settings",
    "view_AboutView": "About",
    "view_HomeView_Welcome": "Welcome to Flutter Earth",
    "view_HomeView_WelcomeUser": "Welcome, %1",
    "status_gee_ready": "Earth Engine: Ready",
    "status_gee_not_ready": "Earth Engine: Not Authenticated",
    "action_goto_map": "Go to Map",
    "action_goto_download": "Download Data",
    "action_goto_settings": "Settings",
    "dialog_title_info": "Information",
    "desc_SatelliteInfoView": "Detailed information about satellites and sensors.",
    "header_satellite_category": "Satellite / Category",
    "header_type": "Type",
    "placeholder_select_satellite": "Select a satellite for details.",
    "about_hello_user": "Hello, %1!",
    "about_hello_generic": "Hello!",
    "about_developed_by": "Developed by the Flutter Earth Team & Contributors.",
    "action_visit_website": "Visit Project Website",
    "dialog_title_welcome": "Welcome",
    "prompt_enter_name": "Please enter your name:",
    "placeholder_your_name": "Your name",
    "settings_group_theme": "Appearance",
    "settings_label_theme": "Theme:",
    "settings_label_theme_options": "Theme Options:",
    "settings_opt_catchphrases": "Use Character Catchphrases",
    "settings_opt_icons": "Show Special Icons",
    "settings_opt_animations": "Enable Animated Backgrounds",
    "settings_group_general": "General",
    "settings_label_output_dir": "Output Directory:",
    "settings_group_actions": "Actions",
    "action_reload_settings": "Reload Settings",
    "action_clear_cache": "Clear Cache & Logs",
    "dialog_msg_cleanup_complete": "Cache and logs cleared.",
    "dialog_title_cleanup_complete": "Cleanup Complete",
    "status_no_active_downloads": "No active downloads."
  }
}
```

### Theme Options
```json
{
  "options": {
    "use_character_catchphrases": false,
    "show_special_icons": false,
    "enable_animated_background": false
  }
}
```

## Creating a New Theme

### Step 1: Choose a Category
Select the appropriate category for your theme:
- **professional**: Clean, business-like themes
- **mlp**: My Little Pony character themes
- **minecraft**: Blocky, game-inspired themes
- **pride**: LGBTQ+ pride themes
- **unity**: Global solidarity themes

### Step 2: Define Basic Properties
```json
{
  "name": "my_custom_theme",
  "display_name": "My Custom Theme",
  "category": "professional",
  "background": "#1a1a1a",
  "primary": "#4CAF50",
  "emoji": "🌿",
  "icon": "🌿",
  "splashEffect": "fade",
  "uiEffect": "none",
  "welcomeMessage": "Welcome to My Custom Theme!",
  "splashText": "My Custom Theme",
  "notificationMessage": "My Custom Theme"
}
```

### Step 3: Define Colors
Create a comprehensive color palette:
```json
{
  "colors": {
    "background": "#1a1a1a",
    "foreground": "#ffffff",
    "primary": "#4CAF50",
    "secondary": "#2196F3",
    "accent": "#FF9800",
    "error": "#f44336",
    "success": "#4CAF50",
    "text": "#ffffff",
    "text_subtle": "#b0b0b0",
    "disabled": "#666666",
    "widget_bg": "#2d2d2d",
    "widget_border": "#404040",
    "text_on_primary": "#ffffff",
    "button_bg": "#4CAF50",
    "button_fg": "#ffffff",
    "button_hover_bg": "#66BB6A",
    "entry_bg": "#333333",
    "entry_fg": "#ffffff",
    "entry_border": "#404040",
    "list_bg": "#2d2d2d",
    "list_fg": "#ffffff",
    "list_selected_bg": "#4CAF50",
    "list_selected_fg": "#ffffff",
    "tooltip_bg": "#333333",
    "tooltip_fg": "#ffffff",
    "progressbar_bg": "#404040",
    "progressbar_fg": "#4CAF50"
  }
}
```

### Step 4: Customize Catchphrases
Update text elements to match your theme:
```json
{
  "catchphrases": {
    "app_title": "My Custom Theme",
    "view_HomeView_Welcome": "Welcome to My Custom Theme!",
    "about_developed_by": "Created with love and care.",
    "status_gee_ready": "Earth Engine: Ready to explore!"
  }
}
```

### Step 5: Set Theme Options
Configure theme behavior:
```json
{
  "options": {
    "use_character_catchphrases": false,
    "show_special_icons": true,
    "enable_animated_background": true
  }
}
```

## Special Effects

### Splash Effects
Available splash effects for theme transitions:
- **fade**: Smooth fade transition
- **stars**: Starry night effect
- **sunbeams**: Radiant sun effect
- **magic**: Magical sparkle effect
- **confetti**: Party confetti effect
- **rainbow**: Rainbow trail effect
- **blocky**: Minecraft-style block effect
- **explode**: Explosion effect
- **portal**: Portal effect
- **trans**: Trans flag wave effect

### UI Effects
Available UI effects for interactive elements:
- **none**: No special effects
- **nightGlow**: Night glow effect
- **sunshine**: Sunshine effect
- **magicSparkle**: Magic sparkle effect
- **rainbowTrail**: Rainbow trail effect
- **partyConfetti**: Party confetti effect
- **transWave**: Trans flag wave effect
- **biWave**: Bisexual flag wave effect
- **blockyOverlay**: Minecraft block overlay
- **creeperShake**: Creeper explosion shake

## Theme Categories

### Professional Themes
Clean, modern designs suitable for professional work:
- **Default (Dark)**: Classic dark theme
- **Light**: Clean light theme
- **Sanofi Inspired**: Corporate-inspired design

### My Little Pony Themes
Character-inspired themes with personality:
- **Twilight Sparkle**: Purple, scholarly theme
- **Pinkie Pie**: Pink, party-themed
- **Rainbow Dash**: Rainbow, energetic theme
- **Fluttershy**: Gentle, pastel theme
- **Applejack**: Orange, honest theme
- **Rarity**: Purple, elegant theme
- **Princess Celestia**: Golden, regal theme
- **Princess Luna**: Dark blue, night theme
- **Trixie**: Magenta, showy theme
- **Starlight Glimmer**: Light purple, friendship theme
- **Derpy Hooves**: Gray, muffin-themed
- **Princess Cadence**: Pink, love theme
- **Sunset Shimmer**: Orange, sunset theme

### Minecraft Themes
Blocky, game-inspired themes:
- **Steve**: Classic Minecraft character theme
- **Alex**: Modern Minecraft character theme
- **Enderman**: Dark, mysterious theme
- **Skeleton**: Bone-white, spooky theme
- **Zombie**: Green, undead theme
- **Creeper**: Green, explosive theme

### Pride Themes
Inclusive themes celebrating diversity:
- **WLW Pride**: Lesbian pride theme
- **MLM Pride**: Gay pride theme
- **Nonbinary Pride**: Nonbinary pride theme
- **Genderqueer Pride**: Genderqueer pride theme
- **Pan Pride**: Pansexual pride theme
- **Ace Pride**: Asexual pride theme
- **Aro Pride**: Aromantic pride theme
- **Black Pride**: Black pride theme
- **Unity Pride**: Unity pride theme

## Testing Your Theme

### 1. Add to themes.json
Add your theme definition to `frontend/themes.json`:
```json
[
  // ... existing themes ...
  {
    "name": "my_custom_theme",
    "display_name": "My Custom Theme",
    // ... your theme definition ...
  }
]
```

### 2. Generate JavaScript
Run the theme converter:
```bash
cd frontend
python theme_converter.py
```

### 3. Test in Application
- Open `test_themes.html` to test your theme
- Use `theme_showcase.html` to preview all themes
- Test in the main application

### 4. Validate
Check that your theme:
- [ ] Loads without errors
- [ ] Displays correctly in all views
- [ ] Has proper contrast ratios
- [ ] Works with all UI elements
- [ ] Transitions smoothly

## Best Practices

### Color Selection
- **Contrast**: Ensure sufficient contrast for readability
- **Accessibility**: Consider colorblind users
- **Consistency**: Use consistent color relationships
- **Branding**: Align with character or brand colors

### Text Customization
- **Character Voice**: Match character personality
- **Tone**: Maintain appropriate tone for category
- **Length**: Keep messages concise and clear
- **Placeholders**: Use %1 for dynamic content

### Performance
- **Effects**: Use effects sparingly for performance
- **Animations**: Keep animations smooth and not distracting
- **Loading**: Ensure theme loads quickly

### Accessibility
- **Contrast**: Meet WCAG contrast guidelines
- **Text Size**: Ensure readable text sizes
- **Keyboard Navigation**: Test keyboard accessibility
- **Screen Readers**: Consider screen reader compatibility

## Troubleshooting

### Common Issues
1. **Theme not loading**: Check JSON syntax and file paths
2. **Colors not applying**: Verify color format (#RRGGBB)
3. **Effects not working**: Check effect names and implementation
4. **Text not updating**: Verify catchphrase keys

### Debug Tools
- Browser developer tools for CSS inspection
- Console logging for JavaScript debugging
- Theme testing interface for validation
- Log files for error tracking

## Contributing Themes

### Submission Guidelines
1. **Original Work**: Create original themes or get permission
2. **Quality**: Ensure high quality and polish
3. **Testing**: Thoroughly test before submission
4. **Documentation**: Include theme description and credits

### Review Process
1. **Technical Review**: Check for errors and issues
2. **Design Review**: Evaluate visual quality and consistency
3. **Accessibility Review**: Ensure accessibility compliance
4. **Performance Review**: Verify performance impact

## Conclusion

The Flutter Earth theming system provides extensive customization options while maintaining consistency and accessibility. By following this guide, you can create unique, engaging themes that enhance the user experience while respecting the application's design principles.

### Resources
- [Color Theory Guide](https://www.smashingmagazine.com/2010/02/color-theory-for-designers-part-1-the-meaning-of-color/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Animation Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations)
- [JSON Schema Validation](https://json-schema.org/)

Happy theming! 🌈✨ 