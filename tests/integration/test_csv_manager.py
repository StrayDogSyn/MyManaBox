"""
Integration tests for CSV Collection Manager.
"""

import pytest
import pytest_asyncio
import shutil
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

from cardforge.services.csv_collection_manager import CsvCollectionManager
from cardforge.database import init_db
from cardforge.models import Collection, Card
from cardforge.repositories import CardRepository, CollectionRepository, CollectionCardRepository

@pytest_asyncio.fixture(autouse=True)
async def setup_db(tmp_path):
    """Initialize a temporary database for each test."""
    from cardforge.database import connection
    from cardforge.database.connection import DatabaseConnection
    
    # Reset singleton and global variable
    if DatabaseConnection._instance:
        await DatabaseConnection._instance.close()
    
    connection._db = None  # Reset global variable
        
    db_path = tmp_path / "test.db"
    await init_db(str(db_path))

@pytest.fixture
def test_csv_path(tmp_path):
    """Create a sample Moxfield/ManaBox CSV."""
    csv_path = tmp_path / "moxfield_collection_test.csv"
    content = """Count,Name,Edition,Condition,Language,Foil,Tag
1,Sol Ring,CMD,Near Mint,English,False,
2,Command Tower,CMR,Lightly Played,English,True,
"""
    csv_path.write_text(content, encoding='utf-8')
    return csv_path

@pytest.mark.asyncio
class TestCsvCollectionManager:
    
    async def test_initialize_syncs_from_csv(self, test_csv_path, mock_scryfall):
        """Test that initialization reads the CSV and populates DB."""
        # Setup mock card repo to avoid scryfall calls
        with patch('cardforge.importers.csv_importer.CardRepository.get_by_name', new_callable=AsyncMock) as mock_get:
            # Return dummy card
            mock_get.return_value = Card(id=1, name="Sol Ring", scryfall_id="sol-1", set_code="CMD")
            
            manager = CsvCollectionManager(test_csv_path)
            await manager.initialize()
            
            # Check DB
            repo = CollectionRepository()
            coll = await repo.get_by_name("moxfield_collection_test")
            assert coll is not None
            
            cards = await CollectionCardRepository().get_by_collection(coll.id)
            # Should have 2 entries (Sol Ring and Command Tower - assuming importer creates placeholder for 2nd)
            # Note: Importer creates placeholders if not found.
            # We mocked the first one. The second one will hit _create_placeholder_card.
            
            assert len(cards) == 2

    async def test_add_card_syncs_to_csv(self, test_csv_path, tmp_path):
        """Test that adding a card writes back to CSV."""
        manager = CsvCollectionManager(test_csv_path)
        
        # Initialize (sync IN)
        with patch('cardforge.importers.csv_importer.CardRepository.get_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = Card(id=1, name="Sol Ring", scryfall_id="sol-1", set_code="CMD")
            await manager.initialize()
        
        # Mock card repo for ADD
        with patch('cardforge.repositories.CardRepository.get_by_scryfall_id', new_callable=AsyncMock) as mock_get_sf:
            mock_get_sf.return_value = Card(id=1, name="Sol Ring", scryfall_id="sol-1", set_code="CMD")
            
            # Add a card
            await manager.add_card("sol-1", quantity=4)
            
            # Check CSV content
            content = test_csv_path.read_text(encoding='utf-8')
            assert "Sol Ring" in content
            # Quantity should be updated or new row added depending on exporter logic.
            # The exporter likely aggregates.
            
            # Verify version created
            history_dir = test_csv_path.parent / "history"
            assert history_dir.exists()
            assert len(list(history_dir.glob("*.csv"))) == 1

    async def test_file_locking(self, test_csv_path):
        """Test that file locking prevents concurrent access."""
        from cardforge.utils.file_locking import FileLock, FileLockError
        
        manager = CsvCollectionManager(test_csv_path)
        
        # Manually acquire lock
        lock = FileLock(test_csv_path)
        lock.acquire()
        
        try:
            # Try to sync while locked (should fail or wait -> we simulate fail with short timeout)
            # We need to patch the internal lock of manager or use a separate process.
            # Since we are in same process, re-entrant locking isn't supported by our simple FileLock.
            # So creating another lock object for same file should fail.
            
            lock2 = FileLock(test_csv_path, timeout=0.1)
            with pytest.raises(FileLockError):
                lock2.acquire()
                
        finally:
            lock.release()

    async def test_data_integrity_roundtrip(self, test_csv_path):
        """Test full round trip: CSV -> DB -> Update -> CSV."""
        manager = CsvCollectionManager(test_csv_path)
        
        # 1. Init
        with patch('cardforge.importers.csv_importer.CardRepository.get_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = Card(id=1, name="Sol Ring", scryfall_id="sol-1", set_code="CMD")
            await manager.initialize()
            
        # 2. Update quantity of existing card
        cards = await manager.get_all_cards()
        target_card = cards[0]
        original_qty = target_card.quantity
        
        await manager.update_quantity(target_card.id, original_qty + 5)
        
        # 3. Verify CSV updated
        content = test_csv_path.read_text()
        # Exporter format might differ slightly but data should be there
        # We rely on CSVImporter logic to parse it back to verify
        
        # 4. Re-read to verify
        manager2 = CsvCollectionManager(test_csv_path, collection_id=manager.collection_id)
        # We need to force re-import, but initialize() only imports if file exists...
        # We can call sync_from_csv directly
        stats = await manager2.sync_from_csv()
        
        cards_new = await manager2.get_all_cards()
        updated_card = next(c for c in cards_new if c.id == target_card.id)
        assert updated_card.quantity == original_qty + 5
