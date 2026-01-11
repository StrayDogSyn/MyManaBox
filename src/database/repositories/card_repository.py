"""
Card Repository
===============

Data access layer for Card model.
Provides specialized queries for card search and filtering.
"""

from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.models import Card
from src.database.repositories import BaseRepository


class CardRepository(BaseRepository[Card]):
    """Repository for Card model with specialized queries."""
    
    def __init__(self):
        super().__init__(Card)
    
    # --- Synchronous Methods ---
    
    def get_by_scryfall_id(self, session: Session, scryfall_id: str) -> Optional[Card]:
        """Get card by Scryfall ID."""
        return session.query(Card).filter(Card.scryfall_id == scryfall_id).first()
    
    def get_by_name(self, session: Session, name: str) -> List[Card]:
        """Get all printings of a card by name."""
        return session.query(Card).filter(Card.name == name).all()
    
    def get_by_name_and_set(
        self,
        session: Session,
        name: str,
        set_code: str,
    ) -> Optional[Card]:
        """Get specific card printing."""
        return (
            session.query(Card)
            .filter(and_(Card.name == name, Card.set_code == set_code))
            .first()
        )
    
    def search_by_name(
        self,
        session: Session,
        query: str,
        limit: int = 50,
    ) -> List[Card]:
        """Search cards by name (partial match)."""
        pattern = f"%{query}%"
        return (
            session.query(Card)
            .filter(Card.name.ilike(pattern))
            .limit(limit)
            .all()
        )
    
    def search_full_text(
        self,
        session: Session,
        query: str,
        limit: int = 50,
    ) -> List[Card]:
        """
        Search cards using FTS5 full-text search.
        
        Searches across name, type_line, and oracle_text.
        """
        # FTS5 query
        sql = """
            SELECT c.* FROM cards c
            INNER JOIN cards_fts fts ON c.id = fts.card_id
            WHERE cards_fts MATCH :query
            ORDER BY rank
            LIMIT :limit
        """
        result = session.execute(sql, {"query": query, "limit": limit})
        card_ids = [row[0] for row in result]
        
        # Fetch full card objects
        return session.query(Card).filter(Card.id.in_(card_ids)).all()
    
    def filter_by_colors(
        self,
        session: Session,
        colors: List[str],
        exact: bool = False,
    ) -> List[Card]:
        """
        Filter cards by color identity.
        
        Args:
            colors: List of color codes (W, U, B, R, G)
            exact: If True, match exact colors; if False, match any
        """
        color_str = ",".join(sorted(colors))
        
        if exact:
            return session.query(Card).filter(Card.colors == color_str).all()
        else:
            # Match any of the colors
            conditions = [Card.colors.like(f"%{c}%") for c in colors]
            return session.query(Card).filter(or_(*conditions)).all()
    
    def filter_by_type(self, session: Session, card_type: str) -> List[Card]:
        """Filter cards by type (e.g., 'Creature', 'Instant')."""
        return session.query(Card).filter(Card.type_line.like(f"%{card_type}%")).all()
    
    def filter_by_rarity(self, session: Session, rarity: str) -> List[Card]:
        """Filter cards by rarity."""
        return session.query(Card).filter(Card.rarity == rarity).all()
    
    def get_commanders(self, session: Session) -> List[Card]:
        """Get all cards that can be commanders."""
        return session.query(Card).filter(Card.is_commander == True).all()
    
    def get_reserved_list(self, session: Session) -> List[Card]:
        """Get all cards on the Reserved List."""
        return session.query(Card).filter(Card.is_reserved_list == True).all()
    
    def get_by_set(self, session: Session, set_code: str) -> List[Card]:
        """Get all cards from a specific set."""
        return session.query(Card).filter(Card.set_code == set_code).all()
    
    # --- Asynchronous Methods ---
    
    async def get_by_scryfall_id_async(
        self,
        session: AsyncSession,
        scryfall_id: str,
    ) -> Optional[Card]:
        """Get card by Scryfall ID (async)."""
        result = await session.execute(
            select(Card).where(Card.scryfall_id == scryfall_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name_async(self, session: AsyncSession, name: str) -> List[Card]:
        """Get all printings of a card by name (async)."""
        result = await session.execute(select(Card).where(Card.name == name))
        return list(result.scalars().all())
    
    async def get_by_name_and_set_async(
        self,
        session: AsyncSession,
        name: str,
        set_code: str,
    ) -> Optional[Card]:
        """Get specific card printing (async)."""
        result = await session.execute(
            select(Card).where(and_(Card.name == name, Card.set_code == set_code))
        )
        return result.scalar_one_or_none()
    
    async def search_by_name_async(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 50,
    ) -> List[Card]:
        """Search cards by name (async, partial match)."""
        pattern = f"%{query}%"
        result = await session.execute(
            select(Card).where(Card.name.ilike(pattern)).limit(limit)
        )
        return list(result.scalars().all())
    
    async def filter_by_colors_async(
        self,
        session: AsyncSession,
        colors: List[str],
        exact: bool = False,
    ) -> List[Card]:
        """Filter cards by color identity (async)."""
        color_str = ",".join(sorted(colors))
        
        if exact:
            result = await session.execute(
                select(Card).where(Card.colors == color_str)
            )
        else:
            conditions = [Card.colors.like(f"%{c}%") for c in colors]
            result = await session.execute(select(Card).where(or_(*conditions)))
        
        return list(result.scalars().all())
    
    async def filter_by_type_async(
        self,
        session: AsyncSession,
        card_type: str,
    ) -> List[Card]:
        """Filter cards by type (async)."""
        result = await session.execute(
            select(Card).where(Card.type_line.like(f"%{card_type}%"))
        )
        return list(result.scalars().all())
    
    async def get_commanders_async(self, session: AsyncSession) -> List[Card]:
        """Get all cards that can be commanders (async)."""
        result = await session.execute(
            select(Card).where(Card.is_commander == True)
        )
        return list(result.scalars().all())
