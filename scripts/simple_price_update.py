#!/usr/bin/env python3
"""
Simple price update script to improve collection values to better match Moxfield.

This script focuses on the core improvements identified in the pricing analysis.
"""

import sys
import pandas as pd
from pathlib import Path
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.card import Card
from data.csv_loader import CSVLoader
from data.scryfall_client import ScryfallClient


def update_collection_prices(csv_path: str, output_path: str = None):
    """Update collection prices with current Scryfall data."""
    
    print("🔄 MyManaBox Price Update Tool")
    print("=" * 40)
    
    # Load current collection
    print(f"📁 Loading collection from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        print(f"   Loaded {len(df)} cards from CSV")
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False
    
    # Calculate current totals
    current_total = Decimal('0')
    cards_with_prices = 0
    
    print("\n📊 Current Collection Analysis:")
    
    for idx, row in df.iterrows():
        try:
            card = Card.from_csv_row(row.to_dict())
            if card.total_value > 0:
                current_total += card.total_value
                cards_with_prices += 1
        except Exception as e:
            print(f"   Warning: Error processing card {row.get('Name', 'Unknown')}: {e}")
    
    print(f"   Current total value: ${current_total:,.2f}")
    print(f"   Cards with pricing: {cards_with_prices:,}")
    print(f"   Cards without pricing: {len(df) - cards_with_prices:,}")
    
    # Initialize Scryfall client for updates
    print(f"\n🔍 Updating prices from Scryfall API...")
    scryfall = ScryfallClient()
    
    updated_cards = 0
    price_improvements = Decimal('0')
    
    for idx, row in df.iterrows():
        try:
            card_name = row.get('Name', '')
            card_set = row.get('Edition', '') or row.get('Set Name', '')
            
            # Skip if we already have good pricing
            current_card = Card.from_csv_row(row.to_dict())
            if current_card.purchase_price and current_card.market_value:
                continue
            
            # Try to get updated Scryfall data
            print(f"   Updating: {card_name}...")
            
            scryfall_data = scryfall.search_card(card_name, card_set)
            
            if scryfall_data and scryfall_data.get('prices'):
                prices = scryfall_data['prices']
                
                # Update USD Price if missing
                if pd.isna(row.get('USD Price')) and prices.get('usd'):
                    df.at[idx, 'USD Price'] = float(prices['usd'])
                    updated_cards += 1
                    price_improvements += Decimal(str(prices['usd'])) * int(row.get('Count', 1))
                
                # Update USD Foil Price if card is foil and missing foil price
                foil_status = str(row.get('Foil', '')).lower()
                if foil_status in ['foil', 'etched'] and pd.isna(row.get('USD Foil Price')) and prices.get('usd_foil'):
                    df.at[idx, 'USD Foil Price'] = float(prices['usd_foil'])
                    updated_cards += 1
                    
            # Rate limiting
            if updated_cards % 10 == 0:
                print(f"     Updated {updated_cards} cards so far...")
                
        except Exception as e:
            print(f"   Warning: Failed to update {card_name}: {e}")
            continue
    
    # Save updated collection
    output_file = output_path or csv_path.replace('.csv', '_price_updated.csv')
    
    print(f"\n💾 Saving updated collection to: {output_file}")
    df.to_csv(output_file, index=False)
    
    # Calculate new totals
    new_total = Decimal('0')
    new_cards_with_prices = 0
    
    for idx, row in df.iterrows():
        try:
            card = Card.from_csv_row(row.to_dict())
            if card.total_value > 0:
                new_total += card.total_value
                new_cards_with_prices += 1
        except:
            continue
    
    print(f"\n✅ Price Update Complete!")
    print(f"   Cards updated: {updated_cards}")
    print(f"   Value before: ${current_total:,.2f}")
    print(f"   Value after: ${new_total:,.2f}")
    print(f"   Improvement: ${new_total - current_total:,.2f}")
    print(f"   Cards with pricing: {cards_with_prices} → {new_cards_with_prices}")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update MyManaBox collection prices")
    parser.add_argument("csv_file", help="Path to collection CSV file")
    parser.add_argument("-o", "--output", help="Output file path (default: input_file_price_updated.csv)")
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"❌ Error: File {csv_path} not found")
        return 1
    
    try:
        success = update_collection_prices(str(csv_path), args.output)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️ Update cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    # Default run for testing
    csv_path = Path(__file__).parent.parent / "data" / "enriched_collection_complete.csv"
    if csv_path.exists():
        update_collection_prices(str(csv_path))
    else:
        print("❌ Default collection file not found. Run with: python update_prices.py <csv_file>")
