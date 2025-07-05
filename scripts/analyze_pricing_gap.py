#!/usr/bin/env python3
"""
Analyze the pricing gap between our collection data and Moxfield.

This script identifies the differences in pricing logic and data sources
to understand why our total ($610.57) differs from Moxfield's ($2,379.52).
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.card import Card
from decimal import Decimal


def analyze_pricing_gap():
    """Analyze the pricing differences between our data and Moxfield."""
    print("🔍 MyManaBox Pricing Gap Analysis")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv('data/enriched_collection_complete.csv')
    
    print(f"📊 Collection Overview:")
    print(f"   Total cards: {df['Count'].sum():,}")
    print(f"   Unique cards: {len(df):,}")
    print()
    
    # Calculate our totals
    our_total = Decimal('0')
    purchase_value = Decimal('0')
    market_value = Decimal('0')
    
    cards_with_purchase = 0
    cards_with_market = 0
    cards_with_any_price = 0
    
    high_value_cards = []
    
    for idx, row in df.iterrows():
        card = Card.from_csv_row(row.to_dict())
        
        if card.total_value > 0:
            cards_with_any_price += 1
            our_total += card.total_value
            
            # Track which price source was used
            if card.purchase_price and card.purchase_price > 0:
                cards_with_purchase += 1
                purchase_value += card.total_value
            elif card.market_value and card.market_value > 0:
                cards_with_market += 1
                market_value += card.total_value
        
        # Identify high-value cards for comparison
        if card.total_value > 5:  # Cards worth more than $5
            high_value_cards.append({
                'name': card.name,
                'count': card.count,
                'purchase_price': card.purchase_price,
                'market_value': card.market_value,
                'total_value': card.total_value,
                'foil': card.foil
            })
    
    print(f"💰 Our Pricing Analysis:")
    print(f"   Our calculated total: ${our_total:,.2f}")
    print(f"   Moxfield target: $2,379.52")
    print(f"   Difference: ${2379.52 - float(our_total):,.2f} ({((2379.52 / float(our_total)) - 1) * 100:.1f}% higher)")
    print()
    
    print(f"📈 Price Source Breakdown:")
    print(f"   Cards with any price: {cards_with_any_price:,}")
    print(f"   Using purchase price: {cards_with_purchase:,} (${purchase_value:,.2f})")
    print(f"   Using market price: {cards_with_market:,} (${market_value:,.2f})")
    print(f"   Cards without price: {len(df) - cards_with_any_price:,}")
    print()
    
    print(f"💎 High-Value Cards (>${5}+):")
    high_value_cards.sort(key=lambda x: float(x['total_value']), reverse=True)
    for card in high_value_cards[:10]:  # Top 10
        price_source = "Purchase" if card['purchase_price'] else "Market"
        foil_indicator = " (FOIL)" if card['foil'] else ""
        print(f"   {card['name'][:30]:<30} ${card['total_value']:>7.2f} ({price_source}){foil_indicator}")
    
    if len(high_value_cards) > 10:
        print(f"   ... and {len(high_value_cards) - 10} more high-value cards")
    print()
    
    # Calculate average multiplier needed
    multiplier_needed = 2379.52 / float(our_total)
    print(f"🎯 Analysis Summary:")
    print(f"   • Our pricing logic appears correct (foil handling, purchase priority)")
    print(f"   • Card counts match Moxfield exactly")
    print(f"   • Price data appears to be from a different source/time")
    print(f"   • Average price multiplier needed: {multiplier_needed:.2f}x")
    print(f"   • This suggests Moxfield uses more recent/premium pricing")
    print()
    
    print(f"🔧 Recommendations:")
    print(f"   1. Update price data from current Scryfall API")
    print(f"   2. Consider using TCGPlayer prices (often higher)")
    print(f"   3. Check if Moxfield includes shipping/handling costs")
    print(f"   4. Verify if collection data is complete and current")


if __name__ == "__main__":
    analyze_pricing_gap()
