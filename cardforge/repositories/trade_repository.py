"""
CardForge Trade Repository
Buy list and sell list data access
"""

from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

from cardforge.models import (
    BuyListItem, SellListItem, 
    BuyListSummary, SellListSummary
)
from cardforge.database import get_connection
from .base_repository import BaseRepository


class BuyListRepository(BaseRepository[BuyListItem]):
    """Repository for buy list management."""
    
    table_name = "buy_list"
    model_class = BuyListItem
    
    async def get_wanted(self) -> List[BuyListItem]:
        """Get all wanted items."""
        return await self.find_by(status='wanted')
    
    async def get_by_deck(self, deck_id: int) -> List[BuyListItem]:
        """Get buy list items for a specific deck."""
        return await self.find_by(deck_id=deck_id)
    
    async def get_by_priority(self, priority: int) -> List[BuyListItem]:
        """Get items by priority level."""
        return await self.find_by(priority=priority)
    
    async def get_with_details(self, status: str = 'wanted') -> List[BuyListItem]:
        """Get buy list with card details."""
        sql = """
            SELECT 
                bl.*,
                c.name as card_name,
                c.set_code,
                c.scryfall_id,
                COALESCE(json_extract(c.prices_json, '$.usd'), 0) as current_price,
                d.name as deck_name,
                dc.category
            FROM buy_list bl
            JOIN cards c ON bl.card_id = c.id
            LEFT JOIN decks d ON bl.deck_id = d.id
            LEFT JOIN deck_cards dc ON dc.deck_id = bl.deck_id AND dc.card_id = bl.card_id
            WHERE bl.status = ?
            ORDER BY bl.priority, bl.best_price
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (status,))
            rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                item = BuyListItem.from_row(row)
                item.card_name = row['card_name']  # Attach card name for display
                item.deck_name = row['deck_name']
                item.category = row['category']
                results.append(item)
            
            return results
    
    async def add_item(
        self,
        card_id: int,
        deck_id: Optional[int] = None,
        priority: int = 3,
        quantity_needed: int = 1,
        max_price: Optional[Decimal] = None,
    ) -> BuyListItem:
        """Add item to buy list."""
        # Check if already exists
        existing = await self.find_one_by(
            card_id=card_id,
            deck_id=deck_id,
            status='wanted'
        )
        
        if existing:
            existing.quantity_needed += quantity_needed
            if max_price and (not existing.max_price or max_price > existing.max_price):
                existing.max_price = max_price
            return await self.update(existing)
        
        item = BuyListItem(
            card_id=card_id,
            deck_id=deck_id,
            priority=priority,
            quantity_needed=quantity_needed,
            max_price=max_price,
        )
        return await self.create(item)
    
    async def mark_ordered(
        self, 
        item_id: int,
        source: str,
        price: Decimal
    ) -> Optional[BuyListItem]:
        """Mark item as ordered."""
        item = await self.get(item_id)
        if item:
            item.status = 'ordered'
            item.purchased_source = source
            item.purchased_price = price
            return await self.update(item)
        return None
    
    async def mark_received(self, item_id: int) -> Optional[BuyListItem]:
        """Mark item as received."""
        item = await self.get(item_id)
        if item:
            item.status = 'received'
            item.purchased_at = datetime.now()
            return await self.update(item)
        return None
    
    async def get_summary(self) -> BuyListSummary:
        """Get buy list summary statistics."""
        async with get_connection() as conn:
            # Total counts
            cursor = await conn.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    SUM(quantity_needed) as total_cards,
                    SUM(best_price * quantity_needed) as total_cost
                FROM buy_list
                WHERE status = 'wanted'
            """)
            totals = await cursor.fetchone()
            
            # By priority
            cursor = await conn.execute("""
                SELECT priority, COUNT(*) as count
                FROM buy_list WHERE status = 'wanted'
                GROUP BY priority
            """)
            priority_rows = await cursor.fetchall()
            by_priority = {row['priority']: row['count'] for row in priority_rows}
            
            # By status
            cursor = await conn.execute("""
                SELECT status, COUNT(*) as count
                FROM buy_list
                GROUP BY status
            """)
            status_rows = await cursor.fetchall()
            by_status = {row['status']: row['count'] for row in status_rows}
            
            # By deck
            cursor = await conn.execute("""
                SELECT d.name, COUNT(*) as count
                FROM buy_list bl
                JOIN decks d ON bl.deck_id = d.id
                WHERE bl.status = 'wanted'
                GROUP BY d.name
            """)
            deck_rows = await cursor.fetchall()
            by_deck = {row['name']: row['count'] for row in deck_rows}
            
            # Budget analysis
            cursor = await conn.execute("""
                SELECT 
                    SUM(CASE WHEN best_price <= max_price OR max_price IS NULL THEN 1 ELSE 0 END) as within,
                    SUM(CASE WHEN best_price > max_price AND max_price IS NOT NULL THEN 1 ELSE 0 END) as over
                FROM buy_list
                WHERE status = 'wanted'
            """)
            budget = await cursor.fetchone()
        
        return BuyListSummary(
            total_items=totals['total_items'] or 0,
            total_cards=totals['total_cards'] or 0,
            total_cost=Decimal(str(totals['total_cost'] or 0)),
            by_priority=by_priority,
            by_status=by_status,
            by_deck=by_deck,
            within_budget_count=budget['within'] or 0,
            over_budget_count=budget['over'] or 0,
        )


