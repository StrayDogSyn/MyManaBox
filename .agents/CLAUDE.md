# CLAUDE.md - CardForge/MyManaBox Project Instructions
## AI Assistant Context for Claude Code, Windsurf, Cursor, Cline

---

## 🎯 PROJECT IDENTITY

**Project Name:** CardForge (formerly MyManaBox)
**Owner:** Hunter @ StrayDog Syndications LLC
**Repository:** https://github.com/StrayDogSyn/MyManaBox
**Local Path:** `C:\Users\EHunt\Repos\Projects\MyManaBox`

**Purpose:** Professional-grade Magic: The Gathering collection management platform with:
- Mobile scanning integration (ManaBox app)
- Multi-source price aggregation (Scryfall, TCGPlayer, CardKingdom)
- AI-powered deck optimization (Claude MCP integration)
- Automated buy/sell list generation
- Platform synchronization (Moxfield, Archidekt)

---

## 📂 CRITICAL REFERENCE FOLDERS

When working on this project, **ALWAYS** check these locations for context:

### `/docs/` - Documentation Hub
```
docs/
├── ENHANCED_FEATURES.md      # Feature descriptions and usage
├── IMPORT_INSTRUCTIONS.md    # CSV import workflows
├── PROJECT_STRUCTURE.md      # Codebase organization
├── QUICK_START.md            # Command reference
├── REFACTORING_SUMMARY.md    # Technical history
└── USAGE.md                  # Detailed usage guide
```

### `/agents/` or `/.agents/` - AI Agent Configurations (if present)
```
agents/
├── claude/
│   ├── CLAUDE.md             # This file - main instructions
│   ├── mcp_config.json       # MCP server tool definitions
│   └── prompts/              # Reusable prompt templates
├── windsurf/
│   └── rules.md              # Windsurf-specific rules
├── cursor/
│   └── .cursorrules          # Cursor AI rules
└── cline/
    └── instructions.md       # Cline-specific context
```

### `/config/` - Configuration Files
```
config/
├── mcp_config.json           # Claude MCP server configuration
├── settings.json             # Application settings
└── api_keys.env              # API credentials (gitignored)
```

### `/.vscode/` - VS Code/Windsurf Settings
```
.vscode/
├── settings.json             # Editor settings
├── launch.json               # Debug configurations
└── extensions.json           # Recommended extensions
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### Layer Structure
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ PyQt6 GUI│  │   CLI    │  │ MCP Server│ │ Web (future)│ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
├───────┴─────────────┴─────────────┴─────────────┴─────────┤
│                    SERVICE LAYER                           │
│  CollectionService │ DeckService │ PriceService │ Trade   │
├────────────────────────────────────────────────────────────┤
│                    DATA ACCESS LAYER                       │
│  CardRepository │ DeckRepository │ PriceRepository        │
├────────────────────────────────────────────────────────────┤
│                    DATABASE LAYER                          │
│  SQLite (FTS5) │ CSV Fallback │ Scryfall Cache            │
└────────────────────────────────────────────────────────────┘
```

### Source Code Structure
```
src/
├── models/           # Data classes: Card, Collection, Deck
├── data/             # Data access: CSV, Scryfall, Database
├── services/         # Business logic: sorting, search, analytics
├── presentation/     # CLI formatters and output
├── api_clients/      # External API integrations
├── importers/        # CSV/platform import handlers
├── exporters/        # Multi-format export handlers
├── mcp/              # Claude MCP server (in progress)
└── utils/            # Shared utilities and constants
```

---

## 🎨 DESIGN SPECIFICATIONS

### PyQt6 GUI Theme (CRITICAL - Follow Exactly)
```python
# Dark theme with purple accents (Moxfield-inspired)
BG_PRIMARY = "#1e1e1e"      # Main window
BG_SECONDARY = "#252526"    # Panels
ACCENT_PRIMARY = "#5a4fcf"  # Interactive elements
TEXT_PRIMARY = "#cccccc"    # Main text
```

### File Naming Conventions
- Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `SCREAMING_SNAKE_CASE`
- Test files: `test_<module_name>.py`

### Import Order
1. Standard library
2. Third-party packages
3. Local application imports
4. Type hints (if separate)

---

