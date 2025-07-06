# MyManaBox Scripts

This directory contains essential scripts for MyManaBox collection management.

## Core Scripts

### `average_pricing.py`

Comprehensive average pricing analysis service that provides:

- Card-level averages for duplicate cards
- Set-level pricing statistics  
- Rarity-based price analysis
- Foil vs non-foil comparison
- Price tier distribution analysis
- JSON export for detailed reporting

**Usage**: Called automatically from GUI "Average Pricing Analysis" menu option

### `enrich_collection.py`

Enriches collection data with Scryfall API information:

- Fetches missing card details
- Updates pricing information
- Adds comprehensive card metadata
- Handles rate limiting and API errors

**Usage**: `python scripts/enrich_collection.py [csv_file]`

### `price_analysis.py`

Analyzes pricing gaps and coverage in the collection:

- Identifies cards with missing prices
- Reports pricing coverage statistics
- Suggests improvements for data quality

**Usage**: `python scripts/price_analysis.py`

### `comprehensive_price_update.py`

Complete price update system with advanced features:

- Updates missing USD and foil prices
- Applies premium multipliers for accurate market pricing
- Handles purchase price optimization
- Creates backups and detailed reports

**Usage**: Called from GUI "Enhanced Price Update" menu option

### `advanced_price_enhancement.py`

Advanced pricing logic with TCGPlayer-style multipliers:

- Aggressive premium pricing for competitive accuracy
- Special handling for foils, rarities, and high-value cards
- Market-accurate pricing adjustments
- Value optimization for collection accuracy

**Usage**: `python scripts/advanced_price_enhancement.py`

## Usage Notes

- Most scripts are integrated into the GUI for easy access
- All scripts create backups before making changes
- Run scripts from the MyManaBox root directory
- Check `data/` directory for output files and backups

## Requirements

All scripts require the main MyManaBox dependencies:

- pandas
- requests
- python-dateutil

See `requirements.txt` in the root directory for complete dependencies.
