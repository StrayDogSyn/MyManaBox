"""CardForge - Professional MTG Collection Management Platform.

A comprehensive Magic: The Gathering collection management system with:
- SQLite database with full-text search
- Multi-source price aggregation (Scryfall, TCGPlayer, CardKingdom)
- Deck building with inventory-aware buy lists
- Claude MCP integration for AI-powered optimization
- Platform sync (Moxfield, ManaBox)
- Automated backups to Google Drive

Architecture:
    cardforge/
    ├── core/           # Domain layer (models, types, exceptions)
    ├── data/           # Persistence layer (repositories, migrations)
    ├── services/       # Business logic layer
    ├── integrations/   # External API layer (Scryfall, TCGPlayer, etc.)
    ├── ai/             # AI agents and orchestration
    ├── cli/            # Command-line interface
    └── config/         # Configuration management

Usage:
    # Import domain entities
    from cardforge.core import Card, Collection, Deck
    
    # Import repositories
    from cardforge.data import CardRepository, CollectionRepository
    
    # Import services
    from cardforge.services import CollectionService, DeckService
    
    # Import API clients
    from cardforge.integrations import ScryfallClient, TCGPlayerClient
"""

__version__ = "2.0.0"
__author__ = "Hunter @ StrayDog Syndications LLC"
__app_name__ = "CardForge"

from cardforge.config import get_config, AppConfig

# Expose subpackages for clean imports
from cardforge import core
from cardforge import data
from cardforge import integrations
from cardforge import services
from cardforge import ai
from cardforge import cli

__all__ = [
    "__version__",
    "__author__",
    "__app_name__",
    "get_config",
    "AppConfig",
    # Architecture layers
    "core",
    "data",
    "integrations",
    "services",
    "ai",
    "cli",
]
