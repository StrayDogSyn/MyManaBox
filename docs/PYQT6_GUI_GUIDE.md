# CardForge PyQt6 GUI Guide

## Overview

CardForge now includes a **professional PyQt6-based desktop GUI** that provides a native, high-performance interface for managing your MTG collection.

### Why PyQt6?

- **Native Performance** - Truly native look and feel on Windows, macOS, and Linux
- **Professional Quality** - Used by Autodesk Maya, VLC, Spotify, OBS Studio
- **Rich Widget Library** - Comprehensive built-in components
- **QSS Styling** - CSS-like styling system for complete customization
- **Thread-Safe** - Proper async integration without blocking

## Features

### 📊 Collection Dashboard
- Real-time collection statistics
- Total value tracking
- Card count and foil tracking
- Set distribution

### 🔍 Advanced Search
- Debounced search (300ms)
- Search by name, type, or oracle text
- Instant filtering

### 📋 Collection Browser
- Sortable table with 9 columns
- Click headers to sort ascending/descending
- Alternating row colors for readability
- Single-click selection

### 🎴 Card Details Panel
- Full card information
- Current market pricing
- Gain/loss tracking
- Collection metadata

### 🎨 Professional Theming
- Dark purple theme
- Consistent with Tkinter GUI
- Fully customizable via QSS
- Fallback QPalette for unstyled widgets

## Quick Start

### Launch the GUI

**Windows:**
```bash
python run_qt_gui.py
```

**macOS/Linux:**
```bash
./run_qt_gui.py
```

**Using Python Module:**
```bash
python -m cardforge.qt_gui.app
```

## Architecture

### Module Structure

```
cardforge/qt_gui/
├── __init__.py           # Module exports
├── app.py                # Application entry point
├── async_bridge.py       # Async/Qt integration
├── theme.py              # QSS theming system
├── main_window.py        # Main application window
├── widgets.py            # Reusable UI components
└── panels.py             # Main UI panels
```

### Async Integration

Unlike Tkinter, PyQt6 has its own event loop. The `AsyncBridge` class provides clean integration:

```python
class MyWidget(QWidget):
    def __init__(self):
        self.async_bridge = AsyncBridge()

    def load_data(self):
        async def fetch():
            return await collection_service.get_stats(collection_id)

        self.async_bridge.run_async(
            fetch(),
            on_success=self.handle_stats,
            on_error=self.handle_error
        )

    def handle_stats(self, stats):
        # Update UI with stats
        pass

    def handle_error(self, error):
        QMessageBox.critical(self, "Error", str(error))
```

### How It Works

1. `AsyncWorker` (QThread) runs coroutines in background threads
2. Each worker has its own asyncio event loop
3. Signals (`finished`, `error`) communicate results back to Qt
4. Qt's signal/slot system ensures thread-safe UI updates

## Theming System

### QSS (Qt Style Sheets)

CardForge uses QSS for styling, similar to CSS:

```python
# In theme.py
class CardForgeTheme:
    BG_PRIMARY = "#1a1625"
    ACCENT_PRIMARY = "#5a4fcf"

    @classmethod
    def get_stylesheet(cls) -> str:
        return f"""
        QPushButton {{
            background-color: {cls.ACCENT_PRIMARY};
            color: {cls.TEXT_PRIMARY};
            border-radius: 4px;
            padding: 8px 16px;
        }}

        QPushButton:hover {{
            background-color: {cls.ACCENT_HOVER};
        }}
        """
```

### Customizing the Theme

Edit `cardforge/qt_gui/theme.py`:

```python
# Change accent color from purple to blue
ACCENT_PRIMARY = "#2196f3"
ACCENT_HOVER = "#42a5f5"
ACCENT_PRESSED = "#1976d2"

# Change background to lighter dark theme
BG_PRIMARY = "#1e1e1e"
BG_SECONDARY = "#2d2d30"
```

The entire UI will update automatically!

### Dynamic Property Classes

Use dynamic properties for widget variants:

```python
# In QSS
QPushButton[class="secondary"] {
    background-color: #2a2235;
}

# In Python
button = QPushButton("Cancel")
button.setProperty("class", "secondary")
button.style().unpolish(button)  # Force restyle
button.style().polish(button)
```

## Components

### Widgets

#### SearchBar
```python
search_bar = SearchBar(placeholder="Search cards...")
search_bar.search_triggered.connect(self.on_search)

def on_search(self, query: str):
    print(f"Searching for: {query}")
```

#### StatCard
```python
card = StatCard(
    title="Total Value",
    value="$1,234.56",
    subtitle="2,500 cards",
    icon="💰"
)

# Update later
card.update_value("$1,500.00", "2,600 cards")
```

#### StatsPanel
```python
stats_panel = StatsPanel()
stats_panel.update_stats(collection_stats)
```

#### LoadingOverlay
```python
loading = LoadingOverlay(self, "Loading collection...")
loading.show()

# When done
loading.close()
```

### Panels

#### CollectionBrowserPanel
```python
browser = CollectionBrowserPanel()
browser.card_selected.connect(self.on_card_selected)

browser.load_cards(card_list)
browser.filter_cards("lightning")
browser.clear_filter()
```

#### CardDetailPanel
```python
detail_panel = CardDetailPanel()
detail_panel.show_card(collection_card)
```

