"""
CardForge Scryfall Client
Async Scryfall API integration (FREE - no key required)
"""

from typing import Optional, List, Dict, Any
from datetime import timedelta
import asyncio
import aiohttp

from cardforge.models import Card, SetInfo
from .base_client import BaseAPIClient


class ScryfallClient(BaseAPIClient):
    """
    Async Scryfall API client.
    
    Scryfall is the primary card data source (FREE).
    Rate limit: 10 requests/second with good behavior.
    """
    
    base_url = "https://api.scryfall.com"
    rate_limit = 10.0  # Per Scryfall guidelines
    cache_ttl = timedelta(hours=24)  # Card data doesn't change often
    
    async def health_check(self) -> bool:
        """Check if Scryfall API is reachable."""
        try:
            await self.get("/")
            return True
        except Exception:
            return False
    
    # =====================
    # Card Search Methods
    # =====================
    
    async def search_cards(
        self,
        query: str,
        unique: str = "cards",
        order: str = "name",
        direction: str = "auto",
        include_extras: bool = False,
        include_multilingual: bool = False,
        include_variations: bool = False,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Search for cards using Scryfall syntax.
        
        Args:
            query: Scryfall search query (supports full syntax)
            unique: "cards", "art", or "prints"
            order: Sort order field
            direction: "auto", "asc", or "desc"
            include_extras: Include tokens, planes, etc.
            include_multilingual: Include non-English prints
            include_variations: Include all variations
            page: Page number (175 cards per page)
        
        Returns:
            Search results with has_more, next_page, and data
        """
        params = {
            "q": query,
            "unique": unique,
            "order": order,
            "dir": direction,
            "page": page,
        }
        
        if include_extras:
            params["include_extras"] = "true"
        if include_multilingual:
            params["include_multilingual"] = "true"
        if include_variations:
            params["include_variations"] = "true"
        
        return await self.get("/cards/search", params=params)
    
    async def search_all_pages(
        self,
        query: str,
        max_pages: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search and collect all pages of results.
        
        Be careful with broad queries - this can return thousands of cards.
        """
        all_cards = []
        page = 1
        
        while page <= max_pages:
            result = await self.search_cards(query, page=page, **kwargs)
            all_cards.extend(result.get("data", []))
            
            if not result.get("has_more"):
                break
            
            page += 1
            await asyncio.sleep(0.1)  # Be polite
        
        return all_cards
    
    # =====================
    # Individual Card Methods
    # =====================
    
    async def get_card_by_id(self, scryfall_id: str) -> Dict[str, Any]:
        """Get a card by Scryfall UUID."""
        return await self.get(f"/cards/{scryfall_id}")
    
    async def get_card_by_name(
        self,
        name: str,
        exact: bool = True,
        set_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a card by name.
        
        Args:
            name: Card name
            exact: If True, requires exact match
            set_code: Optional set code to get specific printing
        """
        params = {}
        if exact:
            params["exact"] = name
        else:
            params["fuzzy"] = name
        
        if set_code:
            params["set"] = set_code
        
        return await self.get("/cards/named", params=params)
    
    async def get_card_by_set(self, set_code: str, collector_number: str) -> Dict[str, Any]:
        """Get a specific printing by set and collector number."""
        return await self.get(f"/cards/{set_code}/{collector_number}")
    
    async def get_card_by_oracle_id(self, oracle_id: str) -> Dict[str, Any]:
        """Get all printings of a card by oracle ID."""
        return await self.search_cards(f"oracle_id:{oracle_id}", unique="prints")
    
    async def get_card_by_tcgplayer_id(self, tcgplayer_id: int) -> Dict[str, Any]:
        """Get card by TCGPlayer ID."""
        return await self.get(f"/cards/tcgplayer/{tcgplayer_id}")
    
    async def get_card_by_arena_id(self, arena_id: int) -> Dict[str, Any]:
        """Get card by MTG Arena ID."""
        return await self.get(f"/cards/arena/{arena_id}")
    
    async def get_random_card(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get a random card, optionally matching a query."""
        params = {"q": query} if query else None
        return await self.get("/cards/random", params=params, use_cache=False)
    
    async def autocomplete(self, query: str) -> List[str]:
        """Autocomplete card names."""
        result = await self.get("/cards/autocomplete", params={"q": query})
        return result.get("data", [])
    
    # =====================
    # Bulk Data Methods
    # =====================
    
    async def get_bulk_data_info(self) -> List[Dict[str, Any]]:
        """Get available bulk data downloads."""
        result = await self.get("/bulk-data")
        return result.get("data", [])
    
    async def get_all_cards_download_uri(self) -> str:
        """Get download URI for all cards bulk data."""
        bulk_data = await self.get_bulk_data_info()
        for item in bulk_data:
            if item.get("type") == "all_cards":
                return item.get("download_uri")
        raise ValueError("All cards bulk data not found")
    
    async def get_oracle_cards_download_uri(self) -> str:
        """Get download URI for oracle cards (one per oracle_id)."""
        bulk_data = await self.get_bulk_data_info()
        for item in bulk_data:
            if item.get("type") == "oracle_cards":
                return item.get("download_uri")
        raise ValueError("Oracle cards bulk data not found")
    
    # =====================
    # Set Methods
    # =====================
    
    async def get_all_sets(self) -> List[Dict[str, Any]]:
        """Get all MTG sets."""
        result = await self.get("/sets")
        return result.get("data", [])
    
    async def get_set(self, code: str) -> Dict[str, Any]:
        """Get a specific set by code."""
        return await self.get(f"/sets/{code}")
    
    async def get_set_by_id(self, set_id: str) -> Dict[str, Any]:
        """Get a specific set by Scryfall ID."""
        return await self.get(f"/sets/{set_id}")
    
    # =====================
    # Catalog Methods
    # =====================
    
    async def get_catalog(self, catalog_name: str) -> List[str]:
        """
        Get a catalog of known values.
        
        Available catalogs:
        - card-names
        - artist-names
        - word-bank
        - creature-types
        - planeswalker-types
        - land-types
        - artifact-types
        - enchantment-types
        - spell-types
        - powers
        - toughnesses
        - loyalties
        - watermarks
        - keyword-abilities
        - keyword-actions
        - ability-words
        """
        result = await self.get(f"/catalog/{catalog_name}")
        return result.get("data", [])
    
    # =====================
    # Symbol Methods
    # =====================
    
    async def get_symbology(self) -> List[Dict[str, Any]]:
        """Get all card symbols."""
        result = await self.get("/symbology")
        return result.get("data", [])
    
    async def parse_mana_cost(self, cost: str) -> Dict[str, Any]:
        """Parse a mana cost string."""
        return await self.get("/symbology/parse-mana", params={"cost": cost})
    
    # =====================
    # Helper Methods
    # =====================
    
    async def get_card_as_model(self, scryfall_id: str) -> Card:
        """Get card and convert to Card model."""
        data = await self.get_card_by_id(scryfall_id)
        return Card.from_scryfall(data)
    
    async def get_set_as_model(self, code: str) -> SetInfo:
        """Get set and convert to SetInfo model."""
        data = await self.get_set(code)
        return SetInfo(
            code=data['code'],
            name=data['name'],
            set_type=data.get('set_type'),
            card_count=data.get('card_count', 0),
            release_date=data.get('released_at'),
            icon_svg_uri=data.get('icon_svg_uri'),
            scryfall_id=data.get('id'),
        )
    
    async def get_cards_batch(
        self, 
        identifiers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get multiple cards in one request (POST endpoint).
        
        Each identifier can be one of:
        - {"id": scryfall_uuid}
        - {"name": "exact name"}
        - {"set": "code", "collector_number": "123"}
        - {"oracle_id": oracle_uuid}
        
        Max 75 identifiers per request.
        """
        if len(identifiers) > 75:
            raise ValueError("Maximum 75 identifiers per batch request")
        
        return await self.post(
            "/cards/collection",
            data={"identifiers": identifiers}
        )
    
    async def search_commander_options(
        self,
        colors: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search for potential commanders with filters."""
        query_parts = ["is:commander"]
        
        if colors:
            color_string = "".join(colors)
            query_parts.append(f"id<={color_string}")
        
        if min_price is not None:
            query_parts.append(f"usd>={min_price}")
        
        if max_price is not None:
            query_parts.append(f"usd<={max_price}")
        
        query = " ".join(query_parts)
        return await self.search_all_pages(query)
