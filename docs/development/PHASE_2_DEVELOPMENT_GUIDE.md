# CardForge Phase 2 Development Guide
## Complete Roadmap: Cleanup + Testing + Analytics + Best Practices

**Created:** December 29, 2025  
**Status:** Ready for Windsurf Execution  
**Estimated Time:** 2-3 hours

---

## 📊 CURRENT STATE

| Component | Completion | Priority |
|-----------|------------|----------|
| Environment | ✅ 100% | - |
| PyQt6 GUI Core | ✅ 85% | - |
| Data Models & DB | ✅ 90% | - |
| Import/Export | ✅ 95% | - |
| MCP Integration | ✅ 100% | - |
| Automation | ✅ 90% | - |
| **Testing** | 🔴 **5%** | **CRITICAL** |
| Directory Structure | 🟡 60% | **HIGH** |
| Analytics GUI | 🟡 0% | MEDIUM |

**Overall: ~85% Complete** (up from ~60% in Phase 1)

---

## 🎯 PHASE 2 OBJECTIVES

1. **Directory Cleanup** - Organize project structure
2. **Test Suite Foundation** - Achieve 50%+ coverage
3. **Analytics Dashboard** - Implement visualization panel
4. **Automation Validation** - Test all Phase 1 automation

---

## 📋 EXECUTION PROMPTS

Copy these prompts directly into Windsurf. Execute in order.

### PROMPT 1: Directory Cleanup ⭐ PRIORITY 1

```
@workspace Execute comprehensive directory cleanup for CardForge.

## Task 1: Consolidate Agent Configurations
1. Create .agents/ directory at project root
2. Move all files from opus-instructions/ to .agents/
3. Check .claude/ for unique content and merge if needed
4. Delete empty opus-instructions/ and .claude/ directories
5. Keep .windsurfrules in project root (not in .agents/)

## Task 2: Create Config Directory
1. Create config/ directory
2. Move claude_desktop_config.json to config/
3. Create config/settings.json:

```json
{
  "version": "2.0.0",
  "database": {
    "path": "data/collections/main.db",
    "backup_count": 7,
    "auto_backup": true
  },
  "api": {
    "scryfall_rate_limit": 10,
    "cache_ttl_hours": 24
  },
  "import": {
    "watch_directory": "data/imports",
    "backup_before_import": true,
    "default_binder": "Default",
    "default_condition": "NM"
  },
  "export": {
    "output_directory": "data/exports",
    "formats": ["moxfield", "archidekt", "csv"]
  },
  "gui": {
    "theme": "dark",
    "default_size": [1440, 900],
    "min_size": [1280, 720]
  },
  "logging": {
    "level": "INFO",
    "file": "logs/cardforge.log",
    "max_size_mb": 10,
    "backup_count": 3
  }
}
```

## Task 3: Reorganize Documentation
```bash
mkdir -p docs/architecture docs/api docs/guides docs/development

