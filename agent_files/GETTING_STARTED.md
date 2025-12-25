# Getting Started with MTG Collection Manager

**Your complete system for cataloging 5000+ Magic cards is ready!**

---

## 🎯 What You Have

A comprehensive Python-based collection management system featuring:

✅ **ManaBox Integration** - Import mobile scans via CSV  
✅ **Local MyManaBox Sync** - Direct integration with your existing app at `C:\Users\EHunt\Repos\Projects\MyManaBox`  
✅ **Scryfall API Client** - Automatic card data enrichment  
✅ **Moxfield Export** - Seamless deck building sync  
✅ **Price Tracking** - Scryfall + TCGPlayer support  
✅ **Smart Deduplication** - Merge duplicate scans automatically  
✅ **SQLite Database** - Fast local storage with search  
✅ **Automation Scripts** - Batch processing and workflows  

---

## 🚀 Quick Start (5 Minutes)

### Option A: Using Your Local MyManaBox

**Fastest path - you already have data!**

```bash
cd mtg-collection-manager

# Setup
python setup.py

# Sync from local MyManaBox
python scripts/sync_mymanabox.py --auto-enrich

# Check results
python src/catalogue.py --stats
```

**Done!** Your entire MyManaBox collection is now in the manager.

### Option B: Fresh Start with Mobile ManaBox
```bash
cd mtg-collection-manager
python setup.py
```

This will:
- Check Python version (3.9+ required)
- Install dependencies (requests, python-dotenv)
- Create directory structure
- Initialize database
- Test Scryfall connection

### 2. Test with Sample Data

Scan 10-20 cards in ManaBox to test the workflow:

```bash
# Export from ManaBox as CSV
# Transfer to laptop

# Import to database
python src/catalogue.py --import ~/Downloads/manabox_export.csv

# Enrich with Scryfall data
python scripts/enrich_collection.py --update-prices

# Check results
python src/catalogue.py --stats
```

### 3. Export to Moxfield

```bash
python src/catalogue.py \
  --export exports/moxfield_test.csv \
  --format moxfield

# Upload to Moxfield.com → Collection → Import
```

---

## 📚 Documentation Structure

Your project includes comprehensive documentation:

### Core Documents
- **README.md** - Project overview and features
- **QUICK_REFERENCE.md** - Command cheat sheet
- **PROJECT_GUIDE.md** - Claude Projects setup

### Detailed Guides
- **docs/API_INTEGRATION.md** - Scryfall, TCGPlayer, Card Kingdom setup
- **docs/WORKFLOWS.md** - Step-by-step task walkthroughs

### Source Code
- **src/catalogue.py** - Main collection manager
- **src/api_clients/scryfall.py** - Scryfall API client
- **scripts/consolidate_manabox.py** - Batch CSV merger
- **scripts/enrich_collection.py** - Data enrichment tool

---

## 🎓 Your First Real Session

### Phase 1: Scan First Batch (Tonight - 1 hour)

```bash
1. Sort 100-200 cards by set
2. Open ManaBox → Scan Cards
3. Scan in "Bulk Mode"
4. Export → CSV → Save as "session_1.csv"
5. Transfer to laptop
```

### Phase 2: Import & Enrich (Tomorrow - 30 mins)

```bash
# Import session
python src/catalogue.py --import data/exports/session_1.csv

# Add Scryfall data (runs for ~10-15 mins)
python scripts/enrich_collection.py --update-prices

# Review results
python src/catalogue.py --stats
```

### Phase 3: Sync to Moxfield (5 mins)

```bash
# Export
python src/catalogue.py \
  --export exports/moxfield_session1.csv \
  --format moxfield

# Upload to Moxfield
# Collection → Import → Upload CSV
```

---

## 💡 Key Concepts

### The Workflow Pipeline

```
ManaBox (Phone)
    ↓ CSV Export
Consolidation Script
    ↓ Dedupe & Clean
SQLite Database
    ↓ Enrich via Scryfall
Price Updates
    ↓ Export
Moxfield (Web)
```

### Data Flow

1. **Scan** - ManaBox captures card names, sets, conditions
2. **Consolidate** - Merge multiple CSVs, remove duplicates
3. **Import** - Load into local SQLite database
4. **Enrich** - Add Scryfall data (types, prices, images)
5. **Export** - Generate platform-specific formats
6. **Sync** - Upload to Moxfield, update decks

### File Organization

```
mtg-collection-manager/
├── data/
│   ├── collections/     # Your SQLite databases
│   ├── exports/         # ManaBox CSV files
│   └── cache/           # Scryfall API cache
├── exports/             # Generated export files
├── docs/                # Documentation
├── src/                 # Core application code
└── scripts/             # Automation utilities
```

