#!/usr/bin/env python3
"""
MyManaBox - Magic: The Gathering Card Collection Manager
A comprehensive tool for organizing and managing MTG card collections.

Refactored with separation of concerns principles:
- Data models in src/models/
- Data access in src/data/  
- Business logic in src/services/
- Presentation in src/presentation/
- Utilities in src/utils/
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.data import CSVLoader, ScryfallClient, FileManager
from src.services import (
    CollectionService, SortingService, SearchService, 
    AnalyticsService, ImportService
)
from src.presentation import ConsoleInterface
from src.utils import Constants


def create_services(csv_file: str = Constants.DEFAULT_CSV_FILE, 
                   use_api: bool = True) -> tuple:
    """Create and configure all services."""
    
    # Data access layer
    csv_loader = CSVLoader(csv_file)
    scryfall_client = ScryfallClient() if use_api else None
    file_manager = FileManager()
    
    # Business logic layer
    collection_service = CollectionService(csv_loader, scryfall_client)
    sorting_service = SortingService(csv_loader)
    search_service = SearchService()
    analytics_service = AnalyticsService()
    import_service = ImportService(csv_loader, file_manager)
    
    return (collection_service, sorting_service, search_service, 
            analytics_service, import_service)


def main():
    """Main entry point."""
    try:
        # Create services
        services = create_services()
        
        # Create and run console interface
        console = ConsoleInterface(*services)
        console.run()
        
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
