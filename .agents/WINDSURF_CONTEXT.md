# WINDSURF_CONTEXT.md
## CardForge/MyManaBox - Complete Project Context for AI Assistants
### Place this file in project root for automatic context loading

---

## 🎯 PROJECT SUMMARY

**What is this?** A professional-grade Magic: The Gathering collection management platform.

**Tech Stack:**
- Python 3.9+ 
- GUI: PyQt6 (transitioning from tkinter)
- Database: SQLite with FTS5 full-text search
- APIs: Scryfall (card data), TCGPlayer (pricing)
- AI: Claude MCP server integration

**Owner:** Hunter @ StrayDog Syndications LLC
**Repo:** https://github.com/StrayDogSyn/MyManaBox

---

## 📁 CRITICAL FOLDERS TO REFERENCE

```
MyManaBox/
├── agents/                    # 🤖 AI ASSISTANT CONFIGS
│   ├── CLAUDE.md             # Main Claude/AI instructions
│   ├── windsurf/rules.md     # Windsurf-specific rules
│   └── cursor/.cursorrules   # Cursor AI rules
│
├── docs/                      # 📚 DOCUMENTATION
│   ├── PROJECT_STRUCTURE.md  # Codebase organization
│   ├── ENHANCED_FEATURES.md  # Feature reference
│   ├── USAGE.md              # Usage guide
│   └── IMPORT_INSTRUCTIONS.md# CSV import guide
│
├── src/                       # 💻 SOURCE CODE
│   ├── models/               # Data classes
│   ├── data/                 # Data access layer
│   ├── services/             # Business logic
│   └── presentation/         # UI layer
│
├── scripts/                   # 🔧 AUTOMATION
│   ├── auto_enrich.py        # Price enrichment
│   ├── import_mobile.py      # ManaBox import
│   └── verify_setup.py       # Health checks
│
├── gui_pyqt6/                 # 🎨 NEW GUI (in development)
│   ├── main_window.py        # Main window
│   ├── styles/               # Theme system
│   ├── widgets/              # Custom widgets
│   └── panels/               # Major UI panels
│
└── data/                      # 💾 USER DATA (don't modify directly)
    ├── collections/          # Database files
    └── backups/              # Automatic backups
```

---

## 📋 SPECIFICATION DOCUMENTS

**ALWAYS check these before implementing features:**

| Document | Purpose | Location |
|----------|---------|----------|
| `PYQT6_BUILD_SPECIFICATION.md` | Complete GUI implementation spec | Project Knowledge |
| `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md` | Architecture & database schema | Project Knowledge |
| `dual_research_synthesis.md` | Commander deck optimization data | Project Knowledge |
| `executive_summary_cheat_sheet.md` | Quick reference for deck building | Project Knowledge |

---

## 🎨 DESIGN SYSTEM (MANDATORY)

### Color Palette
```python
class Theme:
    # Backgrounds (VS Code dark inspired)
    BG_PRIMARY = "#1e1e1e"      # Main window
    BG_SECONDARY = "#252526"    # Panels
    BG_TERTIARY = "#2d2d30"     # Input fields
    BG_HOVER = "#37373d"        # Hover states
    
    # Accents (Moxfield purple)
    ACCENT_PRIMARY = "#5a4fcf"  # Buttons, focus
    ACCENT_HOVER = "#6a5fdf"    # Hover state
    ACCENT_PRESSED = "#4a3fbf"  # Pressed state
    
    # Text
    TEXT_PRIMARY = "#cccccc"    # Main text
    TEXT_SECONDARY = "#999999"  # Muted text
    TEXT_MUTED = "#6a6a6a"      # Disabled text
    
    # Semantic
    SUCCESS = "#4caf50"         # Green
    WARNING = "#ff9800"         # Orange
    ERROR = "#f44336"           # Red
    INFO = "#2196f3"            # Blue
    
    # Borders
    BORDER_DEFAULT = "#3e3e42"
    BORDER_FOCUS = "#5a4fcf"
    
    # MTG Mana Colors
    MANA_WHITE = "#f0f2c0"
    MANA_BLUE = "#0e68ab"
    MANA_BLACK = "#150b00"
    MANA_RED = "#d3202a"
    MANA_GREEN = "#00733e"
```

