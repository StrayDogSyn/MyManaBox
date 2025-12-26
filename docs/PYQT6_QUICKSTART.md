# CardForge PyQt6 GUI - Quick Start

## 🚀 Launch in 3 Steps

### 1. Install PyQt6

```bash
pip install PyQt6>=6.6.0
```

### 2. Initialize Database (if needed)

```bash
python -m cardforge.cli.main db init
```

### 3. Launch PyQt6 GUI

```bash
python run_qt_gui.py
```

That's it! The professional GUI will open with your collection.

---

## First Time Setup

If this is your first time using CardForge, you'll need some cards:

### Import from Moxfield or ManaBox

1. Export your collection as CSV
2. Save the CSV file
3. Use CLI to import (GUI import coming soon):

```bash
python -m cardforge.cli.main collection import "path/to/your/export.csv"
```

Then launch the PyQt6 GUI:

```bash
python run_qt_gui.py
```

---

## Quick Tour

![CardForge PyQt6 Interface](../assets/screenshots/qt_main_window.png)

### 📊 Dashboard
Top panel shows:
- **Total Value** - Your collection's worth
- **Total Cards** - Count with unique cards
- **Average Value** - Per card
- **Foils** - Special printings

### 🔍 Search
Type in the search bar:
- By name: `"Lightning Bolt"`
- By type: `"instant"`
- By text: `"draw a card"`

Results filter instantly (300ms debounce)!

### 📋 Collection Table
- Click column headers to sort
- Click again to reverse
- Select a card to view details
- Alternating row colors for easy reading

### 🎴 Card Details
Right panel shows:
- Full card information
- Current market price
- Your quantity and condition
- Gain/loss vs purchase price

---

## Keyboard Shortcuts

- `Ctrl+I` - Import CSV (coming soon)
- `Ctrl+E` - Export collection
- `Ctrl+N` - Add new card
- `Ctrl+Q` - Quit
- `F5` - Refresh collection

---

## Common Tasks

### Find Your Most Valuable Cards

1. Click the **"Value"** column header
2. Click again to sort highest-to-lowest
3. Review your top cards

### Search for Specific Card Types

Want all your creatures?

1. Type `"creature"` in search bar
2. Results filter instantly
3. Clear search to see all cards

### Find Duplicates

1. Go to **Collection → Find Duplicates**
2. Review cards you have in excess
3. Identify trading opportunities

---

## What's Different from Tkinter GUI?

| Feature | Tkinter GUI | PyQt6 GUI |
|---------|-------------|-----------|
| Look & Feel | Basic | **Native** |
| Performance | Good | **Excellent** |
| Styling | Limited | **Full QSS** |
| Threading | Custom bridge | **Built-in** |
| File Size | Small | Moderate |
| Production Ready | Yes | **Very Yes** |

**Both GUIs work with the same CardForge backend!**

---

## Troubleshooting

### "No module named 'PyQt6'"

Install PyQt6:
```bash
pip install PyQt6>=6.6.0
```

### "No cards loaded"

Import a collection first:
```bash
python -m cardforge.cli.main collection import your_file.csv
```

### GUI looks blurry on high-DPI display

This is handled automatically in the code. If issues persist, check your Windows display scaling settings.

---

## Next Steps

- 📖 Read the [Full PyQt6 GUI Guide](PYQT6_GUI_GUIDE.md)
- 💻 Explore the [CLI commands](API.md)
- 🤖 Set up [MCP integration](MCP_INTEGRATION.md)
- 🎨 Learn about [customizing the theme](PYQT6_GUI_GUIDE.md#theming-system)

---

**Enjoy the professional desktop experience! ✨**
