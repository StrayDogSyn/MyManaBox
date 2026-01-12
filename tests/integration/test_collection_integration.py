"""
Integration tests for Collection and Database systems.
Covers lookup, analysis, recommendations, and performance.
"""

import pytest
import pytest_asyncio
import time
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from cardforge.models import Card, Collection, SetInfo
from cardforge.services.integration_service import CollectionIntegrationService
from cardforge.repositories import CardRepository, CollectionRepository, CollectionCardRepository, SetRepository
from cardforge.utils.monitoring import PerformanceMonitor
from cardforge.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db(tmp_path):
    """Initialize a temporary database for each test."""
    from cardforge.database import connection
    from cardforge.database.connection import DatabaseConnection
    
    # Reset singleton and global variable
    if DatabaseConnection._instance:
        await DatabaseConnection._instance.close()
        DatabaseConnection._instance = None
    
    connection._db = None  # Reset global variable
        
    db_path = tmp_path / "test.db"
    await init_db(str(db_path))
    
    # Create default sets for testing
    set_repo = SetRepository()
    test_sets = [
        SetInfo(code="tst", name="Test Set", release_date="2023-01-01"),
        SetInfo(code="cmd", name="Commander Set", release_date="2023-01-01"),
        SetInfo(code="prf", name="Perf Set", release_date="2023-01-01"),
        SetInfo(code="del", name="Delete Set", release_date="2023-01-01"),
    ]
    
    for set_info in test_sets:
        await set_repo.upsert(set_info)
    
    # Verify sets exist
    sets = await set_repo.get_all_codes()
    print(f"DEBUG: Existing sets: {sets}")
    
    yield
    
    # Cleanup
    if DatabaseConnection._instance:
        await DatabaseConnection._instance.close()
        DatabaseConnection._instance = None

@pytest_asyncio.fixture
async def integration_service():
    return CollectionIntegrationService()

@pytest.mark.asyncio
@pytest.mark.integration
class TestCollectionIntegration:
    
    async def test_secure_card_lookup_and_add(self, integration_service):
        """Test Case 1: Secure Connection & Basic Lookup"""
        # 1. Setup mock card in DB
        card_repo = CardRepository()
        card = Card(
            name="Integration Test Card",
            set_code="tst",
            scryfall_id="test-uuid-123",
            oracle_id="oracle-123"
        )
        print(f"DEBUG: Inserting card with set_code={card.set_code}")
        created_card = await card_repo.upsert(card)
        
        # 2. Create collection
        coll_repo = CollectionRepository()
        collection = await coll_repo.create(Collection(name=f"Integration Test Coll {time.time()}"))
        
        # 3. Perform verified add
        success = await integration_service.add_card_to_collection(
            collection.id, 
            "test-uuid-123", 
            quantity=4
        )
        
        assert success is True
        
        # 4. Verify data mapping
        cc_repo = CollectionCardRepository()
        cards = await cc_repo.get_with_card_data(collection.id)
        assert len(cards) == 1
        assert cards[0].card.name == "Integration Test Card"
        assert cards[0].quantity == 4

    async def test_collection_analysis_preparation(self, integration_service):
        """Test Case 2: Analysis Feature Data Prep"""
        # Setup data
        coll_repo = CollectionRepository()
        collection = await coll_repo.create(Collection(name=f"Analysis Test {time.time()}"))
        
        card_repo = CardRepository()
        c1 = await card_repo.upsert(Card(name="Sol Ring", set_code="cmd", scryfall_id="sol-1", cmc=1.0, type_line="Artifact"))
        c2 = await card_repo.upsert(Card(name="Command Tower", set_code="cmd", scryfall_id="tow-1", cmc=0.0, type_line="Land"))
        
        await integration_service.add_card_to_collection(collection.id, "sol-1")
        await integration_service.add_card_to_collection(collection.id, "tow-1")
        
        # Run analysis prep
        data = await integration_service.get_collection_for_analysis(collection.id)
        
        assert len(data) == 2
        assert any(d['name'] == "Sol Ring" for d in data)
        assert any(d['type_line'] == "Land" for d in data)

    async def test_validation_checks(self, integration_service):
        """Test Case 3: Data Validation"""
        coll_repo = CollectionRepository()
        collection = await coll_repo.create(Collection(name=f"Validation Test {time.time()}"))
        
        # Inject an invalid collection card directly (bypassing service)
        # Assuming we insert a record with a non-existent card_id if FKs allowed it, 
        # or simulate it by deleting the card after adding
        
        card = await CardRepository().upsert(Card(name="To Delete", set_code="del", scryfall_id="del-1"))
        await integration_service.add_card_to_collection(collection.id, "del-1")
        
        # Force delete the card (violating integrity if FKs weren't strict, but useful for logic test)
        # Note: SQLite FKs are ON, so this might fail at DB level, which is also a pass for "Secure Connection"
        # We will mock the repository response to simulate an orphan for the logic test
        
        with patch.object(CardRepository, 'get', return_value=None):
            issues = await integration_service.validate_collection_integrity(collection.id)
            assert len(issues['orphans']) > 0

    async def test_performance_load(self, integration_service):
        """Test Case 4: Performance under load"""
        coll_repo = CollectionRepository()
        collection = await coll_repo.create(Collection(name=f"Perf Test {time.time()}"))
        
        # Create 100 cards
        card_repo = CardRepository()
        cards = [
            Card(name=f"Perf Card {i}", set_code="prf", scryfall_id=f"perf-{i}")
            for i in range(100)
        ]
        await card_repo.bulk_upsert(cards)
        
        # Add them to collection
        start_time = time.time()
        for i in range(100):
            await integration_service.add_card_to_collection(collection.id, f"perf-{i}")
        duration = time.time() - start_time
        
        # Verify monitoring captured it
        stats = PerformanceMonitor.get_stats()
        assert stats['total_operations'] >= 100
        
        print(f"\nBulk add of 100 cards took {duration:.4f}s")
        assert duration < 5.0  # Performance budget