## 🔧 DEVELOPMENT COMMANDS

### Environment Setup
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# CLI mode
python main.py --summary
python main.py --search "Lightning Bolt"

# GUI mode (current tkinter)
python run_gui.py

# GUI mode (future PyQt6)
python run_pyqt_gui.py
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Scripts
```bash
# Verify setup
python scripts/verify_setup.py

# Enrich collection with Scryfall data
python scripts/auto_enrich.py --backup

# Import from ManaBox mobile
python scripts/import_mobile.py <file.csv> --merge

# Export to Moxfield format
python scripts/export_collection.py --format moxfield
```

---

## 📋 KEY SPECIFICATIONS TO REFERENCE

When implementing features, check these specification documents:

| Feature | Reference Document |
|---------|-------------------|
| PyQt6 GUI | `PYQT6_BUILD_SPECIFICATION.md` |
| Database Schema | `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md` |
| MCP Server | `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md` (MCP section) |
| Deck Optimization | `dual_research_synthesis.md` |
| Commander Strategy | `executive_summary_cheat_sheet.md` |

---

## 🚨 CRITICAL RULES

### DO:
- ✅ Follow existing code patterns in `src/`
- ✅ Use async/await for all I/O operations
- ✅ Add type hints to all function signatures
- ✅ Write tests for new functionality
- ✅ Use the dark theme color palette for GUI
- ✅ Handle errors gracefully with user-friendly messages
- ✅ Preserve existing CSV schemas during import
- ✅ Back up data before destructive operations

### DON'T:
- ❌ Break existing CSV import compatibility
- ❌ Hard-code file paths (use pathlib)
- ❌ Block the main thread with I/O operations
- ❌ Skip validation on user input
- ❌ Ignore the 10 req/sec Scryfall rate limit
- ❌ Store API keys in code (use .env files)
- ❌ Create duplicate utility functions

---

## 🎯 CURRENT PRIORITIES

### Immediate (This Sprint)
1. **PyQt6 GUI Implementation** - Tasks 1-5 from `PYQT6_BUILD_SPECIFICATION.md`
2. **CSV Schema Harmonization** - Handle both 15 and 17 column formats
3. **SQLite Migration** - Move from CSV to database backend

### Next Sprint
1. **MCP Server Activation** - 10 tools for Claude integration
2. **Daily Automation** - Windows Task Scheduler setup
3. **Analytics Dashboard** - PyQtGraph charts

### Backlog
1. Web interface option
2. Tournament tracking
3. Trade matching features

---

## 🧪 TESTING EXPECTATIONS

### Unit Test Coverage Target: 80%
```python
# Test file naming: test_<module>.py
# Test function naming: test_<function>_<scenario>

def test_import_csv_with_17_columns():
    """Test full schema CSV import."""
    pass

def test_import_csv_with_15_columns():
    """Test legacy schema CSV import with defaults."""
    pass
```

### Integration Test Scenarios
- Import → Enrich → Export cycle
- Search with various filters
- Price update pipeline
- MCP tool responses

---

## 📞 ASKING FOR HELP

When you need clarification, search these resources first:

1. **Project Knowledge** - Search this project's uploaded documents
2. **Scryfall API** - https://scryfall.com/docs/api
3. **PyQt6 Docs** - https://www.riverbankcomputing.com/static/Docs/PyQt6/
4. **MCP Specification** - https://modelcontextprotocol.io/

If still stuck, ask the user with specific context about what's needed.

---

## 🔑 KEY IDENTIFIERS

### Collection Context
- **Total Cards Target:** 5,000+
- **Current Cataloged:** ~1,894 unique cards
- **Primary Format:** Commander (EDH)
- **Active Decks:** Kaalia of the Vast, Cloud Ex-SOLDIER

### Commander Deck Priorities
- **Kaalia:** 65%+ win rate, competitive optimization
- **Cloud:** FF-only theme deck, 70-75% power level

### Budget Thresholds
- **Single card max:** $50 unless critical
- **Deck budget:** Variable by strategy
- **Buylist minimum:** $1.00 per card

---

**Document Version:** 2.0
**Last Updated:** December 2025
**Maintained By:** Claude (Opus 4.5) for Hunter @ StrayDog Syndications
