#!/usr/bin/env python3
"""
CardForge Collection Import Script
==================================

Main entry point for importing collections from CSV files.

Usage:
    python import_collection.py <csv_file> [--format FORMAT] [--replace] [--no-backup]

Examples:
    python import_collection.py data/imports/ManaBox_Collection_Bulk.csv
    python import_collection.py data/imports/manabox_export.csv --format manabox --replace
    python import_collection.py data/imports/archidekt.csv --format archidekt
"""

import asyncio
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from src.database.connection import DatabaseManager
from src.services.migration_service import MigrationManager, BackupManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Import MTG collection from CSV file",
        usage="python import_collection.py <csv_file> [options]",
    )
    
    parser.add_argument(
        "csv_file",
        help="Path to CSV file to import",
    )
    
    parser.add_argument(
        "--format",
        choices=["manabox", "archidekt", "moxfield", "standard"],
        default=None,
        help="CSV format (auto-detect if not specified)",
    )
    
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing collection (dangerous!)",
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show collection status and exit",
    )
    
    return parser.parse_args()


def print_status(db_manager: DatabaseManager):
    """Print collection status."""
    from src.services.migration_service import MigrationManager
    
    migration = MigrationManager(db_manager)
    status = migration.get_import_status()
    
    print("\n" + "="*50)
    print("Collection Status")
    print("="*50)
    print(f"Collection Items: {status['collection_items']:,}")
    print(f"Unique Cards: {status['unique_cards']:,}")
    print(f"Total Cards: {status['total_cards']:,}")
    print(f"Foil Cards: {status['foil_cards']:,}")
    print(f"Total Value: ${status['total_value']:,.2f}")
    print("="*50 + "\n")


async def main():
    """Main import function."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    try:
        # Handle status request
        if args.status:
            print_status(db_manager)
            return 0
        
        # Validate CSV file
        csv_path = Path(args.csv_file)
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            return 1
        
        logger.info(f"CSV file: {csv_path}")
        logger.info(f"File size: {csv_path.stat().st_size:,} bytes")
        
        # Show backup location
        backup_manager = BackupManager()
        logger.info(f"Backup directory: {backup_manager.backup_dir}")
        
        # Confirm if replacing collection
        if args.replace:
            print("\n" + "!"*50)
            print("WARNING: Replace mode enabled")
            print("This will CLEAR your existing collection!")
            print("!"*50)
            response = input("\nType 'YES' to confirm: ").strip()
            if response != "YES":
                logger.info("Import cancelled")
                return 0
        
        # Run import
        migration = MigrationManager(db_manager)
        result = await migration.import_csv_file(
            csv_path,
            format=args.format,
            create_backup=not args.no_backup,
            replace_mode=args.replace,
        )
        
        # Print results
        print("\n" + "="*50)
        print("Import Results")
        print("="*50)
        
        csv_stats = result.get("csv_stats", {})
        print(f"\nCSV Import:")
        print(f"  Cards imported: {csv_stats.get('total_imported', 0):,}")
        print(f"  Errors: {csv_stats.get('errors', 0)}")
        
        enrich_stats = result.get("enrichment_stats", {})
        print(f"\nScryfall Enrichment:")
        print(f"  Cards enriched: {enrich_stats.get('found', 0):,}")
        print(f"  Not found: {enrich_stats.get('not_found', 0):,}")
        print(f"  Errors: {enrich_stats.get('errors', 0)}")
        
        insert_stats = result.get("insert_stats", {})
        print(f"\nDatabase Insertion:")
        print(f"  Inserted: {insert_stats.get('inserted', 0):,}")
        print(f"  Updated: {insert_stats.get('updated', 0):,}")
        print(f"  Skipped: {insert_stats.get('skipped', 0):,}")
        print(f"  Errors: {insert_stats.get('errors', 0):,}")
        
        collection_stats = result.get("collection_stats", {})
        print(f"\nCollection Summary:")
        print(f"  Total items: {collection_stats.get('collection_items', 0):,}")
        print(f"  Unique cards: {collection_stats.get('unique_cards', 0):,}")
        print(f"  Total cards: {collection_stats.get('total_cards', 0):,}")
        print(f"  Foil cards: {collection_stats.get('foil_cards', 0):,}")
        print(f"  Total value: ${collection_stats.get('total_value', 0):,.2f}")
        
        print("="*50 + "\n")
        
        logger.info("Import completed successfully!")
        return 0
    
    except KeyboardInterrupt:
        logger.warning("Import cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        return 1
    finally:
        db_manager.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
