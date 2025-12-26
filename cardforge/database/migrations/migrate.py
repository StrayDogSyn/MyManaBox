"""
CardForge Database Migration System
Simple version-based SQL migrations
"""

import asyncio
from pathlib import Path
from typing import List, Tuple
import logging
import aiosqlite

from cardforge.database.connection import get_db

logger = logging.getLogger(__name__)


class MigrationRunner:
    """
    Handles database schema migrations.
    
    Migrations are SQL files in the migrations/ directory named:
    - v001_initial.sql
    - v002_add_price_history.sql
    - etc.
    """
    
    def __init__(self, migrations_dir: Path = None):
        """Initialize migration runner."""
        self.migrations_dir = migrations_dir or Path(__file__).parent / 'migrations'
        self.migrations_dir.mkdir(exist_ok=True)
    
    def get_available_migrations(self) -> List[Tuple[int, Path]]:
        """Get list of available migration files sorted by version."""
        migrations = []
        
        for file in self.migrations_dir.glob("v*.sql"):
            try:
                # Extract version number from filename (e.g., v001_initial.sql -> 1)
                version_str = file.stem.split('_')[0].lstrip('v')
                version = int(version_str)
                migrations.append((version, file))
            except (ValueError, IndexError):
                logger.warning(f"Skipping invalid migration file: {file}")
                continue
        
        return sorted(migrations, key=lambda x: x[0])
    
    async def get_applied_versions(self, conn: aiosqlite.Connection) -> set:
        """Get set of applied migration versions."""
        try:
            cursor = await conn.execute(
                "SELECT version FROM schema_version ORDER BY version"
            )
            rows = await cursor.fetchall()
            return {row[0] for row in rows}
        except Exception:
            # Table doesn't exist yet
            return set()
    
    async def apply_migration(
        self, 
        conn: aiosqlite.Connection, 
        version: int, 
        migration_path: Path
    ) -> bool:
        """Apply a single migration."""
        try:
            logger.info(f"Applying migration v{version:03d}: {migration_path.stem}")
            
            sql = migration_path.read_text()
            await conn.executescript(sql)
            
            # Record migration
            await conn.execute(
                "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                (version, migration_path.stem)
            )
            await conn.commit()
            
            logger.info(f"Migration v{version:03d} applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration v{version:03d} failed: {e}")
            await conn.rollback()
            raise
    
    async def migrate(self, target_version: int = None) -> int:
        """
        Run pending migrations up to target version.
        
        Args:
            target_version: Stop at this version (None = run all)
        
        Returns:
            Number of migrations applied
        """
        db = await get_db()
        applied_count = 0
        
        async with db.connection() as conn:
            applied = await self.get_applied_versions(conn)
            available = self.get_available_migrations()
            
            for version, path in available:
                if version in applied:
                    continue
                
                if target_version and version > target_version:
                    break
                
                await self.apply_migration(conn, version, path)
                applied_count += 1
        
        if applied_count > 0:
            logger.info(f"Applied {applied_count} migration(s)")
        else:
            logger.info("Database is up to date")
        
        return applied_count
    
    async def status(self) -> dict:
        """Get migration status."""
        db = await get_db()
        
        async with db.connection() as conn:
            applied = await self.get_applied_versions(conn)
            available = self.get_available_migrations()
            
            pending = [
                (v, p.stem) for v, p in available 
                if v not in applied
            ]
            
            return {
                "current_version": max(applied) if applied else 0,
                "applied_count": len(applied),
                "pending_count": len(pending),
                "pending_migrations": pending
            }


async def run_migrations(target_version: int = None) -> int:
    """Convenience function to run migrations."""
    runner = MigrationRunner()
    return await runner.migrate(target_version)


async def check_migration_status() -> dict:
    """Convenience function to check migration status."""
    runner = MigrationRunner()
    return await runner.status()


# CLI entry point for running migrations directly
if __name__ == "__main__":
    import sys
    
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        if len(sys.argv) > 1 and sys.argv[1] == "status":
            status = await check_migration_status()
            print(f"Current version: {status['current_version']}")
            print(f"Applied: {status['applied_count']}")
            print(f"Pending: {status['pending_count']}")
            if status['pending_migrations']:
                print("Pending migrations:")
                for v, name in status['pending_migrations']:
                    print(f"  - v{v:03d}: {name}")
        else:
            count = await run_migrations()
            print(f"Applied {count} migration(s)")
    
    asyncio.run(main())
