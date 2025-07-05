#!/usr/bin/env python3
"""
Simple script to create enriched CSV using the existing MyManaBox infrastructure.
"""

import os
import sys
from pathlib import Path

# Set working directory and add src to path
os.chdir(Path(__file__).parent)
sys.path.insert(0, "src")

def main():
    try:
        from src.data import CSVLoader, ScryfallClient
        from src.services import CollectionService
        
        print("🔄 Creating enriched CSV export...")
        
        # Initialize services
        csv_loader = CSVLoader("data/moxfield_export.csv")
        scryfall_client = ScryfallClient()
        collection_service = CollectionService(csv_loader, scryfall_client)
        
        # Load collection
        print("📂 Loading collection from moxfield_export.csv...")
        if not collection_service.load_collection("My Collection"):
            print("❌ Failed to load collection")
            return 1
        
        collection = collection_service.get_collection()
        if not collection:
            print("❌ Collection is empty")
            return 1
            
        print(f"✅ Loaded {collection.unique_cards} unique cards ({collection.total_cards} total)")
        
        # Apply cached enrichment data (no API calls since cache exists)
        print("🔍 Applying cached Scryfall data...")
        enriched_count = collection_service.enrich_collection_data()
        print(f"✅ Applied enriched data to {enriched_count} cards")
        
        # Export enriched CSV
        output_file = "data/enriched_collection.csv"
        print(f"💾 Exporting enriched collection to {output_file}...")
        
        if csv_loader.save_collection(collection, output_file):
            print(f"✅ Successfully created enriched CSV: {output_file}")
            
            # Show file info
            file_path = Path(output_file)
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"📊 File size: {size_mb:.1f} MB")
                
                # Show sample of enriched data
                print(f"📋 Sample enriched fields for first card:")
                if collection.cards:
                    sample_dict = collection.cards[0].to_dict()
                    print(f"   - Total columns: {len(sample_dict)}")
                    print(f"   - Includes: market prices, card details, legalities, images, etc.")
            
            return 0
        else:
            print("❌ Failed to export enriched collection")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
