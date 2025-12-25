#!/usr/bin/env python3
"""
MTG Collection Manager - Main Catalogue Application

Manages a local SQLite database of your Magic: The Gathering collection
with support for:
- ManaBox CSV imports
- Scryfall API enrichment
- TCGPlayer pricing integration
- Moxfield export generation
- Deck analysis and missing card detection
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import argparse


class Collection:
    """Main collection database manager"""
    
    def __init__(self, db_path: str = "data/collections/main.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database schema if it doesn't exist"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return dicts instead of tuples
        
        cursor = self.conn.cursor()
        
        # Main cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                set_code TEXT NOT NULL,
                set_name TEXT,
                collector_number TEXT,
                quantity INTEGER DEFAULT 1,
                foil BOOLEAN DEFAULT 0,
                condition TEXT DEFAULT 'NM',
                language TEXT DEFAULT 'English',
                
                -- Scryfall enrichment
                scryfall_id TEXT,
                type_line TEXT,
                mana_cost TEXT,
                cmc REAL,
                colors TEXT,  -- JSON array
                rarity TEXT,
                image_url TEXT,
                
                -- Pricing
                market_price REAL,
                foil_price REAL,
                buylist_price REAL,
                price_updated_at TEXT,
                
                -- Metadata
                tags TEXT,  -- JSON array
                notes TEXT,
                purchase_price REAL,
                purchase_date TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                -- Create unique constraint on name + set + foil
                UNIQUE(name, set_code, collector_number, foil)
            )
        """)
        
        # Decks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                format TEXT,
                commander TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Deck cards (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deck_cards (
                deck_id INTEGER,
                card_id INTEGER,
                quantity INTEGER DEFAULT 1,
                category TEXT DEFAULT 'main',  -- 'main', 'sideboard', 'commander'
                FOREIGN KEY (deck_id) REFERENCES decks(id),
                FOREIGN KEY (card_id) REFERENCES cards(id),
                PRIMARY KEY (deck_id, card_id, category)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_set ON cards(set_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_scryfall ON cards(scryfall_id)")
        
        self.conn.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    def add_card(self, card_data: Dict) -> int:
        """
        Add a single card to the collection
        
        Returns: card_id
        """
        cursor = self.conn.cursor()
        
        # Convert JSON fields
        colors = json.dumps(card_data.get("colors", []))
        tags = json.dumps(card_data.get("tags", []))
        
        try:
            cursor.execute("""
                INSERT INTO cards (
                    name, set_code, set_name, collector_number,
                    quantity, foil, condition, language,
                    scryfall_id, type_line, mana_cost, cmc, colors, rarity,
                    image_url, market_price, foil_price, buylist_price,
                    tags, notes, purchase_price, purchase_date,
                    price_updated_at
                ) VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?
                )
            """, (
                card_data["name"],
                card_data.get("set_code", card_data.get("set", "")),
                card_data.get("set_name"),
                card_data.get("collector_number"),
                card_data.get("quantity", 1),
                card_data.get("foil", False),
                card_data.get("condition", "NM"),
                card_data.get("language", "English"),
                card_data.get("scryfall_id"),
                card_data.get("type_line"),
                card_data.get("mana_cost"),
                card_data.get("cmc"),
                colors,
                card_data.get("rarity"),
                card_data.get("image_url"),
                card_data.get("market_price"),
                card_data.get("foil_price"),
                card_data.get("buylist_price"),
                tags,
                card_data.get("notes"),
                card_data.get("purchase_price"),
                card_data.get("purchase_date"),
                card_data.get("price_updated_at")
            ))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # Card already exists, update quantity instead
            cursor.execute("""
                UPDATE cards
                SET quantity = quantity + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
                  AND set_code = ?
                  AND collector_number = ?
                  AND foil = ?
            """, (
                card_data.get("quantity", 1),
                card_data["name"],
                card_data.get("set_code", card_data.get("set", "")),
                card_data.get("collector_number"),
                card_data.get("foil", False)
            ))
            self.conn.commit()
            
            # Get the existing card_id
            cursor.execute("""
                SELECT id FROM cards
                WHERE name = ? AND set_code = ? AND collector_number = ? AND foil = ?
            """, (
                card_data["name"],
                card_data.get("set_code", card_data.get("set", "")),
                card_data.get("collector_number"),
                card_data.get("foil", False)
            ))
            
            return cursor.fetchone()[0]
    
    def bulk_insert(self, cards: List[Dict], dedupe: bool = True) -> int:
        """
        Insert multiple cards efficiently
        
        Returns: number of cards added/updated
        """
        added = 0
        updated = 0
        
        for card in cards:
            try:
                card_id = self.add_card(card)
                if card_id:
                    added += 1
            except Exception as e:
                print(f"⚠️  Error adding {card.get('name')}: {e}")
                continue
        
        print(f"✅ Bulk insert complete: {added} cards processed")
        return added
    
    def search_cards(self, query: str = None, filters: Dict = None) -> List[Dict]:
        """
        Search collection with optional filters
        
        filters: {
            'set': 'NEO',
            'rarity': 'rare',
            'colors': ['R'],
            'min_price': 5.0,
            'foil': True
        }
        """
        cursor = self.conn.cursor()
        
        sql = "SELECT * FROM cards WHERE 1=1"
        params = []
        
        if query:
            sql += " AND name LIKE ?"
            params.append(f"%{query}%")
        
        if filters:
            if "set" in filters:
                sql += " AND set_code = ?"
                params.append(filters["set"])
            
            if "rarity" in filters:
                sql += " AND rarity = ?"
                params.append(filters["rarity"])
            
            if "foil" in filters:
                sql += " AND foil = ?"
                params.append(filters["foil"])
            
            if "min_price" in filters:
                sql += " AND market_price >= ?"
                params.append(filters["min_price"])
            
            if "colors" in filters:
                # Note: This is simplified; proper color filtering needs JSON parsing
                colors_json = json.dumps(filters["colors"])
                sql += " AND colors = ?"
                params.append(colors_json)
        
        cursor.execute(sql, params)
        
        results = []
        for row in cursor.fetchall():
            card = dict(row)
            # Parse JSON fields
            card["colors"] = json.loads(card["colors"]) if card["colors"] else []
            card["tags"] = json.loads(card["tags"]) if card["tags"] else []
            results.append(card)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get collection statistics"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total cards
        cursor.execute("SELECT SUM(quantity) FROM cards")
        stats["total_cards"] = cursor.fetchone()[0] or 0
        
        # Unique cards
        cursor.execute("SELECT COUNT(DISTINCT name) FROM cards")
        stats["unique_cards"] = cursor.fetchone()[0] or 0
        
        # Total value
        cursor.execute("SELECT SUM(quantity * COALESCE(market_price, 0)) FROM cards")
        stats["total_value"] = round(cursor.fetchone()[0] or 0, 2)
        
        # By rarity
        cursor.execute("""
            SELECT rarity, COUNT(*), SUM(quantity)
            FROM cards
            WHERE rarity IS NOT NULL
            GROUP BY rarity
        """)
        stats["by_rarity"] = {row[0]: {"unique": row[1], "total": row[2]} 
                              for row in cursor.fetchall()}
        
        # By set
        cursor.execute("""
            SELECT set_code, set_name, COUNT(*), SUM(quantity)
            FROM cards
            WHERE set_code IS NOT NULL
            GROUP BY set_code, set_name
            ORDER BY SUM(quantity) DESC
            LIMIT 10
        """)
        stats["top_sets"] = [
            {"set": row[0], "name": row[1], "unique": row[2], "total": row[3]}
            for row in cursor.fetchall()
        ]
        
        return stats
    
    def export_to_csv(self, output_path: str, format_type: str = "standard"):
        """
        Export collection to CSV
        
        format_type: 'standard', 'moxfield', 'deckbox'
        """
        cards = self.search_cards()
        
        if format_type == "moxfield":
            headers = [
                "Count", "Tradelist Count", "Name", "Edition",
                "Condition", "Language", "Foil", "Tags",
                "Last Modified", "Collector Number", "Alter",
                "Proxy", "Purchase Price"
            ]
            
            rows = []
            for card in cards:
                row = [
                    card["quantity"],
                    0,  # Tradelist count
                    card["name"],
                    card["set_code"],
                    card["condition"],
                    card["language"],
                    "foil" if card["foil"] else "",
                    ";".join(card["tags"]),
                    datetime.now().strftime("%Y-%m-%d"),
                    card["collector_number"] or "",
                    "",  # Alter
                    "",  # Proxy
                    card["purchase_price"] or ""
                ]
                rows.append(row)
        
        else:  # Standard format
            headers = [
                "Name", "Set", "Set Name", "Quantity", "Foil",
                "Condition", "Language", "Collector Number",
                "Market Price", "Total Value", "Tags"
            ]
            
            rows = []
            for card in cards:
                row = [
                    card["name"],
                    card["set_code"],
                    card["set_name"] or "",
                    card["quantity"],
                    "Yes" if card["foil"] else "No",
                    card["condition"],
                    card["language"],
                    card["collector_number"] or "",
                    f"${card['market_price']:.2f}" if card["market_price"] else "",
                    f"${(card['quantity'] * (card['market_price'] or 0)):.2f}",
                    ";".join(card["tags"])
                ]
                rows.append(row)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"✅ Exported {len(rows)} cards to {output_path}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def import_manabox_csv(csv_path: str, collection: Collection) -> int:
    """Import cards from ManaBox CSV export"""
    cards = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            card = {
                "name": row["Card Name"],
                "set_code": row["Set Code"],
                "set_name": row["Set Name"],
                "collector_number": row.get("Card Number", ""),
                "quantity": int(row.get("Quantity", 1)),
                "language": row.get("Language", "English"),
                "condition": row.get("Condition", "NM"),
                "foil": row.get("Foil", "").lower() == "foil",
                "purchase_price": float(row["Purchase Price"]) if row.get("Purchase Price") else None,
            }
            cards.append(card)
    
    print(f"📥 Importing {len(cards)} cards from ManaBox...")
    return collection.bulk_insert(cards)


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="MTG Collection Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize new database"
    )
    
    parser.add_argument(
        "--import",
        dest="import_file",
        help="Import ManaBox CSV file"
    )
    
    parser.add_argument(
        "--export",
        dest="export_file",
        help="Export collection to CSV"
    )
    
    parser.add_argument(
        "--format",
        choices=["standard", "moxfield", "deckbox"],
        default="standard",
        help="Export format (default: standard)"
    )
    
    parser.add_argument(
        "--search",
        help="Search for cards by name"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show collection statistics"
    )
    
    parser.add_argument(
        "--db",
        default="data/collections/main.db",
        help="Database path (default: data/collections/main.db)"
    )
    
    args = parser.parse_args()
    
    # Initialize collection
    collection = Collection(args.db)
    
    try:
        if args.init:
            print("✅ Database initialized")
        
        if args.import_file:
            import_manabox_csv(args.import_file, collection)
        
        if args.export_file:
            collection.export_to_csv(args.export_file, args.format)
        
        if args.search:
            results = collection.search_cards(args.search)
            print(f"\n🔍 Found {len(results)} cards matching '{args.search}':")
            for card in results[:20]:  # Show first 20
                print(f"  {card['quantity']}x {card['name']} ({card['set_code']}) - "
                      f"${card['market_price'] or 0:.2f}")
        
        if args.stats:
            stats = collection.get_statistics()
            print("\n📊 Collection Statistics:")
            print(f"  Total Cards: {stats['total_cards']:,}")
            print(f"  Unique Cards: {stats['unique_cards']:,}")
            print(f"  Total Value: ${stats['total_value']:,.2f}")
            
            print("\n  By Rarity:")
            for rarity, data in stats["by_rarity"].items():
                print(f"    {rarity}: {data['total']} cards ({data['unique']} unique)")
            
            print("\n  Top 10 Sets:")
            for set_data in stats["top_sets"]:
                print(f"    {set_data['set']} - {set_data['name']}: "
                      f"{set_data['total']} cards ({set_data['unique']} unique)")
    
    finally:
        collection.close()


if __name__ == "__main__":
    main()