### Typography
```python
FONT_FAMILY = "Segoe UI"
FONT_SIZE_LARGE = 16
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10
```

### Spacing (8px grid)
```python
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32
```

---

## 🔧 DEVELOPMENT COMMANDS

```bash
# Environment
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

# Run Application
python main.py --summary        # CLI summary
python run_gui.py               # Current GUI (tkinter)
python run_pyqt_gui.py          # New GUI (PyQt6)

# Testing
pytest tests/ -v                # All tests
pytest tests/ -v --cov=src      # With coverage

# Scripts
python scripts/verify_setup.py              # Check environment
python scripts/auto_enrich.py --backup      # Update prices
python scripts/import_mobile.py file.csv    # Import CSV
python scripts/export_collection.py --format moxfield  # Export
```

---

## 📊 DATABASE SCHEMA (Key Tables)

```sql
-- Card cache (from Scryfall)
cards (id, scryfall_id, name, set_code, oracle_text, prices, ...)

-- User's inventory
collection_cards (id, card_id, quantity, foil, condition, ...)

-- Deck management
decks (id, name, format, commander_id, colors, ...)
deck_cards (id, deck_id, card_id, quantity, category, ...)

-- Price history
price_history (id, card_id, source, price_usd, recorded_at, ...)
```

---

## 🚨 RULES & CONSTRAINTS

### ALWAYS DO:
✅ Use type hints on all functions
✅ Use pathlib for file paths
✅ Use async/await for I/O operations
✅ Back up data before destructive operations
✅ Handle both CSV schemas (15 and 17 columns)
✅ Follow existing code patterns in src/
✅ Test new functionality (80% coverage target)
✅ Use the dark theme color palette for GUI

### NEVER DO:
❌ Hard-code Windows paths
❌ Block main thread with I/O
❌ Skip error handling
❌ Exceed Scryfall's 10 req/sec limit
❌ Modify user data without backup
❌ Create duplicate utility functions
❌ Break CSV import compatibility

---

## 🎯 CURRENT PRIORITIES

### Immediate (This Sprint)
1. **PyQt6 GUI** - Implement Tasks 1-5 from spec
2. **CSV Harmonization** - Handle both schemas
3. **SQLite Migration** - Move from CSV to database

### Next Sprint
1. **MCP Server** - Activate 10 Claude tools
2. **Daily Automation** - Task Scheduler setup
3. **Analytics Dashboard** - Charts with PyQtGraph

---

## 🔑 IMPORTANT CONTEXT

### Collection Status
- **Target:** 5,000+ cards
- **Current:** ~1,894 cataloged
- **Format:** Commander (EDH)
- **Active Decks:** Kaalia of the Vast, Cloud Ex-SOLDIER

### CSV Schemas
```
17-column (full): Includes Binder Name, Binder Type
15-column (minimal): No Binder columns

Both MUST be supported - auto-detect and provide defaults.
```

### API Limits
- **Scryfall:** 10 requests/second (ENFORCE)
- **TCGPlayer:** Requires API key
- **Caching:** 24-hour cache for card data

---

## 📞 WHEN YOU NEED HELP

1. **Search project knowledge** for spec documents
2. **Check `src/`** for existing patterns
3. **Review docs/** for feature documentation
4. **Ask user** with specific context about what's needed

---

## 🧪 TESTING PATTERNS

```python
# Test file: test_<module>.py
# Test function: test_<function>_<scenario>()

# Example
def test_import_csv_with_17_columns_succeeds():
    """Import full schema CSV file."""
    result = import_csv("full_schema.csv")
    assert len(result.cards) > 0
    assert result.cards[0].binder_name is not None

def test_import_csv_with_15_columns_uses_defaults():
    """Import minimal schema CSV with default binder."""
    result = import_csv("minimal_schema.csv")
    assert result.cards[0].binder_name == "Default"
```

---

## 📚 ADDITIONAL RESOURCES

- **Scryfall API:** https://scryfall.com/docs/api
- **PyQt6 Docs:** https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **MCP Spec:** https://modelcontextprotocol.io/
- **EDHrec:** https://edhrec.com (deck statistics)

---

**Version:** 2.0
**Last Updated:** December 2025
**For AI Assistants:** Claude Code, Windsurf, Cursor, Cline
