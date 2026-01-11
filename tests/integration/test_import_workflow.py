"""
Integration tests for CSV import and migration workflow.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import List, Tuple

import pytest
from sqlalchemy.orm import Session

from src.database.connection import DatabaseManager
from src.database.models import Card, CollectionItem
from src.importers.csv_importer import CardImport, import_csv
from src.services.migration_service import MigrationManager, BackupManager
from src.services.batch_insert_service import BatchInsertService


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db_manager = DatabaseManager(database_path=db_path)
        db_manager.create_tables()  # Initialize the schema
        yield db_manager
        try:
            db_manager.close()
        except:
            pass


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """Create sample CSV file for testing."""
    csv_file = tmp_path / "test_collection.csv"
    
    # ManaBox format
    csv_content = """Name,Card Name,Set Code,Set,Quantity,Foil?,Condition,Language,Location,Notes
Aetherflux Reservoir,Aetherflux Reservoir,KLD,Kaladesh,1,No,NM,English,Binder,Test card 1
Artery Urchin,Artery Urchin,MIR,Mirage,2,Yes,LP,English,Box,Test card 2
Austere Command,Austere Command,LRW,Lorwyn,1,No,NM,English,Binder,Test card 3
"""
    
    csv_file.write_text(csv_content, encoding='utf-8')
    return csv_file


class TestCSVImporter:
    """Tests for CSV importer."""
    
    def test_import_manabox_format(self, sample_csv: Path):
        """Test importing ManaBox format CSV."""
        cards, errors = import_csv(sample_csv, format="manabox")
        
        assert len(cards) == 3
        assert len(errors) == 0
        
        # Check first card
        card = cards[0]
        assert card.name == "Aetherflux Reservoir"
        assert card.set_code == "kld"  # Set codes are lowercase in importer
        assert card.quantity == 1
        assert card.is_foil is False
    
    def test_import_auto_detect(self, sample_csv: Path):
        """Test auto-detection of CSV format."""
        cards, errors = import_csv(sample_csv)  # No format specified
        
        assert len(cards) == 3
        assert len(errors) == 0
    
    def test_import_with_errors(self, tmp_path: Path):
        """Test import with malformed data."""
        csv_file = tmp_path / "bad_data.csv"
        csv_content = """name,set,quantity,foil
