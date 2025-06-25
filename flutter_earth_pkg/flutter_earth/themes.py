from PySide6.QtCore import QObject, Signal
from .config import THEMES, config_manager

import logging

class ThemeManager(QObject):
    theme_changed = Signal(str, dict)  # theme name, full theme data dict

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # Ensure config is loaded before using theme
        config_manager.load_config()
        self._themes_data_source = THEMES
        self._current_theme_name = config_manager.get('theme', 'Default (Dark)')
        self.logger.info(f"ThemeManager initialized with theme: {self._current_theme_name}")
        self.logger.debug(f"Initial theme data: {self.get_current_theme_data()}")

    def get_current_theme_data(self) -> dict:
        theme_data = self._themes_data_source.get(self._current_theme_name,
                                     self._themes_data_source['Default (Dark)'])
        self.logger.debug(f"get_current_theme_data: {theme_data}")
        return theme_data

    def get_theme_data(self, theme_name: str) -> dict:
        theme_data = self._themes_data_source.get(theme_name,
                                     self._themes_data_source['Default (Dark)'])
        self.logger.debug(f"get_theme_data({theme_name}): {theme_data}")
        return theme_data

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
        self.logger.debug(f"Available themes: {available}")
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
        self.logger.debug(f"Theme data after change: {new_theme_data}")

    def set_suboptions(self, suboptions: dict):
        theme_data = self.get_current_theme_data()
        if 'options' in theme_data:
            theme_data['options'].update(suboptions)
            self.logger.info(f"Theme suboptions updated: {suboptions}")
            self.theme_changed.emit(self.current_theme_name(), theme_data)
        else:
            self.logger.warning("No 'options' key in current theme data to update suboptions.")

    def current_theme_name(self) -> str:
        return self._current_theme_name

# Usage in GUI:
# theme_manager = ThemeManager()
# theme_manager.theme_changed.connect(your_theme_update_function)
# theme_manager.apply_theme('Sanofi') 