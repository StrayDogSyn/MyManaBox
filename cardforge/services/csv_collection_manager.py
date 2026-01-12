"""
CSV Collection Manager Service
==============================

Provides continuous access and synchronization for CSV-based collections.
Implements a hybrid storage model with SQLite for fast reads and CSV as
the authoritative source of truth.

Features:
- File locking for safe concurrent access
- Atomic writes with temporary files
- Automatic version history with configurable retention
- Bidirectional sync (CSV <-> Database)
"""

import csv
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from cardforge.models import Collection, CollectionCard, Condition, Language
from cardforge.repositories import (
    CardRepository,
    CollectionCardRepository,
    CollectionRepository,
)
from cardforge.utils.file_locking import FileLock, FileLockError

logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    """Statistics from a sync operation."""
    total_rows: int = 0
    imported: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    warnings: List[str] = field(default_factory=list)
    duration_ms: float = 0.0


@dataclass 
class ManagerConfig:
    """Configuration for CsvCollectionManager."""
    history_retention: int = 10
    lock_timeout: float = 30.0
    lock_retry_interval: float = 0.1
    auto_sync_on_write: bool = True
    create_backup_on_sync: bool = True


class CsvCollectionManager:
    """
    Manages a specific CSV file as a persistent collection.
    
    Provides a hybrid storage model:
    - **Reads**: Served from SQLite for millisecond-latency queries
    - **Writes**: Applied to SQLite first, then synced to CSV
    - **CSV**: Remains the authoritative "source of truth"
    
    Thread Safety:
        Uses file-based locking to prevent concurrent write corruption.
        Multiple readers are allowed; writers acquire exclusive locks.
    
    Example:
        ```python
        manager = CsvCollectionManager("data/my_collection.csv")
        await manager.initialize()
        
        # Fast queries from SQLite
        cards = await manager.query(foil="foil", condition="NM")
        
        # Writes sync to both DB and CSV
        await manager.add_card(scryfall_id="abc123", quantity=4)
        ```
    """
    
    # CSV column definitions for Moxfield format
    CSV_COLUMNS = [
        "Count", "Tradelist Count", "Name", "Edition", "Card Number",
        "Condition", "Language", "Foil", "Tags", "Last Modified",
        "Collector Number", "Alter", "Proxy", "Purchase Price",
        "Binder Name", "Binder Type", "Notes"
    ]
    
    def __init__(
        self,
        file_path: Union[str, Path],
        collection_id: Optional[int] = None,
        config: Optional[ManagerConfig] = None,
    ):
        """
        Initialize the CSV Collection Manager.
        
        Args:
            file_path: Path to the target CSV file.
            collection_id: ID of the internal collection to sync with.
                          If None, derives from filename or creates new.
            config: Optional configuration overrides.
        """
        self.file_path = Path(file_path).resolve()
        self.history_dir = self.file_path.parent / "history"
        self.collection_id = collection_id
        self.config = config or ManagerConfig()
        
        # Repositories (lazy initialization)
        self._collection_repo: Optional[CollectionRepository] = None
        self._card_repo: Optional[CollectionCardRepository] = None
        self._card_master_repo: Optional[CardRepository] = None
        
        # State
        self._initialized = False
        self._collection_name: Optional[str] = None
        
    @property
    def collection_repo(self) -> CollectionRepository:
        if self._collection_repo is None:
            self._collection_repo = CollectionRepository()
        return self._collection_repo
    
    @property
    def card_repo(self) -> CollectionCardRepository:
        if self._card_repo is None:
            self._card_repo = CollectionCardRepository()
        return self._card_repo
    
    @property
    def card_master_repo(self) -> CardRepository:
        if self._card_master_repo is None:
            self._card_master_repo = CardRepository()
        return self._card_master_repo

    # =========================================================================
    # Initialization & Lifecycle
    # =========================================================================
    
    async def initialize(self) -> SyncStats:
        """
        Initialize the manager and perform initial synchronization.
        
        This method:
        1. Creates necessary directories (history, etc.)
        2. Resolves or creates the collection in the database
        3. Syncs CSV -> DB if file exists, or creates empty CSV
        
        Returns:
            SyncStats from the initial sync operation.
            
        Raises:
            FileNotFoundError: If file_path directory doesn't exist.
            FileLockError: If unable to acquire lock during sync.
        """
        if self._initialized:
            logger.warning("Manager already initialized, skipping")
            return SyncStats()
        
        logger.info(f"Initializing CsvCollectionManager for: {self.file_path}")
        
        # Ensure directories exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Resolve collection
        await self._resolve_collection()
        
        # Initial sync
        stats = SyncStats()
        if self.file_path.exists():
            stats = await self.sync_from_csv()
            logger.info(f"Synced {stats.imported} cards from CSV to database")
        else:
            # Create empty CSV with headers
            await self._write_csv_headers()
            logger.info(f"Created new CSV file: {self.file_path}")
        
        self._initialized = True
        return stats
    
    async def _resolve_collection(self) -> None:
        """Resolve or create the collection in the database."""
        if self.collection_id:
            collection = await self.collection_repo.get(self.collection_id)
            if collection:
                self._collection_name = collection.name
                return
        
        # Derive name from filename
        self._collection_name = self.file_path.stem
        
        # Try to find existing collection
        collection = await self.collection_repo.get_by_name(self._collection_name)
        
        if not collection:
            # Create new collection
            collection = Collection(
                name=self._collection_name,
                description=f"Managed CSV collection: {self.file_path.name}",
                is_default=False,
            )
            collection = await self.collection_repo.create(collection)
            logger.info(f"Created new collection: {self._collection_name} (ID: {collection.id})")
        
        self.collection_id = collection.id
    
    async def _write_csv_headers(self) -> None:
        """Write CSV file with headers only."""
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.CSV_COLUMNS)
            writer.writeheader()

    # =========================================================================
    # Synchronization Operations
    # =========================================================================
    
    async def sync_from_csv(self) -> SyncStats:
        """
        Synchronize from CSV file to Database (CSV is source of truth).
        
        This operation:
        1. Acquires file lock
        2. Reads and parses CSV
        3. Clears existing collection data in DB
        4. Imports all rows from CSV
        
        Returns:
            SyncStats with import statistics.
            
        Raises:
            FileLockError: If unable to acquire lock.
            FileNotFoundError: If CSV file doesn't exist.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        
        start_time = datetime.now()
        stats = SyncStats()
        
        lock = FileLock(
            self.file_path,
            timeout=self.config.lock_timeout,
            retry_interval=self.config.lock_retry_interval,
        )
        
        try:
            lock.acquire()
            logger.info(f"Syncing from CSV: {self.file_path}")
            
            # Read CSV
            df = pd.read_csv(self.file_path)
            stats.total_rows = len(df)
            
            if stats.total_rows == 0:
                logger.info("CSV is empty, nothing to sync")
                return stats
            
            # Clear existing collection data (replace mode)
            await self._clear_collection()
            
            # Import each row
            for idx, row in df.iterrows():
                try:
                    await self._import_csv_row(row, idx + 2)  # +2 for 1-indexed + header
                    stats.imported += 1
                except Exception as e:
                    stats.errors += 1
                    stats.warnings.append(f"Row {idx + 2}: {str(e)}")
                    logger.warning(f"Error importing row {idx + 2}: {e}")
            
        finally:
            lock.release()
        
        stats.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"CSV sync complete: {stats.imported}/{stats.total_rows} imported, "
            f"{stats.errors} errors in {stats.duration_ms:.1f}ms"
        )
        
        return stats
    
    async def sync_to_csv(self) -> SyncStats:
        """
        Synchronize from Database to CSV file.
        
        This operation:
        1. Acquires file lock
        2. Creates version backup (if enabled)
        3. Exports DB collection to temporary file
        4. Atomically replaces CSV with temp file
        
        Returns:
            SyncStats with export statistics.
            
        Raises:
            FileLockError: If unable to acquire lock.
        """
        start_time = datetime.now()
        stats = SyncStats()
        
        lock = FileLock(
            self.file_path,
            timeout=self.config.lock_timeout,
            retry_interval=self.config.lock_retry_interval,
        )
        
        temp_path = self.file_path.with_suffix('.csv.tmp')
        
        try:
            lock.acquire()
            logger.info(f"Syncing to CSV: {self.file_path}")
            
            # Create version backup
            if self.config.create_backup_on_sync and self.file_path.exists():
                self._create_version_backup()
            
            # Get all cards from DB
            cards = await self.card_repo.get_with_card_data(self.collection_id, limit=100000)
            stats.total_rows = len(cards)
            
            # Write to temp file
            rows = []
            for cc in cards:
                try:
                    row = self._collection_card_to_csv_row(cc)
                    rows.append(row)
                    stats.imported += 1
                except Exception as e:
                    stats.errors += 1
                    stats.warnings.append(f"Card {cc.id}: {str(e)}")
            
            # Write CSV
            df = pd.DataFrame(rows, columns=self.CSV_COLUMNS)
            df.to_csv(temp_path, index=False)
            
            # Atomic replace
            if temp_path.exists():
                # On Windows, need to remove target first
                if os.name == 'nt' and self.file_path.exists():
                    self.file_path.unlink()
                temp_path.replace(self.file_path)
                
        except Exception as e:
            logger.error(f"Failed to sync to CSV: {e}")
            if temp_path.exists():
                temp_path.unlink()
            raise
            
        finally:
            lock.release()
        
        stats.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(
            f"CSV export complete: {stats.imported} cards written in {stats.duration_ms:.1f}ms"
        )
        
        return stats
    
    async def _clear_collection(self) -> None:
        """Clear all cards from the collection in the database."""
        cards = await self.card_repo.get_by_collection(self.collection_id, limit=100000)
        for card in cards:
            await self.card_repo.delete(card.id)
    
    async def _import_csv_row(self, row: pd.Series, line_num: int) -> None:
        """Import a single CSV row into the database."""
        name = str(row.get("Name", "")).strip()
        set_code = str(row.get("Edition", "")).strip().upper()
        if not set_code:
            set_code = str(row.get("Set code", "")).strip().upper()
        
        if not name:
            raise ValueError(f"Missing card name at line {line_num}")
        
        # Find card in master database
        card = await self.card_master_repo.get_by_name(name, set_code)
        
        if not card:
            # Create placeholder for unknown cards
            from cardforge.models import Card
            card = Card(
                name=name,
                set_code=set_code,
                collector_number=str(row.get("Card Number", "") or row.get("Collector Number", "")),
                scryfall_id=None,
                oracle_text="",
                type_line="Unknown",
                mana_cost="",
                cmc=0,
                colors=[],
                color_identity=[],
                rarity="common",
                prices={},
            )
            card = await self.card_master_repo.create(card)
        
        # Parse collection card attributes
        quantity = int(row.get("Count", 1) or 1)
        foil_str = str(row.get("Foil", "")).lower()
        foil = "foil" if foil_str in ("foil", "true", "1", "yes") else "normal"
        
        condition = self._parse_condition(str(row.get("Condition", "Near Mint")))
        language = self._parse_language(str(row.get("Language", "English")))
        
        purchase_price = None
        price_str = str(row.get("Purchase Price", ""))
        if price_str and price_str != "nan":
            try:
                purchase_price = Decimal(price_str.replace("$", "").replace(",", "").strip())
            except (ValueError, TypeError):
                pass
        
        # Create collection card entry
        await self.card_repo.add_card(
            collection_id=self.collection_id,
            card_id=card.id,
            quantity=quantity,
            foil=foil,
            condition=condition,
            language=language,
            purchase_price=purchase_price,
        )
    
    def _collection_card_to_csv_row(self, cc: CollectionCard) -> Dict[str, Any]:
        """Convert a CollectionCard to a CSV row dictionary."""
        card = cc.card if hasattr(cc, 'card') and cc.card else None
        
        return {
            "Count": cc.quantity,
            "Tradelist Count": 0,
            "Name": card.name if card else "Unknown",
            "Edition": card.set_code if card else "",
            "Card Number": card.collector_number if card else "",
            "Condition": self._format_condition(cc.condition),
            "Language": self._format_language(cc.language),
            "Foil": "foil" if cc.foil == "foil" else "",
            "Tags": getattr(cc, 'tags', "") or "",
            "Last Modified": datetime.now().strftime("%Y-%m-%d"),
            "Collector Number": card.collector_number if card else "",
            "Alter": "",
            "Proxy": "",
            "Purchase Price": f"${cc.purchase_price:.2f}" if cc.purchase_price else "",
            "Binder Name": getattr(cc, 'binder_name', "Default") or "Default",
            "Binder Type": getattr(cc, 'binder_type', "Collection") or "Collection",
            "Notes": getattr(cc, 'notes', "") or "",
        }

    # =========================================================================
    # Version Control & History
    # =========================================================================
    
    def _create_version_backup(self) -> Path:
        """Create a timestamped backup of the current CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{self.file_path.stem}_{timestamp}{self.file_path.suffix}"
        version_path = self.history_dir / version_name
        
        shutil.copy2(self.file_path, version_path)
        logger.debug(f"Created version backup: {version_path}")
        
        # Cleanup old versions
        self._cleanup_history()
        
        return version_path
    
    def _cleanup_history(self) -> None:
        """Remove old versions beyond retention limit."""
        pattern = f"{self.file_path.stem}_*{self.file_path.suffix}"
        versions = sorted(self.history_dir.glob(pattern))
        
        if len(versions) > self.config.history_retention:
            for old_version in versions[:-self.config.history_retention]:
                try:
                    old_version.unlink()
                    logger.debug(f"Removed old version: {old_version}")
                except OSError as e:
                    logger.warning(f"Failed to remove old version {old_version}: {e}")
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """
        Get list of available version backups.
        
        Returns:
            List of dicts with 'path', 'timestamp', 'size_bytes' keys.
        """
        pattern = f"{self.file_path.stem}_*{self.file_path.suffix}"
        versions = sorted(self.history_dir.glob(pattern), reverse=True)
        
        result = []
        for v in versions:
            stat = v.stat()
            result.append({
                'path': v,
                'filename': v.name,
                'timestamp': datetime.fromtimestamp(stat.st_mtime),
                'size_bytes': stat.st_size,
            })
        
        return result
    
    async def restore_version(self, version_path: Union[str, Path]) -> SyncStats:
        """
        Restore collection from a historical version.
        
        Args:
            version_path: Path to the version file to restore.
            
        Returns:
            SyncStats from the restore operation.
        """
        version_path = Path(version_path)
        
        if not version_path.exists():
            raise FileNotFoundError(f"Version file not found: {version_path}")
        
        # Backup current before restore
        self._create_version_backup()
        
        # Copy version to main file
        shutil.copy2(version_path, self.file_path)
        
        # Sync to DB
        return await self.sync_from_csv()

    # =========================================================================
    # CRUD Operations (Atomic: DB Update + CSV Sync)
    # =========================================================================
    
    async def add_card(
        self,
        scryfall_id: Optional[str] = None,
        card_name: Optional[str] = None,
        set_code: Optional[str] = None,
        quantity: int = 1,
        foil: str = "normal",
        condition: str = "NM",
        language: str = "en",
        purchase_price: Optional[Decimal] = None,
        **kwargs,
    ) -> Optional[CollectionCard]:
        """
        Add a card to the collection.
        
        Args:
            scryfall_id: Scryfall ID of the card (preferred).
            card_name: Card name (used if scryfall_id not provided).
            set_code: Set code (used with card_name).
            quantity: Number of copies to add.
            foil: Foil status ("normal", "foil", "etched").
            condition: Card condition (NM, LP, MP, HP, DMG).
            language: Language code.
            purchase_price: Purchase price per card.
            **kwargs: Additional attributes.
            
        Returns:
            Created CollectionCard or None if card not found.
        """
        self._ensure_initialized()
        
        # Find the card
        card = None
        if scryfall_id:
            card = await self.card_master_repo.get_by_scryfall_id(scryfall_id)
        elif card_name:
            card = await self.card_master_repo.get_by_name_and_set(card_name, set_code or "")
        
        if not card:
            logger.error(f"Card not found: scryfall_id={scryfall_id}, name={card_name}")
            return None
        
        # Add to collection
        cc = await self.card_repo.add_card(
            collection_id=self.collection_id,
            card_id=card.id,
            quantity=quantity,
            foil=foil,
            condition=condition,
            language=language,
            purchase_price=purchase_price,
        )
        
        # Sync to CSV
        if self.config.auto_sync_on_write:
            await self.sync_to_csv()
        
        return cc
    
    async def remove_card(self, collection_card_id: int) -> bool:
        """
        Remove a card from the collection.
        
        Args:
            collection_card_id: ID of the CollectionCard entry to remove.
            
        Returns:
            True if removed successfully.
        """
        self._ensure_initialized()
        
        success = await self.card_repo.delete(collection_card_id)
        
        if success and self.config.auto_sync_on_write:
            await self.sync_to_csv()
        
        return success
    
    async def update_card(
        self,
        collection_card_id: int,
        quantity: Optional[int] = None,
        foil: Optional[str] = None,
        condition: Optional[str] = None,
        **kwargs,
    ) -> Optional[CollectionCard]:
        """
        Update a card in the collection.
        
        Args:
            collection_card_id: ID of the CollectionCard to update.
            quantity: New quantity (removes if 0).
            foil: New foil status.
            condition: New condition.
            **kwargs: Additional attributes to update.
            
        Returns:
            Updated CollectionCard or None if not found.
        """
        self._ensure_initialized()
        
        cc = await self.card_repo.get(collection_card_id)
        if not cc:
            return None
        
        # Handle quantity=0 as removal
        if quantity is not None and quantity <= 0:
            await self.remove_card(collection_card_id)
            return None
        
        # Update fields
        if quantity is not None:
            cc.quantity = quantity
        if foil is not None:
            cc.foil = foil
        if condition is not None:
            cc.condition = condition
        
        for key, value in kwargs.items():
            if hasattr(cc, key):
                setattr(cc, key, value)
        
        updated = await self.card_repo.update(cc)
        
        if self.config.auto_sync_on_write:
            await self.sync_to_csv()
        
        return updated
    
    async def bulk_import(
        self,
        csv_path: Union[str, Path],
        merge: bool = False,
    ) -> SyncStats:
        """
        Bulk import cards from another CSV file.
        
        Args:
            csv_path: Path to CSV file to import.
            merge: If True, merge with existing; if False, replace.
            
        Returns:
            SyncStats from the import operation.
        """
        self._ensure_initialized()
        
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Import file not found: {csv_path}")
        
        # Backup current state
        if self.file_path.exists():
            self._create_version_backup()
        
        if not merge:
            await self._clear_collection()
        
        # Read and import
        start_time = datetime.now()
        stats = SyncStats()
        
        df = pd.read_csv(csv_path)
        stats.total_rows = len(df)
        
        for idx, row in df.iterrows():
            try:
                await self._import_csv_row(row, idx + 2)
                stats.imported += 1
            except Exception as e:
                stats.errors += 1
                stats.warnings.append(f"Row {idx + 2}: {str(e)}")
        
        # Sync to main CSV
        await self.sync_to_csv()
        
        stats.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return stats

    # =========================================================================
    # Query Interface (Fast reads from SQLite)
    # =========================================================================
    
    async def get_all_cards(self, limit: int = 10000) -> List[CollectionCard]:
        """
        Get all cards in the collection.
        
        Args:
            limit: Maximum number of cards to return.
            
        Returns:
            List of CollectionCard objects.
        """
        self._ensure_initialized()
        return await self.card_repo.get_by_collection(self.collection_id, limit=limit)
    
    async def get_cards_with_data(self, limit: int = 10000) -> List[CollectionCard]:
        """
        Get all cards with full card data loaded.
        
        Args:
            limit: Maximum number of cards to return.
            
        Returns:
            List of CollectionCard objects with card attribute populated.
        """
        self._ensure_initialized()
        return await self.card_repo.get_with_card_data(self.collection_id, limit=limit)
    
    async def query(
        self,
        name: Optional[str] = None,
        set_code: Optional[str] = None,
        foil: Optional[str] = None,
        condition: Optional[str] = None,
        min_quantity: Optional[int] = None,
        **kwargs,
    ) -> List[CollectionCard]:
        """
        Query cards with filters.
        
        Args:
            name: Filter by card name (partial match).
            set_code: Filter by set code.
            foil: Filter by foil status.
            condition: Filter by condition.
            min_quantity: Minimum quantity.
            **kwargs: Additional attribute filters.
            
        Returns:
            List of matching CollectionCard objects.
        """
        self._ensure_initialized()
        
        # Get all cards with data for filtering
        cards = await self.card_repo.get_with_card_data(self.collection_id, limit=100000)
        
        filtered = []
        for cc in cards:
            # Name filter (partial match)
            if name and cc.card:
                if name.lower() not in cc.card.name.lower():
                    continue
            
            # Set code filter
            if set_code and cc.card:
                if cc.card.set_code.upper() != set_code.upper():
                    continue
            
            # Foil filter
            if foil is not None and cc.foil != foil:
                continue
            
            # Condition filter
            if condition is not None and cc.condition != condition:
                continue
            
            # Quantity filter
            if min_quantity is not None and cc.quantity < min_quantity:
                continue
            
            # Additional kwargs filters
            match = True
            for key, value in kwargs.items():
                if hasattr(cc, key) and getattr(cc, key) != value:
                    match = False
                    break
            
            if match:
                filtered.append(cc)
        
        return filtered
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dictionary with collection statistics.
        """
        self._ensure_initialized()
        
        cards = await self.card_repo.get_by_collection(self.collection_id, limit=100000)
        total_value = await self.card_repo.get_total_value(self.collection_id)
        
        unique_cards = len(cards)
        total_quantity = sum(c.quantity for c in cards)
        foil_count = sum(c.quantity for c in cards if c.foil == "foil")
        
        return {
            'collection_id': self.collection_id,
            'collection_name': self._collection_name,
            'csv_path': str(self.file_path),
            'unique_cards': unique_cards,
            'total_cards': total_quantity,
            'foil_count': foil_count,
            'total_value': total_value,
            'history_versions': len(self.get_version_history()),
        }

    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _ensure_initialized(self) -> None:
        """Raise error if manager not initialized."""
        if not self._initialized:
            raise RuntimeError(
                "CsvCollectionManager not initialized. Call initialize() first."
            )
    
    @staticmethod
    def _parse_condition(value: str) -> str:
        """Parse condition string to standard format."""
        if pd.isna(value) or not value:
            return "NM"
        
        value_lower = str(value).lower().strip()
        condition_map = {
            "near mint": "NM", "nm": "NM",
            "lightly played": "LP", "lp": "LP",
            "moderately played": "MP", "mp": "MP",
            "heavily played": "HP", "hp": "HP",
            "damaged": "DMG", "dmg": "DMG",
        }
        return condition_map.get(value_lower, "NM")
    
    @staticmethod
    def _format_condition(value: str) -> str:
        """Format condition for CSV export."""
        condition_map = {
            "NM": "Near Mint", "nm": "Near Mint",
            "LP": "Lightly Played", "lp": "Lightly Played",
            "MP": "Moderately Played", "mp": "Moderately Played",
            "HP": "Heavily Played", "hp": "Heavily Played",
            "DMG": "Damaged", "dmg": "Damaged",
        }
        return condition_map.get(str(value).upper(), "Near Mint")
    
    @staticmethod
    def _parse_language(value: str) -> str:
        """Parse language string to code."""
        if pd.isna(value) or not value:
            return "en"
        
        value_lower = str(value).lower().strip()
        lang_map = {
            "english": "en", "en": "en",
            "japanese": "ja", "ja": "ja",
            "chinese": "zh", "zh": "zh",
            "korean": "ko", "ko": "ko",
            "french": "fr", "fr": "fr",
            "german": "de", "de": "de",
            "spanish": "es", "es": "es",
            "italian": "it", "it": "it",
            "portuguese": "pt", "pt": "pt",
            "russian": "ru", "ru": "ru",
        }
        return lang_map.get(value_lower, "en")
    
    @staticmethod
    def _format_language(value: str) -> str:
        """Format language code for CSV export."""
        lang_map = {
            "en": "English", "ja": "Japanese", "zh": "Chinese",
            "ko": "Korean", "fr": "French", "de": "German",
            "es": "Spanish", "it": "Italian", "pt": "Portuguese",
            "ru": "Russian",
        }
        return lang_map.get(str(value).lower(), "English")
    
    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"<CsvCollectionManager(path={self.file_path}, collection_id={self.collection_id}, {status})>"
