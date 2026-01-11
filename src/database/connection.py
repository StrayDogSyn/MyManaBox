"""
Database Connection Management
===============================

Provides centralized database connection handling, session management,
and connection pooling for the CardForge SQLite database.
"""

import logging
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from src.database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and session lifecycle.
    
    Supports both synchronous and asynchronous operations.
    Handles connection pooling, foreign key constraints, and WAL mode.
    """
    
    def __init__(
        self,
        database_path: Optional[Path] = None,
        echo: bool = False,
        enable_fts: bool = True,
    ):
        """
        Initialize the database manager.
        
        Args:
            database_path: Path to SQLite database file (default: data/cardforge.db)
            echo: If True, log all SQL statements
            enable_fts: If True, enable FTS5 full-text search
        """
        if database_path is None:
            database_path = Path(__file__).parent.parent.parent / "data" / "cardforge.db"
        
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.echo = echo
        self.enable_fts = enable_fts
        
        # Create sync and async engines
        self.sync_engine = self._create_sync_engine()
        self.async_engine = self._create_async_engine()
        
        # Create session factories
        self.sync_session_factory = sessionmaker(
            bind=self.sync_engine,
            class_=Session,
            expire_on_commit=False,
        )
        self.async_session_factory = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info(f"Database initialized at: {self.database_path}")
    
    def _create_sync_engine(self):
        """Create synchronous SQLite engine with optimizations."""
        database_url = f"sqlite:///{self.database_path}"
        
        engine = create_engine(
            database_url,
            echo=self.echo,
            poolclass=pool.StaticPool,  # Single connection pool for SQLite
            connect_args={
                "check_same_thread": False,  # Allow multi-threaded access
            },
        )
        
        # Enable foreign keys and WAL mode
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
        
        return engine
    
    def _create_async_engine(self):
        """Create asynchronous SQLite engine with optimizations."""
        database_url = f"sqlite+aiosqlite:///{self.database_path}"
        
        engine = create_async_engine(
            database_url,
            echo=self.echo,
            poolclass=pool.StaticPool,
            connect_args={
                "check_same_thread": False,
            },
        )
        
        # Note: Async engine pragma configuration handled differently
        # WAL mode and foreign keys set via initial sync connection
        
        return engine
    
    def create_tables(self):
        """Create all database tables synchronously."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.sync_engine)
        
        if self.enable_fts:
            self._create_fts5_tables()
        
        logger.info("Database tables created successfully")
    
    async def create_tables_async(self):
        """Create all database tables asynchronously."""
        logger.info("Creating database tables (async)...")
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        if self.enable_fts:
            await self._create_fts5_tables_async()
        
        logger.info("Database tables created successfully (async)")
    
    def _create_fts5_tables(self):
        """Create FTS5 full-text search tables."""
        with self.get_session() as session:
            # Create FTS5 virtual table for card search
            session.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
                    card_id UNINDEXED,
                    name,
                    type_line,
                    oracle_text,
                    content='cards',
                    content_rowid='id'
                )
            """)
            
            # Create triggers to keep FTS5 in sync
            session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_insert AFTER INSERT ON cards
                BEGIN
                    INSERT INTO cards_fts(card_id, name, type_line, oracle_text)
                    VALUES (new.id, new.name, new.type_line, new.oracle_text);
                END
            """)
            
            session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_update AFTER UPDATE ON cards
                BEGIN
                    UPDATE cards_fts
                    SET name = new.name,
                        type_line = new.type_line,
                        oracle_text = new.oracle_text
                    WHERE card_id = new.id;
                END
            """)
            
            session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_delete AFTER DELETE ON cards
                BEGIN
                    DELETE FROM cards_fts WHERE card_id = old.id;
                END
            """)
            
            session.commit()
            logger.info("FTS5 tables and triggers created")
    
    async def _create_fts5_tables_async(self):
        """Create FTS5 full-text search tables asynchronously."""
        async with self.async_session_factory() as session:
            # Create FTS5 virtual table for card search
            await session.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS cards_fts USING fts5(
                    card_id UNINDEXED,
                    name,
                    type_line,
                    oracle_text,
                    content='cards',
                    content_rowid='id'
                )
            """)
            
            # Create triggers (same as sync version)
            await session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_insert AFTER INSERT ON cards
                BEGIN
                    INSERT INTO cards_fts(card_id, name, type_line, oracle_text)
                    VALUES (new.id, new.name, new.type_line, new.oracle_text);
                END
            """)
            
            await session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_update AFTER UPDATE ON cards
                BEGIN
                    UPDATE cards_fts
                    SET name = new.name,
                        type_line = new.type_line,
                        oracle_text = new.oracle_text
                    WHERE card_id = new.id;
                END
            """)
            
            await session.execute("""
                CREATE TRIGGER IF NOT EXISTS cards_fts_delete AFTER DELETE ON cards
                BEGIN
                    DELETE FROM cards_fts WHERE card_id = old.id;
                END
            """)
            
            await session.commit()
            logger.info("FTS5 tables and triggers created (async)")
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(self.sync_engine)
        
        # Drop FTS5 tables
        with self.get_session() as session:
            session.execute("DROP TABLE IF EXISTS cards_fts")
            session.commit()
        
        logger.warning("All database tables dropped")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a synchronous database session (context manager).
        
        Usage:
            with db_manager.get_session() as session:
                cards = session.query(Card).all()
        """
        session = self.sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an asynchronous database session (async context manager).
        
        Usage:
            async with db_manager.get_async_session() as session:
                result = await session.execute(select(Card))
                cards = result.scalars().all()
        """
        session = self.async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error (async): {e}")
            raise
        finally:
            await session.close()
    
    def close(self):
        """Close all database connections."""
        self.sync_engine.dispose()
        logger.info("Database connections closed")
    
    async def close_async(self):
        """Close all async database connections."""
        await self.async_engine.dispose()
        logger.info("Database connections closed (async)")


# Global database manager instance (lazy initialization)
_db_manager: Optional[DatabaseManager] = None


def get_database_manager(
    database_path: Optional[Path] = None,
    echo: bool = False,
) -> DatabaseManager:
    """
    Get or create the global database manager instance.
    
    Args:
        database_path: Path to SQLite database file
        echo: If True, log all SQL statements
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager(database_path=database_path, echo=echo)
    
    return _db_manager


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Convenience function to get a database session.
    
    Usage:
        from src.database import get_db_session
        
        with get_db_session() as session:
            cards = session.query(Card).all()
    """
    db_manager = get_database_manager()
    with db_manager.get_session() as session:
        yield session
