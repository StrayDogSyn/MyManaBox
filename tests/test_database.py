"""
Database Layer Tests
====================

Integration tests for database connection, models, and repositories.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from src.database import (
    DatabaseManager,
    Card,
    CollectionItem,
    Deck,
    DeckCard,
)
from src.database.repositories.card_repository import CardRepository
from src.database.repositories.collection_repository import CollectionRepository
from src.database.repositories.deck_repository import DeckRepository, DeckCardRepository


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database for testing."""
    return tmp_path / "test_cardforge.db"


@pytest.fixture
def db_manager(test_db_path):
    """Create and initialize a test database manager."""
    manager = DatabaseManager(database_path=test_db_path, enable_fts=True)
    manager.create_tables()
    yield manager
    manager.close()


@pytest.fixture
def sample_card_data():
    """Sample card data for testing."""
    return {
        "scryfall_id": "12345678-1234-1234-1234-123456789012",
        "oracle_id": "87654321-4321-4321-4321-210987654321",
        "name": "Sol Ring",
        "set_code": "cmr",
        "collector_number": "415",
        "mana_cost": "{1}",
        "cmc": 1.0,
        "type_line": "Artifact",
        "oracle_text": "{T}: Add {C}{C}.",
        "colors": "",
        "color_identity": "",
        "rarity": "uncommon",
        "is_foil_available": True,
        "is_reserved_list": False,
        "is_commander": False,
        "price_usd": Decimal("1.50"),
    }


# ============================================================================
# DATABASE CONNECTION TESTS
# ============================================================================

class TestDatabaseManager:
    """Test database connection and initialization."""
    
    def test_create_database(self, test_db_path):
        """Test database creation."""
        manager = DatabaseManager(database_path=test_db_path)
        manager.create_tables()
        
        assert test_db_path.exists()
        assert test_db_path.stat().st_size > 0
        
        manager.close()
    
    def test_get_session(self, db_manager):
        """Test synchronous session creation."""
        with db_manager.get_session() as session:
            assert session is not None
            # Session should be active
            assert session.is_active
    
    def test_fts5_tables_created(self, db_manager):
        """Test FTS5 tables are created."""
        with db_manager.get_session() as session:
            # Query FTS5 table (should not raise error)
            result = session.execute("SELECT name FROM sqlite_master WHERE name='cards_fts'")
            tables = result.fetchall()
            assert len(tables) == 1
    
    @pytest.mark.asyncio
    async def test_async_session(self, db_manager):
        """Test asynchronous session creation."""
        async with db_manager.get_async_session() as session:
            assert session is not None


# ============================================================================
# CARD MODEL TESTS
# ============================================================================

class TestCardModel:
    """Test Card model and CardRepository."""
    
    def test_create_card(self, db_manager, sample_card_data):
        """Test creating a card."""
        repo = CardRepository()
        
        with db_manager.get_session() as session:
            card = repo.create(session, **sample_card_data)
            
            assert card.id is not None
            assert card.name == "Sol Ring"
            assert card.scryfall_id == sample_card_data["scryfall_id"]
            assert card.price_usd == Decimal("1.50")
    
    def test_get_card_by_id(self, db_manager, sample_card_data):
        """Test retrieving a card by ID."""
        repo = CardRepository()
        
        with db_manager.get_session() as session:
            card = repo.create(session, **sample_card_data)
            card_id = card.id
        
        with db_manager.get_session() as session:
            retrieved = repo.get_by_id(session, card_id)
            assert retrieved is not None
            assert retrieved.name == "Sol Ring"
    
    def test_get_card_by_scryfall_id(self, db_manager, sample_card_data):
        """Test retrieving a card by Scryfall ID."""
        repo = CardRepository()
        
        with db_manager.get_session() as session:
            repo.create(session, **sample_card_data)
        
        with db_manager.get_session() as session:
            card = repo.get_by_scryfall_id(session, sample_card_data["scryfall_id"])
            assert card is not None
            assert card.name == "Sol Ring"
    
    def test_search_by_name(self, db_manager, sample_card_data):
        """Test searching cards by name."""
        repo = CardRepository()
        
        with db_manager.get_session() as session:
            repo.create(session, **sample_card_data)
        
        with db_manager.get_session() as session:
            results = repo.search_by_name(session, "Sol")
            assert len(results) == 1
            assert results[0].name == "Sol Ring"
    
    @pytest.mark.asyncio
    async def test_create_card_async(self, db_manager, sample_card_data):
        """Test creating a card asynchronously."""
        repo = CardRepository()
        
        async with db_manager.get_async_session() as session:
            card = await repo.create_async(session, **sample_card_data)
            
            assert card.id is not None
            assert card.name == "Sol Ring"


