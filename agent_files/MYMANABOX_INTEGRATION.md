# MyManaBox Local Integration Guide

**Connecting your local MyManaBox application with mtg-collection-manager**

---

## 🎯 Your Setup

You have **two MTG tools** that can work together:

1. **MyManaBox** (`C:\Users\EHunt\Repos\Projects\MyManaBox`)
   - Your existing application
   - 143 MB of data
   - Contains `card_cache.json` and GUI

2. **mtg-collection-manager** (this project)
   - New comprehensive system
   - Database-driven
   - Platform integrations

**Goal:** Sync data between both systems seamlessly.

---

## 🚀 Quick Start Integration

### Step 1: Test the Connection

```bash
# Navigate to mtg-collection-manager
cd mtg-collection-manager

# Test MyManaBox connection
python src/integrations/mymanabox.py \
  --path "C:/Users/EHunt/Repos/Projects/MyManaBox" \
  --action list
```

Expected output:
```
📂 Connected to MyManaBox: C:\Users\EHunt\Repos\Projects\MyManaBox
   ✓ Found database: collection.db
✅ Loaded 5247 cards from database

📊 Found 5247 cards

First 5 cards:
   1. Lightning Bolt (LEA)
   2. Black Lotus (LEA)
   ...
```

### Step 2: Dry Run Sync

See what would be synced **without** actually syncing:

```bash
python scripts/sync_mymanabox.py --dry-run
```

### Step 3: First Real Sync

```bash
# Full sync with auto-enrichment
python scripts/sync_mymanabox.py --auto-enrich
```

This will:
1. Backup your MyManaBox data
2. Import all cards to collection manager
3. Enrich with Scryfall data
4. Update prices

**Duration:** ~15-20 minutes for 5000 cards

---

## 🔄 Workflow Options

### Option A: MyManaBox as Primary (Recommended)

**Use case:** You prefer MyManaBox GUI for adding/editing cards

**Workflow:**
```
1. Edit cards in MyManaBox GUI
2. Save changes in MyManaBox
3. Run sync to update collection manager:
   python scripts/sync_mymanabox.py --auto-enrich
4. Export to Moxfield:
   python src/catalogue.py --export exports/moxfield.csv --format moxfield
```

**Automation:** Set up daily sync
```bash
python scripts/sync_mymanabox.py --setup-automation daily
```

### Option B: Collection Manager as Primary

**Use case:** You want advanced features (pricing, exports, deck analysis)

**Workflow:**
```
1. Import initial data from MyManaBox:
   python scripts/sync_mymanabox.py --auto-enrich
2. Use collection manager for all updates:
   python src/catalogue.py --import new_cards.csv
3. Optionally export back to MyManaBox
   (requires custom script - see below)
```

### Option C: Parallel Use

**Use case:** Best of both worlds

**Workflow:**
```
1. Scan new cards in mobile ManaBox app
2. Export from mobile → import to local MyManaBox
3. Sync local MyManaBox → collection manager
4. Use collection manager for deck building
5. Use MyManaBox for casual browsing
```

**Sync schedule:** Daily or weekly

---

## 🛠️ Integration Commands

### Manual Sync

```bash
# Basic sync
python scripts/sync_mymanabox.py

# Sync with Scryfall enrichment
python scripts/sync_mymanabox.py --auto-enrich

# Dry run (preview only)
python scripts/sync_mymanabox.py --dry-run

# Custom MyManaBox path
python scripts/sync_mymanabox.py \
  --path "D:/Different/Path/MyManaBox" \
  --auto-enrich
```

### Export from MyManaBox

```bash
# Export MyManaBox to CSV for manual review
python src/integrations/mymanabox.py \
  --path "C:/Users/EHunt/Repos/Projects/MyManaBox" \
  --action export \
  --output exports/manabox_export.csv
```

### Backup MyManaBox Data

```bash
# Create backup before major changes
python src/integrations/mymanabox.py \
  --path "C:/Users/EHunt/Repos/Projects/MyManaBox" \
  --action backup
```

Backups saved to: `data/backups/manabox/`

---

## 🤖 Automated Sync Setup

### Windows (Task Scheduler)

**Daily sync at 9 AM:**
```bash
python scripts/sync_mymanabox.py --setup-automation daily
```

This generates a command like:
```cmd
schtasks /CREATE /TN "MTG-ManaBox-Sync" /SC DAILY /ST 09:00 ^
  /TR "python C:\Users\EHunt\Repos\Projects\mtg-collection-manager\scripts\sync_mymanabox.py --auto-enrich" /F
```

**Run in Command Prompt as Administrator**

**Verify it's running:**
```cmd
schtasks /Query /TN MTG-ManaBox-Sync
```

### Alternative: Manual Batch Script

Create `sync_daily.bat` in mtg-collection-manager:

```batch
@echo off
cd C:\Users\EHunt\Repos\Projects\mtg-collection-manager
python scripts/sync_mymanabox.py --auto-enrich >> logs\sync.log 2>&1
echo Sync completed at %date% %time% >> logs\sync.log
```

