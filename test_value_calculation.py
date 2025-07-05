#!/usr/bin/env python3
"""
Quick test script to demonstrate the value calculation difference.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.data import CSVLoader
from src.services import CollectionService


def main():
    """Test value calculations."""
    print("MyManaBox - Value Calculation Demo")
    print("=" * 40)
    
    # Load collection without API enrichment
    csv_loader = CSVLoader("data/moxfield_export.csv")
    collection_service = CollectionService(csv_loader, None)  # No API client
    
    if collection_service.load_collection():
        collection = collection_service.get_collection()
        
        if collection:
            print(f"Collection loaded: {collection.unique_cards} unique cards, {collection.total_cards} total")
            print(f"Purchase price total: ${collection.total_value:.2f}")
            
            # Count cards with and without purchase prices
            cards_with_prices = 0
            cards_without_prices = 0
            total_purchase_value = 0
            
            for card in collection.cards:
                if card.purchase_price and card.purchase_price > 0:
                    cards_with_prices += 1
                    total_purchase_value += float(card.purchase_price * card.count)
                else:
                    cards_without_prices += 1
            
            print(f"\nPrice Analysis:")
            print(f"- Cards with purchase prices: {cards_with_prices}")
            print(f"- Cards without purchase prices: {cards_without_prices}")
            print(f"- Total from purchase prices: ${total_purchase_value:.2f}")
            
            print(f"\nNote: Moxfield shows ${2379.52:.2f} because it uses current market values,")
            print(f"not historical purchase prices. Many cards in your CSV have empty purchase prices.")
            print(f"\nTo get current market values, the application would need to:")
            print(f"1. Fetch current prices from Scryfall API for each card")
            print(f"2. This takes ~2-3 minutes for {collection.unique_cards} unique cards")
            print(f"3. The result would be much closer to Moxfield's ${2379.52:.2f}")
        else:
            print("Collection object is None")
    else:
        print("Failed to load collection")


if __name__ == "__main__":
    main()
