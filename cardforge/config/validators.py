"""Configuration validation using Pydantic v2.

Validates all config files at runtime. TRAE's config files get validated
against these schemas to catch errors early.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Literal
from pathlib import Path


# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================


class OllamaConfigSchema(BaseModel):
    """Validated Ollama configuration."""

    base_url: HttpUrl = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama service",
    )
    default_model: str = Field(
        default="llama3.2:3b",
        pattern=r"^[a-z0-9.-]+:[a-z0-9.]+$",
        description="Default model name and tag",
    )
    timeout: int = Field(
        default=120,
        ge=10,
        le=600,
        description="Request timeout in seconds",
    )
    stream_chunk_size: int = Field(
        default=512,
        ge=1,
        le=4096,
        description="Chunk size for streaming responses",
    )

    class Config:
        str_strip_whitespace = True

    @field_validator("base_url", mode="before")
    @classmethod
    def validate_base_url(cls, v):
        """Ensure base_url has no trailing slash."""
        if isinstance(v, str):
            v = v.rstrip("/")
        return v


# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================


class DatabaseConfigSchema(BaseModel):
    """Validated database configuration."""

    path: str = Field(
        default="data/cardforge.db",
        description="Path to SQLite database file",
    )
    backup_dir: str = Field(
        default="data/backups",
        description="Directory for database backups",
    )
    enable_wal: bool = Field(
        default=True,
        description="Enable Write-Ahead Logging for better concurrency",
    )
    timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Database query timeout in seconds",
    )

    class Config:
        str_strip_whitespace = True


# ============================================================================
# API CONFIGURATION
# ============================================================================


class ApiConfigSchema(BaseModel):
    """Validated API configuration."""

    scryfall_base_url: HttpUrl = Field(
        default="https://api.scryfall.com",
        description="Scryfall API base URL",
    )
    scryfall_rate_limit: float = Field(
        default=0.1,
        gt=0,
        le=1,
        description="Requests per second to Scryfall (max 1)",
    )
    tcgplayer_api_key: Optional[str] = Field(
        default=None,
        description="TCGPlayer API key (optional)",
    )
    cache_duration_hours: int = Field(
        default=24,
        ge=1,
        le=720,
        description="Cache duration for API responses",
    )

    class Config:
        str_strip_whitespace = True


# ============================================================================
# ROOT SETTINGS SCHEMA
# ============================================================================


class SettingsSchema(BaseModel):
    """Root settings schema - validates entire config."""

    environment: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Deployment environment",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    ollama: OllamaConfigSchema = Field(
        default_factory=OllamaConfigSchema,
        description="Ollama service configuration",
    )
    database: DatabaseConfigSchema = Field(
        default_factory=DatabaseConfigSchema,
        description="Database configuration",
    )
    api: ApiConfigSchema = Field(
        default_factory=ApiConfigSchema,
        description="External API configuration",
    )

    class Config:
        validate_assignment = True
        json_schema_extra = {
            "example": {
                "environment": "development",
                "debug": False,
                "log_level": "INFO",
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "default_model": "llama3.2:3b",
                    "timeout": 120,
                },
                "database": {
                    "path": "data/cardforge.db",
                    "backup_dir": "data/backups",
                },
                "api": {
                    "scryfall_base_url": "https://api.scryfall.com",
                    "scryfall_rate_limit": 0.1,
                },
            }
        }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================


def validate_config(config_dict: dict) -> tuple[bool, list[str]]:
    """Validate config dictionary against schema.

    Args:
        config_dict: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, errors) where errors is list of validation messages
    """
    errors: list[str] = []

    try:
        SettingsSchema(**config_dict)
        return True, []
    except Exception as e:
        # Extract error messages from Pydantic validation error
        if hasattr(e, "errors"):
            for error in e.errors():
                loc = ".".join(str(x) for x in error["loc"])
                msg = error["msg"]
                errors.append(f"{loc}: {msg}")
        else:
            errors.append(str(e))
        return False, errors


def validate_config_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate config from JSON file.

    Args:
        file_path: Path to JSON config file

    Returns:
        Tuple of (is_valid, errors)
    """
    import json

    if not file_path.exists():
        return False, [f"Config file not found: {file_path}"]

    try:
        with open(file_path) as f:
            config_dict = json.load(f)
        return validate_config(config_dict)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON in config file: {e}"]
    except Exception as e:
        return False, [f"Error reading config file: {e}"]


__all__ = [
    "OllamaConfigSchema",
    "DatabaseConfigSchema",
    "ApiConfigSchema",
    "SettingsSchema",
    "validate_config",
    "validate_config_file",
]
