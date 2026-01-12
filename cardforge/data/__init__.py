"""CardForge Data Persistence Layer.

This module provides the data access layer following the repository pattern.
It abstracts all database operations and returns domain entities.

Responsibilities:
- Store and retrieve domain entities
- Handle all SQL/database logic
- Map database rows to domain entities
- Database migrations

Rules:
- Returns domain entities, not database rows
- No business logic (that's in services)
- No API calls (that's in integrations)
- Depends on core (domain entities)
"""

# Re-export database connection utilities
from cardforge.database.connection import (
    DatabaseConnection,
    get_connection,
    get_db,
    init_db,
    get_transaction,
)

# Re-export repositories
from cardforge.repositories import (
    BaseRepository,
    CardRepository,
    SetRepository,
    CollectionRepository,
    CollectionCardRepository,
    DeckRepository,
    DeckCardRepository,
    BuyListRepository,
    SellListRepository,
    PriceRepository,
)

# Re-export migration utilities
from cardforge.database import (
    MigrationRunner,
    run_migrations,
    check_migration_status,
    init_database,
)

__all__ = [
    # Connection
    "DatabaseConnection",
    "get_connection",
    "get_db",
    "init_db",
    "get_transaction",
    # Repositories
    "BaseRepository",
    "CardRepository",
    "SetRepository",
    "CollectionRepository",
    "CollectionCardRepository",
    "DeckRepository",
    "DeckCardRepository",
    "BuyListRepository",
    "SellListRepository",
    "PriceRepository",
    # Migrations
    "MigrationRunner",
    "run_migrations",
    "check_migration_status",
    "init_database",
]
