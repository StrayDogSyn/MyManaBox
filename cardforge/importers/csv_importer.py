"""
CSV Importer for CardForge
Handles both 15-column and 17-column ManaBox CSV schemas
"""

from pathlib import Path
from typing import Optional
from enum import Enum
import csv
from decimal import Decimal
from datetime import datetime

import pandas as pd

from cardforge.models import Card, CollectionCard, Condition, Language
from cardforge.repositories import CardRepository, CollectionRepository


class CSVSchema(Enum):
    """CSV schema versions."""
    FULL_17_COLUMN = "full_17"  # With Binder Name, Binder Type
    MINIMAL_15_COLUMN = "minimal_15"  # Without Binder columns
    MOXFIELD_SIMPLE = "moxfield_simple" # Basic Moxfield columns
    UNKNOWN = "unknown"


def detect_csv_schema(file_path: Path) -> CSVSchema:
    """
    Auto-detect CSV schema version.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Detected schema type
    """
    try:
        df = pd.read_csv(file_path, nrows=1)
        columns = set(df.columns)
        
        # Check for binder columns (17-column schema)
        if "Binder Name" in columns and "Binder Type" in columns:
            return CSVSchema.FULL_17_COLUMN
        elif len(df.columns) >= 15:
            return CSVSchema.MINIMAL_15_COLUMN
        elif "Name" in columns and ("Edition" in columns or "Set code" in columns) and "Count" in columns:
            return CSVSchema.MOXFIELD_SIMPLE
        else:
            return CSVSchema.UNKNOWN
            
    except Exception:
        return CSVSchema.UNKNOWN


