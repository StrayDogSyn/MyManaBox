# CardForge Collection Migration Guide

This document describes the CSV import/export workflow for CardForge.

## Quick Start

### Import Collection from CSV

```bash
# Auto-detect format and import
python scripts/import_collection.py data/imports/ManaBox_Collection_Bulk.csv

# Specify format explicitly
python scripts/import_collection.py data/imports/manabox.csv --format manabox

# Replace existing collection
python scripts/import_collection.py data/imports/manabox.csv --replace

# Skip backup
python scripts/import_collection.py data/imports/manabox.csv --no-backup

# View collection status
python scripts/import_collection.py --status
```

### Export Collection

```bash
# Export to CSV (default)
python scripts/export_collection.py

# Export to Moxfield format
python scripts/export_collection.py --format moxfield

# Export with prices
python scripts/export_collection.py --with-prices

# Export only foil cards
python scripts/export_collection.py --foil

# Export to JSON with prices
python scripts/export_collection.py --format json --with-prices
```

## Supported CSV Formats

### 1. ManaBox Format (Recommended)

Used by ManaBox mobile app. Supports flexible column names.

**Example:**

```csv
Name,Card Name,Set Code,Set,Quantity,Foil?,Condition,Language,Location,Notes
Aetherflux Reservoir,Aetherflux Reservoir,KLD,Kaladesh,1,No,NM,English,Binder,Test card
```

**Columns:**

- Name or Card Name: Card name (required)
- Set Code or Set: Magic set code (required)
- Quantity: Number of copies (default: 1)
- Foil?: Is foil version? (Yes/No)
- Condition: Card condition (NM, LP, MP, HP, Damaged)
- Language: Card language
- Location: Where card is stored
- Notes: Custom notes

### 2. Standard Format

Minimal format for bulk imports.

**Example:**

```csv
Name,Set,Quantity,Foil
Aetherflux Reservoir,KLD,1,No
```

### 3. Archidekt Format

Used by Archidekt deck builder.

**Example:**

```csv
Quantity,Card Name,Set Code,Foil
1,Aetherflux Reservoir,KLD,0
```

### 4. Moxfield Format

Used by Moxfield deck building tool.

**Example:**

```csv
Count,Name,Edition,Foil?,Language
1,Aetherflux Reservoir,KLD,nonfoil,en
```

## Import Process

### Step 1: Prepare CSV File

- Place CSV file in `data/imports/` directory
- Ensure it follows one of the supported formats

### Step 2: Run Import

```bash
python scripts/import_collection.py data/imports/your_file.csv
```

### Step 3: Backup Created

The import script automatically creates a backup:

- Location: `data/backups/pre_import_YYYYMMDD_HHMMSS/`
- Contains database snapshot before import

### Step 4: Scryfall Enrichment

The import process automatically enriches cards with Scryfall data:

- Pricing (USD, foil, EUR, TIX)
- Card metadata (colors, type, oracle text)
- Legality information
- Images
- Time: ~10-15 minutes for 3,830 cards

### Step 5: Database Insertion

Cards are inserted into the database with:

- Duplicate detection by name+set code
- Quantity accumulation for multiples
- Replace mode option (clear existing collection)

### Step 6: Statistics

Final statistics shown:

- CSV import stats (cards imported, errors)
- Enrichment stats (found, not found, errors)
- Database insertion stats (inserted, updated, skipped)
- Collection summary (totals, value, foil count)

## Export Process

### Export to CSV

```bash
python scripts/export_collection.py --format csv --with-prices
```

Output: `data/exports/collection_YYYYMMDD_HHMMSS.csv`

**Columns:**

- Name, Set Code, Quantity, Foil, Condition, Language, Location, Notes
- Price USD, Foil Price USD, Total Value (if --with-prices)

### Export to Moxfield

```bash
python scripts/export_collection.py --format moxfield
```

Output: `data/exports/moxfield_export_YYYYMMDD_HHMMSS.csv`

Compatible with Moxfield import.

### Export to Archidekt

```bash
python scripts/export_collection.py --format archidekt
```

Output: `data/exports/archidekt_export_YYYYMMDD_HHMMSS.csv`

Compatible with Archidekt import.

### Export to JSON

```bash
python scripts/export_collection.py --format json --with-prices
```

Output: `data/exports/collection_YYYYMMDD_HHMMSS.json`

Includes full metadata as JSON structure.

## Filtering

### By Set Code

```bash
python scripts/export_collection.py --set-code KLD
```

### By Rarity

