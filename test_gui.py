#!/usr/bin/env python3
"""Test script for the GUI."""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required imports work."""
    try:
        from src.data.csv_loader import CSVLoader
        from src.data.scryfall_client import ScryfallClient
        from src.services.collection_service import CollectionService
        from src.models.collection import Collection
        from src.models.card import Card
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_loading():
    """Test loading the enriched collection."""
    try:
        from src.data.csv_loader import CSVLoader
        
        csv_path = Path("data/enriched_collection_complete.csv")
        if not csv_path.exists():
            print(f"✗ Data file not found: {csv_path}")
            return False
        
        loader = CSVLoader(str(csv_path))
        collection = loader.load_collection("Test Collection")
        
        if collection and collection.cards:
            print(f"✓ Loaded collection with {len(collection.cards)} cards")
            return True
        else:
            print("✗ Failed to load collection")
            return False
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False

if __name__ == "__main__":
    print("Testing MyManaBox GUI dependencies...")
    
    if test_imports():
        if test_data_loading():
            print("\n✓ All tests passed! GUI should work.")
            
            # Try to import and run GUI
            try:
                import gui
                print("Starting GUI...")
                app = gui.MyManaBoxGUI()
                app.run()
            except Exception as e:
                print(f"✗ GUI error: {e}")
        else:
            print("\n✗ Data loading failed")
    else:
        print("\n✗ Import tests failed")
