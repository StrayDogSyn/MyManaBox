"""
CardForge Trade Service
Buy list and sell list management
"""

from typing import Optional, List, Dict
from decimal import Decimal

from cardforge.repositories import (
    BuyListRepository, 
    SellListRepository,
    CollectionCardRepository,
    CardRepository,
    DeckCardRepository,
)
from cardforge.models import BuyListItem, SellListItem, BuyListSummary, SellListSummary


class TradeService:
    """Service for buy/sell list operations."""
    
    def __init__(self):
        self.buy_repo = BuyListRepository()
        self.sell_repo = SellListRepository()
        self.collection_repo = CollectionCardRepository()
        self.card_repo = CardRepository()
        self.deck_card_repo = DeckCardRepository()
    
    # =====================
    # Buy List Operations
    # =====================
    
    async def add_to_buy_list(
        self,
        card_name: str,
        quantity: int = 1,
        priority: int = 3,
        deck_id: Optional[int] = None,
        max_price: Optional[Decimal] = None,
    ) -> Optional[BuyListItem]:
        """Add card to buy list."""
        card = await self.card_repo.get_by_name(card_name)
        if not card:
            return None
        
        return await self.buy_repo.add_item(
            card_id=card.id,
            deck_id=deck_id,
            priority=priority,
            quantity_needed=quantity,
            max_price=max_price,
        )
    
    async def get_buy_list(self) -> List[BuyListItem]:
        """Get all wanted items."""
        return await self.buy_repo.get_with_details()
    
    async def get_buy_list_summary(self) -> BuyListSummary:
        """Get buy list statistics."""
        return await self.buy_repo.get_summary()
    
    async def mark_ordered(
        self,
        item_id: int,
        source: str,
        price: Decimal,
    ) -> Optional[BuyListItem]:
        """Mark item as ordered."""
        return await self.buy_repo.mark_ordered(item_id, source, price)
    
    async def mark_received(self, item_id: int) -> Optional[BuyListItem]:
        """Mark item as received and add to collection."""
        item = await self.buy_repo.mark_received(item_id)
        if item:
            # Add to collection
            await self.collection_repo.add_card(
                collection_id=1,  # Default collection
                card_id=item.card_id,
                quantity=item.quantity_needed,
                purchase_price=item.purchased_price,
            )
        return item
    
    async def generate_buy_list_from_decks(self) -> int:
        """Generate buy list from all deck missing cards."""
        from cardforge.repositories import DeckRepository
        deck_repo = DeckRepository()
        
        decks = await deck_repo.get_active_decks()
        count = 0
        
        for deck in decks:
            missing = await self.deck_card_repo.get_missing_cards(deck.id)
            for card in missing:
                await self.buy_repo.add_item(
                    card_id=card.card_id if hasattr(card, 'card_id') else None,
                    deck_id=deck.id,
                    quantity_needed=card.quantity_needed,
                    priority=2,
                )
                count += 1
        
        return count
    
    # =====================
    # Sell List Operations
    # =====================
    
    async def add_to_sell_list(
        self,
        collection_card_id: int,
        quantity: int = 1,
        reason: str = 'duplicate',
        min_price: Optional[Decimal] = None,
    ) -> SellListItem:
        """Add collection card to sell list."""
        return await self.sell_repo.add_item(
            collection_card_id=collection_card_id,
            quantity_to_sell=quantity,
            reason=reason,
            min_price=min_price,
        )
    
    async def get_sell_list(self) -> List[SellListItem]:
        """Get items being considered for sale."""
        return await self.sell_repo.get_with_details()
    
    async def get_sell_list_summary(self) -> SellListSummary:
        """Get sell list statistics."""
        return await self.sell_repo.get_summary()
    
    async def generate_sell_list_from_duplicates(
        self,
        keep_count: int = 4,
        min_value: Decimal = Decimal('0.50'),
    ) -> int:
        """Auto-generate sell list from duplicate cards."""
        duplicates = await self.collection_repo.find_duplicates(
            min_count=keep_count + 1,
            min_value=min_value,
        )
        
        count = 0
        for dup in duplicates:
            excess = dup['total_copies'] - keep_count
            if excess > 0:
                # Find collection entries to sell
                entries = await self.collection_repo.find_by(
                    oracle_id=dup['oracle_id']
                )
                
                remaining = excess
                for entry in entries:
                    if remaining <= 0:
                        break
                    sell_qty = min(entry.quantity, remaining)
                    await self.sell_repo.add_item(
                        collection_card_id=entry.id,
                        quantity_to_sell=sell_qty,
                        reason='duplicate',
                    )
                    remaining -= sell_qty
                    count += 1
        
        return count
    
    async def mark_sold(
        self,
        item_id: int,
        price: Decimal,
        buyer: Optional[str] = None,
    ) -> Optional[SellListItem]:
        """Mark item as sold and remove from collection."""
        item = await self.sell_repo.mark_sold(item_id, price, buyer)
        if item:
            # Reduce collection quantity
            await self.collection_repo.update_quantity(
                item.collection_card_id,
                -item.quantity_to_sell
            )
        return item
