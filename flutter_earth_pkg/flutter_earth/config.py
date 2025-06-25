"""Configuration management for Flutter Earth."""
import os
import json
import logging
from typing import Any, Dict, Optional, List, Union, Literal
from pathlib import Path
import copy
from dataclasses import fields
from PySide6.QtCore import QObject, Signal

from .types import AppConfig, Environment, SatelliteDetails, ValidationRule
from .errors import ConfigurationError

# Environment types
Environment = Literal['development', 'production', 'test']

# Configuration validation rules
CONFIG_RULES: Dict[str, ValidationRule] = {
    'output_dir': ValidationRule(type=str, required=True),
    'tile_size': ValidationRule(type=float, required=True, min_value=0.1, max_value=5.0),
    'max_workers': ValidationRule(type=int, required=True, min_value=1, max_value=16),
    'cloud_mask': ValidationRule(type=bool, required=True),
    'max_cloud_cover': ValidationRule(type=(int, float), required=True, min_value=0, max_value=100),
    'sensor_priority': ValidationRule(type=list, required=False),
    'recent_directories': ValidationRule(type=list, required=True),
    'theme': ValidationRule(type=str, required=True),
    'theme_suboptions': ValidationRule(type=dict, required=False)
}

# Theme definitions
# New expanded theme structure
THEMES = {
    'Default (Dark)': {
        'metadata': {'display_name': 'Default (Dark)', 'category': 'Professional', 'author': 'Flutter Earth Team'},
        'colors': {
            'background': '#2E2E2E',
            'foreground': '#FFFFFF',
            'primary': '#5A9BD5',
            'secondary': '#7AC043',
            'accent': '#F4B183',
            'error': '#FF5555',
            'success': '#77DD77', # Adjusted success color
            'text': '#F0F0F0',
            'text_subtle': '#B0B0B0',
            'disabled': '#555555',
            'widget_bg': '#3C3C3C',
            'widget_border': '#505050',
            'text_on_primary': '#FFFFFF', # New
            'button_bg': '#5A9BD5',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#7FBCE9',
            'entry_bg': '#252525',
            'entry_fg': '#FFFFFF',
            'entry_border': '#505050',
            'list_bg': '#333333',
            'list_fg': '#FFFFFF',
            'list_selected_bg': '#5A9BD5',
            'list_selected_fg': '#FFFFFF',
            'tooltip_bg': '#333333', # Dark tooltip
            'tooltip_fg': '#FFFFFF', # Light text on dark tooltip
            'progressbar_bg': '#555555',
            'progressbar_fg': '#5A9BD5',
        },
        'fonts': {
            'body': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13}
        },
        'styles': {
            'button_default': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'button_bg', 'borderWidth': 1},
            'button_primary': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 3},
            'sidebar_button_color': '#FFFFFF',
            'sidebar_button_text_color': '#880e4f',
            'sidebar_button_hover_color': '#f8bbd0',
            'sidebar_button_pressed_color': '#f06292',
            'sidebar_button_border_color': '#e91e63',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_default_dark.png',
            'window_icon': 'qrc:/assets/icons/app_icon_dark.png'
        },
        'catchphrases': {
            'app_title': "Flutter Earth",
            'view_HomeView': "Home",
            'view_MapView': "Map",
            'view_DownloadView': "Download",
            'view_SatelliteInfoView': "Satellite Info",
            'view_IndexAnalysisView': "Index Analysis",
            'view_VectorDownloadView': "Vector Download",
            'view_DataViewerView': "Data Viewer",
            'view_ProgressView': "Progress",
            'view_SettingsView': "Settings",
            'view_AboutView': "About",
            'view_HomeView_Welcome': "Welcome to Flutter Earth",
            'view_HomeView_WelcomeUser': "Welcome, %1",
            'status_gee_ready': "Earth Engine: Ready",
            'status_gee_not_ready': "Earth Engine: Not Authenticated",
            'action_goto_map': "Go to Map",
            'action_goto_download': "Download Data",
            'action_goto_settings': "Settings",
            'dialog_title_info': "Information",
            'desc_SatelliteInfoView': "Detailed information about satellites and sensors.",
            'header_satellite_category': "Satellite / Category",
            'header_type': "Type",
            'placeholder_select_satellite': "Select a satellite for details.",
            'about_hello_user': "Hello, %1!",
            'about_hello_generic': "Hello!",
            'about_developed_by': "Developed by the Flutter Earth Team & Contributors.",
            'action_visit_website': "Visit Project Website",
            'dialog_title_welcome': "Welcome",
            'prompt_enter_name': "Please enter your name:",
            'placeholder_your_name': "Your name",
            'settings_group_theme': "Appearance",
            'settings_label_theme': "Theme:",
            'settings_label_theme_options': "Theme Options:",
            'settings_opt_catchphrases': "Use Character Catchphrases",
            'settings_opt_icons': "Show Special Icons",
            'settings_opt_animations': "Enable Animated Backgrounds",
            'settings_group_general': "General",
            'settings_label_output_dir': "Output Directory:",
            'settings_group_actions': "Actions",
            'action_reload_settings': "Reload Settings",
            'action_clear_cache': "Clear Cache & Logs",
            'dialog_msg_cleanup_complete': "Cache and logs cleared.",
            'dialog_title_cleanup_complete': "Cleanup Complete",
            'status_no_active_downloads': "No active downloads."
        },
        'options': {
            'use_character_catchphrases': False,
            'show_special_icons': False,
            'enable_animated_background': False
        }
    },
    'Light': {
        'metadata': {'display_name': 'Light', 'category': 'Professional', 'author': 'Flutter Earth Team'},
        'colors': {
            'background': '#F0F0F0',
            'foreground': '#000000',
            'primary': '#0078D7',
            'secondary': '#107C10',
            'accent': '#D83B01',
            'error': '#E81123',
            'success': '#107C10',
            'text': '#201F1E',
            'text_subtle': '#605E5C',
            'disabled': '#A19F9D',
            'widget_bg': '#FFFFFF',
            'widget_border': '#C8C6C4',
            'button_bg': '#0078D7',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#2B88D8',
            'entry_bg': '#FFFFFF',
            'entry_fg': '#000000',
            'entry_border': '#8A8886',
            'list_bg': '#FFFFFF',
            'list_fg': '#000000',
            'list_selected_bg': '#0078D7',
            'list_selected_fg': '#FFFFFF',
            'tooltip_bg': '#333333',
            'tooltip_fg': '#FFFFFF',
            'progressbar_bg': '#C8C6C4',
            'progressbar_fg': '#0078D7',
        },
        'fonts': { # Similar to Default (Dark) but could be adjusted
            'body': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13}
        },
        'styles': {
            'button_default': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'button_bg', 'borderWidth': 1},
            'button_primary': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 3},
            'sidebar_button_color': '#E0E0E0',
            'sidebar_button_text_color': '#004C8C',
            'sidebar_button_hover_color': '#B3E5FC',
            'sidebar_button_pressed_color': '#81D4FA',
            'sidebar_button_border_color': '#0078D7',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_default_light.png',
            'window_icon': 'qrc:/assets/icons/app_icon_light.png'
        },
        'catchphrases': {
            'app_title': "Flutter Earth",
            'view_HomeView': "Home",
            'view_MapView': "Map",
            'view_DownloadView': "Download",
            'view_SatelliteInfoView': "Satellite Info",
            'view_IndexAnalysisView': "Index Analysis",
            'view_VectorDownloadView': "Vector Download",
            'view_DataViewerView': "Data Viewer",
            'view_ProgressView': "Progress",
            'view_SettingsView': "Settings",
            'view_AboutView': "About",
            'view_HomeView_Welcome': "Welcome to Flutter Earth",
            'view_HomeView_WelcomeUser': "Welcome, %1",
            'status_gee_ready': "Earth Engine: Ready",
            'status_gee_not_ready': "Earth Engine: Not Authenticated",
            'action_goto_map': "Go to Map",
            'action_goto_download': "Download Data",
            'action_goto_settings': "Settings",
            'dialog_title_info': "Information",
            'desc_SatelliteInfoView': "Detailed information about satellites and sensors.",
            'header_satellite_category': "Satellite / Category",
            'header_type': "Type",
            'placeholder_select_satellite': "Select a satellite for details.",
            'about_hello_user': "Hello, %1!",
            'about_hello_generic': "Hello!",
            'about_developed_by': "Developed by the Flutter Earth Team & Contributors.",
            'action_visit_website': "Visit Project Website",
            'dialog_title_welcome': "Welcome",
            'prompt_enter_name': "Please enter your name:",
            'placeholder_your_name': "Your name",
            'settings_group_theme': "Appearance",
            'settings_label_theme': "Theme:",
            'settings_label_theme_options': "Theme Options:",
            'settings_opt_catchphrases': "Use Character Catchphrases",
            'settings_opt_icons': "Show Special Icons",
            'settings_opt_animations': "Enable Animated Backgrounds",
            'settings_group_general': "General",
            'settings_label_output_dir': "Output Directory:",
            'settings_group_actions': "Actions",
            'action_reload_settings': "Reload Settings",
            'action_clear_cache': "Clear Cache & Logs",
            'dialog_msg_cleanup_complete': "Cache and logs cleared.",
            'dialog_title_cleanup_complete': "Cleanup Complete",
            'status_no_active_downloads': "No active downloads."
        },
        'options': {
            'use_character_catchphrases': False,
            'show_special_icons': False,
            'enable_animated_background': False
        }
    },
    'Sanofi': { # Example corporate theme
        'metadata': {'display_name': 'Sanofi Inspired', 'category': 'Corporate', 'author': 'Flutter Earth Team'},
        'colors': {
            'background': '#FFFFFF',
            'foreground': '#000000',
            'primary': '#0064B4',
            'secondary': '#9B9B9B',
            'accent': '#E10098',
            'error': '#D83B01',
            'success': '#107C10',
            'text': '#333333',
            'text_subtle': '#666666',
            'disabled': '#CCCCCC',
            'widget_bg': '#F8F8F8',
            'widget_border': '#DCDCDC',
            'button_bg': '#0064B4',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#0078D7',
            'entry_bg': '#FFFFFF',
            'entry_fg': '#000000',
            'entry_border': '#9B9B9B',
            'list_bg': '#FFFFFF',
            'list_fg': '#000000',
            'list_selected_bg': '#0064B4',
            'list_selected_fg': '#FFFFFF',
            'tooltip_bg': '#FFFFE0',
            'tooltip_fg': '#000000',
            'progressbar_bg': '#DCDCDC',
            'progressbar_fg': '#0064B4',
        },
        'fonts': {
            'body': {'family': 'Helvetica Neue, Helvetica, Arial, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Helvetica Neue, Helvetica, Arial, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Helvetica Neue, Helvetica, Arial, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13}
        },
         'styles': { # Styles would be adjusted to match corporate branding
            'button_default': {'radius': 3, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'button_bg', 'borderWidth': 0},
            'button_primary': {'radius': 3, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 0},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 2},
            'sidebar_button_color': '#F0F4F7',
            'sidebar_button_text_color': '#003F72',
            'sidebar_button_hover_color': '#D6E0E7',
            'sidebar_button_pressed_color': '#B8C7D1',
            'sidebar_button_border_color': '#0064B4',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_sanofi.png',
            'window_icon': 'qrc:/assets/icons/app_icon_sanofi.png'
        },
        'catchphrases': {
            'app_title': "Flutter Earth Platform", # Adjusted for corporate feel
            'view_HomeView': "Dashboard",
            'view_MapView': "Geo-Platform",
            'view_DownloadView': "Data Ingestion",
            'view_SatelliteInfoView': "Asset Information",
            'view_IndexAnalysisView': "Spectral Analytics",
            'view_VectorDownloadView': "Vector Services",
            'view_DataViewerView': "Visualization Suite",
            'view_ProgressView': "Task Monitor",
            'view_SettingsView': "Configuration",
            'view_AboutView': "Platform Details",
            'view_HomeView_Welcome': "Welcome to the Platform",
            'view_HomeView_WelcomeUser': "Welcome, %1",
            'status_gee_ready': "Earth Engine: Online",
            'status_gee_not_ready': "Earth Engine: Authentication Required",
            'action_goto_map': "Access Geo-Platform",
            'action_goto_download': "Initiate Data Ingestion",
            'action_goto_settings': "Configure System",
            'dialog_title_info': "System Notification",
            'desc_SatelliteInfoView': "Review satellite asset specifications and capabilities.",
            'header_satellite_category': "Asset Group / Name",
            'header_type': "Asset Class",
            'placeholder_select_satellite': "Select asset for detailed information.",
            'about_hello_user': "Greetings, %1.",
            'about_hello_generic': "Greetings.",
            'about_developed_by': "Enterprise Solution by Flutter Earth Team.",
            'action_visit_website': "Visit Corporate Portal",
            'dialog_title_welcome': "System Access",
            'prompt_enter_name': "Please identify yourself:",
            'placeholder_your_name': "User ID",
            'settings_group_theme': "Interface Branding",
            'settings_label_theme': "Skin:",
            'settings_label_theme_options': "Branding Options:",
            'settings_opt_catchphrases': "Use Corporate Terminology", # Usually False for corporate
            'settings_opt_icons': "Display Standard Icons",
            'settings_opt_animations': "Enable UI Transitions",
            'settings_group_general': "Operational Settings",
            'settings_label_output_dir': "Default Storage Path:",
            'settings_group_actions': "System Maintenance",
            'action_reload_settings': "Refresh Configuration",
            'action_clear_cache': "Purge Temporary Data",
            'dialog_msg_cleanup_complete': "Temporary data purged successfully.",
            'dialog_title_cleanup_complete': "Maintenance Operation Complete",
            'status_no_active_downloads': "No active data operations."
        },
        'options': {
            'use_character_catchphrases': False, # Typically false for corporate
            'show_special_icons': False,
            'enable_animated_background': False
        }
    },
    # MLP Themes Start Here
    'Twilight Sparkle': {
        'metadata': {'display_name': 'Twilight Sparkle', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#2c1a4d', # Deep Indigo
            'foreground': '#f0e4ff', # Pale Lavender
            'primary': '#6c4a8e',    # Medium Purple
            'secondary': '#f04e98',  # Bright Pink (cutie mark)
            'accent': '#f8c5f8',     # Light Pink (magic aura)
            'error': '#ff6666',
            'success': '#90ee90',
            'text': '#f0e4ff',
            'text_subtle': '#d1c4e9',
            'disabled': '#7e57c2', # Muted purple
            'widget_bg': '#3e2763',  # Darker Indigo
            'widget_border': '#6c4a8e',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#6c4a8e',
            'button_fg': '#f0e4ff',
            'button_hover_bg': '#8a6aaa',
            'entry_bg': '#352055',
            'entry_fg': '#f0e4ff',
            'entry_border': '#6c4a8e',
            'list_bg': '#3e2763',
            'list_fg': '#f0e4ff',
            'list_selected_bg': '#f04e98', # Pink for selection
            'list_selected_fg': '#2c1a4d',
            'tooltip_bg': '#4a3075',
            'tooltip_fg': '#f0e4ff',
            'progressbar_bg': '#3e2763',
            'progressbar_fg': '#f04e98', # Pink progress
        },
        'fonts': {
            'body': {'family': 'Georgia, serif', 'pixelSize': 14}, # Elegant, bookish
            'title': {'family': 'Georgia, serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14 } # Or a custom "magic" font
        },
        'styles': {
            'button_default': {'radius': 5, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'button_primary': {'radius': 5, 'textColorKey': 'button_fg', 'backgroundColorKey': 'secondary', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 4},
            'sidebar_button_color': '#3e2763',
            'sidebar_button_text_color': '#f0e4ff',
            'sidebar_button_hover_color': '#6c4a8e',
            'sidebar_button_pressed_color': '#f04e98',
            'sidebar_button_border_color': '#f04e98',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_twilight.png', # Placeholder
            'window_icon': 'qrc:/assets/icons/app_icon_twilight.png'    # Placeholder
        },
        'catchphrases': {
            'app_title': "Twilight's Flutter Earth Study",
            'view_HomeView_Welcome': "Greetings, Everypony!",
            'view_HomeView_WelcomeUser': "Salutations, %1! Ready for some research?",
            'status_gee_ready': "Earth Engine: All systems nominal!",
            'status_gee_not_ready': "Earth Engine: Needs more magic (authentication)!",
            'view_DownloadView': "Organize Data Acquisition Spell",
            'action_goto_map': "To the Map of Equestria!",
            'action_goto_download': "Prepare Download Incantation",
            'action_goto_settings': "Adjust Arcane Settings",
            'dialog_title_info': "A Magical Missive!",
            'view_MapView': "Cartography Console",
            'view_SatelliteInfoView': "Celestial Body Compendium",
            'view_IndexAnalysisView': "Advanced Potion... I mean, Index Analysis!",
            'view_VectorDownloadView': "Geographic Data Teleportation",
            'view_DataViewerView': "Crystal Scrying Orb (Data Viewer)",
            'view_ProgressView': "Current Spell Progress",
            'view_SettingsView': "Scroll of Configuration",
            'view_AboutView': "Codex of Flutter Earth",
            'desc_SatelliteInfoView': "Peruse the scrolls detailing various orbital constructs and their observation capabilities.",
            'header_satellite_category': "Constellation / Archive",
            'header_type': "Orbital Class",
            'placeholder_select_satellite': "Select a celestial body from the archives.",
            'settings_group_theme': "Library Ambiance",
            'settings_label_theme': "Choose Scroll:",
            'settings_label_theme_options': "Enchantment Options:",
            'settings_opt_catchphrases': "Use Twilight's Terminology",
            'settings_opt_icons': "Display Magical Glyphs",
            'settings_opt_animations': "Activate Spell Effects",
        },
        'options': { # Default sub-options for this theme
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True # e.g. subtle magic sparkles
        }
    },
    'Pinkie Pie': {
        'metadata': {'display_name': 'Pinkie Pie', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': { # Bright pinks, yellows, light blues
            'background': '#ffe6f2', # Very Light Pink
            'foreground': '#8c0038', # Dark Pink
            'primary': '#ff80c0',    # Bright Pink
            'secondary': '#ffff80',  # Bright Yellow (balloons)
            'accent': '#80d4ff',     # Light Blue (balloons)
            'error': '#ff6666',
            'success': '#90ee90',
            'text': '#8c0038',
            'text_subtle': '#c06080',
            'disabled': '#ffc0e0',
            'widget_bg': '#fff0f7',
            'widget_border': '#ff80c0',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#ff80c0',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#ffaccf',
            'entry_bg': '#FFFFFF',
            'entry_fg': '#8c0038',
            'entry_border': '#ff80c0',
            'list_bg': '#fff0f7',
            'list_fg': '#8c0038',
            'list_selected_bg': '#ffff80', # Yellow for selection
            'list_selected_fg': '#8c0038',
            'tooltip_bg': '#ffc0e0',
            'tooltip_fg': '#8c0038',
            'progressbar_bg': '#ffc0e0',
            'progressbar_fg': '#ff80c0',
        },
        'fonts': { # Fun, rounded
            'body': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14 }
        },
        'styles': { # Bubbly, rounded
            'button_default': {'radius': 15, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'button_primary': {'radius': 15, 'textColorKey': 'button_fg', 'backgroundColorKey': 'secondary', 'hoverColorKey': 'primary', 'borderColorKey': 'accent', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 10},
            'sidebar_button_color': '#fff0f7',
            'sidebar_button_text_color': '#8c0038',
            'sidebar_button_hover_color': '#ffc0e0',
            'sidebar_button_pressed_color': '#ff80c0',
            'sidebar_button_border_color': '#ffff80',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_pinkiepie.png',
            'window_icon': 'qrc:/assets/icons/app_icon_pinkiepie.png'
        },
        'catchphrases': {
            'app_title': "Pinkie Pie's Super Duper Party App!",
            'view_HomeView_Welcome': "Okie Dokie Lokie!",
            'view_HomeView_WelcomeUser': "Hiya %1! Let's get this party STARTED!",
            'status_gee_ready': "Earth Engine: Ready for FUN FUN FUN!",
            'status_gee_not_ready': "Earth Engine: Aww, it's a bit sleepy!",
            'view_DownloadView': "Let's Bake Some Data!",
            'action_goto_map': "Explore the Party Zone!",
            'action_goto_download': "Grab the Goodies!",
            'action_goto_settings': "Party Settings!",
            'dialog_title_info': "Listen to Pinkie!",
            'view_MapView': "Party Planning Map",
            'view_SatelliteInfoView': "Balloon... Uh, Satellite Guide!",
            'view_IndexAnalysisView': "Super-Duper Calculations!",
            'view_VectorDownloadView': "Confetti... I mean, Vector Grabber!",
            'view_DataViewerView': "Giggle- melihat Data Viewer!",
            'view_ProgressView': "Party Progress Meter!",
            'view_SettingsView': "Party Cannon Controls!",
            'view_AboutView': "The Story of the Best App EVER!",
            'settings_opt_catchphrases': "Use Pinkie's Phrases",
            'settings_opt_icons': "Show Balloon Icons",
            'settings_opt_animations': "Activate Confetti Effects",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True # e.g. bouncing balloons, confetti
        }
    },
    'Fluttershy': {
        'metadata': {'display_name': 'Fluttershy', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': { # Soft pinks, yellows, light greens
            'background': '#f3e5f5', # Very light pink
            'foreground': '#2e2e2e',
            'primary': '#ffb3d9',    # Soft pink
            'secondary': '#fff2cc',  # Light yellow
            'accent': '#b3e5fc',     # Light blue
            'error': '#ffcdd2',      # Soft red
            'success': '#c8e6c9',    # Soft green
            'text': '#2e2e2e',
            'text_subtle': '#666666',
            'disabled': '#cccccc',
            'widget_bg': '#ffffff',
            'widget_border': '#e1bee7', # Light purple border
            'text_on_primary': '#2e2e2e',
            'button_bg': '#ffb3d9',
            'button_fg': '#2e2e2e',
            'button_hover_bg': '#ffcce6',
            'entry_bg': '#ffffff',
            'entry_fg': '#2e2e2e',
            'entry_border': '#e1bee7',
            'list_bg': '#ffffff',
            'list_fg': '#2e2e2e',
            'list_selected_bg': '#ffb3d9',
            'list_selected_fg': '#2e2e2e',
            'tooltip_bg': '#f3e5f5',
            'tooltip_fg': '#2e2e2e',
            'progressbar_bg': '#f3e5f5',
            'progressbar_fg': '#ffb3d9',
        },
        'fonts': { # Gentle, soft
            'body': {'family': 'Georgia, serif', 'pixelSize': 14},
            'title': {'family': 'Georgia, serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14 }
        },
        'styles': { # Soft, rounded
            'button_default': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 6},
            'sidebar_button_color': '#ffffff',
            'sidebar_button_text_color': '#ffb3d9',
            'sidebar_button_hover_color': '#f3e5f5',
            'sidebar_button_pressed_color': '#ffb3d9',
            'sidebar_button_border_color': '#e1bee7',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_fluttershy.png',
            'window_icon': 'qrc:/assets/icons/app_icon_fluttershy.png'
        },
        'catchphrases': {
            'app_title': "Fluttershy's Gentle Earth Explorer",
            'view_HomeView_Welcome': "Oh, hello there...",
            'view_HomeView_WelcomeUser': "Welcome, %1... if that's okay with you...",
            'status_gee_ready': "Earth Engine: Ready... I think...",
            'status_gee_not_ready': "Earth Engine: Needs authentication... um...",
            'view_DownloadView': "Download Data... quietly...",
            'action_goto_map': "Look at the Map...",
            'action_goto_download': "Get Some Data...",
            'action_goto_settings': "Settings... if you want...",
            'dialog_title_info': "Information...",
            'view_MapView': "The Map View...",
            'view_SatelliteInfoView': "Satellite Information...",
            'view_IndexAnalysisView': "Index Analysis...",
            'view_VectorDownloadView': "Vector Download...",
            'view_DataViewerView': "Data Viewer...",
            'view_ProgressView': "Progress...",
            'view_SettingsView': "Settings...",
            'view_AboutView': "About...",
            'settings_opt_catchphrases': "Use Gentle Speech",
            'settings_opt_icons': "Show Soft Icons",
            'settings_opt_animations': "Enable Gentle Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': False
        }
    },
    'Rainbow Dash': {
        'metadata': {'display_name': 'Rainbow Dash', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': { # Blues, cyans, bright colors
            'background': '#e3f2fd', # Light blue
            'foreground': '#1a237e',
            'primary': '#2196f3',    # Blue
            'secondary': '#00bcd4',  # Cyan
            'accent': '#ff5722',     # Orange
            'error': '#f44336',      # Red
            'success': '#4caf50',    # Green
            'text': '#1a237e',
            'text_subtle': '#3949ab',
            'disabled': '#9fa8da',
            'widget_bg': '#ffffff',
            'widget_border': '#2196f3',
            'text_on_primary': '#ffffff',
            'button_bg': '#2196f3',
            'button_fg': '#ffffff',
            'button_hover_bg': '#1976d2',
            'entry_bg': '#ffffff',
            'entry_fg': '#1a237e',
            'entry_border': '#2196f3',
            'list_bg': '#ffffff',
            'list_fg': '#1a237e',
            'list_selected_bg': '#2196f3',
            'list_selected_fg': '#ffffff',
            'tooltip_bg': '#e3f2fd',
            'tooltip_fg': '#1a237e',
            'progressbar_bg': '#e3f2fd',
            'progressbar_fg': '#2196f3',
        },
        'fonts': { # Bold, energetic
            'body': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14, 'bold': True},
            'title': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14, 'bold': True }
        },
        'styles': { # Sharp, angular
            'button_default': {'radius': 2, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 2, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 2},
            'sidebar_button_color': '#ffffff',
            'sidebar_button_text_color': '#2196f3',
            'sidebar_button_hover_color': '#e3f2fd',
            'sidebar_button_pressed_color': '#2196f3',
            'sidebar_button_border_color': '#2196f3',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_rainbowdash.png',
            'window_icon': 'qrc:/assets/icons/app_icon_rainbowdash.png'
        },
        'catchphrases': {
            'app_title': "Rainbow Dash's Awesome Earth Explorer",
            'view_HomeView_Welcome': "Hey there!",
            'view_HomeView_WelcomeUser': "What's up, %1?",
            'status_gee_ready': "Earth Engine: AWESOME!",
            'status_gee_not_ready': "Earth Engine: Needs authentication...",
            'view_DownloadView': "Download Data - 20% Cooler!",
            'action_goto_map': "Check Out the Map!",
            'action_goto_download': "Get Some Data!",
            'action_goto_settings': "Settings!",
            'dialog_title_info': "Info!",
            'view_MapView': "The Map!",
            'view_SatelliteInfoView': "Satellite Info!",
            'view_IndexAnalysisView': "Index Analysis!",
            'view_VectorDownloadView': "Vector Download!",
            'view_DataViewerView': "Data Viewer!",
            'view_ProgressView': "Progress!",
            'view_SettingsView': "Settings!",
            'view_AboutView': "About!",
            'settings_opt_catchphrases': "Use Awesome Speech",
            'settings_opt_icons': "Show Cool Icons",
            'settings_opt_animations': "Enable Awesome Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Applejack': {
        'metadata': {'display_name': 'Applejack', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': { # Oranges, browns, greens
            'background': '#fff3e0', # Light orange
            'foreground': '#3e2723',
            'primary': '#ff9800',    # Orange
            'secondary': '#8bc34a',  # Green
            'accent': '#795548',     # Brown
            'error': '#f44336',      # Red
            'success': '#4caf50',    # Green
            'text': '#3e2723',
            'text_subtle': '#5d4037',
            'disabled': '#bcaaa4',
            'widget_bg': '#ffffff',
            'widget_border': '#ff9800',
            'text_on_primary': '#ffffff',
            'button_bg': '#ff9800',
            'button_fg': '#ffffff',
            'button_hover_bg': '#f57c00',
            'entry_bg': '#ffffff',
            'entry_fg': '#3e2723',
            'entry_border': '#ff9800',
            'list_bg': '#ffffff',
            'list_fg': '#3e2723',
            'list_selected_bg': '#ff9800',
            'list_selected_fg': '#ffffff',
            'tooltip_bg': '#fff3e0',
            'tooltip_fg': '#3e2723',
            'progressbar_bg': '#fff3e0',
            'progressbar_fg': '#ff9800',
        },
        'fonts': { # Strong, reliable
            'body': {'family': 'Georgia, serif', 'pixelSize': 14, 'bold': True},
            'title': {'family': 'Georgia, serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14, 'bold': True }
        },
        'styles': { # Solid, reliable
            'button_default': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 4, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 4},
            'sidebar_button_color': '#ffffff',
            'sidebar_button_text_color': '#ff9800',
            'sidebar_button_hover_color': '#fff3e0',
            'sidebar_button_pressed_color': '#ff9800',
            'sidebar_button_border_color': '#ff9800',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_applejack.png',
            'window_icon': 'qrc:/assets/icons/app_icon_applejack.png'
        },
        'catchphrases': {
            'app_title': "Applejack's Honest Earth Explorer",
            'view_HomeView_Welcome': "Howdy!",
            'view_HomeView_WelcomeUser': "Welcome, %1!",
            'status_gee_ready': "Earth Engine: Ready as can be!",
            'status_gee_not_ready': "Earth Engine: Needs authentication...",
            'view_DownloadView': "Download Data - Honest work!",
            'action_goto_map': "Check the Map!",
            'action_goto_download': "Get Some Data!",
            'action_goto_settings': "Settings!",
            'dialog_title_info': "Information!",
            'view_MapView': "The Map!",
            'view_SatelliteInfoView': "Satellite Information!",
            'view_IndexAnalysisView': "Index Analysis!",
            'view_VectorDownloadView': "Vector Download!",
            'view_DataViewerView': "Data Viewer!",
            'view_ProgressView': "Progress!",
            'view_SettingsView': "Settings!",
            'view_AboutView': "About!",
            'settings_opt_catchphrases': "Use Honest Speech",
            'settings_opt_icons': "Show Apple Icons",
            'settings_opt_animations': "Enable Farm Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': False
        }
    },
    'Rarity': {
        'metadata': {'display_name': 'Rarity', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': { # Purples, pinks, elegant colors
            'background': '#f3e5f5', # Light purple
            'foreground': '#4a148c',
            'primary': '#9c27b0',    # Purple
            'secondary': '#e91e63',  # Pink
            'accent': '#ff9800',     # Orange
            'error': '#f44336',      # Red
            'success': '#4caf50',    # Green
            'text': '#4a148c',
            'text_subtle': '#6a1b9a',
            'disabled': '#ce93d8',
            'widget_bg': '#ffffff',
            'widget_border': '#9c27b0',
            'text_on_primary': '#ffffff',
            'button_bg': '#9c27b0',
            'button_fg': '#ffffff',
            'button_hover_bg': '#7b1fa2',
            'entry_bg': '#ffffff',
            'entry_fg': '#4a148c',
            'entry_border': '#9c27b0',
            'list_bg': '#ffffff',
            'list_fg': '#4a148c',
            'list_selected_bg': '#9c27b0',
            'list_selected_fg': '#ffffff',
            'tooltip_bg': '#f3e5f5',
            'tooltip_fg': '#4a148c',
            'progressbar_bg': '#f3e5f5',
            'progressbar_fg': '#9c27b0',
        },
        'fonts': { # Elegant, refined
            'body': {'family': 'Georgia, serif', 'pixelSize': 14},
            'title': {'family': 'Georgia, serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14 }
        },
        'styles': { # Elegant, refined
            'button_default': {'radius': 6, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 6, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 6},
            'sidebar_button_color': '#ffffff',
            'sidebar_button_text_color': '#9c27b0',
            'sidebar_button_hover_color': '#f3e5f5',
            'sidebar_button_pressed_color': '#9c27b0',
            'sidebar_button_border_color': '#9c27b0',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_rarity.png',
            'window_icon': 'qrc:/assets/icons/app_icon_rarity.png'
        },
        'catchphrases': {
            'app_title': "Rarity's Fabulous Earth Explorer",
            'view_HomeView_Welcome': "Darling!",
            'view_HomeView_WelcomeUser': "Welcome, %1 darling!",
            'status_gee_ready': "Earth Engine: Simply divine!",
            'status_gee_not_ready': "Earth Engine: Needs authentication... how dreadful!",
            'view_DownloadView': "Download Data - Simply fabulous!",
            'action_goto_map': "Check the Map darling!",
            'action_goto_download': "Get Some Data!",
            'action_goto_settings': "Settings!",
            'dialog_title_info': "Information darling!",
            'view_MapView': "The Map!",
            'view_SatelliteInfoView': "Satellite Information!",
            'view_IndexAnalysisView': "Index Analysis!",
            'view_VectorDownloadView': "Vector Download!",
            'view_DataViewerView': "Data Viewer!",
            'view_ProgressView': "Progress!",
            'view_SettingsView': "Settings!",
            'view_AboutView': "About!",
            'settings_opt_catchphrases': "Use Fabulous Speech",
            'settings_opt_icons': "Show Gem Icons",
            'settings_opt_animations': "Enable Sparkle Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Princess Celestia': {
        'metadata': {'display_name': 'Princess Celestia', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#fff8e1',
            'foreground': '#6d4c41',
            'primary': '#ffd54f',
            'secondary': '#fff176',
            'accent': '#b39ddb',
            'error': '#ff8a65',
            'success': '#aed581',
            'text': '#6d4c41',
            'text_subtle': '#bdbdbd',
            'disabled': '#e0e0e0',
            'widget_bg': '#fffde7',
            'widget_border': '#ffd54f',
            'text_on_primary': '#6d4c41',
            'button_bg': '#ffd54f',
            'button_fg': '#6d4c41',
            'button_hover_bg': '#fff176',
            'entry_bg': '#fffde7',
            'entry_fg': '#6d4c41',
            'entry_border': '#ffd54f',
            'list_bg': '#fffde7',
            'list_fg': '#6d4c41',
            'list_selected_bg': '#ffd54f',
            'list_selected_fg': '#6d4c41',
            'tooltip_bg': '#fff8e1',
            'tooltip_fg': '#6d4c41',
            'progressbar_bg': '#fff8e1',
            'progressbar_fg': '#ffd54f',
        },
        'fonts': {
            'body': {'family': 'Georgia, serif', 'pixelSize': 14},
            'title': {'family': 'Georgia, serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 6},
            'sidebar_button_color': '#fffde7',
            'sidebar_button_text_color': '#ffd54f',
            'sidebar_button_hover_color': '#fff8e1',
            'sidebar_button_pressed_color': '#ffd54f',
            'sidebar_button_border_color': '#ffd54f',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_celestia.png',
            'window_icon': 'qrc:/assets/icons/app_icon_celestia.png'
        },
        'catchphrases': {
            'app_title': "Celestia's Solar Surveyor",
            'view_HomeView_Welcome': "Greetings, my little pony!",
            'view_HomeView_WelcomeUser': "Welcome, %1! Let the sun shine on your research!",
            'status_gee_ready': "Earth Engine: Radiant and ready!",
            'status_gee_not_ready': "Earth Engine: Needs a little more sunlight (auth)!",
            'view_DownloadView': "Sunbeam Data Download",
            'action_goto_map': "To the Solar Map!",
            'action_goto_download': "Download Sunlit Data",
            'action_goto_settings': "Royal Settings",
            'dialog_title_info': "A Royal Message!",
            'view_MapView': "Solar Cartography",
            'view_SatelliteInfoView': "Celestial Archives",
            'view_IndexAnalysisView': "Sun Index Analysis",
            'view_VectorDownloadView': "Solar Vector Download",
            'view_DataViewerView': "Sunlit Data Viewer",
            'view_ProgressView': "Solar Progress",
            'view_SettingsView': "Royal Preferences",
            'view_AboutView': "About the Sun Princess",
            'settings_opt_catchphrases': "Use Royal Speech",
            'settings_opt_icons': "Show Sun Icons",
            'settings_opt_animations': "Enable Solar Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Princess Luna': {
        'metadata': {'display_name': 'Princess Luna', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#23213a',
            'foreground': '#e0e0ff',
            'primary': '#3949ab',
            'secondary': '#7e57c2',
            'accent': '#90caf9',
            'error': '#b39ddb',
            'success': '#80cbc4',
            'text': '#e0e0ff',
            'text_subtle': '#b0bec5',
            'disabled': '#616161',
            'widget_bg': '#2c254d',
            'widget_border': '#3949ab',
            'text_on_primary': '#e0e0ff',
            'button_bg': '#3949ab',
            'button_fg': '#e0e0ff',
            'button_hover_bg': '#7e57c2',
            'entry_bg': '#2c254d',
            'entry_fg': '#e0e0ff',
            'entry_border': '#3949ab',
            'list_bg': '#2c254d',
            'list_fg': '#e0e0ff',
            'list_selected_bg': '#3949ab',
            'list_selected_fg': '#e0e0ff',
            'tooltip_bg': '#23213a',
            'tooltip_fg': '#e0e0ff',
            'progressbar_bg': '#23213a',
            'progressbar_fg': '#3949ab',
        },
        'fonts': {
            'body': {'family': 'Georgia, serif', 'pixelSize': 14},
            'title': {'family': 'Georgia, serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Georgia, serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Georgia, serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 6},
            'sidebar_button_color': '#2c254d',
            'sidebar_button_text_color': '#3949ab',
            'sidebar_button_hover_color': '#23213a',
            'sidebar_button_pressed_color': '#3949ab',
            'sidebar_button_border_color': '#3949ab',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_luna.png',
            'window_icon': 'qrc:/assets/icons/app_icon_luna.png'
        },
        'catchphrases': {
            'app_title': "Luna's Lunar Mapper",
            'view_HomeView_Welcome': "Good evening, dreamer!",
            'view_HomeView_WelcomeUser': "Welcome, %1! The night is young for research!",
            'status_gee_ready': "Earth Engine: Nightly operations ready!",
            'status_gee_not_ready': "Earth Engine: Needs more moonlight (auth)!",
            'view_DownloadView': "Moonbeam Data Download",
            'action_goto_map': "To the Lunar Map!",
            'action_goto_download': "Download Night Data",
            'action_goto_settings': "Dream Settings",
            'dialog_title_info': "A Dream Message!",
            'view_MapView': "Lunar Cartography",
            'view_SatelliteInfoView': "Dream Archives",
            'view_IndexAnalysisView': "Moon Index Analysis",
            'view_VectorDownloadView': "Lunar Vector Download",
            'view_DataViewerView': "Dream Data Viewer",
            'view_ProgressView': "Lunar Progress",
            'view_SettingsView': "Dream Preferences",
            'view_AboutView': "About the Moon Princess",
            'settings_opt_catchphrases': "Use Dream Speech",
            'settings_opt_icons': "Show Moon Icons",
            'settings_opt_animations': "Enable Lunar Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Trixie': {
        'metadata': {'display_name': 'Trixie', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#e1bee7',
            'foreground': '#4a148c',
            'primary': '#7c43bd',
            'secondary': '#ffd600',
            'accent': '#00bcd4',
            'error': '#ff5252',
            'success': '#69f0ae',
            'text': '#4a148c',
            'text_subtle': '#9575cd',
            'disabled': '#bdbdbd',
            'widget_bg': '#ede7f6',
            'widget_border': '#7c43bd',
            'text_on_primary': '#ffffff',
            'button_bg': '#7c43bd',
            'button_fg': '#ffffff',
            'button_hover_bg': '#9575cd',
            'entry_bg': '#ede7f6',
            'entry_fg': '#4a148c',
            'entry_border': '#7c43bd',
            'list_bg': '#ede7f6',
            'list_fg': '#4a148c',
            'list_selected_bg': '#ffd600',
            'list_selected_fg': '#4a148c',
            'tooltip_bg': '#e1bee7',
            'tooltip_fg': '#4a148c',
            'progressbar_bg': '#e1bee7',
            'progressbar_fg': '#7c43bd',
        },
        'fonts': {
            'body': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 10, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 10, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 8},
            'sidebar_button_color': '#ede7f6',
            'sidebar_button_text_color': '#7c43bd',
            'sidebar_button_hover_color': '#e1bee7',
            'sidebar_button_pressed_color': '#7c43bd',
            'sidebar_button_border_color': '#7c43bd',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_trixie.png',
            'window_icon': 'qrc:/assets/icons/app_icon_trixie.png'
        },
        'catchphrases': {
            'app_title': "The Great and Powerful Trixie's Map!",
            'view_HomeView_Welcome': "Behold, the Great and Powerful Trixie!",
            'view_HomeView_WelcomeUser': "Welcome, %1! Prepare to be amazed!",
            'status_gee_ready': "Earth Engine: Ready for a magical performance!",
            'status_gee_not_ready': "Earth Engine: Needs more applause (auth)!",
            'view_DownloadView': "Trixie's Data Download",
            'action_goto_map': "To the Stage Map!",
            'action_goto_download': "Download Magical Data",
            'action_goto_settings': "Trixie's Settings",
            'dialog_title_info': "A Magical Announcement!",
            'view_MapView': "Stage Cartography",
            'view_SatelliteInfoView': "Trixie's Archives",
            'view_IndexAnalysisView': "Magic Index Analysis",
            'view_VectorDownloadView': "Trixie's Vector Download",
            'view_DataViewerView': "Magical Data Viewer",
            'view_ProgressView': "Performance Progress",
            'view_SettingsView': "Trixie's Preferences",
            'view_AboutView': "About Trixie",
            'settings_opt_catchphrases': "Use Trixie's Speech",
            'settings_opt_icons': "Show Magic Icons",
            'settings_opt_animations': "Enable Magic Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Starlight Glimmer': {
        'metadata': {'display_name': 'Starlight Glimmer', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#e0f7fa',
            'foreground': '#4a148c',
            'primary': '#ba68c8',
            'secondary': '#4dd0e1',
            'accent': '#ffd54f',
            'error': '#ff5252',
            'success': '#69f0ae',
            'text': '#4a148c',
            'text_subtle': '#9575cd',
            'disabled': '#bdbdbd',
            'widget_bg': '#f3e5f5',
            'widget_border': '#ba68c8',
            'text_on_primary': '#ffffff',
            'button_bg': '#ba68c8',
            'button_fg': '#ffffff',
            'button_hover_bg': '#9575cd',
            'entry_bg': '#f3e5f5',
            'entry_fg': '#4a148c',
            'entry_border': '#ba68c8',
            'list_bg': '#f3e5f5',
            'list_fg': '#4a148c',
            'list_selected_bg': '#4dd0e1',
            'list_selected_fg': '#4a148c',
            'tooltip_bg': '#e0f7fa',
            'tooltip_fg': '#4a148c',
            'progressbar_bg': '#e0f7fa',
            'progressbar_fg': '#ba68c8',
        },
        'fonts': {
            'body': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Arial, Helvetica, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 8, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 6},
            'sidebar_button_color': '#f3e5f5',
            'sidebar_button_text_color': '#ba68c8',
            'sidebar_button_hover_color': '#e0f7fa',
            'sidebar_button_pressed_color': '#ba68c8',
            'sidebar_button_border_color': '#ba68c8',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_starlight.png',
            'window_icon': 'qrc:/assets/icons/app_icon_starlight.png'
        },
        'catchphrases': {
            'app_title': "Starlight's Equality Explorer",
            'view_HomeView_Welcome': "Welcome, friend!",
            'view_HomeView_WelcomeUser': "Welcome, %1! Let's make some magic!",
            'status_gee_ready': "Earth Engine: All equal and ready!",
            'status_gee_not_ready': "Earth Engine: Needs more friendship (auth)!",
            'view_DownloadView': "Equality Data Download",
            'action_goto_map': "To the Equal Map!",
            'action_goto_download': "Download Equal Data",
            'action_goto_settings': "Equality Settings",
            'dialog_title_info': "A Friendship Message!",
            'view_MapView': "Equality Cartography",
            'view_SatelliteInfoView': "Friendship Archives",
            'view_IndexAnalysisView': "Equality Index Analysis",
            'view_VectorDownloadView': "Equality Vector Download",
            'view_DataViewerView': "Friendship Data Viewer",
            'view_ProgressView': "Equality Progress",
            'view_SettingsView': "Equality Preferences",
            'view_AboutView': "About Starlight Glimmer",
            'settings_opt_catchphrases': "Use Equality Speech",
            'settings_opt_icons': "Show Equality Icons",
            'settings_opt_animations': "Enable Equality Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Derpy Hooves': {
        'metadata': {'display_name': 'Derpy Hooves', 'category': 'MLP', 'author': 'Jules for Flutter Earth'},
        'colors': {
            'background': '#e0e0e0',
            'foreground': '#616161',
            'primary': '#ffd600',
            'secondary': '#90caf9',
            'accent': '#bdbdbd',
            'error': '#ff5252',
            'success': '#69f0ae',
            'text': '#616161',
            'text_subtle': '#bdbdbd',
            'disabled': '#bdbdbd',
            'widget_bg': '#f5f5f5',
            'widget_border': '#ffd600',
            'text_on_primary': '#616161',
            'button_bg': '#ffd600',
            'button_fg': '#616161',
            'button_hover_bg': '#fff176',
            'entry_bg': '#f5f5f5',
            'entry_fg': '#616161',
            'entry_border': '#ffd600',
            'list_bg': '#f5f5f5',
            'list_fg': '#616161',
            'list_selected_bg': '#ffd600',
            'list_selected_fg': '#616161',
            'tooltip_bg': '#e0e0e0',
            'tooltip_fg': '#616161',
            'progressbar_bg': '#e0e0e0',
            'progressbar_fg': '#ffd600',
        },
        'fonts': {
            'body': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 22, 'bold': True},
            'button': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 13, 'bold': True},
            'monospace': {'family': 'Courier New, Courier, monospace', 'pixelSize': 13},
            'character_specific': {'family': 'Comic Sans MS, Chalkboard SE, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 10, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 10, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 8},
            'sidebar_button_color': '#f5f5f5',
            'sidebar_button_text_color': '#ffd600',
            'sidebar_button_hover_color': '#e0e0e0',
            'sidebar_button_pressed_color': '#ffd600',
            'sidebar_button_border_color': '#ffd600',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_derpy.png',
            'window_icon': 'qrc:/assets/icons/app_icon_derpy.png'
        },
        'catchphrases': {
            'app_title': "Derpy's Muffin Mapper",
            'view_HomeView_Welcome': "Muffins!",
            'view_HomeView_WelcomeUser': "Hi %1! Did you bring muffins?",
            'status_gee_ready': "Earth Engine: Ready for delivery!",
            'status_gee_not_ready': "Earth Engine: Oops! Needs more muffins (auth)!",
            'view_DownloadView': "Muffin Data Download",
            'action_goto_map': "To the Muffin Map!",
            'action_goto_download': "Download Muffin Data",
            'action_goto_settings': "Muffin Settings",
            'dialog_title_info': "A Muffin Message!",
            'view_MapView': "Muffin Cartography",
            'view_SatelliteInfoView': "Muffin Archives",
            'view_IndexAnalysisView': "Muffin Index Analysis",
            'view_VectorDownloadView': "Muffin Vector Download",
            'view_DataViewerView': "Muffin Data Viewer",
            'view_ProgressView': "Muffin Progress",
            'view_SettingsView': "Muffin Preferences",
            'view_AboutView': "About Derpy Hooves",
            'settings_opt_catchphrases': "Use Muffin Speech",
            'settings_opt_icons': "Show Muffin Icons",
            'settings_opt_animations': "Enable Muffin Animations",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    # Minecraft Themes Start Here
    'Steve': {
        'metadata': {'display_name': 'Steve (Minecraft)', 'category': 'Minecraft', 'author': 'Jules for Flutter Earth'},
        'colors': { # Blues, browns, greens
            'background': '#5a82c8', # Steve's Shirt Blue
            'foreground': '#FFFFFF',
            'primary': '#3d2d1e',    # Steve's Hair Brown
            'secondary': '#8b5a2b',  # Steve's Pants Dark Blue/Brownish
            'accent': '#76c05d',     # Grass Green
            'error': '#FF5555',
            'success': '#55FF55',
            'text': '#FFFFFF',
            'text_subtle': '#c0d4f8',
            'disabled': '#808080',
            'widget_bg': '#4a6da8',
            'widget_border': '#3d2d1e',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#8b5a2b', # Pants color for buttons
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#a07040',
            'entry_bg': '#426090', # Darker shirt blue
            'entry_fg': '#FFFFFF',
            'entry_border': '#3d2d1e',
            'list_bg': '#4a6da8',
            'list_fg': '#FFFFFF',
            'list_selected_bg': '#76c05d', # Grass green for selection
            'list_selected_fg': '#3d2d1e',
            'tooltip_bg': '#3d2d1e', # Brown tooltip
            'tooltip_fg': '#FFFFFF',
            'progressbar_bg': '#4a6da8',
            'progressbar_fg': '#76c05d',
        },
        'fonts': { # Pixelated/Blocky if possible, otherwise clean sans-serif
            'body': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14}, # Placeholder for a pixel font
            'title': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 12},
            'character_specific': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14 }
        },
        'styles': { # Blocky, simple
            'button_default': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 0},
            'sidebar_button_color': '#4a6da8',
            'sidebar_button_text_color': '#FFFFFF',
            'sidebar_button_hover_color': '#8b5a2b',
            'sidebar_button_pressed_color': '#76c05d',
            'sidebar_button_border_color': '#3d2d1e',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_steve.png',
            'window_icon': 'qrc:/assets/icons/app_icon_steve.png'
        },
        'catchphrases': {
            'app_title': "Steve's Blocky World Explorer",
            'view_HomeView_Welcome': "Howdy, Miner!",
            'view_HomeView_WelcomeUser': "Greetings, %1! Ready to craft some maps?",
            'status_gee_ready': "Earth Engine: World Loaded!",
            'status_gee_not_ready': "Earth Engine: Map generation failed (Auth needed)!",
            'view_DownloadView': "Resource Gathering Terminal",
            'action_goto_map': "Explore Biomes",
            'action_goto_download': "Mine Data Blocks",
            'action_goto_settings': "Crafting Table (Settings)",
            'dialog_title_info': "A Sign!",
            'view_MapView': "Overworld Map",
            'view_SatelliteInfoView': "Beacon Network (Satellites)",
            'view_IndexAnalysisView': "Enchantment Table (Indices)",
            'view_VectorDownloadView': "Chunk Loader (Vectors)",
            'view_DataViewerView': "Chest Contents (Data Viewer)",
            'view_ProgressView': "Mining Progress",
            'view_SettingsView': "Game Rules",
            'view_AboutView': "Ancient Tome (About)",
            'settings_opt_catchphrases': "Use Steve's Terms",
            'settings_opt_icons': "Show Blocky Icons",
            'settings_opt_animations': "Enable Pixel Dust",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': False # Pixel dust might be too much, simple is better
        }
    },
    'Alex (Minecraft)': {
        'metadata': {'display_name': 'Alex (Minecraft)', 'category': 'Minecraft', 'author': 'Jules for Flutter Earth'},
        'colors': { # Greens, oranges, browns
            'background': '#6aa038', # Alex's Shirt Green
            'foreground': '#FFFFFF',
            'primary': '#b8662c',    # Alex's Hair Orange
            'secondary': '#674620',  # Alex's Pants Brown
            'accent': '#ffc87c',     # Light skin tone / highlight
            'error': '#FF5555',
            'success': '#55FF55',
            'text': '#FFFFFF',
            'text_subtle': '#d0e0c0',
            'disabled': '#808080',
            'widget_bg': '#5a8828',
            'widget_border': '#b8662c',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#674620',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#805830',
            'entry_bg': '#527820',
            'entry_fg': '#FFFFFF',
            'entry_border': '#b8662c',
            'list_bg': '#5a8828',
            'list_fg': '#FFFFFF',
            'list_selected_bg': '#ffc87c',
            'list_selected_fg': '#674620',
            'tooltip_bg': '#b8662c',
            'tooltip_fg': '#FFFFFF',
            'progressbar_bg': '#5a8828',
            'progressbar_fg': '#ffc87c',
        },
        'fonts': {
            'body': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 12},
            'character_specific': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 2},
            'button_primary': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 2},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 0},
            'sidebar_button_color': '#5a8828',
            'sidebar_button_text_color': '#FFFFFF',
            'sidebar_button_hover_color': '#674620',
            'sidebar_button_pressed_color': '#ffc87c',
            'sidebar_button_border_color': '#b8662c',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_alex.png',
            'window_icon': 'qrc:/assets/icons/app_icon_alex.png'
        },
        'catchphrases': {
            'app_title': "Alex's Adventure Mapper",
            'view_HomeView_Welcome': "Hey Explorer!",
            'view_HomeView_WelcomeUser': "Welcome, %1! New biomes await!",
            'status_gee_ready': "Earth Engine: Map Data Synced!",
            'status_gee_not_ready': "Earth Engine: Compass needs calibrating (Auth)!",
            'view_DownloadView': "Exploration Supplies",
            'action_goto_map': "Chart New Lands",
            'action_goto_download': "Gather Coordinates",
            'action_goto_settings': "Survival Guide (Settings)",
            'dialog_title_info': "Explorer's Log!",
            'view_MapView': "Wilderness Atlas",
            'view_SatelliteInfoView': "Cartography Table",
            'view_IndexAnalysisView': "Potion Brewing (Indices)",
            'view_VectorDownloadView': "Biome Data Collector",
            'view_DataViewerView': "Inventory Check (Data Viewer)",
            'view_ProgressView': "Journey Progress",
            'view_SettingsView': "World Options",
            'view_AboutView': "Lore Book (About)",
            'settings_opt_catchphrases': "Use Alex's Terms",
            'settings_opt_icons': "Show Adventure Icons",
            'settings_opt_animations': "Enable Nature Particles",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': False
        }
    },
    'Creeper (Minecraft)': {
        'metadata': {'display_name': 'Creeper (Minecraft)', 'category': 'Minecraft', 'author': 'Jules for Flutter Earth'},
        'colors': { # Greens, grays, black
            'background': '#2d7a3f', # Creeper Green
            'foreground': '#FFFFFF',
            'primary': '#1a4a25',    # Dark Creeper Green
            'secondary': '#ababab',  # Light Gray (for accents)
            'accent': '#000000',     # Black (face details)
            'error': '#FF5555',
            'success': '#30cb00',    # Bright Green for success
            'text': '#FFFFFF',
            'text_subtle': '#b0e0b0',
            'disabled': '#555555',
            'widget_bg': '#256030',
            'widget_border': '#1a4a25',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#1a4a25',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#000000', # Black hover
            'entry_bg': '#205028',
            'entry_fg': '#FFFFFF',
            'entry_border': '#000000',
            'list_bg': '#256030',
            'list_fg': '#FFFFFF',
            'list_selected_bg': '#000000',
            'list_selected_fg': '#30cb00', # Bright Green text on black
            'tooltip_bg': '#000000',
            'tooltip_fg': '#30cb00',
            'progressbar_bg': '#256030',
            'progressbar_fg': '#000000',
        },
        'fonts': {
            'body': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 13, 'bold': True}, # Bold buttons
            'monospace': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 12},
            'character_specific': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'accent', 'borderWidth': 3},
            'button_primary': {'radius': 0, 'textColorKey': 'foreground', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 3},
            'text_input': {'borderColorKey': 'accent', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 0},
            'sidebar_button_color': '#256030',
            'sidebar_button_text_color': '#FFFFFF',
            'sidebar_button_hover_color': '#1a4a25',
            'sidebar_button_pressed_color': '#000000',
            'sidebar_button_border_color': '#000000',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_creeper.png',
            'window_icon': 'qrc:/assets/icons/app_icon_creeper.png'
        },
        'catchphrases': {
            'app_title': "Creeper's Sssssecret Maps",
            'view_HomeView_Welcome': "Sssss...",
            'view_HomeView_WelcomeUser': "Hullo, %1... Don't mind the hissing...",
            'status_gee_ready': "Earth Engine: Primed...",
            'status_gee_not_ready': "Earth Engine: Dud... (Auth needed)",
            'view_DownloadView': "Data Detonation Setup",
            'action_goto_map': "Survey Blast Zone",
            'action_goto_download': "Acquire... Resources",
            'action_goto_settings': "Fuse Settings",
            'dialog_title_info': "Important Hiss!",
            'view_MapView': "Pre-Detonation Scan",
            'view_SatelliteInfoView': "Orbital... Hazards",
            'view_IndexAnalysisView': "Impact Analysis",
            'view_VectorDownloadView': "Fragment Collector",
            'view_DataViewerView': "Crater Overview",
            'view_ProgressView': "Countdown...",
            'view_SettingsView': "Detonator Controls",
            'view_AboutView': "The Creeper Code",
            'settings_opt_catchphrases': "Sssspeak like a Creeper",
            'settings_opt_icons': "Show Explosive Icons",
            'settings_opt_animations': "Enable Fuse Sparks",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Enderman (Minecraft)': {
        'metadata': {'display_name': 'Enderman (Minecraft)', 'category': 'Minecraft', 'author': 'Jules for Flutter Earth'},
        'colors': { # Blacks, purples, magenta
            'background': '#1a1a1a', # Very Dark Gray / Black
            'foreground': '#d881ff', # Enderman Eye Purple/Magenta
            'primary': '#330033',    # Dark Purple
            'secondary': '#bc50ff',  # Bright Purple
            'accent': '#ff00ff',     # Magenta (particles)
            'error': '#FF5555',
            'success': '#cc66ff',    # Lighter Purple for success
            'text': '#d881ff',
            'text_subtle': '#b070d0',
            'disabled': '#444444',
            'widget_bg': '#220022',
            'widget_border': '#330033',
            'text_on_primary': '#d881ff',
            'button_bg': '#330033',
            'button_fg': '#d881ff',
            'button_hover_bg': '#4d004d',
            'entry_bg': '#2a002a',
            'entry_fg': '#d881ff',
            'entry_border': '#bc50ff',
            'list_bg': '#220022',
            'list_fg': '#d881ff',
            'list_selected_bg': '#ff00ff',
            'list_selected_fg': '#1a1a1a',
            'tooltip_bg': '#ff00ff',
            'tooltip_fg': '#1a1a1a',
            'progressbar_bg': '#220022',
            'progressbar_fg': '#ff00ff',
        },
        'fonts': {
            'body': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 12},
            'character_specific': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14 } # Could be a more "alien" font
        },
        'styles': {
            'button_default': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'button_primary': {'radius': 0, 'textColorKey': 'foreground', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 0},
            'sidebar_button_color': '#220022',
            'sidebar_button_text_color': '#d881ff',
            'sidebar_button_hover_color': '#330033',
            'sidebar_button_pressed_color': '#ff00ff',
            'sidebar_button_border_color': '#bc50ff',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_enderman.png',
            'window_icon': 'qrc:/assets/icons/app_icon_enderman.png'
        },
        'catchphrases': {
            'app_title': "Enderman's Teleportation Almanac",
            'view_HomeView_Welcome': "*Vwoop*",
            'view_HomeView_WelcomeUser': "You look... interesting, %1.",
            'status_gee_ready': "Earth Engine: Reality Stable.",
            'status_gee_not_ready': "Earth Engine: Dimensional Rift (Auth needed)!",
            'view_DownloadView': "Block Relocation Interface",
            'action_goto_map': "Observe Dimensions",
            'action_goto_download': "Collect... Blocks",
            'action_goto_settings': "Reality Configuration",
            'dialog_title_info': "*Stares Intently*",
            'view_MapView': "The Void (Map)",
            'view_SatelliteInfoView': "Otherworldly Beacons",
            'view_IndexAnalysisView': "Dimensional Analysis",
            'view_VectorDownloadView': "Particle Transporter",
            'view_DataViewerView': "Held Block (Data Viewer)",
            'view_ProgressView': "Teleportation Sequence...",
            'view_SettingsView': "Ender Chest",
            'view_AboutView': "Scrolls of the End",
            'settings_opt_catchphrases': "Use Enderman Sounds/Speech",
            'settings_opt_icons': "Show Ender Pearl Icons",
            'settings_opt_animations': "Enable Particle Effects",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': True
        }
    },
    'Zombie (Minecraft)': {
        'metadata': {'display_name': 'Zombie (Minecraft)', 'category': 'Minecraft', 'author': 'Jules for Flutter Earth'},
        'colors': { # Muted greens, grays, dark blues
            'background': '#4a654e', # Zombie Green
            'foreground': '#FFFFFF',
            'primary': '#3b5340',    # Darker Zombie Green
            'secondary': '#7b8b7f',  # Torn Clothes Gray/Blue
            'accent': '#c0c0c0',     # Dull metal / highlight
            'error': '#FF5555',
            'success': '#80a080',    # Muted Green success
            'text': '#FFFFFF',
            'text_subtle': '#c0d0c0',
            'disabled': '#606060',
            'widget_bg': '#3e5542',
            'widget_border': '#3b5340',
            'text_on_primary': '#FFFFFF',
            'button_bg': '#7b8b7f',
            'button_fg': '#FFFFFF',
            'button_hover_bg': '#90a090',
            'entry_bg': '#364838',
            'entry_fg': '#FFFFFF',
            'entry_border': '#7b8b7f',
            'list_bg': '#3e5542',
            'list_fg': '#FFFFFF',
            'list_selected_bg': '#c0c0c0',
            'list_selected_fg': '#3b5340',
            'tooltip_bg': '#3b5340',
            'tooltip_fg': '#FFFFFF',
            'progressbar_bg': '#3e5542',
            'progressbar_fg': '#c0c0c0',
        },
        'fonts': {
            'body': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14},
            'title': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 20, 'bold': True},
            'button': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 13, 'bold': False},
            'monospace': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 12},
            'character_specific': {'family': 'Minecraftia, Fixedsys, System, sans-serif', 'pixelSize': 14 }
        },
        'styles': {
            'button_default': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'button_bg', 'hoverColorKey': 'button_hover_bg', 'borderColorKey': 'primary', 'borderWidth': 1},
            'button_primary': {'radius': 0, 'textColorKey': 'button_fg', 'backgroundColorKey': 'accent', 'hoverColorKey': 'primary', 'borderColorKey': 'secondary', 'borderWidth': 1},
            'text_input': {'borderColorKey': 'entry_border', 'backgroundColorKey': 'entry_bg', 'textColorKey': 'entry_fg', 'radius': 0},
            'sidebar_button_color': '#3e5542',
            'sidebar_button_text_color': '#FFFFFF',
            'sidebar_button_hover_color': '#7b8b7f',
            'sidebar_button_pressed_color': '#c0c0c0',
            'sidebar_button_border_color': '#3b5340',
        },
        'paths': {
            'splash_screen_image': 'qrc:/assets/images/splash_zombie.png',
            'window_icon': 'qrc:/assets/icons/app_icon_zombie.png'
        },
        'catchphrases': {
            'app_title': "Zombie's... Uh... Maps?",
            'view_HomeView_Welcome': "Braaaains... I mean, Welcome!",
            'view_HomeView_WelcomeUser': "Urrgh, %1... Maps?",
            'status_gee_ready': "Earth Engine: World... not eaten.",
            'status_gee_not_ready': "Earth Engine: *Groans* (Auth needed)!",
            'view_DownloadView': "Resource... Piles",
            'action_goto_map': "Shuffle Around (Map)",
            'action_goto_download': "Collect... Things",
            'action_goto_settings': "Mumble Settings",
            'dialog_title_info': "*Moan*",
            'view_MapView': "The Horde's Territory",
            'view_SatelliteInfoView': "Sky... Things?",
            'view_IndexAnalysisView': "Decay Analysis",
            'view_VectorDownloadView': "Slow Data Shuffle",
            'view_DataViewerView': "Dropped Items (Viewer)",
            'view_ProgressView': "Shambling Progress",
            'view_SettingsView': "Zombie Preferences",
            'view_AboutView': "Ancient Zombie Scrolls",
            'settings_opt_catchphrases': "Use Zombie Moans",
            'settings_opt_icons': "Show Rotten Flesh Icons",
            'settings_opt_animations': "Enable Groaning Sounds (pls no)",
        },
        'options': {
            'use_character_catchphrases': True,
            'show_special_icons': True,
            'enable_animated_background': False
        }
    }
}

