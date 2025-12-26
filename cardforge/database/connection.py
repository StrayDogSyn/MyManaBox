"""
CardForge Database Connection Management
Async SQLite with connection pooling and WAL mode
"""

import asyncio
import aiosqlite
from pathlib import Path
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import logging

from cardforge.config import get_config, DATA_DIR

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Async SQLite database connection manager.
    
    Features:
    - WAL mode for better concurrency
    - Foreign keys enabled
    - Connection pooling with semaphore
    - Automatic schema initialization
    """
    
    _instance: Optional['DatabaseConnection'] = None
    _lock = asyncio.Lock()
    
    def __init__(self, db_path: Optional[str] = None, pool_size: int = 5):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file
            pool_size: Maximum concurrent connections
        """
        config = get_config()
        self.db_path = Path(db_path or config.database.path)
        self.pool_size = pool_size
        self._semaphore = asyncio.Semaphore(pool_size)
        self._initialized = False
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    async def get_instance(cls, db_path: Optional[str] = None) -> 'DatabaseConnection':
        """Get singleton instance of database connection."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(db_path)
                    await cls._instance.initialize()
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize database with schema."""
        if self._initialized:
            return
        
        async with self._semaphore:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable WAL mode for better concurrency
                await db.execute("PRAGMA journal_mode=WAL")
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys=ON")
                # Performance optimizations
                await db.execute("PRAGMA synchronous=NORMAL")
                await db.execute("PRAGMA cache_size=-64000")  # 64MB cache
                await db.execute("PRAGMA temp_store=MEMORY")
                
                # Run schema initialization
                schema_path = Path(__file__).parent / 'schema.sqlite.sql'
                if schema_path.exists():
                    schema_sql = schema_path.read_text()
                    await db.executescript(schema_sql)
                    await db.commit()
                    logger.info(f"Database initialized at {self.db_path}")
                else:
                    logger.warning(f"Schema file not found at {schema_path}")
        
        self._initialized = True
    
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Get a database connection from the pool.
        
        Usage:
            async with db.connection() as conn:
                await conn.execute("SELECT * FROM cards")
        """
        await self.initialize()
        
        async with self._semaphore:
            conn = await aiosqlite.connect(self.db_path)
            try:
                # Configure connection
                await conn.execute("PRAGMA foreign_keys=ON")
                conn.row_factory = aiosqlite.Row
                yield conn
            finally:
                await conn.close()
    
    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """
        Get a connection with automatic transaction handling.
        
        Commits on success, rolls back on exception.
        """
        async with self.connection() as conn:
            try:
                yield conn
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
    
    async def execute(self, sql: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """Execute a single SQL statement."""
        async with self.connection() as conn:
            cursor = await conn.execute(sql, parameters)
            await conn.commit()
            return cursor
    
    async def execute_many(self, sql: str, parameters_list: list) -> None:
        """Execute SQL statement with multiple parameter sets."""
        async with self.connection() as conn:
            await conn.executemany(sql, parameters_list)
            await conn.commit()
    
    async def fetch_one(self, sql: str, parameters: tuple = ()) -> Optional[aiosqlite.Row]:
        """Fetch a single row."""
        async with self.connection() as conn:
            cursor = await conn.execute(sql, parameters)
            return await cursor.fetchone()
    
    async def fetch_all(self, sql: str, parameters: tuple = ()) -> list[aiosqlite.Row]:
        """Fetch all rows."""
        async with self.connection() as conn:
            cursor = await conn.execute(sql, parameters)
            return await cursor.fetchall()
    
    async def get_schema_version(self) -> int:
        """Get current schema version."""
        try:
            row = await self.fetch_one(
                "SELECT MAX(version) as version FROM schema_version"
            )
            return row['version'] if row else 0
        except Exception:
            return 0
    
    async def close(self) -> None:
        """Close all connections and reset singleton."""
        DatabaseConnection._instance = None
        self._initialized = False


# Convenience functions for global access
_db: Optional[DatabaseConnection] = None


async def get_db(db_path: Optional[str] = None) -> DatabaseConnection:
    """Get database connection instance."""
    global _db
    if _db is None:
        _db = await DatabaseConnection.get_instance(db_path)
    return _db


async def init_db(db_path: Optional[str] = None) -> DatabaseConnection:
    """Initialize database and return connection."""
    db = await get_db(db_path)
    await db.initialize()
    return db


@asynccontextmanager
async def get_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get a database connection (convenience wrapper)."""
    db = await get_db()
    async with db.connection() as conn:
        yield conn


@asynccontextmanager  
async def get_transaction() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get a database transaction (convenience wrapper)."""
    db = await get_db()
    async with db.transaction() as conn:
        yield conn
