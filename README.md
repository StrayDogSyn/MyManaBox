# MyManaBox
Python program for organizing my MTG cards

## Features
- Import and analyze MTG card collections from Moxfield CSV exports
- Sort cards by color, type, rarity, and set
- Find duplicate cards and expensive cards
- Mana curve analysis with API integration
- Export sorted collections to CSV files

## Quick Start

### Basic Usage
```bash
# Show collection summary
python mymanabox.py --summary

# Search for specific cards
python mymanabox.py --search "Lightning Bolt"

# Find duplicate cards
python mymanabox.py --duplicates

# Sort by color and export
python mymanabox.py --sort color
```

### Enhanced Features (with API)
```bash
# Use enhanced mode with Scryfall API
python mymanabox.py --enhanced --summary

# Analyze mana curve
python mymanabox.py --enhanced --mana-curve

# Find expensive cards ($20+)
python mymanabox.py --enhanced --expensive 20

# Enhanced sorting with accurate type data
python mymanabox.py --enhanced --sort type
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your Moxfield export CSV in the project directory as `moxfield_export.csv`

3. Run the program:
```bash
python mymanabox.py --help
```

## Files
- `mymanabox.py` - Main CLI interface
- `card_sorter.py` - Basic card sorting functionality
- `enhanced_sorter.py` - Enhanced features with API integration
- `scryfall_api.py` - Scryfall API integration for card data
- `requirements.txt` - Python dependencies

## API Features
When using `--enhanced` mode, the program connects to the Scryfall API to get accurate card data including:
- Precise color identity
- Exact card types and subtypes
- Real rarity information
- Current market prices
- Mana cost information

Note: API calls are cached locally to improve performance and reduce API usage.
