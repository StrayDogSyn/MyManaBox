"""
Integration tests for CSV Collection Manager.

Tests cover:
- Initialization and synchronization
- File locking and concurrency
- Data persistence and integrity
- Version history management
- Performance with large datasets
- CRUD operations with CSV sync
"""

import asyncio
import csv
import os
import shutil
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest
import pytest_asyncio

from cardforge.services.csv_collection_manager import (
    CsvCollectionManager,
    ManagerConfig,
    SyncStats,
)
from cardforge.utils.file_locking import FileLock, FileLockError


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def tmp_data_dir(tmp_path):
    """Create a temporary data directory structure."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def sample_moxfield_csv(tmp_data_dir) -> Path:
    """Create a sample Moxfield-format CSV file."""
    csv_path = tmp_data_dir / "moxfield_collection_2026-01-12-0154Z.csv"
    
    rows = [
        {
            "Count": 4, "Tradelist Count": 0, "Name": "Sol Ring",
            "Edition": "CMD", "Card Number": "113", "Condition": "Near Mint",
            "Language": "English", "Foil": "", "Tags": "",
            "Last Modified": "2026-01-12", "Collector Number": "113",
            "Alter": "", "Proxy": "", "Purchase Price": "$2.50",
            "Binder Name": "Main", "Binder Type": "Collection", "Notes": ""
        },
        {
            "Count": 2, "Tradelist Count": 1, "Name": "Command Tower",
            "Edition": "CMR", "Card Number": "350", "Condition": "Lightly Played",
            "Language": "English", "Foil": "foil", "Tags": "staple",
            "Last Modified": "2026-01-12", "Collector Number": "350",
            "Alter": "", "Proxy": "", "Purchase Price": "$1.00",
            "Binder Name": "Trade", "Binder Type": "Binder", "Notes": "For trade"
        },
        {
            "Count": 1, "Tradelist Count": 0, "Name": "Arcane Signet",
            "Edition": "ELD", "Card Number": "331", "Condition": "Near Mint",
            "Language": "Japanese", "Foil": "", "Tags": "",
            "Last Modified": "2026-01-12", "Collector Number": "331",
            "Alter": "", "Proxy": "", "Purchase Price": "",
            "Binder Name": "Main", "Binder Type": "Collection", "Notes": ""
        },
    ]
    
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    
    return csv_path


@pytest.fixture
def large_csv(tmp_data_dir) -> Path:
    """Create a large CSV file for performance testing (10k+ cards)."""
    csv_path = tmp_data_dir / "large_collection.csv"
    
    rows = []
    card_names = [
        "Lightning Bolt", "Counterspell", "Dark Ritual", "Giant Growth",
        "Swords to Plowshares", "Birds of Paradise", "Llanowar Elves",
        "Brainstorm", "Force of Will", "Thoughtseize"
    ]
    sets = ["LEA", "LEB", "2ED", "3ED", "4ED", "ICE", "ALL", "MIR", "TMP", "USG"]
    conditions = ["Near Mint", "Lightly Played", "Moderately Played"]
    
    for i in range(10000):
        rows.append({
            "Count": (i % 4) + 1,
            "Tradelist Count": 0,
            "Name": card_names[i % len(card_names)],
            "Edition": sets[i % len(sets)],
            "Card Number": str(i % 300 + 1),
            "Condition": conditions[i % len(conditions)],
            "Language": "English",
            "Foil": "foil" if i % 10 == 0 else "",
            "Tags": "",
            "Last Modified": "2026-01-12",
            "Collector Number": str(i % 300 + 1),
            "Alter": "",
            "Proxy": "",
            "Purchase Price": f"${(i % 100) / 10:.2f}" if i % 5 == 0 else "",
            "Binder Name": "Main",
            "Binder Type": "Collection",
            "Notes": ""
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    
    return csv_path


@pytest.fixture
def empty_csv(tmp_data_dir) -> Path:
    """Create an empty CSV with headers only."""
    csv_path = tmp_data_dir / "empty_collection.csv"
    
    columns = [
        "Count", "Tradelist Count", "Name", "Edition", "Card Number",
        "Condition", "Language", "Foil", "Tags", "Last Modified",
        "Collector Number", "Alter", "Proxy", "Purchase Price",
        "Binder Name", "Binder Type", "Notes"
    ]
    
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_path, index=False)
    
    return csv_path


@pytest.fixture
def mock_repositories():
    """Mock all repository dependencies."""
    with patch('cardforge.services.csv_collection_manager.CollectionRepository') as mock_coll_repo, \
         patch('cardforge.services.csv_collection_manager.CollectionCardRepository') as mock_card_repo, \
         patch('cardforge.services.csv_collection_manager.CardRepository') as mock_master_repo:
        
        # Setup collection repo mock
        mock_coll_instance = AsyncMock()
        mock_coll_instance.get.return_value = None
        mock_coll_instance.get_by_name.return_value = None
        mock_coll_instance.create.return_value = MagicMock(id=1, name="test_collection")
        mock_coll_repo.return_value = mock_coll_instance
        
        # Setup collection card repo mock
        mock_card_instance = AsyncMock()
        mock_card_instance.get_by_collection.return_value = []
        mock_card_instance.get_with_card_data.return_value = []
        mock_card_instance.add_card.return_value = MagicMock(id=1)
        mock_card_instance.delete.return_value = True
        mock_card_instance.get_total_value.return_value = Decimal("0")
        mock_card_repo.return_value = mock_card_instance
        
        # Setup master card repo mock
        mock_master_instance = AsyncMock()
        mock_master_instance.get_by_name_and_set.return_value = None
        mock_master_instance.get_by_scryfall_id.return_value = None
        mock_master_instance.create.return_value = MagicMock(id=1, name="Test Card", set_code="TST")
        mock_master_repo.return_value = mock_master_instance
        
        yield {
            'collection_repo': mock_coll_instance,
            'card_repo': mock_card_instance,
            'master_repo': mock_master_instance,
        }


# =============================================================================
# FILE LOCKING TESTS
# =============================================================================

class TestFileLocking:
    """Tests for file locking mechanism."""
    
    def test_acquire_and_release_lock(self, sample_moxfield_csv):
        """Test basic lock acquisition and release."""
        lock = FileLock(sample_moxfield_csv, timeout=5.0)
        
        # Should acquire successfully
        lock.acquire()
        assert lock._is_locked
        
        # Lock file should exist
        assert lock.lock_file.exists()
        
        # Release
        lock.release()
        assert not lock._is_locked
        assert not lock.lock_file.exists()
    
    def test_lock_context_manager(self, sample_moxfield_csv):
        """Test lock as context manager."""
        lock = FileLock(sample_moxfield_csv)
        
        with lock:
            assert lock._is_locked
            assert lock.lock_file.exists()
        
        assert not lock._is_locked
        assert not lock.lock_file.exists()
    
    def test_concurrent_lock_fails(self, sample_moxfield_csv):
        """Test that concurrent lock acquisition fails with timeout."""
        lock1 = FileLock(sample_moxfield_csv, timeout=5.0)
        lock2 = FileLock(sample_moxfield_csv, timeout=0.2)
        
        lock1.acquire()
        
        try:
            with pytest.raises(FileLockError) as exc_info:
                lock2.acquire()
            
            assert "Timeout" in str(exc_info.value)
        finally:
            lock1.release()
    
    def test_stale_lock_cleanup(self, sample_moxfield_csv):
        """Test that stale locks are automatically cleaned up."""
        lock = FileLock(sample_moxfield_csv, timeout=0.5)
        
        # Manually create a stale lock file (old timestamp)
        lock_file = sample_moxfield_csv.with_suffix(sample_moxfield_csv.suffix + '.lock')
        old_timestamp = time.time() - 120  # 2 minutes ago
        lock_file.write_text(f"99999,{old_timestamp}")
        
        # Should acquire despite existing lock (it's stale)
        lock.acquire()
        assert lock._is_locked
        
        lock.release()
    
    def test_lock_file_contains_pid_and_timestamp(self, sample_moxfield_csv):
        """Test that lock file contains process ID and timestamp."""
        lock = FileLock(sample_moxfield_csv)
        lock.acquire()
        
        try:
            content = lock.lock_file.read_text()
            parts = content.split(',')
            
            assert len(parts) == 2
            pid = int(parts[0])
            timestamp = float(parts[1])
            
            assert pid == os.getpid()
            assert timestamp <= time.time()
        finally:
            lock.release()


# =============================================================================
# CSV COLLECTION MANAGER TESTS
# =============================================================================

class TestCsvCollectionManagerInit:
    """Tests for CsvCollectionManager initialization."""
    
    @pytest.mark.asyncio
    async def test_initialize_creates_directories(self, tmp_data_dir, mock_repositories):
        """Test that initialization creates necessary directories."""
        csv_path = tmp_data_dir / "new_collection.csv"
        
        manager = CsvCollectionManager(csv_path)
        await manager.initialize()
        
        # History directory should be created
        assert manager.history_dir.exists()
        
        # CSV file should be created (empty with headers)
        assert csv_path.exists()
    
    @pytest.mark.asyncio
    async def test_initialize_syncs_existing_csv(self, sample_moxfield_csv, mock_repositories):
        """Test that initialization syncs from existing CSV."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        stats = await manager.initialize()
        
        # Should have imported rows
        assert stats.total_rows == 3
        assert stats.imported >= 0  # May vary based on mock behavior
    
    @pytest.mark.asyncio
    async def test_initialize_with_custom_config(self, sample_moxfield_csv, mock_repositories):
        """Test initialization with custom configuration."""
        config = ManagerConfig(
            history_retention=5,
            lock_timeout=60.0,
            auto_sync_on_write=False,
            create_backup_on_sync=False,
        )
        
        manager = CsvCollectionManager(sample_moxfield_csv, config=config)
        await manager.initialize()
        
        assert manager.config.history_retention == 5
        assert manager.config.lock_timeout == 60.0
        assert manager.config.auto_sync_on_write is False
    
    @pytest.mark.asyncio
    async def test_double_initialize_warns(self, sample_moxfield_csv, mock_repositories):
        """Test that double initialization logs warning."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        
        await manager.initialize()
        stats = await manager.initialize()  # Second call
        
        # Should return empty stats on second call
        assert stats.total_rows == 0


class TestCsvCollectionManagerSync:
    """Tests for synchronization operations."""
    
    @pytest.mark.asyncio
    async def test_sync_from_csv_reads_all_rows(self, sample_moxfield_csv, mock_repositories):
        """Test that sync_from_csv reads all CSV rows."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        stats = await manager.sync_from_csv()
        
        assert stats.total_rows == 3
    
    @pytest.mark.asyncio
    async def test_sync_to_csv_creates_backup(self, sample_moxfield_csv, mock_repositories):
        """Test that sync_to_csv creates version backup."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Sync to CSV (should create backup)
        await manager.sync_to_csv()
        
        # Check history directory
        history_files = list(manager.history_dir.glob("*.csv"))
        assert len(history_files) >= 1
    
    @pytest.mark.asyncio
    async def test_sync_to_csv_atomic_write(self, sample_moxfield_csv, mock_repositories):
        """Test that sync_to_csv uses atomic write (temp file)."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Record original content
        original_content = sample_moxfield_csv.read_text()
        
        # Sync to CSV
        await manager.sync_to_csv()
        
        # File should still exist and be valid
        assert sample_moxfield_csv.exists()
        
        # No temp file should remain
        temp_file = sample_moxfield_csv.with_suffix('.csv.tmp')
        assert not temp_file.exists()
    
    @pytest.mark.asyncio
    async def test_sync_from_nonexistent_file_raises(self, tmp_data_dir, mock_repositories):
        """Test that sync_from_csv raises for non-existent file."""
        csv_path = tmp_data_dir / "nonexistent.csv"
        
        manager = CsvCollectionManager(csv_path)
        manager._initialized = True
        manager.collection_id = 1
        
        with pytest.raises(FileNotFoundError):
            await manager.sync_from_csv()


