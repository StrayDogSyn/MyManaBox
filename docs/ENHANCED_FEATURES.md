# Enhanced Features Guide

## 🎉 New Enhancements Added!

Your MyManaBox now includes powerful automation and export features while maintaining its clean architecture.

---

## 🚀 New Scripts Added

### 1. Automated Enrichment (`scripts/auto_enrich.py`)

**Purpose:** Automatically update your collection with current Scryfall prices and data.

**Usage:**
```bash
# Basic enrichment
python scripts/auto_enrich.py

# With backup (recommended)
python scripts/auto_enrich.py --backup

# Quiet mode (for scheduled tasks)
python scripts/auto_enrich.py --backup --quiet

# Different CSV file
python scripts/auto_enrich.py --csv data/my_collection.csv
```

**Features:**
- ✅ Updates market prices from Scryfall
- ✅ Enriches card data (types, colors, rarity)
- ✅ Optional automatic backup
- ✅ Progress tracking
- ✅ Quiet mode for automation

**Perfect for:** Daily scheduled tasks to keep prices current

---

### 2. Mobile ManaBox Import (`scripts/import_mobile.py`)

**Purpose:** Import cards from mobile ManaBox app exports with smart format detection.

**Usage:**
```bash
# Import and replace collection
python scripts/import_mobile.py ~/Downloads/manabox_export.csv

# Merge with existing collection
python scripts/import_mobile.py mobile_scan.csv --merge --backup

# Import to specific file
python scripts/import_mobile.py new_cards.csv --target data/collection.csv
```

**Features:**
- ✅ Automatic format detection
- ✅ Normalizes mobile ManaBox CSV structure
- ✅ Smart merging (updates quantities)
- ✅ Filters out tradelist/wishlist items
- ✅ Automatic backups

**Workflow:**
1. Export from mobile ManaBox app
2. Transfer CSV to computer
3. Run import script
4. Run enrichment to add Scryfall data

---

### 3. Multi-Format Export (`scripts/export_collection.py`)

**Purpose:** Export your collection to various deck-building platforms.

**Supported Formats:**
- **Moxfield** - Moxfield.com collection import
- **Archidekt** - Archidekt.com collection format
- **TappedOut** - TappedOut.net simple list
- **MTG Goldfish** - MTGGoldfish.com format
- **Deckbox** - Deckbox.org inventory format

**Usage:**
```bash
# Export to Moxfield
python scripts/export_collection.py --format moxfield

# Export to Archidekt with custom output
python scripts/export_collection.py --format archidekt --output my_archidekt.csv

# Export to ALL formats at once
python scripts/export_collection.py --all

# Use different source
python scripts/export_collection.py --csv data/other_collection.csv --format moxfield
```

**Import Instructions:**
- **Moxfield:** Collection → Import → Upload CSV
- **Archidekt:** Collection → Import → Paste or Upload
- **TappedOut:** Collection → Add Cards → Import
- **MTGGoldfish:** Collection → Import → Choose File
- **Deckbox:** Inventory → Tools → Import

---

### 4. Automation Setup (`scripts/setup_automation.py`)

**Purpose:** Generate Windows Task Scheduler commands for automated tasks.

**Usage:**
```bash
# Show automation setup commands
python scripts/setup_automation.py

# See commands only (no prompts)
python scripts/setup_automation.py --show-only
```

**What It Does:**
- Generates PowerShell commands for Task Scheduler
- Provides manual setup instructions
- Shows verification commands
- Suggests additional automation ideas

**Recommended Schedule:**
- **Daily at 9:00 AM:** Auto-enrichment
- **Weekly on Sunday:** Price updates
- **Monthly on 1st:** Backup archive
- **Friday 5:00 PM:** Pre-FNM export

---

### 5. Setup Verification (`scripts/verify_setup.py`)

**Purpose:** Check that everything is properly configured.

**Usage:**
```bash
# Basic verification
python scripts/verify_setup.py

# Detailed information
python scripts/verify_setup.py --detailed
```

**Checks:**
- ✅ Python version (3.9+ required)
- ✅ Virtual environment active
- ✅ Dependencies installed
- ✅ Project structure intact
- ✅ Collection files present
- ✅ Core modules importable
- ✅ Enhancement scripts available

**When to Use:**
- After initial setup
- After updating dependencies
- Troubleshooting issues
- Before teaching/demo sessions

---

## 🔄 Complete Workflows

### Workflow 1: Daily Automation
**Set it and forget it!**

```bash
# 1. Setup automation
python scripts/setup_automation.py

# 2. Copy PowerShell command (shown in output)
# 3. Run in PowerShell as Administrator

# Your collection now updates daily automatically! ✨
```

---

### Workflow 2: Mobile Scanning Session
**Scan cards, sync, and export**

