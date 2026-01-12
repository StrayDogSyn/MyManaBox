"""
Integration tests for CSV Collection Manager.
"""

import pytest
import pytest_asyncio
import shutil
import asyncio
import pandas as pd
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
    
    async def _seed_db(self):
        """Seed DB with necessary sets and cards."""
        from cardforge.repositories import SetRepository, CardRepository
        from cardforge.models import SetInfo, Card
        
        # Sets
        set_repo = SetRepository()
        await set_repo.upsert(SetInfo(code="CMD", name="Commander", release_date="2011-06-17"))
        await set_repo.upsert(SetInfo(code="CMR", name="Commander Legends", release_date="2020-11-20"))
        
        # Cards
        card_repo = CardRepository()
        await card_repo.upsert(Card(
            name="Sol Ring", 
            set_code="CMD", 
            scryfall_id="sol-1", 
            oracle_id="oracle-sol",
            collector_number="1"
        ))
        await card_repo.upsert(Card(
            name="Command Tower", 
            set_code="CMR", 
            scryfall_id="tower-1", 
            oracle_id="oracle-tower",
            collector_number="2"
        ))

    async def test_initialize_syncs_from_csv(self, test_csv_path):
        """Test that initialization reads the CSV and populates DB."""
        await self._seed_db()
        
        manager = CsvCollectionManager(test_csv_path)
        await manager.initialize()
        
        # Check DB
        repo = CollectionRepository()
        coll = await repo.get_by_name("moxfield_collection_test")
        assert coll is not None
        
        cards = await CollectionCardRepository().get_by_collection(coll.id)
        assert len(cards) == 2
        
        # Verify specific card data
        sol_ring = next(c for c in cards if c.card_id == 1) # Assuming auto-inc ID 1
        assert sol_ring.quantity == 1
        assert sol_ring.condition == "Near Mint"

    async def test_add_card_syncs_to_csv(self, test_csv_path):
        """Test that adding a card writes back to CSV."""
        await self._seed_db()
        
        # First sync (import existing)
        manager = CsvCollectionManager(test_csv_path)
        await manager.initialize()
        
        # Add Sol Ring (already exists, so should update quantity or fail unique constraint depending on impl)
        # add_card implementation in CsvCollectionManager calls CollectionCardRepository.add_card
        # which handles "existing" by updating quantity if attributes match.
        # But here we just pass scryfall_id and quantity.
        # Defaults: foil="normal", condition="NM".
        # The CSV Sol Ring is Near Mint, Normal (implied False).
        
        await manager.add_card("sol-1", quantity=4)
        
        # Check CSV content
        content = test_csv_path.read_text(encoding='utf-8')
        
        # Re-read to verify logical content
        df = pd.read_csv(test_csv_path)
        # Find Sol Ring row
        # Note: Exporter might combine or separate rows. 
        # CSVImporter separates by condition/foil/lang.
        # CollectionCardRepository separates by same.
        # So we should see updated quantity for the matching row.
        
        row = df[(df["Name"] == "Sol Ring") & (df["Condition"] == "Near Mint")]
        # Original was 1, added 4 -> 5
        assert row["Count"].sum() == 5
        
        # Verify version created
        history_dir = test_csv_path.parent / "history"
        assert history_dir.exists()
        assert len(list(history_dir.glob("*.csv"))) >= 1

    async def test_file_locking(self, test_csv_path):
        """Test that file locking prevents concurrent access."""
        from cardforge.utils.file_locking import FileLock, FileLockError
        
        manager = CsvCollectionManager(test_csv_path)
        
        # Manually acquire lock
        lock = FileLock(test_csv_path)
        lock.acquire()
        
        try:
            lock2 = FileLock(test_csv_path, timeout=0.1)
            with pytest.raises(FileLockError):
                lock2.acquire()
        finally:
            lock.release()

    async def test_data_integrity_roundtrip(self, test_csv_path):
        """Test full round trip: CSV -> DB -> Update -> CSV."""
        await self._seed_db()
        
        manager = CsvCollectionManager(test_csv_path)
        await manager.initialize()
            
        # 2. Update quantity of existing card
        cards = await manager.get_all_cards()
        target_card = cards[0]
        original_qty = target_card.quantity
        
        await manager.update_quantity(target_card.id, original_qty + 5)
        
        # 3. Verify CSV updated
        df = pd.read_csv(test_csv_path)
        # We need to find the specific row corresponding to target_card
        # Since we only have 2 cards and unique names, name matching is enough
        
        # We need the card name. CollectionCard has card_id.
        card_repo = CardRepository()
        card_obj = await card_repo.get(target_card.card_id)
        
        row = df[df["Name"] == card_obj.name]
        assert row["Count"].sum() == original_qty + 5
        # We rely on CSVImporter logic to parse it back to verify
        
        # 4. Re-read to verify
        manager2 = CsvCollectionManager(test_csv_path, collection_id=manager.collection_id)
        # We need to force re-import, but initialize() only imports if file exists...
        # We can call sync_from_csv directly
        stats = await manager2.sync_from_csv()
        
        cards_new = await manager2.get_all_cards()
        updated_card = next(c for c in cards_new if c.id == target_card.id)
        assert updated_card.quantity == original_qty + 5
