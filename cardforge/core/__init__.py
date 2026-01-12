"""CardForge Core Domain Layer.

This module contains the domain entities, types, and exceptions that form
the foundation of CardForge. Following clean architecture principles:

- Pure Python dataclasses or Pydantic models
- Business logic only (no I/O operations)
- No external dependencies (no SQLAlchemy, no aiohttp)
- No framework code

All other layers depend on this layer, but this layer depends on nothing.
"""

# Re-export models from the models package
from cardforge.models import (
    # Enums
    CardColor,
    Rarity,
    Condition,
    FoilType,
    Format,
    Legality,
    CardLayout,
    CardType,
    DeckCategory,
    BuyListStatus,
    SellListStatus,
    SellReason,
    SyncStatus,
    SyncPlatform,
    GameResult,
    PriceSource,
    Language,
    # Base
    BaseModel,
    TimestampMixin,
    # Card
    Card,
    CardFace,
    CardPrices,
    PriceRecord,
    PriceQuote,
    AggregatedPrice,
    # Collection
    Collection,
    CollectionCard,
    OwnershipInfo,
    CollectionStats,
    # Deck
    Deck,
    DeckCard,
    DeckAnalysis,
    MissingCard,
    GameRecord,
    # Trade
    BuyListItem,
    SellListItem,
    BuyListSummary,
    SellListSummary,
    DuplicateCard,
    # Sync
    SyncState,
    SetInfo,
)

# Re-export types from the types package
from cardforge.types import (
    T,
    CardT,
    CardProtocol,
    RepositoryProtocol,
    ServiceProtocol,
    PriceData,
    SearchFilters,
)

# Re-export exceptions
from cardforge.exceptions import (
    CardForgeError,
    # Configuration
    ConfigurationError,
    MissingConfigError,
    InvalidConfigError,
    # Database
    DatabaseError,
    RecordNotFoundError,
    DuplicateRecordError,
    IntegrityError,
    DatabaseConnectionError,
    MigrationError,
    # API
    ApiError,
    RateLimitError,
    ApiConnectionError,
    ApiResponseError,
    ApiAuthenticationError,
    # Agent
    AgentError,
    ModelNotFoundError,
    AgentTimeoutError,
    ContextTooLargeError,
    OllamaConnectionError,
    ModelLoadError,
    # Import/Export
    InvalidFormatError,
    ImportDataError,
    ExportError,
    # Validation
    ValidationError,
    SchemaValidationError,
    InvalidInputError,
)

__all__ = [
    # Enums
    "CardColor",
    "Rarity",
    "Condition",
    "FoilType",
    "Format",
    "Legality",
    "CardLayout",
    "CardType",
    "DeckCategory",
    "BuyListStatus",
    "SellListStatus",
    "SellReason",
    "SyncStatus",
    "SyncPlatform",
    "GameResult",
    "PriceSource",
    "Language",
    # Base
    "BaseModel",
    "TimestampMixin",
    # Card
    "Card",
    "CardFace",
    "CardPrices",
    "PriceRecord",
    "PriceQuote",
    "AggregatedPrice",
    # Collection
    "Collection",
    "CollectionCard",
    "OwnershipInfo",
    "CollectionStats",
    # Deck
    "Deck",
    "DeckCard",
    "DeckAnalysis",
    "MissingCard",
    "GameRecord",
    # Trade
    "BuyListItem",
    "SellListItem",
    "BuyListSummary",
    "SellListSummary",
    "DuplicateCard",
    # Sync
    "SyncState",
    "SetInfo",
    # Types
    "T",
    "CardT",
    "CardProtocol",
    "RepositoryProtocol",
    "ServiceProtocol",
    "PriceData",
    "SearchFilters",
    # Exceptions
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
    "InvalidFormatError",
    "ImportDataError",
    "ExportError",
    "ValidationError",
    "SchemaValidationError",
    "InvalidInputError",
]
