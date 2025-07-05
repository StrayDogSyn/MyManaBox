#!/usr/bin/env python3
"""
Collection verification and data completeness checker.

This script analyzes the collection data to identify missing information,
pricing gaps, and opportunities for improvement to match Moxfield totals.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from decimal import Decimal
import sys

def verify_collection_completeness():
    """Verify collection data completeness and identify issues."""
    print("🔍 MyManaBox Collection Verification")
    print("=" * 50)
    
    # Load collection data
    csv_path = Path("data/enriched_collection_complete.csv")
    if not csv_path.exists():
        print("❌ Collection file not found!")
        return
    
    df = pd.read_csv(csv_path)
    
    print(f"📊 Collection Overview:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Total cards: {df['Count'].sum():,}")
    print(f"   Unique cards: {len(df):,}")
    print()
    
    # Check data completeness
    print("📋 Data Completeness Analysis:")
    important_fields = [
        'Name', 'Edition', 'Count', 'Purchase Price', 'USD Price', 'USD Foil Price',
        'Rarity', 'Type Line', 'CMC', 'Colors', 'Set Name', 'Foil'
    ]
    
    for field in important_fields:
        if field in df.columns:
            non_null = df[field].notna().sum()
            completeness = (non_null / len(df)) * 100
            status = "✅" if completeness > 80 else "⚠️" if completeness > 50 else "❌"
            print(f"   {status} {field:<20}: {non_null:>4}/{len(df)} ({completeness:5.1f}%)")
        else:
            print(f"   ❌ {field:<20}: Missing column")
    print()
    
    # Pricing analysis
    print("💰 Pricing Analysis:")
    
    # Purchase prices
    purchase_cards = df[df['Purchase Price'].notna()]
    purchase_total = (purchase_cards['Purchase Price'] * purchase_cards['Count']).sum()
    print(f"   Purchase Price coverage: {len(purchase_cards):,} cards (${purchase_total:,.2f})")
    
    # Market prices (USD)
    market_cards = df[df['USD Price'].notna()]
    if len(market_cards) > 0:
        market_total = (market_cards['USD Price'] * market_cards['Count']).sum()
        print(f"   USD Price coverage: {len(market_cards):,} cards (${market_total:,.2f})")
    
    # Foil prices
    foil_cards = df[df['USD Foil Price'].notna()]
    if len(foil_cards) > 0:
        foil_total = (foil_cards['USD Foil Price'] * foil_cards['Count']).sum()
        print(f"   USD Foil Price coverage: {len(foil_cards):,} cards (${foil_total:,.2f})")
    
    # Cards without any price
    no_price = df[(df['Purchase Price'].isna()) & (df['USD Price'].isna())]
    print(f"   Cards without price: {len(no_price):,} cards ({(len(no_price)/len(df)*100):.1f}%)")
    print()
    
    # High-value card analysis
    print("💎 High-Value Cards Analysis:")
    
    # Cards with purchase price > $5
    high_purchase = purchase_cards[purchase_cards['Purchase Price'] > 5]
    if len(high_purchase) > 0:
        high_purchase_value = (high_purchase['Purchase Price'] * high_purchase['Count']).sum()
        print(f"   High-value purchase cards (>$5): {len(high_purchase)} (${high_purchase_value:,.2f})")
    
    # Cards with market price > $5
    if len(market_cards) > 0:
        high_market = market_cards[market_cards['USD Price'] > 5]
        if len(high_market) > 0:
            high_market_value = (high_market['USD Price'] * high_market['Count']).sum()
            print(f"   High-value market cards (>$5): {len(high_market)} (${high_market_value:,.2f})")
    
    # Top 10 most valuable cards
    print("\\n   Top 10 Most Valuable Cards:")
    value_analysis = []
    for idx, row in df.iterrows():
        count = row['Count']
        purchase = row.get('Purchase Price', 0) if pd.notna(row.get('Purchase Price')) else 0
        market = row.get('USD Price', 0) if pd.notna(row.get('USD Price')) else 0
        
        best_price = max(purchase, market)
        total_value = best_price * count
        
        if total_value > 0:
            value_analysis.append({
                'name': row['Name'],
                'count': count,
                'price': best_price,
                'total': total_value,
                'source': 'Purchase' if purchase > market else 'Market'
            })
    
    value_analysis.sort(key=lambda x: x['total'], reverse=True)
    for i, card in enumerate(value_analysis[:10], 1):
        print(f"   {i:2}. {card['name'][:25]:<25} ${card['total']:>7.2f} ({card['source']})")
    print()
    
    # Foil analysis
    print("✨ Foil Cards Analysis:")
    actual_foils = df[df['Foil'].isin(['foil', 'etched'])]
    print(f"   Actual foil cards: {len(actual_foils):,}")
    
    foil_with_price = actual_foils[actual_foils['USD Foil Price'].notna()]
    print(f"   Foils with foil pricing: {len(foil_with_price):,}")
    
    if len(foil_with_price) > 0:
        foil_premium_total = (foil_with_price['USD Foil Price'] * foil_with_price['Count']).sum()
        print(f"   Foil premium value: ${foil_premium_total:,.2f}")
    print()
    
    # Missing data opportunities
    print("🔧 Improvement Opportunities:")
    
    missing_usd_price = len(df[df['USD Price'].isna()])
    if missing_usd_price > 0:
        print(f"   • Update {missing_usd_price:,} cards missing USD prices")
    
    missing_foil_price = len(actual_foils[actual_foils['USD Foil Price'].isna()])
    if missing_foil_price > 0:
        print(f"   • Update {missing_foil_price:,} foil cards missing foil prices")
    
    missing_set_names = len(df[df['Set Name'].isna()])
    if missing_set_names > 0:
        print(f"   • Enrich {missing_set_names:,} cards missing set names")
    
    missing_rarity = len(df[df['Rarity'].isna()])
    if missing_rarity > 0:
        print(f"   • Add rarity for {missing_rarity:,} cards")
    
    print()
    
    # Calculate theoretical maximum value
    print("🎯 Value Analysis vs Moxfield Target:")
    current_total = Decimal('0')
    
    for idx, row in df.iterrows():
        count = row['Count']
        purchase = row.get('Purchase Price', 0) if pd.notna(row.get('Purchase Price')) else 0
        market = row.get('USD Price', 0) if pd.notna(row.get('USD Price')) else 0
        
        # Use current pricing logic (purchase price priority)
        best_price = purchase if purchase > 0 else market
        current_total += Decimal(str(best_price)) * count
    
    target_total = Decimal('2379.52')
    accuracy = (current_total / target_total) * 100 if target_total > 0 else 0
    
    print(f"   Current total value: ${current_total:,.2f}")
    print(f"   Moxfield target: ${target_total:,.2f}")
    print(f"   Accuracy: {accuracy:.1f}%")
    print(f"   Gap: ${target_total - current_total:,.2f}")
    
    if accuracy < 90:
        print("\\n💡 Recommendations to reach target:")
        print("   1. Run price update script to get current market prices")
        print("   2. Consider TCGPlayer prices (often 20-40% higher than Scryfall)")
        print("   3. Verify all high-value cards have current pricing")
        print("   4. Check if any cards are missing from the collection")
        print("   5. Consider shipping/handling costs Moxfield might include")


def analyze_price_gaps():
    """Analyze specific price gaps and suggest corrections."""
    print("\\n" + "=" * 50)
    print("🔍 Price Gap Analysis")
    print("=" * 50)
    
    csv_path = Path("data/enriched_collection_complete.csv")
    df = pd.read_csv(csv_path)
    
    # Find cards where purchase price significantly differs from market price
    price_gaps = []
    
    for idx, row in df.iterrows():
        purchase = row.get('Purchase Price', 0) if pd.notna(row.get('Purchase Price')) else 0
        market = row.get('USD Price', 0) if pd.notna(row.get('USD Price')) else 0
        
        if purchase > 0 and market > 0:
            gap = abs(purchase - market)
            gap_percent = (gap / max(purchase, market)) * 100
            
            if gap_percent > 50:  # More than 50% difference
                price_gaps.append({
                    'name': row['Name'],
                    'purchase': purchase,
                    'market': market,
                    'gap': gap,
                    'gap_percent': gap_percent,
                    'count': row['Count']
                })
    
    price_gaps.sort(key=lambda x: x['gap'] * x['count'], reverse=True)
    
    if price_gaps:
        print("Cards with significant price differences:")
        print("(This might indicate outdated prices or different sources)")
        print()
        
        for gap in price_gaps[:15]:
            print(f"   {gap['name'][:25]:<25} Purchase: ${gap['purchase']:>6.2f} | Market: ${gap['market']:>6.2f} | Gap: {gap['gap_percent']:>5.1f}%")


if __name__ == "__main__":
    verify_collection_completeness()
    analyze_price_gaps()
