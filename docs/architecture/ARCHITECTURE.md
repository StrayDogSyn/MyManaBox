# CardForge Architecture

## Overview

CardForge is built with a clean, layered architecture following separation of concerns:

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │     CLI         │  │      MCP        │  │   (Future GUI)  │  │
│  │  Click + Rich   │  │  Claude Desktop │  │                 │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
┌───────────┴────────────────────┴────────────────────┴───────────┐
│                         Service Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ CardService │ │CollectionSvc│ │ DeckService │ │ TradeService│ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬─────┘ │
└─────────┼───────────────┼───────────────┼───────────────┼───────┘
          │               │               │               │
┌─────────┴───────────────┴───────────────┴───────────────┴───────┐
│                       Repository Layer                           │
│  ┌──────────────┐ ┌────────────────┐ ┌───────────┐ ┌──────────┐ │
│  │ CardRepository│ │CollectionRepo  │ │ DeckRepo  │ │TradeRepo │ │
│  └───────┬──────┘ └───────┬────────┘ └─────┬─────┘ └────┬─────┘ │
└──────────┼────────────────┼────────────────┼────────────┼───────┘
           │                │                │            │
┌──────────┴────────────────┴────────────────┴────────────┴───────┐
│                        Data Layer                                │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │   SQLite (FTS5)     │  │     External APIs               │   │
│  │   - cards           │  │     - Scryfall                  │   │
│  │   - collections     │  │     - TCGPlayer                 │   │
│  │   - decks           │  │     - Moxfield                  │   │
│  │   - buy_list        │  │                                 │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```text
cardforge/
├── __init__.py           # Package initialization
├── __main__.py           # Entry point for `python -m cardforge`
│
├── api/                  # External API clients
│   ├── __init__.py
│   ├── scryfall.py       # Scryfall card data API
│   ├── tcgplayer.py      # TCGPlayer pricing API
│   └── moxfield.py       # Moxfield deck import
│
├── cli/                  # Command-line interface
│   ├── __init__.py
│   └── main.py           # Click commands with Rich formatting
│
├── config/               # Configuration management
│   ├── __init__.py
│   └── settings.py       # Pydantic settings from env/files
│
├── database/             # Database layer
│   ├── __init__.py
│   ├── connection.py     # Async SQLite connection pool
│   ├── schema.sqlite.sql # Full database schema (SQLite)
│   └── migrations/       # Schema migrations
│
├── models/               # Pydantic data models
│   ├── __init__.py
│   ├── base.py           # Base model with JSON/DB serialization
│   ├── card.py           # Card, CardFace, CardPrices
│   ├── collection.py     # Collection, CollectionCard
│   ├── deck.py           # Deck, DeckCard
│   ├── trade.py          # BuyListItem, SellListItem
│   ├── enums.py          # Color, Rarity, Condition enums
│   └── sync.py           # SetInfo, SyncStatus
│
├── repositories/         # Data access layer
│   ├── __init__.py
│   ├── base_repository.py    # Generic CRUD operations
│   ├── card_repository.py    # Card-specific queries with FTS
│   ├── collection_repository.py
│   ├── deck_repository.py
│   └── trade_repository.py
│
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── card_service.py       # Card search and Scryfall sync
│   ├── collection_service.py # Collection management
│   ├── deck_service.py       # Deck building and analysis
│   ├── trade_service.py      # Buy/sell list management
│   ├── pricing_service.py    # Price aggregation
│   └── sync_service.py       # Data sync orchestration
│
├── mcp/                  # Model Context Protocol
│   ├── __init__.py
│   └── server.py         # Claude Desktop integration
│
└── tests/                # Test suite
    ├── __init__.py
    ├── test_models.py
    ├── test_repositories.py
    └── test_services.py
```

## Key Design Patterns

### Repository Pattern

All database access goes through repository classes that handle SQL generation, parameter binding, and model conversion.

### Service Layer

Business logic is encapsulated in service classes that orchestrate multiple repositories and external APIs.

### Pydantic Models

All data structures use Pydantic for automatic validation, JSON serialization, and type safety.

### Async-First

All I/O operations (database, HTTP) are async for optimal performance.

### Computed Fields

Pydantic's `@computed_field` decorator for derived properties that aren't stored.

## Database Schema

Key tables:

- `cards` - Card data from Scryfall (normalized)
- `cards_fts` - FTS5 virtual table for full-text search
- `sets` - Set metadata
- `collections` - User collection containers
- `collection_cards` - Cards in collections with quantity/condition
- `decks` - Deck containers
- `deck_cards` - Cards in decks with categories
- `buy_list` / `sell_list` - Trade tracking