class SellListRepository(BaseRepository[SellListItem]):
    """Repository for sell list management."""
    
    table_name = "sell_list"
    model_class = SellListItem
    
    async def get_considering(self) -> List[SellListItem]:
        """Get items being considered for sale."""
        return await self.find_by(status='considering')
    
    async def get_listed(self) -> List[SellListItem]:
        """Get items currently listed."""
        return await self.find_by(status='listed')
    
    async def get_with_details(self, status: str = 'considering') -> List[SellListItem]:
        """Get sell list with card details."""
        sql = """
            SELECT 
                sl.*,
                c.name as card_name,
                c.set_code,
                COALESCE(json_extract(c.prices_json, '$.usd'), 0) as market_price,
                cc.foil,
                cc.condition
            FROM sell_list sl
            JOIN collection_cards cc ON sl.collection_card_id = cc.id
            JOIN cards c ON cc.card_id = c.id
            WHERE sl.status = ?
            ORDER BY sl.best_tcgplayer_price DESC
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (status,))
            rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                item = SellListItem.from_row(row)
                item.card_name = row['card_name']
                item.set_code = row['set_code']
                item.current_market_price = Decimal(str(row['market_price']))
                results.append(item)
            
            return results
    
    async def add_item(
        self,
        collection_card_id: int,
        quantity_to_sell: int = 1,
        reason: str = 'duplicate',
        min_price: Optional[Decimal] = None,
    ) -> SellListItem:
        """Add item to sell list."""
        existing = await self.find_one_by(
            collection_card_id=collection_card_id,
            status='considering'
        )
        
        if existing:
            existing.quantity_to_sell += quantity_to_sell
            return await self.update(existing)
        
        item = SellListItem(
            collection_card_id=collection_card_id,
            quantity_to_sell=quantity_to_sell,
            reason=reason,
            min_price=min_price,
        )
        return await self.create(item)
    
    async def mark_listed(
        self,
        item_id: int,
        platform: str,
        price: Decimal,
    ) -> Optional[SellListItem]:
        """Mark item as listed."""
        item = await self.get(item_id)
        if item:
            item.status = 'listed'
            item.listed_platform = platform
            item.listed_price = price
            item.listed_at = datetime.now()
            return await self.update(item)
        return None
    
    async def mark_sold(
        self,
        item_id: int,
        price: Decimal,
        buyer: Optional[str] = None,
    ) -> Optional[SellListItem]:
        """Mark item as sold."""
        item = await self.get(item_id)
        if item:
            item.status = 'sold'
            item.sold_price = price
            item.sold_to = buyer
            item.sold_at = datetime.now()
            return await self.update(item)
        return None
    
    async def get_summary(self) -> SellListSummary:
        """Get sell list summary statistics."""
        async with get_connection() as conn:
            cursor = await conn.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    SUM(quantity_to_sell) as total_cards,
                    SUM(COALESCE(best_tcgplayer_price, best_buylist_price, 0) * quantity_to_sell) as potential_value
                FROM sell_list
                WHERE status IN ('considering', 'listed')
            """)
            totals = await cursor.fetchone()
            
            cursor = await conn.execute("""
                SELECT reason, COUNT(*) as count
                FROM sell_list
                WHERE status IN ('considering', 'listed')
                GROUP BY reason
            """)
            reason_rows = await cursor.fetchall()
            by_reason = {row['reason']: row['count'] for row in reason_rows}
            
            cursor = await conn.execute("""
                SELECT status, COUNT(*) as count
                FROM sell_list
                GROUP BY status
            """)
            status_rows = await cursor.fetchall()
            by_status = {row['status']: row['count'] for row in status_rows}
        
        return SellListSummary(
            total_items=totals['total_items'] or 0,
            total_cards=totals['total_cards'] or 0,
            potential_value=Decimal(str(totals['potential_value'] or 0)),
            by_reason=by_reason,
            by_status=by_status,
        )
