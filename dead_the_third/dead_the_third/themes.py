"""Theme system for Flutter Earth GUI."""
from typing import Dict, Any
from PyQt5 import QtGui

# Theme color definitions
FLUTTERSHY_COLORS = {
    "BG_MAIN": "#FEFEFA",
    "BG_FRAME": "#FFF5FA",
    "TEXT_COLOR": "#5D4037",
    "INPUT_BG": "#FFFCF5",
    "INPUT_FG": "#5D4037",
    "ACCENT_BORDER": "#E0B0E0",
    "PLACEHOLDER_FG": "#A98F84",
    "BUTTON_PINK_BG": "#FFC0CB",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFFFE0",
    "BUTTON_YELLOW_FG": "#8D6E63",
    "BUTTON_YELLOW_HOVER": "#FFFFF0",
    "BUTTON_LAVENDER_BG": "#F0E6FF",
    "BUTTON_LAVENDER_FG": "#4A4A6A",
    "BUTTON_LAVENDER_HOVER": "#E8DFFF",
    "PROGRESS_BG": "#FFF0F0",
    "PROGRESS_FG_OVERALL": "#FFC0CB",  # Pink
    "PROGRESS_FG_MONTHLY": "#FFF41E",  # Light Yellow
    "CALENDAR_HEADER_BG": "#FFF5FA",
    "TEXT_LIGHT": "#755C51",
    "LOG_BG": "#FFFCF5",
    "LOG_FG": "#5D4037",
    "MAP_BUTTON_FG": "#8D6E63"
}

NIGHT_MODE_COLORS = {
    "BG_MAIN": "#1E1E1E",
    "BG_FRAME": "#252526",
    "TEXT_COLOR": "#D4D4D4",
    "INPUT_BG": "#3C3C3C",
    "INPUT_FG": "#D4D4D4",
    "ACCENT_BORDER": "#007ACC",  # A nice blue accent
    "PLACEHOLDER_FG": "#7A7A7A",
    "BUTTON_PINK_BG": "#007ACC",  # Using the blue accent for "pink"
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#4A4A4A",  # Darker grey for "yellow"
    "BUTTON_YELLOW_FG": "#D4D4D4",
    "BUTTON_YELLOW_HOVER": "#5A5A5A",
    "BUTTON_LAVENDER_BG": "#333333",  # Dark grey for "lavender"
    "BUTTON_LAVENDER_FG": "#D4D4D4",
    "BUTTON_LAVENDER_HOVER": "#404040",
    "PROGRESS_BG": "#2A2A2A",
    "PROGRESS_FG_OVERALL": "#007ACC",
    "PROGRESS_FG_MONTHLY": "#1E90FF",  # Lighter blue (DodgerBlue)
    "CALENDAR_HEADER_BG": "#252526",
    "TEXT_LIGHT": "#A0A0A0",
    "LOG_BG": "#1E1E1E",
    "LOG_FG": "#D4D4D4",
    "MAP_BUTTON_FG": "#D4D4D4"
}

