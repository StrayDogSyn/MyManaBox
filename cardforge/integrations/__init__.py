"""CardForge External Integrations Layer.

This module provides communication with external services and APIs.
Following clean architecture principles, this layer:

Responsibilities:
- Handle HTTP requests/responses
- Return raw API data (Dict, JSON)
- Manage rate limiting, retries, caching
- Abstract external service communication

Rules:
- No business logic (that's in services)
- No database access (that's in data)
- Doesn't know about domain entities (services convert)
- Services layer orchestrates and converts API responses

Supported Integrations:
- Scryfall: Card data and search
- TCGPlayer: Pricing information
- Moxfield: Deck sharing and sync
- Google Drive: Cloud backup

Example Usage:
    from cardforge.integrations import ScryfallClient
    
    client = ScryfallClient()
    card_data = await client.get_card_by_name("Lightning Bolt")
    # Returns raw API response, service layer converts to domain entity
"""

# Re-export from api package for clean architecture naming
from cardforge.api import (
    BaseAPIClient,
    RateLimiter,
    InMemoryCache,
    ScryfallClient,
    TCGPlayerClient,
    MoxfieldClient,
    GoogleDriveClient,
)

# Create submodule aliases for organized imports
# These allow: from cardforge.integrations.scryfall import ScryfallClient
import cardforge.api.scryfall_client as scryfall
import cardforge.api.tcgplayer_client as tcgplayer
import cardforge.api.moxfield_client as moxfield
import cardforge.api.google_drive_client as google_drive

__all__ = [
    # Base utilities
    "BaseAPIClient",
    "RateLimiter",
    "InMemoryCache",
    # API Clients
    "ScryfallClient",
    "TCGPlayerClient",
    "MoxfieldClient",
    "GoogleDriveClient",
    # Submodules
    "scryfall",
    "tcgplayer",
    "moxfield",
    "google_drive",
]
