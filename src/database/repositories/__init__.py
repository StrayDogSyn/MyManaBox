"""
Base Repository Pattern
=======================

Provides abstract base class for all repository implementations.
Defines common CRUD operations and query patterns.
"""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Abstract base repository for common CRUD operations.
    
    Provides synchronous and asynchronous methods for database access.
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with model class.
        
        Args:
            model: SQLAlchemy ORM model class
        """
        self.model = model
    
    # --- Synchronous Methods ---
    
    def get_by_id(self, session: Session, id: int) -> Optional[T]:
        """Get a single record by ID."""
        return session.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, session: Session, limit: Optional[int] = None) -> List[T]:
        """Get all records (with optional limit)."""
        query = session.query(self.model)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def create(self, session: Session, **kwargs) -> T:
        """Create a new record."""
        instance = self.model(**kwargs)
        session.add(instance)
        session.flush()  # Get ID without committing
        return instance
    
    def update(self, session: Session, id: int, **kwargs) -> Optional[T]:
        """Update a record by ID."""
        instance = self.get_by_id(session, id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            session.flush()
        return instance
    
    def delete(self, session: Session, id: int) -> bool:
        """Delete a record by ID."""
        instance = self.get_by_id(session, id)
        if instance:
            session.delete(instance)
            session.flush()
            return True
        return False
    
    def count(self, session: Session) -> int:
        """Count total records."""
        return session.query(self.model).count()
    
    # --- Asynchronous Methods ---
    
    async def get_by_id_async(self, session: AsyncSession, id: int) -> Optional[T]:
        """Get a single record by ID (async)."""
        result = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_async(
        self,
        session: AsyncSession,
        limit: Optional[int] = None,
    ) -> List[T]:
        """Get all records (async, with optional limit)."""
        query = select(self.model)
        if limit:
            query = query.limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def create_async(self, session: AsyncSession, **kwargs) -> T:
        """Create a new record (async)."""
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        return instance
    
    async def update_async(
        self,
        session: AsyncSession,
        id: int,
        **kwargs,
    ) -> Optional[T]:
        """Update a record by ID (async)."""
        instance = await self.get_by_id_async(session, id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await session.flush()
        return instance
    
    async def delete_async(self, session: AsyncSession, id: int) -> bool:
        """Delete a record by ID (async)."""
        instance = await self.get_by_id_async(session, id)
        if instance:
            await session.delete(instance)
            await session.flush()
            return True
        return False
    
    async def count_async(self, session: AsyncSession) -> int:
        """Count total records (async)."""
        result = await session.execute(select(self.model))
        return len(list(result.scalars().all()))
