"""
CSV Collection Manager Service
Provides continuous access and synchronization for CSV-based collections.
"""

import logging
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from cardforge.utils.file_locking import FileLock
from cardforge.importers.csv_importer import CSVImporter, CSVSchema
from cardforge.exporters.csv_exporter import CSVExporter
from cardforge.repositories import CollectionRepository, CardRepository, CollectionCardRepository
from cardforge.models import Collection, CollectionCard
from cardforge.database import get_transaction

logger = logging.getLogger(__name__)

class CsvCollectionManager:
    """
    Manages a specific CSV file as a persistent collection.
    Ensures synchronization between the CSV file and the internal database.
    """
    
    def __init__(self, file_path: Union[str, Path], collection_id: Optional[int] = None):
        """
        Initialize the manager.
        
        Args:
            file_path: Path to the target CSV file.
            collection_id: ID of the internal collection to sync with. 
                           If None, attempts to find by name derived from filename.
        """
        self.file_path = Path(file_path)
        self.history_dir = self.file_path.parent / "history"
        self.collection_id = collection_id
        
        self.importer = CSVImporter()
        self.exporter = CSVExporter()
        self.repo = CollectionRepository()
        self.card_repo = CollectionCardRepository()
        
        # Ensure directories exist
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self) -> None:
        """
        Initialize the connection.
        - Verifies/creates the CSV file.
        - Resolves collection ID.
        - Performs initial sync (CSV -> DB).
        """
        # Resolve collection ID
        if not self.collection_id:
            coll_name = self.file_path.stem
            collection = await self.repo.get_by_name(coll_name)
            if not collection:
                collection = await self.repo.create(Collection(name=coll_name))
            self.collection_id = collection.id
            
        # If file doesn't exist, create it from DB (if DB has data) or empty
        if not self.file_path.exists():
            await self.sync_to_csv()
        else:
            # File exists, sync IN to DB
            await self.sync_from_csv()
            
    async def sync_from_csv(self) -> Dict[str, Any]:
        """
        Synchronize from CSV file to Database.
        This is the "Read" operation.
        """
        with FileLock(self.file_path):
            logger.info(f"Syncing from CSV: {self.file_path}")
            
            # Use existing importer logic
            # We use 'replace' mode (merge=False) to ensure DB exactly matches CSV
            stats = await self.importer.import_csv(
                self.file_path,
                self.collection_id,
                merge=False,
                backup=False # We handle our own versioning
            )
            return stats

    async def sync_to_csv(self) -> None:
        """
        Synchronize from Database to CSV file.
        This is the "Write" operation.
        """
        with FileLock(self.file_path):
            logger.info(f"Syncing to CSV: {self.file_path}")
            
            # Create versioned backup before overwriting
            if self.file_path.exists():
                self._create_version()
            
            # Write new content atomically
            temp_path = self.file_path.with_suffix('.tmp')
            try:
                # Use exporter logic to write to temp file
                await self.exporter.export_csv(self.collection_id, temp_path)
                
                # Atomic replace
                if temp_path.exists():
                    temp_path.replace(self.file_path)
                    
            except Exception as e:
                logger.error(f"Failed to sync to CSV: {e}")
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def _create_version(self) -> None:
        """Create a timestamped copy of the current CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{self.file_path.stem}_v{timestamp}{self.file_path.suffix}"
        version_path = self.history_dir / version_name
        
        shutil.copy2(self.file_path, version_path)
        
        # Cleanup old versions (keep last 10)
        self._cleanup_history()

    def _cleanup_history(self) -> None:
        """Keep only the last 10 versions."""
        files = sorted(self.history_dir.glob(f"{self.file_path.stem}_v*{self.file_path.suffix}"))
        if len(files) > 10:
            for f in files[:-10]:
                try:
                    f.unlink()
                except OSError:
                    pass

    # =========================================================================
    # CRUD Operations (Atomic: DB Update + Sync Out)
    # =========================================================================

    async def add_card(self, scryfall_id: str, quantity: int = 1, **kwargs) -> bool:
        """Add a card and sync to CSV."""
        from cardforge.repositories import CardRepository
        
        # 1. Update DB
        async with get_transaction() as conn:
            card_repo = CardRepository()
            card = await card_repo.get_by_scryfall_id(scryfall_id)
            if not card:
                logger.error(f"Card {scryfall_id} not found")
                return False
                
            await self.card_repo.add_card(
                collection_id=self.collection_id,
                card_id=card.id,
                quantity=quantity,
                **kwargs
            )
            
        # 2. Sync to CSV
        await self.sync_to_csv()
        return True

    async def remove_card(self, collection_card_id: int) -> bool:
        """Remove a card and sync to CSV."""
        # 1. Update DB
        success = await self.card_repo.delete(collection_card_id)
        
        # 2. Sync to CSV if successful
        if success:
            await self.sync_to_csv()
            
        return success
        
    async def update_quantity(self, collection_card_id: int, quantity: int) -> bool:
        """Update card quantity and sync to CSV."""
        card = await self.card_repo.get(collection_card_id)
        if not card:
            return False
            
        card.quantity = quantity
        await self.card_repo.update(card)
        
        await self.sync_to_csv()
        return True

    # =========================================================================
    # Query Interface (Proxies to DB for speed)
    # =========================================================================
    
    async def get_all_cards(self) -> List[CollectionCard]:
        """Get all cards in the collection."""
        return await self.card_repo.get_by_collection(self.collection_id)
        
    async def query(self, **filters) -> List[CollectionCard]:
        """Query cards with filters."""
        # This assumes CollectionCardRepository has a robust filter method
        # If not, we fall back to get_by_collection and filter in python
        # But for 'comprehensive' system, we'd ideally enhance the repo.
        # For now, we use what we have.
        cards = await self.card_repo.get_by_collection(self.collection_id)
        
        # Simple in-memory filtering for now
        filtered = []
        for c in cards:
            match = True
            for k, v in filters.items():
                if not hasattr(c, k) or getattr(c, k) != v:
                    match = False
                    break
            if match:
                filtered.append(c)
        return filtered
