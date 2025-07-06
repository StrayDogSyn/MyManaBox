#!/usr/bin/env python3
"""
Average Pricing Implementation for MyManaBox

This module implements comprehensive average pricing functionality including:
1. Card-level average pricing (multiple copies, different conditions)
2. Set-level average pricing
3. Rarity-based average pricing  
4. Format-based average pricing
5. Market trend analysis
6. Collection-wide pricing statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

class AveragePricingService:
    """Service for calculating various types of average pricing."""
    
    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or "data/enriched_collection_complete.csv"
        self.df: Optional[pd.DataFrame] = None
        self.load_collection()
    
    def load_collection(self):
        """Load the collection data."""
        try:
            csv_path = Path(self.csv_path)
            if not csv_path.exists():
                raise FileNotFoundError(f"Collection file not found: {csv_path}")
            
            self.df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"📂 Loaded collection: {len(self.df):,} cards")
        except Exception as e:
            print(f"❌ Error loading collection: {e}")
            raise
    
    def extract_price(self, price_str) -> float:
        """Extract numeric price from price string."""
        if pd.isna(price_str) or not str(price_str).strip():
            return 0.0
        try:
            return float(str(price_str).replace('$', '').replace(',', ''))
        except (ValueError, TypeError):
            return 0.0
    
    def get_card_price(self, row) -> Tuple[float, str]:
        """Get the effective price for a card (purchase price priority)."""
        # Purchase price first
        purchase_price = self.extract_price(row.get('Purchase Price'))
        if purchase_price > 0:
            return purchase_price, 'purchase'
        
        # Foil price for foil cards
        is_foil = str(row.get('Foil', '')).lower() in ['foil', 'etched']
        if is_foil:
            foil_price = self.extract_price(row.get('USD Foil Price'))
            if foil_price > 0:
                return foil_price, 'foil'
        
        # Regular USD price
        usd_price = self.extract_price(row.get('USD Price'))
        if usd_price > 0:
            return usd_price, 'usd'
        
        return 0.0, 'none'
    
    def calculate_card_level_averages(self) -> Dict:
        """Calculate average prices for cards with multiple copies."""
        if self.df is None:
            return {}
            
        print("\n📊 CALCULATING CARD-LEVEL AVERAGES")
        
        card_stats = {}
        
        # Group by card name
        for card_name, group in self.df.groupby('Name'):
            if len(group) <= 1:
                continue  # Skip single copies
            
            prices = []
            conditions = []
            foil_status = []
            quantities = []
            
            for _, row in group.iterrows():
                price, source = self.get_card_price(row)
                if price > 0:
                    quantity = int(row.get('Quantity', 1) or 1)
                    prices.extend([price] * quantity)  # Weight by quantity
                    conditions.append(row.get('Condition', 'NM'))
                    foil_status.append(str(row.get('Foil', '')).lower() in ['foil', 'etched'])
                    quantities.append(quantity)
            
            if len(prices) > 1:
                card_stats[card_name] = {
                    'copies': len(group),
                    'total_quantity': sum(quantities),
                    'average_price': np.mean(prices),
                    'median_price': np.median(prices),
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'price_std': np.std(prices),
                    'conditions': list(set(conditions)),
                    'has_foils': any(foil_status),
                    'foil_count': sum(foil_status)
                }
        
        print(f"   Found {len(card_stats)} cards with multiple copies")
        return card_stats
    
    def calculate_set_averages(self) -> Dict:
        """Calculate average prices by set."""
        if self.df is None:
            return {}
            
        print("\n📦 CALCULATING SET-LEVEL AVERAGES")
        
        set_stats = {}
        
        for set_code, group in self.df.groupby('Edition'):
            prices = []
            total_value = 0
            total_quantity = 0
            
            for _, row in group.iterrows():
                price, source = self.get_card_price(row)
                quantity = int(row.get('Quantity', 1) or 1)
                
                if price > 0:
                    prices.append(price)
                    total_value += price * quantity
                    total_quantity += quantity
            
            if prices:
                set_stats[set_code] = {
                    'card_count': len(group),
                    'total_quantity': total_quantity,
                    'average_card_price': np.mean(prices),
                    'median_card_price': np.median(prices),
                    'total_set_value': total_value,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'price_std': np.std(prices) if len(prices) > 1 else 0,
                    'set_name': group.iloc[0].get('Edition', set_code)
                }
        
        print(f"   Analyzed {len(set_stats)} sets")
        return set_stats
    
    def calculate_rarity_averages(self) -> Dict:
        """Calculate average prices by rarity."""
        if self.df is None:
            return {}
            
        print("\n💎 CALCULATING RARITY-LEVEL AVERAGES")
        
        rarity_stats = {}
        
        for rarity, group in self.df.groupby('Rarity'):
            prices = []
            total_value = 0
            total_quantity = 0
            
            for _, row in group.iterrows():
                price, source = self.get_card_price(row)
                quantity = int(row.get('Quantity', 1) or 1)
                
                if price > 0:
                    prices.append(price)
                    total_value += price * quantity
                    total_quantity += quantity
            
            if prices:
                rarity_stats[rarity] = {
                    'card_count': len(group),
                    'total_quantity': total_quantity,
                    'average_price': np.mean(prices),
                    'median_price': np.median(prices),
                    'total_value': total_value,
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'price_std': np.std(prices) if len(prices) > 1 else 0
                }
        
        print(f"   Analyzed {len(rarity_stats)} rarity levels")
        return rarity_stats
    
    def calculate_condition_averages(self) -> Dict:
        """Calculate average prices by condition."""
        print("\n🎯 CALCULATING CONDITION-LEVEL AVERAGES")
        
        condition_stats = {}
        
        if self.df is not None:
            for condition, group in self.df.groupby('Condition'):
                prices = []
                total_value = 0
                total_quantity = 0
                
                for _, row in group.iterrows():
                    price, source = self.get_card_price(row)
                    quantity = int(row.get('Quantity', 1) or 1)
                    
                    if price > 0:
                        prices.append(price)
                        total_value += price * quantity
                        total_quantity += quantity
                
                if prices:
                    condition_stats[condition] = {
                        'card_count': len(group),
                        'total_quantity': total_quantity,
                        'average_price': np.mean(prices),
                        'median_price': np.median(prices),
                        'total_value': total_value,
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'price_std': np.std(prices) if len(prices) > 1 else 0
                    }
        
        print(f"   Analyzed {len(condition_stats)} condition types")
        return condition_stats
    
    def calculate_foil_vs_nonfoil_averages(self) -> Dict:
        """Calculate average prices for foil vs non-foil cards."""
        print("\n✨ CALCULATING FOIL VS NON-FOIL AVERAGES")
        
        foil_stats = {}
        
        if self.df is not None:
            # Separate foil and non-foil
            foil_cards = self.df[self.df['Foil'].str.lower().isin(['foil', 'etched'])]
            nonfoil_cards = self.df[~self.df['Foil'].str.lower().isin(['foil', 'etched'])]
            
            for category, group in [('foil', foil_cards), ('non-foil', nonfoil_cards)]:
                prices = []
                total_value = 0
                total_quantity = 0
                
                for _, row in group.iterrows():
                    price, source = self.get_card_price(row)
                    quantity = int(row.get('Quantity', 1) or 1)
                    
                    if price > 0:
                        prices.append(price)
                        total_value += price * quantity
                        total_quantity += quantity
                
                if prices:
                    foil_stats[category] = {
                        'card_count': len(group),
                        'total_quantity': total_quantity,
                        'average_price': np.mean(prices),
                        'median_price': np.median(prices),
                        'total_value': total_value,
                        'min_price': min(prices),
                        'max_price': max(prices),
                        'price_std': np.std(prices) if len(prices) > 1 else 0
                    }
            
            # Calculate foil premium
            if 'foil' in foil_stats and 'non-foil' in foil_stats:
                foil_premium = foil_stats['foil']['average_price'] / foil_stats['non-foil']['average_price']
                foil_stats['foil_premium'] = foil_premium
                print(f"   Foil premium: {foil_premium:.2f}x")
        
        return foil_stats
    
    def calculate_price_tier_averages(self) -> Dict:
        """Calculate averages by price tiers."""
        print("\n💰 CALCULATING PRICE TIER AVERAGES")
        
        tier_stats = {}
        
        # Define price tiers
        tiers = {
            'bulk': (0, 1),
            'low': (1, 5),
            'medium': (5, 25),
            'high': (25, 100),
            'ultra_high': (100, float('inf'))
        }
        
        if self.df is not None:
            for tier_name, (min_price, max_price) in tiers.items():
                tier_cards = []
                
                for _, row in self.df.iterrows():
                    price, source = self.get_card_price(row)
                    if min_price <= price < max_price:
                        quantity = int(row.get('Quantity', 1) or 1)
                        tier_cards.extend([price] * quantity)
                
                if tier_cards:
                    tier_stats[tier_name] = {
                        'card_count': len(tier_cards),
                        'price_range': f"${min_price}-${max_price if max_price != float('inf') else '∞'}",
                        'average_price': np.mean(tier_cards),
                        'median_price': np.median(tier_cards),
                        'total_value': sum(tier_cards),
                        'min_price': min(tier_cards),
                        'max_price': max(tier_cards),
                        'price_std': np.std(tier_cards) if len(tier_cards) > 1 else 0
                    }
        
        print(f"   Analyzed {len(tier_stats)} price tiers")
        return tier_stats
    
    def calculate_comprehensive_averages(self) -> Dict:
        """Calculate all types of averages."""
        print("🧮 COMPREHENSIVE AVERAGE PRICING ANALYSIS")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'collection_size': len(self.df) if self.df is not None else 0,
            'card_level': self.calculate_card_level_averages(),
            'set_level': self.calculate_set_averages(),
            'rarity_level': self.calculate_rarity_averages(),
            'condition_level': self.calculate_condition_averages(),
            'foil_analysis': self.calculate_foil_vs_nonfoil_averages(),
            'price_tiers': self.calculate_price_tier_averages()
        }
        
        # Overall collection stats
        all_prices = []
        total_value = 0
        
        if self.df is not None:
            for _, row in self.df.iterrows():
                price, source = self.get_card_price(row)
                quantity = int(row.get('Quantity', 1) or 1)
                
                if price > 0:
                    all_prices.extend([price] * quantity)
                    total_value += price * quantity
        
        if all_prices:
            results['collection_overview'] = {
                'total_cards': len(self.df) if self.df is not None else 0,
                'total_quantity': len(all_prices),
                'total_value': total_value,
                'average_card_price': np.mean(all_prices),
                'median_card_price': np.median(all_prices),
                'min_price': min(all_prices),
                'max_price': max(all_prices),
                'price_std': np.std(all_prices)
            }
        
        return results
    
    def print_average_summary(self, results: Dict):
        """Print a formatted summary of average pricing results."""
        print(f"\n📋 AVERAGE PRICING SUMMARY")
        print("=" * 50)
        
        overview = results.get('collection_overview', {})
        if overview:
            print(f"📊 Collection Overview:")
            print(f"   Total Cards: {overview['total_cards']:,}")
            print(f"   Total Quantity: {overview['total_quantity']:,}")
            print(f"   Total Value: ${overview['total_value']:,.2f}")
            print(f"   Average Price: ${overview['average_card_price']:.2f}")
            print(f"   Median Price: ${overview['median_card_price']:.2f}")
            print(f"   Price Range: ${overview['min_price']:.2f} - ${overview['max_price']:.2f}")
        
        # Rarity averages
        rarity_stats = results.get('rarity_level', {})
        if rarity_stats:
            print(f"\n💎 Average by Rarity:")
            for rarity, stats in sorted(rarity_stats.items(), 
                                      key=lambda x: x[1]['average_price'], reverse=True):
                print(f"   {rarity:<12}: ${stats['average_price']:>7.2f} "
                      f"(median: ${stats['median_price']:>6.2f}, "
                      f"cards: {stats['card_count']:>4})")
        
        # Price tier averages
        tier_stats = results.get('price_tiers', {})
        if tier_stats:
            print(f"\n💰 Average by Price Tier:")
            tier_order = ['bulk', 'low', 'medium', 'high', 'ultra_high']
            for tier in tier_order:
                if tier in tier_stats:
                    stats = tier_stats[tier]
                    print(f"   {tier:<12}: ${stats['average_price']:>7.2f} "
                          f"(range: {stats['price_range']}, "
                          f"cards: {stats['card_count']:>4})")
        
        # Foil analysis
        foil_stats = results.get('foil_analysis', {})
        if foil_stats:
            print(f"\n✨ Foil Analysis:")
            if 'non-foil' in foil_stats:
                stats = foil_stats['non-foil']
                print(f"   Non-foil avg: ${stats['average_price']:>7.2f} "
                      f"(cards: {stats['card_count']:>4})")
            if 'foil' in foil_stats:
                stats = foil_stats['foil']
                print(f"   Foil avg:     ${stats['average_price']:>7.2f} "
                      f"(cards: {stats['card_count']:>4})")
            if 'foil_premium' in foil_stats:
                print(f"   Foil premium: {foil_stats['foil_premium']:>7.2f}x")
        
        # Top sets by average price
        set_stats = results.get('set_level', {})
        if set_stats:
            print(f"\n📦 Top Sets by Average Price:")
            top_sets = sorted(set_stats.items(), 
                            key=lambda x: x[1]['average_card_price'], reverse=True)[:10]
            for set_code, stats in top_sets:
                set_name = stats.get('set_name', set_code)
                print(f"   {set_code:<6}: ${stats['average_card_price']:>7.2f} "
                      f"({set_name[:25]:<25}, cards: {stats['card_count']:>3})")
    
    def save_results(self, results: Dict, output_path: Optional[str] = None):
        """Save average pricing results to JSON file."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/average_pricing_analysis_{timestamp}.json"
        
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Results saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def run_average_pricing_analysis():
    """Run comprehensive average pricing analysis."""
    try:
        # Initialize service
        pricing_service = AveragePricingService()
        
        # Calculate all averages
        results = pricing_service.calculate_comprehensive_averages()
        
        # Print summary
        pricing_service.print_average_summary(results)
        
        # Save results
        pricing_service.save_results(results)
        
        print(f"\n✨ Average pricing analysis complete!")
        return results
        
    except Exception as e:
        print(f"❌ Error in average pricing analysis: {e}")
        return None

if __name__ == "__main__":
    run_average_pricing_analysis()
