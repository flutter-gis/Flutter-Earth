"""Enhanced theme system for Flutter Earth GUI with MLP and Minecraft themes and categories."""
from typing import Dict, Any, Optional
from PyQt6 import QtGui

# --- MAIN THEMES ---
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
    "PROGRESS_FG_OVERALL": "#FFC0CB",
    "PROGRESS_FG_MONTHLY": "#FFF41E",
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
    "ACCENT_BORDER": "#007ACC",
    "PLACEHOLDER_FG": "#7A7A7A",
    "BUTTON_PINK_BG": "#007ACC",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#4A4A4A",
    "BUTTON_YELLOW_FG": "#D4D4D4",
    "BUTTON_YELLOW_HOVER": "#5A5A5A",
    "BUTTON_LAVENDER_BG": "#333333",
    "BUTTON_LAVENDER_FG": "#D4D4D4",
    "BUTTON_LAVENDER_HOVER": "#404040",
    "PROGRESS_BG": "#2A2A2A",
    "PROGRESS_FG_OVERALL": "#007ACC",
    "PROGRESS_FG_MONTHLY": "#1E90FF",
    "CALENDAR_HEADER_BG": "#252526",
    "TEXT_LIGHT": "#A0A0A0",
    "LOG_BG": "#1E1E1E",
    "LOG_FG": "#D4D4D4",
    "MAP_BUTTON_FG": "#D4D4D4"
}

