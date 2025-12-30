# CardForge - Windsurf Quick-Reference Prompts
## Copy-Paste Ready Development Commands
### December 2025

---

## 📁 AGENT CONFIGURATION FILES

**Copy these files to your project root for automatic context loading:**

| File | Location | Purpose |
|------|----------|---------|
| `CLAUDE.md` | `/agents/CLAUDE.md` | Main AI assistant instructions |
| `rules.md` | `/agents/windsurf/rules.md` | Windsurf-specific rules |
| `.cursorrules` | `/agents/cursor/.cursorrules` | Cursor AI rules |
| `.windsurfrules` | Project root | Windsurf auto-loading config |
| `mcp_config.json` | `/agents/mcp_config.json` | Claude MCP server definition |
| `WINDSURF_CONTEXT.md` | Project root | Comprehensive project context |

**Setup Command:**
```bash
# Copy agents folder to your MyManaBox project
cp -r agents/ C:\Users\EHunt\Repos\Projects\MyManaBox\
cp WINDSURF_CONTEXT.md C:\Users\EHunt\Repos\Projects\MyManaBox\
cp agents/.windsurfrules C:\Users\EHunt\Repos\Projects\MyManaBox\
```

---

## 🚀 QUICK START SEQUENCE

Run these prompts in order for fastest results:

---

### PROMPT 1: Environment Validation (5 min)

```
@workspace Review the MyManaBox project and run validation checks.

1. Execute: python scripts/verify_setup.py
2. Check Python version >= 3.9
3. Verify all requirements.txt dependencies install
4. Report any issues found

Then add PyQt6 to requirements.txt:
PyQt6==6.6.1
PyQt6-Qt6==6.6.1
PyQt6-sip==13.6.0
pyqtgraph==0.13.3
```

---

### PROMPT 2: Create PyQt6 Directory Structure (10 min)

```
@workspace Create the gui_pyqt6/ directory structure for the professional GUI.

Create these directories and __init__.py files:
- gui_pyqt6/__init__.py
- gui_pyqt6/styles/__init__.py
- gui_pyqt6/widgets/__init__.py
- gui_pyqt6/panels/__init__.py
- gui_pyqt6/dialogs/__init__.py
- gui_pyqt6/models/__init__.py
- gui_pyqt6/utils/__init__.py

Also move card_cache.json to data/cache/card_cache.json
```

---

### PROMPT 3: Theme System (15 min)

```
@workspace Implement the complete theme system for PyQt6 GUI.

Create gui_pyqt6/styles/theme.py with:

class Theme:
    # Backgrounds (VS Code dark inspired)
    BG_PRIMARY = "#1e1e1e"
    BG_SECONDARY = "#252526"
    BG_TERTIARY = "#2d2d30"
    BG_HOVER = "#37373d"
    
    # Accents (Moxfield purple)
    ACCENT_PRIMARY = "#5a4fcf"
    ACCENT_HOVER = "#6a5fdf"
    ACCENT_PRESSED = "#4a3fbf"
    
    # Text
    TEXT_PRIMARY = "#cccccc"
    TEXT_SECONDARY = "#999999"
    TEXT_MUTED = "#6a6a6a"
    
    # Semantic
    SUCCESS = "#4caf50"
    WARNING = "#ff9800"
    ERROR = "#f44336"
    INFO = "#2196f3"
    
    # Borders
    BORDER_DEFAULT = "#3e3e42"
    BORDER_FOCUS = "#5a4fcf"
    
    # MTG Mana Colors
    MANA_WHITE = "#f0f2c0"
    MANA_BLUE = "#0e68ab"
    MANA_BLACK = "#150b00"
    MANA_RED = "#d3202a"
    MANA_GREEN = "#00733e"

Include:
1. create_palette() -> QPalette
2. load_stylesheet() -> str (complete QSS)
3. Font definitions (Segoe UI, sizes 10/12/16)
4. Spacing constants (4/8/16/24/32)

Also create gui_pyqt6/styles/stylesheet.qss with full dark theme styling.
```

---

### PROMPT 4: Main Window (20 min)

```
@workspace Create the main application window for CardForge.

Create gui_pyqt6/main_window.py:

class MTGCommandCenter(QMainWindow):
    """CardForge main application window"""

Requirements:
1. Window: 1440x900 default, 1280x720 minimum
2. Title: "CardForge - MTG Collection Manager"
3. Menu bar: File, Collection, Decks, Tools, Help
4. Toolbar: Import, Export, Sync, Search buttons
5. Central widget: QSplitter with three panels
   - Left: Filter panel (250px)
   - Center: Card table (flex)
   - Right: Card details (300px)
6. Status bar: Total cards, Total value, Last sync

Also create run_pyqt_gui.py launcher with:
- High DPI scaling
- Application metadata (StrayDog Syndications)
- Stylesheet loading
- Error handling
```

---

### PROMPT 5: Card Table Widget (25 min)

