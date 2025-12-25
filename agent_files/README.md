# MTG Collection Manager

**A comprehensive Python-based system for cataloging, managing, and optimizing Magic: The Gathering collections with multi-platform integration.**

---

## 🎯 Project Overview

This project provides tools to:
- **Catalog 5000+ cards** efficiently using mobile scanning + desktop management
- **Sync across platforms**: ManaBox ↔ CSV ↔ Moxfield
- **Integrate pricing data**: Scryfall, TCGPlayer, Card Kingdom
- **Build/optimize decks** with data-driven insights
- **Export/Import** in multiple formats for cross-platform compatibility

---

## 🏗️ Project Structure

```
mtg-collection-manager/
├── README.md                 # This file
├── docs/
│   ├── API_INTEGRATION.md    # Scryfall, TCG, Card Kingdom guides
│   ├── WORKFLOWS.md          # Step-by-step processes
│   └── TROUBLESHOOTING.md    # Common issues & solutions
├── src/
│   ├── catalogue.py          # Main collection manager
│   ├── api_clients/          # API integration modules
│   │   ├── scryfall.py
│   │   ├── tcgplayer.py
│   │   └── cardkingdom.py
│   ├── importers/            # Data import utilities
│   │   ├── manabox.py
│   │   └── moxfield.py
│   └── exporters/            # Data export utilities
│       └── csv_exporter.py
├── config/
│   ├── api_keys.template     # Template for API credentials
│   └── settings.json         # Application settings
├── data/
│   ├── collections/          # Your card databases
│   ├── decks/               # Deck lists
│   └── cache/               # API response cache
├── exports/                  # Generated CSV/JSON exports
└── scripts/                  # Automation helpers
    ├── sync_manabox.sh
    └── bulk_price_update.py
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- ManaBox mobile app (for scanning)
- Moxfield account (for deck building)

### Installation

1. **Clone or download this project**
2. **Install dependencies:**
   ```bash
   pip install requests pandas python-dotenv
   ```

3. **Configure API keys** (optional for pricing):
   ```bash
   cp config/api_keys.template config/api_keys.env
   # Edit api_keys.env with your credentials
   ```

4. **Run initial setup:**
   ```bash
   python src/catalogue.py --init
   ```

---

## 🔗 Special Feature: Local MyManaBox Integration

**Got the local MyManaBox app already?** This project integrates seamlessly!

Your local MyManaBox installation at:
```
C:\Users\EHunt\Repos\Projects\MyManaBox
```

Can sync directly to this collection manager:

```bash
# One-command sync
python scripts/sync_mymanabox.py --auto-enrich

# Set up daily automation
python scripts/sync_mymanabox.py --setup-automation daily
```

**See [`docs/MYMANABOX_INTEGRATION.md`](docs/MYMANABOX_INTEGRATION.md) and [`INTEGRATION_OVERVIEW.md`](INTEGRATION_OVERVIEW.md) for complete integration guide.**

---

## 📱 Scanning Workflow (5000+ Cards)

### Phase 1: Mobile Scanning (2-3 evenings)

1. **Batch cards by set** for faster scanning
2. **Scan in ManaBox** (mobile or local app): 100-200 cards per session
3. **Quick review** for obvious errors
4. **Mark value cards** vs. bulk

### Phase 2: Export & Consolidate (1 evening)

1. **ManaBox → Export → CSV**
2. **Transfer to laptop** (email/cloud/USB)
3. **Run consolidation script:**
   ```bash
   python scripts/consolidate_exports.py
   ```

### Phase 3: Import to Platforms (30 mins)

1. **Moxfield**: Collection → Import → Upload CSV
2. **Local Database**: 
   ```bash
   python src/catalogue.py --import exports/consolidated.csv
   ```

---

## 🔗 Platform Integration

### Supported Services

| Platform | Purpose | Integration Method |
|----------|---------|-------------------|
| **Scryfall** | Card data, images, rules | API (free, no key required) |
| **TCGPlayer** | Market prices, buy links | API (requires key) |
| **Card Kingdom** | Buylist prices | Web scraping |
| **Moxfield** | Deck building, inventory | CSV import/export |
| **ManaBox** | Mobile scanning | CSV export |

See `docs/API_INTEGRATION.md` for detailed setup.

---

## 💡 Key Features

### 1. Smart Cataloging
- **Bulk imports** from ManaBox CSV
- **Duplicate detection** and merging
- **Set/condition tracking**
- **Automatic pricing updates**

### 2. Deck Optimization
- **Compare deck lists** against collection
- **Missing card identification**
- **Budget alternatives** suggestion
- **Mana curve analysis**

### 3. Price Tracking
- **Historical price data** from multiple sources
- **Value alerts** for significant changes
- **Trade value calculator**

### 4. Export Flexibility
- **CSV** (universal compatibility)
- **JSON** (programmatic access)
- **Moxfield format** (direct import)
- **Printable inventory lists**

---

## 📊 Example Usage

### Import ManaBox Export
```bash
python src/catalogue.py \
  --import data/manabox_export_2025-12-25.csv \
  --dedupe
