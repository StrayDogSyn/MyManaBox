"""
CardForge Base Repository
Generic CRUD operations with async SQLite
"""

from typing import TypeVar, Generic, Optional, List, Type, Any, Dict
from abc import ABC, abstractmethod
import aiosqlite

from cardforge.models.base import BaseModel
from cardforge.database import get_connection

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T], ABC):
    """
    Base repository with generic CRUD operations.
    
    Provides async database operations for all model types.
    """
    
    table_name: str
    model_class: Type[T]
    
    def __init__(self, conn: Optional[aiosqlite.Connection] = None):
        """
        Initialize repository.
        
        Args:
            conn: Optional connection to use. If None, will get from pool.
        """
        self._conn = conn
    
    async def _get_conn(self) -> aiosqlite.Connection:
        """Get database connection."""
        if self._conn:
            return self._conn
        # This will be used in context manager pattern
        raise RuntimeError("No connection available. Use 'async with' pattern.")
    
    async def get(self, id: int) -> Optional[T]:
        """Get a single record by ID."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?",
                (id,)
            )
            row = await cursor.fetchone()
            return self.model_class.from_row(row) if row else None
    
    async def get_all(self, limit: int = 1000, offset: int = 0) -> List[T]:
        """Get all records with pagination."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [self.model_class.from_row(row) for row in rows]
    
    async def count(self) -> int:
        """Get total record count."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT COUNT(*) FROM {self.table_name}"
            )
            row = await cursor.fetchone()
            return row[0] if row else 0
    
    async def exists(self, id: int) -> bool:
        """Check if record exists."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT 1 FROM {self.table_name} WHERE id = ? LIMIT 1",
                (id,)
            )
            return await cursor.fetchone() is not None
    
    async def create(self, model: T) -> T:
        """Create a new record."""
        data = model.to_db_dict()
        
        # Remove id if None (auto-increment)
        if 'id' in data and data['id'] is None:
            del data['id']
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})",
                tuple(data.values())
            )
            await conn.commit()
            
            # Get the created record with ID
            model.id = cursor.lastrowid
            return model
    
    async def update(self, model: T) -> T:
        """Update an existing record."""
        if not model.id:
            raise ValueError("Cannot update model without ID")
        
        data = model.to_db_dict()
        id_value = data.pop('id')
        
        # Update timestamps
        if 'updated_at' in data:
            data['updated_at'] = 'CURRENT_TIMESTAMP'
        
        set_clause = ', '.join(f"{k} = ?" for k in data.keys())
        
        async with get_connection() as conn:
            await conn.execute(
                f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?",
                (*data.values(), id_value)
            )
            await conn.commit()
        
        return model
    
    async def delete(self, id: int) -> bool:
        """Delete a record by ID."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE id = ?",
                (id,)
            )
            await conn.commit()
            return cursor.rowcount > 0
    
    async def delete_many(self, ids: List[int]) -> int:
        """Delete multiple records."""
        if not ids:
            return 0
        
        placeholders = ', '.join('?' * len(ids))
        
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE id IN ({placeholders})",
                tuple(ids)
            )
            await conn.commit()
            return cursor.rowcount
    
    async def find_by(self, **kwargs) -> List[T]:
        """Find records by column values."""
        if not kwargs:
            return await self.get_all()
        
        conditions = ' AND '.join(f"{k} = ?" for k in kwargs.keys())
        
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT * FROM {self.table_name} WHERE {conditions}",
                tuple(kwargs.values())
            )
            rows = await cursor.fetchall()
            return [self.model_class.from_row(row) for row in rows]
    
    async def find_one_by(self, **kwargs) -> Optional[T]:
        """Find a single record by column values."""
        results = await self.find_by(**kwargs)
        return results[0] if results else None
    
    async def execute_query(
        self, 
        sql: str, 
        params: tuple = ()
    ) -> List[aiosqlite.Row]:
        """Execute a custom query."""
        async with get_connection() as conn:
            cursor = await conn.execute(sql, params)
            return await cursor.fetchall()
    
    async def execute_write(
        self, 
        sql: str, 
        params: tuple = ()
    ) -> int:
        """Execute a write query, return affected rows."""
        async with get_connection() as conn:
            cursor = await conn.execute(sql, params)
            await conn.commit()
            return cursor.rowcount
    
    async def bulk_create(self, models: List[T]) -> List[T]:
        """Create multiple records efficiently."""
        if not models:
            return []
        
        # Get column names from first model
        data = models[0].to_db_dict()
        if 'id' in data and data['id'] is None:
            del data['id']
        
        columns = list(data.keys())
        columns_str = ', '.join(columns)
        placeholders = ', '.join('?' * len(columns))
        
        async with get_connection() as conn:
            for model in models:
                model_data = model.to_db_dict()
                if 'id' in model_data and model_data['id'] is None:
                    del model_data['id']
                
                values = tuple(model_data.get(col) for col in columns)
                cursor = await conn.execute(
                    f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})",
                    values
                )
                model.id = cursor.lastrowid
            
            await conn.commit()
        
        return models
