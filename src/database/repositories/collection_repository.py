"""
Collection Repository
=====================

Data access layer for CollectionItem model.
Provides queries for collection management and analysis.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from src.database.models import Card, CollectionItem
from src.database.repositories import BaseRepository


class CollectionRepository(BaseRepository[CollectionItem]):
    """Repository for CollectionItem model with collection queries."""
    
    def __init__(self):
        super().__init__(CollectionItem)
    
    # --- Synchronous Methods ---
    
    def get_with_card(self, session: Session, id: int) -> Optional[CollectionItem]:
        """Get collection item with card data eagerly loaded."""
        return (
            session.query(CollectionItem)
            .options(joinedload(CollectionItem.card))
            .filter(CollectionItem.id == id)
            .first()
        )
    
    def get_all_with_cards(
        self,
        session: Session,
        limit: Optional[int] = None,
    ) -> List[CollectionItem]:
        """Get all collection items with card data."""
        query = (
            session.query(CollectionItem)
            .options(joinedload(CollectionItem.card))
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_by_card_id(self, session: Session, card_id: int) -> List[CollectionItem]:
        """Get all collection items for a specific card."""
        return (
            session.query(CollectionItem)
            .filter(CollectionItem.card_id == card_id)
            .all()
        )
    
    def get_total_quantity(self, session: Session, card_id: int) -> int:
        """Get total quantity of a card in collection (all copies)."""
        result = (
            session.query(func.sum(CollectionItem.quantity))
            .filter(CollectionItem.card_id == card_id)
            .scalar()
        )
        return result or 0
    
    def get_foil_quantity(self, session: Session, card_id: int) -> int:
        """Get total foil quantity of a card."""
        result = (
            session.query(func.sum(CollectionItem.quantity))
            .filter(
                and_(
                    CollectionItem.card_id == card_id,
                    CollectionItem.is_foil == True,
                )
            )
            .scalar()
        )
        return result or 0
    
    def get_by_condition(
        self,
        session: Session,
        condition: str,
    ) -> List[CollectionItem]:
        """Get all collection items by condition."""
        return (
            session.query(CollectionItem)
            .options(joinedload(CollectionItem.card))
            .filter(CollectionItem.condition == condition)
            .all()
        )
    
    def get_by_location(
        self,
        session: Session,
        location: str,
    ) -> List[CollectionItem]:
        """Get all collection items at a specific location."""
        return (
            session.query(CollectionItem)
            .options(joinedload(CollectionItem.card))
            .filter(CollectionItem.location == location)
            .all()
        )
    
    def get_collection_value(self, session: Session) -> Decimal:
        """Calculate total collection value based on current card prices."""
        result = (
            session.query(
                func.sum(
                    CollectionItem.quantity * 
                    func.coalesce(Card.price_usd, 0)
                )
            )
            .join(Card, CollectionItem.card_id == Card.id)
            .scalar()
        )
        return Decimal(str(result or 0))
    
    def get_foil_collection_value(self, session: Session) -> Decimal:
        """Calculate total foil collection value."""
        result = (
            session.query(
                func.sum(
                    CollectionItem.quantity * 
                    func.coalesce(Card.price_usd_foil, 0)
                )
            )
            .join(Card, CollectionItem.card_id == Card.id)
            .filter(CollectionItem.is_foil == True)
            .scalar()
        )
        return Decimal(str(result or 0))
    
    def get_collection_stats(self, session: Session) -> dict:
        """Get collection statistics."""
        total_cards = (
            session.query(func.sum(CollectionItem.quantity))
            .scalar() or 0
        )
        
        unique_cards = (
            session.query(func.count(func.distinct(CollectionItem.card_id)))
            .scalar() or 0
        )
        
        total_value = self.get_collection_value(session)
        foil_value = self.get_foil_collection_value(session)
        
        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "total_value": total_value,
            "foil_value": foil_value,
            "non_foil_value": total_value - foil_value,
        }
    
    def find_duplicates(self, session: Session, min_quantity: int = 2) -> List[dict]:
        """Find cards with multiple copies (potential duplicates)."""
        results = (
            session.query(
                Card.name,
                Card.set_code,
                func.sum(CollectionItem.quantity).label("total_quantity"),
            )
            .join(Card, CollectionItem.card_id == Card.id)
            .group_by(Card.name, Card.set_code)
            .having(func.sum(CollectionItem.quantity) >= min_quantity)
            .all()
        )
        
        return [
            {
                "name": name,
                "set": set_code,
                "quantity": total_qty,
            }
            for name, set_code, total_qty in results
        ]
    
    # --- Asynchronous Methods ---
    
    async def get_with_card_async(
        self,
        session: AsyncSession,
        id: int,
    ) -> Optional[CollectionItem]:
        """Get collection item with card data (async)."""
        result = await session.execute(
            select(CollectionItem)
            .options(joinedload(CollectionItem.card))
            .where(CollectionItem.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_cards_async(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
    ) -> List[CollectionItem]:
        """Get all collection items with card data (async)."""
        query = select(CollectionItem).options(joinedload(CollectionItem.card))
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_collection_value_async(self, session: AsyncSession) -> Decimal:
        """Calculate total collection value (async)."""
        result = await session.execute(
            select(
                func.sum(
                    CollectionItem.quantity * 
                    func.coalesce(Card.price_usd, 0)
                )
            )
            .join(Card, CollectionItem.card_id == Card.id)
        )
        value = result.scalar()
        return Decimal(str(value or 0))
    
    async def get_collection_stats_async(self, session: AsyncSession) -> dict:
        """Get collection statistics (async)."""
        # Total cards
        total_result = await session.execute(
            select(func.sum(CollectionItem.quantity))
        )
        total_cards = total_result.scalar() or 0
        
        # Unique cards
        unique_result = await session.execute(
            select(func.count(func.distinct(CollectionItem.card_id)))
        )
        unique_cards = unique_result.scalar() or 0
        
        # Values
        total_value = await self.get_collection_value_async(session)
        
        foil_value_result = await session.execute(
            select(
                func.sum(
                    CollectionItem.quantity * 
                    func.coalesce(Card.price_usd_foil, 0)
                )
            )
            .join(Card, CollectionItem.card_id == Card.id)
            .where(CollectionItem.is_foil == True)
        )
        foil_value = Decimal(str(foil_value_result.scalar() or 0))
        
        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "total_value": total_value,
            "foil_value": foil_value,
            "non_foil_value": total_value - foil_value,
        }
