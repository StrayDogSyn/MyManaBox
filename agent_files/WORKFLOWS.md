# MTG Collection Manager - Workflows

**Step-by-step guides for common tasks**

---

## 🎯 Quick Navigation

- [First-Time Setup](#first-time-setup)
- [Scanning & Cataloging 5000+ Cards](#scanning--cataloging-5000-cards)
- [Syncing ManaBox → Moxfield](#syncing-manabox--moxfield)
- [Updating Card Prices](#updating-card-prices)
- [Building & Optimizing Decks](#building--optimizing-decks)
- [Exporting for Trading](#exporting-for-trading)

---

## First-Time Setup

### Prerequisites Checklist

- [x] Python 3.9+ installed
- [x] ManaBox mobile app installed
- [x] Moxfield account created
- [x] Phone scanner stand (optional but recommended)

### Step 1: Install Dependencies

```bash
cd mtg-collection-manager

# Install required packages
pip install requests pandas python-dotenv

# Verify installation
python src/catalogue.py --help
```

### Step 2: Initialize Database

```bash
# Create fresh database
python src/catalogue.py --init

# Verify database created
ls data/collections/main.db
```

### Step 3: Test Scryfall Integration

```bash
# Run Scryfall test
python src/api_clients/scryfall.py
```

Expected output:
```
Testing card lookup...
✅ Lightning Bolt (Limited Edition Alpha)
   Price: $599.99
   Scryfall ID: abc123...

Testing search...
✅ Found 147 red 3-drop creatures
```

### Step 4: (Optional) Configure TCGPlayer

If you want real-time pricing from TCGPlayer:

1. Sign up at [TCGPlayer Developer Portal](https://developer.tcgplayer.com/)
2. Create `config/api_keys.env`:
   ```
   TCGPLAYER_PUBLIC_KEY=your_public_key_here
   TCGPLAYER_PRIVATE_KEY=your_private_key_here
   ```

---

## Scanning & Cataloging 5000+ Cards

### The Efficient Approach

**Timeline:** 4-6 evenings of work

**Session Breakdown:**
- Sessions 1-3: Bulk scanning (3 x 2-hour sessions)
- Session 4: Data consolidation & cleanup (2 hours)
- Session 5: Import & verification (1 hour)

---

### Session 1-3: Mobile Scanning (6 hours total)

#### Prep Work (15 mins)

1. **Sort cards by set** (speeds up ManaBox recognition)
2. **Set up scanning station:**
   - Bright, even lighting (fluorescent white > warm yellow)
   - Dark matte surface (reduces glare)
   - Phone stand at 6-8" height
3. **Create backup system:**
   ```bash
   mkdir data/exports/manabox_sessions
   ```

#### Scanning Process (2 hours per session)

**Target:** 100-200 cards per hour

```
For each batch of 100 cards:
1. Open ManaBox → Scan Cards
2. Scan in "Bulk Mode" (faster, less verification)
3. Quick review:
   - Check obvious misreads (glare, angle issues)
   - Mark value cards for manual verification later
4. Save session progress
5. Export to CSV:
   ManaBox → Collection → Export → CSV
6. Name file: manabox_session_X_YYYY-MM-DD.csv
7. Transfer to laptop (email/cloud/USB)
```

**Pro Tips:**
- Batch same set together (faster recognition)
- Skip foils initially (harder to scan, do separately)
- Take 5-min break every 30 minutes (scanning fatigue is real)

#### After Each Session

```bash
# Backup exports
cp ~/Downloads/manabox_session_1_*.csv \
   data/exports/manabox_sessions/

# Quick stats check
wc -l data/exports/manabox_sessions/manabox_session_1_*.csv
```

---

### Session 4: Data Consolidation (2 hours)

#### Combine All Exports

```bash
# Navigate to project
cd mtg-collection-manager

# Run consolidation script
python scripts/consolidate_manabox.py \
  --input data/exports/manabox_sessions \
  --output data/exports/consolidated_collection.csv \
  --dedupe
```

#### Manual Cleanup (The Important Part!)

Open `consolidated_collection.csv` in Excel/Sheets and:

1. **Check for duplicates:**
   - Sort by Card Name
   - Look for same card scanned multiple times
   - Merge quantities: combine into single row

2. **Verify high-value cards:**
   - Filter: `Market Price > $10`
   - Check set codes are correct
   - Verify condition ratings

3. **Fix common errors:**
   - Set symbol confusion (same name, different printing)
   - Foil detection misses
   - Foreign language cards marked as English

4. **Save cleaned version:**
   ```
   data/exports/consolidated_collection_CLEAN.csv
   ```

---

### Session 5: Import & Enrich (1 hour)

#### Import to Local Database

```bash
# Import cleaned CSV
python src/catalogue.py \
  --import data/exports/consolidated_collection_CLEAN.csv

# Verify import
python src/catalogue.py --stats
```

Expected output:
```
📊 Collection Statistics:
  Total Cards: 5,247
  Unique Cards: 3,891
  Total Value: $12,438.72
```

#### Enrich with Scryfall Data

```bash
# Run enrichment script
python scripts/enrich_collection.py \
  --source data/collections/main.db \
  --update-prices \
  --cache 24h
```

This adds:
- Card types and Oracle text
- Current market prices
- Card images URLs
- Mana costs and color identity

**Progress:** ~20-30 cards/minute (rate-limited)
**Duration:** ~3-4 hours for 5000 cards (run overnight)

---

## Syncing ManaBox → Moxfield

### Quick Sync (Post-Scanning)

```bash
# Convert ManaBox export to Moxfield format
python src/exporters/csv_exporter.py \
  --collection data/collections/main.db \
  --format moxfield \
  --output exports/moxfield_import.csv
```

### Import to Moxfield

1. Go to **Moxfield.com** → **Collection**
2. Click **Import** button (top right)
3. Select **CSV** format
4. Upload `moxfield_import.csv`
5. Review import summary:
   - Check for errors (red warnings)
   - Verify card counts match
6. Click **Confirm Import**

### Verify Sync

In Moxfield:
- Check total card count matches your database
- Spot-check 10-20 random cards
- Verify foils and conditions imported correctly

---

## Updating Card Prices

### Manual Update (On-Demand)

```bash
# Update all card prices from Scryfall
python src/catalogue.py --update-prices --source scryfall

# Update specific cards
python scripts/update_prices.py \
  --cards "Lightning Bolt,Force of Will,Mox Diamond" \
  --source tcgplayer
```

### Automated Updates (Recommended)

**Schedule weekly price updates:**

Create `scripts/weekly_price_update.sh`:
```bash
#!/bin/bash
cd /path/to/mtg-collection-manager

python src/catalogue.py \
  --update-prices \
  --source scryfall \
  --cache 24h \
  --log logs/price_update_$(date +%Y%m%d).log

echo "Price update complete: $(date)" | \
  mail -s "MTG Collection Price Update" your@email.com
```

**Set up cron job:**
```bash
# Run every Sunday at 2 AM
0 2 * * 0 /path/to/scripts/weekly_price_update.sh
```

### Price Alerts

Get notified when cards spike:

```bash
# Set up price alerts
python scripts/price_alerts.py \
  --threshold 50% \  # Alert on 50%+ price change
  --min-value 10 \   # Only track cards > $10
  --email your@email.com
```

---

## Building & Optimizing Decks

### Import Deck from Moxfield

1. **Export from Moxfield:**
   - Open your deck
   - Click **Export** → **Text**
   - Save as `decks/my_deck.txt`

2. **Import to local database:**
   ```bash
   python src/catalogue.py \
     --import-deck decks/my_deck.txt \
     --name "Kaalia Voltron"
   ```

### Check Missing Cards

```bash
# Find which cards you need
python scripts/check_missing.py \
  --deck decks/kaalia.txt \
  --collection data/collections/main.db \
  --output exports/kaalia_shopping_list.csv
```

Output example:
```
Missing Cards (32 total):
  1x Sword of Feast and Famine ($45.00)
  1x Teferi's Protection ($38.00)
  1x Mana Crypt ($120.00)
  ...
Total cost: $847.50
```

### Find Budget Alternatives

```bash
# Suggest cheaper replacements
python scripts/budget_alternatives.py \
  --deck decks/kaalia.txt \
  --max-price 10 \
  --function-match
```

### Optimize Mana Base

```bash
# Analyze mana curve and suggest fixes
python scripts/mana_analysis.py \
  --deck decks/kaalia.txt \
  --format commander \
  --color-weight RWB
```

---

## Exporting for Trading

### Generate Trade Binder

Export high-value cards for trading:

```bash
# Create trade list
python scripts/create_trade_binder.py \
  --min-value 5 \
  --exclude-decks \  # Don't include cards currently in decks
  --output exports/trade_binder_$(date +%Y%m%d).csv
```

### Card Kingdom Buylist Report

Check what you can sell:

```bash
# Generate buylist report
python scripts/buylist_report.py \
  --source cardkingdom \
  --min-cash 1 \
  --output exports/buylist_$(date +%Y%m%d).csv
```

Output includes:
- Card names
- Your quantity
- CK cash price
- CK credit price (typically +30%)
- Total cash / credit values

### TCGPlayer Sell List

```bash
# Export for TCGPlayer seller portal
python scripts/tcg_sell_export.py \
  --condition NM \  # Only Near Mint
  --min-price 3 \   # Minimum $3 market price
  --output exports/tcg_sell_list.csv
```

---

## Advanced Workflows

### Complete Deck Analysis

```bash
# Run full deck report
python scripts/deck_report.py \
  --deck decks/kaalia.txt \
  --check-owned \
  --price-analysis \
  --mana-curve \
  --suggest-cuts \
  --output reports/kaalia_analysis.md
```

### Collection Health Check

```bash
# Identify issues in collection
python scripts/health_check.py \
  --duplicates \     # Find duplicate entries
  --missing-prices \ # Cards without pricing
  --orphaned-cards \ # Cards not in any deck
  --output reports/collection_health_$(date +%Y%m%d).md
```

### Backup Everything

```bash
# Complete backup
python scripts/backup.py \
  --database data/collections/main.db \
  --exports data/exports \
  --destination ~/Dropbox/MTG-Backups/$(date +%Y%m%d)
```

---

## Troubleshooting Common Issues

### ManaBox won't recognize card

**Solutions:**
1. Better lighting (most common issue)
2. Clean card surface (fingerprints = glare)
3. Try different angle
4. Manual entry (faster than fighting scanner)

### Scryfall rate limit hit

**Error:** `429 Too Many Requests`

**Solutions:**
1. Enable caching: `cache_enabled=True`
2. Use bulk data downloads for large imports
3. Add delays between requests

### Moxfield import fails

**Common causes:**
- Extra columns in CSV
- Missing required fields
- Encoding issues (use UTF-8)

**Fix:**
```bash
# Re-export with strict Moxfield format
python src/exporters/csv_exporter.py \
  --format moxfield \
  --validate \
  --output exports/moxfield_import_FIXED.csv
```

### Database corruption

**Symptoms:**
- Queries fail
- Stats don't match reality
- Import errors

**Recovery:**
```bash
# Backup current (corrupt) database
cp data/collections/main.db data/collections/main_CORRUPT_backup.db

# Export to CSV
sqlite3 data/collections/main.db ".mode csv" ".output /tmp/export.csv" "SELECT * FROM cards"

# Rebuild fresh database
rm data/collections/main.db
python src/catalogue.py --init
python src/catalogue.py --import /tmp/export.csv
```

---

## Tips for Maximum Efficiency

### Scanning
- Sort by set BEFORE scanning (3x faster recognition)
- Scan during good lighting (natural daylight or fluorescent)
- Use bulk mode, review later
- Skip problem cards, manual entry later

### Data Management
- Weekly backups to cloud
- Monthly price updates
- Quarterly collection health checks

### Deck Building
- Import first, THEN scan for missing cards
- Use budget alternatives for testing
- Proxy expensive cards before buying

---

## Next Steps

After completing initial cataloging:

1. **Set up automation:**
   - Weekly price updates
   - Daily backups
   - Monthly collection reports

2. **Optimize workflows:**
   - Create custom scripts for your needs
   - Build deck templates
   - Set up price alert thresholds

3. **Expand integration:**
   - Connect to more platforms
   - Build web dashboard
   - Mobile app for quick lookups

---

**Questions?** Check `docs/API_INTEGRATION.md` for technical details.
