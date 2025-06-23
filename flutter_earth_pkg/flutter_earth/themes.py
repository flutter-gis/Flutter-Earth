from PySide6.QtCore import QObject, Signal
from .config import THEMES, config_manager

class ThemeManager(QObject):
    theme_changed = Signal(str, dict)  # theme name, theme colors dict

    def __init__(self):
        super().__init__()
        self._themes = THEMES
        self._current_theme = config_manager.get('theme', 'Default (Dark)')

    def get_theme(self, name: str = None) -> dict:
        """Get the color dictionary for a theme by name (or current)."""
        if name is None:
            name = self._current_theme
        return self._themes.get(name, self._themes['Default (Dark)'])

    def get_available_themes(self) -> list:
        """Return a list of available theme names."""
        return list(self._themes.keys())

    def apply_theme(self, name: str):
        """Set and apply a new theme, persist to config, and emit signal."""
        if name not in self._themes:
            name = 'Default (Dark)'
        self._current_theme = name
        config_manager.set('theme', name)
        self.theme_changed.emit(name, self.get_theme(name))

    def current_theme_name(self) -> str:
        return self._current_theme

# Usage in GUI:
# theme_manager = ThemeManager()
# theme_manager.theme_changed.connect(your_theme_update_function)
# theme_manager.apply_theme('Sanofi') 