# Default configuration
DEFAULT_CONFIG = AppConfig(
    output_dir=os.path.expanduser('~/Downloads/flutter_earth'),
    tile_size=1.0,
    max_workers=4,
    cloud_mask=True,
    max_cloud_cover=20.0,
    sensor_priority=['LANDSAT_9', 'SENTINEL_2', 'LANDSAT_8'],
    recent_directories=[],
    theme='Default (Dark)'
)

# Environment-specific configurations
ENV_CONFIGS: Dict[Environment, Dict[str, Any]] = {
    'development': {
        'tile_size': 0.5,
        'max_workers': 2
    },
    'production': {
        'tile_size': 1.0,
        'max_workers': 4
    },
    'testing': {
        'tile_size': 0.1,
        'max_workers': 1
    }
}

# Satellite configuration
SATELLITE_DETAILS: Dict[str, SatelliteDetails] = {
    'LANDSAT_9': {
        'name': 'Landsat 9',
        'description': 'Latest Landsat satellite with improved sensors',
        'resolution_nominal': '30m',
        'bands': ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'],
        'start_date': '2021-09-27',
        'end_date': 'present',
        'cloud_cover': True,
        'collection_id': 'LANDSAT/LC09/C02/T1_L2'
    },
    'SENTINEL_2': {
        'name': 'Sentinel-2',
        'description': 'ESA optical satellite with high revisit rate',
        'resolution_nominal': '10m',
        'bands': ['B2', 'B3', 'B4', 'B8'],
        'start_date': '2015-06-23',
        'end_date': 'present',
        'cloud_cover': True,
        'collection_id': 'COPERNICUS/S2_SR_HARMONIZED'
    }
}

