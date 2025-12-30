# Windsurf Rules - CardForge/MyManaBox Project
## AI Coding Assistant Configuration

---

## Project Context

You are working on **CardForge**, a professional MTG collection management platform.

**Key Facts:**
- Python 3.9+ project with PyQt6 GUI (in transition from tkinter)
- Windows 11 primary environment
- SQLite database with FTS5 search
- Scryfall API for card data (10 req/sec limit)
- Claude MCP integration for AI-powered features

---

## Reference Documents (READ FIRST)

Before implementing ANY feature, check these files:

| Task | Reference File |
|------|---------------|
| GUI work | `PYQT6_BUILD_SPECIFICATION.md` |
| Database/architecture | `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md` |
| Deck optimization | `dual_research_synthesis.md` |
| Project structure | `docs/PROJECT_STRUCTURE.md` |
| Features | `docs/ENHANCED_FEATURES.md` |

---

## Code Style Rules

### Python
```python
# Always use type hints
def search_cards(query: str, limit: int = 50) -> list[Card]:
    pass

# Use pathlib for file paths
from pathlib import Path
data_dir = Path(__file__).parent / "data"

# Async for I/O operations
async def fetch_price(card_id: str) -> Decimal:
    pass

# Docstrings for public functions
def calculate_deck_value(deck: Deck) -> Decimal:
    """
    Calculate total market value of a deck.
    
    Args:
        deck: Deck object with card list
        
    Returns:
        Total USD value as Decimal
    """
    pass
```

### Imports Order
```python
# 1. Standard library
import asyncio
from pathlib import Path
from decimal import Decimal

# 2. Third-party
from PyQt6.QtWidgets import QMainWindow
import aiohttp
import pandas as pd

# 3. Local
from src.models import Card, Collection
from src.services import PriceService
```

### Error Handling
```python
# Always specific exceptions with context
try:
    card = await scryfall.get_card(name)
except aiohttp.ClientError as e:
    logger.error(f"Scryfall API error for '{name}': {e}")
    raise CardNotFoundError(f"Could not fetch card: {name}") from e
```

---

## GUI Rules (PyQt6)

### Theme Colors (MANDATORY)
```python
# Use these exact colors for consistency
BG_PRIMARY = "#1e1e1e"      # Main window background
BG_SECONDARY = "#252526"    # Panel backgrounds
BG_TERTIARY = "#2d2d30"     # Input fields
ACCENT_PRIMARY = "#5a4fcf"  # Buttons, links, focus
TEXT_PRIMARY = "#cccccc"    # Main text
TEXT_SECONDARY = "#999999"  # Muted text
SUCCESS = "#4caf50"
WARNING = "#ff9800"  
ERROR = "#f44336"
```

### Widget Patterns
```python
# Use worker threads for I/O
class DataLoader(QRunnable):
    signals = WorkerSignals()
    
    def run(self):
        data = load_heavy_data()  # Background thread
        self.signals.finished.emit(data)

# Never block main thread
# ❌ BAD
def on_button_click(self):
    data = requests.get(url)  # Freezes UI
    
# ✅ GOOD
def on_button_click(self):
    worker = DataLoader(url)
    worker.signals.finished.connect(self.on_data_loaded)
    QThreadPool.globalInstance().start(worker)
```

---

## Database Rules

### Schema Location
Primary schema defined in `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md`

### Key Tables
- `cards` - Scryfall card cache
- `collection_cards` - User inventory
- `decks` / `deck_cards` - Deck management
- `price_history` - Price tracking

### Query Patterns
```python
# Use parameterized queries (prevent SQL injection)
cursor.execute(
    "SELECT * FROM cards WHERE name LIKE ?",
    (f"%{search_term}%",)
)

# Use FTS5 for text search
cursor.execute(
    "SELECT * FROM cards_fts WHERE cards_fts MATCH ?",
    (search_term,)
)
```

---

## API Integration Rules

### Scryfall
- **Rate limit:** 10 requests/second (ENFORCE THIS)
- **Caching:** 24-hour cache for card data
- **Bulk data:** Use for initial imports

```python
# Rate limiting pattern
async with rate_limiter:
    response = await session.get(scryfall_url)
```

### TCGPlayer (if API key available)
- Real-time market prices
- Requires authentication

---

## File Handling Rules

### CSV Import
Must handle BOTH schemas:
- 17 columns (with Binder Name, Binder Type)
- 15 columns (without Binder columns)

```python
# Auto-detect and provide defaults
def detect_schema(df: pd.DataFrame) -> str:
    if "Binder Name" in df.columns:
        return "full"
    return "minimal"
```

### Backup Before Destructive Operations
```python
# Always backup before import/migration
backup_path = create_backup(data_file)
try:
    perform_operation()
except Exception:
    restore_from_backup(backup_path)
    raise
```

---

## Testing Requirements

### Minimum Coverage: 80%

### Test File Structure
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_importers.py
├── integration/
│   ├── test_scryfall_client.py
│   └── test_import_pipeline.py
└── gui/
    ├── test_main_window.py
    └── test_widgets.py
```

### Test Naming
```python
def test_<function>_<scenario>_<expected_result>():
    """Descriptive docstring."""
    pass

# Examples:
def test_import_csv_valid_file_returns_collection():
def test_import_csv_missing_columns_raises_error():
def test_search_empty_query_returns_all():
```

---

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(gui): add PyQt6 main window structure
fix(import): handle 15-column CSV schema
docs(readme): update installation instructions
test(services): add price calculation tests
```

---

## DO NOT

❌ Modify these files without explicit permission:
- `requirements.txt` (dependencies)
- `pyproject.toml` (project config)
- `.gitignore`
- Any file in `data/` (user's collection)

❌ Actions to avoid:
- Hard-coding Windows paths (use pathlib)
- Blocking main thread with I/O
- Skipping error handling
- Ignoring rate limits
- Creating duplicate utilities
- Breaking CSV import compatibility

---

## WHEN STUCK

1. Search project knowledge for relevant docs
2. Check existing code in `src/` for patterns
3. Review `PYQT6_BUILD_SPECIFICATION.md` for GUI tasks
4. Review `MTG_COLLECTION_MANAGER_DESIGN_PATTERN.md` for architecture
5. Ask user with specific context

---

## Quick Reference Commands

```bash
# Verify environment
python scripts/verify_setup.py

# Run tests
pytest tests/ -v

# Launch GUI
python run_gui.py

# Import CSV
python scripts/import_mobile.py <file.csv>

# Enrich with prices
python scripts/auto_enrich.py --backup
```

---

**Version:** 1.0
**Project:** CardForge/MyManaBox
**Owner:** Hunter @ StrayDog Syndications LLC
