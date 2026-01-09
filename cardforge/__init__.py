"""
CardForge - Professional MTG Collection Management Platform

A comprehensive Magic: The Gathering collection management system with:
- SQLite database with full-text search
- Multi-source price aggregation (Scryfall, TCGPlayer, CardKingdom)
- Deck building with inventory-aware buy lists
- Claude MCP integration for AI-powered optimization
- Platform sync (Moxfield, ManaBox)
- Automated backups to Google Drive
"""

__version__ = "2.0.0"
__author__ = "Hunter @ StrayDog Syndications LLC"
__app_name__ = "CardForge"

from cardforge.config import get_config, AppConfig

__all__ = [
    "__version__",
    "__author__", 
    "__app_name__",
    "get_config",
    "AppConfig",
]
