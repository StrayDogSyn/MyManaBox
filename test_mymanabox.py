#!/usr/bin/env python3
"""
Test script for MyManaBox functionality
"""

import sys
import os
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

try:
    from card_sorter import MTGCardSorter
    from enhanced_sorter import EnhancedMTGCardSorter
    from scryfall_api import ScryfallAPI
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic card sorting functionality."""
    print("\n=== Testing Basic Functionality ===")
    
    # Check if CSV file exists
    csv_file = "moxfield_export.csv"
    if not os.path.exists(csv_file):
        print(f"✗ CSV file '{csv_file}' not found")
        return False
    
    try:
        # Test basic sorter
        sorter = MTGCardSorter(csv_file)
        if sorter.cards_df is not None:
            print("✓ Basic sorter loaded successfully")
            print(f"  - {len(sorter.cards_df)} cards loaded")
            
            # Test sorting
            color_groups = sorter.sort_by_color()
            print(f"  - Color sorting: {len(color_groups)} groups")
            
            return True
        else:
            print("✗ Failed to load cards")
            return False
            
    except Exception as e:
        print(f"✗ Error testing basic functionality: {e}")
        return False

def test_enhanced_functionality():
    """Test enhanced functionality (without API calls)."""
    print("\n=== Testing Enhanced Functionality ===")
    
    try:
        # Test enhanced sorter without API
        sorter = EnhancedMTGCardSorter("moxfield_export.csv", use_api=False)
        if sorter.cards_df is not None:
            print("✓ Enhanced sorter loaded successfully (no API)")
            return True
        else:
            print("✗ Failed to load enhanced sorter")
            return False
            
    except Exception as e:
        print(f"✗ Error testing enhanced functionality: {e}")
        return False

def test_api_connection():
    """Test API connection (optional)."""
    print("\n=== Testing API Connection ===")
    
    try:
        api = ScryfallAPI()
        print("✓ API object created")
        
        # Test with a simple card
        test_card = api.get_card_data("Lightning Bolt")
        if test_card:
            print("✓ API connection working")
            print(f"  - Test card: {test_card.get('name', 'Unknown')}")
            return True
        else:
            print("⚠ API connection failed or card not found")
            return False
            
    except Exception as e:
        print(f"⚠ API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("MyManaBox - Test Suite")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 0
    
    # Test basic functionality
    total_tests += 1
    if test_basic_functionality():
        tests_passed += 1
    
    # Test enhanced functionality
    total_tests += 1
    if test_enhanced_functionality():
        tests_passed += 1
    
    # Test API (optional)
    total_tests += 1
    if test_api_connection():
        tests_passed += 1
    else:
        print("  (API test is optional and may fail due to network issues)")
    
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed >= 2:  # Basic and enhanced must work
        print("✓ Core functionality is working!")
        return 0
    else:
        print("✗ Core tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