# ============================================================================
# COLLECTION MODEL TESTS
# ============================================================================

class TestCollectionModel:
    """Test CollectionItem model and CollectionRepository."""
    
    def test_create_collection_item(self, db_manager, sample_card_data):
        """Test creating a collection item."""
        card_repo = CardRepository()
        collection_repo = CollectionRepository()
        
        with db_manager.get_session() as session:
            # Create card first
            card = card_repo.create(session, **sample_card_data)
            
            # Create collection item
            item = collection_repo.create(
                session,
                card_id=card.id,
                quantity=4,
                is_foil=False,
                condition="near_mint",
            )
            
            assert item.id is not None
            assert item.quantity == 4
            assert item.card_id == card.id
    
    def test_get_collection_with_card(self, db_manager, sample_card_data):
        """Test retrieving collection item with card data."""
        card_repo = CardRepository()
        collection_repo = CollectionRepository()
        
        with db_manager.get_session() as session:
            card = card_repo.create(session, **sample_card_data)
            item = collection_repo.create(session, card_id=card.id, quantity=2)
            item_id = item.id
        
        with db_manager.get_session() as session:
            retrieved = collection_repo.get_with_card(session, item_id)
            assert retrieved is not None
            assert retrieved.card.name == "Sol Ring"
    
    def test_get_collection_stats(self, db_manager, sample_card_data):
        """Test collection statistics."""
        card_repo = CardRepository()
        collection_repo = CollectionRepository()
        
        with db_manager.get_session() as session:
            # Create multiple cards
            card1 = card_repo.create(session, **sample_card_data)
            
            card2_data = sample_card_data.copy()
            card2_data["scryfall_id"] = "11111111-1111-1111-1111-111111111111"
            card2_data["name"] = "Command Tower"
            card2_data["price_usd"] = Decimal("0.50")
            card2 = card_repo.create(session, **card2_data)
            
            # Add to collection
            collection_repo.create(session, card_id=card1.id, quantity=4)
            collection_repo.create(session, card_id=card2.id, quantity=1)
        
        with db_manager.get_session() as session:
            stats = collection_repo.get_collection_stats(session)
            
            assert stats["total_cards"] == 5  # 4 + 1
            assert stats["unique_cards"] == 2
            assert stats["total_value"] == Decimal("6.50")  # (4 * 1.50) + (1 * 0.50)


# ============================================================================
# DECK MODEL TESTS
# ============================================================================

