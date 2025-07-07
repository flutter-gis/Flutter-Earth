#!/usr/bin/env python3
"""
Theme Converter for Flutter Earth
Converts Python theme definitions to JavaScript format for the frontend
"""

import json
import sys
import os

# Add the flutter_earth_pkg to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'flutter_earth_pkg'))

try:
    from flutter_earth.config import THEMES
except ImportError:
    print("Error: Could not import THEMES from flutter_earth.config")
    sys.exit(1)

def convert_theme_to_js(theme_name, theme_data):
    """Convert a Python theme definition to JavaScript format"""
    
    # Extract colors
    colors = theme_data.get('colors', {})
    background = colors.get('background', '#f0f0f0')
    primary = colors.get('primary', '#e91e63')
    
    # Extract metadata
    metadata = theme_data.get('metadata', {})
    display_name = metadata.get('display_name', theme_name)
    category = metadata.get('category', 'default').lower()
    
    # Extract catchphrases
    catchphrases = theme_data.get('catchphrases', {})
    welcome_message = catchphrases.get('view_HomeView_Welcome', f'Welcome to {display_name}!')
    splash_text = catchphrases.get('app_title', f'{display_name} theme')
    
    # Determine emoji/icon based on theme name and category
    emoji_map = {
        # MLP themes
        'twilight sparkle': '📚',
        'pinkie pie': '🎉',
        'rainbow dash': '🌈',
        'applejack': '🍎',
        'rarity': '💎',
        'fluttershy': '🦋',
        'derpy hooves': '🧁',
        'princess luna': '🌙',
        'princess celestia': '☀️',
        'princess cadence': '💖',
        'sunset shimmer': '🌅',
        'starlight glimmer': '⭐',
        'trixie': '🎩',
        
        # Minecraft themes
        'steve': '🧑‍🌾',
        'alex': '🧑‍🦰',
        'enderman': '👾',
        'skeleton': '💀',
        'zombie': '🧟',
        'creeper': '💣',
        
        # Pride themes
        'wlw pride': '👭',
        'mlm pride': '👬',
        'nonbinary pride': '⚧️',
        'genderqueer pride': '🏳️‍🌈',
        'pan pride': '💖',
        'ace pride': '🖤',
        'aro pride': '💚',
        'black pride': '✊🏿',
        'unity pride': '🤝',
        
        # Professional themes
        'default (dark)': '🌑',
        'light': '🌞',
    }
    
    # Find emoji for this theme
    emoji = None
    for key, value in emoji_map.items():
        if key in theme_name.lower():
            emoji = value
            break
    
    # Default emojis by category
    if not emoji:
        category_emojis = {
            'mlp': '🦄',
            'minecraft': '⛏️',
            'pride': '🏳️‍🌈',
            'professional': '🌍',
            'default': '🌍'
        }
        emoji = category_emojis.get(category, '🌍')
    
    # Determine splash effect based on theme
    splash_effects = {
        'twilight sparkle': 'magic',
        'pinkie pie': 'confetti',
        'rainbow dash': 'rainbow',
        'princess luna': 'stars',
        'princess celestia': 'sunbeams',
        'steve': 'blocky',
        'alex': 'blocky',
        'enderman': 'portal',
        'creeper': 'explode',
        'wlw pride': 'rainbow',
        'mlm pride': 'rainbow',
        'nonbinary pride': 'trans',
        'pan pride': 'rainbow',
        'ace pride': 'stars',
        'aro pride': 'rainbow',
        'black pride': 'fade',
        'unity pride': 'rainbow',
        'default (dark)': 'stars',
        'light': 'sunbeams',
    }
    
    splash_effect = 'fade'
    for key, value in splash_effects.items():
        if key in theme_name.lower():
            splash_effect = value
            break
    
    # Determine UI effect
    ui_effects = {
        'twilight sparkle': 'magicSparkle',
        'pinkie pie': 'partyConfetti',
        'rainbow dash': 'rainbowTrail',
        'princess luna': 'nightGlow',
        'princess celestia': 'sunshine',
        'steve': 'blockyOverlay',
        'alex': 'blockyOverlay',
        'enderman': 'nightGlow',
        'creeper': 'creeperShake',
        'wlw pride': 'rainbowTrail',
        'mlm pride': 'rainbowTrail',
        'nonbinary pride': 'transWave',
        'pan pride': 'rainbowTrail',
        'ace pride': 'nightGlow',
        'aro pride': 'rainbowTrail',
        'black pride': 'nightGlow',
        'unity pride': 'rainbowTrail',
        'default (dark)': 'nightGlow',
        'light': 'sunshine',
    }
    
    ui_effect = 'none'
    for key, value in ui_effects.items():
        if key in theme_name.lower():
            ui_effect = value
            break
    
    # Create JavaScript theme object
    js_theme = {
        'name': theme_name.lower().replace(' ', '_').replace('(', '').replace(')', ''),
        'display_name': display_name,
        'category': category,
        'background': background,
        'primary': primary,
        'emoji': emoji,
        'icon': emoji,
        'splashEffect': splash_effect,
        'uiEffect': ui_effect,
        'welcomeMessage': welcome_message,
        'splashText': splash_text,
        'notificationMessage': splash_text,
        'colors': colors,
        'catchphrases': catchphrases,
        'options': theme_data.get('options', {})
    }
    
    return js_theme

