#!/usr/bin/env python3
"""
Enrich Collection Script - Export CSV with all available Scryfall API data.
This script will enrich your collection with comprehensive card data and export it to CSV.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.data import CSVLoader, ScryfallClient
from src.services import CollectionService
from colorama import init, Fore, Style

init()


def main():
    """Enrich and export collection with all Scryfall data."""
    print(f"{Fore.CYAN}MyManaBox - Collection Enrichment Tool{Style.RESET_ALL}")
    print("=" * 50)
    
    # Create services
    csv_loader = CSVLoader("data/moxfield_export.csv")
    scryfall_client = ScryfallClient()
    collection_service = CollectionService(csv_loader, scryfall_client)
    
    # Load collection
    print(f"{Fore.YELLOW}Loading collection...{Style.RESET_ALL}")
    if not collection_service.load_collection():
        print(f"{Fore.RED}Failed to load collection from data/moxfield_export.csv{Style.RESET_ALL}")
        return 1
    
    collection = collection_service.get_collection()
    if not collection:
        print(f"{Fore.RED}Collection is empty{Style.RESET_ALL}")
        return 1
    
    print(f"{Fore.GREEN}✓ Loaded {collection.unique_cards} unique cards ({collection.total_cards} total){Style.RESET_ALL}")
    print(f"Current purchase value: ${collection.total_value:.2f}")
    
    # Show what will be enriched
    print(f"\n{Fore.CYAN}This tool will enrich your collection with:{Style.RESET_ALL}")
    print("• Current market prices (USD, EUR, TIX)")
    print("• Card colors, types, and rarity")
    print("• Mana cost and converted mana cost")
    print("• Power, toughness, loyalty")
    print("• Oracle text and flavor text")
    print("• Artist and set information")
    print("• Legal format information")
    print("• Image URLs for all sizes")
    print("• EDHREC and Penny Dreadful rankings")
    print("• Card properties (reserved, promo, etc.)")
    
    # Estimate time
    print(f"\n{Fore.YELLOW}Estimated time: {(collection.unique_cards * 0.05 / 60):.1f} minutes{Style.RESET_ALL}")
    print(f"(Rate limited to respect Scryfall API)")
    
    # Confirm
    confirm = input(f"\nProceed with enrichment? (y/N): ").lower().strip()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return 0
    
    # Export enriched collection
    output_file = "data/enriched_collection.csv"
    success = collection_service.export_enriched_collection(output_file)
    
    if success:
        # Show updated values
        print(f"\n{Fore.GREEN}=== Results ==={Style.RESET_ALL}")
        print(f"Purchase value: ${sum(card.purchase_price * card.count for card in collection.cards if card.purchase_price):.2f}")
        print(f"Current market value: ${collection.total_value:.2f}")
        difference = collection.total_value - sum(card.purchase_price * card.count for card in collection.cards if card.purchase_price)
        print(f"Value appreciation: ${difference:.2f}")
        
        # Show file info
        output_path = Path(output_file)
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nEnriched CSV saved: {output_file} ({size_mb:.1f} MB)")
        
        print(f"\n{Fore.CYAN}The enriched CSV includes {len(collection.cards[0].to_dict())} columns with comprehensive card data!{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}Failed to export enriched collection{Style.RESET_ALL}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