```

### Update Prices for Collection
```bash
python src/catalogue.py \
  --update-prices \
  --source scryfall \
  --cache 24h
```

### Generate Deck Missing List
```bash
python src/catalogue.py \
  --deck decks/kaalia.txt \
  --check-missing \
  --export exports/kaalia_needs.csv
```

### Sync to Moxfield
```bash
python src/exporters/csv_exporter.py \
  --collection data/collections/main.db \
  --format moxfield \
  --output exports/moxfield_import.csv
```

---

## 🎓 Tips for Efficiency

### Scanning Setup
- **Lighting**: Bright, even fluorescent white (not warm yellow)
- **Surface**: Dark matte background reduces glare
- **Position**: Hold phone 6-8" above card
- **Batch**: Sort by set before scanning (faster recognition)

### Data Management
- **Weekly backups**: `data/collections/` → cloud storage
- **Cache API calls**: Reduces rate limits, speeds up repeated queries
- **Incremental updates**: Don't re-scan entire collection

### Quality Control
- **Review high-value cards** manually (foils, alt art)
- **Check set symbols** on similar printings
- **Validate quantities** after batch imports

---

## 🔧 Configuration

Edit `config/settings.json`:

```json
{
  "cache_duration_hours": 24,
  "price_sources": ["scryfall", "tcgplayer"],
  "default_condition": "NM",
  "auto_update_prices": false,
  "moxfield_export_format": "standard"
}
```

---

## 📚 Documentation

- **[API Integration Guide](docs/API_INTEGRATION.md)**: Detailed setup for each service
- **[Workflows](docs/WORKFLOWS.md)**: Step-by-step common tasks
- **[Troubleshooting](docs/TROUBLESHOOTING.md)**: Solutions to common issues

---

## 🗺️ Roadmap

### Current (v1.0)
- ✅ ManaBox CSV import
- ✅ Scryfall API integration
- ✅ Moxfield export format
- ✅ Basic price tracking

### Next (v1.1)
- ⬜ TCGPlayer API integration
- ⬜ Card Kingdom buylist scraper
- ⬜ Automated price alerts
- ⬜ Web dashboard (Flask/FastAPI)

### Future (v2.0)
- ⬜ Direct Moxfield API sync
- ⬜ Trade calculator with friends
- ⬜ Deck proxy generator
- ⬜ Mobile companion app

---

## 🤝 Contributing

This is a personal project, but improvements welcome:
1. Test new features thoroughly
2. Document changes in relevant files
3. Keep dependencies minimal
4. Follow existing code style

---

## 📄 License

Personal use project. API data subject to respective service terms:
- Scryfall: [API Terms](https://scryfall.com/docs/api)
- TCGPlayer: [Developer Terms](https://developer.tcgplayer.com/)
- Card Kingdom: Respect robots.txt

---

## 🙏 Acknowledgments

- **Scryfall**: Fantastic free API, comprehensive data
- **ManaBox**: Best mobile scanning experience
- **Moxfield**: Superior deck building tools
- **The Last Mile / Code The Dream**: Training and mentorship

---

**Current Status:** 🟢 Active Development  
**Last Updated:** 2025-12-25  
**Collection Size:** ~5000+ cards to catalog
