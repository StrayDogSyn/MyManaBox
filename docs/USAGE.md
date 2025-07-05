# MyManaBox Usage Examples

## Basic Commands

### View Collection Summary
```bash
python mymanabox.py --summary
```
Shows total cards, unique cards, total value, and top 10 most valuable cards.

### Search for Specific Cards
```bash
python mymanabox.py --search "Lightning Bolt"
python mymanabox.py --search "Dragon"
```

### Find Duplicate Cards
```bash
python mymanabox.py --duplicates
```

### View Collection Statistics
```bash
python mymanabox.py --stats
```

## Sorting and Exporting

### Sort by Color
```bash
python mymanabox.py --sort color
```
Creates CSV files for each color: `sorted_output/color_white.csv`, `color_blue.csv`, etc.

### Sort by Set
```bash
python mymanabox.py --sort set
```

### Sort by Rarity
```bash
python mymanabox.py --sort rarity
```

### Sort by Type
```bash
python mymanabox.py --sort type
```

## Enhanced Features (with API)

### Enable Enhanced Mode
```bash
python mymanabox.py --enhanced --summary
```

### Mana Curve Analysis
```bash
python mymanabox.py --enhanced --mana-curve
```
Analyzes the converted mana cost distribution of your collection.

### Find Expensive Cards
```bash
# Find cards worth $10 or more
python mymanabox.py --enhanced --expensive 10

# Find cards worth $50 or more
python mymanabox.py --enhanced --expensive 50
```

### Enhanced Sorting (More Accurate)
```bash
# Sort by color using API data for accuracy
python mymanabox.py --enhanced --sort color

# Sort by type with precise type information
python mymanabox.py --enhanced --sort type

# Sort by rarity with real rarity data
python mymanabox.py --enhanced --sort rarity
```

## Configuration Options

### Use Different CSV File
```bash
python mymanabox.py --csv my_other_collection.csv --summary
```

### Change Output Directory
```bash
python mymanabox.py --sort color --output-dir my_sorted_cards
```

### Disable API (Enhanced Mode Without Network)
```bash
python mymanabox.py --enhanced --no-api --summary
```

## Interactive Mode

Simply run without arguments for interactive mode:
```bash
python mymanabox.py
```

## Output Files

### Sorted Collections
- Basic sorting: `sorted_output/`
- Enhanced sorting: `enhanced_sorted/`

### API Cache
- `card_cache.json` - Cached API responses for faster subsequent runs

## Tips

1. **First Run**: The enhanced mode will be slower on first run as it fetches card data from the API. Subsequent runs use cached data.

2. **Large Collections**: For collections with thousands of cards, enhanced mode may take several minutes on first run due to API rate limiting.

3. **Network Issues**: If you have network issues, use `--no-api` flag with enhanced features for offline functionality.

4. **CSV Format**: Ensure your CSV export from Moxfield includes the standard columns: Count, Name, Edition, Condition, Purchase Price, etc.
