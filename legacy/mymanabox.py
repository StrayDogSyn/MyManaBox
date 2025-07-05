#!/usr/bin/env python3
"""
MyManaBox CLI - Simple command-line interface for the MTG card sorter
"""

from card_sorter import MTGCardSorter
from enhanced_sorter import EnhancedMTGCardSorter
from colorama import init, Fore, Style
import argparse
import sys

init()

def show_banner():
    """Display the application banner."""
    print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                        MyManaBox                             ║
║              Magic: The Gathering Card Sorter               ║
║                                                              ║
║  Organize your MTG collection with powerful sorting tools   ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="MyManaBox - Magic: The Gathering Card Sorting Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mymanabox.py --summary                    # Show collection summary
  python mymanabox.py --search "Lightning Bolt"    # Search for specific cards
  python mymanabox.py --sort color                 # Sort by color and export
  python mymanabox.py --enhanced --mana-curve      # Show mana curve (with API)
  python mymanabox.py --duplicates                 # Find duplicate cards
  python mymanabox.py --expensive 20               # Find cards worth $20+
        """
    )
    
    # Input options
    parser.add_argument("--csv", default="moxfield_export.csv", 
                       help="Path to your card collection CSV file")
    parser.add_argument("--import-url", metavar="URL",
                       help="Import collection from URL (supports Moxfield collections)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup when importing new collection")
    
    # Analysis options
    parser.add_argument("--summary", action="store_true",
                       help="Show collection summary")
    parser.add_argument("--stats", action="store_true",
                       help="Show detailed collection statistics")
    parser.add_argument("--duplicates", action="store_true", 
                       help="Find duplicate cards in collection")
    parser.add_argument("--search", metavar="TERM",
                       help="Search for cards by name")
    
    # Sorting options
    parser.add_argument("--sort", choices=["color", "set", "rarity", "type"],
                       help="Sort collection by category and export to CSV files")
    
    # Enhanced features (requires API)
    parser.add_argument("--enhanced", action="store_true",
                       help="Use enhanced features with Scryfall API")
    parser.add_argument("--mana-curve", action="store_true",
                       help="Analyze mana curve (enhanced mode only)")
    parser.add_argument("--expensive", type=float, metavar="PRICE",
                       help="Find expensive cards above price threshold")
    
    # Output options
    parser.add_argument("--output-dir", default="sorted_output",
                       help="Directory for exported CSV files")
    parser.add_argument("--no-api", action="store_true",
                       help="Disable API features even in enhanced mode")
    
    args = parser.parse_args()
    
    # Show banner
    show_banner()
    
    # Handle URL import first if specified
    if args.import_url:
        print(f"{Fore.CYAN}=== Collection Import ==={Style.RESET_ALL}")
        # Use enhanced mode if available
        if args.enhanced or args.mana_curve or args.expensive is not None:
            sorter = EnhancedMTGCardSorter(args.csv, use_api=not args.no_api)
        else:
            sorter = MTGCardSorter(args.csv)
        
        success = sorter.update_from_url(args.import_url)
        if success:
            print(f"\n{Fore.GREEN}Collection import completed! You can now use other commands.{Style.RESET_ALL}")
            # Show summary after successful import
            if hasattr(sorter, 'display_summary'):
                sorter.display_summary()
        return 0
    
    # Determine which sorter to use
    if args.enhanced or args.mana_curve or args.expensive is not None:
        print(f"{Fore.YELLOW}Using enhanced mode with API integration...{Style.RESET_ALL}")
        sorter = EnhancedMTGCardSorter(args.csv, use_api=not args.no_api)
        is_enhanced = True
    else:
        print(f"{Fore.GREEN}Using basic mode...{Style.RESET_ALL}")
        sorter = MTGCardSorter(args.csv)
        is_enhanced = False
    
    # Execute requested action
    try:
        if args.summary:
            if hasattr(sorter, 'display_summary'):
                sorter.display_summary()
            else:
                print(f"{Fore.RED}Summary not available in this mode{Style.RESET_ALL}")
                
        elif args.stats:
            if hasattr(sorter, 'get_collection_statistics'):
                sorter.get_collection_statistics()
            else:
                print(f"{Fore.RED}Statistics not available in this mode{Style.RESET_ALL}")
                
        elif args.duplicates:
            if hasattr(sorter, 'find_duplicates'):
                sorter.find_duplicates()
            else:
                print(f"{Fore.RED}Duplicate detection not available in this mode{Style.RESET_ALL}")
                
        elif args.search:
            if hasattr(sorter, 'search_cards'):
                sorter.search_cards(args.search)
            else:
                print(f"{Fore.RED}Search not available in this mode{Style.RESET_ALL}")
                
        elif args.sort:
            if is_enhanced and hasattr(sorter, 'export_enhanced_collection'):
                sorter.export_enhanced_collection(args.sort, args.output_dir)
            elif hasattr(sorter, 'export_sorted_collection'):
                sorter.export_sorted_collection(args.sort, args.output_dir)
            else:
                print(f"{Fore.RED}Sorting not available in this mode{Style.RESET_ALL}")
                
        elif args.mana_curve:
            if is_enhanced and hasattr(sorter, 'analyze_mana_curve'):
                sorter.analyze_mana_curve()
            else:
                print(f"{Fore.RED}Mana curve analysis requires enhanced mode{Style.RESET_ALL}")
                
        elif args.expensive is not None:
            if is_enhanced and hasattr(sorter, 'find_expensive_cards'):
                sorter.find_expensive_cards(args.expensive)
            else:
                print(f"{Fore.RED}Expensive card search requires enhanced mode{Style.RESET_ALL}")
                
        else:
            # Interactive mode
            print(f"\n{Fore.CYAN}No specific action requested. Available options:{Style.RESET_ALL}")
            print("  --summary          Show collection summary")
            print("  --stats            Show detailed statistics")
            print("  --duplicates       Find duplicate cards")
            print("  --search TERM      Search for cards")
            print("  --sort TYPE        Sort by color/set/rarity/type")
            print("  --enhanced         Enable API features")
            print("  --mana-curve       Analyze mana curve (enhanced)")
            print("  --expensive PRICE  Find expensive cards (enhanced)")
            print(f"\nUse {Fore.YELLOW}python mymanabox.py --help{Style.RESET_ALL} for detailed help.")
            print(f"\n{Fore.CYAN}To update your collection from Moxfield:{Style.RESET_ALL}")
            print(f"  python card_sorter.py --import-url YOUR_MOXFIELD_URL")
            print(f"  python card_sorter.py --import-file YOUR_CSV_FILE")
            print(f"\n{Fore.YELLOW}See IMPORT_INSTRUCTIONS.md for detailed import help.{Style.RESET_ALL}")
            
            if hasattr(sorter, 'display_summary'):
                print(f"\n{Fore.GREEN}Showing collection summary:{Style.RESET_ALL}")
                sorter.display_summary()
                
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return 1
    
    print(f"\n{Fore.GREEN}Done! Thank you for using MyManaBox.{Style.RESET_ALL}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