class ConfigManager(QObject):
    """Manages application configuration.
    Emits config_changed(dict) when the config is changed or reloaded.
    Emits settingChanged(str key, object value) for each individual setting change.
    """
    config_changed = Signal(dict)  # Emitted when config is changed or reloaded
    settingChanged = Signal(str, object)  # Emitted when a single setting is changed
    
    def __init__(self, config_file: str = 'flutter_earth_config.json', environment: Environment = 'production'):
        """Initialize configuration manager."""
        super().__init__()
        self.config_file = config_file
        self.environment = environment
        self.config: AppConfig = self._get_env_config()
        self.load_config()
    
    def _get_env_config(self) -> AppConfig:
        """Get environment-specific configuration."""
        config = copy.deepcopy(DEFAULT_CONFIG)
        overrides = ENV_CONFIGS.get(self.environment, {})
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def _validate_config(self, config: AppConfig) -> None:
        """Validate configuration values."""
        for key, rule in CONFIG_RULES.items():
            value = getattr(config, key, None)
            if value is None and rule.required:
                raise ConfigurationError(f"Missing required configuration key: {key}")
            if not rule.validate(value):
                type_str = getattr(rule.type, '__name__', str(rule.type))
                raise ConfigurationError(
                    f"Invalid configuration value for {key}: {value}. "
                    f"Expected type {type_str}"
                )

    def load_config(self) -> None:
        """Load configuration from file, falling back to defaults if needed."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for key, value in data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
            self._validate_config(self.config)
            logging.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logging.error(f"Failed to load config: {e}. Using defaults.")
        self.config_changed.emit(self.to_dict())

    def reload_config(self) -> None:
        """Reload configuration from file and emit config_changed signal."""
        self.load_config()

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2)
            logging.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return getattr(self.config, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and emit config_changed and settingChanged signals."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
            self.settingChanged.emit(key, value)
            self.config_changed.emit(self.to_dict())

    def get_current_theme_colors(self) -> Dict[str, str]:
        """Get the current theme's color dictionary."""
        theme_data = THEMES.get(self.config.theme, THEMES['Default (Dark)'])
        return theme_data.get('colors', {}) # Return colors sub-dictionary

    def get_current_theme_data(self) -> Dict[str, Any]:
        theme_data = self.get('theme', None)
        if not theme_data or theme_data not in THEMES:
            theme_data = 'Default (Dark)'
        data = copy.deepcopy(THEMES.get(theme_data, THEMES['Default (Dark)']))
        if not isinstance(data, dict):
            logging.error(f"get_current_theme_data: theme data for '{theme_data}' is not a dict! Returning empty dict.")
            return {}
        logging.debug(f"get_current_theme_data: returning {data}")
        return data

    def get_theme_data(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get the full data dictionary for a specific theme by name."""
        theme_info = THEMES.get(theme_name)
        return copy.deepcopy(theme_info) if theme_info else None # Return a copy

    def get_available_themes(self) -> List[Dict[str, Any]]:
        available = []
        for name, data in THEMES.items():
            meta = data.get('metadata', {})
            available.append({
                'name': name,
                'display_name': meta.get('display_name', name),
                'category': meta.get('category', 'Uncategorized')
            })
        logging.debug(f"get_available_themes: returning {available}")
        return available

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values and emit config_changed and settingChanged signals."""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.settingChanged.emit(key, value)
        self.save_config()
        self.config_changed.emit(self.to_dict())

    def add_recent_directory(self, directory: str) -> None:
        """Add a directory to the recent directories list."""
        if directory not in self.config.recent_directories:
            self.config.recent_directories.append(directory)
            self.save_config()
            self.config_changed.emit(self.to_dict())

    def get_satellite_details(self, sensor_name: str) -> Optional[SatelliteDetails]:
        """Get details for a given satellite sensor."""
        return SATELLITE_DETAILS.get(sensor_name)

    def get_environment(self) -> Environment:
        """Get the current environment."""
        return self.environment

    def set_environment(self, environment: Environment) -> None:
        """Set the environment and reload config."""
        self.environment = environment
        self.config = self._get_env_config()
        self.reload_config()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the config dataclass to a dictionary."""
        return {field.name: getattr(self.config, field.name) for field in fields(self.config)}

    def getAllSettings(self) -> Dict[str, Any]:
        # Return a dict with all expected config keys, filling with defaults if missing
        keys = ['output_dir', 'tile_size', 'max_workers', 'cloud_mask', 'max_cloud_cover', 'sensor_priority', 'recent_directories', 'theme']
        settings = {k: self.get(k, None) for k in keys}
        # Fill with defaults if any are missing
        for k in keys:
            if settings[k] is None:
                if k == 'sensor_priority' or k == 'recent_directories':
                    settings[k] = []
                elif k == 'cloud_mask':
                    settings[k] = False
                elif k == 'tile_size':
                    settings[k] = 1.0
                elif k == 'max_workers':
                    settings[k] = 4
                elif k == 'max_cloud_cover':
                    settings[k] = 100
                elif k == 'theme':
                    settings[k] = 'Default (Dark)'
                else:
                    settings[k] = ''
        logging.debug(f"getAllSettings: returning {settings}")
        return settings

# Singleton instance for global access
config_manager = ConfigManager() 