"""Tests for configuration validation."""

import pytest
from pathlib import Path
from cardforge.config.validators import (
    OllamaConfigSchema,
    DatabaseConfigSchema,
    ApiConfigSchema,
    SettingsSchema,
    validate_config,
    validate_config_file,
)
from pydantic import ValidationError


class TestOllamaConfigValidation:
    """Tests for Ollama configuration validation."""

    def test_ollama_valid_config(self):
        """Valid Ollama config passes validation."""
        config = OllamaConfigSchema(
            base_url="http://localhost:11434",
            default_model="llama3.2:3b",
            timeout=120,
        )
        assert config.base_url == "http://localhost:11434"
        assert config.default_model == "llama3.2:3b"

    def test_ollama_base_url_stripped(self):
        """Base URL trailing slash is removed."""
        config = OllamaConfigSchema(base_url="http://localhost:11434/")
        assert str(config.base_url) == "http://localhost:11434"

    def test_ollama_invalid_timeout(self):
        """Invalid timeout raises error."""
        with pytest.raises(ValidationError) as exc_info:
            OllamaConfigSchema(timeout=1000)  # Too high
        assert "less than or equal to 600" in str(exc_info.value)

    def test_ollama_invalid_model_format(self):
        """Invalid model name format raises error."""
        with pytest.raises(ValidationError):
            OllamaConfigSchema(default_model="invalid model name")


class TestDatabaseConfigValidation:
    """Tests for database configuration validation."""

    def test_database_valid_config(self):
        """Valid database config passes validation."""
        config = DatabaseConfigSchema(
            path="data/test.db",
            backup_dir="data/backups",
            enable_wal=True,
        )
        assert config.path == "data/test.db"
        assert config.enable_wal is True

    def test_database_invalid_timeout(self):
        """Invalid timeout raises error."""
        with pytest.raises(ValidationError):
            DatabaseConfigSchema(timeout=1)  # Too low


class TestApiConfigValidation:
    """Tests for API configuration validation."""

    def test_api_valid_config(self):
        """Valid API config passes validation."""
        config = ApiConfigSchema(
            scryfall_base_url="https://api.scryfall.com",
            scryfall_rate_limit=0.1,
            cache_duration_hours=24,
        )
        assert config.cache_duration_hours == 24

    def test_api_invalid_rate_limit(self):
        """Rate limit must be > 0 and <= 1."""
        with pytest.raises(ValidationError):
            ApiConfigSchema(scryfall_rate_limit=0)  # Too low

        with pytest.raises(ValidationError):
            ApiConfigSchema(scryfall_rate_limit=2.0)  # Too high


class TestSettingsSchemaValidation:
    """Tests for root settings schema validation."""

    def test_settings_valid_full_config(self, sample_config_dict):
        """Valid full config passes validation."""
        settings = SettingsSchema(**sample_config_dict)
        assert settings.environment == "testing"
        assert settings.debug is True

    def test_settings_default_values(self):
        """Settings provides sensible defaults."""
        settings = SettingsSchema()
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.log_level == "INFO"

    def test_settings_invalid_environment(self):
        """Invalid environment raises error."""
        with pytest.raises(ValidationError):
            SettingsSchema(environment="invalid")

    def test_settings_invalid_log_level(self):
        """Invalid log level raises error."""
        with pytest.raises(ValidationError):
            SettingsSchema(log_level="INVALID")


class TestValidateConfigFunction:
    """Tests for validate_config() helper."""

    def test_validate_config_valid(self, sample_config_dict):
        """Valid config passes validation."""
        is_valid, errors = validate_config(sample_config_dict)
        assert is_valid is True
        assert errors == []

    def test_validate_config_invalid(self):
        """Invalid config returns errors."""
        invalid_config = {
            "environment": "invalid",
            "ollama": {"timeout": 1000},  # Too high
        }
        is_valid, errors = validate_config(invalid_config)
        assert is_valid is False
        assert len(errors) > 0

    def test_validate_config_returns_error_messages(self):
        """Error messages are human-readable."""
        invalid_config = {"environment": "bad"}
        is_valid, errors = validate_config(invalid_config)
        assert is_valid is False
        assert any("development" in str(e) or "production" in str(e) for e in errors)


class TestValidateConfigFileFunction:
    """Tests for validate_config_file() helper."""

    def test_validate_config_file_not_found(self):
        """Missing file returns error."""
        is_valid, errors = validate_config_file(Path("/nonexistent/config.json"))
        assert is_valid is False
        assert any("not found" in e for e in errors)

    def test_validate_config_file_valid(self, tmp_path, sample_config_dict):
        """Valid config file passes validation."""
        import json

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(sample_config_dict))

        is_valid, errors = validate_config_file(config_path)
        assert is_valid is True
        assert errors == []

    def test_validate_config_file_invalid_json(self, tmp_path):
        """Invalid JSON returns error."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{invalid json")

        is_valid, errors = validate_config_file(config_path)
        assert is_valid is False
        assert any("JSON" in e for e in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