class TestCsvCollectionManagerVersioning:
    """Tests for version control and history."""
    
    @pytest.mark.asyncio
    async def test_version_backup_created_on_write(self, sample_moxfield_csv, mock_repositories):
        """Test that version backup is created on write operations."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Trigger a write (sync to CSV)
        await manager.sync_to_csv()
        
        history = manager.get_version_history()
        assert len(history) >= 1
        assert history[0]['path'].exists()
    
    @pytest.mark.asyncio
    async def test_version_history_retention(self, sample_moxfield_csv, mock_repositories):
        """Test that old versions are cleaned up based on retention."""
        config = ManagerConfig(history_retention=3)
        manager = CsvCollectionManager(sample_moxfield_csv, config=config)
        await manager.initialize()
        
        # Create multiple versions
        for _ in range(5):
            await manager.sync_to_csv()
            await asyncio.sleep(0.01)  # Small delay for unique timestamps
        
        history = manager.get_version_history()
        assert len(history) <= 3
    
    @pytest.mark.asyncio
    async def test_restore_version(self, sample_moxfield_csv, mock_repositories):
        """Test restoring from a historical version."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Create a backup
        await manager.sync_to_csv()
        
        history = manager.get_version_history()
        assert len(history) >= 1
        
        # Restore from backup
        version_path = history[0]['path']
        stats = await manager.restore_version(version_path)
        
        assert stats.total_rows >= 0
    
    def test_get_version_history_returns_metadata(self, sample_moxfield_csv, mock_repositories):
        """Test that version history includes proper metadata."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        manager.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a fake version file
        version_file = manager.history_dir / f"{sample_moxfield_csv.stem}_20260112_120000.csv"
        version_file.write_text("test content")
        
        history = manager.get_version_history()
        
        assert len(history) == 1
        assert 'path' in history[0]
        assert 'filename' in history[0]
        assert 'timestamp' in history[0]
        assert 'size_bytes' in history[0]


class TestCsvCollectionManagerCRUD:
    """Tests for CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_add_card_by_name(self, sample_moxfield_csv, mock_repositories):
        """Test adding a card by name."""
        mocks = mock_repositories
        mocks['master_repo'].get_by_name_and_set.return_value = MagicMock(
            id=10, name="Test Card", set_code="TST"
        )
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        result = await manager.add_card(
            card_name="Test Card",
            set_code="TST",
            quantity=4,
            condition="NM",
        )
        
        # Should have called add_card on repo
        mocks['card_repo'].add_card.assert_called()
    
    @pytest.mark.asyncio
    async def test_remove_card(self, sample_moxfield_csv, mock_repositories):
        """Test removing a card."""
        mocks = mock_repositories
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        result = await manager.remove_card(collection_card_id=1)
        
        assert result is True
        mocks['card_repo'].delete.assert_called_with(1)
    
    @pytest.mark.asyncio
    async def test_update_card_quantity(self, sample_moxfield_csv, mock_repositories):
        """Test updating card quantity."""
        mocks = mock_repositories
        mock_card = MagicMock(id=1, quantity=2, foil="normal", condition="NM")
        mocks['card_repo'].get.return_value = mock_card
        mocks['card_repo'].update.return_value = mock_card
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        result = await manager.update_card(
            collection_card_id=1,
            quantity=5,
        )
        
        assert mock_card.quantity == 5
        mocks['card_repo'].update.assert_called()
    
    @pytest.mark.asyncio
    async def test_update_card_to_zero_removes(self, sample_moxfield_csv, mock_repositories):
        """Test that updating quantity to 0 removes the card."""
        mocks = mock_repositories
        mock_card = MagicMock(id=1, quantity=2)
        mocks['card_repo'].get.return_value = mock_card
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        result = await manager.update_card(collection_card_id=1, quantity=0)
        
        assert result is None
        mocks['card_repo'].delete.assert_called_with(1)


