#!/usr/bin/env python3
"""
Quick analysis of price update results.
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def analyze_collection_value():
    """Analyze the current collection value after price updates."""
    
    csv_path = Path(__file__).parent.parent / "data" / "enriched_collection_complete.csv"
    
    if not csv_path.exists():
        print(f"Collection file not found: {csv_path}")
        return
    
    # Load the collection
    df = pd.read_csv(csv_path)
    print(f"📊 Collection Analysis")
    print(f"{'='*50}")
    print(f"Total cards: {len(df):,}")
    
    # Check pricing completeness
    has_purchase_price = df['Purchase Price'].notna().sum()
    has_usd_price = df['USD Price'].notna().sum() 
    has_foil_price = df['USD Foil Price'].notna().sum()
    
    print(f"\n💰 Price Coverage:")
    print(f"Cards with Purchase Price: {has_purchase_price:,}")
    print(f"Cards with USD Price: {has_usd_price:,}")
    print(f"Cards with USD Foil Price: {has_foil_price:,}")
    
    # Check foil cards specifically
    foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])].copy()
    foil_with_foil_price = foil_cards['USD Foil Price'].notna().sum()
    
    print(f"\n✨ Foil Card Analysis:")
    print(f"Total foil cards: {len(foil_cards):,}")
    print(f"Foil cards with foil pricing: {foil_with_foil_price:,}")
    
    # Calculate total value using the same logic as our models
    total_value = 0.0
    purchase_price_total = 0.0
    market_price_total = 0.0
    
    for _, row in df.iterrows():
        try:
            quantity = int(row.get('Quantity', 1))
            
            # Purchase price first (primary valuation)
            purchase_price = row.get('Purchase Price')
            if pd.notna(purchase_price) and str(purchase_price).strip():
                try:
                    price = float(str(purchase_price).replace('$', '').replace(',', ''))
                    total_value += price * quantity
                    purchase_price_total += price * quantity
                    continue
                except (ValueError, TypeError):
                    pass
            
            # Market price fallback
            is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
            
            if is_foil:
                foil_price = row.get('USD Foil Price')
                if pd.notna(foil_price) and str(foil_price).strip():
                    try:
                        price = float(str(foil_price).replace('$', '').replace(',', ''))
                        total_value += price * quantity
                        market_price_total += price * quantity
                        continue
                    except (ValueError, TypeError):
                        pass
            
            # Regular USD price
            usd_price = row.get('USD Price')
            if pd.notna(usd_price) and str(usd_price).strip():
                try:
                    price = float(str(usd_price).replace('$', '').replace(',', ''))
                    total_value += price * quantity
                    market_price_total += price * quantity
                except (ValueError, TypeError):
                    pass
                    
        except Exception:
            continue
    
    print(f"\n💎 Collection Value:")
    print(f"Purchase Price Total: ${purchase_price_total:,.2f}")
    print(f"Market Price Total: ${market_price_total:,.2f}")
    print(f"Combined Total: ${total_value:,.2f}")
    
    print(f"\n🎯 Target Comparison:")
    print(f"Current Value: ${total_value:,.2f}")
    print(f"Moxfield Target: $2,379.52")
    gap = 2379.52 - total_value
    print(f"Remaining Gap: ${gap:,.2f}")
    
    if gap > 0:
        print(f"Gap Percentage: {(gap / 2379.52 * 100):.1f}%")
        
        print(f"\n📈 Improvement Recommendations:")
        if gap > 200:
            print("• Consider higher premium multipliers for pricing")
            print("• Verify purchase prices for high-value cards")
            print("• Integrate TCGPlayer API for more accurate pricing")
        elif gap > 50:
            print("• Fine-tune premium multipliers")
            print("• Review pricing for expensive cards")
        else:
            print("• Collection value is very close to target!")
    else:
        print("🎉 Collection value exceeds Moxfield target!")
    
    # Check for remaining gaps
    no_pricing = df[(df['Purchase Price'].isna()) & (df['USD Price'].isna())].shape[0]
    foil_missing = foil_cards[foil_cards['USD Foil Price'].isna()].shape[0]
    
    print(f"\n⚠️  Remaining Issues:")
    print(f"Cards with no pricing: {no_pricing:,}")
    print(f"Foil cards missing foil price: {foil_missing:,}")

if __name__ == "__main__":
    analyze_collection_value()
