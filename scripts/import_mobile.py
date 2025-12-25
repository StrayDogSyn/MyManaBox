#!/usr/bin/env python3
"""
Mobile ManaBox Import Script

Handles CSV imports from the mobile ManaBox app with format detection and merging.

Usage:
    python scripts/import_mobile.py ~/Downloads/manabox_export.csv
    python scripts/import_mobile.py mobile_scan.csv --merge --backup
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data import CSVLoader
from src.models import Collection, Card


def detect_manabox_format(csv_path: Path) -> bool:
    """Detect if CSV is from mobile ManaBox app."""
    try:
        df = pd.read_csv(csv_path, nrows=1)
        
        # ManaBox typically has these columns
        manabox_indicators = ['quantity', 'tradelist', 'wishlist', 'foil']
        
        return any(col.lower() in [c.lower() for c in df.columns] for col in manabox_indicators)
    except Exception:
        return False


def normalize_manabox_csv(csv_path: Path) -> pd.DataFrame:
    """Normalize ManaBox CSV to MyManaBox format."""
    df = pd.read_csv(csv_path)
    
    # Map ManaBox columns to MyManaBox columns
    column_mapping = {
        'name': 'Name',
        'set name': 'Edition',
        'set': 'Edition',
        'quantity': 'Count',
        'foil': 'Foil',
        'condition': 'Condition',
        'purchase price': 'Purchase Price',
        'price': 'Purchase Price'
    }
    
    # Rename columns (case-insensitive)
    df.columns = df.columns.str.strip()
    for old_col, new_col in column_mapping.items():
        for df_col in df.columns:
            if df_col.lower() == old_col.lower():
                df.rename(columns={df_col: new_col}, inplace=True)
                break
    
    # Ensure required columns exist
    required = ['Name', 'Edition', 'Count']
    for col in required:
        if col not in df.columns:
            if col == 'Count':
                df['Count'] = 1
            elif col == 'Edition':
                df['Edition'] = 'Unknown'
    
    # Convert Foil to boolean
    if 'Foil' in df.columns:
        df['Foil'] = df['Foil'].fillna('').astype(str).str.lower().isin(['yes', 'true', '1', 'foil'])
    else:
        df['Foil'] = False
    
    # Default condition
    if 'Condition' not in df.columns:
        df['Condition'] = 'Near Mint'
    
    # Filter out tradelist/wishlist items if columns exist
    if 'tradelist' in [c.lower() for c in df.columns]:
        tradelist_col = [c for c in df.columns if c.lower() == 'tradelist'][0]
        df = df[df[tradelist_col].fillna(0) == 0]
    
    if 'wishlist' in [c.lower() for c in df.columns]:
        wishlist_col = [c for c in df.columns if c.lower() == 'wishlist'][0]
        df = df[df[wishlist_col].fillna(0) == 0]
    
    return df


def merge_collections(existing_path: Path, new_df: pd.DataFrame) -> Collection:
    """Merge new cards into existing collection."""
    
    # Load existing collection
    loader = CSVLoader(str(existing_path))
    existing_collection = loader.load_collection()
    
    if not existing_collection:
        existing_collection = Collection(name="My Collection")
    
    # Convert new DataFrame to cards
    new_cards = Collection.from_csv_data(new_df.to_dict('records'))
    
    # Merge cards
    added = 0
    updated = 0
    
    for new_card in new_cards.cards:
        # Check if card exists
        existing_card = None
        for card in existing_collection.cards:
            if (card.name == new_card.name and 
                card.edition == new_card.edition and
                card.foil == new_card.foil):
                existing_card = card
                break
        
        if existing_card:
            # Update quantity
            existing_card.count += new_card.count
            updated += 1
        else:
            # Add new card
            existing_collection.cards.append(new_card)
            added += 1
    
    return existing_collection, added, updated


def import_mobile_manabox(import_file: str, merge: bool = False, 
                         target: str = "data/enriched_collection_complete.csv",
                         backup: bool = True):
    """Import from mobile ManaBox CSV."""
    
    import_path = Path(import_file)
    target_path = Path(target)
    
    if not import_path.exists():
        print(f"Error: Import file not found: {import_file}")
        return False
    
    print(f"Analyzing {import_path.name}...")
    
    # Detect format
    is_manabox = detect_manabox_format(import_path)
    
    if is_manabox:
        print("✓ Detected mobile ManaBox format")
        print("Normalizing CSV structure...")
        df = normalize_manabox_csv(import_path)
    else:
        print("✓ Standard MyManaBox format detected")
        df = pd.read_csv(import_path)
    
    print(f"Found {len(df)} cards to import")
    
    # Backup existing collection
    if backup and target_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = target_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f"{target_path.stem}_before_import_{timestamp}.csv"
        
        import shutil
        shutil.copy2(target_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
    
    # Merge or replace
    if merge and target_path.exists():
        print("Merging with existing collection...")
        merged_collection, added, updated = merge_collections(target_path, df)
        
        print(f"✓ Added {added} new cards")
        print(f"✓ Updated quantities for {updated} existing cards")
        print(f"Total collection: {merged_collection.unique_cards} unique cards ({merged_collection.total_cards} total)")
        
        # Save merged collection
        loader = CSVLoader(str(target_path))
        if loader.save_collection(merged_collection):
            print(f"✓ Saved to {target_path}")
            return True
        else:
            print("Error: Failed to save merged collection")
            return False
    else:
        # Replace entire collection
        print(f"Saving to {target_path}...")
        df.to_csv(target_path, index=False)
        print(f"✓ Saved {len(df)} cards")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import cards from mobile ManaBox CSV exports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Replace entire collection
  python scripts/import_mobile.py ~/Downloads/manabox_export.csv
  
  # Merge with existing collection
  python scripts/import_mobile.py mobile_scan.csv --merge --backup
  
  # Import to different target
  python scripts/import_mobile.py new_cards.csv --target data/collection.csv

Mobile ManaBox Export Instructions:
  1. Open ManaBox app on phone
  2. Go to Collection → Export
  3. Choose CSV format
  4. Transfer file to computer
  5. Run this script
        """
    )
    
    parser.add_argument(
        "import_file",
        help="CSV file to import"
    )
    
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing collection (default: replace)"
    )
    
    parser.add_argument(
        "--target",
        default="data/enriched_collection_complete.csv",
        help="Target collection file (default: data/enriched_collection_complete.csv)"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before import (default: enabled)"
    )
    
    parser.add_argument(
        "--no-backup",
        dest="backup",
        action="store_false",
        help="Skip backup"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MyManaBox - Mobile ManaBox Import")
    print("=" * 60)
    print()
    
    success = import_mobile_manabox(
        args.import_file,
        args.merge,
        args.target,
        args.backup
    )
    
    print()
    if success:
        print("✓ Import complete!")
        print()
        print("Next steps:")
        print("  1. Enrich with Scryfall data: python scripts/auto_enrich.py")
        print("  2. View collection: python main.py --summary")
    else:
        print("✗ Import failed")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
