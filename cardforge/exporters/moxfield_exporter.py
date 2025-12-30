"""
Moxfield Exporter
Export decks and collections to Moxfield format
"""

from pathlib import Path
from typing import Optional
import csv

from cardforge.repositories import DeckRepository, CardRepository, CollectionRepository
from cardforge.models import Deck


class MoxfieldExporter:
    """
    Export to Moxfield format.
    
    Moxfield CSV format:
    Count,Name,Edition,Condition,Language,Foil,Tags,Collector Number,Purchase Price
    """
    
    def __init__(self):
        """Initialize exporter with repositories."""
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
        self.collection_repo = CollectionRepository()
    
    async def export_deck(
        self,
        deck_id: int,
        output_path: Path,
    ) -> dict:
        """
        Export deck to Moxfield CSV format.
        
        Args:
            deck_id: Deck to export
            output_path: Output file path
            
        Returns:
            Export statistics
        """
        # Get deck
        deck = await self.deck_repo.get_by_id(deck_id)
        
        if not deck:
            raise ValueError(f"Deck {deck_id} not found")
        
        # Get deck cards
        deck_cards = await self.deck_repo.get_deck_cards(deck_id)
        
        stats = {
            "deck_name": deck.name,
            "total_cards": len(deck_cards),
            "exported": 0,
            "errors": 0,
            "output_file": str(output_path),
        }
        
        # Prepare CSV rows
        rows = []
        
        for dc in deck_cards:
            try:
                card = await self.card_repo.get_by_id(dc.card_id)
                
                if not card:
                    stats["errors"] += 1
                    continue
                
                row = {
                    "Count": dc.quantity,
                    "Name": card.name,
                    "Edition": card.set_code,
                    "Condition": "Near Mint",
                    "Language": "English",
                    "Foil": "",
                    "Tags": dc.category or "",
                    "Collector Number": card.collector_number or "",
                    "Purchase Price": "",
                }
                
                rows.append(row)
                stats["exported"] += 1
                
            except Exception:
                stats["errors"] += 1
                continue
        
        # Write CSV
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        
        return stats
    
    async def export_collection(
        self,
        collection_id: int,
        output_path: Path,
    ) -> dict:
        """
        Export collection to Moxfield CSV format.
        
        Args:
            collection_id: Collection to export
            output_path: Output file path
            
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
        
        # Prepare CSV rows
        rows = []
        
        for cc in collection_cards:
            try:
                card = await self.card_repo.get_by_id(cc.card_id)
                
                if not card:
                    stats["errors"] += 1
                    continue
                
                row = {
                    "Count": cc.quantity,
                    "Name": card.name,
                    "Edition": card.set_code,
                    "Condition": self._format_condition(cc.condition),
                    "Language": self._format_language(cc.language),
                    "Foil": "foil" if cc.foil else "",
                    "Tags": cc.tags or "",
                    "Collector Number": card.collector_number or "",
                    "Purchase Price": f"${cc.purchase_price:.2f}" if cc.purchase_price else "",
                }
                
                rows.append(row)
                stats["exported"] += 1
                
            except Exception:
                stats["errors"] += 1
                continue
        
        # Write CSV
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if rows:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        
        return stats
    
    def _format_condition(self, condition) -> str:
        """Format condition for Moxfield."""
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
        """Format language for Moxfield."""
        return str(language).capitalize() if language else "English"