# Theme text definitions
FLUTTERSHY_TEXTS = {
    "window_title_main": "💖 Flutter Earth - Gentle GEE Downloader 💖",
    "start_date_label": "Start Date for our adventure 🗓️:",
    "end_date_label": "End Date for our adventure 🗓️:",
    "output_dir_label": "A cozy place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like a blooming flower 🌷:",
    "log_console_label": "Whispers from the Earth Engine 👇:",
    "run_button": "🌸 Begin Download 🌸",
    "cancel_button": "🍃 Pause Gently 🍂",
    "run_button_processing": "Working softly... 🐾",
    "cancel_button_cancelling": "Pausing gently...",
    "verify_button_text_base": "Check Satellite Friends",
    "verify_satellites_button_icon": "🛰️",
    "verify_satellites_button_verifying": "Asking friends... 🛰️",
    "verify_satellites_status_start": "Checking in with our satellite friends...",
    "verify_satellites_status_done": "All satellite friends are accounted for! (Or see notes below)",
    "verify_satellites_title": "🦋 Checking In With Satellite Friends 🦋",
    "status_bar_ready": "Ready for some lovely downloads! ✨",
    "status_bar_ee_init_fail": "Oh dear, EE couldn't connect. Some magic might be missing.",
    "status_bar_ee_init_ok": "Earth Engine is all set! Ready for a magical journey! ✨",
    "status_bar_input_error_prefix": "Oopsie! Something's not quite right: ",
    "status_bar_processing_started": "Our gentle download has begun...",
    "status_bar_cancellation_requested": "Pausing our journey for now...",
    "status_bar_processing_finished": "Our adventure is complete! Check your treasures.",
    "sensor_priority_label": "Sensor Friends Order 💖:",
    "sensor_priority_edit_button": "Arrange Friends...",
    "sensor_priority_dialog_title": "Arrange Our Sensor Friends 🌸",
    "sensor_priority_instruction": "Drag & drop to change order, or use buttons. Topmost is most preferred!",
    "sensor_priority_add_button": "Invite Friend...",
    "sensor_priority_remove_button": "Say Goodbye",
    "sensor_priority_up_button": "Up ↑",
    "sensor_priority_down_button": "Down ↓",
    "about_dialog_title": "About Flutter Earth 🦋",
    "about_dialog_tagline": "Gently downloading GEE data with QtPy!",
    "help_menu_text": "&Help",
    "about_menu_item_text": "&About Flutter Earth",
    "themes_menu_text": "&Themes",
    "sensor_priority_add_dialog_title": "Invite a New Sensor Friend!",
    "sensor_priority_add_dialog_label": "Which friend to invite to our list?",
    "cleanup_tiles_label": "Tidy up individual tiles after stitching? 🧹:",
    "use_highest_resolution_cb": "Use Highest Sensor Resolution ✨",
    "tools_menu_label": "&Tools 🛠️",
    "satellite_info_action_label": "🛰️ Satellite Info",
    "post_processing_action_label": "📊 Post Processing",
    "application_guide_menu_item_text": "Application Guide 📖",
    "target_resolution_auto_tooltip": "Resolution automatically set by 'Use Highest Sensor Resolution' option.",
    "target_resolution_manual_tooltip": "Target resolution in meters for the output mosaic (e.g., 10, 30).",
    "vector_download_tab_title": "🗺️ Vector Data Download",
    "vector_source_label": "Data Source (e.g., URL, Overpass Query):",
    "vector_type_label": "Source Type:",
    "vector_output_dir_label": "Save Vector Data To:",
    "vector_format_label": "Output Format:",
    "vector_start_download_button": "📥 Download Vector Data",
    "vector_osm_feature_type_label": "OSM Feature Type:",
    "vector_status_fetching": "Fetching vector data from {source}...",
    "vector_status_processing": "Processing vector data...",
    "vector_status_saving": "Saving vector data as {format} to {filename}...",
    "vector_status_success": "Vector data saved: {filename}",
    "vector_status_fail": "Vector data download/processing failed: {error}",
    "vector_aoi_missing_error": "AOI is required for Overpass API queries.",
    "vector_overpass_geojson_only_msg": "For Overpass API, data is saved as GeoJSON. Please convert to other formats manually if needed."
}

# Font settings
QT_FLUTTER_FONT_FAMILY = "Segoe UI"
QT_FLUTTER_FONT_SIZE_NORMAL = "11pt"

# Theme dictionary
THEMES = {
    "Fluttershy": FLUTTERSHY_COLORS,
    "Night Mode": NIGHT_MODE_COLORS,
}

DEFAULT_THEME = "Fluttershy"