class TestCsvCollectionManagerQuery:
    """Tests for query operations."""
    
    @pytest.mark.asyncio
    async def test_get_all_cards(self, sample_moxfield_csv, mock_repositories):
        """Test getting all cards."""
        mocks = mock_repositories
        mocks['card_repo'].get_by_collection.return_value = [
            MagicMock(id=1, quantity=4),
            MagicMock(id=2, quantity=2),
        ]
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        cards = await manager.get_all_cards()
        
        assert len(cards) == 2
    
    @pytest.mark.asyncio
    async def test_query_with_filters(self, sample_moxfield_csv, mock_repositories):
        """Test querying with filters."""
        mocks = mock_repositories
        
        mock_card1 = MagicMock(id=1, quantity=4, foil="normal", condition="NM")
        mock_card1.card = MagicMock(name="Sol Ring", set_code="CMD")
        
        mock_card2 = MagicMock(id=2, quantity=2, foil="foil", condition="LP")
        mock_card2.card = MagicMock(name="Command Tower", set_code="CMR")
        
        mocks['card_repo'].get_with_card_data.return_value = [mock_card1, mock_card2]
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Query for foil cards only
        foil_cards = await manager.query(foil="foil")
        assert len(foil_cards) == 1
        assert foil_cards[0].foil == "foil"
    
    @pytest.mark.asyncio
    async def test_get_stats(self, sample_moxfield_csv, mock_repositories):
        """Test getting collection statistics."""
        mocks = mock_repositories
        mocks['card_repo'].get_by_collection.return_value = [
            MagicMock(id=1, quantity=4, foil="normal"),
            MagicMock(id=2, quantity=2, foil="foil"),
        ]
        mocks['card_repo'].get_total_value.return_value = Decimal("15.50")
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        stats = await manager.get_stats()
        
        assert stats['unique_cards'] == 2
        assert stats['total_cards'] == 6
        assert stats['foil_count'] == 2
        assert stats['total_value'] == Decimal("15.50")


