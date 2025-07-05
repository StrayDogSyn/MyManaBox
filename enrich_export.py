#!/usr/bin/env python3
"""
Quick script to export enriched collection CSV using cached data.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data import CSVLoader, ScryfallClient
from src.services import CollectionService

def main():
    print("Creating enriched CSV export...")
    
    # Create services
    csv_loader = CSVLoader("data/moxfield_export.csv")
    scryfall_client = ScryfallClient()
    collection_service = CollectionService(csv_loader, scryfall_client)
    
    # Load collection
    print("Loading collection...")
    if not collection_service.load_collection():
        print("Failed to load collection")
        return 1
    
    collection = collection_service.get_collection()
    if not collection:
        print("No collection loaded")
        return 1
        
    print(f"Loaded {collection.unique_cards} unique cards ({collection.total_cards} total)")
    
    # Since enrichment has already been run, the cache should contain the data
    # Let's try to enrich with cache only (no API calls)
    print("Using cached Scryfall data...")
    enriched_count = collection_service.enrich_collection_data()
    print(f"Applied cached data to {enriched_count} cards")
    
    # Export to enriched CSV
    output_file = "data/enriched_collection.csv"
    print(f"Exporting to {output_file}...")
    
    if collection_service.save_collection(output_file):
        print(f"✓ Successfully exported enriched collection to {output_file}")
        
        # Show some stats
        total_purchase = sum(card.purchase_price * card.count for card in collection.cards if card.purchase_price)
        total_market = sum(card.market_value * card.count for card in collection.cards if card.market_value)
        
        print(f"\nCollection Summary:")
        print(f"- Total cards: {collection.total_cards}")
        print(f"- Unique cards: {collection.unique_cards}")
        print(f"- Purchase value: ${total_purchase:.2f}")
        print(f"- Current market value: ${total_market:.2f}")
        
        if total_purchase > 0:
            appreciation = total_market - total_purchase
            print(f"- Value change: ${appreciation:.2f} ({(appreciation/total_purchase)*100:.1f}%)")
        
        # Show file size
        file_path = Path(output_file)
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"- File size: {size_mb:.1f} MB")
            
        return 0
    else:
        print("✗ Failed to export enriched collection")
        return 1

if __name__ == "__main__":
    sys.exit(main())