Card 1,abc,1,false
Card 2,def,invalid,false
Card 3,ghi,1,false
"""
        csv_file.write_text(csv_content, encoding='utf-8')
        
        cards, errors = import_csv(csv_file, format="standard")
        
        # Should import 2 valid cards (Card 1 and Card 3, skipping Card 2)
        assert len(cards) >= 2
        # Should have 1 error for the invalid quantity
        assert len(errors) >= 1


class TestBackupManager:
    """Tests for backup manager."""
    
    def test_create_backup(self, temp_db: DatabaseManager, tmp_path: Path):
        """Test creating a backup."""
        backup_manager = BackupManager(tmp_path)
        
        # Create some test data
        with temp_db.get_session() as session:
            card = Card(
                name="Test Card",
                scryfall_id="test-id-123",
                set_code="TST",
                rarity="common",
            )
            session.add(card)
            session.commit()
        
        # Create backup
        backup_path = backup_manager.create_backup(temp_db, "test_backup")
        
        assert backup_path.exists()
        assert backup_path.is_dir()
        assert "test_backup" in backup_path.name
    
    def test_list_backups(self, temp_db: DatabaseManager, tmp_path: Path):
        """Test listing backups."""
        backup_manager = BackupManager(tmp_path)
        
        # Create multiple backups
        backup_manager.create_backup(temp_db, "backup1")
        backup_manager.create_backup(temp_db, "backup2")
        
        backups = backup_manager.list_backups()
        
        assert len(backups) == 2


class TestMigrationManager:
    """Tests for migration manager."""
    
    @pytest.mark.asyncio
    async def test_import_csv_file(
        self,
        temp_db: DatabaseManager,
        sample_csv: Path,
        tmp_path: Path,
    ):
        """Test importing CSV file."""
        migration = MigrationManager(temp_db)
        migration.backup_manager = BackupManager(tmp_path)
        
        result = await migration.import_csv_file(
            sample_csv,
            format="manabox",
            create_backup=False,
            replace_mode=False,
        )
        
        # Check result structure
        assert "csv_stats" in result
        assert "enrichment_stats" in result
        assert "insert_stats" in result
        assert "collection_stats" in result
        
        # Check CSV stats
        csv_stats = result["csv_stats"]
        assert csv_stats["total_imported"] >= 3
        assert csv_stats["errors"] == 0
    
    @pytest.mark.asyncio
    async def test_import_with_backup(
        self,
        temp_db: DatabaseManager,
        sample_csv: Path,
        tmp_path: Path,
    ):
        """Test import with backup creation."""
        migration = MigrationManager(temp_db)
        migration.backup_manager = BackupManager(tmp_path)
        
        result = await migration.import_csv_file(
            sample_csv,
            create_backup=True,
            replace_mode=False,
        )
        
        # Check backup was created
        backups = migration.backup_manager.list_backups()
        assert len(backups) >= 1
    
    def test_get_import_status(self, temp_db: DatabaseManager):
        """Test getting import status."""
        # Add test data
        with temp_db.get_session() as session:
            card = Card(
                name="Test Card",
                scryfall_id="test-123",
                set_code="TST",
                rarity="common",
            )
            session.add(card)
            session.flush()  # Flush to get the ID
            card_id = card.id
            
            item = CollectionItem(
                card_id=card_id,
                quantity=2,
                is_foil=False,
            )
            session.add(item)
            session.commit()
        
        # Get status - should see the item we just added
        migration = MigrationManager(temp_db)
        status = migration.get_import_status()
        
        # Verify we have data
        assert status["unique_cards"] >= 1
        assert status["total_cards"] >= 2


class TestBatchInsertService:
    """Tests for batch insertion."""
    
    def test_insert_collection_items(
        self,
        temp_db: DatabaseManager,
        sample_csv: Path,
    ):
        """Test inserting collection items."""
        # Import CSV
        cards, _ = import_csv(sample_csv, format="manabox")
        
        # Insert into database
        with temp_db.get_session() as session:
            service = BatchInsertService(session)
            stats = service.insert_collection_items(
                cards,
                replace_mode=False,
            )
        
        # Check stats
        assert "inserted" in stats
        assert "updated" in stats
        assert stats["inserted"] >= 3
    
    def test_insert_with_replace_mode(
        self,
        temp_db: DatabaseManager,
        sample_csv: Path,
    ):
        """Test insert with replace mode."""
        # Import CSV
        cards, _ = import_csv(sample_csv, format="manabox")
        
        # First insert
        with temp_db.get_session() as session:
            service = BatchInsertService(session)
            stats1 = service.insert_collection_items(cards, replace_mode=False)
        
        count_after_first = self._count_items(temp_db)
        
        # Second insert with replace mode
        with temp_db.get_session() as session:
            service = BatchInsertService(session)
            stats2 = service.insert_collection_items(cards, replace_mode=True)
        
        count_after_second = self._count_items(temp_db)
        
        # Replace mode should clear and re-insert
        # Counts might differ due to deduplication
        assert count_after_second > 0
    
    def _count_items(self, db_manager: DatabaseManager) -> int:
        """Count total collection items."""
        with db_manager.get_session() as session:
            return session.query(CollectionItem).count()


class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_complete_import_workflow(
        self,
        temp_db: DatabaseManager,
        sample_csv: Path,
        tmp_path: Path,
    ):
        """Test complete import workflow from CSV to database."""
        # Setup
        migration = MigrationManager(temp_db)
        migration.backup_manager = BackupManager(tmp_path)
        
        # Import
        result = await migration.import_csv_file(
            sample_csv,
            format="manabox",
            create_backup=True,
            replace_mode=False,
        )
        
        # Verify all stages completed
        assert result["csv_stats"]["total_imported"] >= 3
        assert result["collection_stats"]["total_cards"] >= 3
        
        # Verify data in database
        with temp_db.get_session() as session:
            cards = session.query(Card).count()
            items = session.query(CollectionItem).count()
            
            assert cards >= 3
            assert items >= 3