def main():
    """Convert all themes to JavaScript format"""
    
    print("Converting Python themes to JavaScript format...")
    
    js_themes = []
    
    for theme_name, theme_data in THEMES.items():
        try:
            js_theme = convert_theme_to_js(theme_name, theme_data)
            js_themes.append(js_theme)
            print(f"✓ Converted: {theme_name}")
        except Exception as e:
            print(f"✗ Error converting {theme_name}: {e}")
    
    # Create the JavaScript array
    js_code = "// Auto-generated theme definitions\n"
    js_code += "// Generated from Python THEMES dictionary\n\n"
    js_code += "const availableThemes = [\n"
    
    for i, theme in enumerate(js_themes):
        js_code += "    {\n"
        js_code += f"        name: '{theme['name']}',\n"
        js_code += f"        display_name: '{theme['display_name']}',\n"
        js_code += f"        category: '{theme['category']}',\n"
        js_code += f"        background: '{theme['background']}',\n"
        js_code += f"        primary: '{theme['primary']}',\n"
        js_code += f"        emoji: '{theme['emoji']}',\n"
        js_code += f"        icon: '{theme['icon']}',\n"
        js_code += f"        splashEffect: '{theme['splashEffect']}',\n"
        js_code += f"        uiEffect: '{theme['uiEffect']}',\n"
        js_code += f"        welcomeMessage: '{theme['welcomeMessage']}',\n"
        js_code += f"        splashText: '{theme['splashText']}',\n"
        js_code += f"        notificationMessage: '{theme['notificationMessage']}',\n"
        js_code += f"        colors: {json.dumps(theme['colors'], indent=8)},\n"
        js_code += f"        catchphrases: {json.dumps(theme['catchphrases'], indent=8)},\n"
        js_code += f"        options: {json.dumps(theme['options'], indent=8)}\n"
        js_code += "    }"
        if i < len(js_themes) - 1:
            js_code += ","
        js_code += "\n"
    
    js_code += "];\n\n"
    js_code += "// Export for use in other modules\n"
    js_code += "if (typeof module !== 'undefined' && module.exports) {\n"
    js_code += "    module.exports = availableThemes;\n"
    js_code += "}\n"
    
    # Write to generated_themes.js
    output_file = 'generated_themes.js'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"\n✓ Generated {len(js_themes)} themes in {output_file}")
    print(f"✓ Total themes processed: {len(THEMES)}")

if __name__ == "__main__":
    main() 