---

## 🔧 Essential Commands

### Daily Operations
```bash
# Import new scans
python src/catalogue.py --import [file.csv]

# Update prices
python scripts/enrich_collection.py --update-prices

# Check collection
python src/catalogue.py --stats

# Export to Moxfield
python src/catalogue.py --export [file.csv] --format moxfield
```

### Batch Processing
```bash
# Consolidate multiple scans
python scripts/consolidate_manabox.py \
  --input data/exports/sessions \
  --output data/exports/consolidated.csv \
  --dedupe
```

### Troubleshooting
```bash
# Re-initialize database
python src/catalogue.py --init

# Test Scryfall connection
python src/api_clients/scryfall.py

# Check enrichment status
python scripts/enrich_collection.py --stats
```

---

## 📊 Monitoring Progress

### After Each Session

Check your stats to track progress:

```bash
python src/catalogue.py --stats
```

Example output:
```
📊 Collection Statistics:
  Total Cards: 5,247
  Unique Cards: 3,891
  Total Value: $12,438.72

  By Rarity:
    mythic: 847 cards (312 unique)
    rare: 1,923 cards (1,104 unique)
    ...

  Top 10 Sets:
    NEO - Kamigawa: Neon Dynasty: 423 cards
    ...
```

### Track Your Goals

Create a `PROGRESS.md` file:

```markdown
# Collection Progress

## Overall Goals
- [ ] Catalog all 5000+ cards
- [ ] Sync to Moxfield
- [ ] Complete Kaalia deck
- [ ] Reach $15,000 collection value

## Sessions Completed
- [x] Session 1: 187 cards (NEO) - 2025-12-25
- [ ] Session 2: TBD
- [ ] Session 3: TBD

## Current Stats
- Total cards: 187
- Collection value: $342.15
- Top card: Boseiju, Who Endures ($24.99)
```

---

## 🎯 Next Steps

### This Week
1. ✅ Run `python setup.py`
2. ⬜ Scan first 100-200 cards
3. ⬜ Import and enrich
4. ⬜ Verify Moxfield sync works
5. ⬜ Read `docs/WORKFLOWS.md` for detailed guides

### Next Week
1. ⬜ Complete 3 scanning sessions (~500 cards)
2. ⬜ Set up automated price updates
3. ⬜ Create backup routine
4. ⬜ Start deck analysis

### This Month
1. ⬜ Catalog all 5000+ cards
2. ⬜ Optimize deck lists
3. ⬜ Set up Claude Project for ongoing management
4. ⬜ Create custom automation scripts

---

## 🆘 Getting Help

### Documentation
- **Quick commands**: See `QUICK_REFERENCE.md`
- **Detailed workflows**: See `docs/WORKFLOWS.md`
- **API setup**: See `docs/API_INTEGRATION.md`

### Common Issues

**"No module named requests"**
→ Run: `pip install requests python-dotenv`

**"Database locked"**
→ Close other programs accessing the database

**"Card not found in Scryfall"**
→ Check spelling, try different set code

**Import fails with duplicates**
→ Use `--dedupe` flag when consolidating

### Ask Claude

If you're using Claude Projects (recommended):

```
Me: I'm getting an error when importing. Here's the message: [paste error]

Claude: [Diagnoses issue, provides specific fix]
```

---

## 🎉 You're Ready!

You now have a professional-grade MTG collection management system that can:

✅ Handle 5000+ cards efficiently  
✅ Integrate with ManaBox, Scryfall, Moxfield  
✅ Track prices automatically  
✅ Export in multiple formats  
✅ Scale to your entire collection  

**Start with your first scanning session tonight!**

---

## 📞 Quick Reference Card

Keep this handy during scanning sessions:

```
┌─────────────────────────────────────────┐
│  MTG COLLECTION MANAGER - CHEAT SHEET   │
├─────────────────────────────────────────┤
│ IMPORT:                                 │
│ python src/catalogue.py --import FILE   │
│                                         │
│ ENRICH:                                 │
│ python scripts/enrich_collection.py \   │
│   --update-prices                       │
│                                         │
│ STATS:                                  │
│ python src/catalogue.py --stats         │
│                                         │
│ EXPORT TO MOXFIELD:                     │
│ python src/catalogue.py --export FILE \ │
│   --format moxfield                     │
└─────────────────────────────────────────┘
```

---

**Happy collecting! 🃏**

*Last Updated: 2025-12-25*
*Project Version: 1.0.0*
