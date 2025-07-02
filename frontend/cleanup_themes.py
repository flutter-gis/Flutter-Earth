#!/usr/bin/env python3
"""
Theme Cleanup Script for Flutter Earth
Removes duplicate themes from themes.json and regenerates JavaScript
"""

import json
import os

def cleanup_themes():
    """Remove duplicate themes from themes.json"""
    
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
    
    print(f"Original themes count: {len(themes_data)}")
    
    # Remove duplicates based on theme name
    seen_names = set()
    unique_themes = []
    
    for theme in themes_data:
        theme_name = theme.get('name', '')
        if theme_name not in seen_names:
            seen_names.add(theme_name)
            unique_themes.append(theme)
        else:
            print(f"Removing duplicate theme: {theme_name}")
    
    print(f"Unique themes count: {len(unique_themes)}")
    print(f"Removed {len(themes_data) - len(unique_themes)} duplicate themes")
    
    # Write back the cleaned themes
    try:
        with open(themes_json_path, 'w', encoding='utf-8') as f:
            json.dump(unique_themes, f, indent=2, ensure_ascii=False)
        print(f"✓ Successfully cleaned themes.json")
        return True
    except Exception as e:
        print(f"Error writing to {themes_json_path}: {e}")
        return False

def regenerate_js():
    """Regenerate the JavaScript themes file"""
    
    # Import the conversion function
    from convert_themes_json_to_js import convert_themes_json_to_js
    
    return convert_themes_json_to_js()

if __name__ == "__main__":
    print("Cleaning up duplicate themes...")
    if cleanup_themes():
        print("Regenerating JavaScript themes file...")
        if regenerate_js():
            print("Theme cleanup and regeneration completed successfully!")
        else:
            print("Theme regeneration failed!")
            exit(1)
    else:
        print("Theme cleanup failed!")
        exit(1) 