class ThemeManager:
    """Manages theme colors and styling for the application."""
    
    def __init__(self, theme_name: str = DEFAULT_THEME):
        """Initialize theme manager with specified theme."""
        self.theme_name = theme_name
        self.colors = self.get_theme_colors(theme_name)
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Get color palette for specified theme."""
        return THEMES.get(theme_name, FLUTTERSHY_COLORS)
    
    def set_theme(self, theme_name: str):
        """Set the current theme."""
        self.theme_name = theme_name
        self.colors = self.get_theme_colors(theme_name)
    
    def get_stylesheet(self) -> str:
        """Generate Qt stylesheet for current theme."""
        colors = self.colors
        
        # Generate lighter variants for gradients
        input_bg_lighter = QtGui.QColor(colors['INPUT_BG']).lighter(105).name()
        log_bg_lighter = QtGui.QColor(colors['LOG_BG']).lighter(105).name()
        progress_overall_lighter = QtGui.QColor(colors['PROGRESS_FG_OVERALL']).lighter(120).name()
        progress_monthly_lighter = QtGui.QColor(colors['PROGRESS_FG_MONTHLY']).lighter(120).name()
        
        # Button hover/pressed states
        button_pink_hover = QtGui.QColor(colors['BUTTON_PINK_BG']).lighter(110).name()
        button_pink_pressed = QtGui.QColor(colors['BUTTON_PINK_BG']).darker(110).name()
        button_lavender_hover = colors.get('BUTTON_LAVENDER_HOVER', QtGui.QColor(colors['BUTTON_LAVENDER_BG']).lighter(110).name())
        button_lavender_pressed = QtGui.QColor(colors['BUTTON_LAVENDER_BG']).darker(110).name()
        button_yellow_hover = colors.get('BUTTON_YELLOW_HOVER', QtGui.QColor(colors['BUTTON_YELLOW_BG']).lighter(110).name())
        button_yellow_pressed = QtGui.QColor(colors['BUTTON_YELLOW_BG']).darker(110).name()
        
        # Font sizes
        font_size_normal_str = str(QT_FLUTTER_FONT_SIZE_NORMAL)
        if not font_size_normal_str.endswith('pt'):
            font_size_normal_str += "pt"
        
        font_size_small_str = str(int(font_size_normal_str.replace('pt', '')) - 1) + "pt"
        font_size_log_str = str(int(font_size_normal_str.replace('pt', '')) - 1) + "pt"
        
        return f"""
            QMainWindow, QWidget {{
                background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.7, fx:0.5, fy:0.5,
                                    stop:0 {colors['BG_MAIN']},
                                    stop:0.5 {colors['BG_FRAME']},
                                    stop:1 {colors['BG_MAIN']});
                font-family: '{QT_FLUTTER_FONT_FAMILY}';
            }}
            QLabel {{ color: {colors['TEXT_COLOR']}; font-size: {font_size_normal_str}; padding-top: 4px; padding-bottom: 4px; }}
            QLineEdit, QDateEdit, QComboBox {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['INPUT_BG']}, stop:1 {input_bg_lighter});
                color: {colors['INPUT_FG']}; border: 1px solid {colors['ACCENT_BORDER']};
                border-radius: 5px; padding: 7px; font-size: {font_size_normal_str}; min-height: 20px;
            }}
            QLineEdit::placeholder {{ color: {colors['PLACEHOLDER_FG']}; }}
            QDateEdit::drop-down, QComboBox::drop-down {{ 
                subcontrol-origin: padding; subcontrol-position: top right; width: 20px;
                border-left-width: 1px; border-left-color: {colors['ACCENT_BORDER']}; border-left-style: solid;
                border-top-right-radius: 3px; border-bottom-right-radius: 3px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['INPUT_BG']}, stop:1 {colors['BG_MAIN']});
            }}
            QDateEdit::down-arrow, QComboBox::down-arrow {{ image: url(:/qt-project.org/styles/commonstyle/images/standardbutton-down-arrow.png); }}
            QComboBox QAbstractItemView {{ 
                background-color: {colors['INPUT_BG']}; color: {colors['INPUT_FG']};
                selection-background-color: {colors['BUTTON_PINK_BG']}; selection-color: {colors['BUTTON_PINK_FG']};
                border: 1px solid {colors['ACCENT_BORDER']};
            }}
            QCalendarWidget QWidget {{ alternate-background-color: {colors['INPUT_BG']}; background-color: {colors['BG_MAIN']}; color: {colors['TEXT_COLOR']}; }} 
            QCalendarWidget QAbstractItemView:enabled {{ color: {colors['INPUT_FG']};
                selection-background-color: {colors['BUTTON_PINK_BG']}; selection-color: {colors['BUTTON_PINK_FG']}; font-size: {font_size_small_str};
            }}
            QCalendarWidget QToolButton {{ color: {colors['TEXT_COLOR']}; background-color: {colors['CALENDAR_HEADER_BG']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 3px; padding: 5px; font-size: {font_size_normal_str};
            }}
            QCalendarWidget QToolButton:hover {{ background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']}; }}
            QTextEdit#logConsole {{ 
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['LOG_BG']}, stop:1 {log_bg_lighter});
                color: {colors['LOG_FG']}; border: 1px solid {colors['ACCENT_BORDER']};
                border-radius: 4px; font-family: 'Consolas', '{QT_FLUTTER_FONT_FAMILY}', monospace; font-size: {font_size_log_str}; padding: 3px;
            }}
            QProgressBar {{ border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 5px; text-align: center;
                background-color: {colors['PROGRESS_BG']}; color: {colors['TEXT_COLOR']};
                font-size: {font_size_small_str}; height: 24px;
            }}
            QProgressBar#overallProgressBar::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['PROGRESS_FG_OVERALL']}, stop:1 {progress_overall_lighter}); border-radius: 4px; margin: 1px; }}
            QProgressBar#monthlyProgressBar::chunk {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['PROGRESS_FG_MONTHLY']}, stop:1 {progress_monthly_lighter}); border-radius: 4px; margin: 1px; }}
            QCheckBox {{ spacing: 7px; color: {colors['TEXT_COLOR']}; font-size: {font_size_normal_str}; padding-top: 4px; padding-bottom: 4px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; background-color: {colors['INPUT_BG']}; }}
            QCheckBox::indicator:checked {{ background-color: {colors['BUTTON_PINK_BG']}; }}
            QCheckBox::indicator:hover {{ border: 1px solid {colors['BUTTON_PINK_BG']}; }}
            
            QPushButton#browseButton, QPushButton#indexBrowseButton {{ 
                background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 5px 10px; font-size: {font_size_normal_str}; min-height: 20px;
            }}
            QPushButton#browseButton:hover, QPushButton#indexBrowseButton:hover {{ background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']}; }}
            QPushButton#browseButton:pressed, QPushButton#indexBrowseButton:pressed {{ background-color: {button_pink_pressed}; }}
            
            QPushButton#startButton, QPushButton#startIndexAnalysisButton {{ 
                background-color: {colors['BUTTON_PINK_BG']}; color: {colors['BUTTON_PINK_FG']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 7px 15px; font-size: {font_size_normal_str}; font-weight: bold;
            }}
            QPushButton#startButton:hover, QPushButton#startIndexAnalysisButton:hover {{ background-color: {button_pink_hover}; }} 
            QPushButton#startButton:pressed, QPushButton#startIndexAnalysisButton:pressed {{ background-color: {button_pink_pressed}; }}
            QPushButton#startButton:disabled, QPushButton#startIndexAnalysisButton:disabled {{ 
                background-color: #555555; color: #AAAAAA; border-color: #666666; 
            }}
            
            QPushButton#cancelButton {{ 
                background-color: {colors['BUTTON_LAVENDER_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 6px 12px; font-size: {font_size_normal_str};
            }}
            QPushButton#cancelButton:hover {{ background-color: {button_lavender_hover}; }} 
            QPushButton#cancelButton:pressed {{ background-color: {button_lavender_pressed}; }}
            QPushButton#cancelButton:disabled {{ background-color: #555555; color: #AAAAAA; border-color: #666666; }}
            
            QPushButton#verifyButton {{ 
                background-color: {colors['BUTTON_YELLOW_BG']}; color: {colors['TEXT_COLOR']};
                border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 4px; padding: 6px 12px; font-size: {font_size_normal_str};
            }}
            QPushButton#verifyButton:hover {{ background-color: {button_yellow_hover}; }} 
            QPushButton#verifyButton:pressed {{ background-color: {button_yellow_pressed}; }}
            QPushButton#verifyButton:disabled {{ background-color: #555555; color: #AAAAAA; border-color: #666666; }}
            
            QGroupBox {{ border: 1px solid {colors['ACCENT_BORDER']}; border-radius: 5px; margin-top: 1ex; padding: 5px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: {colors['TEXT_COLOR']}; font-weight: bold; }}
            
            QMenuBar {{ background-color: {colors.get('BG_FRAME', '#252526')}; color: {colors.get('TEXT_COLOR', '#D4D4D4')}; font-size: {font_size_normal_str}; }}
            QMenuBar::item:selected {{ background-color: {colors.get('BUTTON_YELLOW_HOVER', '#5A5A5A')}; }}
            QMenu {{ background-color: {colors.get('BG_FRAME', '#252526')}; color: {colors.get('TEXT_COLOR', '#D4D4D4')}; border: 1px solid {colors['ACCENT_BORDER']}; }}
            QMenu::item:selected {{ background-color: {colors.get('BUTTON_YELLOW_HOVER', '#5A5A5A')}; }}

            QTabWidget::pane {{ border-top: 1px solid {colors['ACCENT_BORDER']}; margin-top: -1px; }}
            QTabBar::tab {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {colors['BG_FRAME']}, stop:1 {colors['BG_MAIN']});
                border: 1px solid {colors['ACCENT_BORDER']}; border-bottom-color: {colors['ACCENT_BORDER']}; 
                border-top-left-radius: 4px; border-top-right-radius: 4px;
                min-width: 8ex; padding: 8px 12px; margin-right: 2px; color: {colors['TEXT_COLOR']};
            }}
            QTabBar::tab:selected {{ 
                background: {colors['BG_MAIN']}; border-bottom-color: {colors['BG_MAIN']};
                color: {colors['TEXT_COLOR']}; font-weight: bold;
            }}
            QTabBar::tab:!selected:hover {{ background: {colors['BUTTON_LAVENDER_HOVER']}; }}
            QSplitter::handle {{ background-color: {colors['ACCENT_BORDER']}; height: 3px; width: 3px; }}
            QSplitter::handle:horizontal {{ height: 3px; }}
            QSplitter::handle:vertical {{ width: 3px; }}
        """
    
    def get_text(self, key: str, default: str = None) -> str:
        """Get themed text for the given key."""
        return FLUTTERSHY_TEXTS.get(key, default or key)
    
    def get_available_themes(self) -> list:
        """Get list of available theme names."""
        return list(THEMES.keys()) 