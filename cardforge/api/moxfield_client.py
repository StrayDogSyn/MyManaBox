"""
CardForge Moxfield Client
Async Moxfield API integration for deck import/export
"""

from typing import Optional, List, Dict, Any
from datetime import timedelta

from .base_client import BaseAPIClient


class MoxfieldClient(BaseAPIClient):
    """
    Async Moxfield API client.
    
    Note: Moxfield doesn't have an official public API.
    This uses observed endpoints which may change.
    """
    
    base_url = "https://api2.moxfield.com"
    rate_limit = 2.0  # Be conservative with unofficial API
    cache_ttl = timedelta(minutes=30)
    
    def __init__(
        self,
        bearer_token: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        if bearer_token:
            self._headers["Authorization"] = f"Bearer {bearer_token}"
    
    async def health_check(self) -> bool:
        """Check if Moxfield API is reachable."""
        try:
            await self.get("/v2/users/me", use_cache=False)
            return True
        except Exception:
            return False
    
    # =====================
    # User Methods
    # =====================
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user info."""
        return await self.get("/v2/users/me", use_cache=False)
    
    async def get_user(self, username: str) -> Dict[str, Any]:
        """Get user info by username."""
        return await self.get(f"/v2/users/{username}")
    
    async def get_user_decks(
        self, 
        username: str,
        page: int = 1,
        page_size: int = 12,
    ) -> Dict[str, Any]:
        """Get user's public decks."""
        params = {
            "pageNumber": page,
            "pageSize": page_size,
        }
        return await self.get(f"/v2/users/{username}/decks", params=params)
    
    # =====================
    # Deck Methods
    # =====================
    
    async def get_deck(self, deck_id: str) -> Dict[str, Any]:
        """Get a deck by ID."""
        return await self.get(f"/v2/decks/all/{deck_id}")
    
    async def get_deck_cards(self, deck_id: str) -> Dict[str, Any]:
        """Get detailed card list for a deck."""
        deck = await self.get_deck(deck_id)
        return deck
    
    async def get_my_decks(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_type: str = "updated",
        sort_direction: str = "descending",
    ) -> Dict[str, Any]:
        """Get authenticated user's decks."""
        params = {
            "pageNumber": page,
            "pageSize": page_size,
            "sortType": sort_type,
            "sortDirection": sort_direction,
        }
        return await self.get("/v2/decks", params=params)
    
    async def export_deck_text(self, deck_id: str) -> str:
        """Export deck as text format."""
        # This returns plain text, not JSON
        url = f"{self.base_url}/v1/decks/all/{deck_id}/export"
        
        await self._rate_limiter.acquire()
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    # =====================
    # Search Methods
    # =====================
    
    async def search_decks(
        self,
        query: Optional[str] = None,
        format: Optional[str] = None,
        commander: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort_type: str = "views",
        sort_direction: str = "descending",
    ) -> Dict[str, Any]:
        """Search public decks."""
        params = {
            "pageNumber": page,
            "pageSize": page_size,
            "sortType": sort_type,
            "sortDirection": sort_direction,
        }
        
        if query:
            params["q"] = query
        if format:
            params["fmt"] = format
        if commander:
            params["commanderCardId"] = commander
        
        return await self.get("/v2/decks/search", params=params)
    
    # =====================
    # Helper Methods
    # =====================
    
    def parse_deck_response(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Moxfield deck response into CardForge format.
        
        Returns dict with:
        - name, format, description
        - mainboard, sideboard, commanders (lists of cards)
        - created_at, updated_at
        """
        result = {
            "moxfield_id": deck_data.get("publicId"),
            "name": deck_data.get("name"),
            "format": deck_data.get("format"),
            "description": deck_data.get("description"),
            "created_at": deck_data.get("createdAtUtc"),
            "updated_at": deck_data.get("lastUpdatedAtUtc"),
            "visibility": deck_data.get("visibility"),
            "mainboard": [],
            "sideboard": [],
            "commanders": [],
            "companions": [],
            "maybeboard": [],
        }
        
        # Parse boards
        boards = deck_data.get("boards", {})
        
        for board_name, board_data in boards.items():
            cards = board_data.get("cards", {})
            card_list = []
            
            for card_id, card_data in cards.items():
                card_info = card_data.get("card", {})
                card_list.append({
                    "scryfall_id": card_info.get("scryfall_id"),
                    "name": card_info.get("name"),
                    "set_code": card_info.get("set"),
                    "collector_number": card_info.get("cn"),
                    "quantity": card_data.get("quantity", 1),
                    "is_foil": card_data.get("isFoil", False),
                    "is_proxy": card_data.get("isProxy", False),
                    "category": card_data.get("boardType"),
                })
            
            if board_name == "mainboard":
                result["mainboard"] = card_list
            elif board_name == "sideboard":
                result["sideboard"] = card_list
            elif board_name == "commanders":
                result["commanders"] = card_list
            elif board_name == "companions":
                result["companions"] = card_list
            elif board_name == "maybeboard":
                result["maybeboard"] = card_list
        
        return result
    
    async def import_deck(self, deck_id: str) -> Dict[str, Any]:
        """Import a deck and parse it into CardForge format."""
        deck_data = await self.get_deck(deck_id)
        return self.parse_deck_response(deck_data)
    
    async def get_all_my_decks(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Get all of the authenticated user's decks."""
        all_decks = []
        page = 1
        
        while page <= max_pages:
            result = await self.get_my_decks(page=page, page_size=100)
            decks = result.get("data", [])
            all_decks.extend(decks)
            
            total_pages = result.get("totalPages", 1)
            if page >= total_pages:
                break
            
            page += 1
        
        return all_decks
