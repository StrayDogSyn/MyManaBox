#!/usr/bin/env python3
"""
Automated Collection Enrichment Script

Enriches your collection with current Scryfall data and prices.
Designed to run on a schedule (daily/weekly) via Windows Task Scheduler.

Usage:
    python scripts/auto_enrich.py
    python scripts/auto_enrich.py --csv data/enriched_collection_complete.csv
    python scripts/auto_enrich.py --backup --quiet
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data import CSVLoader, ScryfallClient
from src.services import CollectionService


def create_backup(csv_path: Path) -> Path:
    """Create timestamped backup of collection."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = csv_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / f"{csv_path.stem}_backup_{timestamp}.csv"
    
    # Copy file
    import shutil
    shutil.copy2(csv_path, backup_path)
    
    return backup_path


def enrich_collection(csv_file: str, backup: bool = True, quiet: bool = False):
    """Enrich collection with current market data."""
    
    csv_path = Path(csv_file)
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_file}")
        return False
    
    # Backup if requested
    if backup:
        if not quiet:
            print(f"Creating backup...")
        backup_path = create_backup(csv_path)
        if not quiet:
            print(f"✓ Backup created: {backup_path}")
    
    # Load collection
    if not quiet:
        print(f"Loading collection from {csv_file}...")
    
    csv_loader = CSVLoader(csv_file)
    scryfall_client = ScryfallClient()
    collection_service = CollectionService(csv_loader, scryfall_client)
    
    if not collection_service.load_collection():
        print("Error: Failed to load collection")
        return False
    
    collection = collection_service.get_collection()
    
    if not quiet:
        print(f"✓ Loaded {collection.unique_cards} unique cards ({collection.total_cards} total)")
        print(f"Enriching with current Scryfall data...")
    
    # Progress callback
    def progress_callback(current, total):
        if not quiet and (current % 100 == 0 or current == total):
            percent = (current / total) * 100
            print(f"  Progress: {current}/{total} cards ({percent:.1f}%)")
    
    # Enrich
    enriched_count = collection_service.enrich_collection_data(progress_callback)
    
    if enriched_count > 0:
        if not quiet:
            print(f"✓ Enriched {enriched_count} cards")
            print(f"Total current market value: ${collection.total_value:.2f}")
        
        # Save enriched collection
        if not quiet:
            print(f"Saving enriched collection...")
        
        if csv_loader.save_collection(collection, csv_file):
            if not quiet:
                print(f"✓ Saved to {csv_file}")
            return True
        else:
            print("Error: Failed to save collection")
            return False
    else:
        if not quiet:
            print("No cards were enriched (may be using cached data)")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatically enrich collection with current Scryfall data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/auto_enrich.py
  python scripts/auto_enrich.py --csv data/collection.csv
  python scripts/auto_enrich.py --backup --quiet
  
Recommended Windows Task Scheduler setup:
  Program: C:/Users/EHunt/Repos/Projects/MyManaBox/.venv/Scripts/python.exe
  Arguments: scripts/auto_enrich.py --backup --quiet
  Start in: C:/Users/EHunt/Repos/Projects/MyManaBox
  Schedule: Daily at 9:00 AM
        """
    )
    
    parser.add_argument(
        "--csv",
        default="data/enriched_collection_complete.csv",
        help="Path to CSV file (default: data/enriched_collection_complete.csv)"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup before enriching"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (for scheduled tasks)"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("=" * 60)
        print("MyManaBox - Automated Collection Enrichment")
        print("=" * 60)
        print()
    
    success = enrich_collection(args.csv, args.backup, args.quiet)
    
    if not args.quiet:
        print()
        if success:
            print("✓ Enrichment complete!")
        else:
            print("✗ Enrichment failed")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
