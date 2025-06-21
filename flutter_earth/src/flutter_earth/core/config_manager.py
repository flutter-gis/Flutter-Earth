"""Configuration management for Flutter Earth."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import asdict, dataclass, field

from .types import AppConfig, OutputFormat


@dataclass
class ConfigManager:
    """Manages application configuration."""
    
    config_file: Path = field(default_factory=lambda: Path.home() / ".flutter_earth" / "config.json")
    _config: Optional[AppConfig] = None
    _logger: Optional[logging.Logger] = None
    
    def __post_init__(self):
        """Initialize the configuration manager."""
        self._logger = logging.getLogger(__name__)
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._config = self._deserialize_config(config_data)
                self._logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self._config = AppConfig()
                self._save_config()
                self._logger.info("Created default configuration")
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            self._config = AppConfig()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize and save
            config_data = self._serialize_config(self._config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._logger.debug(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
    
    def _serialize_config(self, config: AppConfig) -> Dict[str, Any]:
        """Serialize AppConfig to dictionary."""
        config_dict = asdict(config)
        
        # Convert Path objects to strings
        if config_dict.get('service_account_path'):
            config_dict['service_account_path'] = str(config_dict['service_account_path'])
        if config_dict.get('default_output_directory'):
            config_dict['default_output_directory'] = str(config_dict['default_output_directory'])
        if config_dict.get('cache_directory'):
            config_dict['cache_directory'] = str(config_dict['cache_directory'])
        
        # Convert OutputFormat enum to string
        config_dict['default_output_format'] = config_dict['default_output_format'].value
        
        return config_dict
    
    def _deserialize_config(self, config_data: Dict[str, Any]) -> AppConfig:
        """Deserialize dictionary to AppConfig."""
        # Convert string paths back to Path objects
        if config_data.get('service_account_path'):
            config_data['service_account_path'] = Path(config_data['service_account_path'])
        if config_data.get('default_output_directory'):
            config_data['default_output_directory'] = Path(config_data['default_output_directory'])
        if config_data.get('cache_directory'):
            config_data['cache_directory'] = Path(config_data['cache_directory'])
        
        # Convert string back to OutputFormat enum
        if config_data.get('default_output_format'):
            config_data['default_output_format'] = OutputFormat(config_data['default_output_format'])
        
        return AppConfig(**config_data)
    
    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return getattr(self._config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if hasattr(self._config, key):
            setattr(self._config, key, value)
            self._save_config()
            self._logger.debug(f"Configuration updated: {key} = {value}")
        else:
            raise ValueError(f"Unknown configuration key: {key}")
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = AppConfig()
        self._save_config()
        self._logger.info("Configuration reset to defaults")
    
    def export_config(self, file_path: Path) -> None:
        """Export configuration to a file."""
        try:
            config_data = self._serialize_config(self._config)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            self._logger.info(f"Configuration exported to {file_path}")
        except Exception as e:
            self._logger.error(f"Failed to export configuration: {e}")
            raise
    
    def import_config(self, file_path: Path) -> None:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            self._config = self._deserialize_config(config_data)
            self._save_config()
            self._logger.info(f"Configuration imported from {file_path}")
        except Exception as e:
            self._logger.error(f"Failed to import configuration: {e}")
            raise
    
    def validate_config(self) -> bool:
        """Validate the current configuration."""
        try:
            # Basic validation
            if self._config.max_concurrent_downloads <= 0:
                self._logger.error("max_concurrent_downloads must be positive")
                return False
            
            if self._config.default_resolution <= 0:
                self._logger.error("default_resolution must be positive")
                return False
            
            if not 0 <= self._config.default_cloud_cover <= 100:
                self._logger.error("default_cloud_cover must be between 0 and 100")
                return False
            
            # Validate paths if they exist
            if self._config.service_account_path and not self._config.service_account_path.exists():
                self._logger.warning(f"Service account file not found: {self._config.service_account_path}")
            
            if self._config.default_output_directory and not self._config.default_output_directory.exists():
                self._logger.warning(f"Default output directory does not exist: {self._config.default_output_directory}")
            
            self._logger.debug("Configuration validation passed")
            return True
            
        except Exception as e:
            self._logger.error(f"Configuration validation failed: {e}")
            return False 