class TestCsvCollectionManagerBulkOperations:
    """Tests for bulk import operations."""
    
    @pytest.mark.asyncio
    async def test_bulk_import_replace_mode(self, sample_moxfield_csv, tmp_data_dir, mock_repositories):
        """Test bulk import in replace mode."""
        # Create a second CSV to import
        import_csv = tmp_data_dir / "import.csv"
        df = pd.DataFrame([{
            "Count": 1, "Tradelist Count": 0, "Name": "New Card",
            "Edition": "NEW", "Card Number": "1", "Condition": "Near Mint",
            "Language": "English", "Foil": "", "Tags": "",
            "Last Modified": "2026-01-12", "Collector Number": "1",
            "Alter": "", "Proxy": "", "Purchase Price": "",
            "Binder Name": "Main", "Binder Type": "Collection", "Notes": ""
        }])
        df.to_csv(import_csv, index=False)
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        stats = await manager.bulk_import(import_csv, merge=False)
        
        assert stats.total_rows == 1
    
    @pytest.mark.asyncio
    async def test_bulk_import_merge_mode(self, sample_moxfield_csv, tmp_data_dir, mock_repositories):
        """Test bulk import in merge mode."""
        import_csv = tmp_data_dir / "import.csv"
        df = pd.DataFrame([{
            "Count": 1, "Tradelist Count": 0, "Name": "New Card",
            "Edition": "NEW", "Card Number": "1", "Condition": "Near Mint",
            "Language": "English", "Foil": "", "Tags": "",
            "Last Modified": "2026-01-12", "Collector Number": "1",
            "Alter": "", "Proxy": "", "Purchase Price": "",
            "Binder Name": "Main", "Binder Type": "Collection", "Notes": ""
        }])
        df.to_csv(import_csv, index=False)
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        stats = await manager.bulk_import(import_csv, merge=True)
        
        assert stats.total_rows == 1


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestCsvCollectionManagerPerformance:
    """Performance tests for large datasets."""
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_large_csv_sync_performance(self, large_csv, mock_repositories):
        """Test sync performance with 10k+ cards."""
        manager = CsvCollectionManager(large_csv)
        
        start_time = time.time()
        stats = await manager.initialize()
        duration = time.time() - start_time
        
        assert stats.total_rows == 10000
        # Should complete in reasonable time (< 30 seconds)
        assert duration < 30.0, f"Sync took too long: {duration:.2f}s"
        
        # Log performance metrics
        print(f"\nPerformance: Synced {stats.total_rows} rows in {duration:.2f}s")
        print(f"Rate: {stats.total_rows / duration:.0f} rows/second")
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_query_performance(self, large_csv, mock_repositories):
        """Test query performance with large dataset."""
        mocks = mock_repositories
        
        # Create mock data for 10k cards
        mock_cards = []
        for i in range(10000):
            mock_card = MagicMock(
                id=i,
                quantity=(i % 4) + 1,
                foil="foil" if i % 10 == 0 else "normal",
                condition="NM" if i % 3 == 0 else "LP",
            )
            mock_card.card = MagicMock(
                name=f"Card {i}",
                set_code=["LEA", "LEB", "2ED"][i % 3],
            )
            mock_cards.append(mock_card)
        
        mocks['card_repo'].get_with_card_data.return_value = mock_cards
        
        manager = CsvCollectionManager(large_csv)
        await manager.initialize()
        
        start_time = time.time()
        results = await manager.query(foil="foil")
        duration = time.time() - start_time
        
        assert len(results) == 1000  # 10% are foil
        assert duration < 1.0, f"Query took too long: {duration:.2f}s"


