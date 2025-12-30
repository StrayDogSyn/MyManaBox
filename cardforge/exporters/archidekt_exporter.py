"""
Archidekt Exporter
Export decks to Archidekt format
"""

from pathlib import Path
from typing import Optional

from cardforge.repositories import DeckRepository, CardRepository


class ArchidektExporter:
    """
    Export to Archidekt format.
    
    Archidekt uses a simple text format:
    <quantity> <card name>
    """
    
    def __init__(self):
        """Initialize exporter with repositories."""
        self.deck_repo = DeckRepository()
        self.card_repo = CardRepository()
    
    async def export_deck(
        self,
        deck_id: int,
        output_path: Path,
        include_categories: bool = True,
    ) -> dict:
        """
        Export deck to Archidekt text format.
        
        Args:
            deck_id: Deck to export
            output_path: Output file path
            include_categories: Include category headers
            
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
        
        # Group by category if requested
        if include_categories:
            categorized = {}
            for dc in deck_cards:
                category = dc.category or "Main Deck"
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(dc)
        else:
            categorized = {"Main Deck": deck_cards}
        
        # Build output lines
        lines = []
        
        # Add commander if present
        if deck.commander_id:
            commander = await self.card_repo.get_by_id(deck.commander_id)
            if commander:
                lines.append(f"Commander:\n1 {commander.name}\n")
        
        # Add cards by category
        for category, cards in categorized.items():
            if include_categories and category != "Commander":
                lines.append(f"\n{category}:\n")
            
            for dc in cards:
                try:
                    card = await self.card_repo.get_by_id(dc.card_id)
                    
                    if not card:
                        stats["errors"] += 1
                        continue
                    
                    lines.append(f"{dc.quantity} {card.name}\n")
                    stats["exported"] += 1
                    
                except Exception:
                    stats["errors"] += 1
                    continue
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        return stats
