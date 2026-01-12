"""Type definitions and protocols for CardForge.

This module provides the contracts that all CardForge implementations must follow.
These types are defined FIRST to guide TRAE's implementation.
"""

from typing import TypeVar, Protocol, runtime_checkable, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Generic type variables
T = TypeVar('T')
CardT = TypeVar('CardT', bound='CardProtocol')


# ============================================================================
# ENUMS - Shared across models and database
# ============================================================================

class Rarity(str, Enum):
    """Card rarity levels from Scryfall."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"


class Condition(str, Enum):
    """Card condition grades (PSA-style)."""

    MINT = "mint"
    NEAR_MINT = "near_mint"
    LIGHTLY_PLAYED = "lightly_played"
    MODERATELY_PLAYED = "moderately_played"
    HEAVILY_PLAYED = "heavily_played"
    DAMAGED = "damaged"


class Foil(str, Enum):
    """Foil treatment types."""

    NON_FOIL = "non_foil"
    FOIL = "foil"
    ETCHED = "etched"


class Language(str, Enum):
    """Supported card languages."""

    ENGLISH = "english"
    JAPANESE = "japanese"
    SIMPLIFIED_CHINESE = "simplified_chinese"
    TRADITIONAL_CHINESE = "traditional_chinese"
    FRENCH = "french"
    GERMAN = "german"
    ITALIAN = "italian"
    PORTUGUESE = "portuguese"
    RUSSIAN = "russian"
    SPANISH = "spanish"
    KOREAN = "korean"


class Format(str, Enum):
    """MTG formats."""

    STANDARD = "standard"
    PIONEER = "pioneer"
    MODERN = "modern"
    COMMANDER = "commander"
    CANLANDER = "canlander"
    VINTAGE = "vintage"
    LEGACY = "legacy"
    CASUAL = "casual"
    CUBE = "cube"


# ============================================================================
# PROTOCOLS - Define interfaces without implementation
# ============================================================================


@runtime_checkable
class CardProtocol(Protocol):
    """Protocol defining the minimal card interface.
    
    Any card implementation must provide at least these properties.
    """

    @property
    def id(self) -> int:
        """Unique card ID in database."""
        ...

    @property
    def name(self) -> str:
        """Card name."""
        ...

    @property
    def scryfall_id(self) -> str:
        """Unique Scryfall API ID."""
        ...

    @property
    def oracle_id(self) -> str | None:
        """Oracle ID (same across printings)."""
        ...

    @property
    def set_code(self) -> str:
        """Magic set code (e.g., 'MOM', 'BRO')."""
        ...

    @property
    def rarity(self) -> Rarity:
        """Card rarity in this printing."""
        ...

    @property
    def cmc(self) -> float:
        """Converted mana cost."""
        ...

    @property
    def type_line(self) -> str:
        """Type line from Scryfall."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        ...


@runtime_checkable
class RepositoryProtocol(Protocol[T]):
    """Generic repository interface for data access."""

    async def get(self, id: int) -> T | None:
        """Get single item by ID."""
        ...

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get multiple items with pagination."""
        ...

    async def search(self, query: str) -> list[T]:
        """Search items by query."""
        ...

    async def create(self, item: T) -> T:
        """Create new item."""
        ...

    async def update(self, id: int, item: T) -> T | None:
        """Update existing item."""
        ...

    async def delete(self, id: int) -> bool:
        """Delete item by ID."""
        ...


@runtime_checkable
class ServiceProtocol(Protocol):
    """Base service interface."""

    async def initialize(self) -> None:
        """Initialize service."""
        ...

    async def shutdown(self) -> None:
        """Clean shutdown."""
        ...


# ============================================================================
# DATA CLASSES - Immutable value objects
# ============================================================================


@dataclass(frozen=True)
class PriceData:
    """Immutable price information for a card."""

    usd: Decimal | None = None
    usd_foil: Decimal | None = None
    eur: Decimal | None = None
    tix: Decimal | None = None
    timestamp: datetime | None = None

    def is_stale(self, hours: int = 24) -> bool:
        """Check if price data is older than specified hours."""
        if self.timestamp is None:
            return True
        age = datetime.now(self.timestamp.tzinfo) - self.timestamp
        return age.total_seconds() > (hours * 3600)


@dataclass(frozen=True)
class SearchFilters:
    """Immutable search filter parameters."""

    query: str = ""
    rarities: tuple[Rarity, ...] = ()
    min_cmc: int = 0
    max_cmc: int = 10
    colors: tuple[str, ...] = ()  # WUBRG
    formats: tuple[Format, ...] = ()
    sets: tuple[str, ...] = ()
    limit: int = 100
    offset: int = 0

    def is_empty(self) -> bool:
        """Check if no filters are applied."""
        return (
            not self.query
            and not self.rarities
            and not self.colors
            and not self.formats
            and not self.sets
            and self.min_cmc == 0
            and self.max_cmc == 10
        )


__all__ = [
    "T",
    "CardT",
    "Rarity",
    "Condition",
    "Foil",
    "Language",
    "Format",
    "CardProtocol",
    "RepositoryProtocol",
    "ServiceProtocol",
    "PriceData",
    "SearchFilters",
]
