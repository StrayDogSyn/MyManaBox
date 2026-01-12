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
        from cardforge.repositories import CardRepository, CollectionCardRepository
        
        self.card_repo = CardRepository()
        self.collection_repo = CollectionCardRepository()
        
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
            stats["backup_path"] = await self._create_backup(collection_id)
        
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
                error_msg = f"Row {idx + 2}: {str(e)}"
                stats["warnings"].append(error_msg)
                # Debug: Print first error
                if stats["errors"] == 1:
                    import traceback
                    print(f"DEBUG First import error:\n{traceback.format_exc()}")
        
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
        
        # Ensure card.id is set before using it
        if not card or not card.id:
            raise ValueError(f"Failed to create card: {name} ({set_code})")
        
        # Parse collection card data (normalize enums to raw values for storage)
        quantity = int(row.get("Count", 1))
        foil = self._parse_foil(row.get("Foil", ""))
        condition_enum = self._parse_condition(row.get("Condition", "Near Mint"))
        condition = condition_enum.value if hasattr(condition_enum, "value") else str(condition_enum)
        language_enum = self._parse_language(row.get("Language", "English"))
        language = language_enum.value if hasattr(language_enum, "value") else str(language_enum)
        
        # Optional fields
        purchase_price = self._parse_price(row.get("Purchase Price"))
        tags = row.get("Tags", "")
        
        # Save to database with upsert semantics to handle duplicate rows gracefully
        await self.collection_repo.add_card(
            collection_id=collection_id,
            card_id=card.id,
            quantity=quantity,
            foil=foil,
            condition=condition,
            language=language,
            purchase_price=purchase_price,
        )
    
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
        import uuid
        from cardforge.database import get_connection
        
        # Ensure set exists (required by FOREIGN KEY)
        async with get_connection() as conn:
            # Check if set exists
            cursor = await conn.execute(
                "SELECT code FROM sets WHERE code = ? LIMIT 1",
                (set_code.upper(),)
            )
            existing_set = await cursor.fetchone()
            
            if not existing_set:
                # Create placeholder set
                await conn.execute(
                    "INSERT INTO sets (code, name) VALUES (?, ?)",
                    (set_code.upper(), f"Set {set_code.upper()}")
                )
                await conn.commit()
        
        # Generate a temporary UUID for placeholder cards
        # Will be replaced with real Scryfall ID during enrichment
        temp_id = f"placeholder-{uuid.uuid4().hex[:12]}"
        
        card = Card(
            name=name,
            set_code=set_code.upper(),
            collector_number=collector_number,
            scryfall_id=temp_id,  # Will be filled by enrichment
            oracle_text="",
            type_line="",
            mana_cost="",
            cmc=0,
            colors=[],
            color_identity=[],
            rarity="common",
        )
        
        return await self.card_repo.create(card)
    
    def _parse_foil(self, value: str) -> str:
        """Parse foil status from CSV and return as string."""
        if pd.isna(value):
            return "normal"
        value_str = str(value).lower().strip()
        if value_str in ("foil", "true", "1", "yes"):
            return "foil"
        return "normal"
    
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
            "german": Language.GERMAN,
            "de": Language.GERMAN,
            "french": Language.FRENCH,
            "fr": Language.FRENCH,
            "italian": Language.ITALIAN,
            "it": Language.ITALIAN,
            "spanish": Language.SPANISH,
            "es": Language.SPANISH,
            "portuguese": Language.PORTUGUESE,
            "pt": Language.PORTUGUESE,
            "japanese": Language.JAPANESE,
            "ja": Language.JAPANESE,
            "korean": Language.KOREAN,
            "ko": Language.KOREAN,
            "russian": Language.RUSSIAN,
            "ru": Language.RUSSIAN,
            "chinese": Language.CHINESE_SIMPLIFIED,
            "zh": Language.CHINESE_SIMPLIFIED,
            "chinese simplified": Language.CHINESE_SIMPLIFIED,
            "zhs": Language.CHINESE_SIMPLIFIED,
            "chinese traditional": Language.CHINESE_TRADITIONAL,
            "zht": Language.CHINESE_TRADITIONAL,
            "phyrexian": Language.PHYREXIAN,
            "ph": Language.PHYREXIAN,
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
