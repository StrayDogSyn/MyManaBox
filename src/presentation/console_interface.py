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
                
                # Show basic summary
                print(f"Total cards: {collection.total_cards}")
                print(f"Total value: ${collection.total_value:.2f}")
                
                # Test sorting
                color_groups = self.sorting_service.sort_by_color(collection)
                print(f"Color groups: {len(color_groups)}")
                
                # Show some duplicates
                duplicates = self.search_service.find_duplicates(collection)
                print(f"Duplicate cards: {len(duplicates)}")
        else:
            print(f"{Fore.YELLOW}No collection loaded{Style.RESET_ALL}")
