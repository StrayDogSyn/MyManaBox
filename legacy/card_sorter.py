#!/usr/bin/env python3
"""
MyManaBox - Magic: The Gathering Card Sorting Program
A comprehensive tool for organizing and managing MTG card collections.
"""

import pandas as pd
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import argparse
from colorama import init, Fore, Style
from tabulate import tabulate
import shutil

# Initialize colorama for Windows compatibility
init()

class MTGCardSorter:
    """Main class for handling Magic: The Gathering card sorting and organization."""
    
    def __init__(self, csv_file: str = "moxfield_export.csv"):
        """Initialize the card sorter with a CSV file."""
        self.csv_file = csv_file
        self.cards_df = None
        self.load_cards()
        
    def load_cards(self):
        """Load cards from the CSV file."""
        try:
            self.cards_df = pd.read_csv(self.csv_file)
            print(f"{Fore.GREEN}✓ Loaded {len(self.cards_df)} cards from {self.csv_file}{Style.RESET_ALL}")
        except FileNotFoundError:
            print(f"{Fore.RED}✗ Error: Could not find {self.csv_file}{Style.RESET_ALL}")
            return
        except Exception as e:
            print(f"{Fore.RED}✗ Error loading CSV: {e}{Style.RESET_ALL}")
            return
    
    def display_summary(self):
        """Display a summary of the card collection."""
        if self.cards_df is None:
            return
            
        total_cards = self.cards_df['Count'].sum()
        unique_cards = len(self.cards_df)
        total_value = self.cards_df['Purchase Price'].replace('', 0).astype(str).str.replace('$', '').astype(float).sum()
        
        print(f"\n{Fore.CYAN}=== Collection Summary ==={Style.RESET_ALL}")
        print(f"Total Cards: {total_cards}")
        print(f"Unique Cards: {unique_cards}")
        print(f"Total Purchase Value: ${total_value:.2f}")
        
        # Top 10 most valuable cards
        df_with_prices = self.cards_df.copy()
        df_with_prices['Price'] = df_with_prices['Purchase Price'].replace('', 0).astype(str).str.replace('$', '').astype(float)
        top_valuable = df_with_prices.nlargest(10, 'Price')[['Name', 'Edition', 'Price', 'Count']]
        
        if not top_valuable.empty:
            print(f"\n{Fore.YELLOW}Top 10 Most Valuable Cards:{Style.RESET_ALL}")
            print(tabulate(top_valuable.values, headers=['Name', 'Edition', 'Price', 'Count'], tablefmt='grid'))
    
    def sort_by_color(self) -> Dict[str, List]:
        """Sort cards by color identity (requires API lookup for accurate color data)."""
        if self.cards_df is None:
            return {}
            
        color_groups = {
            'White': [],
            'Blue': [],
            'Black': [],
            'Red': [],
            'Green': [],
            'Colorless': [],
            'Multicolor': []
        }
        
        # For now, sort by basic color associations in card names
        # This is a simplified approach - a full implementation would use the Scryfall API
        for _, card in self.cards_df.iterrows():
            name = card['Name'].lower()
            # Basic heuristic color sorting (this would be much better with API data)
            if any(word in name for word in ['swamp', 'black', 'dark', 'death', 'shadow']):
                color_groups['Black'].append(card)
            elif any(word in name for word in ['island', 'blue', 'water', 'counter', 'draw']):
                color_groups['Blue'].append(card)
            elif any(word in name for word in ['plains', 'white', 'angel', 'heal', 'life']):
                color_groups['White'].append(card)
            elif any(word in name for word in ['mountain', 'red', 'fire', 'lightning', 'burn']):
                color_groups['Red'].append(card)
            elif any(word in name for word in ['forest', 'green', 'elf', 'growth', 'nature']):
                color_groups['Green'].append(card)
            elif any(word in name for word in ['artifact', 'colorless']):
                color_groups['Colorless'].append(card)
            else:
                color_groups['Multicolor'].append(card)
        
        return color_groups
    
    def sort_by_set(self) -> Dict[str, List]:
        """Sort cards by set/edition."""
        if self.cards_df is None:
            return {}
            
        set_groups = defaultdict(list)
        for _, card in self.cards_df.iterrows():
            set_groups[card['Edition']].append(card)
        
        return dict(set_groups)
    
    def sort_by_rarity(self) -> Dict[str, List]:
        """Sort cards by rarity (would need API data for accurate rarity)."""
        if self.cards_df is None:
            return {}
            
        # Placeholder - would need API integration for real rarity data
        rarity_groups = {
            'Common': [],
            'Uncommon': [],
            'Rare': [],
            'Mythic Rare': []
        }
        
        # Basic heuristic based on purchase price
        for _, card in self.cards_df.iterrows():
            price = float(str(card['Purchase Price']).replace('$', '') or 0)
            if price == 0:
                rarity_groups['Common'].append(card)
            elif price < 0.50:
                rarity_groups['Common'].append(card)
            elif price < 2.00:
                rarity_groups['Uncommon'].append(card)
            elif price < 10.00:
                rarity_groups['Rare'].append(card)
            else:
                rarity_groups['Mythic Rare'].append(card)
        
        return rarity_groups
    
    def sort_by_type(self) -> Dict[str, List]:
        """Sort cards by type (heuristic based on card names)."""
        if self.cards_df is None:
            return {}
            
        type_groups = {
            'Creatures': [],
            'Instants': [],
            'Sorceries': [],
            'Artifacts': [],
            'Enchantments': [],
            'Planeswalkers': [],
            'Lands': [],
            'Other': []
        }
        
        # Basic heuristic type sorting based on common naming patterns
        for _, card in self.cards_df.iterrows():
            name = card['Name'].lower()
            
            if any(word in name for word in ['swamp', 'island', 'plains', 'mountain', 'forest', 'hub', 'wastes']):
                type_groups['Lands'].append(card)
            elif any(word in name for word in ['angel', 'demon', 'dragon', 'elf', 'knight', 'beast', 'warrior']):
                type_groups['Creatures'].append(card)
            elif any(word in name for word in ['aether', 'mana', 'mind', 'soul']):
                type_groups['Artifacts'].append(card)
            else:
                type_groups['Other'].append(card)
        
        return type_groups
    
    def export_sorted_collection(self, sort_type: str, output_dir: str = "sorted_output"):
        """Export sorted collection to CSV files."""
        if self.cards_df is None:
            return
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if sort_type == "color":
            groups = self.sort_by_color()
        elif sort_type == "set":
            groups = self.sort_by_set()
        elif sort_type == "rarity":
            groups = self.sort_by_rarity()
        elif sort_type == "type":
            groups = self.sort_by_type()
        else:
            print(f"{Fore.RED}✗ Unknown sort type: {sort_type}{Style.RESET_ALL}")
            return
        
        for group_name, cards in groups.items():
            if cards:  # Only create files for non-empty groups
                df = pd.DataFrame(cards)
                filename = f"{sort_type}_{group_name.replace(' ', '_').lower()}.csv"
                filepath = output_path / filename
                df.to_csv(filepath, index=False)
                print(f"{Fore.GREEN}✓ Exported {len(cards)} cards to {filepath}{Style.RESET_ALL}")
    
    def find_duplicates(self):
        """Find duplicate cards in the collection."""
        if self.cards_df is None:
            return
            
        # Group by name and edition to find duplicates
        duplicates = self.cards_df.groupby(['Name', 'Edition']).agg({
            'Count': 'sum',
            'Purchase Price': 'first'
        }).reset_index()
        
        # Filter for cards with count > 1
        real_duplicates = duplicates[duplicates['Count'] > 1]
        
        if not real_duplicates.empty:
            print(f"\n{Fore.YELLOW}=== Duplicate Cards ==={Style.RESET_ALL}")
            print(tabulate(real_duplicates.values, headers=['Name', 'Edition', 'Total Count', 'Price'], tablefmt='grid'))
        else:
            print(f"\n{Fore.GREEN}✓ No duplicate cards found!{Style.RESET_ALL}")
    
    def search_cards(self, query: str):
        """Search for cards by name."""
        if self.cards_df is None:
            return
            
        results = self.cards_df[self.cards_df['Name'].str.contains(query, case=False, na=False)]
        
        if not results.empty:
            print(f"\n{Fore.CYAN}=== Search Results for '{query}' ==={Style.RESET_ALL}")
            display_cols = ['Name', 'Edition', 'Count', 'Purchase Price', 'Condition']
            print(tabulate(results[display_cols].values, headers=display_cols, tablefmt='grid'))
        else:
            print(f"\n{Fore.YELLOW}No cards found matching '{query}'{Style.RESET_ALL}")
    
    def get_collection_statistics(self):
        """Get detailed statistics about the collection."""
        if self.cards_df is None:
            return
            
        print(f"\n{Fore.CYAN}=== Detailed Collection Statistics ==={Style.RESET_ALL}")
        
        # Cards by condition
        condition_stats = self.cards_df.groupby('Condition')['Count'].sum().sort_values(ascending=False)
        print(f"\n{Fore.YELLOW}Cards by Condition:{Style.RESET_ALL}")
        for condition, count in condition_stats.items():
            print(f"  {condition}: {count}")
        
        # Cards by set (top 10)
        set_stats = self.cards_df.groupby('Edition')['Count'].sum().sort_values(ascending=False).head(10)
        print(f"\n{Fore.YELLOW}Top 10 Sets by Card Count:{Style.RESET_ALL}")
        for edition, count in set_stats.items():
            print(f"  {edition}: {count}")
        
        # Foil vs non-foil
        foil_count = len(self.cards_df[self.cards_df['Foil'] != ''])
        non_foil_count = len(self.cards_df[self.cards_df['Foil'] == ''])
        print(f"\n{Fore.YELLOW}Foil Status:{Style.RESET_ALL}")
        print(f"  Foil cards: {foil_count}")
        print(f"  Non-foil cards: {non_foil_count}")
    
    def import_from_moxfield_url(self, url: str, backup_existing: bool = True) -> bool:
        """Import collection from a Moxfield collection URL."""
        print(f"{Fore.CYAN}Importing collection from Moxfield URL...{Style.RESET_ALL}")
        
        # Backup existing collection if requested
        if backup_existing and Path(self.csv_file).exists():
            backup_file = f"{self.csv_file}.backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                Path(self.csv_file).rename(backup_file)
                print(f"{Fore.GREEN}✓ Backed up existing collection to {backup_file}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Could not backup existing file: {e}{Style.RESET_ALL}")
        
        try:
            # Extract collection ID from URL
            if "/collection/" in url:
                collection_id = url.split("/collection/")[1].split("/")[0].split("?")[0]
            else:
                print(f"{Fore.RED}✗ Invalid Moxfield collection URL format{Style.RESET_ALL}")
                return False
            
            print(f"{Fore.YELLOW}Attempting to fetch collection data...{Style.RESET_ALL}")
            
            # Try different API endpoints and methods
            endpoints_to_try = [
                f"https://api.moxfield.com/v2/collections/{collection_id}/export/csv",
                f"https://api.moxfield.com/v3/collections/{collection_id}/export/csv",
                f"https://moxfield.com/collections/{collection_id}/export/csv"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/csv,text/plain,*/*',
                'Referer': url
            }
            
            success = False
            for endpoint in endpoints_to_try:
                try:
                    print(f"{Fore.YELLOW}Trying: {endpoint}{Style.RESET_ALL}")
                    response = requests.get(endpoint, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        # Check if we got CSV content
                        content = response.text
                        if content and ('Count' in content or 'Name' in content):
                            # Save the CSV content
                            with open(self.csv_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            print(f"{Fore.GREEN}✓ Collection data downloaded successfully{Style.RESET_ALL}")
                            success = True
                            break
                        else:
                            print(f"{Fore.YELLOW}⚠ Response doesn't contain expected CSV data{Style.RESET_ALL}")
                    elif response.status_code == 403:
                        print(f"{Fore.YELLOW}⚠ Access forbidden - collection may be private{Style.RESET_ALL}")
                    elif response.status_code == 404:
                        print(f"{Fore.YELLOW}⚠ Collection not found{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠ HTTP {response.status_code} response{Style.RESET_ALL}")
                        
                except requests.RequestException as e:
                    print(f"{Fore.YELLOW}⚠ Request failed: {e}{Style.RESET_ALL}")
                    continue
            
            if not success:
                print(f"\n{Fore.RED}✗ Could not access the collection data.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}This could be because:{Style.RESET_ALL}")
                print(f"  • The collection is set to private")
                print(f"  • The collection URL is invalid") 
                print(f"  • Moxfield's API has changed")
                print(f"\n{Fore.CYAN}Alternative options:{Style.RESET_ALL}")
                print(f"  1. Make sure the collection is public on Moxfield")
                print(f"  2. Export the collection manually from Moxfield:")
                print(f"     - Go to {url}")
                print(f"     - Click 'Export' button")
                print(f"     - Download as CSV")
                print(f"     - Save as 'moxfield_export.csv' in this directory")
                return False
            
            # Reload the collection
            self.load_cards()
            
            if self.cards_df is not None:
                print(f"{Fore.GREEN}✓ Collection import completed successfully!{Style.RESET_ALL}")
                print(f"   - {len(self.cards_df)} unique cards imported")
                print(f"   - {self.cards_df['Count'].sum()} total cards")
                return True
            else:
                print(f"{Fore.RED}✗ Failed to load imported collection{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}✗ Error importing collection: {e}{Style.RESET_ALL}")
            return False

    def import_from_file(self, file_path: str, backup_existing: bool = True) -> bool:
        """Import collection from a downloaded CSV file."""
        print(f"{Fore.CYAN}Importing collection from file: {file_path}{Style.RESET_ALL}")
        
        if not Path(file_path).exists():
            print(f"{Fore.RED}✗ File not found: {file_path}{Style.RESET_ALL}")
            return False
        
        # Backup existing collection if requested
        if backup_existing and Path(self.csv_file).exists():
            backup_file = f"{self.csv_file}.backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                Path(self.csv_file).rename(backup_file)
                print(f"{Fore.GREEN}✓ Backed up existing collection to {backup_file}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Could not backup existing file: {e}{Style.RESET_ALL}")
        
        try:
            # Copy the file to our standard location
            shutil.copy2(file_path, self.csv_file)
            print(f"{Fore.GREEN}✓ Collection file copied successfully{Style.RESET_ALL}")
            
            # Reload the collection
            self.load_cards()
            
            if self.cards_df is not None:
                print(f"{Fore.GREEN}✓ Collection import completed successfully!{Style.RESET_ALL}")
                print(f"   - {len(self.cards_df)} unique cards imported")
                print(f"   - {self.cards_df['Count'].sum()} total cards")
                return True
            else:
                print(f"{Fore.RED}✗ Failed to load imported collection{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}✗ Error importing file: {e}{Style.RESET_ALL}")
            return False

    def show_manual_import_instructions(self, url: str):
        """Show detailed instructions for manual collection import."""
        print(f"\n{Fore.CYAN}=== Manual Import Instructions ==={Style.RESET_ALL}")
        print(f"\nSince automatic import failed, please follow these steps:")
        print(f"\n{Fore.YELLOW}Step 1: Access Your Collection{Style.RESET_ALL}")
        print(f"  • Go to: {url}")
        print(f"  • Make sure you're logged into Moxfield")
        print(f"  • Ensure the collection is set to 'Public' if you want to share it")
        
        print(f"\n{Fore.YELLOW}Step 2: Export Your Collection{Style.RESET_ALL}")
        print(f"  • Look for an 'Export' or 'Download' button on the collection page")
        print(f"  • Select 'CSV' format")
        print(f"  • Download the file")
        
        print(f"\n{Fore.YELLOW}Step 3: Import to MyManaBox{Style.RESET_ALL}")
        print(f"  • Save the downloaded CSV file in this directory:")
        print(f"    {Path.cwd()}")
        print(f"  • Rename it to 'moxfield_export.csv' or use the --import-file option:")
        print(f"    python card_sorter.py --import-file 'your_downloaded_file.csv'")
        
        print(f"\n{Fore.GREEN}Alternative: Direct File Import{Style.RESET_ALL}")
        print(f"  • If you already have the CSV file, use:")
        print(f"    python card_sorter.py --import-file 'path_to_your_file.csv'")
        
        print(f"\n{Fore.CYAN}Once imported, you can use all MyManaBox features!{Style.RESET_ALL}")
    
    def update_from_url(self, url: str) -> bool:
        """Update collection from various supported URLs."""
        if "moxfield.com" in url.lower():
            success = self.import_from_moxfield_url(url)
            if not success:
                self.show_manual_import_instructions(url)
            return success
        else:
            print(f"{Fore.RED}✗ Unsupported URL format. Currently supported: Moxfield collections{Style.RESET_ALL}")
            return False


def main():
    """Main function to run the card sorting program."""
    parser = argparse.ArgumentParser(description="MyManaBox - MTG Card Sorting Program")
    parser.add_argument("--csv", default="moxfield_export.csv", help="Path to CSV file")
    parser.add_argument("--sort", choices=["color", "set", "rarity", "type"], help="Sort and export by category")
    parser.add_argument("--search", help="Search for cards by name")
    parser.add_argument("--duplicates", action="store_true", help="Find duplicate cards")
    parser.add_argument("--stats", action="store_true", help="Show collection statistics")
    parser.add_argument("--summary", action="store_true", help="Show collection summary")
    parser.add_argument("--import-url", help="Import collection from URL (Moxfield supported)")
    parser.add_argument("--import-file", help="Import collection from a local CSV file")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup when importing")
    
    args = parser.parse_args()
    
    # Handle URL import first if specified
    if args.import_url:
        print(f"{Fore.CYAN}=== Collection Import ==={Style.RESET_ALL}")
        sorter = MTGCardSorter(args.csv)
        success = sorter.update_from_url(args.import_url)
        if success:
            print(f"\n{Fore.GREEN}Collection import completed! You can now use other commands.{Style.RESET_ALL}")
            # Show summary after successful import
            sorter.display_summary()
        return
    
    # Handle file import
    if args.import_file:
        print(f"{Fore.CYAN}=== Collection File Import ==={Style.RESET_ALL}")
        sorter = MTGCardSorter(args.csv)
        success = sorter.import_from_file(args.import_file, backup_existing=not args.no_backup)
        if success:
            print(f"\n{Fore.GREEN}Collection import completed! You can now use other commands.{Style.RESET_ALL}")
            # Show summary after successful import
            sorter.display_summary()
        return
    
    # Create the sorter instance
    sorter = MTGCardSorter(args.csv)
    
    if args.summary:
        sorter.display_summary()
    elif args.stats:
        sorter.get_collection_statistics()
    elif args.duplicates:
        sorter.find_duplicates()
    elif args.search:
        sorter.search_cards(args.search)
    elif args.sort:
        sorter.export_sorted_collection(args.sort)
    elif args.import_file:
        sorter.import_from_file(args.import_file, not args.no_backup)
    else:
        # Interactive mode
        print(f"\n{Fore.CYAN}Welcome to MyManaBox - MTG Card Sorter!{Style.RESET_ALL}")
        print("\nAvailable commands:")
        print("1. Show summary")
        print("2. Show statistics") 
        print("3. Find duplicates")
        print("4. Search cards")
        print("5. Sort by color")
        print("6. Sort by set")
        print("7. Sort by rarity")
        print("8. Sort by type")
        print("9. Exit")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}Enter your choice (1-9): {Style.RESET_ALL}")
                
                if choice == "1":
                    sorter.display_summary()
                elif choice == "2":
                    sorter.get_collection_statistics()
                elif choice == "3":
                    sorter.find_duplicates()
                elif choice == "4":
                    query = input("Enter search term: ")
                    sorter.search_cards(query)
                elif choice == "5":
                    sorter.export_sorted_collection("color")
                elif choice == "6":
                    sorter.export_sorted_collection("set")
                elif choice == "7":
                    sorter.export_sorted_collection("rarity")
                elif choice == "8":
                    sorter.export_sorted_collection("type")
                elif choice == "9":
                    print(f"{Fore.GREEN}Thanks for using MyManaBox!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 1-9.{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.GREEN}Thanks for using MyManaBox!{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
