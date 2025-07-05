"""Collection management service."""

from typing import Optional, List
from ..models import Collection, Card
from ..data import CSVLoader, ScryfallClient


class CollectionService:
    """Service for managing card collections."""
    
    def __init__(self, csv_loader: CSVLoader, scryfall_client: Optional[ScryfallClient] = None):
        """Initialize collection service."""
        self.csv_loader = csv_loader
        self.scryfall_client = scryfall_client
        self.collection: Optional[Collection] = None
    
    def load_collection(self, name: str = "My Collection") -> bool:
        """Load collection from CSV file."""
        self.collection = self.csv_loader.load_collection(name)
        return self.collection is not None
    
    def save_collection(self, file_path: Optional[str] = None) -> bool:
        """Save current collection to CSV file."""
        if not self.collection:
            return False
        return self.csv_loader.save_collection(self.collection, file_path)
    
    def get_collection(self) -> Optional[Collection]:
        """Get the current collection."""
        return self.collection
    
    def enrich_collection_data(self, progress_callback=None) -> int:
        """Enrich collection with API data."""
        if not self.collection or not self.scryfall_client:
            return 0
        
        return self.scryfall_client.enrich_collection(self.collection.cards, progress_callback)
    
    def add_card(self, card: Card) -> None:
        """Add a card to the collection."""
        if self.collection:
            self.collection.add_card(card)
    
    def remove_card(self, card: Card, count: Optional[int] = None) -> bool:
        """Remove card(s) from collection."""
        if not self.collection:
            return False
        return self.collection.remove_card(card, count)
    
    def get_collection_stats(self) -> dict:
        """Get basic collection statistics."""
        if not self.collection:
            return {}
        
        return {
            'total_cards': self.collection.total_cards,
            'unique_cards': self.collection.unique_cards,
            'total_value': self.collection.total_value,
            'condition_stats': self.collection.get_condition_stats(),
            'set_stats': self.collection.get_set_stats(),
            'foil_stats': self.collection.get_foil_stats()
        }
    
    def export_enriched_collection(self, file_path: str = "enriched_collection.csv") -> bool:
        """Export collection with all available Scryfall data."""
        if not self.collection:
            return False
        
        print(f"Enriching collection with Scryfall data...")
        enriched_count = self.enrich_collection_data()
        print(f"Enriched {enriched_count} cards with API data")
        
        print(f"Exporting enriched collection to {file_path}...")
        success = self.save_collection(file_path)
        
        if success:
            print(f"✓ Enriched collection exported to {file_path}")
            print(f"The CSV now includes comprehensive Scryfall data:")
            print("- Current market prices")
            print("- Card colors, types, and rarity")
            print("- Mana cost and CMC")
            print("- Power/toughness/loyalty")
            print("- Oracle text and flavor text")
            print("- Artist and set information")
            print("- Legal format information")
            print("- Image URLs")
            print("- Rankings and properties")
        
        return success
