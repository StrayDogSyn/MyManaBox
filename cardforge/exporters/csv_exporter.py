"""
CSV Exporter for CardForge
Export collection data to CSV format (ManaBox-compatible)
"""

from pathlib import Path
from typing import Optional
import csv
from datetime import datetime

import pandas as pd

from cardforge.repositories import CollectionRepository, CardRepository
from cardforge.models import CollectionCard


class CSVExporter:
    """
    Export collection to CSV format.
    
    Exports in 17-column ManaBox-compatible format.
    """
    
    # CSV column order (17-column full schema)
    COLUMNS = [
        "Count",
        "Tradelist Count",
        "Name",
        "Edition",
        "Card Number",
        "Condition",
        "Language",
        "Foil",
        "Tags",
        "Last Modified",
        "Collector Number",
        "Alter",
        "Proxy",
        "Purchase Price",
        "Binder Name",
        "Binder Type",
        "Notes",
    ]
    
    def __init__(self):
        """Initialize exporter with repositories."""
        self.collection_repo = CollectionRepository()
        self.card_repo = CardRepository()
    
    async def export_csv(
        self,
        collection_id: int,
        output_path: Path,
        include_binder_info: bool = True,
    ) -> dict:
        """
        Export collection to CSV file.
        
        Args:
            collection_id: Collection to export
            output_path: Output file path
            include_binder_info: Include binder columns (17-column format)
            
        Returns:
            Export statistics
        """
        # Get collection cards
        collection_cards = await self.collection_repo.get_all_cards(collection_id)
        
        stats = {
            "total_cards": len(collection_cards),
            "exported": 0,
            "errors": 0,
            "output_file": str(output_path),
        }
        
        # Prepare data rows
        rows = []
        
        for cc in collection_cards:
            try:
                # Get card details
                card = await self.card_repo.get_by_id(cc.card_id)
                
                if not card:
                    stats["errors"] += 1
                    continue
                
                # Build row
                row = {
                    "Count": cc.quantity,
                    "Tradelist Count": 0,  # Not tracked yet
                    "Name": card.name,
                    "Edition": card.set_code,
                    "Card Number": card.collector_number or "",
                    "Condition": self._format_condition(cc.condition),
                    "Language": self._format_language(cc.language),
                    "Foil": "foil" if cc.foil else "",
                    "Tags": cc.tags or "",
                    "Last Modified": datetime.now().strftime("%Y-%m-%d"),
                    "Collector Number": card.collector_number or "",
                    "Alter": "",  # Not tracked
                    "Proxy": "",  # Not tracked
                    "Purchase Price": f"${cc.purchase_price:.2f}" if cc.purchase_price else "",
                }
                
                # Add binder info if requested
                if include_binder_info:
                    row["Binder Name"] = getattr(cc, "binder_name", "Default")
                    row["Binder Type"] = getattr(cc, "binder_type", "Collection")
                    row["Notes"] = getattr(cc, "notes", "")
                
                rows.append(row)
                stats["exported"] += 1
                
            except Exception as e:
                stats["errors"] += 1
                continue
        
        # Write to CSV
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        columns = self.COLUMNS if include_binder_info else self.COLUMNS[:14]
        
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(output_path, index=False)
        
        return stats
    
    def _format_condition(self, condition) -> str:
        """Format condition for CSV export."""
        condition_map = {
            "near_mint": "Near Mint",
            "lightly_played": "Lightly Played",
            "moderately_played": "Moderately Played",
            "heavily_played": "Heavily Played",
            "damaged": "Damaged",
        }
        
        condition_str = str(condition).lower() if condition else "near_mint"
        return condition_map.get(condition_str, "Near Mint")
    
    def _format_language(self, language) -> str:
        """Format language for CSV export."""
        language_map = {
            "english": "English",
            "japanese": "Japanese",
            "chinese": "Chinese",
            "korean": "Korean",
            "french": "French",
            "german": "German",
            "spanish": "Spanish",
            "italian": "Italian",
            "portuguese": "Portuguese",
            "russian": "Russian",
        }
        
        language_str = str(language).lower() if language else "english"
        return language_map.get(language_str, "English")
