#!/usr/bin/env python3
"""
Complete Theme Migration Script for Flutter Earth
Converts all themes from themes.json to Python format and adds them to config.py
"""

import json
import re
import os

def convert_json_to_python_dict(theme_dict):
    """Convert JSON dictionary to Python dictionary format"""
    # Convert the dictionary to a string representation
    theme_str = json.dumps(theme_dict, indent=2)
    
    # Replace JSON boolean values with Python boolean values
    theme_str = re.sub(r'\btrue\b', 'True', theme_str)
    theme_str = re.sub(r'\bfalse\b', 'False', theme_str)
    
    # Replace double quotes with single quotes for Python
    theme_str = theme_str.replace('"', "'")
    
    # Handle any special characters that might cause issues
    theme_str = theme_str.replace("\\'", "'")
    
    return theme_str

def migrate_all_themes():
    """Migrate all themes from themes.json to config.py"""
    
    print("Loading themes from themes.json...")
    
    # Load themes from themes.json
    with open('frontend/themes.json', 'r', encoding='utf-8') as f:
        themes_json = json.load(f)
    
    print(f"Found {len(themes_json)} themes in themes.json")
    
    # Load current config.py
    with open('flutter_earth_pkg/flutter_earth/config.py', 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Find existing themes in config.py
    existing_themes = []
    for theme in themes_json:
        theme_name = theme['display_name']
        if f"'{theme_name}':" in config_content:
            existing_themes.append(theme_name)
    
    print(f"Found {len(existing_themes)} existing themes in config.py")
    
    # Find themes that need to be added
    new_themes = []
    for theme in themes_json:
        theme_name = theme['display_name']
        if theme_name not in existing_themes:
            new_themes.append(theme)
    
    print(f"Found {len(new_themes)} new themes to add")
    
    if not new_themes:
        print("No new themes to add!")
        return
    
    # Convert themes to Python format
    python_themes = []
    for theme in new_themes:
        print(f"Converting theme: {theme['display_name']}")
        
        # Convert the theme to Python format
        python_theme_str = convert_json_to_python_dict(theme)
        
        # Create the theme entry for config.py
        theme_entry = f"    '{theme['display_name']}': {python_theme_str}"
        python_themes.append(theme_entry)
    
    # Find where to insert the new themes (before the closing brace of THEMES)
    lines = config_content.split('\n')
    insert_index = None
    
    for i, line in enumerate(lines):
        if line.strip() == '}':
            # Check if this is the end of THEMES dictionary
            # Look for the pattern where we have a closing brace followed by something that's not a theme
            if i > 0 and lines[i-1].strip().endswith(','):
                insert_index = i
                break
    
    if insert_index is None:
        print("Could not find where to insert themes!")
        return
    
    # Insert the new themes
    new_lines = lines[:insert_index] + python_themes + lines[insert_index:]
    
    # Write back to config.py
    with open('flutter_earth_pkg/flutter_earth/config.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Successfully added {len(new_themes)} themes to config.py")
    
    # List the new themes
    for theme in new_themes:
        print(f"  - {theme['display_name']} ({theme['category']})")

if __name__ == "__main__":
    migrate_all_themes() 