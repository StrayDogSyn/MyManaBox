"""
Pytest fixtures for CardForge test suite.

Central fixtures used across all test modules. Provides:
- Temporary databases for isolation
- Sample data
- Mock services
- Configuration fixtures
"""
import pytest
import tempfile
import sqlite3
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import types after path is set
from cardforge.types import Rarity, Condition, Foil, Language, Format


# =============================================================================
# SAMPLE DATA - Database models
# =============================================================================

@pytest.fixture
def sample_card_data():
    """Sample card data matching database schema."""
    return {
        "id": 1,
        "scryfall_id": "12345678-1234-1234-1234-123456789012",
        "oracle_id": "87654321-4321-4321-4321-210987654321",
        "name": "Lightning Bolt",
        "set_code": "LEA",
        "collector_number": "1",
        "type_line": "Instant",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "mana_cost": "{R}",
        "cmc": 1.0,
        "rarity": Rarity.COMMON,
        "colors": "R",
        "color_identity": "R",
        "power": None,
        "toughness": None,
        "loyalty": None,
        "released_at": "1993-08-05",
        "image_uris_small": "https://example.com/small.jpg",
        "image_uris_normal": "https://example.com/normal.jpg",
        "image_uris_large": "https://example.com/large.jpg",
        "price_usd": Decimal("5.00"),
        "price_usd_foil": Decimal("15.00"),
        "price_eur": Decimal("4.50"),
        "price_tix": Decimal("0.05"),
        "price_updated_at": datetime.now(),
    }


@pytest.fixture
def sample_creature_card():
    """Sample creature card for testing."""
    return {
        "id": 2,
        "scryfall_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "oracle_id": "fffffff-gggg-hhhh-iiii-jjjjjjjjjjj",
        "name": "Grizzly Bears",
        "set_code": "LEB",
        "collector_number": "234",
        "type_line": "Creature — Bear",
        "oracle_text": "",
        "mana_cost": "{1}{G}",
        "cmc": 2.0,
        "rarity": Rarity.COMMON,
        "colors": "G",
        "color_identity": "G",
        "power": "2",
        "toughness": "2",
        "loyalty": None,
        "released_at": "1993-08-05",
        "image_uris_small": "https://example.com/bear_small.jpg",
        "image_uris_normal": "https://example.com/bear_normal.jpg",
        "image_uris_large": "https://example.com/bear_large.jpg",
        "price_usd": Decimal("2.00"),
        "price_usd_foil": Decimal("8.00"),
        "price_eur": Decimal("1.80"),
        "price_tix": Decimal("0.02"),
        "price_updated_at": datetime.now(),
    }


@pytest.fixture
def sample_collection_card_data(sample_card_data):
    """Sample collection card (card instance in collection)."""
    return {
        "id": 1,
        "collection_id": 1,
        "card_id": sample_card_data["id"],
        "quantity": 3,
        "condition": Condition.LIGHTLY_PLAYED,
        "foil": Foil.NON_FOIL,
        "language": Language.ENGLISH,
        "acquisition_date": "2023-01-15",
        "acquisition_price": Decimal("4.50"),
        "notes": "Damaged corner, slight wear",
        "manabox_id": "mbox_123456",
    }


@pytest.fixture
def sample_deck_data():
    """Sample deck data for testing."""
    return {
        "id": 1,
        "name": "Gruul Aggro",
        "format": Format.MODERN,
        "commander_id": None,
        "partner_id": None,
        "description": "Fast aggressive deck with green and red creatures",
        "is_active": True,
        "is_public": False,
        "collection_id": 1,
    }


@pytest.fixture
def sample_commander_deck_data():
    """Sample commander deck data."""
    return {
        "id": 2,
        "name": "Rhys the Redeemed",
        "format": Format.COMMANDER,
        "commander_id": 3,
        "partner_id": None,
        "description": "Token-focused commander deck",
        "is_active": True,
        "is_public": True,
        "collection_id": 1,
    }


