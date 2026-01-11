#!/usr/bin/env python3
"""
CardForge Collection Export Script
==================================

Export collection to various formats (CSV, Moxfield, Archidekt, JSON).

Usage:
    python export_collection.py [--format FORMAT] [--output FILE]

Examples:
    python export_collection.py --format csv
    python export_collection.py --format moxfield --output my_moxfield.csv
    python export_collection.py --format json --prices
"""

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from src.database.connection import DatabaseManager
from src.services.export_service import CollectionExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="Export MTG collection to various formats",
    )
    
    parser.add_argument(
        "--format",
        choices=["csv", "moxfield", "archidekt", "json"],
        default="csv",
        help="Export format (default: csv)",
    )
    
    parser.add_argument(
        "--output",
        help="Output filename (auto-generated if not specified)",
    )
    
    parser.add_argument(
        "--with-prices",
        action="store_true",
        help="Include price information (CSV and JSON only)",
    )
    
    parser.add_argument(
        "--set-code",
        help="Filter by set code",
    )
    
    parser.add_argument(
        "--rarity",
        help="Filter by rarity (common, uncommon, rare, mythic)",
    )
    
    parser.add_argument(
        "--foil",
        action="store_true",
        help="Only export foil cards",
    )
    
    parser.add_argument(
        "--min-value",
        type=float,
        help="Only export cards worth at least this much",
    )
    
    parser.add_argument(
        "--format-legal",
        help="Only export cards legal in this format (standard, modern, etc.)",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    
    return parser.parse_args()


def main():
    """Main export function."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize database
    db_manager = DatabaseManager()
    
    try:
        exporter = CollectionExporter(db_manager)
        
        # Build filters
        filters = {}
        if args.set_code:
            filters['set_code'] = args.set_code
        if args.rarity:
            filters['rarity'] = args.rarity
        if args.foil:
            filters['is_foil'] = True
        if args.min_value:
            filters['min_value'] = args.min_value
        if args.format_legal:
            filters['format'] = args.format_legal
        
        # Export based on format
        format_type = args.format.lower()
        
        logger.info(f"Exporting collection in {format_type.upper()} format...")
        
        if format_type == "csv":
            output_path = exporter.export_csv(
                filename=args.output,
                include_prices=args.with_prices,
                filters=filters if filters else None,
            )
        
        elif format_type == "moxfield":
            output_path = exporter.export_moxfield(
                filename=args.output,
                filters=filters if filters else None,
            )
        
        elif format_type == "archidekt":
            output_path = exporter.export_archidekt(
                filename=args.output,
                filters=filters if filters else None,
            )
        
        elif format_type == "json":
            output_path = exporter.export_json(
                filename=args.output,
                include_prices=args.with_prices,
                filters=filters if filters else None,
            )
        
        # Print result
        print("\n" + "="*50)
        print("Export Complete")
        print("="*50)
        print(f"Format: {format_type.upper()}")
        print(f"Output: {output_path}")
        print(f"File size: {output_path.stat().st_size:,} bytes")
        print("="*50 + "\n")
        
        logger.info("Export completed successfully!")
        return 0
    
    except Exception as e:
        logger.error(f"Export failed: {e}", exc_info=True)
        return 1
    finally:
        db_manager.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