```
@workspace Create the high-performance card table widget.

Create gui_pyqt6/widgets/card_table.py:

class CardTableModel(QAbstractTableModel):
    """Model for card data - handles 5000+ cards"""

class CardTableView(QTableView):
    """View with sorting, selection, context menus"""

Features:
1. Columns: Name, Set, Rarity, Price USD, Foil, Quantity, Condition
2. Virtual scrolling for large datasets
3. Sortable columns
4. Multi-select with checkboxes
5. Right-click context menu
6. Double-click shows card details
7. Rarity color coding:
   - Mythic: #d4763b (orange)
   - Rare: #c9a832 (gold)
   - Uncommon: #7c7c7c (silver)
   - Common: #ffffff (white)

Integration:
- Connect to existing CollectionService from src/services/
- Load data in background thread (QRunnable)
- Emit selection_changed signal
```

---

### PROMPT 6: Import Dialog (15 min)

```
@workspace Create the CSV import wizard dialog.

Create gui_pyqt6/dialogs/import_dialog.py:

class ImportWizardDialog(QDialog):
    """Multi-step import wizard"""

Steps:
1. File Selection
   - Browse button for CSV file
   - Drag-drop support
   - Recent files list

2. Schema Detection
   - Auto-detect column mapping
   - Show preview of first 5 rows
   - Allow manual column remapping

3. Import Options
   - Merge vs. Replace existing
   - Default condition (NM)
   - Default language (en)
   - Price currency (USD)

4. Confirmation
   - Summary of cards to import
   - Warnings for duplicates
   - Import button

Connect to src/data/csv_loader.py for the actual import.
Use worker thread for import operation with progress bar.
```

---

### PROMPT 7: Analytics Panel (20 min)

```
@workspace Create the analytics dashboard panel.

Create gui_pyqt6/panels/analytics_panel.py:

class AnalyticsPanel(QWidget):
    """Collection analytics dashboard with charts"""

Charts to include (use PyQtGraph):
1. Rarity Distribution - Pie chart
2. Price Distribution - Histogram
3. Set Distribution - Bar chart (top 10)
4. Mana Curve - Bar chart (0-7+)
5. Color Distribution - Pie chart

Statistics cards (StatCard widgets):
- Total Unique Cards
- Total Collection Value
- Average Card Price
- Cards in Decks vs Trade Binder
- Foil Percentage
- Most Valuable Card

Create reusable StatCard widget at gui_pyqt6/widgets/stat_card.py:
- Title, Value, optional trend indicator
- Clickable for drill-down
- Dark theme styling

Connect to src/services/AnalyticsService for data.
```

---

### PROMPT 8: Database Migration (25 min)

```
@workspace Implement SQLite database backend.

Create src/data/database.py:

class DatabaseManager:
    """SQLite database with FTS5 search"""

Schema (create tables):
1. cards - Scryfall card data cache
2. card_faces - Double-faced card support
3. price_history - Multi-source price tracking
4. collections - User collections
5. collection_cards - Inventory
6. decks - Deck management
7. deck_cards - Deck contents

Features:
1. Connection pooling
2. Schema migrations (version tracking)
3. FTS5 full-text search on name/oracle_text
4. Async support with aiosqlite
5. Bulk insert optimization

Create scripts/migrate_to_sqlite.py:
- Import existing CSVs
- Verify data integrity
- Create indexes
- Report migration results

Database location: data/collections/main.db
```

---

### PROMPT 9: MCP Server (30 min)

```
@workspace Implement Claude MCP server for AI integration.

Create src/mcp/server.py:

class CardForgeMCPServer:
    """MCP server exposing collection tools to Claude"""

Tools to implement:
1. search_collection(query, filters) -> cards[]
2. get_card_details(card_name) -> card
3. analyze_deck(deck_name) -> analysis
4. suggest_upgrades(deck_name, budget) -> suggestions[]
5. price_check(card_names[]) -> prices
6. collection_stats() -> statistics
7. find_duplicates(min_copies) -> cards[]
8. generate_buylist(min_value) -> cards[]
9. generate_shopping_list(deck_name) -> cards[]
10. optimize_deck(deck_name, strategy) -> suggestions

Configuration:
- Create config/mcp_config.json
- Tool definitions with parameters
- Rate limiting settings

Create scripts/start_mcp_server.py:
- Launch server on configurable port
- Health check endpoint
- Graceful shutdown
- Logging
```

---

### PROMPT 10: Daily Automation (15 min)

```
@workspace Complete the daily automation pipeline.

Update scripts/setup_automation.py to properly create Windows Task Scheduler tasks.

Create scripts/daily_sync.py:
1. Check for new ManaBox exports in configured directory
2. Import any new CSVs found
3. Enrich new cards with Scryfall data
4. Update prices for all cards
5. Generate daily report
6. Show Windows toast notification on completion

Create scripts/weekly_report.py:
1. Calculate collection value change (week over week)
2. List notable price movements (>10% change)
3. Deck completion progress
4. Shopping list summary
5. Save report to data/reports/

Add comprehensive logging to logs/automation.log
```

