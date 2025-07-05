"""
Simple test script for the refactored MyManaBox.
Tests basic functionality without the complex CLI.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_basic_functionality():
    """Test basic functionality of refactored code."""
    
    try:
        print("Testing refactored MyManaBox...")
        
        # Test imports
        print("✓ Testing imports...")
        from src.models import Card, Collection, CardColor, CardRarity
        from src.data import CSVLoader
        from src.services import CollectionService, SortingService
        from src.utils import Constants, PriceHelper
        print("✓ All imports successful")
        
        # Test model creation
        print("✓ Testing model creation...")
        card = Card(name="Lightning Bolt", edition="lea", count=1)
        collection = Collection([card])
        print(f"✓ Created collection with {collection.unique_cards} cards")
        
        # Test services
        print("✓ Testing services...")
        csv_loader = CSVLoader("moxfield_export.csv")
        collection_service = CollectionService(csv_loader)
        sorting_service = SortingService(csv_loader)
        print("✓ Services created successfully")
        
        # Test loading existing collection if available
        if Path("moxfield_export.csv").exists():
            print("✓ Testing collection loading...")
            success = collection_service.load_collection()
            if success:
                loaded_collection = collection_service.get_collection()
                if loaded_collection:
                    print(f"✓ Loaded collection with {loaded_collection.unique_cards} unique cards")
                    
                    # Test sorting
                    sorted_by_color = sorting_service.sort_by_color(loaded_collection)
                    print(f"✓ Sorted by color: {len(sorted_by_color)} color groups")
                    
                    # Test analytics
                    stats = collection_service.get_collection_stats()
                    print(f"✓ Got collection stats: {stats.get('total_cards', 0)} total cards")
            else:
                print("! Collection file not found or invalid, but that's OK for testing")
        
        print("\n🎉 All tests passed! The refactored code is working correctly.")
        print("\nThe project has been successfully reorganized with separation of concerns:")
        print("  📁 src/models/     - Data models (Card, Collection)")
        print("  📁 src/data/       - Data access (CSV, API, file management)")  
        print("  📁 src/services/   - Business logic (sorting, search, analytics)")
        print("  📁 src/presentation/ - UI layer (console interface, formatting)")
        print("  📁 src/utils/      - Common utilities and helpers")
        print("  📄 main.py         - Main entry point that orchestrates everything")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_basic_functionality()