# Move files
mv docs/ARCHITECTURE.md docs/architecture/ 2>/dev/null || true
mv docs/API.md docs/api/ 2>/dev/null || true
mv docs/GUI*.md docs/guides/ 2>/dev/null || true
mv docs/MCP_INTEGRATION.md docs/guides/ 2>/dev/null || true
mv docs/PYQT6*.md docs/development/ 2>/dev/null || true
mv docs/*SUMMARY*.md docs/development/ 2>/dev/null || true
mv docs/ENVIRONMENT_VALIDATION.md docs/development/ 2>/dev/null || true
```

## Task 4: Archive Legacy Code
```bash
git checkout -b archive/legacy-v1
git add archive/
git commit -m "Archive legacy code"
git checkout main
rm -rf archive/
echo "archive/" >> .gitignore
```

## Task 5: Deprecate Old Launcher
Update run_gui.py with deprecation warning:

```python
#!/usr/bin/env python3
"""DEPRECATED: Use run_qt_gui.py instead."""
import warnings
import sys

def main():
    warnings.warn(
        "\n" + "="*60 + "\n"
        "WARNING: run_gui.py is DEPRECATED\n"
        "Use 'python run_qt_gui.py' instead.\n"
        "Will be removed in CardForge v2.0\n"
        + "="*60,
        DeprecationWarning,
        stacklevel=2
    )
    print("Please use: python run_qt_gui.py")
    sys.exit(1)

if __name__ == "__main__":
    main()
```

## Validation
```bash
python run_qt_gui.py  # Should launch
python -c "import cardforge; print('OK')"
git status  # Check structure
```
```

---

### PROMPT 2: Test Suite Foundation ⭐ PRIORITY 2

```
@workspace Create comprehensive test suite for CardForge.

## Task 1: Create Test Structure
```bash
mkdir -p tests/unit tests/integration tests/gui
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/gui/__init__.py
```

## Task 2: Create tests/conftest.py
See full code in PHASE_2_DEVELOPMENT_GUIDE.md section "Test Suite Foundation"

## Task 3: Create Unit Tests
Create tests/unit/test_importers.py - See guide for full code

## Task 4: Create Integration Tests  
Create tests/integration/test_mcp_tools.py - See guide for full code

## Task 5: Update pyproject.toml
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["cardforge"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "raise NotImplementedError"]
```

## Task 6: Update requirements.txt
Add:
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-qt>=4.2.0
```

## Validation
```bash
pip install -r requirements.txt
pytest tests/ -v
pytest tests/ --cov=cardforge --cov-report=html
```

Target: 50%+ coverage initially, 80% final goal
```

---

### PROMPT 3: Analytics Dashboard

```
@workspace Implement analytics dashboard for CardForge PyQt6 GUI.

## Task 1: Create StatCard Widget
Create cardforge/qt_gui/widgets/stat_card.py
See PHASE_2_DEVELOPMENT_GUIDE.md for full implementation

## Task 2: Create Analytics Panel
Create cardforge/qt_gui/panels/analytics_panel.py
See guide for complete code with charts

## Task 3: Integrate into Main Window
Update cardforge/qt_gui/main_window.py:

```python
from .panels.analytics_panel import AnalyticsPanel

# In setup:
self.analytics_panel = AnalyticsPanel()
self.tab_widget.addTab(self.analytics_panel, "📊 Analytics")

def refresh_analytics(self):
    stats = self.collection_service.get_statistics()
    self.analytics_panel.update_stats(stats)
```

## Task 4: Update __init__ Files
Ensure widgets/panels are importable

## Validation
```bash
python run_qt_gui.py
# Navigate to Analytics tab
# Verify stats cards and charts display
```
```

---

### PROMPT 4: Automation Validation

```
@workspace Validate automation pipeline from Phase 1.

## Test Daily Sync
```bash
mkdir -p data/imports
echo 'Name,Set code,Quantity
Test Card,TST,1' > data/imports/test.csv
python -m cardforge.automation.daily_sync
```

## Test Weekly Report
```bash
python -m cardforge.automation.weekly_report
ls data/reports/  # Check for generated files
```

## Test Price Updater
```bash
python -m cardforge.automation.price_updater --card "Lightning Bolt"
```

## Validate MCP Server
```bash
python -c "from cardforge.mcp.server import server; print('MCP OK')"
```

## Configure Claude Desktop
Update config/claude_desktop_config.json:
```json
{
  "mcpServers": {
    "cardforge": {
      "command": "python",
      "args": ["-m", "cardforge.mcp.server"],
      "cwd": "C:\\Users\\EHunt\\Repos\\Projects\\MyManaBox"
    }
  }
}
```

Copy to: %APPDATA%\Claude\claude_desktop_config.json

## Checklist
- [ ] Daily sync runs without errors
- [ ] Backups created before import
- [ ] Weekly reports generate JSON + MD
- [ ] Price updater respects rate limits
- [ ] MCP server starts successfully
```

---

## 📚 REFERENCE: Test Suite Code

### conftest.py (Shared Fixtures)

```python
"""Pytest fixtures for CardForge test suite."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def sample_csv_17_columns():
    """Full schema CSV (17 columns)."""
    return '''Binder Name,Binder Type,Name,Set code,Collector number,Foil,Rarity,Quantity,ManaBox ID,Scryfall ID,Purchase price,Misprint,Altered,Condition,Language,Purchase price currency
Main,binder,Lightning Bolt,M21,199,normal,uncommon,4,12345,abc123,2.50,false,false,near_mint,en,USD
Trade,binder,Sol Ring,CMR,472,foil,uncommon,1,12346,def456,5.00,false,false,near_mint,en,USD'''

@pytest.fixture
def temp_csv_file_17(sample_csv_17_columns, tmp_path):
    """Create temp CSV with 17 columns."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(sample_csv_17_columns, encoding='utf-8')
    return csv_path

@pytest.fixture
def mock_scryfall():
    """Mocked Scryfall client."""
    mock = MagicMock()
    mock.get_card = AsyncMock(return_value={"name": "Lightning Bolt", "prices": {"usd": "2.50"}})
    return mock
```

### test_importers.py (Unit Tests)

```python
"""Unit tests for CSV import."""
import pytest

class TestCSVImporter:
    def test_detect_17_column_schema(self, temp_csv_file_17):
        from cardforge.importers.csv_importer import detect_csv_schema, CSVSchema
        schema = detect_csv_schema(temp_csv_file_17)
        assert schema == CSVSchema.FULL_17_COLUMN
    
    def test_import_preserves_binder_info(self, temp_csv_file_17):
        from cardforge.importers import CSVImporter
        importer = CSVImporter()
        stats = await importer.import_csv(temp_csv_file_17, collection_id=1)
        assert stats['imported'] == 2
```

---

## 🎨 REFERENCE: Analytics Dashboard Code

### StatCard Widget

```python
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont

class StatCard(QFrame):
    """Statistics display card."""
    
    def __init__(self, title: str, value: str = "0", icon: str = ""):
        super().__init__()
        self._setup_ui(title, value, icon)
    
    def _setup_ui(self, title, value, icon):
        layout = QVBoxLayout(self)
        
        # Icon + Title
        header = QLabel(f"{icon} {title}")
        layout.addWidget(header)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        self.value_label.setText(value)
```

### Analytics Panel

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from .widgets.stat_card import StatCard

class AnalyticsPanel(QWidget):
    """Analytics dashboard with stats and charts."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Stats row
        stats_row = QHBoxLayout()
        self.total_cards = StatCard("Total Cards", "0", "📦")
        self.total_value = StatCard("Value", "$0.00", "💰")
        stats_row.addWidget(self.total_cards)
        stats_row.addWidget(self.total_value)
        layout.addLayout(stats_row)
    
    def update_stats(self, stats: dict):
        self.total_cards.set_value(f"{stats['total_cards']:,}")
        self.total_value.set_value(f"${stats['total_value']:,.2f}")
```

---

## ✅ SUCCESS CRITERIA

After completing Phase 2:

| Metric | Target | Validation |
|--------|--------|------------|
| Directory Structure | Clean & Organized | `git status` shows logical layout |
| Test Coverage | 50%+ | `pytest --cov` report |
| Analytics GUI | Functional | Tab displays in run_qt_gui.py |
| Automation | Validated | All scripts run without errors |
| MCP Server | Connectable | Claude Desktop integration works |

---

## 🚀 EXECUTION CHECKLIST

- [ ] **Prompt 1:** Directory cleanup complete
- [ ] **Prompt 2:** Test suite created (50%+ coverage)
- [ ] **Prompt 3:** Analytics dashboard implemented
- [ ] **Prompt 4:** Automation validated
- [ ] All tests passing
- [ ] GUI launches successfully
- [ ] Documentation updated

---

## 📞 TROUBLESHOOTING

### Import Errors After Cleanup
```bash
# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall in development mode
pip install -e .
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -vv

# Run specific test
pytest tests/unit/test_importers.py::TestCSVImporter::test_detect_schema -v
```

### GUI Not Launching
```bash
# Check PyQt6 installation
python -c "from PyQt6.QtWidgets import QApplication; print('OK')"

# Check for errors
python run_qt_gui.py 2>&1 | tee gui_errors.log
```

---

**Ready for Windsurf execution. Estimated time: 2-3 hours**
