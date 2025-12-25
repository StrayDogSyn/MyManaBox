#!/usr/bin/env python3
"""
Export Collection to Multiple Formats

Exports your collection to various deck-building platform formats.

Supported formats:
  - Moxfield
  - Archidekt
  - TappedOut
  - MTG Goldfish
  - Deckbox

Usage:
    python scripts/export_collection.py --format moxfield
    python scripts/export_collection.py --format archidekt --output exports/archidekt.csv
    python scripts/export_collection.py --all
"""

import sys
from pathlib import Path
from datetime import datetime
import argparse
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data import CSVLoader


def export_moxfield(collection, output_path: Path) -> bool:
    """Export in Moxfield format."""
    
    data = []
    for card in collection.cards:
        data.append({
            'Count': card.count,
            'Name': card.name,
            'Edition': card.edition,
            'Condition': card.condition.value,
            'Language': 'English',  # Default
            'Foil': 'foil' if card.foil else '',
            'Tags': '',
            'Last Modified': datetime.now().strftime("%Y-%m-%d"),
            'Collector Number': '',
            'Alter': '',
            'Proxy': '',
            'Purchase Price': card.purchase_price if card.purchase_price else ''
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return True


def export_archidekt(collection, output_path: Path) -> bool:
    """Export in Archidekt format."""
    
    data = []
    for card in collection.cards:
        # Archidekt format: Quantity, Card Name, Set, Foil
        foil_suffix = ' *F*' if card.foil else ''
        data.append({
            'Quantity': card.count,
            'Card Name': card.name + foil_suffix,
            'Set': card.edition,
            'Collector Number': '',
            'Condition': card.condition.value,
            'Price': card.market_value if card.market_value else card.purchase_price
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return True


def export_tappedout(collection, output_path: Path) -> bool:
    """Export in TappedOut format."""
    
    lines = []
    for card in collection.cards:
        # TappedOut format: count Name
        foil_marker = ' *FOIL*' if card.foil else ''
        lines.append(f"{card.count} {card.name}{foil_marker}")
    
    output_path.write_text('\n'.join(lines))
    return True


def export_mtggoldfish(collection, output_path: Path) -> bool:
    """Export in MTG Goldfish format."""
    
    data = []
    for card in collection.cards:
        data.append({
            'Card': card.name,
            'Set Name': card.edition,
            'Quantity': card.count,
            'Foil': 'Yes' if card.foil else 'No',
            'Condition': card.condition.value
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return True


def export_deckbox(collection, output_path: Path) -> bool:
    """Export in Deckbox format."""
    
    data = []
    for card in collection.cards:
        data.append({
            'Count': card.count,
            'Tradelist Count': 0,
            'Name': card.name,
            'Edition': card.edition,
            'Card Number': '',
            'Condition': card.condition.value,
            'Language': 'English',
            'Foil': 'foil' if card.foil else '',
            'Signed': '',
            'Artist Proof': '',
            'Altered Art': '',
            'Misprint': '',
            'Promo': '',
            'Textless': '',
            'My Price': card.purchase_price if card.purchase_price else ''
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    return True


EXPORT_FORMATS = {
    'moxfield': {
        'function': export_moxfield,
        'extension': '.csv',
        'description': 'Moxfield.com collection import format'
    },
    'archidekt': {
        'function': export_archidekt,
        'extension': '.csv',
        'description': 'Archidekt.com collection import format'
    },
    'tappedout': {
        'function': export_tappedout,
        'extension': '.txt',
        'description': 'TappedOut.net simple list format'
    },
    'mtggoldfish': {
        'function': export_mtggoldfish,
        'extension': '.csv',
        'description': 'MTGGoldfish.com collection format'
    },
    'deckbox': {
        'function': export_deckbox,
        'extension': '.csv',
        'description': 'Deckbox.org collection format'
    }
}


def export_collection(csv_file: str, format_name: str, output_path: str = None) -> bool:
    """Export collection in specified format."""
    
    # Load collection
    loader = CSVLoader(csv_file)
    collection = loader.load_collection()
    
    if not collection:
        print(f"Error: Failed to load collection from {csv_file}")
        return False
    
    print(f"Loaded {collection.unique_cards} unique cards ({collection.total_cards} total)")
    
    # Get format config
    if format_name not in EXPORT_FORMATS:
        print(f"Error: Unknown format '{format_name}'")
        print(f"Available formats: {', '.join(EXPORT_FORMATS.keys())}")
        return False
    
    format_config = EXPORT_FORMATS[format_name]
    
    # Determine output path
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d")
        output_path = f"exports/{format_name}_{timestamp}{format_config['extension']}"
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Exporting to {format_name} format...")
    
    # Export
    export_func = format_config['function']
    if export_func(collection, output_path):
        print(f"✓ Exported to {output_path}")
        print(f"  Format: {format_config['description']}")
        return True
    else:
        print(f"✗ Export failed")
        return False


def export_all_formats(csv_file: str, output_dir: str = "exports"):
    """Export collection to all supported formats."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d")
    
    results = {}
    
    for format_name in EXPORT_FORMATS.keys():
        output_file = output_path / f"{format_name}_{timestamp}{EXPORT_FORMATS[format_name]['extension']}"
        print(f"\nExporting {format_name}...")
        results[format_name] = export_collection(csv_file, format_name, str(output_file))
    
    # Summary
    print("\n" + "=" * 60)
    print("Export Summary")
    print("=" * 60)
    
    for format_name, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {format_name}: {EXPORT_FORMATS[format_name]['description']}")
    
    return all(results.values())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export collection to various deck-building platform formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported Formats:
{chr(10).join(f"  {name}: {config['description']}" for name, config in EXPORT_FORMATS.items())}

Examples:
  # Export to Moxfield
  python scripts/export_collection.py --format moxfield
  
  # Export to Archidekt with custom output
  python scripts/export_collection.py --format archidekt --output my_collection.csv
  
  # Export to all formats
  python scripts/export_collection.py --all
  
  # Use different source CSV
  python scripts/export_collection.py --csv data/my_collection.csv --format moxfield

Import Instructions:
  Moxfield:    Collection → Import → Upload CSV
  Archidekt:   Collection → Import → Paste or Upload
  TappedOut:   Collection → Add Cards → Import
  MTGGoldfish: Collection → Import → Choose File
  Deckbox:     Inventory → Tools → Import
        """
    )
    
    parser.add_argument(
        "--csv",
        default="data/enriched_collection_complete.csv",
        help="Source CSV file (default: data/enriched_collection_complete.csv)"
    )
    
    parser.add_argument(
        "--format",
        choices=list(EXPORT_FORMATS.keys()),
        help="Export format"
    )
    
    parser.add_argument(
        "--output",
        help="Output file path (default: exports/<format>_YYYYMMDD.<ext>)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export to all supported formats"
    )
    
    args = parser.parse_args()
    
    if not args.format and not args.all:
        parser.error("Either --format or --all must be specified")
    
    print("=" * 60)
    print("MyManaBox - Collection Export")
    print("=" * 60)
    print()
    
    if args.all:
        success = export_all_formats(args.csv)
    else:
        success = export_collection(args.csv, args.format, args.output)
    
    print()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