@pytest.fixture
def sample_deck_card():
    """Sample deck card entry."""
    return {
        "id": 1,
        "deck_id": 1,
        "card_id": 2,
        "quantity": 4,
        "category": "creatures",
        "is_sideboard": False,
        "is_maybeboard": False,
    }


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary."""
    return {
        "environment": "testing",
        "debug": True,
        "log_level": "DEBUG",
        "ollama": {
            "base_url": "http://localhost:11434",
            "default_model": "llama3.2:3b",
            "timeout": 120,
            "stream_chunk_size": 512,
        },
        "database": {
            "path": "data/test.db",
            "backup_dir": "data/backups",
            "enable_wal": True,
            "timeout": 30,
        },
        "api": {
            "scryfall_base_url": "https://api.scryfall.com",
            "scryfall_rate_limit": 0.1,
            "cache_duration_hours": 24,
        },
    }


# =============================================================================
# LEGACY CSV DATA - For import/export testing
# =============================================================================

@pytest.fixture
def sample_csv_17_columns():
    """Full schema CSV (17 columns with binder info)."""
    return '''Binder Name,Binder Type,Name,Set code,Set name,Collector number,Foil,Rarity,Quantity,ManaBox ID,Scryfall ID,Purchase price,Misprint,Altered,Condition,Language,Purchase price currency
Main Collection,binder,Lightning Bolt,M21,Core Set 2021,199,normal,uncommon,4,12345,abc123,2.50,false,false,near_mint,en,USD
Trade Binder,binder,Sol Ring,CMR,Commander Legends,472,foil,uncommon,1,12346,def456,5.00,false,false,near_mint,en,USD'''


@pytest.fixture
def sample_csv_15_columns():
    """Minimal schema CSV (15 columns, no binder)."""
    return '''Name,Set code,Set name,Collector number,Foil,Rarity,Quantity,ManaBox ID,Scryfall ID,Purchase price,Misprint,Altered,Condition,Language,Purchase price currency
Lightning Bolt,M21,Core Set 2021,199,normal,uncommon,4,12345,abc123,2.50,false,false,near_mint,en,USD
Sol Ring,CMR,Commander Legends,472,foil,uncommon,1,12346,def456,5.00,false,false,near_mint,en,USD'''


# =============================================================================
# FILE FIXTURES
# =============================================================================

@pytest.fixture
def temp_csv_file_17(sample_csv_17_columns, tmp_path):
    """Create temp CSV with 17 columns."""
    csv_path = tmp_path / "test_17.csv"
    csv_path.write_text(sample_csv_17_columns, encoding='utf-8')
    return csv_path


@pytest.fixture
def temp_csv_file_15(sample_csv_15_columns, tmp_path):
    """Create temp CSV with 15 columns."""
    csv_path = tmp_path / "test_15.csv"
    csv_path.write_text(sample_csv_15_columns, encoding='utf-8')
    return csv_path


@pytest.fixture
def temp_db(tmp_path):
    """Create temp SQLite database."""
    db_path = tmp_path / "test.db"
    return db_path


@pytest.fixture
def temp_db_path(tmp_path):
    """Alias for temp_db - returns path to temporary database."""
    db_path = tmp_path / "test.db"
    return db_path


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        "model": "llama3.2:3b",
        "created_at": "2025-01-11T12:00:00.000000Z",
        "response": "Lightning Bolt is a classic Magic card...",
        "done": True,
        "context": [1, 2, 3, 4, 5],
        "total_duration": 1500000000,
        "load_duration": 500000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 100000000,
        "eval_count": 50,
        "eval_duration": 900000000,
    }


@pytest.fixture
def mock_ollama_models_response():
    """Mock response from Ollama models list endpoint."""
    return {
        "models": [
            {
                "name": "llama3.2:3b",
                "modified_at": "2025-01-10T00:00:00.000000Z",
                "size": 2147483648,
                "digest": "abc123def456",
            },
            {
                "name": "llama3.1:70b",
                "modified_at": "2025-01-09T00:00:00.000000Z",
                "size": 42949672960,
                "digest": "ghi789jkl012",
            },
        ]
    }


@pytest.fixture
def mock_scryfall():
    """Mocked Scryfall client."""
    mock = MagicMock()
    mock.get_card = AsyncMock(return_value={"name": "Lightning Bolt", "prices": {"usd": "2.50"}})
    mock.search = AsyncMock(return_value=[{"name": "Lightning Bolt"}])
    return mock


@pytest.fixture
def mock_ollama():
    """Mocked Ollama client."""
    mock = AsyncMock()
    mock.generate = AsyncMock(return_value=MagicMock(
        response='{"deck_score": 8.0, "recommendations": []}',
        eval_count=100
    ))
    mock.check_health = AsyncMock(return_value=True)
    mock.list_models = AsyncMock(return_value=[
        MagicMock(name="llama3.2:3b", size=2000000000)
    ])
    return mock


# =============================================================================
# GUI FIXTURES
# =============================================================================

@pytest.fixture
def qapp():
    """PyQt6 application for GUI tests."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app
