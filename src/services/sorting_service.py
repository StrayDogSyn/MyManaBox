"""Sorting service for organizing collections."""

from typing import Dict, List, Optional
from ..models import Collection, Card
from ..data import CSVLoader


class SortingService:
    """Service for sorting and organizing card collections."""
    
    def __init__(self, csv_loader: CSVLoader):
        """Initialize sorting service."""
        self.csv_loader = csv_loader
    
    def sort_by_color(self, collection: Collection) -> Dict[str, List[Card]]:
        """Sort collection by color identity."""
        return collection.get_cards_by_color()
    
    def sort_by_set(self, collection: Collection) -> Dict[str, List[Card]]:
        """Sort collection by set/edition."""
        return collection.get_cards_by_set()
    
    def sort_by_rarity(self, collection: Collection) -> Dict[str, List[Card]]:
        """Sort collection by rarity."""
        return collection.get_cards_by_rarity()
    
    def sort_by_type(self, collection: Collection) -> Dict[str, List[Card]]:
        """Sort collection by card type."""
        return collection.get_cards_by_type()
    
    def sort_by_value(self, collection: Collection, descending: bool = True) -> List[Card]:
        """Sort collection by card value."""
        cards_with_prices = [card for card in collection.cards if card.purchase_price is not None]
        return sorted(
            cards_with_prices,
            key=lambda c: c.purchase_price or 0,
            reverse=descending
        )
    
    def sort_by_name(self, collection: Collection, descending: bool = False) -> List[Card]:
        """Sort collection alphabetically by name."""
        return sorted(collection.cards, key=lambda c: c.name.lower(), reverse=descending)
    
    def sort_by_count(self, collection: Collection, descending: bool = True) -> List[Card]:
        """Sort collection by card count."""
        return sorted(collection.cards, key=lambda c: c.count, reverse=descending)
    
    def export_sorted_collection(self, grouped_cards: Dict[str, List[Card]], 
                                sort_type: str, output_dir: str = "sorted_output") -> bool:
        """Export sorted collection to CSV files."""
        return self.csv_loader.export_grouped_collections(
            grouped_cards, 
            output_dir, 
            f"{sort_type}"
        )
    
    def get_available_sort_methods(self) -> List[str]:
        """Get list of available sorting methods."""
        return ["color", "set", "rarity", "type", "value", "name", "count"]
