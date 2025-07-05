#!/usr/bin/env python3
"""
Test script to verify comprehensive CSV export functionality.
Tests with just the first few cards to verify all fields are working.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.data import CSVLoader, ScryfallClient
from src.services import CollectionService
import csv


def test_comprehensive_export():
    """Test comprehensive CSV export with first few cards."""
    print("Testing comprehensive CSV export...")
    
    # Create services
    csv_loader = CSVLoader("data/moxfield_export.csv")
    scryfall_client = ScryfallClient()
    collection_service = CollectionService(csv_loader, scryfall_client)
    
    # Load just the first few cards
    print("Loading collection...")
    if not collection_service.load_collection():
        print("Failed to load collection")
        return False
    
    collection = collection_service.get_collection()
    if not collection or not collection.cards:
        print("No cards found")
        return False
    
    # Take just the first 3 cards for testing
    test_cards = list(collection.cards)[:3]
    print(f"Testing with {len(test_cards)} cards:")
    for card in test_cards:
        print(f"  - {card.name} ({card.edition})")
    
    # Enrich the test cards
    print("\nEnriching cards with Scryfall data...")
    enriched_count = 0
    for card in test_cards:
        if scryfall_client.enrich_card(card):
            enriched_count += 1
            print(f"  ✓ Enriched: {card.name}")
        else:
            print(f"  ✗ Failed: {card.name}")
    
    print(f"\nEnriched {enriched_count} out of {len(test_cards)} cards")
    
    # Test CSV export
    output_file = "data/test_comprehensive_export.csv"
    print(f"\nExporting to {output_file}...")
    
    # Get all card data as dictionaries
    card_dicts = [card.to_dict() for card in test_cards]
    
    if not card_dicts:
        print("No card data to export")
        return False
    
    # Get all possible field names
    all_fields = set()
    for card_dict in card_dicts:
        all_fields.update(card_dict.keys())
    
    # Sort fields for consistent output
    sorted_fields = sorted(all_fields)
    
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted_fields)
        writer.writeheader()
        writer.writerows(card_dicts)
    
    print(f"✓ Exported {len(card_dicts)} cards with {len(sorted_fields)} fields")
    print(f"\nFields included:")
    for i, field in enumerate(sorted_fields):
        print(f"  {i+1:2d}. {field}")
    
    # Show sample data for first card
    if test_cards and enriched_count > 0:
        print(f"\nSample enriched data for '{test_cards[0].name}':")
        enriched_card = test_cards[0]
        sample_fields = [
            'Scryfall ID', 'Colors', 'Rarity', 'Mana Cost', 'CMC',
            'Market Value', 'USD Price', 'Artist', 'Set Name', 'Keywords',
            'Legalities', 'EDHREC Rank'
        ]
        
        card_dict = enriched_card.to_dict()
        for field in sample_fields:
            value = card_dict.get(field, 'N/A')
            if value:  # Only show fields with data
                print(f"  {field}: {value}")
    
    return True


if __name__ == "__main__":
    success = test_comprehensive_export()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