Double-click to run manually, or add to Windows Task Scheduler.

---

## 📊 Understanding the Data Flow

### MyManaBox → Collection Manager

```
MyManaBox Files:
├── card_cache.json          ← Card data (JSON format)
├── collection.db            ← Collection database (SQLite)
└── gui.py                   ← Application code

       ↓ sync_mymanabox.py

Collection Manager:
├── data/collections/main.db ← Imported & enriched data
├── exports/                 ← Generated exports
└── Moxfield ready CSVs
```

### Field Mapping

MyManaBox uses different field names. The integration automatically maps:

| MyManaBox Field | Collection Manager | Notes |
|-----------------|-------------------|-------|
| `card_name` | `name` | Card name |
| `set` / `edition` | `set_code` | 3-letter code |
| `qty` / `count` | `quantity` | Number owned |
| `is_foil` | `foil` | Boolean |
| `collector_number` | `collector_number` | Card # in set |

---

## 🔍 Troubleshooting

### "MyManaBox installation not found"

**Solution:** Provide explicit path
```bash
python scripts/sync_mymanabox.py \
  --path "C:/Users/EHunt/Repos/Projects/MyManaBox"
```

### "No cards found in MyManaBox"

**Check:**
1. Is `card_cache.json` present?
2. Is it a valid JSON file?
3. Does it contain card data?

**Debug:**
```bash
python src/integrations/mymanabox.py \
  --path "C:/Users/EHunt/Repos/Projects/MyManaBox" \
  --action list
```

### Duplicate cards after sync

**Cause:** Card exists in both MyManaBox and collection manager

**Solution:** Use `--dry-run` first to preview, or the sync script automatically dedupes by:
- Card name
- Set code
- Collector number
- Foil status

### Sync is slow

**Cause:** Auto-enrichment queries Scryfall for every card

**Solutions:**
1. Disable auto-enrich, run separately later:
   ```bash
   python scripts/sync_mymanabox.py  # Fast sync only
   python scripts/enrich_collection.py --update-prices  # Later
   ```

2. Use caching (already enabled by default)

3. Only enrich new cards:
   ```bash
   python scripts/enrich_collection.py --cache 168h  # 1 week cache
   ```

---

## 🎯 Best Practices

### Daily Workflow

**Morning:** (Automated)
- Sync runs at 9 AM
- Updates collection manager with MyManaBox changes
- Enriches new cards

**Evening:** (Manual)
- Add new cards in MyManaBox GUI
- Save changes
- Sync will capture tomorrow morning

### Weekly Workflow

**Sunday:**
1. Review collection stats
2. Update all card prices
3. Export to Moxfield
4. Backup both systems

```bash
# Sunday maintenance script
python scripts/sync_mymanabox.py --auto-enrich
python scripts/enrich_collection.py --update-prices --cache 0h
python src/catalogue.py --export exports/moxfield_$(date +%Y%m%d).csv --format moxfield
python src/integrations/mymanabox.py --action backup
```

### Before Major Changes

**Always backup first:**
```bash
# Backup MyManaBox
python src/integrations/mymanabox.py --action backup

# Backup collection manager
cp data/collections/main.db data/collections/backup_$(date +%Y%m%d).db
```

---

## 🚀 Advanced: Bidirectional Sync

Currently, sync is **one-way**: MyManaBox → Collection Manager

To go **both ways** (Collection Manager → MyManaBox), create custom script:

```python
# scripts/sync_to_mymanabox.py (future enhancement)

from src.catalogue import Collection
from src.integrations.mymanabox import MyManaBoxWriter  # To be created

collection = Collection()
writer = MyManaBoxWriter("C:/Users/EHunt/Repos/Projects/MyManaBox")

# Export new cards to MyManaBox
new_cards = collection.search_cards(filters={"added_since": "2025-12-26"})
writer.add_cards(new_cards)
```

**Note:** This requires understanding MyManaBox's internal structure. Contact me if you need this feature.

---

## 📚 Integration Summary

### What Works Now

✅ Read MyManaBox data (JSON + SQLite)  
✅ Sync to collection manager  
✅ Automatic deduplication  
✅ Backup MyManaBox data  
✅ Auto-enrichment with Scryfall  
✅ Export to Moxfield from collection manager  

### Coming Soon

⬜ Bidirectional sync (Collection Manager → MyManaBox)  
⬜ Real-time sync (file watchers)  
⬜ Conflict resolution (different quantities)  
⬜ Selective sync (only certain sets/decks)  

---

## 🆘 Quick Reference

```bash
# Test connection
python src/integrations/mymanabox.py --action list

# Dry run sync
python scripts/sync_mymanabox.py --dry-run

# Full sync
python scripts/sync_mymanabox.py --auto-enrich

# Setup automation
python scripts/sync_mymanabox.py --setup-automation daily

# Manual backup
python src/integrations/mymanabox.py --action backup

# Export for review
python src/integrations/mymanabox.py --action export --output test.csv
```

---

**You now have seamless integration between your local MyManaBox app and the collection manager!**

*Last Updated: 2025-12-25*
