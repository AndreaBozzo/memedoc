import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import hashlib
import threading

@dataclass
class PlatformConfig:
    """Platform configuration structure"""
    platform_name: str
    enabled: bool
    rate_limit: int
    daily_limit: int
    retry_attempts: int = 3
    retry_delay: float = 1.0
    timeout: int = 30
    custom_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_params is None:
            self.custom_params = {}

class ConfigManager:
    """Thread-safe configuration manager with caching and validation"""

    def __init__(self, config_dir: str = "config/platforms"):
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, PlatformConfig] = {}
        self._cache_hashes: Dict[str, str] = {}
        self._lock = threading.RLock()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def get_platform_config(self, platform_name: str) -> PlatformConfig:
        """Get platform configuration with caching"""
        with self._lock:
            config_path = self.config_dir / f"{platform_name}.json"

            # Check if file exists
            if not config_path.exists():
                return self._create_default_config(platform_name)

            # Calculate file hash for cache invalidation
            current_hash = self._get_file_hash(config_path)

            # Return cached config if valid
            if (platform_name in self._cache and
                platform_name in self._cache_hashes and
                self._cache_hashes[platform_name] == current_hash):
                return self._cache[platform_name]

            # Load and validate config
            try:
                config = self._load_and_validate_config(config_path)
                self._cache[platform_name] = config
                self._cache_hashes[platform_name] = current_hash
                return config
            except Exception as e:
                # Return default config on error
                default_config = self._create_default_config(platform_name)
                self._cache[platform_name] = default_config
                return default_config

    def _load_and_validate_config(self, config_path: Path) -> PlatformConfig:
        """Load and validate configuration file"""
        with open(config_path, 'r') as f:
            raw_config = json.load(f)

        # Validate required fields
        required_fields = ['platform_name', 'enabled', 'rate_limit', 'daily_limit']
        for field in required_fields:
            if field not in raw_config:
                raise ValueError(f"Missing required field: {field}")

        # Validate types and ranges
        if not isinstance(raw_config['enabled'], bool):
            raise ValueError("'enabled' must be boolean")

        if not isinstance(raw_config['rate_limit'], int) or raw_config['rate_limit'] <= 0:
            raise ValueError("'rate_limit' must be positive integer")

        if not isinstance(raw_config['daily_limit'], int) or raw_config['daily_limit'] <= 0:
            raise ValueError("'daily_limit' must be positive integer")

        return PlatformConfig(
            platform_name=raw_config['platform_name'],
            enabled=raw_config['enabled'],
            rate_limit=raw_config['rate_limit'],
            daily_limit=raw_config['daily_limit'],
            retry_attempts=raw_config.get('retry_attempts', 3),
            retry_delay=raw_config.get('retry_delay', 1.0),
            timeout=raw_config.get('timeout', 30),
            custom_params=raw_config.get('custom_params', {})
        )

    def _create_default_config(self, platform_name: str) -> PlatformConfig:
        """Create default configuration for platform"""
        default_config = PlatformConfig(
            platform_name=platform_name,
            enabled=True,
            rate_limit=60,
            daily_limit=1000,
            retry_attempts=3,
            retry_delay=1.0,
            timeout=30
        )

        # Save default config to file
        config_path = self.config_dir / f"{platform_name}.json"
        self._save_config(default_config, config_path)

        return default_config

    def _save_config(self, config: PlatformConfig, config_path: Path):
        """Save configuration to file"""
        config_dict = {
            'platform_name': config.platform_name,
            'enabled': config.enabled,
            'rate_limit': config.rate_limit,
            'daily_limit': config.daily_limit,
            'retry_attempts': config.retry_attempts,
            'retry_delay': config.retry_delay,
            'timeout': config.timeout,
            'custom_params': config.custom_params
        }

        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for cache invalidation"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def reload_config(self, platform_name: str) -> PlatformConfig:
        """Force reload configuration from file"""
        with self._lock:
            # Clear cache for this platform
            self._cache.pop(platform_name, None)
            self._cache_hashes.pop(platform_name, None)
            return self.get_platform_config(platform_name)

    def get_all_enabled_platforms(self) -> list[str]:
        """Get list of all enabled platforms"""
        enabled_platforms = []

        for config_file in self.config_dir.glob("*.json"):
            platform_name = config_file.stem
            config = self.get_platform_config(platform_name)
            if config.enabled:
                enabled_platforms.append(platform_name)

        return enabled_platforms

# Global config manager instance
config_manager = ConfigManager()