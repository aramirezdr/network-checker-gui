"""
Configuration management for the Network Checker application.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration with defaults and validation."""
    
    DEFAULT_CONFIG = {
        "network": {
            "ping_count": 1,
            "timeout": 5,
            "dns_servers": ["google.com", "8.8.8.8"]
        },
        "logging": {
            "level": "INFO",
            "file": "network_checker.log",
            "max_bytes": 1048576,
            "backup_count": 3
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file or create with defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self.config = self._merge_with_defaults(self.config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded config with defaults to ensure all keys exist.
        
        Args:
            config: Loaded configuration
            
        Returns:
            Merged configuration
        """
        merged = self.DEFAULT_CONFIG.copy()
        for section, values in config.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Configuration section name
            
        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {})
    
    @property
    def ping_count(self) -> int:
        """Get ping count setting."""
        return self.get("network", "ping_count", 1)
    
    @property
    def timeout(self) -> int:
        """Get timeout setting."""
        return self.get("network", "timeout", 5)
    
    @property
    def dns_servers(self) -> list:
        """Get DNS servers list."""
        return self.get("network", "dns_servers", ["google.com"])
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get("logging", "level", "INFO")
    
    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.get("logging", "file", "network_checker.log")
    
    @property
    def log_max_bytes(self) -> int:
        """Get log file max bytes."""
        return self.get("logging", "max_bytes", 1048576)
    
    @property
    def log_backup_count(self) -> int:
        """Get log backup count."""
        return self.get("logging", "backup_count", 3)
