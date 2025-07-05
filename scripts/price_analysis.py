#!/usr/bin/env python3
"""
MyManaBox Price Analysis and Update Tool

This script analyzes the current pricing in your collection and provides
recommendations to achieve Moxfield-like totals of ~$2,379.52.
"""

import pandas as pd
import requests
import time
import json
from decimal import Decimal
from pathlib import Path


def analyze_current_pricing(csv_path: str):
    """Analyze current pricing structure."""
    print("🔍 MyManaBox Price Analysis")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv(csv_path)
    print(f"📊 Loaded {len(df):,} cards from collection")
    
    # Current pricing analysis
    total_cards = df['Count'].sum()
    purchase_price_cards = df['Purchase Price'].notna().sum()
    usd_price_cards = df['USD Price'].notna().sum()
    usd_foil_price_cards = df['USD Foil Price'].notna().sum()
    
    print(f"\n📈 Current Price Coverage:")
    print(f"   Total cards: {total_cards:,}")
    print(f"   Cards with Purchase Price: {purchase_price_cards:,}")
    print(f"   Cards with USD Price: {usd_price_cards:,}")
    print(f"   Cards with USD Foil Price: {usd_foil_price_cards:,}")
    print(f"   Cards with no pricing: {len(df) - max(purchase_price_cards, usd_price_cards):,}")
    
    # Calculate current total using our logic (purchase price priority)
    current_total = Decimal('0')
    
    for idx, row in df.iterrows():
        count = int(row['Count'])
        
        # Use purchase price first, then market price
        price = None
        
        # Try purchase price first
        if pd.notna(row['Purchase Price']):
            price = Decimal(str(row['Purchase Price']))
        else:
            # Check if foil
            foil_status = str(row.get('Foil', '')).lower()
            is_foil = foil_status in ['foil', 'etched']
            
            if is_foil and pd.notna(row.get('USD Foil Price')):
                price = Decimal(str(row['USD Foil Price']))
            elif pd.notna(row.get('USD Price')):
                price = Decimal(str(row['USD Price']))
        
        if price:
            current_total += price * count
    
    print(f"\n💰 Current Value Calculation:")
    print(f"   Our total: ${current_total:,.2f}")
    print(f"   Moxfield target: $2,379.52")
    print(f"   Gap: ${2379.52 - float(current_total):,.2f}")
    print(f"   Multiplier needed: {2379.52 / float(current_total):.2f}x")
    
    return df, current_total


def identify_improvement_opportunities(df: pd.DataFrame):
    """Identify cards that could benefit from price updates."""
    print(f"\n🎯 Improvement Opportunities:")
    
    # Cards with no pricing at all
    no_price = df[(df['Purchase Price'].isna()) & (df['USD Price'].isna())]
    print(f"   Cards with no pricing: {len(no_price):,}")
    
    # Foil cards without foil pricing
    foil_cards = df[df['Foil'].isin(['foil', 'etched'])]
    foil_missing_price = foil_cards[foil_cards['USD Foil Price'].isna()]
    print(f"   Foil cards missing foil price: {len(foil_missing_price):,}")
    
    # High count cards with low/no pricing
    high_count = df[df['Count'] > 1]
    high_count_no_price = high_count[(high_count['Purchase Price'].isna()) & (high_count['USD Price'].isna())]
    print(f"   High-count cards without pricing: {len(high_count_no_price):,}")
    
    # Cards with only purchase price (could benefit from market price)
    only_purchase = df[(df['Purchase Price'].notna()) & (df['USD Price'].isna())]
    print(f"   Cards with only purchase price: {len(only_purchase):,}")
    
    return {
        'no_price': no_price,
        'foil_missing_price': foil_missing_price,
        'high_count_no_price': high_count_no_price,
        'only_purchase': only_purchase
    }


def estimate_potential_value(df: pd.DataFrame, opportunities: dict):
    """Estimate potential value if pricing gaps were filled."""
    print(f"\n📊 Potential Value Estimation:")
    
    # Calculate average prices from cards that have pricing
    cards_with_usd = df[df['USD Price'].notna()]
    cards_with_purchase = df[df['Purchase Price'].notna()]
    
    if len(cards_with_usd) > 0:
        avg_usd_price = cards_with_usd['USD Price'].mean()
        print(f"   Average USD price: ${avg_usd_price:.2f}")
    else:
        avg_usd_price = 0.50  # Conservative estimate
    
    if len(cards_with_purchase) > 0:
        avg_purchase_price = cards_with_purchase['Purchase Price'].mean()
        print(f"   Average purchase price: ${avg_purchase_price:.2f}")
    else:
        avg_purchase_price = 0.60  # Conservative estimate
    
    # Estimate value if gaps were filled
    no_price_potential = len(opportunities['no_price']) * avg_usd_price
    foil_potential = len(opportunities['foil_missing_price']) * avg_usd_price * 1.5  # Foil premium
    
    print(f"   Potential from cards with no price: ${no_price_potential:,.2f}")
    print(f"   Potential from foil pricing: ${foil_potential:,.2f}")
    print(f"   Total potential additional: ${no_price_potential + foil_potential:,.2f}")
    
    return no_price_potential + foil_potential


def suggest_strategies(current_total: Decimal, potential_additional: float):
    """Suggest strategies to reach Moxfield-like totals."""
    print(f"\n🎯 Recommended Strategies:")
    
    target = 2379.52
    current = float(current_total)
    gap = target - current
    
    print(f"   Current value: ${current:,.2f}")
    print(f"   Target value: ${target:,.2f}")
    print(f"   Gap to close: ${gap:,.2f}")
    print(f"   Potential from missing prices: ${potential_additional:,.2f}")
    
    if potential_additional >= gap:
        print(f"   ✅ Filling pricing gaps could reach target!")
    else:
        remaining_gap = gap - potential_additional
        print(f"   ⚠️  After filling gaps, still need ${remaining_gap:,.2f}")
        print(f"   This suggests prices need to be ~{remaining_gap/current:.1%} higher")
    
    print(f"\n📋 Action Items:")
    print(f"   1. Update {(potential_additional * 0.6 / 0.50):.0f} cards with missing USD prices")
    print(f"   2. Add foil pricing for foil cards")
    print(f"   3. Consider using higher price sources (TCGPlayer vs Scryfall)")
    print(f"   4. Verify purchase prices are current/accurate")
    print(f"   5. Check if Moxfield includes premium/shipping costs")


def main():
    """Main analysis function."""
    csv_path = Path("data/enriched_collection_complete.csv")
    
    if not csv_path.exists():
        print(f"❌ Collection file not found: {csv_path}")
        print("   Please ensure you're running from the MyManaBox directory")
        return
    
    try:
        # Analyze current state
        df, current_total = analyze_current_pricing(csv_path)
        
        # Identify opportunities
        opportunities = identify_improvement_opportunities(df)
        
        # Estimate potential
        potential_additional = estimate_potential_value(df, opportunities)
        
        # Suggest strategies
        suggest_strategies(current_total, potential_additional)
        
        print(f"\n✨ Analysis Complete!")
        print(f"   To improve pricing, consider running price update tools")
        print(f"   or manually reviewing high-value cards in your collection.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")


if __name__ == "__main__":
    main()
