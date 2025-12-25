#!/usr/bin/env python3
"""
Enrich Collection with Scryfall Data

Adds comprehensive card data to your collection from Scryfall API:
- Card types and Oracle text
- Current market prices
- Mana costs and color identity
- Card images
- Rarity information

Usage:
    python scripts/enrich_collection.py
    python scripts/enrich_collection.py --update-prices --cache 24h
    python scripts/enrich_collection.py --cards "Lightning Bolt,Force of Will"
"""

import sys
from pathlib import Path
import argparse
import sqlite3
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_clients.scryfall import ScryfallClient


def enrich_collection(
    db_path: str,
    update_prices: bool = True,
    cache_hours: int = 24,
    specific_cards: list = None,
    batch_size: int = 100
):
    """
    Enrich collection database with Scryfall data
    
    Args:
        db_path: Path to SQLite database
        update_prices: Update pricing information
        cache_hours: Cache duration for Scryfall responses
        specific_cards: List of specific card names to update (None = all)
        batch_size: Number of cards to process before committing
    """
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get cards to enrich
    if specific_cards:
        placeholders = ",".join("?" * len(specific_cards))
        cursor.execute(f"""
            SELECT id, name, set_code, scryfall_id
            FROM cards
            WHERE name IN ({placeholders})
        """, specific_cards)
    else:
        # Get all cards without Scryfall data or old prices
        cursor.execute("""
            SELECT id, name, set_code, scryfall_id
            FROM cards
            WHERE scryfall_id IS NULL
               OR (price_updated_at IS NULL OR 
                   datetime(price_updated_at) < datetime('now', '-' || ? || ' hours'))
            ORDER BY name
        """, (cache_hours,))
    
    cards_to_update = cursor.fetchall()
    total = len(cards_to_update)
    
    if total == 0:
        print("✅ All cards already enriched and prices are current!")
        conn.close()
        return
    
    print(f"📊 Found {total} cards to enrich")
    print(f"   Cache duration: {cache_hours}h")
    print(f"   Batch size: {batch_size}")
    print()
    
    # Initialize Scryfall client
    client = ScryfallClient(cache_enabled=True)
    
    # Process cards
    updated = 0
    errors = 0
    
    for i, card_row in enumerate(cards_to_update, 1):
        card_id = card_row["id"]
        card_name = card_row["name"]
        set_code = card_row["set_code"]
        
        # Progress indicator
        percent = (i / total) * 100
        print(f"[{i}/{total}] ({percent:.1f}%) Enriching: {card_name} ({set_code})", end='\r')
        
        try:
            # Get Scryfall data
            scryfall_data = client.get_card(card_name, set_code)
            
            if not scryfall_data:
                errors += 1
                continue
            
            # Extract relevant fields
            scryfall_id = scryfall_data["id"]
            type_line = scryfall_data.get("type_line")
            mana_cost = scryfall_data.get("mana_cost")
            cmc = scryfall_data.get("cmc")
            colors = json.dumps(scryfall_data.get("colors", []))
            rarity = scryfall_data.get("rarity")
            
            # Get image URL (handle double-faced cards)
            if "image_uris" in scryfall_data:
                image_url = scryfall_data["image_uris"].get("normal")
            elif "card_faces" in scryfall_data:
                image_url = scryfall_data["card_faces"][0]["image_uris"].get("normal")
            else:
                image_url = None
            
            # Get prices
            prices = scryfall_data.get("prices", {})
            market_price = float(prices.get("usd") or 0)
            foil_price = float(prices.get("usd_foil") or 0)
            
            # Update database
            cursor.execute("""
                UPDATE cards
                SET scryfall_id = ?,
                    type_line = ?,
                    mana_cost = ?,
                    cmc = ?,
                    colors = ?,
                    rarity = ?,
                    image_url = ?,
                    market_price = ?,
                    foil_price = ?,
                    price_updated_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                scryfall_id,
                type_line,
                mana_cost,
                cmc,
                colors,
                rarity,
                image_url,
                market_price if update_prices else None,
                foil_price if update_prices else None,
                datetime.now().isoformat() if update_prices else None,
                card_id
            ))
            
            updated += 1
            
            # Commit in batches
            if updated % batch_size == 0:
                conn.commit()
                print(f"\n   ✓ Committed batch (total: {updated})")
        
        except Exception as e:
            print(f"\n⚠️  Error enriching {card_name}: {e}")
            errors += 1
            continue
    
    # Final commit
    conn.commit()
    conn.close()
    
    print(f"\n\n✅ Enrichment complete!")
    print(f"   Updated: {updated} cards")
    print(f"   Errors: {errors} cards")
    print(f"   Success rate: {(updated/(updated+errors)*100):.1f}%")
    
    if errors > 0:
        print(f"\n💡 Tip: Re-run to retry failed cards")


def update_specific_cards(db_path: str, card_names: list):
    """Quick update for specific cards"""
    print(f"🎯 Updating {len(card_names)} specific cards...")
    enrich_collection(
        db_path=db_path,
        update_prices=True,
        cache_hours=0,  # Force fresh data
        specific_cards=card_names
    )


def get_statistics(db_path: str):
    """Show enrichment statistics"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total cards
    cursor.execute("SELECT COUNT(*) FROM cards")
    total = cursor.fetchone()[0]
    
    # Enriched cards
    cursor.execute("SELECT COUNT(*) FROM cards WHERE scryfall_id IS NOT NULL")
    enriched = cursor.fetchone()[0]
    
    # Priced cards
    cursor.execute("SELECT COUNT(*) FROM cards WHERE market_price IS NOT NULL AND market_price > 0")
    priced = cursor.fetchone()[0]
    
    # Recent price updates (last 24h)
    cursor.execute("""
        SELECT COUNT(*) FROM cards 
        WHERE price_updated_at IS NOT NULL 
          AND datetime(price_updated_at) > datetime('now', '-24 hours')
    """)
    recent = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 Enrichment Statistics:")
    print(f"   Total cards: {total}")
    print(f"   Enriched: {enriched} ({enriched/total*100:.1f}%)")
    print(f"   With prices: {priced} ({priced/total*100:.1f}%)")
    print(f"   Updated (24h): {recent} ({recent/total*100:.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Enrich MTG collection with Scryfall data",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--db",
        default="data/collections/main.db",
        help="Database path (default: data/collections/main.db)"
    )
    
    parser.add_argument(
        "--update-prices",
        action="store_true",
        help="Update card prices (default: False)"
    )
    
    parser.add_argument(
        "--cache",
        default="24h",
        help="Cache duration (e.g., 24h, 168h for 1 week) (default: 24h)"
    )
    
    parser.add_argument(
        "--cards",
        help="Comma-separated list of specific cards to update"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show enrichment statistics and exit"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for commits (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Parse cache duration
    cache_str = args.cache.lower()
    if cache_str.endswith('h'):
        cache_hours = int(cache_str[:-1])
    elif cache_str.endswith('d'):
        cache_hours = int(cache_str[:-1]) * 24
    else:
        cache_hours = int(cache_str)
    
    # Check database exists
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"   Run: python src/catalogue.py --init")
        sys.exit(1)
    
    # Show stats and exit
    if args.stats:
        get_statistics(args.db)
        return
    
    # Update specific cards
    if args.cards:
        card_names = [c.strip() for c in args.cards.split(",")]
        update_specific_cards(args.db, card_names)
        return
    
    # Full enrichment
    print("🚀 Starting collection enrichment...")
    print(f"   Database: {args.db}")
    print(f"   Update prices: {args.update_prices}")
    print(f"   Cache: {cache_hours}h")
    print()
    
    enrich_collection(
        db_path=args.db,
        update_prices=args.update_prices,
        cache_hours=cache_hours,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
