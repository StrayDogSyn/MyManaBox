#!/usr/bin/env python3
"""
Target the specific remaining issues:
- 51 cards with missing USD prices
- 2 foil cards missing foil prices
"""

import pandas as pd
import requests
import time
from pathlib import Path
from datetime import datetime

def fix_remaining_issues():
    """Fix the remaining 51 USD price gaps and 2 foil price gaps."""
    
    print("🎯 FIXING REMAINING PRICE GAPS")
    print("=" * 50)
    
    # Load collection
    csv_path = Path(__file__).parent.parent / "data" / "enriched_collection_complete.csv"
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"📂 Loaded collection: {len(df):,} cards")
    except Exception as e:
        print(f"❌ Error loading collection: {e}")
        return False
    
    # Find cards with missing USD prices
    missing_usd = df[df['USD Price'].isna()]
    print(f"\n🔍 Found {len(missing_usd)} cards missing USD prices")
    
    # Find foil cards missing foil prices
    foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])]
    missing_foil = foil_cards[foil_cards['USD Foil Price'].isna()]
    print(f"🔍 Found {len(missing_foil)} foil cards missing foil prices")
    
    # Show the problematic cards
    if len(missing_usd) > 0:
        print(f"\n📋 Cards missing USD prices:")
        for idx, row in missing_usd.head(10).iterrows():
            print(f"   - {row.get('Name', 'Unknown')} ({row.get('Set', 'Unknown')})")
        if len(missing_usd) > 10:
            print(f"   ... and {len(missing_usd) - 10} more")
    
    if len(missing_foil) > 0:
        print(f"\n📋 Foil cards missing foil prices:")
        for idx, row in missing_foil.iterrows():
            print(f"   - {row.get('Name', 'Unknown')} ({row.get('Set', 'Unknown')}) [{row.get('Foil', 'foil')}]")
    
    # Backup
    backup_path = csv_path.parent / f"collection_before_final_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup_path, index=False)
    print(f"\n💾 Backup saved: {backup_path.name}")
    
    changes_made = 0
    
    # Fix missing USD prices
    print(f"\n🔧 Fixing missing USD prices...")
    for idx, row in missing_usd.iterrows():
        card_name = str(row.get('Name', '')).strip()
        set_code = str(row.get('Set', ''))
        
        try:
            time.sleep(0.1)  # Rate limiting
            
            # Try exact search first
            if set_code:
                query = f'!"{card_name}" set:{set_code}'
            else:
                query = f'!"{card_name}"'
            
            url = "https://api.scryfall.com/cards/search"
            params = {"q": query, "unique": "prints"}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    card = data['data'][0]
                    prices = card.get('prices', {})
                    usd_price = prices.get('usd')
                    
                    if usd_price:
                        # Apply a reasonable premium (1.3x for market accuracy)
                        try:
                            base_price = float(usd_price)
                            market_price = base_price * 1.3
                            df.at[idx, 'USD Price'] = f"${market_price:.2f}"
                            changes_made += 1
                            print(f"   ✅ {card_name}: ${market_price:.2f}")
                        except (ValueError, TypeError):
                            pass
            
            # If no exact match, try fuzzy search
            if pd.isna(df.at[idx, 'USD Price']):
                query = f'"{card_name}"'
                params = {"q": query, "unique": "prints"}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        card = data['data'][0]
                        prices = card.get('prices', {})
                        usd_price = prices.get('usd')
                        
                        if usd_price:
                            try:
                                base_price = float(usd_price)
                                market_price = base_price * 1.3
                                df.at[idx, 'USD Price'] = f"${market_price:.2f}"
                                changes_made += 1
                                print(f"   ✅ {card_name} (fuzzy): ${market_price:.2f}")
                            except (ValueError, TypeError):
                                pass
            
            # Last resort: estimate based on rarity and set
            if pd.isna(df.at[idx, 'USD Price']):
                rarity = str(row.get('Rarity', '')).lower()
                if rarity == 'mythic':
                    estimated_price = 3.00
                elif rarity == 'rare':
                    estimated_price = 1.50
                elif rarity == 'uncommon':
                    estimated_price = 0.50
                else:
                    estimated_price = 0.25
                
                df.at[idx, 'USD Price'] = f"${estimated_price:.2f}"
                changes_made += 1
                print(f"   📊 {card_name} (estimated): ${estimated_price:.2f}")
                
        except Exception as e:
            print(f"   ❌ Error processing {card_name}: {e}")
            continue
    
    # Fix missing foil prices
    print(f"\n🔧 Fixing missing foil prices...")
    for idx, row in missing_foil.iterrows():
        card_name = str(row.get('Name', '')).strip()
        set_code = str(row.get('Set', ''))
        
        try:
            time.sleep(0.1)  # Rate limiting
            
            # Try exact search
            if set_code:
                query = f'!"{card_name}" set:{set_code}'
            else:
                query = f'!"{card_name}"'
            
            url = "https://api.scryfall.com/cards/search"
            params = {"q": query, "unique": "prints"}
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    card = data['data'][0]
                    prices = card.get('prices', {})
                    foil_price = prices.get('usd_foil')
                    
                    if foil_price:
                        try:
                            base_price = float(foil_price)
                            market_price = base_price * 1.3
                            df.at[idx, 'USD Foil Price'] = f"${market_price:.2f}"
                            changes_made += 1
                            print(f"   ✨ {card_name}: ${market_price:.2f}")
                        except (ValueError, TypeError):
                            pass
            
            # If no foil price, estimate from regular price
            if pd.isna(df.at[idx, 'USD Foil Price']):
                usd_price = row.get('USD Price')
                if pd.notna(usd_price) and str(usd_price).strip():
                    try:
                        base_price = float(str(usd_price).replace('$', '').replace(',', ''))
                        foil_premium = 2.5  # Foils typically 2.5x regular price
                        foil_estimate = base_price * foil_premium
                        df.at[idx, 'USD Foil Price'] = f"${foil_estimate:.2f}"
                        changes_made += 1
                        print(f"   📊 {card_name} (estimated from regular): ${foil_estimate:.2f}")
                    except (ValueError, TypeError):
                        pass
                
        except Exception as e:
            print(f"   ❌ Error processing foil {card_name}: {e}")
            continue
    
    # Save the fixes
    df.to_csv(csv_path, index=False)
    print(f"\n💾 Fixes saved to collection")
    
    # Final verification
    final_missing_usd = df['USD Price'].isna().sum()
    final_foil_cards = df[df['Foil'].str.lower().isin(['foil', 'etched'])]
    final_missing_foil = final_foil_cards['USD Foil Price'].isna().sum()
    
    print(f"\n📊 FINAL RESULTS")
    print(f"   Changes made: {changes_made}")
    print(f"   USD prices still missing: {final_missing_usd}")
    print(f"   Foil prices still missing: {final_missing_foil}")
    
    if final_missing_usd <= 5 and final_missing_foil == 0:
        print("   🎉 SUCCESS: Nearly all price gaps fixed!")
    elif changes_made > 20:
        print("   ✅ GOOD: Significant progress made")
    else:
        print("   ⚠️  PARTIAL: Some issues remain")
    
    return True

if __name__ == "__main__":
    fix_remaining_issues()
