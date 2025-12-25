#!/usr/bin/env python3
"""Test export functionality"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.data import CSVLoader
from src.models import Collection

# Load collection
loader = CSVLoader("data/enriched_collection_complete.csv")
collection = loader.load_collection()

if collection:
    print(f"Loaded {collection.unique_cards} cards")
    
    # Test export
    success = loader.save_collection(collection, "test_export.csv")
    
    if success:
        print("✓ Export successful! test_export.csv created")
    else:
        print("✗ Export failed")
        sys.exit(1)
else:
    print("✗ Failed to load collection")
    sys.exit(1)