---

## 🔧 TROUBLESHOOTING PROMPTS

### PyQt6 Import Errors
```
@workspace The PyQt6 imports are failing. Check:
1. Virtual environment is activated
2. pip list | grep PyQt6 shows all packages
3. Python version is 3.9+
4. No conflicting Qt installations

Fix any issues found.
```

### Database Connection Issues
```
@workspace The SQLite database isn't working. Debug:
1. Check data/collections/main.db exists
2. Verify file permissions
3. Test connection: sqlite3 data/collections/main.db ".tables"
4. Check for locked database errors

Report findings and fixes.
```

### CSV Import Failures
```
@workspace CSV import is failing with schema errors. 

Check both CSV schemas:
- 1st_Batch_Complete.csv (17 columns with Binder)
- FIC_2nd_Batch.csv (15 columns without Binder)

Update csv_loader.py to handle both schemas with:
- Schema auto-detection
- Default values for missing columns
- Proper error messages
```

---

## 📊 VALIDATION COMMANDS

After each phase, run these to verify:

```bash
# Phase 1-2: GUI launches
python run_pyqt_gui.py

# Phase 3: Data loads
python -c "from src.data.database import DatabaseManager; db = DatabaseManager(); print(f'Cards: {db.count_cards()}')"

# Phase 4: Analytics work
python -c "from src.services.analytics_service import AnalyticsService; print(AnalyticsService().get_summary())"

# Phase 5: MCP server responds
python scripts/start_mcp_server.py --test

# Phase 6: All tests pass
pytest tests/ -v --cov=src --cov-report=html
```

---

## 🎯 SUCCESS CHECKLIST

- [ ] `python run_pyqt_gui.py` launches without errors
- [ ] Dark theme renders correctly
- [ ] Can import both CSV schemas
- [ ] Card table shows all cards
- [ ] Search filters cards in real-time
- [ ] Analytics charts display
- [ ] Database persists data
- [ ] MCP server starts
- [ ] Daily automation runs

---

**Ready to build! Start with Prompt 1 and work through sequentially.** 🚀

---

## 📋 WINDSURF SETUP INSTRUCTIONS

### Step 1: Copy Agent Files to Project
```bash
# Navigate to your MyManaBox project
cd C:\Users\EHunt\Repos\Projects\MyManaBox

# Create agents directory structure
mkdir -p agents/windsurf agents/cursor

# Copy the provided agent files:
# - agents/CLAUDE.md (main instructions)
# - agents/windsurf/rules.md (Windsurf rules)
# - agents/cursor/.cursorrules (Cursor rules)
# - agents/mcp_config.json (MCP server config)
# - agents/.windsurfrules (auto-loading config)
# - WINDSURF_CONTEXT.md (comprehensive context)
```

### Step 2: Configure Windsurf Project
When you open the project in Windsurf:
1. It will automatically read `.windsurfrules` from project root
2. Reference `WINDSURF_CONTEXT.md` for full project context
3. Check `agents/windsurf/rules.md` for specific coding rules

### Step 3: Tell Windsurf About Reference Docs
At the start of each session, you can prime Windsurf with:
```
@workspace Read the following reference documents before starting:
1. WINDSURF_CONTEXT.md - Project overview
2. agents/CLAUDE.md - Full AI instructions  
3. agents/windsurf/rules.md - Coding rules
4. PYQT6_BUILD_SPECIFICATION.md - GUI spec (in project knowledge)
5. MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md - Architecture (in project knowledge)
```

### Step 4: Use Reference in Prompts
When asking Windsurf to implement features, reference the specs:
```
@workspace Following PYQT6_BUILD_SPECIFICATION.md Task 3, implement the 
main window structure at gui_pyqt6/main_window.py with:
- 1440x900 default size
- Dark theme from agents/windsurf/rules.md
- Menu bar with File, Collection, Decks, Tools, Help
```

---

## 🔗 RELATED DOCUMENTS

These files work together to provide complete project context:

```
MyManaBox/
├── WINDSURF_CONTEXT.md          # Start here - full overview
├── .windsurfrules               # Auto-loaded by Windsurf
│
├── agents/
│   ├── CLAUDE.md                # Detailed AI instructions
│   ├── mcp_config.json          # MCP server tool definitions
│   │
│   ├── windsurf/
│   │   └── rules.md             # Windsurf-specific rules
│   │
│   └── cursor/
│       └── .cursorrules         # Cursor AI rules
│
└── docs/
    ├── PROJECT_STRUCTURE.md     # Codebase organization
    ├── ENHANCED_FEATURES.md     # Feature documentation
    └── USAGE.md                 # Usage guide
```

---

## 🎯 SUCCESS METRICS

After setup, Windsurf should:
- ✅ Automatically apply dark theme colors
- ✅ Use async/await for I/O operations
- ✅ Follow existing patterns in src/
- ✅ Handle both CSV schemas
- ✅ Reference correct spec documents
- ✅ Know about MCP server tools
- ✅ Understand Commander deck context
