"""
CardForge Collection Service
Collection management and analytics
"""

from typing import Optional, List, Dict
from decimal import Decimal

from cardforge.repositories import (
    CollectionRepository, 
    CollectionCardRepository,
    CardRepository
)
from cardforge.models import Collection, CollectionCard, CollectionStats, OwnershipInfo


class CollectionService:
    """Service for collection operations."""
    
    def __init__(self):
        self.collection_repo = CollectionRepository()
        self.card_entry_repo = CollectionCardRepository()
        self.card_repo = CardRepository()
    
    async def get_or_create_default(self) -> Collection:
        """Get or create the default collection."""
        return await self.collection_repo.get_or_create_default()
    
    async def get_collection(self, collection_id: int) -> Optional[Collection]:
        """Get a collection by ID."""
        return await self.collection_repo.get(collection_id)
    
    async def get_stats(self, collection_id: int) -> Optional[CollectionStats]:
        """Get collection statistics."""
        return await self.collection_repo.get_stats(collection_id)
    
    async def add_card(
        self,
        card_name: str,
        quantity: int = 1,
        foil: str = "normal",
        condition: str = "NM",
        collection_id: Optional[int] = None,
        set_code: Optional[str] = None,
    ) -> Optional[CollectionCard]:
        """Add a card to collection by name."""
        # Get or create default collection
        if collection_id is None:
            collection = await self.get_or_create_default()
            collection_id = collection.id
        
        # Find card
        card = await self.card_repo.get_by_name(card_name, set_code)
        if not card:
            return None
        
        return await self.card_entry_repo.add_card(
            collection_id=collection_id,
            card_id=card.id,
            quantity=quantity,
            foil=foil,
            condition=condition,
        )
    
    async def remove_card(
        self,
        collection_card_id: int,
        quantity: int = 1,
    ) -> bool:
        """Remove cards from collection."""
        entry = await self.card_entry_repo.get(collection_card_id)
        if not entry:
            return False
        
        new_qty = entry.quantity - quantity
        if new_qty <= 0:
            return await self.card_entry_repo.delete(collection_card_id)
        
        entry.quantity = new_qty
        await self.card_entry_repo.update(entry)
        return True
    
    async def check_ownership(self, card_name: str) -> OwnershipInfo:
        """Check if and how many copies of a card are owned."""
        return await self.card_entry_repo.check_ownership(card_name)
    
    async def get_total_value(self, collection_id: Optional[int] = None) -> Decimal:
        """Get total collection value."""
        if collection_id is None:
            collection = await self.get_or_create_default()
            collection_id = collection.id
        
        return await self.card_entry_repo.get_total_value(collection_id)
    
    async def find_duplicates(
        self,
        min_copies: int = 5,
        min_value: Decimal = Decimal('0.50'),
    ) -> List[Dict]:
        """Find duplicate cards that could be sold."""
        return await self.card_entry_repo.find_duplicates(
            min_count=min_copies,
            min_value=min_value,
        )
    
    async def get_cards(
        self,
        collection_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CollectionCard]:
        """Get cards in collection with card data."""
        if collection_id is None:
            collection = await self.get_or_create_default()
            collection_id = collection.id
        
        return await self.card_entry_repo.get_with_card_data(
            collection_id, limit=limit, offset=offset
        )
