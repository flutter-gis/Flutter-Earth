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
    'theme': ValidationRule(type=str, required=True)
}

# Theme definitions
THEMES = {
    'Default (Dark)': {
        'background': '#2E2E2E',
        'foreground': '#FFFFFF',
        'primary': '#5A9BD5',
        'secondary': '#7AC043',
        'accent': '#F4B183',
        'error': '#FF5555',
        'success': '#66FF66',
        'text': '#F0F0F0',
        'text_subtle': '#B0B0B0',
        'disabled': '#555555',
        'widget_bg': '#3C3C3C',
        'widget_border': '#505050',
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
        'tooltip_bg': '#FFFFE0',
        'tooltip_fg': '#000000',
        'progressbar_bg': '#555555',
        'progressbar_fg': '#5A9BD5',
    },
    'Light': {
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
    'Sanofi': {
        'background': '#FFFFFF',
        'foreground': '#000000',
        'primary': '#0064B4', # Sanofi Blue
        'secondary': '#9B9B9B', # Sanofi Gray
        'accent': '#E10098', # Sanofi Pink
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
        """Get the current theme color dictionary."""
        return THEMES.get(self.config.theme, THEMES['Default (Dark)'])

    def get_available_themes(self) -> List[str]:
        """Get a list of available theme names."""
        return list(THEMES.keys())

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

# Singleton instance for global access
config_manager = ConfigManager() 