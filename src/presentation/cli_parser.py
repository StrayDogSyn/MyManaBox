"""CLI argument parser."""

import argparse
from typing import Any, Optional


class CLIParser:
    """Handles command line argument parsing."""
    
    def __init__(self):
        """Initialize the CLI parser."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="MyManaBox - MTG Card Collection Manager",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s --summary                    Show collection summary
  %(prog)s --sort color                 Sort collection by color
  %(prog)s --search "Dragon"            Search for cards containing "Dragon"
  %(prog)s --import-url "URL"           Import from Moxfield URL
  %(prog)s --import-file "file.csv"     Import from local CSV file
            """
        )
        
        # File options
        parser.add_argument("--csv", default="moxfield_export.csv", 
                          help="Path to CSV file (default: moxfield_export.csv)")
        
        # Display options
        parser.add_argument("--summary", action="store_true", 
                          help="Show collection summary")
        parser.add_argument("--stats", action="store_true", 
                          help="Show detailed collection statistics")
        parser.add_argument("--analytics", action="store_true",
                          help="Show advanced analytics and insights")
        
        # Sorting options
        parser.add_argument("--sort", choices=["color", "set", "rarity", "type", "value", "name", "count"], 
                          help="Sort and export collection by category")
        parser.add_argument("--sort-output", default="sorted_output",
                          help="Output directory for sorted collections (default: sorted_output)")
        
        # Search options
        parser.add_argument("--search", help="Search for cards by name")
        parser.add_argument("--search-text", help="Search for cards by oracle text")
        parser.add_argument("--duplicates", action="store_true", 
                          help="Find duplicate cards")
        
        # Filter options
        parser.add_argument("--filter-color", nargs="+", 
                          help="Filter by color (white, blue, black, red, green, colorless)")
        parser.add_argument("--filter-rarity", nargs="+",
                          help="Filter by rarity (common, uncommon, rare, mythic)")
        parser.add_argument("--filter-type", nargs="+",
                          help="Filter by type (creature, instant, sorcery, etc.)")
        parser.add_argument("--filter-set", nargs="+",
                          help="Filter by set code")
        parser.add_argument("--min-price", type=float,
                          help="Minimum card price filter")
        parser.add_argument("--max-price", type=float,
                          help="Maximum card price filter")
        parser.add_argument("--foils-only", action="store_true",
                          help="Show only foil cards")
        
        # Import options
        parser.add_argument("--import-url", 
                          help="Import collection from URL (Moxfield supported)")
        parser.add_argument("--import-file", 
                          help="Import collection from a local CSV file")
        parser.add_argument("--no-backup", action="store_true", 
                          help="Skip backup when importing")
        parser.add_argument("--validate-file",
                          help="Validate import file format")
        
        # Backup management
        parser.add_argument("--list-backups", action="store_true",
                          help="List available backup files")
        parser.add_argument("--restore-backup",
                          help="Restore from backup file")
        
        # API options
        parser.add_argument("--enrich", action="store_true",
                          help="Enrich collection with Scryfall API data")
        parser.add_argument("--no-api", action="store_true",
                          help="Disable API features")
        
        # Output options
        parser.add_argument("--output-format", choices=["table", "csv", "json"],
                          default="table", help="Output format (default: table)")
        parser.add_argument("--limit", type=int, default=20,
                          help="Limit number of results displayed (default: 20)")
        
        return parser
    
    def parse_args(self, args: Optional[list] = None) -> Any:
        """Parse command line arguments."""
        return self.parser.parse_args(args)
    
    def print_help(self):
        """Print help message."""
        self.parser.print_help()
