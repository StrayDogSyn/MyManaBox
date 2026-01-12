"""Centralized exception definitions for CardForge.

All exceptions inherit from CardForgeError for consistent error handling.
TRAE's code should raise these exceptions, not create new ones.
"""

from typing import Optional


class CardForgeError(Exception):
    """Base exception for all CardForge errors.
    
    All other exceptions inherit from this. Allows catching all
    CardForge-specific errors with a single except clause.
    """

    pass


# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================


class ConfigurationError(CardForgeError):
    """Error in configuration."""

    pass


class MissingConfigError(ConfigurationError):
    """Required configuration file or environment variable is missing."""

    pass


class InvalidConfigError(ConfigurationError):
    """Configuration value is invalid (type, format, range)."""

    pass


# ============================================================================
# DATABASE ERRORS
# ============================================================================


class DatabaseError(CardForgeError):
    """Database operation error."""

    pass


class RecordNotFoundError(DatabaseError):
    """Requested record does not exist."""

    pass


class DuplicateRecordError(DatabaseError):
    """Record already exists (unique constraint violation)."""

    pass


class IntegrityError(DatabaseError):
    """Database integrity constraint violated."""

    pass


class DatabaseConnectionError(DatabaseError):
    """Cannot connect to database."""

    pass


class MigrationError(DatabaseError):
    """Error during database migration."""

    pass


# ============================================================================
# API ERRORS
# ============================================================================


class ApiError(CardForgeError):
    """External API error (Scryfall, TCGPlayer, etc)."""

    pass


class RateLimitError(ApiError):
    """API rate limit exceeded."""

    pass


class ApiConnectionError(ApiError):
    """Cannot connect to API (network error, timeout)."""

    pass


class ApiResponseError(ApiError):
    """Unexpected or malformed API response."""

    pass


class ApiAuthenticationError(ApiError):
    """API authentication failed."""

    pass


# ============================================================================
# AGENT/OLLAMA ERRORS
# ============================================================================


class AgentError(CardForgeError):
    """AI agent error."""

    pass


class ModelNotFoundError(AgentError):
    """Requested model is not available locally."""

    pass


class AgentTimeoutError(AgentError):
    """Agent took too long to respond."""

    pass


class ContextTooLargeError(AgentError):
    """Context/prompt exceeds model's context window."""

    pass


class OllamaConnectionError(AgentError):
    """Cannot connect to Ollama service."""

    pass


class ModelLoadError(AgentError):
    """Error loading or initializing model."""

    pass


# ============================================================================
# IMPORT/EXPORT ERRORS
# ============================================================================


class ImportError(CardForgeError):
    """Error during data import."""

    pass


class InvalidFormatError(ImportError):
    """Import file format is invalid."""

    pass


class ImportDataError(ImportError):
    """Error processing imported data."""

    pass


class ExportError(CardForgeError):
    """Error during data export."""

    pass


# ============================================================================
# VALIDATION ERRORS
# ============================================================================


class ValidationError(CardForgeError):
    """Data validation error."""

    pass


class SchemaValidationError(ValidationError):
    """Data does not match expected schema."""

    pass


class InvalidInputError(ValidationError):
    """User input is invalid."""

    pass


__all__ = [
    "CardForgeError",
    "ConfigurationError",
    "MissingConfigError",
    "InvalidConfigError",
    "DatabaseError",
    "RecordNotFoundError",
    "DuplicateRecordError",
    "IntegrityError",
    "DatabaseConnectionError",
    "MigrationError",
    "ApiError",
    "RateLimitError",
    "ApiConnectionError",
    "ApiResponseError",
    "ApiAuthenticationError",
    "AgentError",
    "ModelNotFoundError",
    "AgentTimeoutError",
    "ContextTooLargeError",
    "OllamaConnectionError",
    "ModelLoadError",
    "ImportError",
    "InvalidFormatError",
    "ImportDataError",
    "ExportError",
    "ValidationError",
    "SchemaValidationError",
    "InvalidInputError",
]
