"""
Pytest fixtures for CardForge test suite.
"""
import pytest
import tempfile
import sqlite3
from pathlib import Path
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# SAMPLE DATA
# =============================================================================

@pytest.fixture
def sample_card_data():
    """Sample Scryfall card data."""
    return {
        "id": "abc123",
        "name": "Lightning Bolt",
        "set": "m21",
        "set_name": "Core Set 2021",
        "collector_number": "199",
        "rarity": "uncommon",
        "mana_cost": "{R}",
        "cmc": 1.0,
        "type_line": "Instant",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "colors": ["R"],
        "prices": {"usd": "2.50", "usd_foil": "5.00"}
    }


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


# =============================================================================
# MOCK FIXTURES
# =============================================================================

@pytest.fixture
def mock_scryfall():
    """Mocked Scryfall client."""
    mock = MagicMock()
    mock.get_card = AsyncMock(return_value={"name": "Lightning Bolt", "prices": {"usd": "2.50"}})
    mock.search = AsyncMock(return_value=[{"name": "Lightning Bolt"}])
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
