"""
Configuration utility for the MultiRAG application.

This module provides functionality to load and access
configuration settings from YAML files.
"""

from pathlib import Path
from typing import Any, Dict, Union

import yaml

from src.utils.logger import app_logger

# Set up logger
logger = app_logger.getChild("src.utils.config")

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    pass

class Config:
    """
    Configuration handler for the application.
    
    This class loads and provides access to configuration settings
    from YAML files.
    
    Attributes
    ----------
    config_path : str
        Path to the configuration file.
    config : Dict
        Dictionary containing the configuration.
    """
    
    def __init__(self, config_path: Union[str, Path] = "config/config.yaml"):
        """
        Initialize the Config class.
        
        Parameters
        ----------
        config_path : str or Path, optional
            Path to the configuration file.
            Default is "config/config.yaml".
        
        Raises
        ------
        ConfigurationError
            If the configuration file cannot be loaded.
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """
        Load the configuration from the YAML file.
        
        Returns
        -------
        Dict
            Dictionary containing the configuration.
            
        Raises
        ------
        ConfigurationError
            If the configuration file cannot be loaded or parsed.
        """
        try:
            # Ensure config directory exists
            config_dir = self.config_path.parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Load configuration if file exists, otherwise return empty dict
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as file:
                    return yaml.safe_load(file)
            else:
                logger.warning(f"Configuration file {self.config_path} not found. Using default config.")
                return {}
                
        except yaml.YAMLError as e:
            error_msg = f"Error parsing YAML configuration: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        except Exception as e:
            error_msg = f"Error loading configuration: {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Parameters
        ----------
        path : str
            Dot-separated path to the configuration value.
            Example: "app.port"
        default : Any, optional
            Default value to return if the path is not found.
            
        Returns
        -------
        Any
            The configuration value at the specified path,
            or the default value if not found.
        """
        keys = path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def reload(self) -> None:
        """
        Reload the configuration from the file.
        
        Raises
        ------
        ConfigurationError
            If the configuration file cannot be loaded.
        """
        self.config = self._load_config()
        logger.info("Configuration reloaded")

# Create a singleton instance
config = Config()

# Function to get configuration values
def get_config(path: str, default: Any = None) -> Any:
    """
    Get a configuration value by path.
    
    Parameters
    ----------
    path : str
        Dot-separated path to the configuration value.
        Example: "app.port"
    default : Any, optional
        Default value to return if the path is not found.
        
    Returns
    -------
    Any
        The configuration value at the specified path,
        or the default value if not found.
    """
    return config.get(path, default) 