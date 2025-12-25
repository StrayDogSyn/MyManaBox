# MyManaBox Quick Start Guide

## 🎯 Your System Overview

You have a **fully functional** MTG collection manager with:
- ✅ 1,834 unique cards (2,228 total)
- ✅ $444.03 in purchase value tracked
- ✅ Scryfall API integration for market prices
- ✅ CSV import/export functionality
- ✅ Search, filter, and analytics tools
- ✅ Console interface with color support

## 🚀 Basic Commands

### Run the Application (Interactive Mode)
```bash
python main.py --summary
```

### Available Features

#### Collection Summary
```bash
# Quick summary
python main.py --summary

# Detailed statistics  
python main.py --stats

# Advanced analytics
python main.py --analytics
```

#### Sorting & Organization
```bash
# Sort by color and export to separate files
python main.py --sort color --sort-output sorted_output/

# Other sort options
python main.py --sort set       # By set/edition
python main.py --sort rarity    # By rarity
python main.py --sort value     # By price
python main.py --sort type      # By card type
python main.py --sort name      # Alphabetically
python main.py --sort count     # By quantity owned
```

#### Search & Filter
```bash
# Search by name
python main.py --search "Lightning Bolt"

# Search by card text
python main.py --search-text "flying"

# Find duplicates
python main.py --duplicates

# Filter by color
python main.py --filter-color blue black

# Filter by rarity
python main.py --filter-rarity rare mythic

# Filter by price range
python main.py --min-price 5.00 --max-price 20.00

# Show foils only
python main.py --foils-only
```

#### Import & Export
```bash
# Import from Moxfield URL
python main.py --import-url "https://www.moxfield.com/decks/..."

# Import from local CSV file
python main.py --import-file path/to/file.csv

# Validate import file format
python main.py --validate-file path/to/file.csv

# Export enriched collection with Scryfall data
python main.py --export-enriched enriched_collection.csv
```

#### Backup Management
```bash
# List available backups
python main.py --list-backups

# Restore from backup
python main.py --restore-backup backups/backup_20250705.csv
```

#### API & Enrichment
```bash
# Enrich collection with current market prices
python main.py --enrich

# Run without API calls (offline mode)
python main.py --no-api
```

#### Output Options
```bash
# Change output format
python main.py --summary --output-format json
python main.py --summary --output-format csv

# Limit results displayed
python main.py --search "Dragon" --limit 10
```

## 📂 Important Files & Locations

### Your Collection Data
- **Main CSV**: `data/moxfield_export.csv` (original import)
- **Enriched CSV**: `data/enriched_collection_complete.csv` (with Scryfall data)
- **Backups**: `data/backups/` (automated backups)

### Cache
- **Card Cache**: `card_cache.json` (Scryfall API responses cached here)

### Configuration
- **Requirements**: `requirements.txt` - Python dependencies
- **Project Config**: `pyproject.toml` - Python project settings

## 🔄 Typical Workflows

### Workflow 1: Update Prices
```bash
# Enrich with current market data
python main.py --enrich

# Export updated collection
python main.py --export-enriched data/enriched_collection_complete.csv
```

### Workflow 2: Find Valuable Cards
```bash
# Find cards worth $10+
python main.py --min-price 10.00 --limit 50

# Export high-value cards
python main.py --min-price 10.00 --export-enriched data/high_value_cards.csv
```

### Workflow 3: Organize by Set
```bash
# Sort and export by set
python main.py --sort set --sort-output sorted_by_set/

# This creates separate CSV files for each set
# sorted_by_set/sorted_foundations.csv
# sorted_by_set/sorted_bloomburrow.csv
# etc.
```

### Workflow 4: Import New Cards
```bash
# From mobile ManaBox export
python main.py --import-file ~/Downloads/manabox_export.csv

# Backup is created automatically
# New cards are merged with existing collection
```

## 🛠️ Advanced Features

### Search Combinations
```bash
# Blue/Black rares worth $5+
python main.py --filter-color blue black --filter-rarity rare --min-price 5.00

# Foil creatures only
python main.py --filter-type creature --foils-only
```

### Custom CSV File
```bash
# Use a different CSV file
python main.py --csv path/to/other_collection.csv --summary
```

## 📊 Your Collection at a Glance

Current stats (as of last run):
- **1,834** unique cards
- **2,228** total cards (including duplicates)
- **$444.03** total purchase value
- **229** duplicate cards
- **7** color groups

## 🎯 What Your System Can Do

✅ **Currently Working:**
- Load/save CSV collections
- Search and filter cards
- Sort and organize by multiple criteria
- Enrich with Scryfall market data
- Track prices and collection value
- Import from Moxfield
- Export enriched data
- Backup/restore collections
- Find duplicates
- Analytics and insights

❓ **What agent_files Offers (May Not Need):**
The `agent_files/` folder contains scripts for a different project architecture. Your current system already has:
- CSV import ✅ (you have this)
- Export functionality ✅ (you have this)  
- Scryfall integration ✅ (you have this)
- Collection management ✅ (you have this)

## 🤔 Questions to Consider

1. **Do you scan cards with mobile ManaBox app?**
   - If yes: Export CSV from mobile → Import with `--import-file`
   - If no: Continue using your current workflow

2. **Do you need automation?**
   - Daily price updates?
   - Automatic backups?
   - Scheduled enrichment?
   
3. **What's your primary use case?**
   - Tracking collection value?
   - Building decks?
   - Trading/selling?
   - Just cataloging?

## 🚦 Next Steps

**Option A: Use What You Have (Recommended)**
Your system works great! Keep using it as-is.

**Option B: Add Mobile Integration**
If you use mobile ManaBox:
```bash
# Export from mobile ManaBox as CSV
# Transfer to computer
python main.py --import-file ~/Downloads/manabox_export.csv
```

**Option C: Add Automation**
Create scheduled tasks for:
- Daily price enrichment
- Automated backups  
- Collection reports

**Option D: Clean Up agent_files**
The agent_files folder can probably be archived or removed since your main application already has the functionality.

## 📚 Need Help?

Check out the existing documentation:
- **docs/USAGE.md** - Detailed usage guide
- **docs/PROJECT_STRUCTURE.md** - Code organization
- **docs/IMPORT_INSTRUCTIONS.md** - Import workflows
- **README.md** - Project overview

## 🎁 Pro Tips

1. **Always backup before imports**: Automatic, but you can disable with `--no-backup`
2. **Cache is your friend**: Scryfall responses are cached in `card_cache.json`
3. **Use filters**: Combine multiple filters for powerful searches
4. **Export enriched data**: Use `--export-enriched` to get full Scryfall data
5. **Check backups**: Run `--list-backups` periodically to manage storage

---

**Your MyManaBox is ready to use! 🎉**

Start with: `python main.py --summary`
