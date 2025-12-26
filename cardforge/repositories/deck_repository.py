"""
CardForge Deck Repository
Deck and DeckCard data access
"""

from typing import Optional, List, Dict
from decimal import Decimal

from cardforge.models import Deck, DeckCard, DeckAnalysis, MissingCard
from cardforge.database import get_connection
from .base_repository import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    """Repository for deck management."""
    
    table_name = "decks"
    model_class = Deck
    
    async def get_by_name(self, name: str) -> Optional[Deck]:
        """Get deck by name."""
        return await self.find_one_by(name=name)
    
    async def get_by_moxfield_id(self, moxfield_id: str) -> Optional[Deck]:
        """Get deck by Moxfield ID."""
        return await self.find_one_by(moxfield_id=moxfield_id)
    
    async def get_active_decks(self) -> List[Deck]:
        """Get all active decks."""
        return await self.find_by(is_active=True)
    
    async def get_by_format(self, format: str) -> List[Deck]:
        """Get decks by format."""
        return await self.find_by(format=format.lower())
    
    async def get_with_cards(self, deck_id: int) -> Optional[Deck]:
        """Get deck with cards loaded."""
        deck = await self.get(deck_id)
        if not deck:
            return None
        
        card_repo = DeckCardRepository()
        deck.cards = await card_repo.get_with_card_data(deck_id)
        
        # Load commander if set
        if deck.commander_id:
            from cardforge.repositories import CardRepository
            card_repo_full = CardRepository()
            deck.commander = await card_repo_full.get(deck.commander_id)
        
        if deck.partner_id:
            from cardforge.repositories import CardRepository
            card_repo_full = CardRepository()
            deck.partner = await card_repo_full.get(deck.partner_id)
        
        return deck
    
    async def get_completion_status(self, deck_id: int) -> Dict:
        """Get deck completion status from view."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM v_deck_completion WHERE deck_id = ?",
                (deck_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return {}
            
            return dict(row)
    
    async def update_value(self, deck_id: int) -> Decimal:
        """Calculate and update deck's current value."""
        sql = """
            SELECT SUM(
                dc.quantity * COALESCE(json_extract(c.prices_json, '$.usd'), 0)
            ) as total
            FROM deck_cards dc
            JOIN cards c ON dc.card_id = c.id
            WHERE dc.deck_id = ? AND dc.is_maybeboard = FALSE
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (deck_id,))
            row = await cursor.fetchone()
            value = Decimal(str(row[0] or 0))
            
            await conn.execute(
                "UPDATE decks SET current_value = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (float(value), deck_id)
            )
            await conn.commit()
        
        return value


class DeckCardRepository(BaseRepository[DeckCard]):
    """Repository for deck card entries."""
    
    table_name = "deck_cards"
    model_class = DeckCard
    
    async def get_by_deck(self, deck_id: int) -> List[DeckCard]:
        """Get all cards in a deck."""
        return await self.find_by(deck_id=deck_id)
    
    async def get_with_card_data(self, deck_id: int) -> List[DeckCard]:
        """Get deck cards with full card data."""
        sql = """
            SELECT 
                dc.*,
                c.name as card_name,
                c.set_code,
                c.scryfall_id,
                c.oracle_id,
                c.rarity,
                c.type_line,
                c.mana_cost,
                c.cmc,
                c.colors,
                c.oracle_text,
                c.image_uris,
                c.prices_json
            FROM deck_cards dc
            JOIN cards c ON dc.card_id = c.id
            WHERE dc.deck_id = ?
            ORDER BY dc.is_commander DESC, dc.category, c.name
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (deck_id,))
            rows = await cursor.fetchall()
            
            from cardforge.models import Card
            
            results = []
            for row in rows:
                dc = DeckCard.from_row(row)
                dc.card = Card(
                    id=row['card_id'],
                    name=row['card_name'],
                    set_code=row['set_code'],
                    scryfall_id=row['scryfall_id'],
                    oracle_id=row['oracle_id'],
                    rarity=row['rarity'],
                    type_line=row['type_line'],
                    mana_cost=row['mana_cost'],
                    cmc=row['cmc'],
                    colors=row['colors'],
                    oracle_text=row['oracle_text'],
                    image_uris=row['image_uris'],
                    prices_json=row['prices_json'],
                )
                results.append(dc)
            
            return results
    
    async def add_card(
        self,
        deck_id: int,
        card_id: int,
        quantity: int = 1,
        is_commander: bool = False,
        is_sideboard: bool = False,
        is_maybeboard: bool = False,
        category: Optional[str] = None,
    ) -> DeckCard:
        """Add card to deck (or update if exists)."""
        existing = await self.find_one_by(
            deck_id=deck_id,
            card_id=card_id,
            is_sideboard=is_sideboard,
            is_maybeboard=is_maybeboard
        )
        
        if existing:
            existing.quantity += quantity
            if category:
                existing.category = category
            return await self.update(existing)
        
        dc = DeckCard(
            deck_id=deck_id,
            card_id=card_id,
            quantity=quantity,
            is_commander=is_commander,
            is_sideboard=is_sideboard,
            is_maybeboard=is_maybeboard,
            category=category,
        )
        return await self.create(dc)
    
    async def remove_card(self, deck_id: int, card_id: int) -> bool:
        """Remove card from deck."""
        existing = await self.find_one_by(deck_id=deck_id, card_id=card_id)
        if existing:
            return await self.delete(existing.id)
        return False
    
    async def get_card_usage(self, card_id: int) -> List[Dict]:
        """Get all decks that use a specific card."""
        sql = """
            SELECT 
                dc.deck_id,
                d.name as deck_name,
                d.format,
                dc.quantity,
                dc.is_commander,
                dc.category
            FROM deck_cards dc
            JOIN decks d ON dc.deck_id = d.id
            WHERE dc.card_id = ?
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (card_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_missing_cards(self, deck_id: int) -> List[MissingCard]:
        """Get cards in deck that aren't owned (or insufficient quantity)."""
        sql = """
            SELECT 
                c.name as card_name,
                c.scryfall_id,
                c.set_code,
                dc.quantity as needed,
                dc.owned_quantity as owned,
                dc.category,
                COALESCE(json_extract(c.prices_json, '$.usd'), 0) as price
            FROM deck_cards dc
            JOIN cards c ON dc.card_id = c.id
            WHERE dc.deck_id = ? 
            AND dc.is_maybeboard = FALSE
            AND dc.owned_quantity < dc.quantity
            ORDER BY dc.category, c.name
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (deck_id,))
            rows = await cursor.fetchall()
            
            return [
                MissingCard(
                    card_name=row['card_name'],
                    scryfall_id=row['scryfall_id'],
                    set_code=row['set_code'],
                    quantity_needed=row['needed'] - row['owned'],
                    category=row['category'],
                    current_price=Decimal(str(row['price'])) if row['price'] else None,
                )
                for row in rows
            ]
    
    async def update_owned_quantities(self, deck_id: int) -> int:
        """Update owned_quantity for all cards in deck based on collection."""
        sql = """
            UPDATE deck_cards
            SET owned_quantity = (
                SELECT COALESCE(SUM(cc.quantity), 0)
                FROM collection_cards cc
                WHERE cc.card_id = deck_cards.card_id
            )
            WHERE deck_id = ?
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (deck_id,))
            await conn.commit()
            return cursor.rowcount
    
    async def get_by_category(self, deck_id: int, category: str) -> List[DeckCard]:
        """Get cards in a deck by category."""
        return await self.find_by(deck_id=deck_id, category=category)