class TestDeckModel:
    """Test Deck and DeckCard models."""
    
    def test_create_deck(self, db_manager, sample_card_data):
        """Test creating a deck."""
        card_repo = CardRepository()
        deck_repo = DeckRepository()
        
        with db_manager.get_session() as session:
            # Create commander card
            commander = card_repo.create(session, **sample_card_data)
            
            # Create deck
            deck = deck_repo.create(
                session,
                name="My Commander Deck",
                format="commander",
                commander_id=commander.id,
                color_identity="",
            )
            
            assert deck.id is not None
            assert deck.name == "My Commander Deck"
            assert deck.commander_id == commander.id
    
    def test_add_cards_to_deck(self, db_manager, sample_card_data):
        """Test adding cards to a deck."""
        card_repo = CardRepository()
        deck_repo = DeckRepository()
        deck_card_repo = DeckCardRepository()
        
        with db_manager.get_session() as session:
            # Create deck and cards
            deck = deck_repo.create(
                session,
                name="Test Deck",
                format="commander",
            )
            card = card_repo.create(session, **sample_card_data)
            
            # Add card to deck
            deck_card = deck_card_repo.add_card_to_deck(
                session,
                deck_id=deck.id,
                card_id=card.id,
                quantity=1,
                category="mainboard",
            )
            
            assert deck_card.id is not None
            assert deck_card.deck_id == deck.id
            assert deck_card.card_id == card.id
    
    def test_get_deck_with_cards(self, db_manager, sample_card_data):
        """Test retrieving deck with all cards."""
        card_repo = CardRepository()
        deck_repo = DeckRepository()
        deck_card_repo = DeckCardRepository()
        
        with db_manager.get_session() as session:
            deck = deck_repo.create(session, name="Test Deck", format="commander")
            card = card_repo.create(session, **sample_card_data)
            deck_card_repo.add_card_to_deck(
                session,
                deck_id=deck.id,
                card_id=card.id,
                quantity=1,
            )
            deck_id = deck.id
        
        with db_manager.get_session() as session:
            retrieved = deck_repo.get_with_cards(session, deck_id)
            assert retrieved is not None
            assert len(retrieved.deck_cards) == 1
            assert retrieved.deck_cards[0].card.name == "Sol Ring"
    
    def test_update_deck_stats(self, db_manager, sample_card_data):
        """Test updating deck statistics."""
        card_repo = CardRepository()
        deck_repo = DeckRepository()
        deck_card_repo = DeckCardRepository()
        
        with db_manager.get_session() as session:
            deck = deck_repo.create(session, name="Test Deck", format="commander")
            card = card_repo.create(session, **sample_card_data)
            deck_card_repo.add_card_to_deck(
                session,
                deck_id=deck.id,
                card_id=card.id,
                quantity=4,
                category="mainboard",
            )
            deck_id = deck.id
        
        with db_manager.get_session() as session:
            updated = deck_repo.update_deck_stats(session, deck_id)
            assert updated.total_cards == 4
            assert updated.estimated_value == Decimal("6.00")  # 4 * 1.50


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDatabaseIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self, db_manager):
        """Test complete workflow: create card, add to collection, add to deck."""
        card_repo = CardRepository()
        collection_repo = CollectionRepository()
        deck_repo = DeckRepository()
        deck_card_repo = DeckCardRepository()
        
        with db_manager.get_session() as session:
            # Create card
            card = card_repo.create(
                session,
                scryfall_id="test-1234",
                name="Test Card",
                set_code="tst",
                collector_number="1",
                type_line="Creature - Human",
                rarity="rare",
                cmc=3.0,
                price_usd=Decimal("5.00"),
            )
            
            # Add to collection
            collection_item = collection_repo.create(
                session,
                card_id=card.id,
                quantity=2,
                condition="near_mint",
            )
            
            # Create deck
            deck = deck_repo.create(
                session,
                name="Test Deck",
                format="standard",
            )
            
            # Add card to deck
            deck_card = deck_card_repo.add_card_to_deck(
                session,
                deck_id=deck.id,
                card_id=card.id,
                quantity=2,
            )
            
            # Verify everything
            assert card.id is not None
            assert collection_item.card_id == card.id
            assert deck_card.deck_id == deck.id
            assert deck_card.card_id == card.id
            
            # Update deck stats
            updated_deck = deck_repo.update_deck_stats(session, deck.id)
            assert updated_deck.total_cards == 2
            assert updated_deck.estimated_value == Decimal("10.00")
