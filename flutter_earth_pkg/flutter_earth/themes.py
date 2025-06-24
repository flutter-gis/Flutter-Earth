from PySide6.QtCore import QObject, Signal
from .config import THEMES, config_manager

import logging

class ThemeManager(QObject):
    theme_changed = Signal(str, dict)  # theme name, full theme data dict

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # THEMES is already the expanded structure from config.py
        self._themes_data_source = THEMES
        self._current_theme_name = config_manager.get('theme', 'Default (Dark)')

    def get_current_theme_data(self) -> dict:
        """Get the full data dictionary for the current theme."""
        return self._themes_data_source.get(self._current_theme_name,
                                     self._themes_data_source['Default (Dark)'])

    def get_theme_data(self, theme_name: str) -> dict:
        """Get the full data dictionary for a specific theme."""
        return self._themes_data_source.get(theme_name,
                                     self._themes_data_source['Default (Dark)'])

    def get_available_themes_meta(self) -> list:
        """Return a list of theme metadata dicts for UI (name, display_name, category)."""
        available = []
        for name, data in self._themes_data_source.items():
            meta = data.get('metadata', {})
            available.append({
                'name': name,
                'display_name': meta.get('display_name', name),
                'category': meta.get('category', 'Uncategorized')
            })
        return available

    def set_current_theme(self, theme_name: str):
        """Set and apply a new theme, persist to config, and emit signal."""
        if theme_name not in self._themes_data_source:
            self.logger.warning(f"Theme '{theme_name}' not found. Reverting to Default (Dark).")
            theme_name = 'Default (Dark)'

        self._current_theme_name = theme_name
        config_manager.set('theme', theme_name) # Persist only the name

        # Emit the full theme data for the newly set theme
        new_theme_data = self.get_theme_data(theme_name)
        self.theme_changed.emit(theme_name, new_theme_data)
        self.logger.info(f"Theme changed to: {theme_name}")

    def current_theme_name(self) -> str:
        return self._current_theme_name

# Usage in GUI:
# theme_manager = ThemeManager()
# theme_manager.theme_changed.connect(your_theme_update_function)
# theme_manager.apply_theme('Sanofi') 