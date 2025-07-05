#!/usr/bin/env python3
"""
Price update script for MyManaBox collection.

This script updates all card prices using the enhanced pricing service
to better match Moxfield totals and current market values.
"""

import sys
import pandas as pd
from pathlib import Path
from decimal import Decimal
import requests
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from services.enhanced_pricing_service import EnhancedPricingService
except ImportError:
    # Fallback implementation if the service isn't available
    class EnhancedPricingService:
        def __init__(self):
            self.scryfall_base_url = "https://api.scryfall.com"
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'MyManaBox/1.0 Price Updater'
            })
        
        def get_current_scryfall_price(self, card_name: str, set_code: str = None, is_foil: bool = False) -> Decimal:
            """Get current price from Scryfall API."""
            try:
                # Search for the card
                search_url = f"{self.scryfall_base_url}/cards/search"
                query = f'name:"{card_name}"'
                if set_code:
                    query += f' set:{set_code}'
                
                params = {'q': query, 'unique': 'prints'}
                response = self.session.get(search_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        # Use the first matching card
                        card_data = data['data'][0]
                        prices = card_data.get('prices', {})
                        
                        # For foil cards, prefer foil price
                        if is_foil and prices.get('usd_foil'):
                            try:
                                return Decimal(str(prices['usd_foil']))
                            except:
                                pass
                        
                        # Otherwise use regular USD price
                        if prices.get('usd'):
                            try:
                                return Decimal(str(prices['usd']))
                            except:
                                pass
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching price for {card_name}: {e}")
            
            return Decimal('0')
        
        def get_enhanced_price(self, card_name: str, set_code: str = None, 
                             is_foil: bool = False, purchase_price: Decimal = None) -> Decimal:
            """Get enhanced price with TCGPlayer estimation."""
            # Get current Scryfall price
            current_price = self.get_current_scryfall_price(card_name, set_code, is_foil)
            
            if current_price > 0:
                # Apply TCGPlayer estimation (typically 30-50% higher)
                tcg_multiplier = Decimal('1.4')  # 40% higher on average
                estimated_tcg = current_price * tcg_multiplier
                
                # Use the higher of purchase price or estimated TCG price
                # This mimics Moxfield's behavior of using acquisition cost or market premium
                if purchase_price and purchase_price > estimated_tcg:
                    return purchase_price
                else:
                    return estimated_tcg
            
            # Fallback to purchase price
            return purchase_price or Decimal('0')


def update_collection_prices():
    """Update all card prices in the collection."""
    print("🔄 MyManaBox Enhanced Price Updater")
    print("=" * 50)
    
    # Load current collection
    csv_path = Path("data/enriched_collection_complete.csv")
    if not csv_path.exists():
        print("❌ Collection file not found!")
        return
    
    df = pd.read_csv(csv_path)
    pricing_service = EnhancedPricingService()
    
    print(f"📊 Loaded {len(df)} cards")
    print("🎯 Using enhanced pricing with TCGPlayer estimation")
    print("💡 Strategy: Current market + TCG premium + purchase cost priority")
    print()
    
    updated_count = 0
    total_old_value = Decimal('0')
    total_new_value = Decimal('0')
    
    # Create backup first
    backup_path = csv_path.with_suffix(f'.backup_{int(time.time())}')
    df.to_csv(backup_path, index=False)
    print(f"💾 Backup created: {backup_path}")
    print()
    
    for idx, row in df.iterrows():
        if idx % 25 == 0:
            print(f"Progress: {idx}/{len(df)} cards... (Total so far: ${total_new_value:,.2f})")
        
        # Get current values
        purchase_price = None
        if pd.notna(row.get('Purchase Price')):
            purchase_price = Decimal(str(row['Purchase Price']))
        
        old_market_value = None
        if pd.notna(row.get('USD Price')):
            old_market_value = Decimal(str(row['USD Price']))
        
        # Calculate old total value (using current logic)
        count = int(row.get('Count', 1))
        old_price = purchase_price if purchase_price else old_market_value
        if old_price:
            total_old_value += old_price * count
        
        # Check if foil
        is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
        
        # Get enhanced price
        new_price = pricing_service.get_enhanced_price(
            card_name=row['Name'],
            set_code=row.get('Edition', ''),
            is_foil=is_foil,
            purchase_price=purchase_price
        )
        
        if new_price > 0:
            new_total = new_price * count
            total_new_value += new_total
            
            # Update USD Price column with new enhanced price
            df.at[idx, 'USD Price'] = float(new_price)
            updated_count += 1
        elif old_price:
            # Keep old price if we can't get a new one
            total_new_value += old_price * count
    
    print(f"\\n✅ Updated {updated_count} card prices")
    print(f"💰 Old total value: ${total_old_value:,.2f}")
    print(f"💰 New total value: ${total_new_value:,.2f}")
    
    if total_old_value > 0:
        change_percent = ((total_new_value / total_old_value) - 1) * 100
        print(f"📈 Change: {change_percent:+.1f}%")
    
    # Save updated collection
    df.to_csv(csv_path, index=False)
    print(f"💾 Updated collection saved to: {csv_path}")
    
    print(f"\\n🎯 Target Moxfield value: $2,379.52")
    print(f"🎯 Our new value: ${total_new_value:,.2f}")
    if total_new_value > 0:
        target = Decimal('2379.52')
        accuracy = (total_new_value / target) * 100
        print(f"🎯 Accuracy: {accuracy:.1f}% of target")
        
        if accuracy < 80:
            print("💡 Still below target. Consider:")
            print("   • Verifying all cards have current prices")
            print("   • Checking for missing high-value cards")
            print("   • Using higher price sources (TCGPlayer retail vs market)")


if __name__ == "__main__":
    update_collection_prices()
