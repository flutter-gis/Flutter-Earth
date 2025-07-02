#!/usr/bin/env python3
"""
Theme JSON to JavaScript Converter for Flutter Earth
Converts themes.json to JavaScript format for the frontend
"""

import json
import os

def js_escape(s):
    return s.replace("'", "\\'") if isinstance(s, str) else s

def convert_themes_json_to_js():
    """Convert themes.json to JavaScript format"""
    
    # Read the themes.json file
    themes_json_path = os.path.join(os.path.dirname(__file__), 'themes.json')
    
    try:
        with open(themes_json_path, 'r', encoding='utf-8') as f:
            themes_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: themes.json not found at {themes_json_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in themes.json: {e}")
        return False
    
    # Create the JavaScript array
    js_code = "// Auto-generated theme definitions\n"
    js_code += "// Generated from themes.json\n\n"
    js_code += "window.availableThemes = [\n"
    
    for i, theme in enumerate(themes_data):
        js_code += "    {\n"
        js_code += f"        name: '{js_escape(theme['name'])}',\n"
        js_code += f"        display_name: '{js_escape(theme['display_name'])}',\n"
        js_code += f"        category: '{js_escape(theme['category'])}',\n"
        js_code += f"        background: '{js_escape(theme['background'])}',\n"
        js_code += f"        primary: '{js_escape(theme['primary'])}',\n"
        js_code += f"        emoji: '{js_escape(theme['emoji'])}',\n"
        js_code += f"        icon: '{js_escape(theme['icon'])}',\n"
        js_code += f"        splashEffect: '{js_escape(theme['splashEffect'])}',\n"
        js_code += f"        uiEffect: '{js_escape(theme['uiEffect'])}',\n"
        js_code += f"        welcomeMessage: '{js_escape(theme['welcomeMessage'])}',\n"
        js_code += f"        splashText: '{js_escape(theme['splashText'])}',\n"
        js_code += f"        notificationMessage: '{js_escape(theme['notificationMessage'])}',\n"
        
        # Add colors object
        js_code += "        colors: {\n"
        color_items = list(theme['colors'].items())
        for j, (color_key, color_value) in enumerate(color_items):
            comma = ',' if j < len(color_items) - 1 else ''
            js_code += f'            "{color_key}": "{js_escape(color_value)}"{comma}\n'
        js_code += "        },\n"
        
        # Add catchphrases object
        js_code += "        catchphrases: {\n"
        phrase_items = list(theme['catchphrases'].items())
        for j, (phrase_key, phrase_value) in enumerate(phrase_items):
            escaped_value = js_escape(phrase_value)
            comma = ',' if j < len(phrase_items) - 1 else ''
            js_code += f'            "{phrase_key}": "{escaped_value}"{comma}\n'
        js_code += "        },\n"
        
        # Add options object
        js_code += "        options: {\n"
        option_items = list(theme['options'].items())
        for j, (option_key, option_value) in enumerate(option_items):
            if isinstance(option_value, bool):
                value_str = str(option_value).lower()
            else:
                value_str = f'"{js_escape(option_value)}"'
            comma = ',' if j < len(option_items) - 1 else ''
            js_code += f'            "{option_key}": {value_str}{comma}\n'
        js_code += "        }\n"
        
        # Close theme object
        if i < len(themes_data) - 1:
            js_code += "    },\n"
        else:
            js_code += "    }\n"
    
    js_code += "];\n"
    
    # Write to generated_themes.js
    output_path = os.path.join(os.path.dirname(__file__), 'generated_themes.js')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_code)
        print(f"✓ Successfully converted {len(themes_data)} themes to {output_path}")
        return True
    except Exception as e:
        print(f"Error writing to {output_path}: {e}")
        return False

if __name__ == "__main__":
    success = convert_themes_json_to_js()
    if success:
        print("Theme conversion completed successfully!")
    else:
        print("Theme conversion failed!")
        exit(1) 