#!/usr/bin/env python3
"""
Quick test script to verify collection import functionality.
Tests the import pipeline with your actual CSV data.
"""

import sys
import asyncio
from pathlib import Path
from decimal import Decimal

# Fix Windows encoding
if sys.platform == 'win32':
    import os
    os.system('chcp 65001 > nul')  # Set console to UTF-8

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cardforge.importers.csv_importer import CSVImporter, detect_csv_schema
from cardforge.database.connection import DatabaseConnection


async def test_import(csv_file: Path, dry_run: bool = True):
    """Test importing CSV data."""
    
    print("=" * 70)
    print(" CardForge Collection Import Test")
    print("=" * 70)
    print()
    
    # Check file exists
    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return False
    
    print(f"📄 CSV File: {csv_file}")
    print(f"📊 File size: {csv_file.stat().st_size:,} bytes")
    
    # Detect schema
    print("\n🔍 Detecting CSV schema...")
    try:
        schema = detect_csv_schema(csv_file)
        print(f"✅ Schema detected: {schema.name}")
    except Exception as e:
        print(f"❌ Schema detection failed: {e}")
        return False
    
    if dry_run:
        print("\n🔬 DRY RUN MODE - No data will be written")
        print("\nPreview first few lines:")
        print("-" * 70)
        with open(csv_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 5:
                    print(line.rstrip())
                else:
                    break
        print("-" * 70)
        
        # Count total lines
        with open(csv_file, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f) - 1  # Subtract header
        print(f"\n📈 Estimated cards to import: {line_count:,}")
        
        return True
    
    # Actual import
    print("\n💾 Connecting to database...")
    db_path = Path("data/cardforge.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize database (creates schema if needed)
        from cardforge.database import init_db, get_connection
        from cardforge.models import Collection

        await init_db(str(db_path))
        print("✅ Database initialized")
        
        # Ensure default collection exists
        print("📦 Ensuring default collection exists...")
        async with get_connection() as conn:
            cursor = await conn.execute(
                "SELECT id FROM collections WHERE id = 1 LIMIT 1"
            )
            default_collection = await cursor.fetchone()
            
            if not default_collection:
                await conn.execute(
                    "INSERT INTO collections (id, name, is_default) VALUES (1, 'Main Collection', 1)"
                )
                await conn.commit()
                print("✅ Created default collection")
            else:
                print("✅ Default collection exists")
        
        # Initialize importer (repositories fetch connections internally)
        importer = CSVImporter()
        
        print("\n📥 Starting import...")
        result = await importer.import_csv(
            file_path=csv_file,
            collection_id=1,  # Default collection
            merge=True,
            backup=True
        )
        
        print("\n✅ Import completed successfully!")
        print(f"\n📊 Import Statistics:")
        print(f"   Cards imported: {result.get('imported', 0):,}")
        print(f"   Duplicates skipped: {result.get('skipped', 0):,}")
        print(f"   Errors: {result.get('errors', 0):,}")
        warnings = result.get('warnings', []) or []
        if warnings:
            preview = warnings[:5]
            print(f"   Warning samples ({len(preview)} of {len(warnings)}):")
            for w in preview:
                print(f"     - {w}")
        
        if result.get('backup_path'):
            print(f"\n💾 Backup created: {result['backup_path']}")
        
        return True
            
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CardForge CSV import")
    parser.add_argument(
        "csv_file",
        type=Path,
        nargs='?',
        default=Path("data/moxfield_collection_2026-01-12-0154Z.csv"),
        help="Path to CSV file to import"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview without importing (default: True)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the import"
    )
    
    args = parser.parse_args()
    
    # If --execute is provided, disable dry-run
    dry_run = not args.execute
    
    print()
    success = asyncio.run(test_import(args.csv_file, dry_run=dry_run))
    
    print("\n" + "=" * 70)
    if success:
        print(" ✅ Test completed successfully")
        if dry_run:
            print(" Run with --execute to perform actual import")
    else:
        print(" ❌ Test failed")
    print("=" * 70)
    print()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
