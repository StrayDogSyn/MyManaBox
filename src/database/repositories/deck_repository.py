"""
Deck Repository
===============

Data access layer for Deck and DeckCard models.
Provides queries for deck management and analysis.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from src.database.models import Card, Deck, DeckCard
from src.database.repositories import BaseRepository


class DeckRepository(BaseRepository[Deck]):
    """Repository for Deck model with deck queries."""
    
    def __init__(self):
        super().__init__(Deck)
    
    # --- Synchronous Methods ---
    
    def get_with_commander(self, session: Session, id: int) -> Optional[Deck]:
        """Get deck with commander data eagerly loaded."""
        return (
            session.query(Deck)
            .options(
                joinedload(Deck.commander),
                joinedload(Deck.partner_commander),
            )
            .filter(Deck.id == id)
            .first()
        )
    
    def get_with_cards(self, session: Session, id: int) -> Optional[Deck]:
        """Get deck with all cards eagerly loaded."""
        return (
            session.query(Deck)
            .options(
                joinedload(Deck.deck_cards).joinedload(DeckCard.card),
                joinedload(Deck.commander),
            )
            .filter(Deck.id == id)
            .first()
        )
    
    def get_by_format(self, session: Session, format: str) -> List[Deck]:
        """Get all decks for a specific format."""
        return session.query(Deck).filter(Deck.format == format).all()
    
    def get_active_decks(self, session: Session) -> List[Deck]:
        """Get all active decks."""
        return session.query(Deck).filter(Deck.is_active == True).all()
    
    def get_by_commander(self, session: Session, card_id: int) -> List[Deck]:
        """Get all decks with a specific commander."""
        return (
            session.query(Deck)
            .filter(
                (Deck.commander_id == card_id) | 
                (Deck.partner_commander_id == card_id)
            )
            .all()
        )
    
    def search_by_name(self, session: Session, query: str) -> List[Deck]:
        """Search decks by name (partial match)."""
        pattern = f"%{query}%"
        return session.query(Deck).filter(Deck.name.ilike(pattern)).all()
    
    def update_deck_stats(self, session: Session, deck_id: int) -> Optional[Deck]:
        """Recalculate and update deck statistics."""
        deck = self.get_by_id(session, deck_id)
        if not deck:
            return None
        
        # Count total cards (mainboard only)
        total_cards = (
            session.query(func.sum(DeckCard.quantity))
            .filter(
                and_(
                    DeckCard.deck_id == deck_id,
                    DeckCard.category == "mainboard",
                )
            )
            .scalar() or 0
        )
        
        # Calculate estimated value
        estimated_value_result = (
            session.query(
                func.sum(
                    DeckCard.quantity * 
                    func.coalesce(Card.price_usd, 0)
                )
            )
            .join(Card, DeckCard.card_id == Card.id)
            .filter(DeckCard.deck_id == deck_id)
            .scalar()
        )
        estimated_value = Decimal(str(estimated_value_result or 0))
        
        # Update deck
        deck.total_cards = total_cards
        deck.estimated_value = estimated_value
        session.flush()
        
        return deck
    
    # --- Asynchronous Methods ---
    
    async def get_with_commander_async(
        self,
        session: AsyncSession,
        id: int,
    ) -> Optional[Deck]:
        """Get deck with commander data (async)."""
        result = await session.execute(
            select(Deck)
            .options(
                joinedload(Deck.commander),
                joinedload(Deck.partner_commander),
            )
            .where(Deck.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_cards_async(
        self,
        session: AsyncSession,
        id: int,
    ) -> Optional[Deck]:
        """Get deck with all cards (async)."""
        result = await session.execute(
            select(Deck)
            .options(
                joinedload(Deck.deck_cards).joinedload(DeckCard.card),
                joinedload(Deck.commander),
            )
            .where(Deck.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_decks_async(self, session: AsyncSession) -> List[Deck]:
        """Get all active decks (async)."""
        result = await session.execute(
            select(Deck).where(Deck.is_active == True)
        )
        return list(result.scalars().all())


class DeckCardRepository(BaseRepository[DeckCard]):
    """Repository for DeckCard model with deck card queries."""
    
    def __init__(self):
        super().__init__(DeckCard)
    
    # --- Synchronous Methods ---
    
    def get_by_deck(self, session: Session, deck_id: int) -> List[DeckCard]:
        """Get all cards in a deck."""
        return (
            session.query(DeckCard)
            .options(joinedload(DeckCard.card))
            .filter(DeckCard.deck_id == deck_id)
            .all()
        )
    
    def get_by_category(
        self,
        session: Session,
        deck_id: int,
        category: str,
    ) -> List[DeckCard]:
        """Get cards in a specific deck category (mainboard, sideboard, etc.)."""
        return (
            session.query(DeckCard)
            .options(joinedload(DeckCard.card))
            .filter(
                and_(
                    DeckCard.deck_id == deck_id,
                    DeckCard.category == category,
                )
            )
            .all()
        )
    
    def get_mainboard(self, session: Session, deck_id: int) -> List[DeckCard]:
        """Get mainboard cards."""
        return self.get_by_category(session, deck_id, "mainboard")
    
    def get_sideboard(self, session: Session, deck_id: int) -> List[DeckCard]:
        """Get sideboard cards."""
        return self.get_by_category(session, deck_id, "sideboard")
    
    def get_maybeboard(self, session: Session, deck_id: int) -> List[DeckCard]:
        """Get maybeboard cards."""
        return self.get_by_category(session, deck_id, "maybeboard")
    
    def find_card_in_deck(
        self,
        session: Session,
        deck_id: int,
        card_id: int,
        category: str = "mainboard",
    ) -> Optional[DeckCard]:
        """Check if a card is in a deck."""
        return (
            session.query(DeckCard)
            .filter(
                and_(
                    DeckCard.deck_id == deck_id,
                    DeckCard.card_id == card_id,
                    DeckCard.category == category,
                )
            )
            .first()
        )
    
    def add_card_to_deck(
        self,
        session: Session,
        deck_id: int,
        card_id: int,
        quantity: int = 1,
        category: str = "mainboard",
        **kwargs,
    ) -> DeckCard:
        """Add a card to a deck (or update quantity if already exists)."""
        existing = self.find_card_in_deck(session, deck_id, card_id, category)
        
        if existing:
            existing.quantity += quantity
            session.flush()
            return existing
        else:
            return self.create(
                session,
                deck_id=deck_id,
                card_id=card_id,
                quantity=quantity,
                category=category,
                **kwargs,
            )
    
    def remove_card_from_deck(
        self,
        session: Session,
        deck_id: int,
        card_id: int,
        quantity: int = 1,
        category: str = "mainboard",
    ) -> bool:
        """Remove a card from a deck (or reduce quantity)."""
        deck_card = self.find_card_in_deck(session, deck_id, card_id, category)
        
        if not deck_card:
            return False
        
        if deck_card.quantity <= quantity:
            session.delete(deck_card)
        else:
            deck_card.quantity -= quantity
        
        session.flush()
        return True
    
    # --- Asynchronous Methods ---
    
    async def get_by_deck_async(
        self,
        session: AsyncSession,
        deck_id: int,
    ) -> List[DeckCard]:
        """Get all cards in a deck (async)."""
        result = await session.execute(
            select(DeckCard)
            .options(joinedload(DeckCard.card))
            .where(DeckCard.deck_id == deck_id)
        )
        return list(result.scalars().all())
    
    async def get_by_category_async(
        self,
        session: AsyncSession,
        deck_id: int,
        category: str,
    ) -> List[DeckCard]:
        """Get cards by category (async)."""
        result = await session.execute(
            select(DeckCard)
            .options(joinedload(DeckCard.card))
            .where(
                and_(
                    DeckCard.deck_id == deck_id,
                    DeckCard.category == category,
                )
            )
        )
        return list(result.scalars().all())
