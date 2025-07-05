#!/usr/bin/env python3
"""
Enhanced MTG Card Sorter with API Integration
Uses Scryfall API for accurate card data and improved sorting.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import argparse
from colorama import init, Fore, Style
from tabulate import tabulate
from scryfall_api import ScryfallAPI
from card_sorter import MTGCardSorter

# Initialize colorama for Windows compatibility
init()

class EnhancedMTGCardSorter(MTGCardSorter):
    """Enhanced card sorter with API integration for accurate data."""
    
    def __init__(self, csv_file: str = "moxfield_export.csv", use_api: bool = True):
        """Initialize the enhanced card sorter."""
        super().__init__(csv_file)
        self.use_api = use_api
        self.api = ScryfallAPI() if use_api else None
        self.enriched_data = {}
        
        if self.use_api:
            print(f"{Fore.YELLOW}⚠ API enrichment enabled. This may take some time...{Style.RESET_ALL}")
    
    def enrich_card_data(self, card_name: str, set_code: Optional[str] = None) -> Dict[str, Any]:
        """Enrich card data using API if available."""
        cache_key = f"{card_name}_{set_code or 'any'}"
        
        if cache_key in self.enriched_data:
            return self.enriched_data[cache_key]
        
        if self.api:
            api_data = self.api.get_card_data(card_name, set_code)
            if api_data:
                self.enriched_data[cache_key] = api_data
                return api_data
        
        # Fallback to basic data
        return {
            "name": card_name,
            "colors": [],
            "color_identity": [],
            "type_line": "",
            "rarity": "unknown"
        }
    
    def sort_by_color_accurate(self) -> Dict[str, List]:
        """Sort cards by color using API data for accuracy."""
        if self.cards_df is None:
            return {}
        
        color_groups = defaultdict(list)
        
        for _, card in self.cards_df.iterrows():
            enriched = self.enrich_card_data(card['Name'], card['Edition'])
            color_name = self.api.get_color_name(enriched.get('color_identity', [])) if self.api else 'Unknown'
            color_groups[color_name].append({**card.to_dict(), **enriched})
        
        return dict(color_groups)
    
    def sort_by_type_accurate(self) -> Dict[str, List]:
        """Sort cards by type using API data."""
        if self.cards_df is None:
            return {}
        
        type_groups = defaultdict(list)
        
        for _, card in self.cards_df.iterrows():
            enriched = self.enrich_card_data(card['Name'], card['Edition'])
            type_line = enriched.get('type_line', '')
            
            # Determine primary type
            if 'Land' in type_line:
                primary_type = 'Lands'
            elif 'Creature' in type_line:
                primary_type = 'Creatures'
            elif 'Instant' in type_line:
                primary_type = 'Instants'
            elif 'Sorcery' in type_line:
                primary_type = 'Sorceries'
            elif 'Artifact' in type_line:
                primary_type = 'Artifacts'
            elif 'Enchantment' in type_line:
                primary_type = 'Enchantments'
            elif 'Planeswalker' in type_line:
                primary_type = 'Planeswalkers'
            else:
                primary_type = 'Other'
            
            type_groups[primary_type].append({**card.to_dict(), **enriched})
        
        return dict(type_groups)
    
    def sort_by_rarity_accurate(self) -> Dict[str, List]:
        """Sort cards by rarity using API data."""
        if self.cards_df is None:
            return {}
        
        rarity_groups = defaultdict(list)
        
        for _, card in self.cards_df.iterrows():
            enriched = self.enrich_card_data(card['Name'], card['Edition'])
            rarity = enriched.get('rarity', 'unknown').title()
            
            if rarity == 'Unknown':
                # Fallback to price-based estimation
                price = float(str(card['Purchase Price']).replace('$', '') or 0)
                if price < 0.50:
                    rarity = 'Common'
                elif price < 2.00:
                    rarity = 'Uncommon'
                elif price < 10.00:
                    rarity = 'Rare'
                else:
                    rarity = 'Mythic'
            
            rarity_groups[rarity].append({**card.to_dict(), **enriched})
        
        return dict(rarity_groups)
    
    def analyze_mana_curve(self):
        """Analyze the mana curve of the collection."""
        if self.cards_df is None:
            return
        
        mana_costs = defaultdict(int)
        
        for _, card in self.cards_df.iterrows():
            enriched = self.enrich_card_data(card['Name'], card['Edition'])
            cmc = enriched.get('cmc', 0)
            count = card['Count']
            
            if cmc >= 7:
                mana_costs['7+'] += count
            else:
                mana_costs[str(int(cmc))] += count
        
        print(f"\n{Fore.CYAN}=== Mana Curve Analysis ==={Style.RESET_ALL}")
        for cost in ['0', '1', '2', '3', '4', '5', '6', '7+']:
            count = mana_costs.get(cost, 0)
            bar = '█' * min(count // 5, 50)  # Scale the bar
            print(f"CMC {cost}: {count:3d} {bar}")
    
    def find_expensive_cards(self, min_price: float = 10.0):
        """Find cards above a certain price threshold."""
        if self.cards_df is None:
            return
        
        expensive_cards = []
        
        for _, card in self.cards_df.iterrows():
            # Check purchase price first
            purchase_price = float(str(card['Purchase Price']).replace('$', '') or 0)
            
            if purchase_price >= min_price:
                expensive_cards.append({
                    'Name': card['Name'],
                    'Edition': card['Edition'],
                    'Purchase Price': f"${purchase_price:.2f}",
                    'Count': card['Count']
                })
            elif self.api:
                # Check current market price from API
                enriched = self.enrich_card_data(card['Name'], card['Edition'])
                current_price = float(enriched.get('prices', {}).get('usd', 0) or 0)
                
                if current_price >= min_price:
                    expensive_cards.append({
                        'Name': card['Name'],
                        'Edition': card['Edition'],
                        'Current Price': f"${current_price:.2f}",
                        'Purchase Price': f"${purchase_price:.2f}",
                        'Count': card['Count']
                    })
        
        if expensive_cards:
            print(f"\n{Fore.YELLOW}=== Cards Worth ${min_price}+ ==={Style.RESET_ALL}")
            df = pd.DataFrame(expensive_cards)
            print(tabulate(df.values, headers=list(df.columns), tablefmt='grid'))
        else:
            print(f"\n{Fore.GREEN}No cards found worth ${min_price} or more.{Style.RESET_ALL}")
    
    def export_enhanced_collection(self, sort_type: str, output_dir: str = "enhanced_sorted"):
        """Export enhanced sorted collection with API data."""
        if self.cards_df is None:
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if sort_type == "color":
            groups = self.sort_by_color_accurate()
        elif sort_type == "type":
            groups = self.sort_by_type_accurate()
        elif sort_type == "rarity":
            groups = self.sort_by_rarity_accurate()
        else:
            print(f"{Fore.RED}✗ Unknown sort type: {sort_type}{Style.RESET_ALL}")
            return
        
        for group_name, cards in groups.items():
            if cards:
                df = pd.DataFrame(cards)
                
                # Add useful columns from API data
                api_columns = ['mana_cost', 'cmc', 'color_identity', 'type_line', 'rarity']
                for col in api_columns:
                    if col in df.columns:
                        continue  # Column already exists
                
                filename = f"enhanced_{sort_type}_{group_name.replace(' ', '_').lower()}.csv"
                filepath = output_path / filename
                df.to_csv(filepath, index=False)
                print(f"{Fore.GREEN}✓ Exported {len(cards)} cards to {filepath}{Style.RESET_ALL}")


def main():
    """Main function for the enhanced card sorter."""
    parser = argparse.ArgumentParser(description="Enhanced MyManaBox - MTG Card Sorter with API")
    parser.add_argument("--csv", default="moxfield_export.csv", help="Path to CSV file")
    parser.add_argument("--no-api", action="store_true", help="Disable API enrichment")
    parser.add_argument("--sort", choices=["color", "type", "rarity"], help="Sort and export by category")
    parser.add_argument("--mana-curve", action="store_true", help="Analyze mana curve")
    parser.add_argument("--expensive", type=float, default=10.0, help="Find expensive cards (default: $10+)")
    
    args = parser.parse_args()
    
    # Create enhanced sorter
    sorter = EnhancedMTGCardSorter(args.csv, use_api=not args.no_api)
    
    if args.mana_curve:
        sorter.analyze_mana_curve()
    elif args.expensive:
        sorter.find_expensive_cards(args.expensive)
    elif args.sort:
        sorter.export_enhanced_collection(args.sort)
    else:
        print(f"\n{Fore.CYAN}Enhanced MyManaBox - MTG Card Sorter!{Style.RESET_ALL}")
        print("Enhanced features:")
        print("1. Accurate color sorting using API")
        print("2. Precise type identification")
        print("3. Real rarity information")
        print("4. Mana curve analysis")
        print("5. Market price tracking")
        
        if sorter.api:
            print(f"\n{Fore.GREEN}✓ API integration enabled{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠ API integration disabled{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
