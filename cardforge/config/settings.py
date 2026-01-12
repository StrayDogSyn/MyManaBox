"""
CardForge Configuration Management
Loads settings from environment variables and .env file
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from functools import lru_cache

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    _dotenv_available = True
except ImportError:
    _dotenv_available = False


def _load_env():
    """Load environment variables from .env file."""
    if _dotenv_available:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Try project root
            root_env = Path(__file__).parent.parent.parent / '.env'
            if root_env.exists():
                load_dotenv(root_env)


_load_env()


def get_env(key: str, default: str = '') -> str:
    """Get environment variable with default."""
    return os.getenv(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable."""
    val = os.getenv(key, str(default)).lower()
    return val in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_float(key: str, default: float = 0.0) -> float:
    """Get float environment variable."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        return default


@dataclass
class DatabaseConfig:
    """Database configuration."""
    path: str = field(default_factory=lambda: get_env('DATABASE_PATH', 'data/cardforge.db'))
    
    @property
    def url(self) -> str:
        """Get SQLite URL."""
        return f"sqlite:///{self.path}"


@dataclass
class ScryfallConfig:
    """Scryfall API configuration."""
    base_url: str = "https://api.scryfall.com"
    rate_limit: int = field(default_factory=lambda: get_env_int('SCRYFALL_RATE_LIMIT', 10))
    cache_ttl: int = field(default_factory=lambda: get_env_int('SCRYFALL_CACHE_TTL', 86400))
    price_cache_ttl: int = field(default_factory=lambda: get_env_int('SCRYFALL_PRICE_CACHE_TTL', 3600))


@dataclass
class TCGPlayerConfig:
    """TCGPlayer API configuration."""
    api_key: str = field(default_factory=lambda: get_env('TCGPLAYER_API_KEY'))
    api_secret: str = field(default_factory=lambda: get_env('TCGPLAYER_API_SECRET'))
    access_token: str = field(default_factory=lambda: get_env('TCGPLAYER_ACCESS_TOKEN'))
    
    @property
    def is_configured(self) -> bool:
        """Check if TCGPlayer is configured."""
        return bool(self.api_key and self.api_secret)


@dataclass
class CardMarketConfig:
    """CardMarket API configuration."""
    app_token: str = field(default_factory=lambda: get_env('CARDMARKET_APP_TOKEN'))
    app_secret: str = field(default_factory=lambda: get_env('CARDMARKET_APP_SECRET'))
    access_token: str = field(default_factory=lambda: get_env('CARDMARKET_ACCESS_TOKEN'))
    access_secret: str = field(default_factory=lambda: get_env('CARDMARKET_ACCESS_SECRET'))
    
    @property
    def is_configured(self) -> bool:
        """Check if CardMarket is configured."""
        return bool(self.app_token and self.app_secret)


@dataclass
class MoxfieldConfig:
    """Moxfield integration configuration."""
    api_key: str = field(default_factory=lambda: get_env('MOXFIELD_API_KEY'))
    username: str = field(default_factory=lambda: get_env('MOXFIELD_USERNAME'))
    
    @property
    def is_configured(self) -> bool:
        """Check if Moxfield is configured."""
        return bool(self.api_key)


@dataclass
class GoogleDriveConfig:
    """Google Drive backup configuration."""
    credentials_path: str = field(default_factory=lambda: get_env('GOOGLE_DRIVE_CREDENTIALS_PATH', 'config/google_credentials.json'))
    backup_folder_id: str = field(default_factory=lambda: get_env('GOOGLE_DRIVE_BACKUP_FOLDER_ID'))
    enabled: bool = field(default_factory=lambda: get_env_bool('GOOGLE_DRIVE_ENABLED', False))
    
    @property
    def is_configured(self) -> bool:
        """Check if Google Drive is configured."""
        return bool(self.backup_folder_id and Path(self.credentials_path).exists())


@dataclass
class MCPConfig:
    """Claude MCP server configuration."""
    port: int = field(default_factory=lambda: get_env_int('MCP_SERVER_PORT', 8765))
    log_level: str = field(default_factory=lambda: get_env('MCP_LOG_LEVEL', 'INFO'))


@dataclass
class PricingConfig:
    """Pricing thresholds and settings."""
    bulk_threshold: float = field(default_factory=lambda: get_env_float('BULK_PRICE_THRESHOLD', 1.00))
    high_value_threshold: float = field(default_factory=lambda: get_env_float('HIGH_VALUE_THRESHOLD', 10.00))
    premium_threshold: float = field(default_factory=lambda: get_env_float('PREMIUM_VALUE_THRESHOLD', 50.00))
    foil_multiplier: float = field(default_factory=lambda: get_env_float('FOIL_PREMIUM_MULTIPLIER', 5.40))
    default_currency: str = field(default_factory=lambda: get_env('DEFAULT_CURRENCY', 'USD'))


@dataclass
class AutomationConfig:
    """Automation settings."""
    price_update_enabled: bool = field(default_factory=lambda: get_env_bool('AUTO_PRICE_UPDATE_ENABLED', True))
    price_update_hour: int = field(default_factory=lambda: get_env_int('AUTO_PRICE_UPDATE_HOUR', 6))
    backup_enabled: bool = field(default_factory=lambda: get_env_bool('AUTO_BACKUP_ENABLED', True))
    backup_hour: int = field(default_factory=lambda: get_env_int('AUTO_BACKUP_HOUR', 3))
    backup_retention_days: int = field(default_factory=lambda: get_env_int('BACKUP_RETENTION_DAYS', 30))


@dataclass
class AppConfig:
    """Main application configuration."""
    debug: bool = field(default_factory=lambda: get_env_bool('DEBUG', False))
    testing: bool = field(default_factory=lambda: get_env_bool('TESTING', False))
    log_level: str = field(default_factory=lambda: get_env('LOG_LEVEL', 'INFO'))
    log_file: str = field(default_factory=lambda: get_env('LOG_FILE', 'data/cardforge.log'))
    default_collection_name: str = field(default_factory=lambda: get_env('DEFAULT_COLLECTION_NAME', 'Main Collection'))
    
    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    scryfall: ScryfallConfig = field(default_factory=ScryfallConfig)
    tcgplayer: TCGPlayerConfig = field(default_factory=TCGPlayerConfig)
    cardmarket: CardMarketConfig = field(default_factory=CardMarketConfig)
    moxfield: MoxfieldConfig = field(default_factory=MoxfieldConfig)
    google_drive: GoogleDriveConfig = field(default_factory=GoogleDriveConfig)
    mcp: MCPConfig = field(default_factory=MCPConfig)
    pricing: PricingConfig = field(default_factory=PricingConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Get application configuration (cached singleton)."""
    return AppConfig()


def reload_config() -> AppConfig:
    """Reload configuration (clears cache)."""
    get_config.cache_clear()
    _load_env()
    return get_config()


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CARDFORGE_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
CACHE_DIR = DATA_DIR / 'cache'
BACKUP_DIR = DATA_DIR / 'backups'
EXPORT_DIR = DATA_DIR / 'exports'
IMPORT_DIR = DATA_DIR / 'imports'


# Ensure directories exist
for dir_path in [DATA_DIR, CACHE_DIR, BACKUP_DIR, EXPORT_DIR, IMPORT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
