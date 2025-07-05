"""CSV file loading functionality."""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from ..models import Collection, Card


class CSVLoader:
    """Handles loading and saving collections from/to CSV files."""
    
    def __init__(self, file_path: str = "moxfield_export.csv"):
        """Initialize with CSV file path."""
        self.file_path = Path(file_path)
    
    def load_collection(self, name: str = "My Collection") -> Optional[Collection]:
        """Load collection from CSV file."""
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"Could not find {self.file_path}")
            
            df = pd.read_csv(self.file_path)
            csv_data = df.to_dict('records')
            return Collection.from_csv_data(csv_data, name)
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None
    
    def save_collection(self, collection: Collection, file_path: Optional[str] = None) -> bool:
        """Save collection to CSV file."""
        try:
            output_path = Path(file_path) if file_path else self.file_path
            
            # Convert cards to dictionaries
            data = [card.to_dict() for card in collection.cards]
            df = pd.DataFrame(data)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            return True
            
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def export_grouped_collections(self, grouped_cards: Dict[str, List[Card]], 
                                  output_dir: str = "sorted_output", 
                                  prefix: str = "sorted") -> bool:
        """Export grouped cards to separate CSV files."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            for group_name, cards in grouped_cards.items():
                if cards:  # Only create files for non-empty groups
                    data = [card.to_dict() for card in cards]
                    df = pd.DataFrame(data)
                    
                    filename = f"{prefix}_{group_name.replace(' ', '_').lower()}.csv"
                    filepath = output_path / filename
                    df.to_csv(filepath, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting grouped collections: {e}")
            return False