## Menu Bar & Shortcuts

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+I` | Import CSV |
| `Ctrl+E` | Export Collection |
| `Ctrl+N` | Add New Card |
| `Ctrl+Q` | Quit Application |
| `F5` | Refresh Collection |

### Adding Custom Actions

```python
def _create_custom_menu(self):
    custom_menu = self.menuBar().addMenu("&Custom")

    action = QAction("My Action", self)
    action.setShortcut(QKeySequence("Ctrl+M"))
    action.triggered.connect(self.my_custom_function)
    custom_menu.addAction(action)
```

## Advanced Features

### Custom Widgets

Create reusable widgets by subclassing Qt widgets:

```python
class ColorFilter(QWidget):
    colors_changed = pyqtSignal(list)  # Signal

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        for color in ['W', 'U', 'B', 'R', 'G']:
            btn = QPushButton(color)
            btn.setCheckable(True)
            btn.toggled.connect(self._on_color_toggled)
            layout.addWidget(btn)

    def _on_color_toggled(self):
        selected = [
            btn.text() for btn in self.findChildren(QPushButton)
            if btn.isChecked()
        ]
        self.colors_changed.emit(selected)
```

### Dialogs

```python
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

class AddCardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Card")

        layout = QVBoxLayout(self)

        # Add your form fields here
        self.card_name = QLineEdit()
        layout.addWidget(QLabel("Card Name:"))
        layout.addWidget(self.card_name)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_card_name(self):
        return self.card_name.text()

# Usage
dialog = AddCardDialog(self)
if dialog.exec() == QDialog.DialogCode.Accepted:
    card_name = dialog.get_card_name()
    # Process card
```

### Charts with QChart

For production apps, use QtCharts:

```bash
pip install PyQt6-Charts
```

```python
from PyQt6.QtCharts import QChart, QChartView, QPieSeries

class RarityChart(QChartView):
    def __init__(self, stats):
        chart = QChart()

        series = QPieSeries()
        series.append("Common", stats.common_count)
        series.append("Uncommon", stats.uncommon_count)
        series.append("Rare", stats.rare_count)
        series.append("Mythic", stats.mythic_count)

        chart.addSeries(series)
        chart.setTitle("Rarity Distribution")

        super().__init__(chart)
```

## Debugging

### Enable Qt Debug Output

```python
import os
os.environ['QT_DEBUG_PLUGINS'] = '1'
```

### Inspector Tool

For complex layouts, use Qt's widget inspector:

```python
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
# ... create windows ...

# Press Ctrl+Shift+I in running app to inspect
```

## Comparison: Tkinter vs PyQt6

| Feature | Tkinter | PyQt6 |
|---------|---------|-------|
| Performance | Good | Excellent |
| Native Look | No | Yes |
| Styling | Limited | QSS (CSS-like) |
| Threading | Manual | Built-in |
| Charts | Manual | QtCharts |
| Icons | Unicode | QIcon, SVG |
| Licensing | Free | LGPL (PySide6) or GPL/Commercial (PyQt6) |
| Learning Curve | Easy | Moderate |
| Production Apps | Few | Many (VLC, Maya, etc.) |

## Troubleshooting

### GUI Won't Launch

**Problem:** `ModuleNotFoundError: No module named 'PyQt6'`

**Solution:**
```bash
pip install PyQt6>=6.6.0
```

### Theme Not Applied

**Problem:** Widgets look plain

**Solution:** Ensure stylesheet is applied:
```python
app.setStyleSheet(THEME.get_stylesheet())
```

### Async Operations Blocking UI

**Problem:** UI freezes during async operations

**Solution:** Ensure you're using `AsyncBridge`:
```python
# DON'T do this (blocks UI)
result = asyncio.run(some_async_function())

# DO this (non-blocking)
self.async_bridge.run_async(
    some_async_function(),
    on_success=self.handle_result
)
```

### High DPI Scaling Issues

**Problem:** UI looks blurry on high-DPI displays

**Solution:** Enable high-DPI scaling:
```python
app.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
```

## Next Steps

### Planned Enhancements

- [ ] **Filter Sidebar** - Color, price range, rarity filters
- [ ] **Analytics Dashboard** - Charts using QtCharts
- [ ] **Deck Builder** - Visual deck construction
- [ ] **Card Images** - Display card art from Scryfall
- [ ] **Drag & Drop** - Drag cards between decks
- [ ] **Export to PDF** - Print deck lists
- [ ] **Theme Switcher** - Light/Dark mode toggle

### Contributing

Want to add features? The architecture makes it easy:

1. **Add a widget:** Create in `widgets.py`
2. **Add a panel:** Create in `panels.py`
3. **Add async functionality:** Use `AsyncBridge`
4. **Style it:** Add QSS to `theme.py`

## Resources

- [Official PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt 6 Documentation](https://doc.qt.io/qt-6/)
- [QSS Reference](https://doc.qt.io/qt-6/stylesheet-reference.html)
- [Qt Examples](https://doc.qt.io/qt-6/qtexamplesandtutorials.html)

---

**Built with ❤️ for the Magic: The Gathering community**

*The PyQt6 GUI provides a professional desktop experience while maintaining full compatibility with CardForge's async backend.*
