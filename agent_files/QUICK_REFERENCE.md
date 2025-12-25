# MTG Collection Manager - Quick Reference

**Common commands for daily use**

---

## 🚀 Setup & Initialization

```bash
# First-time setup
python setup.py

# Initialize new database
python src/catalogue.py --init --db data/collections/main.db
```

---

## 📥 Importing Data

### ManaBox CSV Import
```bash
# Single file
python src/catalogue.py --import exports/manabox_export.csv

# Consolidate multiple sessions first
python scripts/consolidate_manabox.py \
  --input data/exports/manabox_sessions \
  --output data/exports/consolidated.csv \
  --dedupe

# Then import consolidated
python src/catalogue.py --import data/exports/consolidated.csv
```

---

## 🔍 Searching & Statistics

```bash
# View collection stats
python src/catalogue.py --stats

# Search for specific cards
python src/catalogue.py --search "Lightning Bolt"

# Get detailed statistics
python src/catalogue.py --stats --db data/collections/main.db
```

---

## 💰 Price Updates

```bash
# Update all prices (Scryfall)
python scripts/enrich_collection.py --update-prices

# Update specific cards
python scripts/enrich_collection.py \
  --cards "Force of Will,Mox Diamond" \
  --update-prices

# Full enrichment with fresh prices
python scripts/enrich_collection.py \
  --update-prices \
  --cache 0h
```

---

## 📤 Exporting Data

### To Moxfield
```bash
python src/catalogue.py \
  --export exports/moxfield_import.csv \
  --format moxfield
```

### Standard CSV
```bash
python src/catalogue.py \
  --export exports/collection_backup.csv \
  --format standard
```

---

## 🧪 Testing & Validation

```bash
# Test Scryfall connection
python src/api_clients/scryfall.py

# Check database integrity
sqlite3 data/collections/main.db "PRAGMA integrity_check"

# Show enrichment status
python scripts/enrich_collection.py --stats
```

---

## 🔧 Maintenance

```bash
# Backup database
cp data/collections/main.db \
   data/collections/backup_$(date +%Y%m%d).db

# Clear cache
rm -rf data/cache/*

# Rebuild database from CSV
python src/catalogue.py --init --db data/collections/new.db
python src/catalogue.py --import exports/backup.csv --db data/collections/new.db
```

---

## 📊 Advanced Queries

### SQLite Direct Access
```bash
# Open database
sqlite3 data/collections/main.db

# Common queries:
SELECT COUNT(*), SUM(quantity) FROM cards;
SELECT name, market_price FROM cards ORDER BY market_price DESC LIMIT 10;
SELECT set_code, COUNT(*) FROM cards GROUP BY set_code;
```

---

## 🎯 Workflow Shortcuts

### Daily Routine
```bash
# 1. Import today's scans
python src/catalogue.py --import ~/Downloads/manabox_*.csv

# 2. Enrich new cards
python scripts/enrich_collection.py --update-prices

# 3. Check stats
python src/catalogue.py --stats
```

### Weekly Update
```bash
# 1. Update all prices
python scripts/enrich_collection.py --update-prices --cache 0h

# 2. Export to Moxfield
python src/catalogue.py --export exports/moxfield_$(date +%Y%m%d).csv --format moxfield

# 3. Backup database
cp data/collections/main.db ~/Dropbox/mtg-backup/
```

---

## 🆘 Quick Troubleshooting

### Import fails with "duplicate key"
```bash
# Add --dedupe flag when consolidating
python scripts/consolidate_manabox.py --dedupe
```

### Scryfall rate limit hit
```bash
# Enable caching and use longer cache duration
python scripts/enrich_collection.py --cache 48h
```

### Database locked
```bash
# Close all connections, then:
sqlite3 data/collections/main.db "PRAGMA optimize"
```

### Missing prices
```bash
# Re-run enrichment with force refresh
python scripts/enrich_collection.py --update-prices --cache 0h
```

---

## 📝 Custom Aliases (Add to ~/.bashrc)

```bash
# MTG Collection shortcuts
alias mtg-import='python ~/mtg-collection-manager/src/catalogue.py --import'
alias mtg-stats='python ~/mtg-collection-manager/src/catalogue.py --stats'
alias mtg-enrich='python ~/mtg-collection-manager/scripts/enrich_collection.py'
alias mtg-export='python ~/mtg-collection-manager/src/catalogue.py --export'
alias mtg-backup='cp ~/mtg-collection-manager/data/collections/main.db ~/Dropbox/mtg-backup/$(date +%Y%m%d).db'
```

---

## 🎓 Help Commands

```bash
# Main catalogue help
python src/catalogue.py --help

# Enrichment script help
python scripts/enrich_collection.py --help

# Consolidation script help
python scripts/consolidate_manabox.py --help
```

---

**Pro Tip:** Bookmark this file for quick reference during scanning sessions!

*Last Updated: 2025-12-25*
