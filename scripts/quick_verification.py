#!/usr/bin/env python3
"""
Quick verification of current collection status.
"""

import pandas as pd
import sys
from pathlib import Path

def quick_verification():
    """Quick check of collection status."""
    
    print("🔍 QUICK VERIFICATION")
    print("=" * 40)
    
    # Check collection file
    csv_path = Path(__file__).parent.parent / "data" / "enriched_collection_complete.csv"
    
    if not csv_path.exists():
        print("❌ Collection file not found")
        return False
    
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, on_bad_lines='skip')
                print(f"📂 Collection loaded: {len(df):,} cards (encoding: {encoding})")
                break
            except UnicodeDecodeError:
                continue
        else:
            print("❌ Could not read CSV file with any encoding")
            return False
            
        # Basic checks
        print(f"\n📊 BASIC STATS")
        print(f"   Total cards: {len(df):,}")
        
        # USD price coverage
        missing_usd = df['USD Price'].isna().sum()
        usd_coverage = ((len(df) - missing_usd) / len(df)) * 100
        print(f"   USD prices: {len(df) - missing_usd:,}/{len(df):,} ({usd_coverage:.1f}%)")
        print(f"   Missing USD: {missing_usd:,}")
        
        # Foil coverage
        foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])] if 'Foil' in df.columns else df[df['Foil'] == 'foil']
        foil_missing = foil_cards['USD Foil Price'].isna().sum() if 'USD Foil Price' in df.columns else len(foil_cards)
        print(f"   Foil cards: {len(foil_cards):,}")
        print(f"   Missing foil prices: {foil_missing:,}")
        
        # Calculate total value
        total_value = 0
        
        for _, row in df.iterrows():
            try:
                quantity = row.get('Quantity', 1)
                if pd.isna(quantity):
                    quantity = 1
                quantity = int(quantity)
                
                # Purchase price first
                purchase_price = row.get('Purchase Price')
                if pd.notna(purchase_price) and str(purchase_price).strip():
                    try:
                        price = float(str(purchase_price).replace('$', '').replace(',', ''))
                        total_value += price * quantity
                        continue
                    except (ValueError, TypeError):
                        pass
                
                # Market price fallback
                is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
                
                if is_foil and 'USD Foil Price' in df.columns:
                    foil_price = row.get('USD Foil Price')
                    if pd.notna(foil_price) and str(foil_price).strip():
                        try:
                            price = float(str(foil_price).replace('$', '').replace(',', ''))
                            total_value += price * quantity
                            continue
                        except (ValueError, TypeError):
                            pass
                
                # Regular USD price
                usd_price = row.get('USD Price')
                if pd.notna(usd_price) and str(usd_price).strip():
                    try:
                        price = float(str(usd_price).replace('$', '').replace(',', ''))
                        total_value += price * quantity
                    except (ValueError, TypeError):
                        pass
                        
            except Exception:
                continue
        
        print(f"\n💰 VALUE ANALYSIS")
        print(f"   Current collection value: ${total_value:,.2f}")
        print(f"   Target value (Moxfield): $2,379.52")
        print(f"   Gap to target: ${2379.52 - total_value:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_verification()
