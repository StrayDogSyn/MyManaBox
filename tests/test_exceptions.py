"""Tests for exception infrastructure."""

import pytest
from cardforge.exceptions import (
    CardForgeError,
    ConfigurationError,
    MissingConfigError,
    DatabaseError,
    RecordNotFoundError,
    ApiError,
    AgentError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_all_exceptions_inherit_from_base(self):
        """All exceptions inherit from CardForgeError."""
        exceptions = [
            ConfigurationError,
            MissingConfigError,
            DatabaseError,
            RecordNotFoundError,
            ApiError,
            AgentError,
            ValidationError,
        ]
        for exc in exceptions:
            assert issubclass(exc, CardForgeError)

    def test_exception_catching(self):
        """Can catch multiple exceptions with base class."""
        with pytest.raises(CardForgeError):
            raise MissingConfigError("test config missing")

        with pytest.raises(DatabaseError):
            raise RecordNotFoundError("record not found")

    def test_exception_messages(self):
        """Exceptions preserve messages."""
        msg = "This is a test error"
        exc = MissingConfigError(msg)
        assert str(exc) == msg


class TestDatabaseExceptions:
    """Tests for database-related exceptions."""

    def test_record_not_found(self):
        """RecordNotFoundError can be raised and caught."""
        with pytest.raises(RecordNotFoundError):
            raise RecordNotFoundError("Card not found with id=123")

    def test_duplicate_record(self):
        """DuplicateRecordError for constraint violations."""
        with pytest.raises(DatabaseError):
            from cardforge.exceptions import DuplicateRecordError

            raise DuplicateRecordError("Card with scryfall_id already exists")


class TestAgentExceptions:
    """Tests for agent-related exceptions."""

    def test_model_not_found(self):
        """ModelNotFoundError when model unavailable."""
        from cardforge.exceptions import ModelNotFoundError

        with pytest.raises(AgentError):
            raise ModelNotFoundError("llama3.1:70b not found locally")

    def test_agent_timeout(self):
        """AgentTimeoutError for slow responses."""
        from cardforge.exceptions import AgentTimeoutError

        with pytest.raises(AgentError):
            raise AgentTimeoutError("Agent took too long (> 120s)")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
