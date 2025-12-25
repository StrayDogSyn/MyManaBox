#!/usr/bin/env python3
"""
Consolidate ManaBox Exports

Combines multiple ManaBox CSV exports into a single consolidated file
with automatic deduplication and quantity merging.

Usage:
    python scripts/consolidate_manabox.py --input data/exports/manabox_sessions
    python scripts/consolidate_manabox.py --input data/exports --output consolidated.csv --dedupe
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict
import argparse


def read_manabox_csv(filepath: Path) -> List[Dict]:
    """Read a single ManaBox CSV export"""
    cards = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Normalize field names (ManaBox sometimes varies)
                card = {
                    "name": row.get("Card Name", row.get("name", "")),
                    "set_code": row.get("Set Code", row.get("set", "")),
                    "set_name": row.get("Set Name", row.get("set_name", "")),
                    "collector_number": row.get("Card Number", row.get("collector_number", "")),
                    "quantity": int(row.get("Quantity", row.get("quantity", 1))),
                    "language": row.get("Language", "English"),
                    "condition": row.get("Condition", "NM"),
                    "foil": row.get("Foil", "").lower() in ["foil", "yes", "true"],
                    "purchase_price": row.get("Purchase Price", ""),
                    "misprint": row.get("Misprint", "").lower() in ["yes", "true"]
                }
                
                cards.append(card)
        
        return cards
    
    except Exception as e:
        print(f"⚠️  Error reading {filepath}: {e}")
        return []


def consolidate_cards(all_cards: List[Dict], dedupe: bool = True) -> List[Dict]:
    """
    Consolidate cards from multiple sources
    
    If dedupe=True, merges duplicate cards by combining quantities
    """
    if not dedupe:
        return all_cards
    
    # Group by unique identifier: (name, set_code, collector_number, foil)
    card_groups = defaultdict(lambda: {
        "quantity": 0,
        "data": None
    })
    
    for card in all_cards:
        # Create unique key
        key = (
            card["name"].lower().strip(),
            card["set_code"].upper().strip(),
            card["collector_number"].strip(),
            card["foil"]
        )
        
        # Add quantity
        card_groups[key]["quantity"] += card["quantity"]
        
        # Store first occurrence's data
        if card_groups[key]["data"] is None:
            card_groups[key]["data"] = card.copy()
    
    # Build consolidated list
    consolidated = []
    for key, group in card_groups.items():
        card = group["data"]
        card["quantity"] = group["quantity"]
        consolidated.append(card)
    
    # Sort by name
    consolidated.sort(key=lambda c: c["name"])
    
    return consolidated


def write_consolidated_csv(cards: List[Dict], output_path: Path):
    """Write consolidated cards to CSV"""
    if not cards:
        print("❌ No cards to write!")
        return
    
    headers = [
        "Card Name", "Set Code", "Set Name", "Card Number",
        "Quantity", "Language", "Condition", "Foil",
        "Purchase Price", "Misprint"
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for card in cards:
            row = [
                card["name"],
                card["set_code"],
                card["set_name"],
                card["collector_number"],
                card["quantity"],
                card["language"],
                card["condition"],
                "Foil" if card["foil"] else "",
                card["purchase_price"],
                "Yes" if card["misprint"] else ""
            ]
            writer.writerow(row)
    
    print(f"✅ Wrote {len(cards)} cards to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate multiple ManaBox CSV exports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory containing ManaBox CSV files, or single CSV file"
    )
    
    parser.add_argument(
        "--output",
        default="data/exports/consolidated_collection.csv",
        help="Output CSV file path (default: data/exports/consolidated_collection.csv)"
    )
    
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Merge duplicate cards and combine quantities"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics before/after consolidation"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # Collect all CSV files
    if input_path.is_file():
        csv_files = [input_path]
    elif input_path.is_dir():
        csv_files = list(input_path.glob("*.csv"))
    else:
        print(f"❌ Invalid input path: {input_path}")
        sys.exit(1)
    
    if not csv_files:
        print(f"❌ No CSV files found in {input_path}")
        sys.exit(1)
    
    print(f"📥 Found {len(csv_files)} CSV file(s)")
    
    # Read all files
    all_cards = []
    for csv_file in csv_files:
        print(f"   Reading: {csv_file.name}")
        cards = read_manabox_csv(csv_file)
        all_cards.extend(cards)
        print(f"      Loaded {len(cards)} cards")
    
    print(f"\n📊 Total cards loaded: {len(all_cards)}")
    
    if args.stats:
        total_qty = sum(c["quantity"] for c in all_cards)
        foils = sum(1 for c in all_cards if c["foil"])
        print(f"   Total quantity: {total_qty}")
        print(f"   Foils: {foils}")
        print(f"   Languages: {len(set(c['language'] for c in all_cards))}")
    
    # Consolidate
    if args.dedupe:
        print(f"\n🔄 Deduplicating cards...")
        consolidated = consolidate_cards(all_cards, dedupe=True)
        
        duplicates_merged = len(all_cards) - len(consolidated)
        print(f"   Merged {duplicates_merged} duplicate entries")
        print(f"   Final unique cards: {len(consolidated)}")
    else:
        consolidated = all_cards
    
    if args.stats and args.dedupe:
        total_qty = sum(c["quantity"] for c in consolidated)
        print(f"   Final total quantity: {total_qty}")
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_consolidated_csv(consolidated, output_path)
    
    print(f"\n✅ Consolidation complete!")
    print(f"   Input: {len(csv_files)} file(s)")
    print(f"   Output: {output_path}")
    print(f"   Cards: {len(consolidated)} unique cards")
    
    if args.dedupe:
        print(f"\n💡 Next steps:")
        print(f"   1. Review {output_path} for errors")
        print(f"   2. Import to database:")
        print(f"      python src/catalogue.py --import {output_path}")


if __name__ == "__main__":
    main()