class CSVImporter:
    """
    Import MTG cards from CSV files.
    
    Supports both ManaBox export schemas:
    - 17 columns (full): Includes Binder Name, Binder Type
    - 15 columns (minimal): No Binder columns
    """
    
    # Standard column mappings
    COLUMN_MAP_17 = {
        "Count": "quantity",
        "Tradelist Count": "tradelist_count",
        "Name": "name",
        "Edition": "set_code",
        "Card Number": "collector_number",
        "Condition": "condition",
        "Language": "language",
        "Foil": "foil",
        "Tags": "tags",
        "Last Modified": "last_modified",
        "Collector Number": "collector_number",
        "Alter": "alter",
        "Proxy": "proxy",
        "Purchase Price": "purchase_price",
        "Binder Name": "binder_name",
        "Binder Type": "binder_type",
    }
    
    COLUMN_MAP_15 = {
        "Count": "quantity",
        "Tradelist Count": "tradelist_count",
        "Name": "name",
        "Edition": "set_code",
        "Card Number": "collector_number",
        "Condition": "condition",
        "Language": "language",
        "Foil": "foil",
        "Tags": "tags",
        "Last Modified": "last_modified",
        "Collector Number": "collector_number",
        "Alter": "alter",
        "Proxy": "proxy",
        "Purchase Price": "purchase_price",
    }
    
    def __init__(self):
        """Initialize importer with repositories."""
        self.card_repo = CardRepository()
        self.collection_repo = CollectionRepository()
        
    async def import_csv(
        self,
        file_path: Path,
        collection_id: int,
        merge: bool = False,
        backup: bool = True,
    ) -> dict:
        """
        Import cards from CSV file.
        
        Args:
            file_path: Path to CSV file
            collection_id: Target collection ID
            merge: If True, merge with existing data; if False, replace
            backup: Create backup before import
            
        Returns:
            Import statistics dictionary
        """
        # Detect schema
        schema = detect_csv_schema(file_path)
        
        if schema == CSVSchema.UNKNOWN:
            raise ValueError(f"Unknown CSV schema in {file_path}")
        
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Statistics
        stats = {
            "total_rows": len(df),
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "schema": schema.value,
            "warnings": [],
        }
        
        # Backup if requested
        if backup and not merge:
            await self._create_backup(collection_id)
        
        # Clear collection if not merging
        if not merge:
            await self.collection_repo.clear_collection(collection_id)
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                await self._import_row(row, collection_id, schema)
                stats["imported"] += 1
            except Exception as e:
                stats["errors"] += 1
                stats["warnings"].append(f"Row {idx + 2}: {str(e)}")
        
        return stats
    
    async def _import_row(
        self,
        row: pd.Series,
        collection_id: int,
        schema: CSVSchema,
    ) -> None:
        """
        Import a single CSV row.
        
        Args:
            row: Pandas Series representing CSV row
            collection_id: Target collection ID
            schema: Detected schema type
        """
        # Extract card data
        name = row.get("Name", "").strip()
        set_code = row.get("Edition", "").strip().upper()
        if not set_code:
            set_code = row.get("Set code", "").strip().upper()
            
        collector_number = str(row.get("Card Number", "")).strip()
        if not collector_number:
            collector_number = str(row.get("Collector Number", "")).strip()
        
        if not name:
            raise ValueError("Card name is required")
        
        # Get or create card in database
        card = await self.card_repo.get_by_name(name, set_code)
        
        if not card:
            # Card not in cache - need to fetch from Scryfall
            # For now, create placeholder
            card = await self._create_placeholder_card(name, set_code, collector_number)
        
        # Parse collection card data
        quantity = int(row.get("Count", 1))
        foil = self._parse_foil(row.get("Foil", ""))
        condition = self._parse_condition(row.get("Condition", "Near Mint"))
        language = self._parse_language(row.get("Language", "English"))
        
        # Optional fields
        purchase_price = self._parse_price(row.get("Purchase Price"))
        tags = row.get("Tags", "")
        
        # Schema-specific fields
        if schema == CSVSchema.FULL_17_COLUMN:
            binder_name = row.get("Binder Name", "Default")
            binder_type = row.get("Binder Type", "Collection")
        else:
            binder_name = "Default"
            binder_type = "Collection"
        
        # Create collection card entry
        collection_card = CollectionCard(
            card_id=card.id,
            collection_id=collection_id,
            quantity=quantity,
            foil=foil,
            condition=condition,
            language=language,
            purchase_price=purchase_price,
            tags=tags,
            binder_name=binder_name,
            acquired_date=datetime.now(),
        )
        
        # Save to database
        await self.collection_repo.add_card(collection_card)
    
    async def _create_placeholder_card(
        self,
        name: str,
        set_code: str,
        collector_number: str,
    ) -> Card:
        """
        Create placeholder card for cards not yet in Scryfall cache.
        
        Args:
            name: Card name
            set_code: Set code
            collector_number: Collector number
            
        Returns:
            Created card object
        """
        card = Card(
            name=name,
            set_code=set_code,
            collector_number=collector_number,
            scryfall_id=None,  # Will be filled by enrichment
            oracle_text="",
            type_line="",
            mana_cost="",
            cmc=0,
            colors=[],
            color_identity=[],
            rarity="common",
            prices={},
        )
        
        return await self.card_repo.create(card)
    
    def _parse_foil(self, value: str) -> bool:
        """Parse foil status from CSV."""
        if pd.isna(value):
            return False
        value_str = str(value).lower().strip()
        return value_str in ("foil", "true", "1", "yes")
    
    def _parse_condition(self, value: str) -> Condition:
        """Parse condition from CSV."""
        if pd.isna(value):
            return Condition.NEAR_MINT
        
        value_str = str(value).lower().strip()
        condition_map = {
            "near mint": Condition.NEAR_MINT,
            "nm": Condition.NEAR_MINT,
            "lightly played": Condition.LIGHTLY_PLAYED,
            "lp": Condition.LIGHTLY_PLAYED,
            "moderately played": Condition.MODERATELY_PLAYED,
            "mp": Condition.MODERATELY_PLAYED,
            "heavily played": Condition.HEAVILY_PLAYED,
            "hp": Condition.HEAVILY_PLAYED,
            "damaged": Condition.DAMAGED,
            "dmg": Condition.DAMAGED,
        }
        
        return condition_map.get(value_str, Condition.NEAR_MINT)
    
    def _parse_language(self, value: str) -> Language:
        """Parse language from CSV."""
        if pd.isna(value):
            return Language.ENGLISH
        
        value_str = str(value).lower().strip()
        language_map = {
            "english": Language.ENGLISH,
            "en": Language.ENGLISH,
            "japanese": Language.JAPANESE,
            "ja": Language.JAPANESE,
            "chinese": Language.CHINESE,
            "zh": Language.CHINESE,
            "korean": Language.KOREAN,
            "ko": Language.KOREAN,
            "french": Language.FRENCH,
            "fr": Language.FRENCH,
            "german": Language.GERMAN,
            "de": Language.GERMAN,
            "spanish": Language.SPANISH,
            "es": Language.SPANISH,
            "italian": Language.ITALIAN,
            "it": Language.ITALIAN,
            "portuguese": Language.PORTUGUESE,
            "pt": Language.PORTUGUESE,
            "russian": Language.RUSSIAN,
            "ru": Language.RUSSIAN,
        }
        
        return language_map.get(value_str, Language.ENGLISH)
    
    def _parse_price(self, value) -> Optional[Decimal]:
        """Parse purchase price from CSV."""
        if pd.isna(value):
            return None
        
        try:
            # Remove currency symbols and convert
            value_str = str(value).replace("$", "").replace(",", "").strip()
            return Decimal(value_str) if value_str else None
        except (ValueError, TypeError):
            return None
    
    async def _create_backup(self, collection_id: int) -> Path:
        """
        Create backup of collection before import.
        
        Args:
            collection_id: Collection to backup
            
        Returns:
            Path to backup file
        """
        from cardforge.exporters import CSVExporter
        
        exporter = CSVExporter()
        backup_dir = Path("data/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"collection_{collection_id}_backup_{timestamp}.csv"
        
        await exporter.export_csv(collection_id, backup_path)
        
        return backup_path