# --- MLP THEMES ---
RAINBOW_DASH_COLORS = {
    "BG_MAIN": "#E3F2FD",
    "BG_FRAME": "#BBDEFB",
    "TEXT_COLOR": "#1565C0",
    "INPUT_BG": "#E1F5FE",
    "INPUT_FG": "#0D47A1",
    "ACCENT_BORDER": "#42A5F5",
    "PLACEHOLDER_FG": "#64B5F6",
    "BUTTON_PINK_BG": "#2196F3",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FF9800",
    "BUTTON_YELLOW_FG": "#FFFFFF",
    "BUTTON_YELLOW_HOVER": "#FFB74D",
    "BUTTON_LAVENDER_BG": "#9C27B0",
    "BUTTON_LAVENDER_FG": "#FFFFFF",
    "BUTTON_LAVENDER_HOVER": "#BA68C8",
    "PROGRESS_BG": "#E8F4FD",
    "PROGRESS_FG_OVERALL": "#2196F3",
    "PROGRESS_FG_MONTHLY": "#FF9800",
    "CALENDAR_HEADER_BG": "#BBDEFB",
    "TEXT_LIGHT": "#1976D2",
    "LOG_BG": "#E1F5FE",
    "LOG_FG": "#0D47A1",
    "MAP_BUTTON_FG": "#1565C0"
}
APPLEJACK_COLORS = {
    "BG_MAIN": "#FFF8E1",
    "BG_FRAME": "#FFECB3",
    "TEXT_COLOR": "#8D6E63",
    "INPUT_BG": "#FFFDE7",
    "INPUT_FG": "#5D4037",
    "ACCENT_BORDER": "#FFB74D",
    "PLACEHOLDER_FG": "#BCAAA4",
    "BUTTON_PINK_BG": "#FF9800",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFC107",
    "BUTTON_YELLOW_FG": "#5D4037",
    "BUTTON_YELLOW_HOVER": "#FFD54F",
    "BUTTON_LAVENDER_BG": "#8D6E63",
    "BUTTON_LAVENDER_FG": "#FFFFFF",
    "BUTTON_LAVENDER_HOVER": "#A1887F",
    "PROGRESS_BG": "#FFF3E0",
    "PROGRESS_FG_OVERALL": "#FF9800",
    "PROGRESS_FG_MONTHLY": "#FFC107",
    "CALENDAR_HEADER_BG": "#FFECB3",
    "TEXT_LIGHT": "#8D6E63",
    "LOG_BG": "#FFFDE7",
    "LOG_FG": "#5D4037",
    "MAP_BUTTON_FG": "#8D6E63"
}
RARITY_COLORS = {
    "BG_MAIN": "#F3E5F5",
    "BG_FRAME": "#E1BEE7",
    "TEXT_COLOR": "#6A1B9A",
    "INPUT_BG": "#F8BBD0",
    "INPUT_FG": "#6A1B9A",
    "ACCENT_BORDER": "#CE93D8",
    "PLACEHOLDER_FG": "#BA68C8",
    "BUTTON_PINK_BG": "#AB47BC",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFF176",
    "BUTTON_YELLOW_FG": "#6A1B9A",
    "BUTTON_YELLOW_HOVER": "#FFF59D",
    "BUTTON_LAVENDER_BG": "#9575CD",
    "BUTTON_LAVENDER_FG": "#FFFFFF",
    "BUTTON_LAVENDER_HOVER": "#B39DDB",
    "PROGRESS_BG": "#F3E5F5",
    "PROGRESS_FG_OVERALL": "#AB47BC",
    "PROGRESS_FG_MONTHLY": "#FFF176",
    "CALENDAR_HEADER_BG": "#E1BEE7",
    "TEXT_LIGHT": "#6A1B9A",
    "LOG_BG": "#F8BBD0",
    "LOG_FG": "#6A1B9A",
    "MAP_BUTTON_FG": "#6A1B9A"
}
PINKIE_PIE_COLORS = {
    "BG_MAIN": "#FFF0F6",
    "BG_FRAME": "#FFD1E8",
    "TEXT_COLOR": "#E91E63",
    "INPUT_BG": "#FFF8FB",
    "INPUT_FG": "#C2185B",
    "ACCENT_BORDER": "#F06292",
    "PLACEHOLDER_FG": "#F8BBD0",
    "BUTTON_PINK_BG": "#F06292",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFF176",
    "BUTTON_YELLOW_FG": "#E91E63",
    "BUTTON_YELLOW_HOVER": "#FFF59D",
    "BUTTON_LAVENDER_BG": "#BA68C8",
    "BUTTON_LAVENDER_FG": "#FFFFFF",
    "BUTTON_LAVENDER_HOVER": "#CE93D8",
    "PROGRESS_BG": "#FFF0F6",
    "PROGRESS_FG_OVERALL": "#F06292",
    "PROGRESS_FG_MONTHLY": "#FFF176",
    "CALENDAR_HEADER_BG": "#FFD1E8",
    "TEXT_LIGHT": "#E91E63",
    "LOG_BG": "#FFF8FB",
    "LOG_FG": "#C2185B",
    "MAP_BUTTON_FG": "#E91E63"
}
TWILIGHT_SPARKLE_COLORS = {
    "BG_MAIN": "#EDE7F6",
    "BG_FRAME": "#D1C4E9",
    "TEXT_COLOR": "#4527A0",
    "INPUT_BG": "#E1BEE7",
    "INPUT_FG": "#4527A0",
    "ACCENT_BORDER": "#7E57C2",
    "PLACEHOLDER_FG": "#B39DDB",
    "BUTTON_PINK_BG": "#7E57C2",
    "BUTTON_PINK_FG": "#FFFFFF",
    "BUTTON_YELLOW_BG": "#FFD54F",
    "BUTTON_YELLOW_FG": "#4527A0",
    "BUTTON_YELLOW_HOVER": "#FFF176",
    "BUTTON_LAVENDER_BG": "#5E35B1",
    "BUTTON_LAVENDER_FG": "#FFFFFF",
    "BUTTON_LAVENDER_HOVER": "#9575CD",
    "PROGRESS_BG": "#EDE7F6",
    "PROGRESS_FG_OVERALL": "#7E57C2",
    "PROGRESS_FG_MONTHLY": "#FFD54F",
    "CALENDAR_HEADER_BG": "#D1C4E9",
    "TEXT_LIGHT": "#4527A0",
    "LOG_BG": "#E1BEE7",
    "LOG_FG": "#4527A0",
    "MAP_BUTTON_FG": "#4527A0"
}
# Add Celestia, Luna, Starlight Glimmer, Trixie, Derpy, Cadence here (colors omitted for brevity)
CELESTIA_COLORS = {"BG_MAIN": "#FFF8E1", "BG_FRAME": "#FFFDE7", "TEXT_COLOR": "#FFD700", "INPUT_BG": "#FFFDE7", "INPUT_FG": "#FFD700", "ACCENT_BORDER": "#FFFACD", "PLACEHOLDER_FG": "#FFE082", "BUTTON_PINK_BG": "#FFD700", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#FFFACD", "BUTTON_YELLOW_FG": "#FFD700", "BUTTON_YELLOW_HOVER": "#FFFDE7", "BUTTON_LAVENDER_BG": "#FFF8E1", "BUTTON_LAVENDER_FG": "#FFD700", "BUTTON_LAVENDER_HOVER": "#FFF9C4", "PROGRESS_BG": "#FFFDE7", "PROGRESS_FG_OVERALL": "#FFD700", "PROGRESS_FG_MONTHLY": "#FFFACD", "CALENDAR_HEADER_BG": "#FFF8E1", "TEXT_LIGHT": "#FFD700", "LOG_BG": "#FFFDE7", "LOG_FG": "#FFD700", "MAP_BUTTON_FG": "#FFD700"}
LUNA_COLORS = {"BG_MAIN": "#232946", "BG_FRAME": "#2E335B", "TEXT_COLOR": "#A3A8F0", "INPUT_BG": "#232946", "INPUT_FG": "#A3A8F0", "ACCENT_BORDER": "#5A5E9A", "PLACEHOLDER_FG": "#6C6F99", "BUTTON_PINK_BG": "#5A5E9A", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#A3A8F0", "BUTTON_YELLOW_FG": "#232946", "BUTTON_YELLOW_HOVER": "#6C6F99", "BUTTON_LAVENDER_BG": "#232946", "BUTTON_LAVENDER_FG": "#A3A8F0", "BUTTON_LAVENDER_HOVER": "#2E335B", "PROGRESS_BG": "#2E335B", "PROGRESS_FG_OVERALL": "#5A5E9A", "PROGRESS_FG_MONTHLY": "#A3A8F0", "CALENDAR_HEADER_BG": "#232946", "TEXT_LIGHT": "#A3A8F0", "LOG_BG": "#232946", "LOG_FG": "#A3A8F0", "MAP_BUTTON_FG": "#A3A8F0"}
STARLIGHT_COLORS = {"BG_MAIN": "#E1F5FE", "BG_FRAME": "#B3E5FC", "TEXT_COLOR": "#7C4DFF", "INPUT_BG": "#EDE7F6", "INPUT_FG": "#7C4DFF", "ACCENT_BORDER": "#B388FF", "PLACEHOLDER_FG": "#B3E5FC", "BUTTON_PINK_BG": "#7C4DFF", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#B388FF", "BUTTON_YELLOW_FG": "#7C4DFF", "BUTTON_YELLOW_HOVER": "#E1BEE7", "BUTTON_LAVENDER_BG": "#B388FF", "BUTTON_LAVENDER_FG": "#FFFFFF", "BUTTON_LAVENDER_HOVER": "#D1C4E9", "PROGRESS_BG": "#EDE7F6", "PROGRESS_FG_OVERALL": "#7C4DFF", "PROGRESS_FG_MONTHLY": "#B388FF", "CALENDAR_HEADER_BG": "#B3E5FC", "TEXT_LIGHT": "#7C4DFF", "LOG_BG": "#EDE7F6", "LOG_FG": "#7C4DFF", "MAP_BUTTON_FG": "#7C4DFF"}
TRIXIE_COLORS = {"BG_MAIN": "#E3E6F3", "BG_FRAME": "#B3B8D6", "TEXT_COLOR": "#3F51B5", "INPUT_BG": "#E8EAF6", "INPUT_FG": "#3F51B5", "ACCENT_BORDER": "#7986CB", "PLACEHOLDER_FG": "#B3B8D6", "BUTTON_PINK_BG": "#3F51B5", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#B3B8D6", "BUTTON_YELLOW_FG": "#3F51B5", "BUTTON_YELLOW_HOVER": "#C5CAE9", "BUTTON_LAVENDER_BG": "#7986CB", "BUTTON_LAVENDER_FG": "#FFFFFF", "BUTTON_LAVENDER_HOVER": "#9FA8DA", "PROGRESS_BG": "#E8EAF6", "PROGRESS_FG_OVERALL": "#3F51B5", "PROGRESS_FG_MONTHLY": "#B3B8D6", "CALENDAR_HEADER_BG": "#B3B8D6", "TEXT_LIGHT": "#3F51B5", "LOG_BG": "#E8EAF6", "LOG_FG": "#3F51B5", "MAP_BUTTON_FG": "#3F51B5"}
DERPY_COLORS = {"BG_MAIN": "#F0F4C3", "BG_FRAME": "#E6EE9C", "TEXT_COLOR": "#757575", "INPUT_BG": "#F0F4C3", "INPUT_FG": "#757575", "ACCENT_BORDER": "#BDBDBD", "PLACEHOLDER_FG": "#E6EE9C", "BUTTON_PINK_BG": "#BDBDBD", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#FFF176", "BUTTON_YELLOW_FG": "#757575", "BUTTON_YELLOW_HOVER": "#FFF59D", "BUTTON_LAVENDER_BG": "#E6EE9C", "BUTTON_LAVENDER_FG": "#757575", "BUTTON_LAVENDER_HOVER": "#F0F4C3", "PROGRESS_BG": "#F0F4C3", "PROGRESS_FG_OVERALL": "#BDBDBD", "PROGRESS_FG_MONTHLY": "#FFF176", "CALENDAR_HEADER_BG": "#E6EE9C", "TEXT_LIGHT": "#757575", "LOG_BG": "#F0F4C3", "LOG_FG": "#757575", "MAP_BUTTON_FG": "#757575"}
CADENCE_COLORS = {"BG_MAIN": "#F8BBD0", "BG_FRAME": "#F48FB1", "TEXT_COLOR": "#AD1457", "INPUT_BG": "#FCE4EC", "INPUT_FG": "#AD1457", "ACCENT_BORDER": "#F06292", "PLACEHOLDER_FG": "#F8BBD0", "BUTTON_PINK_BG": "#F06292", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#FFF176", "BUTTON_YELLOW_FG": "#AD1457", "BUTTON_YELLOW_HOVER": "#FFF59D", "BUTTON_LAVENDER_BG": "#BA68C8", "BUTTON_LAVENDER_FG": "#FFFFFF", "BUTTON_LAVENDER_HOVER": "#CE93D8", "PROGRESS_BG": "#F8BBD0", "PROGRESS_FG_OVERALL": "#F06292", "PROGRESS_FG_MONTHLY": "#FFF176", "CALENDAR_HEADER_BG": "#F48FB1", "TEXT_LIGHT": "#AD1457", "LOG_BG": "#FCE4EC", "LOG_FG": "#AD1457", "MAP_BUTTON_FG": "#AD1457"}

# --- MINECRAFT THEMES ---
STEVE_COLORS = {"BG_MAIN": "#A7C7E7", "BG_FRAME": "#6D9DC5", "TEXT_COLOR": "#3C3C3C", "INPUT_BG": "#B7E1CD", "INPUT_FG": "#3C3C3C", "ACCENT_BORDER": "#6D9DC5", "PLACEHOLDER_FG": "#A7C7E7", "BUTTON_PINK_BG": "#6D9DC5", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#B7E1CD", "BUTTON_YELLOW_FG": "#3C3C3C", "BUTTON_YELLOW_HOVER": "#C3E6CB", "BUTTON_LAVENDER_BG": "#A7C7E7", "BUTTON_LAVENDER_FG": "#3C3C3C", "BUTTON_LAVENDER_HOVER": "#B7E1CD", "PROGRESS_BG": "#A7C7E7", "PROGRESS_FG_OVERALL": "#6D9DC5", "PROGRESS_FG_MONTHLY": "#B7E1CD", "CALENDAR_HEADER_BG": "#6D9DC5", "TEXT_LIGHT": "#3C3C3C", "LOG_BG": "#B7E1CD", "LOG_FG": "#3C3C3C", "MAP_BUTTON_FG": "#3C3C3C"}
CREEPER_COLORS = {"BG_MAIN": "#4CAF50", "BG_FRAME": "#388E3C", "TEXT_COLOR": "#212121", "INPUT_BG": "#A5D6A7", "INPUT_FG": "#212121", "ACCENT_BORDER": "#388E3C", "PLACEHOLDER_FG": "#4CAF50", "BUTTON_PINK_BG": "#388E3C", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#A5D6A7", "BUTTON_YELLOW_FG": "#212121", "BUTTON_YELLOW_HOVER": "#C8E6C9", "BUTTON_LAVENDER_BG": "#4CAF50", "BUTTON_LAVENDER_FG": "#212121", "BUTTON_LAVENDER_HOVER": "#A5D6A7", "PROGRESS_BG": "#4CAF50", "PROGRESS_FG_OVERALL": "#388E3C", "PROGRESS_FG_MONTHLY": "#A5D6A7", "CALENDAR_HEADER_BG": "#388E3C", "TEXT_LIGHT": "#212121", "LOG_BG": "#A5D6A7", "LOG_FG": "#212121", "MAP_BUTTON_FG": "#212121"}
ENDERMAN_COLORS = {"BG_MAIN": "#212121", "BG_FRAME": "#512DA8", "TEXT_COLOR": "#E1BEE7", "INPUT_BG": "#512DA8", "INPUT_FG": "#E1BEE7", "ACCENT_BORDER": "#9575CD", "PLACEHOLDER_FG": "#9575CD", "BUTTON_PINK_BG": "#512DA8", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#9575CD", "BUTTON_YELLOW_FG": "#E1BEE7", "BUTTON_YELLOW_HOVER": "#7E57C2", "BUTTON_LAVENDER_BG": "#212121", "BUTTON_LAVENDER_FG": "#E1BEE7", "BUTTON_LAVENDER_HOVER": "#512DA8", "PROGRESS_BG": "#212121", "PROGRESS_FG_OVERALL": "#512DA8", "PROGRESS_FG_MONTHLY": "#9575CD", "CALENDAR_HEADER_BG": "#512DA8", "TEXT_LIGHT": "#E1BEE7", "LOG_BG": "#512DA8", "LOG_FG": "#E1BEE7", "MAP_BUTTON_FG": "#E1BEE7"}
ZOMBIE_COLORS = {"BG_MAIN": "#A5D6A7", "BG_FRAME": "#388E3C", "TEXT_COLOR": "#212121", "INPUT_BG": "#C8E6C9", "INPUT_FG": "#212121", "ACCENT_BORDER": "#388E3C", "PLACEHOLDER_FG": "#A5D6A7", "BUTTON_PINK_BG": "#388E3C", "BUTTON_PINK_FG": "#FFFFFF", "BUTTON_YELLOW_BG": "#A5D6A7", "BUTTON_YELLOW_FG": "#212121", "BUTTON_YELLOW_HOVER": "#C8E6C9", "BUTTON_LAVENDER_BG": "#388E3C", "BUTTON_LAVENDER_FG": "#FFFFFF", "BUTTON_LAVENDER_HOVER": "#A5D6A7", "PROGRESS_BG": "#A5D6A7", "PROGRESS_FG_OVERALL": "#388E3C", "PROGRESS_FG_MONTHLY": "#A5D6A7", "CALENDAR_HEADER_BG": "#388E3C", "TEXT_LIGHT": "#212121", "LOG_BG": "#C8E6C9", "LOG_FG": "#212121", "MAP_BUTTON_FG": "#212121"}

# --- THEME METADATA ---
THEMES = {
    # Main
    "Fluttershy": FLUTTERSHY_COLORS,
    "Night Mode": NIGHT_MODE_COLORS,
    # MLP
    "Rainbow Dash": RAINBOW_DASH_COLORS,
    "Applejack": APPLEJACK_COLORS,
    "Rarity": RARITY_COLORS,
    "Pinkie Pie": PINKIE_PIE_COLORS,
    "Twilight Sparkle": TWILIGHT_SPARKLE_COLORS,
    "Celestia": CELESTIA_COLORS,
    "Luna": LUNA_COLORS,
    "Starlight Glimmer": STARLIGHT_COLORS,
    "Trixie": TRIXIE_COLORS,
    "Derpy": DERPY_COLORS,
    "Cadence": CADENCE_COLORS,
    # Minecraft
    "Steve": STEVE_COLORS,
    "Creeper": CREEPER_COLORS,
    "Enderman": ENDERMAN_COLORS,
    "Zombie": ZOMBIE_COLORS,
}
THEMES_METADATA = {
    "Fluttershy": {"category": "Main", "display": "Fluttershy (Default)"},
    "Night Mode": {"category": "Main", "display": "Night Mode"},
    "Rainbow Dash": {"category": "MLP", "display": "Rainbow Dash"},
    "Applejack": {"category": "MLP", "display": "Applejack"},
    "Rarity": {"category": "MLP", "display": "Rarity"},
    "Pinkie Pie": {"category": "MLP", "display": "Pinkie Pie"},
    "Twilight Sparkle": {"category": "MLP", "display": "Twilight Sparkle"},
    "Celestia": {"category": "MLP", "display": "Princess Celestia"},
    "Luna": {"category": "MLP", "display": "Princess Luna"},
    "Starlight Glimmer": {"category": "MLP", "display": "Starlight Glimmer"},
    "Trixie": {"category": "MLP", "display": "Trixie the Powerful"},
    "Derpy": {"category": "MLP", "display": "Derpy Hooves"},
    "Cadence": {"category": "MLP", "display": "Princess Cadence"},
    "Steve": {"category": "MC", "display": "Steve"},
    "Creeper": {"category": "MC", "display": "Creeper"},
    "Enderman": {"category": "MC", "display": "Enderman"},
    "Zombie": {"category": "MC", "display": "Zombie"},
}
DEFAULT_THEME = "Fluttershy"

# Theme text definitions
FLUTTERSHY_TEXTS = {
    "window_title_main": "💖 Flutter Earth - Gentle GEE Downloader 💖",
    "start_date_label": "Start Date for our gentle adventure 🗓️:",
    "end_date_label": "End Date for our gentle adventure 🗓️:",
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

RAINBOW_DASH_TEXTS = {
    "window_title_main": "⚡ Flutter Earth - Awesome GEE Downloader ⚡",
    "start_date_label": "Start Date for our awesome adventure 🗓️:",
    "end_date_label": "End Date for our awesome adventure 🗓️:",
    "output_dir_label": "A cool place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like a lightning bolt ⚡:",
    "log_console_label": "Messages from the Earth Engine 👇:",
    "run_button": "⚡ Begin Download ⚡",
    "cancel_button": "🛑 Stop Everything 🛑",
    "run_button_processing": "Working at lightning speed... ⚡",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some awesome downloads! ⚡",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. That's not awesome.",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's do this! ⚡",
    "status_bar_input_error_prefix": "Oops! Something's not awesome: ",
    "status_bar_processing_started": "Our awesome download has begun...",
    "status_bar_cancellation_requested": "Stopping our journey for now...",
    "status_bar_processing_finished": "Our adventure is complete! Check your treasures.",
}

APPLEJACK_TEXTS = {
    "window_title_main": "🍎 Flutter Earth - Honest GEE Downloader 🍎",
    "start_date_label": "Start Date for our honest work 🗓️:",
    "end_date_label": "End Date for our honest work 🗓️:",
    "output_dir_label": "A good place for your harvest 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like tending the farm 🌾:",
    "log_console_label": "Messages from the Earth Engine 👇:",
    "run_button": "🍎 Begin Download 🍎",
    "cancel_button": "🛑 Stop Work 🛑",
    "run_button_processing": "Working hard... 🍎",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some honest downloads! 🍎",
    "status_bar_ee_init_fail": "Well shucks, EE couldn't connect.",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's get to work! 🍎",
    "status_bar_input_error_prefix": "Well shucks, something's not right: ",
    "status_bar_processing_started": "Our honest download has begun...",
    "status_bar_cancellation_requested": "Stopping our work for now...",
    "status_bar_processing_finished": "Our work is complete! Check your harvest.",
}

RARITY_TEXTS = {
    "window_title_main": "💎 Flutter Earth - Fabulous GEE Downloader 💎",
    "start_date_label": "Start Date for our fabulous adventure 🗓️:",
    "end_date_label": "End Date for our fabulous adventure 🗓️:",
    "output_dir_label": "A fabulous place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like creating a masterpiece 🎨:",
    "log_console_label": "Messages from the Earth Engine 👇:",
    "run_button": "💎 Begin Download 💎",
    "cancel_button": "💔 Stop Everything 💔",
    "run_button_processing": "Creating something fabulous... 💎",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some fabulous downloads! 💎",
    "status_bar_ee_init_fail": "Oh my, EE couldn't connect. How dreadful.",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's make it fabulous! 💎",
    "status_bar_input_error_prefix": "Oh my, something's not fabulous: ",
    "status_bar_processing_started": "Our fabulous download has begun...",
    "status_bar_cancellation_requested": "Stopping our fabulous journey for now...",
    "status_bar_processing_finished": "Our fabulous adventure is complete! Check your treasures.",
}

PINKIE_PIE_TEXTS = {
    "window_title_main": "🎉 Flutter Earth - Party GEE Downloader 🎉",
    "start_date_label": "Start Date for our party adventure 🗓️:",
    "end_date_label": "End Date for our party adventure 🗓️:",
    "output_dir_label": "A party place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like throwing a party 🎉:",
    "log_console_label": "Messages from the Earth Engine 👇:",
    "run_button": "🎉 Begin Download 🎉",
    "cancel_button": "😢 Stop Party 😢",
    "run_button_processing": "Party time... 🎉",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some party downloads! 🎉",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. No party!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's party! 🎉",
    "status_bar_input_error_prefix": "Oopsie! Something's not party: ",
    "status_bar_processing_started": "Our party download has begun...",
    "status_bar_cancellation_requested": "Stopping our party for now...",
    "status_bar_processing_finished": "Our party is complete! Check your treasures.",
}

TWILIGHT_SPARKLE_TEXTS = {
    "window_title_main": "📚 Flutter Earth - Studious GEE Downloader 📚",
    "start_date_label": "Start Date for our research adventure 🗓️:",
    "end_date_label": "End Date for our research adventure 🗓️:",
    "output_dir_label": "A scholarly place for your data 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like conducting research 📊:",
    "log_console_label": "Research notes from the Earth Engine 👇:",
    "run_button": "📚 Begin Download 📚",
    "cancel_button": "🛑 Stop Research 🛑",
    "run_button_processing": "Conducting research... 📚",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some scholarly downloads! 📚",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. Research interrupted!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's research! 📚",
    "status_bar_input_error_prefix": "Research error: ",
    "status_bar_processing_started": "Our research has begun...",
    "status_bar_cancellation_requested": "Stopping our research for now...",
    "status_bar_processing_finished": "Our research is complete! Check your data.",
}

CELESTIA_TEXTS = {
    "window_title_main": "☀️ Flutter Earth - Royal GEE Downloader ☀️",
    "start_date_label": "Start Date for our royal decree 🗓️:",
    "end_date_label": "End Date for our royal decree 🗓️:",
    "output_dir_label": "A royal chamber for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our royal journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like raising the sun ☀️:",
    "log_console_label": "Royal messages from the Earth Engine 👇:",
    "run_button": "☀️ Begin Download ☀️",
    "cancel_button": "👑 Halt Everything 👑",
    "run_button_processing": "Raising the sun... ☀️",
    "cancel_button_cancelling": "Halting...",
    "status_bar_ready": "Ready for some royal downloads! ☀️",
    "status_bar_ee_init_fail": "Oh my, EE couldn't connect. The sun shall not rise!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let us proceed with royal grace! ☀️",
    "status_bar_input_error_prefix": "Oh my, something's not royal: ",
    "status_bar_processing_started": "Our royal download has begun...",
    "status_bar_cancellation_requested": "Halting our royal journey for now...",
    "status_bar_processing_finished": "Our royal adventure is complete! Check your treasures.",
}

LUNA_TEXTS = {
    "window_title_main": "🌙 Flutter Earth - Lunar GEE Downloader 🌙",
    "start_date_label": "Start Date for our lunar adventure 🗓️:",
    "end_date_label": "End Date for our lunar adventure 🗓️:",
    "output_dir_label": "A lunar chamber for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our lunar journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like raising the moon 🌙:",
    "log_console_label": "Lunar whispers from the Earth Engine 👇:",
    "run_button": "🌙 Begin Download 🌙",
    "cancel_button": "🌑 Halt Everything 🌑",
    "run_button_processing": "Raising the moon... 🌙",
    "cancel_button_cancelling": "Halting...",
    "status_bar_ready": "Ready for some lunar downloads! 🌙",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. The night shall be eternal!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let us proceed under the stars! 🌙",
    "status_bar_input_error_prefix": "Oh no, something's not lunar: ",
    "status_bar_processing_started": "Our lunar download has begun...",
    "status_bar_cancellation_requested": "Halting our lunar journey for now...",
    "status_bar_processing_finished": "Our lunar adventure is complete! Check your treasures.",
}

STARLIGHT_TEXTS = {
    "window_title_main": "✨ Flutter Earth - Magical GEE Downloader ✨",
    "start_date_label": "Start Date for our magical adventure 🗓️:",
    "end_date_label": "End Date for our magical adventure 🗓️:",
    "output_dir_label": "A magical place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our magical journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like casting a spell ✨:",
    "log_console_label": "Magical messages from the Earth Engine 👇:",
    "run_button": "✨ Begin Download ✨",
    "cancel_button": "🔮 Stop Magic 🔮",
    "run_button_processing": "Casting spells... ✨",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some magical downloads! ✨",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. The magic is broken!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's work some magic! ✨",
    "status_bar_input_error_prefix": "Oh no, something's not magical: ",
    "status_bar_processing_started": "Our magical download has begun...",
    "status_bar_cancellation_requested": "Stopping our magic for now...",
    "status_bar_processing_finished": "Our magical adventure is complete! Check your treasures.",
}

TRIXIE_TEXTS = {
    "window_title_main": "🎪 Flutter Earth - Great & Powerful GEE Downloader 🎪",
    "start_date_label": "Start Date for our great & powerful adventure 🗓️:",
    "end_date_label": "End Date for our great & powerful adventure 🗓️:",
    "output_dir_label": "A great & powerful place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our great & powerful journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like performing a great trick 🎪:",
    "log_console_label": "Great & powerful messages from the Earth Engine 👇:",
    "run_button": "🎪 Begin Download 🎪",
    "cancel_button": "🎭 Stop Show 🎭",
    "run_button_processing": "Performing great tricks... 🎪",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some great & powerful downloads! 🎪",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. The Great & Powerful Trixie is disappointed!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's show them all! 🎪",
    "status_bar_input_error_prefix": "Oh no, something's not great & powerful: ",
    "status_bar_processing_started": "Our great & powerful download has begun...",
    "status_bar_cancellation_requested": "Stopping our great show for now...",
    "status_bar_processing_finished": "Our great & powerful adventure is complete! Check your treasures.",
}

DERPY_TEXTS = {
    "window_title_main": "🥧 Flutter Earth - Muffin GEE Downloader 🥧",
    "start_date_label": "Start Date for our muffin adventure 🗓️:",
    "end_date_label": "End Date for our muffin adventure 🗓️:",
    "output_dir_label": "A muffin place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our muffin journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like baking muffins 🥧:",
    "log_console_label": "Muffin messages from the Earth Engine 👇:",
    "run_button": "🥧 Begin Download 🥧",
    "cancel_button": "🍪 Stop Baking 🍪",
    "run_button_processing": "Baking muffins... 🥧",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some muffin downloads! 🥧",
    "status_bar_ee_init_fail": "Oops! EE couldn't connect. No muffins!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's bake some muffins! 🥧",
    "status_bar_input_error_prefix": "Oops, something's not muffin: ",
    "status_bar_processing_started": "Our muffin download has begun...",
    "status_bar_cancellation_requested": "Stopping our muffin baking for now...",
    "status_bar_processing_finished": "Our muffin adventure is complete! Check your treasures.",
}

CADENCE_TEXTS = {
    "window_title_main": "💕 Flutter Earth - Loving GEE Downloader 💕",
    "start_date_label": "Start Date for our loving adventure 🗓️:",
    "end_date_label": "End Date for our loving adventure 🗓️:",
    "output_dir_label": "A loving place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our loving journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like spreading love 💕:",
    "log_console_label": "Loving messages from the Earth Engine 👇:",
    "run_button": "💕 Begin Download 💕",
    "cancel_button": "💔 Stop Love 💔",
    "run_button_processing": "Spreading love... 💕",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some loving downloads! 💕",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. Love is lost!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's spread some love! 💕",
    "status_bar_input_error_prefix": "Oh no, something's not loving: ",
    "status_bar_processing_started": "Our loving download has begun...",
    "status_bar_cancellation_requested": "Stopping our love for now...",
    "status_bar_processing_finished": "Our loving adventure is complete! Check your treasures.",
}

# Minecraft themes
STEVE_TEXTS = {
    "window_title_main": "⛏️ Flutter Earth - Mining GEE Downloader ⛏️",
    "start_date_label": "Start Date for our mining adventure 🗓️:",
    "end_date_label": "End Date for our mining adventure 🗓️:",
    "output_dir_label": "A mining place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our mining journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like mining diamonds 💎:",
    "log_console_label": "Mining messages from the Earth Engine 👇:",
    "run_button": "⛏️ Begin Download ⛏️",
    "cancel_button": "🛑 Stop Mining 🛑",
    "run_button_processing": "Mining... ⛏️",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some mining downloads! ⛏️",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. No diamonds!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's mine some data! ⛏️",
    "status_bar_input_error_prefix": "Oh no, something's not mining: ",
    "status_bar_processing_started": "Our mining download has begun...",
    "status_bar_cancellation_requested": "Stopping our mining for now...",
    "status_bar_processing_finished": "Our mining adventure is complete! Check your treasures.",
}

CREEPER_TEXTS = {
    "window_title_main": "💥 Flutter Earth - Explosive GEE Downloader 💥",
    "start_date_label": "Start Date for our explosive adventure 🗓️:",
    "end_date_label": "End Date for our explosive adventure 🗓️:",
    "output_dir_label": "An explosive place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our explosive journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like creating explosions 💥:",
    "log_console_label": "Explosive messages from the Earth Engine 👇:",
    "run_button": "💥 Begin Download 💥",
    "cancel_button": "💣 Stop Explosions 💣",
    "run_button_processing": "Creating explosions... 💥",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some explosive downloads! 💥",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. No explosions!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's make some explosions! 💥",
    "status_bar_input_error_prefix": "Oh no, something's not explosive: ",
    "status_bar_processing_started": "Our explosive download has begun...",
    "status_bar_cancellation_requested": "Stopping our explosions for now...",
    "status_bar_processing_finished": "Our explosive adventure is complete! Check your treasures.",
}

ENDERMAN_TEXTS = {
    "window_title_main": "👁️ Flutter Earth - End GEE Downloader 👁️",
    "start_date_label": "Start Date for our end adventure 🗓️:",
    "end_date_label": "End Date for our end adventure 🗓️:",
    "output_dir_label": "An end place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our end journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like teleporting 👁️:",
    "log_console_label": "End messages from the Earth Engine 👇:",
    "run_button": "👁️ Begin Download 👁️",
    "cancel_button": "🌌 Stop Teleporting 🌌",
    "run_button_processing": "Teleporting... 👁️",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some end downloads! 👁️",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. No teleporting!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's teleport some data! 👁️",
    "status_bar_input_error_prefix": "Oh no, something's not end: ",
    "status_bar_processing_started": "Our end download has begun...",
    "status_bar_cancellation_requested": "Stopping our teleporting for now...",
    "status_bar_processing_finished": "Our end adventure is complete! Check your treasures.",
}

ZOMBIE_TEXTS = {
    "window_title_main": "🧟 Flutter Earth - Undead GEE Downloader 🧟",
    "start_date_label": "Start Date for our undead adventure 🗓️:",
    "end_date_label": "End Date for our undead adventure 🗓️:",
    "output_dir_label": "An undead place for your treasures 📁:",
    "overwrite_label": "Refresh existing monthly pictures? 📜:",
    "overall_progress_label": "Our undead journey's progress, step by step 🐾:",
    "monthly_progress_label": "Each task, like eating brains 🧠:",
    "log_console_label": "Undead messages from the Earth Engine 👇:",
    "run_button": "🧟 Begin Download 🧟",
    "cancel_button": "💀 Stop Undead 💀",
    "run_button_processing": "Eating brains... 🧟",
    "cancel_button_cancelling": "Stopping...",
    "status_bar_ready": "Ready for some undead downloads! 🧟",
    "status_bar_ee_init_fail": "Oh no! EE couldn't connect. No brains!",
    "status_bar_ee_init_ok": "Earth Engine is ready! Let's eat some data! 🧟",
    "status_bar_input_error_prefix": "Oh no, something's not undead: ",
    "status_bar_processing_started": "Our undead download has begun...",
    "status_bar_cancellation_requested": "Stopping our undead activities for now...",
    "status_bar_processing_finished": "Our undead adventure is complete! Check your treasures.",
}

# Theme text mapping
THEME_TEXTS = {
    "Fluttershy": FLUTTERSHY_TEXTS,
    "Night Mode": FLUTTERSHY_TEXTS,  # Use default for night mode
    "Rainbow Dash": RAINBOW_DASH_TEXTS,
    "Applejack": APPLEJACK_TEXTS,
    "Rarity": RARITY_TEXTS,
    "Pinkie Pie": PINKIE_PIE_TEXTS,
    "Twilight Sparkle": TWILIGHT_SPARKLE_TEXTS,
    "Celestia": CELESTIA_TEXTS,
    "Luna": LUNA_TEXTS,
    "Starlight Glimmer": STARLIGHT_TEXTS,
    "Trixie": TRIXIE_TEXTS,
    "Derpy": DERPY_TEXTS,
    "Cadence": CADENCE_TEXTS,
    "Steve": STEVE_TEXTS,
    "Creeper": CREEPER_TEXTS,
    "Enderman": ENDERMAN_TEXTS,
    "Zombie": ZOMBIE_TEXTS,
}

# Font settings
QT_FLUTTER_FONT_FAMILY = "Segoe UI"
QT_FLUTTER_FONT_SIZE_NORMAL = "11pt"

class ThemeManager:
    """Manages theme colors, styling, and metadata for the application."""

    # Default sub-options for all themes
    DEFAULT_SUBOPTIONS = {
        "catchphrases": False,
        "special_icons": False,
        "animated_background": False
    }

    def __init__(self, theme_name: str = DEFAULT_THEME, suboptions: Optional[dict] = None):
        self.theme_name = theme_name
        self.colors = self.get_theme_colors(theme_name)
        self.suboptions = suboptions if suboptions is not None else self.DEFAULT_SUBOPTIONS.copy()
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Get color palette for specified theme."""
        return THEMES.get(theme_name, FLUTTERSHY_COLORS)
    
    def set_theme(self, theme_name: str, suboptions: Optional[dict] = None):
        """Set the current theme."""
        self.theme_name = theme_name
        self.colors = self.get_theme_colors(theme_name)
        if suboptions is not None:
            self.suboptions = suboptions
        else:
            self.suboptions = self.DEFAULT_SUBOPTIONS.copy()
    
    def get_stylesheet(self) -> str:
        """Generate Qt stylesheet for current theme."""
        colors = self.colors
        
        # Support for background gradients/patterns
        bg_pattern = self.get_background_pattern(self.theme_name)
        bg_css = bg_pattern if bg_pattern else f"background-color: {colors['BG_MAIN']};"
        
        # Support for animations
        animation_css = self.get_animation_css(self.theme_name)
        
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
            {animation_css}
            QMainWindow, QWidget {{
                {bg_css}
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
    
    def get_background_pattern(self, theme_name: str) -> str:
        """Return a CSS background pattern or gradient for the theme, if any."""
        if theme_name == "Rainbow Dash":
            return "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #E3F2FD, stop:0.2 #BBDEFB, stop:0.4 #FFF176, stop:0.6 #FF9800, stop:0.8 #9C27B0, stop:1 #E3F2FD);"
        if theme_name == "Pinkie Pie":
            return "background: repeating-radial-gradient(circle at 20% 20%, #FFD1E8, #FFF0F6 20px);"
        if theme_name == "Creeper":
            return "background: repeating-linear-gradient(45deg, #4CAF50, #4CAF50 10px, #388E3C 10px, #388E3C 20px);"
        if theme_name == "Enderman":
            return "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #212121, stop:1 #512DA8);"
        if theme_name == "Celestia":
            return "background: qradialgradient(cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 #FFF8E1, stop:1 #FFFDE7);"
        if theme_name == "Luna":
            return "background: qradialgradient(cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 #232946, stop:1 #2E335B);"
        if theme_name == "Starlight Glimmer":
            return "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E1F5FE, stop:1 #EDE7F6);"
        if theme_name == "Trixie":
            return "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E3E6F3, stop:1 #B3B8D6);"
        if theme_name == "Derpy":
            return "background: repeating-linear-gradient(45deg, #F0F4C3, #F0F4C3 10px, #E6EE9C 10px, #E6EE9C 20px);"
        if theme_name == "Cadence":
            return "background: qradialgradient(cx:0.5, cy:0.5, radius:1, fx:0.5, fy:0.5, stop:0 #F8BBD0, stop:1 #FCE4EC);"
        if theme_name == "Steve":
            return "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A7C7E7, stop:1 #B7E1CD);"
        if theme_name == "Zombie":
            return "background: repeating-linear-gradient(45deg, #A5D6A7, #A5D6A7 10px, #C8E6C9 10px, #C8E6C9 20px);"
        # Add more as desired
        return ""

    def get_animation_css(self, theme_name: str) -> str:
        """Return CSS animations for the theme, if any."""
        if not self.suboptions.get("animated_background", False):
            return ""
            
        if theme_name == "Twilight Sparkle":
            return """
                @keyframes sparkle {
                    0%, 100% { opacity: 0; transform: scale(0); }
                    50% { opacity: 1; transform: scale(1); }
                }
                QMainWindow::before {
                    content: "✨";
                    position: absolute;
                    animation: sparkle 2s infinite;
                    font-size: 20px;
                    color: #7E57C2;
                }
            """
        if theme_name == "Pinkie Pie":
            return """
                @keyframes confetti {
                    0% { transform: translateY(-100px) rotate(0deg); opacity: 1; }
                    100% { transform: translateY(100vh) rotate(360deg); opacity: 0; }
                }
                QMainWindow::before {
                    content: "🎉";
                    position: absolute;
                    animation: confetti 3s infinite;
                    font-size: 16px;
                    color: #F06292;
                }
            """
        if theme_name == "Rainbow Dash":
            return """
                @keyframes rainbow {
                    0% { filter: hue-rotate(0deg); }
                    100% { filter: hue-rotate(360deg); }
                }
                QMainWindow {
                    animation: rainbow 4s infinite;
                }
            """
        if theme_name == "Creeper":
            return """
                @keyframes explode {
                    0%, 90% { transform: scale(1); }
                    95% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                QMainWindow {
                    animation: explode 5s infinite;
                }
            """
        if theme_name == "Enderman":
            return """
                @keyframes teleport {
                    0%, 90% { opacity: 1; }
                    95% { opacity: 0.3; }
                    100% { opacity: 1; }
                }
                QMainWindow {
                    animation: teleport 8s infinite;
                }
            """
        return ""

    def get_character_catchphrases(self, theme_name: str) -> dict:
        """Return character-specific catchphrases for UI elements."""
        catchphrases = {
            "Fluttershy": {
                "greeting": "Oh, hello there! 💖",
                "success": "That was lovely! ✨",
                "error": "Oh dear, something went wrong...",
                "working": "Working gently... 🐾",
                "complete": "All done! That was wonderful! 🌸"
            },
            "Rainbow Dash": {
                "greeting": "Hey there! Ready for some awesome downloads? ⚡",
                "success": "That was totally awesome! ⚡",
                "error": "Oh no! That's not awesome at all!",
                "working": "Working at lightning speed! ⚡",
                "complete": "Boom! All done! That was epic! ⚡"
            },
            "Applejack": {
                "greeting": "Howdy! Ready for some honest work? 🍎",
                "success": "That was some good honest work! 🍎",
                "error": "Well shucks, something went wrong...",
                "working": "Working hard... 🍎",
                "complete": "All done! That was some fine work! 🍎"
            },
            "Rarity": {
                "greeting": "Hello darling! Ready for something fabulous? 💎",
                "success": "That was absolutely fabulous! 💎",
                "error": "Oh my, how dreadful!",
                "working": "Creating something fabulous... 💎",
                "complete": "Perfect! That was simply divine! 💎"
            },
            "Pinkie Pie": {
                "greeting": "Hi there! Ready for a party? 🎉",
                "success": "That was super duper fun! 🎉",
                "error": "Oh no! No party!",
                "working": "Party time! 🎉",
                "complete": "Woo hoo! Party complete! 🎉"
            },
            "Twilight Sparkle": {
                "greeting": "Hello! Ready for some research? 📚",
                "success": "Excellent! The research is complete! 📚",
                "error": "Oh no! Research interrupted!",
                "working": "Conducting research... 📚",
                "complete": "Research complete! Fascinating results! 📚"
            },
            "Celestia": {
                "greeting": "Greetings! Ready for royal downloads? ☀️",
                "success": "Splendid! Royal work well done! ☀️",
                "error": "Oh my! The sun shall not rise!",
                "working": "Raising the sun... ☀️",
                "complete": "Magnificent! Royal duties complete! ☀️"
            },
            "Luna": {
                "greeting": "Good evening! Ready for lunar downloads? 🌙",
                "success": "Wonderful! The night is complete! 🌙",
                "error": "Oh no! The night shall be eternal!",
                "working": "Raising the moon... 🌙",
                "complete": "Perfect! The night is complete! 🌙"
            },
            "Starlight Glimmer": {
                "greeting": "Hello! Ready for some magic? ✨",
                "success": "Amazing! The magic worked! ✨",
                "error": "Oh no! The magic is broken!",
                "working": "Casting spells... ✨",
                "complete": "Incredible! Magic complete! ✨"
            },
            "Trixie": {
                "greeting": "Greetings! Ready for great & powerful downloads? 🎪",
                "success": "Spectacular! The Great & Powerful Trixie succeeds! 🎪",
                "error": "Oh no! The Great & Powerful Trixie is disappointed!",
                "working": "Performing great tricks... 🎪",
                "complete": "Magnificent! The show is complete! 🎪"
            },
            "Derpy": {
                "greeting": "Hi! Ready for some muffins? 🥧",
                "success": "Yay! Muffins are ready! 🥧",
                "error": "Oops! No muffins!",
                "working": "Baking muffins... 🥧",
                "complete": "Delicious! Muffins complete! 🥧"
            },
            "Cadence": {
                "greeting": "Hello! Ready to spread some love? 💕",
                "success": "Wonderful! Love is everywhere! 💕",
                "error": "Oh no! Love is lost!",
                "working": "Spreading love... 💕",
                "complete": "Beautiful! Love is complete! 💕"
            },
            "Steve": {
                "greeting": "Hello! Ready for some mining? ⛏️",
                "success": "Excellent! Found diamonds! ⛏️",
                "error": "Oh no! No diamonds!",
                "working": "Mining... ⛏️",
                "complete": "Perfect! Mining complete! ⛏️"
            },
            "Creeper": {
                "greeting": "Ssss... Ready for explosions? 💥",
                "success": "Boom! Explosions successful! 💥",
                "error": "Oh no! No explosions!",
                "working": "Creating explosions... 💥",
                "complete": "Boom! Explosions complete! 💥"
            },
            "Enderman": {
                "greeting": "... Ready for teleporting? 👁️",
                "success": "... Teleportation successful! 👁️",
                "error": "... No teleporting!",
                "working": "Teleporting... 👁️",
                "complete": "... Teleportation complete! 👁️"
            },
            "Zombie": {
                "greeting": "Brains... Ready for downloads? 🧟",
                "success": "Brains... Downloads successful! 🧟",
                "error": "Brains... No downloads!",
                "working": "Eating brains... 🧟",
                "complete": "Brains... Downloads complete! 🧟"
            }
        }
        return catchphrases.get(theme_name, catchphrases["Fluttershy"])

    def get_catchphrase(self, context: str) -> str:
        """Get a character-specific catchphrase for the given context."""
        if not self.suboptions.get("catchphrases", False):
            return ""
        catchphrases = self.get_character_catchphrases(self.theme_name)
        return catchphrases.get(context, "")

    def get_about_info(self) -> dict:
        """Get about section information for the current theme."""
        about_sections = {
            "Fluttershy": {
                "title": "About Flutter Earth 🦋",
                "subtitle": "Gently downloading GEE data with QtPy!",
                "description": """
                    <h3>💖 Welcome to Flutter Earth! 💖</h3>
                    <p>Flutter Earth is a gentle and user-friendly application for downloading and processing satellite imagery from Google Earth Engine.</p>
                    <h4>🌸 What Flutter Earth Offers:</h4>
                    <ul>
                        <li><b>Satellite Data Download:</b> Download imagery from multiple satellite sensors</li>
                        <li><b>Area of Interest Selection:</b> Define your study area using coordinates, shapefiles, or interactive map selection</li>
                        <li><b>Time Series Processing:</b> Download monthly composites over extended periods</li>
                        <li><b>Cloud Masking:</b> Automatic cloud detection and masking for clear imagery</li>
                        <li><b>Multiple Output Formats:</b> Save data as GeoTIFF, NetCDF, or other formats</li>
                        <li><b>Batch Processing:</b> Process multiple areas or time periods efficiently</li>
                        <li><b>Vector Data Download:</b> Download OpenStreetMap and other vector datasets</li>
                        <li><b>Post-Processing Tools:</b> Calculate vegetation indices and other derived products</li>
                    </ul>
                    <h4>🛰️ Supported Satellites:</h4>
                    <ul>
                        <li>Landsat 8 & 9 (30m resolution)</li>
                        <li>Sentinel-2 (10m resolution)</li>
                        <li>MODIS (250m-1km resolution)</li>
                        <li>VIIRS (375m-750m resolution)</li>
                        <li>And many more!</li>
                    </ul>
                    <p><i>Version 6.19 - Made with kindness and care! 🌸</i></p>
                """
            },
            "Rainbow Dash": {
                "title": "About Flutter Earth ⚡",
                "subtitle": "Awesome GEE data downloading at lightning speed!",
                "description": """
                    <h3>⚡ Welcome to Flutter Earth! ⚡</h3>
                    <p>Flutter Earth is the most awesome application for downloading and processing satellite imagery from Google Earth Engine!</p>
                    <h4>⚡ What Makes Flutter Earth Awesome:</h4>
                    <ul>
                        <li><b>Lightning-Fast Downloads:</b> Download imagery from multiple satellite sensors at incredible speeds</li>
                        <li><b>Awesome Area Selection:</b> Define your study area with precision using coordinates, shapefiles, or interactive maps</li>
                        <li><b>Epic Time Series:</b> Download monthly composites over extended periods for amazing analysis</li>
                        <li><b>Cloud-Busting:</b> Automatic cloud detection and masking for crystal-clear imagery</li>
                        <li><b>Multiple Formats:</b> Save data as GeoTIFF, NetCDF, or other awesome formats</li>
                        <li><b>Batch Processing:</b> Process multiple areas or time periods with lightning efficiency</li>
                        <li><b>Vector Downloads:</b> Download OpenStreetMap and other vector datasets</li>
                        <li><b>Post-Processing:</b> Calculate vegetation indices and other derived products</li>
                    </ul>
                    <p><i>Version 6.19 - Made for speed and awesomeness! ⚡</i></p>
                """
            }
        }
        
        # Get theme-specific about info or fallback to Fluttershy
        about_info = about_sections.get(self.theme_name, about_sections["Fluttershy"])
        return about_info

    def get_splash_chime(self) -> str:
        """Get the splash screen chime description for the current theme."""
        chimes = {
            "Fluttershy": "Gentle butterfly flutter sound",
            "Rainbow Dash": "Lightning bolt zap sound", 
            "Applejack": "Apple crunch sound",
            "Rarity": "Gem sparkle sound",
            "Pinkie Pie": "Party horn sound",
            "Twilight Sparkle": "Magic sparkle sound",
            "Celestia": "Royal fanfare sound",
            "Luna": "Night owl hoot sound",
            "Starlight Glimmer": "Magic spell sound",
            "Trixie": "Circus bell sound",
            "Derpy": "Muffin munch sound",
            "Cadence": "Love heart beat sound",
            "Steve": "Diamond pickaxe sound",
            "Creeper": "Explosion sound",
            "Enderman": "Teleport sound",
            "Zombie": "Brain eating sound"
        }
        return chimes.get(self.theme_name, "Gentle startup sound")
    
    def get_theme_metadata(self, theme_name: str) -> dict:
        return THEMES_METADATA.get(theme_name, {"category": "Main", "display": theme_name})
    
    def get_available_themes(self, category: str = None) -> list:
        if category:
            return [k for k, v in THEMES_METADATA.items() if v["category"] == category]
        return list(THEMES.keys())
    
    def get_categories(self) -> list:
        cats = set(v["category"] for v in THEMES_METADATA.values())
        return sorted(cats)
    
    def get_suboptions(self, theme_name: str) -> dict:
        # Could be extended per-theme
        return self.DEFAULT_SUBOPTIONS.copy()
    
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """Get themed text for the given key."""
        # Try theme-specific text first, then fallback to Fluttershy
        theme_texts = THEME_TEXTS.get(self.theme_name, FLUTTERSHY_TEXTS)
        val = theme_texts.get(key, "")
        if val:
            return val
        # Fallback to Fluttershy texts
        val = FLUTTERSHY_TEXTS.get(key, "")
        if val:
            return val
        if default is not None:
            return default
        return str(key)
    
    def is_animated_background(self) -> bool:
        return self.suboptions.get("animated_background", False)
    
    def get_special_icons(self) -> bool:
        return self.suboptions.get("special_icons", False) 