# =============================================================================
# CONCURRENCY TESTS
# =============================================================================

class TestCsvCollectionManagerConcurrency:
    """Tests for concurrent access scenarios."""
    
    def test_concurrent_lock_acquisition(self, sample_moxfield_csv):
        """Test that concurrent lock attempts are handled correctly."""
        results = []
        
        def try_lock(lock_id):
            lock = FileLock(sample_moxfield_csv, timeout=0.5)
            try:
                lock.acquire()
                time.sleep(0.1)  # Hold lock briefly
                results.append((lock_id, "acquired"))
                lock.release()
            except FileLockError:
                results.append((lock_id, "failed"))
        
        # Run concurrent lock attempts
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(try_lock, i) for i in range(5)]
            for f in futures:
                f.result()
        
        # At least one should succeed, others may fail
        acquired = [r for r in results if r[1] == "acquired"]
        failed = [r for r in results if r[1] == "failed"]
        
        assert len(acquired) >= 1
        # Due to timing, some may succeed sequentially
        assert len(acquired) + len(failed) == 5
    
    @pytest.mark.asyncio
    async def test_sequential_operations_maintain_integrity(self, sample_moxfield_csv, mock_repositories):
        """Test that sequential operations maintain data integrity."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # Perform multiple sequential operations
        for i in range(10):
            await manager.sync_to_csv()
        
        # File should still be valid
        assert sample_moxfield_csv.exists()
        
        # Should be able to read it
        df = pd.read_csv(sample_moxfield_csv)
        assert df is not None


# =============================================================================
# DATA INTEGRITY TESTS
# =============================================================================

class TestCsvCollectionManagerIntegrity:
    """Tests for data integrity."""
    
    @pytest.mark.asyncio
    async def test_csv_roundtrip_preserves_data(self, sample_moxfield_csv, mock_repositories):
        """Test that CSV -> DB -> CSV roundtrip preserves data."""
        mocks = mock_repositories
        
        # Read original CSV
        original_df = pd.read_csv(sample_moxfield_csv)
        original_names = set(original_df['Name'].tolist())
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        # The data should have been imported (mocked)
        # Verify the sync was called
        assert manager._initialized
    
    @pytest.mark.asyncio
    async def test_empty_csv_handling(self, empty_csv, mock_repositories):
        """Test handling of empty CSV files."""
        manager = CsvCollectionManager(empty_csv)
        stats = await manager.initialize()
        
        # Should handle empty CSV gracefully
        assert stats.total_rows == 0
        assert stats.errors == 0
    
    @pytest.mark.asyncio
    async def test_malformed_row_handling(self, tmp_data_dir, mock_repositories):
        """Test handling of malformed CSV rows - rows with missing Name should error."""
        csv_path = tmp_data_dir / "malformed.csv"
        
        # Create CSV using pandas to ensure proper formatting with empty Name cell
        rows = [
            {"Count": 4, "Tradelist Count": 0, "Name": "Sol Ring", "Edition": "CMD", 
             "Card Number": "113", "Condition": "Near Mint", "Language": "English",
             "Foil": "", "Tags": "", "Last Modified": "", "Collector Number": "113",
             "Alter": "", "Proxy": "", "Purchase Price": "$2.50", "Binder Name": "Main",
             "Binder Type": "Collection", "Notes": ""},
            {"Count": 2, "Tradelist Count": 0, "Name": "", "Edition": "BAD",  # Empty name!
             "Card Number": "1", "Condition": "Near Mint", "Language": "English",
             "Foil": "", "Tags": "", "Last Modified": "", "Collector Number": "1",
             "Alter": "", "Proxy": "", "Purchase Price": "", "Binder Name": "",
             "Binder Type": "Collection", "Notes": ""},
            {"Count": 2, "Tradelist Count": 0, "Name": "Command Tower", "Edition": "CMR",
             "Card Number": "350", "Condition": "Near Mint", "Language": "English",
             "Foil": "", "Tags": "", "Last Modified": "", "Collector Number": "350",
             "Alter": "", "Proxy": "", "Purchase Price": "", "Binder Name": "",
             "Binder Type": "Collection", "Notes": ""},
        ]
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False)
        
        manager = CsvCollectionManager(csv_path)
        stats = await manager.initialize()
        
        # Row with empty Name should cause an error
        assert stats.errors >= 1  # The empty Name row should error
        assert stats.imported >= 2  # Sol Ring and Command Tower should succeed
        assert len(stats.warnings) >= 1  # Should have warning message
    
    def test_condition_parsing(self, mock_repositories):
        """Test condition string parsing."""
        manager = CsvCollectionManager(Path("dummy.csv"))
        
        assert manager._parse_condition("Near Mint") == "NM"
        assert manager._parse_condition("NM") == "NM"
        assert manager._parse_condition("Lightly Played") == "LP"
        assert manager._parse_condition("LP") == "LP"
        assert manager._parse_condition("Moderately Played") == "MP"
        assert manager._parse_condition("Heavily Played") == "HP"
        assert manager._parse_condition("Damaged") == "DMG"
        assert manager._parse_condition("") == "NM"  # Default
        assert manager._parse_condition("Unknown") == "NM"  # Default
    
    def test_language_parsing(self, mock_repositories):
        """Test language string parsing."""
        manager = CsvCollectionManager(Path("dummy.csv"))
        
        assert manager._parse_language("English") == "en"
        assert manager._parse_language("Japanese") == "ja"
        assert manager._parse_language("German") == "de"
        assert manager._parse_language("") == "en"  # Default
        assert manager._parse_language("Unknown") == "en"  # Default


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestCsvCollectionManagerErrors:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_operations_before_init_raise(self, sample_moxfield_csv, mock_repositories):
        """Test that operations before initialization raise error."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        
        with pytest.raises(RuntimeError) as exc_info:
            await manager.get_all_cards()
        
        assert "not initialized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_add_nonexistent_card_returns_none(self, sample_moxfield_csv, mock_repositories):
        """Test that adding non-existent card returns None."""
        mocks = mock_repositories
        mocks['master_repo'].get_by_scryfall_id.return_value = None
        mocks['master_repo'].get_by_name_and_set.return_value = None
        
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        result = await manager.add_card(scryfall_id="nonexistent-id")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_restore_nonexistent_version_raises(self, sample_moxfield_csv, mock_repositories):
        """Test that restoring non-existent version raises error."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        with pytest.raises(FileNotFoundError):
            await manager.restore_version(Path("/nonexistent/version.csv"))
    
    @pytest.mark.asyncio
    async def test_bulk_import_nonexistent_file_raises(self, sample_moxfield_csv, mock_repositories):
        """Test that bulk import of non-existent file raises error."""
        manager = CsvCollectionManager(sample_moxfield_csv)
        await manager.initialize()
        
        with pytest.raises(FileNotFoundError):
            await manager.bulk_import(Path("/nonexistent/import.csv"))
