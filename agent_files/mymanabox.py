#!/usr/bin/env python3
"""
MyManaBox Integration Module

Provides direct access to your local MyManaBox application data,
enabling seamless sync between MyManaBox and mtg-collection-manager.

Usage:
    from src.integrations.mymanabox import MyManaBoxReader
    
    reader = MyManaBoxReader("C:/Users/EHunt/Repos/Projects/MyManaBox")
    cards = reader.get_all_cards()
    reader.sync_to_collection(collection)
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import shutil
from datetime import datetime


class MyManaBoxReader:
    """
    Read data from local MyManaBox installation
    
    Supports:
    - JSON-based storage (card_cache.json)
    - SQLite database (if present)
    - Direct file access
    """
    
    def __init__(self, manabox_path: str = None):
        """
        Initialize reader with MyManaBox installation path
        
        Args:
            manabox_path: Path to MyManaBox folder (default: auto-detect)
        """
        if manabox_path is None:
            # Try to auto-detect common locations
            possible_paths = [
                Path("C:/Users/EHunt/Repos/Projects/MyManaBox"),
                Path.home() / "Repos/Projects/MyManaBox",
                Path("~/Projects/MyManaBox").expanduser(),
            ]
            
            for path in possible_paths:
                if path.exists():
                    manabox_path = str(path)
                    break
        
        if manabox_path is None:
            raise FileNotFoundError(
                "MyManaBox installation not found. "
                "Please provide path explicitly."
            )
        
        self.manabox_path = Path(manabox_path)
        
        if not self.manabox_path.exists():
            raise FileNotFoundError(f"MyManaBox path does not exist: {self.manabox_path}")
        
        print(f"📂 Connected to MyManaBox: {self.manabox_path}")
        
        # Locate data files
        self.card_cache = self.manabox_path / "card_cache.json"
        self.collection_db = self._find_database()
    
    def _find_database(self) -> Optional[Path]:
        """Find SQLite database in MyManaBox folder"""
        # Common database filenames
        db_names = [
            "collection.db",
            "manabox.db",
            "cards.db",
            "collection.sqlite",
            "manabox.sqlite"
        ]
        
        for db_name in db_names:
            db_path = self.manabox_path / db_name
            if db_path.exists():
                print(f"   ✓ Found database: {db_name}")
                return db_path
        
        # Search for any .db or .sqlite file
        for ext in ["*.db", "*.sqlite", "*.sqlite3"]:
            found = list(self.manabox_path.glob(ext))
            if found:
                print(f"   ✓ Found database: {found[0].name}")
                return found[0]
        
        print("   ⚠️  No database found (will use JSON cache)")
        return None
    
    def get_all_cards_from_json(self) -> List[Dict]:
        """
        Read cards from card_cache.json
        
        Returns:
            List of card dictionaries
        """
        if not self.card_cache.exists():
            print(f"⚠️  card_cache.json not found at {self.card_cache}")
            return []
        
        try:
            with open(self.card_cache, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                cards = data
            elif isinstance(data, dict):
                # Try common key names
                for key in ["cards", "collection", "data", "cache"]:
                    if key in data:
                        cards = data[key]
                        break
                else:
                    # If it's a dict of cards, convert to list
                    cards = list(data.values()) if data else []
            else:
                print(f"⚠️  Unexpected JSON structure: {type(data)}")
                return []
            
            print(f"✅ Loaded {len(cards)} cards from JSON cache")
            return cards
        
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse card_cache.json: {e}")
            return []
    
    def get_all_cards_from_db(self) -> List[Dict]:
        """
        Read cards from SQLite database (if present)
        
        Returns:
            List of card dictionaries
        """
        if not self.collection_db:
            return []
        
        try:
            conn = sqlite3.connect(self.collection_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Try to find the cards table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"   Found tables: {', '.join(tables)}")
            
            # Common table names
            cards_table = None
            for table_name in ["cards", "collection", "card_collection", "inventory"]:
                if table_name in tables:
                    cards_table = table_name
                    break
            
            if not cards_table:
                # Use first table that isn't sqlite_* or system table
                non_system_tables = [t for t in tables if not t.startswith("sqlite_")]
                if non_system_tables:
                    cards_table = non_system_tables[0]
            
            if not cards_table:
                print("⚠️  No cards table found in database")
                conn.close()
                return []
            
            # Read all cards
            cursor.execute(f"SELECT * FROM {cards_table}")
            rows = cursor.fetchall()
            
            # Convert to dicts
            cards = [dict(row) for row in rows]
            
            conn.close()
            
            print(f"✅ Loaded {len(cards)} cards from database")
            return cards
        
        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return []
    
    def get_all_cards(self, prefer_db: bool = True) -> List[Dict]:
        """
        Get all cards from best available source
        
        Args:
            prefer_db: Prefer database over JSON cache if both exist
        
        Returns:
            List of card dictionaries
        """
        if prefer_db and self.collection_db:
            cards = self.get_all_cards_from_db()
            if cards:
                return cards
        
        # Fallback to JSON
        return self.get_all_cards_from_json()
    
    def normalize_card_data(self, card: Dict) -> Dict:
        """
        Normalize MyManaBox card data to standard format
        
        Handles different field names and structures from MyManaBox
        """
        # Common field mappings
        field_map = {
            "card_name": "name",
            "cardName": "name",
            "card": "name",
            "set": "set_code",
            "setCode": "set_code",
            "set_code": "set_code",
            "edition": "set_code",
            "collector_number": "collector_number",
            "collectorNumber": "collector_number",
            "number": "collector_number",
            "qty": "quantity",
            "count": "quantity",
            "amount": "quantity",
            "is_foil": "foil",
            "isFoil": "foil",
        }
        
        normalized = {}
        
        # Map known fields
        for old_key, new_key in field_map.items():
            if old_key in card:
                normalized[new_key] = card[old_key]
        
        # Copy unmapped fields
        for key, value in card.items():
            if key not in field_map and key.lower() not in normalized:
                normalized[key] = value
        
        # Set defaults
        normalized.setdefault("quantity", 1)
        normalized.setdefault("condition", "NM")
        normalized.setdefault("language", "English")
        normalized.setdefault("foil", False)
        
        return normalized
    
    def sync_to_collection(self, collection, dry_run: bool = False):
        """
        Sync MyManaBox cards to mtg-collection-manager
        
        Args:
            collection: Collection instance from catalogue.py
            dry_run: If True, only show what would be synced
        """
        cards = self.get_all_cards()
        
        if not cards:
            print("❌ No cards found in MyManaBox")
            return 0
        
        print(f"\n🔄 Syncing {len(cards)} cards from MyManaBox...")
        
        # Normalize all cards
        normalized_cards = [self.normalize_card_data(card) for card in cards]
        
        if dry_run:
            print("\n📋 DRY RUN - Would import:")
            for i, card in enumerate(normalized_cards[:10], 1):
                print(f"   {i}. {card.get('name')} ({card.get('set_code')})")
            
            if len(normalized_cards) > 10:
                print(f"   ... and {len(normalized_cards) - 10} more")
            
            return len(normalized_cards)
        
        # Import to collection
        imported = collection.bulk_insert(normalized_cards, dedupe=True)
        
        print(f"✅ Sync complete: {imported} cards imported")
        return imported
    
    def export_to_csv(self, output_path: str):
        """
        Export MyManaBox collection to CSV for manual import
        
        Args:
            output_path: Where to save the CSV file
        """
        import csv
        
        cards = self.get_all_cards()
        
        if not cards:
            print("❌ No cards to export")
            return
        
        # Normalize all cards
        normalized = [self.normalize_card_data(card) for card in cards]
        
        # Write CSV
        headers = ["Card Name", "Set Code", "Quantity", "Foil", "Condition", "Language"]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for card in normalized:
                row = [
                    card.get("name", ""),
                    card.get("set_code", ""),
                    card.get("quantity", 1),
                    "Foil" if card.get("foil") else "",
                    card.get("condition", "NM"),
                    card.get("language", "English")
                ]
                writer.writerow(row)
        
        print(f"✅ Exported {len(normalized)} cards to {output_path}")
    
    def backup_manabox_data(self, backup_dir: str = None):
        """
        Create backup of MyManaBox data files
        
        Args:
            backup_dir: Where to save backup (default: data/backups/manabox)
        """
        if backup_dir is None:
            backup_dir = Path("data/backups/manabox")
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"manabox_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # Backup JSON cache
        if self.card_cache.exists():
            shutil.copy2(self.card_cache, backup_path / "card_cache.json")
            print(f"   ✓ Backed up card_cache.json")
        
        # Backup database
        if self.collection_db:
            shutil.copy2(self.collection_db, backup_path / self.collection_db.name)
            print(f"   ✓ Backed up {self.collection_db.name}")
        
        print(f"✅ Backup saved to: {backup_path}")
        return backup_path


def main():
    """Test the MyManaBox integration"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="MyManaBox Integration Tool")
    
    parser.add_argument(
        "--path",
        default="C:/Users/EHunt/Repos/Projects/MyManaBox",
        help="Path to MyManaBox installation"
    )
    
    parser.add_argument(
        "--action",
        choices=["list", "export", "sync", "backup"],
        default="list",
        help="Action to perform"
    )
    
    parser.add_argument(
        "--output",
        help="Output file for export action"
    )
    
    args = parser.parse_args()
    
    # Initialize reader
    try:
        reader = MyManaBoxReader(args.path)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # Perform action
    if args.action == "list":
        cards = reader.get_all_cards()
        print(f"\n📊 Found {len(cards)} cards")
        
        if cards:
            print("\nFirst 5 cards:")
            for i, card in enumerate(cards[:5], 1):
                normalized = reader.normalize_card_data(card)
                print(f"   {i}. {normalized.get('name')} ({normalized.get('set_code')})")
    
    elif args.action == "export":
        output = args.output or f"exports/manabox_export_{datetime.now().strftime('%Y%m%d')}.csv"
        reader.export_to_csv(output)
    
    elif args.action == "sync":
        # Import collection manager
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from src.catalogue import Collection
        
        collection = Collection()
        reader.sync_to_collection(collection, dry_run=False)
    
    elif args.action == "backup":
        reader.backup_manabox_data()


if __name__ == "__main__":
    main()
