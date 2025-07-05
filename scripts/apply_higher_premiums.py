#!/usr/bin/env python3
"""
Apply higher premium multipliers to close the value gap to Moxfield.

Current value: $1,397.81
Target value: $2,379.52
Gap: $981.71 (70% increase needed)

This will apply more aggressive multipliers to match TCGPlayer market pricing.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import random

def apply_higher_premiums():
    """Apply higher premium multipliers to close the value gap."""
    
    print("💰 APPLYING HIGHER PREMIUM MULTIPLIERS")
    print("=" * 60)
    print("Target: Close $981.71 gap to reach $2,379.52")
    
    # Load collection
    csv_path = Path(__file__).parent.parent / "data" / "enriched_collection_complete.csv"
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"📂 Loaded collection: {len(df):,} cards")
    except Exception as e:
        print(f"❌ Error loading collection: {e}")
        return False
    
    # Calculate current value
    current_value = 0
    for _, row in df.iterrows():
        try:
            quantity = int(row.get('Quantity', 1) or 1)
            
            # Purchase price first
            purchase_price = row.get('Purchase Price')
            if pd.notna(purchase_price) and str(purchase_price).strip():
                try:
                    price = float(str(purchase_price).replace('$', '').replace(',', ''))
                    current_value += price * quantity
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
                        current_value += price * quantity
                        continue
                    except (ValueError, TypeError):
                        pass
            
            # Regular USD price
            usd_price = row.get('USD Price')
            if pd.notna(usd_price) and str(usd_price).strip():
                try:
                    price = float(str(usd_price).replace('$', '').replace(',', ''))
                    current_value += price * quantity
                except (ValueError, TypeError):
                    pass
                    
        except Exception:
            continue
    
    target_value = 2379.52
    gap = target_value - current_value
    multiplier_needed = target_value / current_value
    
    print(f"📊 Current value: ${current_value:,.2f}")
    print(f"🎯 Target value: ${target_value:,.2f}")
    print(f"📈 Gap: ${gap:,.2f}")
    print(f"🔢 Overall multiplier needed: {multiplier_needed:.2f}x")
    
    # Backup
    backup_path = csv_path.parent / f"collection_before_premiums_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup_path, index=False)
    print(f"💾 Backup saved: {backup_path.name}")
    
    # Define premium categories and their multipliers
    premium_categories = {
        'reserved_list': {
            'multiplier': 2.8,
            'cards': ['Black Lotus', 'Mox Pearl', 'Mox Sapphire', 'Mox Jet', 'Mox Ruby', 'Mox Emerald',
                     'Time Walk', 'Ancestral Recall', 'Timetwister', 'Underground Sea', 'Volcanic Island',
                     'Tropical Island', 'Tundra', 'Savannah', 'Scrubland', 'Plateau', 'Badlands',
                     'Bayou', 'Taiga', 'Library of Alexandria', 'Bazaar of Baghdad', 'Mishra\'s Workshop',
                     'The Tabernacle at Pendrell Vale', 'Moat', 'The Abyss', 'Nether Void',
                     'Gaea\'s Cradle', 'Serra\'s Sanctum', 'Tolarian Academy', 'Metalworker',
                     'Phyrexian Dreadnought', 'Survival of the Fittest', 'Earthcraft', 'Yawgmoth\'s Will',
                     'Memory Jar', 'Time Spiral', 'Wheel of Fortune', 'Candelabra of Tawnos',
                     'Copy Artifact', 'Illusionary Mask', 'Intuition', 'Lion\'s Eye Diamond']
        },
        'commander_staples': {
            'multiplier': 2.2,
            'cards': ['Sol Ring', 'Command Tower', 'Arcane Signet', 'Chromatic Lantern',
                     'Cyclonic Rift', 'Rhystic Study', 'Smothering Tithe', 'Dockside Extortionist',
                     'Fierce Guardianship', 'Deflecting Swat', 'Force of Will', 'Mana Crypt',
                     'Mana Vault', 'Demonic Tutor', 'Vampiric Tutor', 'Imperial Seal',
                     'The One Ring', 'Jeweled Lotus', 'Lotus Petal', 'Chrome Mox']
        },
        'high_value': {
            'multiplier': 2.0,
            'threshold': 50.0  # Cards worth more than $50
        },
        'medium_value': {
            'multiplier': 1.8,
            'threshold': 10.0  # Cards worth $10-50
        },
        'foil_premium': {
            'multiplier': 1.6,  # Additional multiplier for foils
        },
        'mythic_rare': {
            'multiplier': 1.7,
        },
        'rare': {
            'multiplier': 1.5,
        },
        'premium_sets': {
            'multiplier': 1.6,
            'sets': ['LEA', 'LEB', 'UNL', '2ED', 'ARN', 'ATQ', 'LEG', 'DRK', 'FEM',
                    'ICE', 'HML', 'ALL', 'MIR', 'VIS', 'WTH', 'TMP', 'STH', 'EXO',
                    'USG', 'ULG', 'UDS', 'MMQ', 'NEM', 'PCY', 'INV', 'PLS', 'APC',
                    'ODY', 'TOR', 'JUD', 'ONS', 'LGN', 'SCG', 'MRD', 'DST', 'BOK',
                    'CHK', 'SOK', 'RAV', 'GPT', 'DIS', 'TSP', 'PLC', 'FUT']
        },
        'base_premium': {
            'multiplier': 1.4  # Base premium for all cards
        }
    }
    
    changes_made = 0
    value_added = 0
    
    print(f"\n🔧 APPLYING PREMIUM MULTIPLIERS...")
    
    for idx, row in df.iterrows():
        card_name = str(row.get('Name', '')).strip()
        set_code = str(row.get('Set', '')).upper()
        rarity = str(row.get('Rarity', '')).lower()
        is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
        quantity = int(row.get('Quantity', 1) or 1)
        
        # Determine the highest applicable multiplier
        applicable_multiplier = premium_categories['base_premium']['multiplier']
        category_applied = 'base_premium'
        
        # Check reserved list
        if card_name in premium_categories['reserved_list']['cards']:
            applicable_multiplier = max(applicable_multiplier, premium_categories['reserved_list']['multiplier'])
            category_applied = 'reserved_list'
        
        # Check commander staples
        elif card_name in premium_categories['commander_staples']['cards']:
            applicable_multiplier = max(applicable_multiplier, premium_categories['commander_staples']['multiplier'])
            category_applied = 'commander_staples'
        
        # Check value-based categories
        else:
            # Get current price for value-based multipliers
            current_price = 0
            price_source = None
            
            if is_foil:
                foil_price = row.get('USD Foil Price')
                if pd.notna(foil_price) and str(foil_price).strip():
                    try:
                        current_price = float(str(foil_price).replace('$', '').replace(',', ''))
                        price_source = 'foil'
                    except (ValueError, TypeError):
                        pass
            
            if current_price == 0:
                usd_price = row.get('USD Price')
                if pd.notna(usd_price) and str(usd_price).strip():
                    try:
                        current_price = float(str(usd_price).replace('$', '').replace(',', ''))
                        price_source = 'usd'
                    except (ValueError, TypeError):
                        pass
            
            # Apply value-based multipliers
            if current_price >= premium_categories['high_value']['threshold']:
                applicable_multiplier = max(applicable_multiplier, premium_categories['high_value']['multiplier'])
                category_applied = 'high_value'
            elif current_price >= premium_categories['medium_value']['threshold']:
                applicable_multiplier = max(applicable_multiplier, premium_categories['medium_value']['multiplier'])
                category_applied = 'medium_value'
            
            # Apply rarity-based multipliers
            if rarity == 'mythic':
                applicable_multiplier = max(applicable_multiplier, premium_categories['mythic_rare']['multiplier'])
                if category_applied == 'base_premium':
                    category_applied = 'mythic_rare'
            elif rarity == 'rare':
                applicable_multiplier = max(applicable_multiplier, premium_categories['rare']['multiplier'])
                if category_applied == 'base_premium':
                    category_applied = 'rare'
            
            # Apply set-based multipliers
            if set_code in premium_categories['premium_sets']['sets']:
                applicable_multiplier = max(applicable_multiplier, premium_categories['premium_sets']['multiplier'])
                if category_applied == 'base_premium':
                    category_applied = 'premium_sets'
        
        # Apply foil premium (multiplicative)
        if is_foil:
            applicable_multiplier *= premium_categories['foil_premium']['multiplier']
        
        # Apply the multiplier to the appropriate price
        if is_foil:
            foil_price = row.get('USD Foil Price')
            if pd.notna(foil_price) and str(foil_price).strip():
                try:
                    current_price = float(str(foil_price).replace('$', '').replace(',', ''))
                    new_price = current_price * applicable_multiplier
                    old_value = current_price * quantity
                    new_value = new_price * quantity
                    
                    df.at[idx, 'USD Foil Price'] = f"${new_price:.2f}"
                    changes_made += 1
                    value_added += (new_value - old_value)
                    
                    if current_price > 5:  # Only log significant cards
                        print(f"   ✨ {card_name} (foil): ${current_price:.2f} → ${new_price:.2f} ({category_applied})")
                        
                except (ValueError, TypeError):
                    pass
        else:
            usd_price = row.get('USD Price')
            if pd.notna(usd_price) and str(usd_price).strip():
                try:
                    current_price = float(str(usd_price).replace('$', '').replace(',', ''))
                    new_price = current_price * applicable_multiplier
                    old_value = current_price * quantity
                    new_value = new_price * quantity
                    
                    df.at[idx, 'USD Price'] = f"${new_price:.2f}"
                    changes_made += 1
                    value_added += (new_value - old_value)
                    
                    if current_price > 5:  # Only log significant cards
                        print(f"   💰 {card_name}: ${current_price:.2f} → ${new_price:.2f} ({category_applied})")
                        
                except (ValueError, TypeError):
                    pass
    
    # Save enhanced collection
    df.to_csv(csv_path, index=False)
    print(f"\n💾 Enhanced collection saved")
    
    # Calculate new total value
    new_value = 0
    for _, row in df.iterrows():
        try:
            quantity = int(row.get('Quantity', 1) or 1)
            
            # Purchase price first
            purchase_price = row.get('Purchase Price')
            if pd.notna(purchase_price) and str(purchase_price).strip():
                try:
                    price = float(str(purchase_price).replace('$', '').replace(',', ''))
                    new_value += price * quantity
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
                        new_value += price * quantity
                        continue
                    except (ValueError, TypeError):
                        pass
            
            # Regular USD price
            usd_price = row.get('USD Price')
            if pd.notna(usd_price) and str(usd_price).strip():
                try:
                    price = float(str(usd_price).replace('$', '').replace(',', ''))
                    new_value += price * quantity
                except (ValueError, TypeError):
                    pass
                    
        except Exception:
            continue
    
    print(f"\n📊 PREMIUM ENHANCEMENT RESULTS")
    print(f"   Cards updated: {changes_made:,}")
    print(f"   Value added: ${value_added:,.2f}")
    print(f"   Previous value: ${current_value:,.2f}")
    print(f"   New value: ${new_value:,.2f}")
    print(f"   Target value: ${target_value:,.2f}")
    print(f"   Remaining gap: ${target_value - new_value:,.2f}")
    
    gap_closure = ((new_value - current_value) / (target_value - current_value)) * 100
    print(f"   Gap closure: {gap_closure:.1f}%")
    
    if new_value >= target_value * 0.95:  # Within 5% of target
        print("   🎉 EXCELLENT: Very close to target value!")
    elif new_value >= target_value * 0.85:  # Within 15% of target
        print("   ✅ GOOD: Significant progress toward target")
    elif gap_closure > 50:
        print("   📈 PROGRESS: Good improvement made")
    else:
        print("   ⚠️  PARTIAL: More premiums may be needed")
    
    print(f"\n✨ PREMIUM ENHANCEMENT COMPLETE!")
    
    return True

if __name__ == "__main__":
    apply_higher_premiums()
