# CardForge GUI Quick Start

## 🚀 Launch in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python -m cardforge.cli.main db init
```

### 3. Launch GUI

```bash
python run_gui.py
```

That's it! The GUI will open and automatically load your collection.

---

## First Time Setup

If this is your first time using CardForge, you'll need some cards in your collection:

### Import from Moxfield or ManaBox

1. Export your collection from Moxfield or ManaBox as CSV
2. In the GUI, go to **File → Import CSV...**
3. Select your exported file
4. Wait for import to complete

### Or Use the CLI

```bash
python -m cardforge.cli.main collection import "path/to/your/export.csv"
```

Then launch the GUI:

```bash
python run_gui.py
```

---

## Quick Tour

### 📊 Dashboard
The top panel shows your collection at a glance:
- Total value
- Card count
- Average card value
- Foil count

### 🔍 Search
Type in the search bar to filter cards:
- By name: `"Lightning Bolt"`
- By type: `"instant"`
- By text: `"draw a card"`

### 📋 Collection Table
Click column headers to sort:
- Name, Set, Rarity
- Value, Quantity
- Ascending/Descending

### 🎴 Card Details
Click any card to see:
- Full card information
- Current market price
- Your quantity and condition
- Gain/loss vs purchase price

---

## Common Tasks

### Find Valuable Cards

1. Click the **Value** column header twice to sort highest-to-lowest
2. Review your most valuable cards
3. Consider moving them to a secure location

### Find Duplicates

1. Go to **Collection → Find Duplicates**
2. Review cards you have in excess
3. Identify trading opportunities

### Search by Type

Want to see all your creatures?

1. Type `"creature"` in the search bar
2. Results filter instantly

---

## Keyboard Shortcuts

- `Ctrl+I` - Import CSV
- `Ctrl+E` - Export collection
- `Ctrl+N` - Add new card
- `F5` - Refresh collection
- `Ctrl+F` - Focus search bar

---

## Troubleshooting

### "No cards loaded"

Make sure you've imported a collection:
```bash
python -m cardforge.cli.main collection import your_file.csv
```

### GUI won't start

Ensure you're in the project directory:
```bash
cd /path/to/MyManaBox
python run_gui.py
```

### Module not found errors

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

- 📖 Read the [Full GUI Guide](GUI_GUIDE.md)
- 💻 Explore the [CLI commands](API.md)
- 🤖 Set up [MCP integration](MCP_INTEGRATION.md)

---

**Enjoy managing your collection! ✨**
