"""Configuration management for Flutter Earth."""
import os
import json
import logging
from typing import Any, Dict, Optional, List, Union, TypedDict, Literal
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .types import AppConfig, Environment, SatelliteDetails
from .errors import ConfigurationError

# Environment types
Environment = Literal['development', 'production', 'test']

@dataclass
class ValidationRule:
    """Rule for validating configuration values."""
    type: type
    required: bool = True
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    
    def validate(self, value: Any) -> bool:
        """Validate a value against this rule."""
        if value is None:
            return not self.required
            
        if isinstance(self.type, tuple):
            if not any(isinstance(value, t) for t in self.type):
                return False
        elif not isinstance(value, self.type):
            return False
            
        if self.min_value is not None and value < self.min_value:
            return False
            
        if self.max_value is not None and value > self.max_value:
            return False
            
        if self.allowed_values is not None and value not in self.allowed_values:
            return False
            
        return True

# Configuration validation rules
CONFIG_RULES: Dict[str, ValidationRule] = {
    'output_dir': ValidationRule(type=str, required=True),
    'tile_size': ValidationRule(type=float, required=True, min_value=0.1, max_value=5.0),
    'max_workers': ValidationRule(type=int, required=True, min_value=1, max_value=16),
    'cloud_mask': ValidationRule(type=bool, required=True),
    'max_cloud_cover': ValidationRule(type=(int, float), required=True, min_value=0, max_value=100),
    'recent_directories': ValidationRule(type=list, required=True),
    'theme': ValidationRule(type=str, required=False, allowed_values=['Fluttershy', 'Night Mode', 'Rainbow Dash', 'Applejack', 'Rarity', 'Pinkie Pie', 'Twilight Sparkle', 'Celestia', 'Luna', 'Starlight Glimmer', 'Trixie', 'Derpy', 'Cadence', 'Steve', 'Creeper', 'Enderman', 'Zombie']),
    'theme_suboptions': ValidationRule(type=dict, required=False),
    'sensor_priority_order': ValidationRule(type=list, required=False),
    'use_best_resolution': ValidationRule(type=bool, required=False),
    'cleanup_tiles': ValidationRule(type=bool, required=False),
    'tiling_method': ValidationRule(type=str, required=False, allowed_values=['degree', 'pixel']),
    'num_subsections': ValidationRule(type=int, required=False, min_value=1, max_value=1000),
    'target_resolution': ValidationRule(type=int, required=False, min_value=1, max_value=1000),
    'start_date': ValidationRule(type=str, required=False),
    'end_date': ValidationRule(type=str, required=False),
    'overwrite': ValidationRule(type=bool, required=False),
    'bbox_str': ValidationRule(type=str, required=False)
}

# Default configuration
DEFAULT_CONFIG: AppConfig = {
    'output_dir': os.path.expanduser('~/Downloads/flutter_earth'),
    'tile_size': 1.0,  # degrees
    'max_workers': 4,
    'cloud_mask': True,
    'max_cloud_cover': 20.0,  # percent
    'recent_directories': [],
    'theme': 'Fluttershy',
    'theme_suboptions': {
        'catchphrases': False,
        'special_icons': False,
        'animated_background': False
    },
    'sensor_priority_order': ['LANDSAT_9', 'SENTINEL2', 'LANDSAT_8', 'LANDSAT_7', 'LANDSAT_5', 'LANDSAT_4', 'ERA5_TEMP', 'VIIRS', 'MODIS'],
    'use_best_resolution': False,
    'cleanup_tiles': True,
    'tiling_method': 'degree',
    'num_subsections': 100,
    'target_resolution': 30,
    'start_date': (datetime.now() - relativedelta(months=6)).strftime('%Y-%m-%d'),
    'end_date': datetime.now().strftime('%Y-%m-%d'),
    'overwrite': False,
    'bbox_str': '35.2,30.5,35.8,32.0'  # Example BBOX (Israel region)
}

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
        """Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file.
            environment: Environment to use for configuration.
        """
        self.config_file = config_file
        self.environment = environment
        self.config: AppConfig = self._get_env_config()
        self.load_config()
    
    def _get_env_config(self) -> AppConfig:
        """Get environment-specific configuration.
        
        Returns:
            Configuration with environment-specific overrides.
        """
        config = DEFAULT_CONFIG.copy()
        config.update(ENV_CONFIGS.get(self.environment, {}))
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration values.
        
        Args:
            config: Configuration to validate.
            
        Raises:
            ConfigurationError: If validation fails.
        """
        for key, rule in CONFIG_RULES.items():
            if key not in config and rule.required:
                raise ConfigurationError(f"Missing required configuration key: {key}")
            
            value = config.get(key)
            if not rule.validate(value):
                raise ConfigurationError(
                    f"Invalid configuration value for {key}: {value}. "
                    f"Expected type {rule.type.__name__}"
                    + (f", min value {rule.min_value}" if rule.min_value is not None else "")
                    + (f", max value {rule.max_value}" if rule.max_value is not None else "")
                    + (f", allowed values {rule.allowed_values}" if rule.allowed_values is not None else "")
                )
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Update default config with loaded values
                self.config.update(loaded_config)
                # Validate configuration
                self._validate_config(self.config)
                logging.info(f"Configuration loaded from {self.config_file}")
            else:
                self._validate_config(self.config)  # Validate default config
                self.save_config()
                logging.info(f"Created new configuration file at {self.config_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(self.config_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                
            # Validate before saving
            self._validate_config(self.config)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            logging.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
        
        Returns:
            Configuration value.
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key.
            value: Configuration value.
            
        Raises:
            ConfigurationError: If validation fails.
        """
        # Create temporary config for validation
        temp_config = self.config.copy()
        temp_config[key] = value
        
        # Validate the change
        self._validate_config(temp_config)
        
        # If validation passes, update and save
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values.
        
        Args:
            updates: Dictionary of configuration updates.
            
        Raises:
            ConfigurationError: If validation fails.
        """
        # Create temporary config for validation
        temp_config = self.config.copy()
        temp_config.update(updates)
        
        # Validate all changes
        self._validate_config(temp_config)
        
        # If validation passes, update and save
        self.config.update(updates)
        self.save_config()
    
    def add_recent_directory(self, directory: str) -> None:
        """Add directory to recent directories list.
        
        Args:
            directory: Directory path to add.
        """
        # Validate directory exists
        if not os.path.exists(directory):
            raise ConfigurationError(f"Directory does not exist: {directory}")
            
        recent = self.config['recent_directories']
        if directory in recent:
            recent.remove(directory)
        recent.insert(0, directory)
        # Keep only last 10 directories
        self.config['recent_directories'] = recent[:10]
        self.save_config()
    
    def get_satellite_details(self, sensor_name: str) -> Optional[SatelliteDetails]:
        """Get details for a satellite sensor.
        
        Args:
            sensor_name: Name of the sensor.
        
        Returns:
            Satellite details or None if not found.
        """
        return SATELLITE_DETAILS.get(sensor_name)
    
    def get_environment(self) -> Environment:
        """Get current environment.
        
        Returns:
            Current environment.
        """
        return self.environment
    
    def set_environment(self, environment: Environment) -> None:
        """Set environment and reload configuration.
        
        Args:
            environment: Environment to set.
        """
        if environment not in ENV_CONFIGS:
            raise ConfigurationError(f"Invalid environment: {environment}")
            
        self.environment = environment
        self.config = self._get_env_config()
        self.load_config()

# Global configuration instance
config_manager = ConfigManager(environment=os.getenv('FLUTTER_EARTH_ENV', 'production')) 