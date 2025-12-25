# 🎯 Integration Overview - Your Complete MTG System

**You now have three integrated tools working together:**

---

## 🔗 The Three-Tool Ecosystem

### 1️⃣ Mobile ManaBox App (Phone)
**Purpose:** Quick scanning on the go  
**Use for:** New card acquisitions, trades, event pickups  
**Export:** CSV files

### 2️⃣ Local MyManaBox (`C:\Users\EHunt\Repos\Projects\MyManaBox`)
**Purpose:** Desktop management with GUI  
**Use for:** Detailed editing, browsing collection  
**Data:** `card_cache.json`, SQLite database

### 3️⃣ Collection Manager (This Project)
**Purpose:** Advanced features, integrations, automation  
**Use for:** Pricing, exports, deck analysis, Moxfield sync  
**Data:** SQLite database with full enrichment

---

## 🌊 Data Flow Options

### Option A: Mobile → Local → Collection Manager
```
📱 Scan in mobile ManaBox
    ↓ Sync to cloud
💻 Import to local MyManaBox
    ↓ python scripts/sync_mymanabox.py
📊 Collection Manager (enriched)
    ↓ python src/catalogue.py --export
🌐 Moxfield / Other platforms
```

**Best for:** Casual collecting, prefer GUI

### Option B: Mobile → Collection Manager Direct
```
📱 Scan in mobile ManaBox
    ↓ Export CSV
📊 Collection Manager
    ↓ python src/catalogue.py --import
    ↓ python scripts/enrich_collection.py
🌐 Moxfield / Other platforms
```

**Best for:** Power users, maximum automation

### Option C: Local MyManaBox Only
```
💻 Use local MyManaBox for everything
    ↓ python scripts/sync_mymanabox.py --auto-enrich
📊 Collection Manager (for analysis/exports only)
    ↓ python src/catalogue.py --export
🌐 Moxfield / Other platforms
```

**Best for:** Already established MyManaBox workflow

---

## 🎯 Recommended Workflow for YOU

Based on your setup, I recommend **Option A** with automation:

### Initial Setup (One-Time)

```bash
# 1. Sync existing MyManaBox data
cd C:\Users\EHunt\Repos\Projects\mtg-collection-manager
python scripts/sync_mymanabox.py --auto-enrich

# 2. Set up daily automation
python scripts/sync_mymanabox.py --setup-automation daily

# 3. Test Moxfield export
python src/catalogue.py --export exports/moxfield_initial.csv --format moxfield
```

### Daily Operation

**Add new cards:**
1. Scan in mobile ManaBox app
2. Sync mobile → local MyManaBox (automatic)
3. Automated daily sync updates collection manager
4. Weekly export to Moxfield

**Manual when needed:**
```bash
# Force immediate sync
python scripts/sync_mymanabox.py --auto-enrich

# Export to Moxfield
python src/catalogue.py --export exports/moxfield.csv --format moxfield
```

---

## 📊 Feature Matrix

| Feature | Mobile ManaBox | Local MyManaBox | Collection Manager |
|---------|----------------|-----------------|-------------------|
| Quick scanning | ✅ Best | ❌ | ❌ |
| GUI browsing | ✅ Good | ✅ Best | ❌ |
| Deck building | ⚠️ Basic | ⚠️ Basic | ✅ Best (via Moxfield export) |
| Price tracking | ⚠️ Limited | ⚠️ Limited | ✅ Best (Scryfall/TCG) |
| Exports | ⚠️ CSV only | ⚠️ CSV only | ✅ Multi-format |
| Automation | ❌ | ❌ | ✅ Best |
| Platform sync | ⚠️ ManaBox cloud | ❌ | ✅ Moxfield, etc. |
| Offline use | ✅ | ✅ | ✅ |
| Search/filter | ✅ Good | ✅ Good | ✅ Best (SQL) |

---

## 🚀 Quick Start for Each Tool

### Using Mobile ManaBox

```
1. Install ManaBox app on phone
2. Create account / sign in
3. Scan → Cards → Bulk mode
4. Export → CSV → Email to yourself
5. Download CSV → Save to mtg-collection-manager/data/exports/
```

### Using Local MyManaBox

```
1. Open MyManaBox GUI
2. Add/edit cards as normal
3. Save changes
4. Collection manager will sync automatically (daily)
```

### Using Collection Manager

```bash
# Import from mobile ManaBox CSV
python src/catalogue.py --import data/exports/mobile_export.csv

# Sync from local MyManaBox
python scripts/sync_mymanabox.py --auto-enrich

# View stats
python src/catalogue.py --stats

# Export to Moxfield
python src/catalogue.py --export exports/moxfield.csv --format moxfield
```

---

## 🔄 Sync Commands Reference

### Manual Syncs

```bash
# Local MyManaBox → Collection Manager
python scripts/sync_mymanabox.py --auto-enrich

# Mobile ManaBox CSV → Collection Manager
python src/catalogue.py --import ~/Downloads/manabox_export.csv
python scripts/enrich_collection.py --update-prices

# Collection Manager → Moxfield
python src/catalogue.py --export exports/moxfield.csv --format moxfield
```

