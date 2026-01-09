"""CardForge database module."""

from cardforge.database.connection import (
    DatabaseConnection,
    get_db,
    init_db,
    get_connection,
    get_transaction,
)
from cardforge.database.migrations.migrate import (
    MigrationRunner,
    run_migrations,
    check_migration_status,
)


async def init_database():
    """Initialize database with schema."""
    import aiosqlite
    from pathlib import Path
    from cardforge.config import get_config
    
    config = get_config()
    db_path = Path(config.database.path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    schema_path = Path(__file__).parent / "schema.sqlite.sql"
    
    async with aiosqlite.connect(str(db_path)) as conn:
        with open(schema_path, 'r') as f:
            await conn.executescript(f.read())
        await conn.commit()


__all__ = [
    'DatabaseConnection',
    'get_db',
    'init_db', 
    'get_connection',
    'get_transaction',
    'MigrationRunner',
    'run_migrations',
    'check_migration_status',
    'init_database',
]
