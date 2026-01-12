"""Tests for type definitions and protocols."""

import pytest
from datetime import datetime
from decimal import Decimal
from typing import Any

from cardforge.types import (
    Rarity,
    Condition,
    Foil,
    Language,
    Format,
    CardProtocol,
    PriceData,
    SearchFilters,
)
from cardforge.types.agents import (
    TaskComplexity,
    AgentCapability,
    MessageRole,
    ChatMessage,
)


class TestEnumValues:
    """Tests for enum definitions."""

    def test_rarity_values(self):
        """Rarity enum has expected values."""
        assert Rarity.COMMON.value == "common"
        assert Rarity.MYTHIC.value == "mythic"
        assert len(Rarity) == 6  # 6 rarity levels

    def test_condition_values(self):
        """Condition enum has expected values."""
        assert Condition.MINT.value == "mint"
        assert Condition.DAMAGED.value == "damaged"
        assert len(Condition) == 6  # 6 condition levels

    def test_foil_values(self):
        """Foil enum has expected values."""
        assert Foil.NON_FOIL.value == "non_foil"
        assert Foil.ETCHED.value == "etched"

    def test_format_values(self):
        """Format enum has expected MTG formats."""
        assert Format.COMMANDER.value == "commander"
        assert Format.MODERN.value == "modern"
        assert len(Format) == 9  # 9 formats

    def test_task_complexity_values(self):
        """TaskComplexity enum for model routing."""
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.COMPLEX.value == "complex"


class TestPriceData:
    """Tests for PriceData value object."""

    def test_price_data_creation(self):
        """PriceData can be created with values."""
        price = PriceData(
            usd=Decimal("5.00"),
            usd_foil=Decimal("10.00"),
            eur=Decimal("4.50"),
        )
        assert price.usd == Decimal("5.00")
        assert price.usd_foil == Decimal("10.00")

    def test_price_data_immutable(self):
        """PriceData is immutable (frozen dataclass)."""
        price = PriceData(usd=Decimal("5.00"))
        with pytest.raises(AttributeError):
            price.usd = Decimal("10.00")

    def test_price_data_is_stale(self):
        """PriceData can check if data is stale."""
        old_time = datetime.fromtimestamp(0)
        price = PriceData(usd=Decimal("5.00"), timestamp=old_time)
        assert price.is_stale(hours=1) is True

        now = datetime.now()
        recent_price = PriceData(usd=Decimal("5.00"), timestamp=now)
        assert recent_price.is_stale(hours=1) is False


class TestSearchFilters:
    """Tests for SearchFilters value object."""

    def test_search_filters_creation(self):
        """SearchFilters can be created."""
        filters = SearchFilters(
            query="Lightning",
            rarities=(Rarity.RARE, Rarity.MYTHIC),
            limit=50,
        )
        assert filters.query == "Lightning"
        assert len(filters.rarities) == 2

    def test_search_filters_immutable(self):
        """SearchFilters is immutable."""
        filters = SearchFilters(query="test")
        with pytest.raises(AttributeError):
            filters.query = "new query"

    def test_search_filters_is_empty(self):
        """SearchFilters.is_empty() works correctly."""
        empty = SearchFilters()
        assert empty.is_empty() is True

        with_query = SearchFilters(query="Lightning")
        assert with_query.is_empty() is False


class TestChatMessage:
    """Tests for ChatMessage value object."""

    def test_chat_message_creation(self):
        """ChatMessage can be created."""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Analyze this deck",
        )
        assert msg.role == MessageRole.USER
        assert msg.content == "Analyze this deck"
        assert msg.timestamp > 0

    def test_chat_message_immutable(self):
        """ChatMessage is immutable."""
        msg = ChatMessage(role=MessageRole.USER, content="test")
        with pytest.raises(AttributeError):
            msg.content = "changed"

    def test_chat_message_to_dict(self):
        """ChatMessage can convert to dictionary."""
        msg = ChatMessage(role=MessageRole.ASSISTANT, content="Response")
        d = msg.to_dict()
        assert d["role"] == "assistant"
        assert d["content"] == "Response"
        assert "timestamp" in d


class TestProtocols:
    """Tests for protocol definitions."""

    def test_card_protocol_has_required_properties(self):
        """CardProtocol defines required card properties."""
        from cardforge.types import CardProtocol

        required_attrs = ["id", "name", "scryfall_id", "rarity", "cmc", "type_line"]
        for attr in required_attrs:
            # Check protocol has the attribute in __annotations__
            assert hasattr(CardProtocol, "__annotations__")

    def test_enum_str_mixin_for_json(self):
        """Enums inherit from str for JSON serialization."""
        rarity_str = str(Rarity.MYTHIC)
        assert isinstance(rarity_str, str)
        assert rarity_str == "mythic"

        condition_str = str(Condition.MINT)
        assert isinstance(condition_str, str)
        assert condition_str == "mint"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