```bash
python scripts/export_collection.py --rarity mythic
```

### By Foil Status

```bash
python scripts/export_collection.py --foil
```

### By Minimum Value

```bash
python scripts/export_collection.py --min-value 10.00
```

### By Format Legality

```bash
python scripts/export_collection.py --format-legal modern
```

## Backup and Recovery

### View Backups

```bash
python scripts/import_collection.py --list-backups
```

### Restore Backup

```bash
python scripts/import_collection.py --restore data/backups/pre_import_20240101_120000
```

## Error Handling

### Common Issues

**CSV file not found:**

- Ensure file exists in correct location
- Check file path is correct

**Scryfall lookup failures:**

- Some cards may not be found (e.g., older/custom cards)
- Check logs for specific failures
- Can manually update prices later

**Database errors:**

- Check database file is not locked
- Ensure adequate disk space
- Restore from backup if needed

### Troubleshooting

Enable verbose logging:

```bash
python scripts/import_collection.py data/imports/file.csv --verbose
```

Check backup directory:

```bash
ls -la data/backups/
```

Restore if needed:

```bash
python scripts/import_collection.py --restore /path/to/backup
```

## Performance

### Import Timing

- CSV parsing: < 1 second
- Scryfall enrichment: 10-15 minutes for 3,830 cards
- Database insertion: 1-2 minutes
- Total: ~15-20 minutes

### Rate Limiting

- Scryfall API: 10 requests/second
- Database commits: Every 100 cards
- Backoff on rate limits: Automatic

## Advanced Usage

### Replace Existing Collection

Clears existing collection before import:

```bash
python scripts/import_collection.py data/imports/file.csv --replace
```

**Warning:** This removes all existing collection data before importing.

### Skip Backup

Proceed without creating backup (not recommended):

```bash
python scripts/import_collection.py data/imports/file.csv --no-backup
```

### Auto-Detect Format

Script automatically detects CSV format:

```bash
python scripts/import_collection.py data/imports/file.csv
```

Supports: ManaBox, Archidekt, Moxfield, Standard

## API Usage

### Import Collection Programmatically

```python
import asyncio
from src.services.migration_service import MigrationManager
from src.database.connection import DatabaseManager

async def main():
    db_manager = DatabaseManager()
    migration = MigrationManager(db_manager)
    
    result = await migration.import_csv_file(
        "data/imports/file.csv",
        format="manabox",
        create_backup=True,
        replace_mode=False,
    )
    
    print(f"Imported: {result['insert_stats']['inserted']} cards")

asyncio.run(main())
```

### Export Collection Programmatically

```python
from src.services.export_service import CollectionExporter
from src.database.connection import DatabaseManager

db_manager = DatabaseManager()
exporter = CollectionExporter(db_manager)

# Export to CSV with prices
path = exporter.export_csv(include_prices=True)
print(f"Exported to: {path}")

# Export to Moxfield
path = exporter.export_moxfield()
```

### Get Collection Status

```python
from src.services.migration_service import MigrationManager
from src.database.connection import DatabaseManager

db_manager = DatabaseManager()
migration = MigrationManager(db_manager)

status = migration.get_import_status()
print(f"Total items: {status['collection_items']}")
print(f"Total value: ${status['total_value']}")
```

## Testing

Run integration tests:

```bash
pytest tests/integration/test_import_workflow.py -v
```

Test specific functionality:

```bash
# Test CSV import
pytest tests/integration/test_import_workflow.py::TestCSVImporter -v

# Test migration manager
pytest tests/integration/test_import_workflow.py::TestMigrationManager -v

# Test end-to-end workflow
pytest tests/integration/test_import_workflow.py::TestEndToEndWorkflow -v
```

## Data Directory Structure

```text
data/
├── imports/              # CSV files for import
│   ├── ManaBox_Collection_Bulk.csv
│   └── archidekt_export.csv
├── exports/              # Export results
│   ├── collection_20240115_120000.csv
│   ├── moxfield_export_20240115_120030.csv
│   └── collection_20240115_120045.json
└── backups/              # Database backups
    ├── pre_import_20240115_115900/
    │   └── cardforge.db
    └── pre_import_20240115_120050/
        └── cardforge.db
```

## Next Steps

1. Prepare your CSV file (ManaBox format recommended)
2. Run import: `python scripts/import_collection.py data/imports/file.csv`
3. Review import statistics
4. Export to other formats as needed: `python scripts/export_collection.py`
5. Check backups: `ls -la data/backups/`

For questions or issues, check the logs in the backup directory.
