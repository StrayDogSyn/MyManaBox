"""
Backup and Migration Utilities
==============================

Handles database backups, migrations, and data imports with safety checks.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import Card, CollectionItem
from src.database.repositories.collection_repository import CollectionRepository
from src.importers.csv_importer import import_csv, CardImport
from src.services.batch_insert_service import BatchInsertService
from src.services.enrichment_service import EnrichmentService

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages database and data backups."""
    
    def __init__(self, backup_dir: Path = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups (default: data/backups)
        """
        if backup_dir is None:
            backup_dir = Path(__file__).parent.parent.parent / "data" / "backups"
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(
        self,
        db_manager: DatabaseManager,
        description: str = "pre_import",
    ) -> Path:
        """
        Create database backup.
        
        Args:
            db_manager: DatabaseManager instance
            description: Backup description for directory name
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{description}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy database file
            db_file = db_manager.database_path
            if db_file.exists():
                backup_db = backup_path / db_file.name
                shutil.copy2(db_file, backup_db)
                logger.info(f"Database backed up to {backup_db}")
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            raise
        
        return backup_path
    
    def list_backups(self) -> list:
        """List all available backups."""
        if not self.backup_dir.exists():
            return []
        
        backups = sorted(
            [d for d in self.backup_dir.iterdir() if d.is_dir()],
            key=lambda x: x.name,
            reverse=True,
        )
        return backups
    
    def restore_backup(
        self,
        backup_path: Path,
        db_manager: DatabaseManager,
    ) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup directory
            db_manager: DatabaseManager instance
        
        Returns:
            True if successful
        """
        try:
            backup_db = backup_path / db_manager.database_path.name
            if not backup_db.exists():
                logger.error(f"Backup database not found: {backup_db}")
                return False
            
            # Close current connection
            db_manager.close()
            
            # Restore database
            shutil.copy2(backup_db, db_manager.database_path)
            logger.info(f"Database restored from {backup_path}")
            
            # Reconnect
            db_manager.sync_engine.dispose()
            
            return True
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False


class MigrationManager:
    """Manages data migrations and imports."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize migration manager.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.backup_manager = BackupManager()
    
    async def import_csv_file(
        self,
        csv_path: Path,
        format: Optional[str] = None,
        create_backup: bool = True,
        replace_mode: bool = False,
    ) -> dict:
        """
        Import CSV file into database.
        
        Args:
            csv_path: Path to CSV file
            format: CSV format ('manabox', 'archidekt', 'moxfield', 'standard')
            create_backup: If True, backup database before import
            replace_mode: If True, replace existing collection
        
        Returns:
            Import statistics
        """
        csv_path = Path(csv_path)
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        logger.info(f"Starting import from {csv_path.name}")
        logger.info(f"  Format: {format or 'auto-detect'}")
        logger.info(f"  Replace mode: {replace_mode}")
        
        # Create backup
        if create_backup:
            backup_path = self.backup_manager.create_backup(
                self.db_manager,
                description="pre_import",
            )
            logger.info(f"Backup created: {backup_path}")
        
        # Import CSV
        cards, errors = import_csv(csv_path, format=format)
        
        if errors:
            logger.warning(f"Import had {len(errors)} errors:")
            for line, error in errors[:10]:
                logger.warning(f"  Line {line}: {error}")
        
        logger.info(f"Imported {len(cards)} cards from CSV")
        
        # Enrich with Scryfall data
        logger.info("Enriching cards with Scryfall data...")
        enrichment_service = EnrichmentService(session=None)
        scryfall_map, enrich_stats = await enrichment_service.enrich_imports(cards)
        logger.info(f"Enrichment stats: {enrich_stats}")
        
        # Insert into database
        with self.db_manager.get_session() as session:
            batch_service = BatchInsertService(session)
            insert_stats = batch_service.insert_collection_items(
                cards,
                scryfall_map=scryfall_map,
                replace_mode=replace_mode,
            )
        
        # Get final collection stats
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            stats = collection_repo.get_collection_stats(session)
            collection_items = session.query(CollectionItem).count()
            foil_cards = session.query(CollectionItem).filter(
                CollectionItem.is_foil == True
            ).count()
            
            collection_stats = {
                'collection_items': collection_items,
                'unique_cards': stats.get('unique_cards', 0),
                'total_cards': stats.get('total_cards', 0),
                'foil_cards': foil_cards,
                'total_value': float(stats.get('total_value', 0)),
            }
        
        result = {
            "csv_stats": {
                "total_imported": len(cards),
                "errors": len(errors),
            },
            "enrichment_stats": enrich_stats,
            "insert_stats": insert_stats,
            "collection_stats": collection_stats,
        }
        
        logger.info(f"Import complete!")
        logger.info(f"  Cards: {collection_stats['total_cards']}")
        logger.info(f"  Value: ${collection_stats.get('total_value', 'N/A')}")
        
        return result
    
    def get_import_status(self) -> dict:
        """Get current import status and stats."""
        with self.db_manager.get_session() as session:
            collection_repo = CollectionRepository()
            stats = collection_repo.get_collection_stats(session)
        
        return {
            "collection_items": stats.get('collection_items', 0),
            "unique_cards": stats.get('unique_cards', 0),
            "total_cards": stats.get('total_cards', 0),
            "foil_cards": stats.get('foil_cards', 0),
            "total_value": stats.get('total_value', 0),
        }