```bash
# 1. Scan cards in mobile ManaBox app
# 2. Export as CSV from mobile

# 3. Import to desktop
python scripts/import_mobile.py ~/Downloads/manabox_export.csv --merge --backup

# 4. Enrich with Scryfall data
python scripts/auto_enrich.py --backup

# 5. Export to Moxfield
python scripts/export_collection.py --format moxfield

# 6. Import to Moxfield.com
```

---

### Workflow 3: Weekly Maintenance
**Keep your collection current**

```bash
# Every Sunday morning:

# 1. Update prices
python scripts/auto_enrich.py --backup

# 2. Export to all platforms
python scripts/export_collection.py --all

# 3. Check summary
python main.py --summary
```

---

### Workflow 4: Event Preparation
**Before FNM or tournaments**

```bash
# 1. Export latest collection
python scripts/export_collection.py --format moxfield

# 2. Find valuable cards for trades
python main.py --min-price 10.00 --limit 50

# 3. Check for duplicates to trade
python main.py --duplicates
```

---

## 🎯 Integration with Existing Features

### Your Original Commands Still Work!
All your existing `main.py` commands work exactly as before:

```bash
python main.py --summary
python main.py --search "Lightning Bolt"
python main.py --sort color
python main.py --filter-rarity rare mythic
python main.py --analytics
```

### Enhanced Workflow
Now you can combine old and new features:

```bash
# Find valuable cards
python main.py --min-price 20.00 > valuable_cards.txt

# Update prices
python scripts/auto_enrich.py --backup

# Export for trade list
python scripts/export_collection.py --format moxfield
```

---

## 📊 Quick Reference

### Daily Tasks
```bash
python scripts/auto_enrich.py --backup --quiet
```

### Weekly Tasks
```bash
python scripts/auto_enrich.py --backup
python scripts/export_collection.py --all
```

### Mobile Import
```bash
python scripts/import_mobile.py ~/Downloads/manabox_export.csv --merge
```

### Export for Platform
```bash
python scripts/export_collection.py --format <platform>
# platforms: moxfield, archidekt, tappedout, mtggoldfish, deckbox
```

### Verify Setup
```bash
python scripts/verify_setup.py
```

### Setup Automation
```bash
python scripts/setup_automation.py
```

---

## 🛠️ Troubleshooting

### Import Issues
```bash
# Verify CSV format
python scripts/verify_setup.py --detailed

# Check if file is mobile ManaBox format
# The script auto-detects, but you can verify column headers
```

### Export Not Working
```bash
# Ensure collection is loaded
python main.py --summary

# Try different format
python scripts/export_collection.py --format moxfield --output test.csv
```

### Automation Not Running
```bash
# Verify task is created
Get-ScheduledTask | Where-Object {$_.TaskName -like 'MyManaBox*'}

# Test task manually
Start-ScheduledTask -TaskName 'MyManaBox-Daily-Enrichment'

# Check task history in Task Scheduler GUI
```

### Dependencies Missing
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Verify
python scripts/verify_setup.py
```

---

## 🎓 Teaching Applications

### For Code The Dream Students

**API Integration Example:**
```python
# Show how auto_enrich.py uses Scryfall API
# Located in: src/data/scryfall_client.py

# Demonstrates:
# - RESTful API calls
# - JSON parsing
# - Rate limiting
# - Caching strategies
# - Error handling
```

**CSV Processing:**
```python
# Show how import_mobile.py normalizes data
# Located in: scripts/import_mobile.py

# Demonstrates:
# - File I/O
# - Pandas DataFrame operations
# - Data transformation
# - Format detection
```

**Task Automation:**
```python
# Show how setup_automation.py generates PowerShell
# Located in: scripts/setup_automation.py

# Demonstrates:
# - Cross-platform scripting
# - Template generation
# - System integration
```

---

## 📚 Related Documentation

- **[QUICK_START.md](../QUICK_START.md)** - Original features guide
- **[START_HERE.md](../START_HERE.md)** - Getting started
- **[COMPLETE_SUMMARY.md](../COMPLETE_SUMMARY.md)** - Full system overview
- **[docs/USAGE.md](../docs/USAGE.md)** - Detailed usage

---

## 🎁 Summary of Enhancements

### What You Had
✅ CSV import/export
✅ Search and filter
✅ Manual enrichment
✅ Console interface

### What You Have Now
✅ **Automated enrichment** - Schedule daily updates
✅ **Mobile import** - Smart ManaBox CSV handling
✅ **Multi-platform export** - 5 deck-building sites
✅ **Windows automation** - Task Scheduler integration
✅ **Setup verification** - Health checks

### Your System is Now
- **More automated** - Less manual work
- **More flexible** - Export to any platform
- **More robust** - Verification and health checks
- **More professional** - Enterprise-grade workflows
- **Still clean** - Same architecture, more features

---

**Your enhanced MyManaBox is ready! 🎉**

Try it now:
```bash
python scripts/verify_setup.py
python scripts/auto_enrich.py --backup
python scripts/export_collection.py --format moxfield
```
