#!/usr/bin/env python3
"""
Automated MyManaBox Sync

Automatically sync your local MyManaBox data to mtg-collection-manager.

Usage:
    python scripts/sync_mymanabox.py
    python scripts/sync_mymanabox.py --auto-enrich
    python scripts/sync_mymanabox.py --dry-run
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.mymanabox import MyManaBoxReader
from src.catalogue import Collection


def sync_manabox(
    manabox_path: str = None,
    db_path: str = "data/collections/main.db",
    auto_enrich: bool = False,
    dry_run: bool = False,
    backup_first: bool = True
):
    """
    Sync MyManaBox to collection manager
    
    Args:
        manabox_path: Path to MyManaBox installation (auto-detect if None)
        db_path: Path to collection database
        auto_enrich: Automatically enrich with Scryfall data after sync
        dry_run: Show what would be synced without actually syncing
        backup_first: Backup MyManaBox data before syncing
    """
    print("=" * 60)
    print("MyManaBox → Collection Manager Sync")
    print("=" * 60)
    print()
    
    # Initialize MyManaBox reader
    try:
        reader = MyManaBoxReader(manabox_path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("\nPlease provide MyManaBox path:")
        print("  python scripts/sync_mymanabox.py --path 'C:/path/to/MyManaBox'")
        return False
    
    # Backup MyManaBox data
    if backup_first and not dry_run:
        print("\n📦 Creating backup of MyManaBox data...")
        reader.backup_manabox_data()
    
    # Initialize collection
    collection = Collection(db_path)
    
    # Get stats before sync
    before_stats = collection.get_statistics()
    print(f"\n📊 Collection before sync:")
    print(f"   Total cards: {before_stats['total_cards']}")
    print(f"   Unique cards: {before_stats['unique_cards']}")
    
    # Perform sync
    print(f"\n{'🔍 DRY RUN - ' if dry_run else '🔄 '}Syncing from MyManaBox...")
    imported = reader.sync_to_collection(collection, dry_run=dry_run)
    
    if dry_run:
        print(f"\n✅ Dry run complete - would import {imported} cards")
        collection.close()
        return True
    
    # Get stats after sync
    after_stats = collection.get_statistics()
    
    print(f"\n📊 Collection after sync:")
    print(f"   Total cards: {after_stats['total_cards']} (+{after_stats['total_cards'] - before_stats['total_cards']})")
    print(f"   Unique cards: {after_stats['unique_cards']} (+{after_stats['unique_cards'] - before_stats['unique_cards']})")
    
    collection.close()
    
    # Auto-enrich if requested
    if auto_enrich and imported > 0:
        print("\n🔍 Auto-enriching with Scryfall data...")
        print("   This may take several minutes...")
        
        try:
            from scripts.enrich_collection import enrich_collection
            
            enrich_collection(
                db_path=db_path,
                update_prices=True,
                cache_hours=24
            )
        except Exception as e:
            print(f"⚠️  Enrichment failed: {e}")
            print("   You can run enrichment manually later:")
            print("   python scripts/enrich_collection.py --update-prices")
    
    print("\n" + "=" * 60)
    print("✅ Sync complete!")
    print("=" * 60)
    
    return True


def setup_automated_sync(interval: str = "daily"):
    """
    Set up automated sync (Windows Task Scheduler / Linux cron)
    
    Args:
        interval: 'daily', 'weekly', or 'hourly'
    """
    script_path = Path(__file__).resolve()
    
    print(f"\n⚙️  Setting up {interval} automated sync...")
    print()
    
    if sys.platform == "win32":
        # Windows Task Scheduler
        task_name = "MTG-ManaBox-Sync"
        
        # Determine schedule
        if interval == "daily":
            schedule = "/SC DAILY /ST 09:00"
        elif interval == "weekly":
            schedule = "/SC WEEKLY /D SUN /ST 09:00"
        elif interval == "hourly":
            schedule = "/SC HOURLY"
        else:
            schedule = "/SC DAILY /ST 09:00"
        
        cmd = f'''schtasks /CREATE /TN "{task_name}" {schedule} /TR "python {script_path} --auto-enrich" /F'''
        
        print("Run this command in Command Prompt (as Administrator):")
        print()
        print(cmd)
        print()
        print("To verify: schtasks /Query /TN MTG-ManaBox-Sync")
        print("To delete: schtasks /DELETE /TN MTG-ManaBox-Sync /F")
    
    else:
        # Linux/Mac cron
        if interval == "daily":
            schedule = "0 9 * * *"
        elif interval == "weekly":
            schedule = "0 9 * * 0"
        elif interval == "hourly":
            schedule = "0 * * * *"
        else:
            schedule = "0 9 * * *"
        
        cron_line = f'{schedule} cd {script_path.parent.parent} && python {script_path} --auto-enrich >> logs/sync.log 2>&1'
        
        print("Add this line to your crontab (run: crontab -e):")
        print()
        print(cron_line)
        print()
        print("Logs will be saved to: logs/sync.log")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Sync MyManaBox to Collection Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync with auto-detection
  python scripts/sync_mymanabox.py
  
  # Sync specific path
  python scripts/sync_mymanabox.py --path "C:/Users/EHunt/Repos/Projects/MyManaBox"
  
  # Sync and enrich
  python scripts/sync_mymanabox.py --auto-enrich
  
  # Dry run to see what would sync
  python scripts/sync_mymanabox.py --dry-run
  
  # Set up automation
  python scripts/sync_mymanabox.py --setup-automation daily
        """
    )
    
    parser.add_argument(
        "--path",
        help="Path to MyManaBox installation (auto-detect if not provided)"
    )
    
    parser.add_argument(
        "--db",
        default="data/collections/main.db",
        help="Collection database path (default: data/collections/main.db)"
    )
    
    parser.add_argument(
        "--auto-enrich",
        action="store_true",
        help="Automatically enrich with Scryfall data after sync"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without actually syncing"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up MyManaBox data before sync"
    )
    
    parser.add_argument(
        "--setup-automation",
        choices=["daily", "weekly", "hourly"],
        help="Set up automated sync schedule"
    )
    
    args = parser.parse_args()
    
    # Setup automation
    if args.setup_automation:
        setup_automated_sync(args.setup_automation)
        return
    
    # Run sync
    success = sync_manabox(
        manabox_path=args.path,
        db_path=args.db,
        auto_enrich=args.auto_enrich,
        dry_run=args.dry_run,
        backup_first=not args.no_backup
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
