"""Console interface for MyManaBox."""

from typing import Optional
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init()


class ConsoleInterface:
    """Main console interface for MyManaBox."""
    
    def __init__(self, collection_service, sorting_service, search_service, 
                 analytics_service, import_service):
        """Initialize console interface."""
        self.collection_service = collection_service
        self.sorting_service = sorting_service
        self.search_service = search_service
        self.analytics_service = analytics_service
        self.import_service = import_service
    
    def run(self, args=None):
        """Run the console interface."""
        # For now, just test basic functionality
        print(f"{Fore.CYAN}MyManaBox - MTG Card Collection Manager{Style.RESET_ALL}")
        print("Refactored with separation of concerns!")
        
        # Test loading collection
        if self.collection_service.load_collection():
            collection = self.collection_service.get_collection()
            if collection:
                print(f"{Fore.GREEN}✓ Loaded collection with {collection.unique_cards} unique cards{Style.RESET_ALL}")
                
                # Show basic summary with purchase prices first
                print(f"Total cards: {collection.total_cards}")
                print(f"Total purchase value: ${collection.total_value:.2f}")
                
                # Ask if user wants to enrich with current market data
                print(f"\n{Fore.CYAN}Note: This shows purchase prices from your CSV.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}To see current market values (like Moxfield shows), we can enrich the data.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}This will take about 2-3 minutes for {collection.unique_cards} unique cards.{Style.RESET_ALL}")
                
                enrich = input(f"\nEnrich with current market prices? (y/N): ").lower().strip()
                
                if enrich == 'y' or enrich == 'yes':
                    # Enrich collection with current market prices
                    print(f"{Fore.YELLOW}Enriching collection with current market data...{Style.RESET_ALL}")
                    
                    def progress_callback(current, total):
                        percent = (current / total) * 100
                        if current % 50 == 0 or current == total:  # Show progress every 50 cards
                            print(f"Progress: {current}/{total} cards ({percent:.1f}%)")
                    
                    enriched_count = self.collection_service.enrich_collection_data(progress_callback)
                    if enriched_count > 0:
                        print(f"{Fore.GREEN}✓ Enriched {enriched_count} cards with market data{Style.RESET_ALL}")
                        print(f"Total current market value: ${collection.total_value:.2f}")
                    else:
                        print(f"{Fore.YELLOW}No cards were enriched (may be using cached data){Style.RESET_ALL}")
                
                # Test sorting
                color_groups = self.sorting_service.sort_by_color(collection)
                print(f"Color groups: {len(color_groups)}")
                
                # Show some duplicates
                duplicates = self.search_service.find_duplicates(collection)
                print(f"Duplicate cards: {len(duplicates)}")
        else:
            print(f"{Fore.YELLOW}No collection loaded{Style.RESET_ALL}")