### Automated Syncs

```bash
# Set up daily auto-sync from local MyManaBox
python scripts/sync_mymanabox.py --setup-automation daily

# Verify automation
schtasks /Query /TN MTG-ManaBox-Sync  # Windows
```

---

## 📁 File Organization

```
Your MTG Files:
├── Mobile ManaBox (Phone)
│   └── Cloud sync to ManaBox servers
│
├── Local MyManaBox (C:\Users\EHunt\Repos\Projects\MyManaBox\)
│   ├── card_cache.json       ← Your collection data
│   ├── collection.db          ← SQLite database
│   └── gui.py                 ← Application
│
└── Collection Manager (C:\Users\EHunt\Repos\Projects\mtg-collection-manager\)
    ├── data/
    │   ├── collections/
    │   │   └── main.db        ← Enriched collection
    │   ├── exports/           ← Mobile CSV imports
    │   └── backups/
    │       └── manabox/       ← Auto-backups
    ├── exports/
    │   └── moxfield_*.csv     ← Platform exports
    └── scripts/
        └── sync_mymanabox.py  ← Auto-sync script
```

---

## 🎯 Decision Tree: Which Tool When?

### Adding New Cards
- **Just bought 10 cards at store?** → Mobile ManaBox (quick scan)
- **Received 100+ card lot?** → Local MyManaBox (batch entry)
- **Importing from list?** → Collection Manager (CSV import)

### Checking Card Value
- **Quick price check?** → Mobile ManaBox (basic pricing)
- **Detailed market analysis?** → Collection Manager (Scryfall/TCG)
- **Historical prices?** → Collection Manager (price tracking)

### Building Decks
- **Casual testing?** → Local MyManaBox (GUI)
- **Competitive optimization?** → Collection Manager → Moxfield
- **Check what you own?** → All three work!

### Trading/Selling
- **Create trade binder?** → Collection Manager (filtered exports)
- **Check buylist prices?** → Collection Manager (Card Kingdom integration)
- **Show at LGS?** → Mobile ManaBox (portable)

---

## 🆘 Troubleshooting Integration

### "Cards showing up twice"

**Cause:** Same cards in mobile export AND local MyManaBox

**Solution:** The sync script dedupes automatically. Check quantities:
```bash
python src/catalogue.py --search "Lightning Bolt"
```

### "Prices don't match between tools"

**Cause:** Different price sources, update frequencies

**Reality:**
- Mobile ManaBox: TCGPlayer (cached)
- Local MyManaBox: TCGPlayer (cached)
- Collection Manager: Scryfall (live) or TCGPlayer (API)

**Solution:** Use collection manager as source of truth for pricing

### "Automated sync not working"

**Check:**
1. Task scheduled correctly: `schtasks /Query /TN MTG-ManaBox-Sync`
2. Python path is correct in task
3. Check logs: `type logs\sync.log`

**Fix:**
```bash
# Re-run setup
python scripts/sync_mymanabox.py --setup-automation daily
```

---

## 💡 Pro Tips

### 1. Use Each Tool for Its Strengths
- **Mobile** = Scanning
- **Local** = Browsing/editing
- **Collection Manager** = Analysis/exports

### 2. Let Automation Handle Syncing
Don't manually sync unless needed. Daily automation keeps everything current.

### 3. Collection Manager is Your Source of Truth
For pricing, deck analysis, exports → always use collection manager's data.

### 4. Backup Before Bulk Changes
```bash
python src/integrations/mymanabox.py --action backup
cp data/collections/main.db data/collections/backup_$(date +%Y%m%d).db
```

### 5. Use Dry Runs
Before any major import/sync:
```bash
python scripts/sync_mymanabox.py --dry-run
```

---

## 📞 Quick Command Reference

```bash
# SYNC COMMANDS
python scripts/sync_mymanabox.py                          # Basic sync
python scripts/sync_mymanabox.py --auto-enrich           # Sync + Scryfall
python scripts/sync_mymanabox.py --dry-run               # Preview only

# IMPORT COMMANDS
python src/catalogue.py --import mobile_export.csv       # From mobile
python src/integrations/mymanabox.py --action export     # Export MyManaBox

# EXPORT COMMANDS
python src/catalogue.py --export file.csv --format moxfield  # To Moxfield
python src/catalogue.py --stats                             # View collection

# AUTOMATION
python scripts/sync_mymanabox.py --setup-automation daily
```

---

## 🎉 Your Complete Ecosystem

You now have:

✅ **Mobile scanning** for quick card capture  
✅ **Desktop management** via local MyManaBox GUI  
✅ **Advanced analysis** in collection manager  
✅ **Automated syncing** between all systems  
✅ **Platform exports** to Moxfield and beyond  
✅ **Price tracking** from multiple sources  
✅ **Deck optimization** capabilities  

**Everything works together seamlessly!**

---

*See `docs/MYMANABOX_INTEGRATION.md` for detailed MyManaBox-specific setup.*  
*See `docs/WORKFLOWS.md` for step-by-step task guides.*  
*See `QUICK_REFERENCE.md` for command cheat sheet.*

*Last Updated: 2025-12-25*
