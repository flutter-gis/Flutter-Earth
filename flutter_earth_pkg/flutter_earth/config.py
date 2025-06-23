"""Configuration management for Flutter Earth."""
import os
import json
import logging
from typing import Any, Dict, Optional, List, Union, Literal
from pathlib import Path
import copy
from dataclasses import fields

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

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = 'flutter_earth_config.json', environment: Environment = 'production'):
        """Initialize configuration manager."""
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
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config: Dict[str, Any] = json.load(f)
                
                for key, value in loaded_config.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)

                self._validate_config(self.config)
                logging.info(f"Configuration loaded from {self.config_file}")
            else:
                self._validate_config(self.config)
                self.save_config()
                logging.info(f"Created new configuration file at {self.config_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            output_dir = os.path.dirname(self.config_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            self._validate_config(self.config)
            
            with open(self.config_file, 'w') as f:
                config_dict = {
                    f.name: getattr(self.config, f.name)
                    for f in fields(self.config)
                }
                json.dump(config_dict, f, indent=4)
            logging.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        temp_config = copy.deepcopy(self.config)
        if hasattr(temp_config, key):
            setattr(temp_config, key, value)
        
        self._validate_config(temp_config)
        
        setattr(self.config, key, value)
        self.save_config()

    def get_current_theme_colors(self) -> Dict[str, str]:
        """Get the color palette for the current theme."""
        theme_name = self.get('theme', 'Default (Dark)')
        return THEMES.get(theme_name, THEMES['Default (Dark)'])

    def get_available_themes(self) -> List[str]:
        """Returns a list of available theme names."""
        return list(THEMES.keys())
        
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        temp_config = copy.deepcopy(self.config)
        for key, value in updates.items():
            if hasattr(temp_config, key):
                setattr(temp_config, key, value)
        
        self._validate_config(temp_config)
        
        for key, value in updates.items():
            setattr(self.config, key, value)
        self.save_config()
    
    def add_recent_directory(self, directory: str) -> None:
        """Add directory to recent directories list."""
        if not os.path.isdir(directory):
            logging.warning(f"Recent directory does not exist: {directory}")
            return
            
        recent_dirs = self.get('recent_directories', [])
        if directory in recent_dirs:
            recent_dirs.remove(directory)
        recent_dirs.insert(0, directory)
        self.set('recent_directories', recent_dirs[:10])
    
    def get_satellite_details(self, sensor_name: str) -> Optional[SatelliteDetails]:
        """Get details for a specific satellite sensor."""
        return SATELLITE_DETAILS.get(sensor_name)

    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
    
    def set_environment(self, environment: Environment) -> None:
        """Set current environment and reload configuration."""
        if environment not in ENV_CONFIGS:
            raise ConfigurationError(f"Invalid environment: {environment}")
        self.environment = environment
        self.config = self._get_env_config()
        self.load_config()

# Global configuration instance
config_manager = ConfigManager(environment=os.getenv('FLUTTER_EARTH_ENV', 'production')) 