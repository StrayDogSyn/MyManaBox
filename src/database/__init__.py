"""
CardForge Database Layer
========================

This package provides database connectivity, schema management, and data access patterns.

Components:
-----------
- connection: Database connection management and session handling
- models: SQLAlchemy ORM models for all database tables
- repositories: Repository pattern for data access
- migrations: SQL migration scripts for schema evolution
"""

from src.database.connection import DatabaseManager, get_db_session
from src.database.models import (
    Base,
    Card,
    CollectionItem,
    Deck,
    DeckCard,
    PriceHistory,
    Trade,
)

__all__ = [
    "DatabaseManager",
    "get_db_session",
    "Base",
    "Card",
    "CollectionItem",
    "Deck",
    "DeckCard",
    "PriceHistory",
    "Trade",
]
