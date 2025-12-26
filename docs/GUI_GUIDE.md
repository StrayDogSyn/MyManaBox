# CardForge GUI Guide

## Overview

CardForge now includes a modern Tkinter-based graphical interface that provides an intuitive way to manage your MTG collection.

![CardForge GUI](https://via.placeholder.com/800x500?text=CardForge+GUI)

## Features

### 📊 Collection Dashboard
- Real-time collection statistics
- Total value tracking
- Card count and unique card tracking
- Foil count and set distribution

### 🔍 Advanced Search
- Real-time search with debouncing
- Search by card name, type, or oracle text
- Filter results instantly

### 📋 Collection Browser
- Sortable table view of all cards
- View quantity, condition, and pricing
- Multi-column sorting
- Select multiple cards for batch operations

### 🎴 Card Details Panel
- Detailed card information
- Current market pricing
- Gain/loss tracking vs purchase price
- Collection-specific metadata (condition, foil status)

## Launching the GUI

### Quick Launch

**Windows:**
```bash
python run_gui.py
```

**macOS/Linux:**
```bash
./run_gui.py
```

### Using Python Module

```bash
python -m cardforge.gui.app
```

## Interface Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  File   Collection   Tools   Help          🔍 Search...   Actions│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 Collection Overview                                          │
│  ┌────────────┬────────────┬────────────┬────────────┐          │
│  │ 💰 Total   │ 🃏 Total   │ 📊 Average │ ✨ Foils  │          │
│  │ Value      │ Cards      │ Value      │            │          │
│  └────────────┴────────────┴────────────┴────────────┘          │
│                                                                  │
├────────────────────────────────┬────────────────────────────────┤
│                                │                                │
│  Card Collection Table         │  Card Details                  │
│  ┌──────────────────────────┐ │  ┌──────────────────────────┐ │
│  │ Name | Set | Rarity | ... │ │  │                          │ │
│  │ Lightning Bolt | M10 | C   │ │  │  [Card Name]             │ │
│  │ Sol Ring | C14 | U          │ │  │  [Mana Cost]             │ │
│  │ ...                        │ │  │  [Type Line]             │ │
│  │                            │ │  │  [Oracle Text]           │ │
│  │                            │ │  │  [Pricing Info]          │ │
│  └──────────────────────────┘ │  └──────────────────────────┘ │
│                                │                                │
└────────────────────────────────┴────────────────────────────────┘
│  Ready                                           1,234 cards    │
└─────────────────────────────────────────────────────────────────┘
```

## Keyboard Shortcuts

| Shortcut    | Action                    |
|-------------|---------------------------|
| `Ctrl+I`    | Import CSV file           |
| `Ctrl+E`    | Export collection         |
| `Ctrl+N`    | Add new card              |
| `F5`        | Refresh collection        |
| `Ctrl+Q`    | Quit application          |

## Menu Bar

### File Menu
- **Import CSV...** - Import cards from Moxfield or ManaBox CSV export
- **Export Collection...** - Export your collection to CSV or JSON
- **Exit** - Close the application

### Collection Menu
- **Refresh** - Reload collection from database
- **Find Duplicates** - Identify cards you have in excess
- **Add Card...** - Add a new card to your collection

### Tools Menu
- **Sync Sets from Scryfall** - Download latest set metadata
- **Update Prices** - Refresh current market prices

### Help Menu
- **About CardForge** - Application information

## Usage Examples

### Searching Your Collection

1. Click the search bar or use `Ctrl+F`
2. Type any card name, type, or text from oracle text
3. Results filter in real-time

**Example searches:**
- `"lightning"` - finds Lightning Bolt, Lightning Greaves, etc.
- `"instant"` - shows all instant spells
- `"draw a card"` - finds cards with that oracle text

### Sorting Cards

Click any column header to sort by that column:
- **Name** - Alphabetical
- **Set** - Alphabetically by set code
- **Rarity** - Common, Uncommon, Rare, Mythic
- **Value** - Market price (ascending/descending)
- **Total** - Total value for quantity owned

Click again to reverse sort direction.

### Viewing Card Details

- **Single-click** a card to view details in the right panel
- **Double-click** to open additional actions (coming soon)

### Finding Duplicates

1. Go to **Collection → Find Duplicates**
2. Wait for analysis to complete
3. Review cards you have in excess of playsets
4. Identify trading or selling opportunities

## Architecture

The GUI is built on a clean architecture that bridges async CardForge services with the synchronous Tkinter UI:

```
┌──────────────────────────────────────────────┐
│              GUI Layer (Tkinter)             │
│  ┌────────────────────────────────────────┐  │
│  │         Main Window & Panels           │  │
│  └────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│           Async Bridge Layer                 │
│  (Threads async operations for Tkinter)      │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│        CardForge Services (Async)            │
│  • CollectionService                         │
│  • CardService                               │
│  • DeckService                               │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│         Repository Layer (aiosqlite)         │
└──────────────────────────────────────────────┘
```

### Key Components

#### AsyncBridge
Runs an asyncio event loop in a background thread, allowing the synchronous Tkinter GUI to call async CardForge services without blocking the UI.

#### Panels
- **StatsPanel** - Top dashboard showing collection metrics
- **CollectionBrowserPanel** - Sortable, filterable table of cards
- **CardDetailPanel** - Right sidebar with detailed card info

#### Widgets
- **SearchBar** - Debounced search with autocomplete
- **StatCard** - Metric display cards
- **StyledButton** - Themed buttons with hover effects
- **ToastNotification** - Non-intrusive notifications

## Customization

### Theme Customization

Edit `cardforge/gui/theme.py` to customize colors:

```python
class Theme:
    # Change accent color from purple to blue
    ACCENT_PRIMARY = "#2196f3"
    ACCENT_HOVER = "#42a5f5"
    ACCENT_PRESSED = "#1976d2"

    # Change background to lighter dark theme
    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#2d2d30"
```

### Adding Custom Widgets

Create new widgets in `cardforge/gui/widgets.py`:

```python
class MyCustomWidget(StyledFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Your widget implementation
```

## Troubleshooting

### GUI Won't Launch

**Problem:** `ModuleNotFoundError: No module named 'cardforge'`

**Solution:** Ensure you're running from the project root:
```bash
cd /path/to/MyManaBox
python run_gui.py
```

### Async Errors

**Problem:** `RuntimeError: AsyncBridge not started`

**Solution:** The async bridge should start automatically. If it doesn't, ensure your Python version is 3.11+.

### Display Issues on macOS

**Problem:** Buttons or text appear incorrectly sized

**Solution:** macOS Tkinter sometimes has font rendering issues. Try:
```python
# In theme.py, change:
FONT_FAMILY = "Helvetica"  # Instead of "Segoe UI"
```

### Collection Not Loading

**Problem:** Empty collection on launch

**Solution:**
1. Ensure database is initialized: `python -m cardforge.cli.main db init`
2. Import some cards: `python -m cardforge.cli.main collection import your_file.csv`
3. Restart the GUI

## Future Enhancements

Planned features for future releases:

- [ ] **Deck Builder** - Visual deck construction interface
- [ ] **Price Charts** - Historical price tracking with matplotlib
- [ ] **Card Images** - Display card images from Scryfall
- [ ] **Advanced Filters** - Color, CMC, rarity filters
- [ ] **Batch Operations** - Edit multiple cards at once
- [ ] **Export to Moxfield** - Direct deck export
- [ ] **Trade Finder** - Match wants with duplicates
- [ ] **Dark/Light Theme Toggle** - User preference

## Contributing

Want to improve the GUI? Here's how:

1. **Add a new panel:** Create in `cardforge/gui/panels.py`
2. **Add a new widget:** Create in `cardforge/gui/widgets.py`
3. **Extend functionality:** Add to `cardforge/gui/app.py`

See the [Component Library](https://claude.ai/public/artifacts/7edd3867-34d8-4f34-a907-facebbae230e) for reusable widget patterns.

## Support

For issues or feature requests:
- GitHub Issues: https://github.com/StrayDogSyn/MyManaBox/issues
- Documentation: See [API.md](API.md) and [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Built with ❤️ for the Magic: The Gathering community**

*The GUI complements the powerful CLI and MCP integration, giving you multiple ways to manage your collection.*
