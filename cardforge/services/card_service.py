"""
CardForge Card Service
Card data management and Scryfall sync
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from cardforge.api import ScryfallClient
from cardforge.repositories import CardRepository, SetRepository
from cardforge.models import Card, SetInfo


class CardService:
    """Service for card data operations."""
    
    def __init__(self):
        self.card_repo = CardRepository()
        self.set_repo = SetRepository()
    
    async def search(
        self,
        query: Optional[str] = None,
        colors: Optional[List[str]] = None,
        set_code: Optional[str] = None,
        rarity: Optional[str] = None,
        type_filter: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        limit: int = 100,
    ) -> List[Card]:
        """Search cards with filters."""
        return await self.card_repo.search(
            query=query,
            colors=colors,
            set_code=set_code,
            rarity=rarity,
            type_filter=type_filter,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
        )
    
    async def get_by_name(self, name: str, set_code: Optional[str] = None) -> Optional[Card]:
        """Get card by name."""
        return await self.card_repo.get_by_name(name, set_code)
    
    async def get_by_scryfall_id(self, scryfall_id: str) -> Optional[Card]:
        """Get card by Scryfall ID."""
        return await self.card_repo.get_by_scryfall_id(scryfall_id)
    
    async def fetch_from_scryfall(self, name: str, set_code: Optional[str] = None) -> Optional[Card]:
        """Fetch card from Scryfall and save to database."""
        async with ScryfallClient() as client:
            try:
                data = await client.get_card_by_name(name, exact=True, set_code=set_code)
                card = Card.from_scryfall(data)
                
                # Ensure set exists before saving card
                if card.set_code:
                    await self._ensure_set_exists(card.set_code)
                
                return await self.card_repo.upsert(card)
            except Exception:
                return None
    
    async def _ensure_set_exists(self, set_code: str) -> None:
        """Ensure a set exists in the database."""
        existing = await self.set_repo.get_by_code(set_code)
        if not existing:
            # Create minimal set entry (can be synced later with full metadata)
            set_info = SetInfo(code=set_code, name=set_code.upper())
            await self.set_repo.upsert(set_info)
    
    async def sync_set(self, set_code: str) -> int:
        """Sync all cards from a set."""
        async with ScryfallClient() as client:
            cards_data = await client.search_all_pages(f"set:{set_code}")
            
            cards = [Card.from_scryfall(c) for c in cards_data]
            return await self.card_repo.bulk_upsert(cards)
    
    async def sync_sets_metadata(self) -> int:
        """Sync all set metadata from Scryfall."""
        async with ScryfallClient() as client:
            sets_data = await client.get_all_sets()
            
            count = 0
            for s in sets_data:
                set_info = SetInfo(
                    code=s['code'],
                    name=s['name'],
                    set_type=s.get('set_type'),
                    card_count=s.get('card_count', 0),
                    release_date=s.get('released_at'),
                    icon_svg_uri=s.get('icon_svg_uri'),
                    scryfall_id=s.get('id'),
                )
                await self.set_repo.upsert(set_info)
                count += 1
            
            return count
    
    async def get_random_card(self) -> Optional[Card]:
        """Get a random card."""
        cards = await self.card_repo.get_random(1)
        return cards[0] if cards else None
