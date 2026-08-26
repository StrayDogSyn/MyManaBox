# CardForge Project Structure

This document provides an overview of the CardForge project structure and organization.

## Root Directory

```
MyManaBox/
├── cardforge/              # Main application package
├── docs/                   # Documentation (organized by type)
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── data/                   # Application data (gitignored)
├── config/                 # Configuration files
├── assets/                 # Static assets (images, screenshots)
├── .github/                # GitHub workflows and templates
├── .venv/                  # Virtual environment (gitignored)
├── README.md              # Project overview
├── LICENSE                # Unlicense
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Python project configuration
├── pytest.ini             # Pytest configuration
├── docker-compose.yml     # Docker compose configuration
├── Dockerfile             # Docker container definition
└── verify_integration.py  # Integration verification script
```

## Documentation Structure (`docs/`)

```
docs/
├── README.md                    # Documentation index and navigation
│
├── guides/                      # User guides
│   ├── COLLECTION_INDEX.md
│   ├── COLLECTION_QUICK_START.md
│   ├── GUI_GUIDE.md
│   ├── GUI_QUICKSTART.md
│   └── MCP_INTEGRATION.md
│
├── development/                 # Developer documentation
│   ├── ENVIRONMENT_VALIDATION.md
│   ├── PARALLEL_DEVELOPMENT.md
│   ├── PHASE_2_DEVELOPMENT_GUIDE.md
│   ├── PROGRESS.md
│   ├── PYQT6_GUI_GUIDE.md
│   ├── PYQT6_QUICKSTART.md
│   └── VS_CODE_QUICK_REFERENCE.md
│
├── architecture/                # Architecture documentation
├── api/                         # API documentation
├── cardforge_ai/                # AI system documentation
├── archive/                     # Archived/deprecated docs
│
├── IMPORT_EXPORT_GUIDE.md
├── integration_testing.md
└── PROMPT_1_5_SPECIFICATION.md
```

## Application Package (`cardforge/`)

```
cardforge/
├── __init__.py
├── __main__.py              # Main entry point
├── exceptions.py            # Custom exceptions
│
├── api/                     # External API clients
│   ├── base_client.py
│   ├── scryfall_client.py
│   ├── tcgplayer_client.py
│   ├── moxfield_client.py
│   └── google_drive_client.py
│
├── ai/                      # AI/LLM integration
│   ├── ollama_client.py
│   └── orchestration.py
│
├── automation/              # Automation tasks
│   ├── daily_sync.py
│   ├── price_updater.py
│   └── weekly_report.py
│
├── cli/                     # Command-line interface
│   └── main.py
│
├── config/                  # Configuration management
│   ├── settings.py
│   └── validators.py
│
├── database/                # Database layer
│   ├── connection.py
│   ├── schema.sqlite.sql
│   ├── schema.hardened.sql
│   └── migrations/
│
├── exporters/               # Data export modules
│   ├── csv_exporter.py
│   ├── moxfield_exporter.py
│   └── archidekt_exporter.py
│
├── gui/                     # Tkinter GUI (legacy)
│   ├── app.py
│   ├── panels.py
│   ├── widgets.py
│   └── theme.py
│
├── qt_gui/                  # PyQt6 GUI (current)
│   ├── app.py
│   ├── main_window.py
│   ├── panels.py
│   ├── widgets/
│   └── theme.py
│
├── importers/               # Data import modules
│   ├── csv_importer.py
│   └── manabox_importer.py
│
├── mcp/                     # Model Context Protocol server
│   └── server.py
│
├── models/                  # Pydantic data models
│   ├── base.py
│   ├── card.py
│   ├── collection.py
│   ├── deck.py
│   ├── trade.py
│   ├── enums.py
│   └── sync.py
│
├── repositories/            # Data access layer
│   ├── base_repository.py
│   ├── card_repository.py
│   ├── collection_repository.py
│   ├── deck_repository.py
│   ├── trade_repository.py
│   └── price_repository.py
│
├── services/                # Business logic layer
│   ├── card_service.py
│   ├── collection_service.py
│   ├── deck_service.py
│   ├── pricing_service.py
│   ├── sync_service.py
│   ├── trade_service.py
│   ├── integration_service.py
│   └── ai/                 # AI-powered services
│       ├── base_agent.py
│       ├── orchestrator.py
│       ├── model_selection.py
│       └── agents/
│           ├── router.py
│           ├── deck_optimizer.py
│           ├── collection_manager.py
│           ├── price_analyzer.py
│           └── ...
│
├── types/                   # Type definitions
│   └── agents.py
│
└── utils/                   # Utility modules
    └── monitoring.py
```

## Test Suite (`tests/`)

```
tests/
├── conftest.py              # Pytest configuration and fixtures
│
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_repositories.py
│   └── test_services.py
│
└── integration/             # Integration tests
    ├── test_collection_integration.py
    ├── test_import_workflow.py
    └── test_mcp_tools.py
```

## Scripts (`scripts/`)

```
scripts/
├── run_gui.py              # Launch Tkinter GUI
├── run_qt_gui.py           # Launch PyQt6 GUI
└── ...                     # Other utility scripts
```

## Data Directory (`data/`)

Runtime data directory (not tracked in git):

```
data/
├── cardforge.db            # Main SQLite database
├── cardforge.log           # Application logs
├── cache/                  # API response cache
├── backups/                # Database backups
├── exports/                # Exported files
└── imports/                # Files for import
```

## Configuration (`config/`)

```
config/
├── claude_desktop_config.json    # Claude MCP configuration example
└── settings.json                 # Application settings
```

## Key Files

- **README.md**: Project overview, features, and quick start guide
- **LICENSE**: Unlicense (public domain dedication)
- **requirements.txt**: Python package dependencies
- **pyproject.toml**: Python project metadata and build configuration
- **pytest.ini**: Pytest configuration (coverage, markers, etc.)
- **docker-compose.yml**: Docker container orchestration
- **Dockerfile**: Docker image definition
- **verify_integration.py**: Integration test verification script
- **.editorconfig**: Editor configuration for consistent formatting
- **.gitignore**: Git ignore patterns

## Special Directories

### `.github/`
GitHub-specific files:
- Workflows (CI/CD)
- Issue templates
- Pull request templates

### `.vscode/`
VS Code workspace settings and launch configurations

### `.agents/` and `.trae/`
AI agent system directories (TRAE autonomous development system)

### `htmlcov/`
Code coverage HTML reports (generated by pytest-cov)

### `assets/screenshots/`
Application screenshots for documentation

## Navigation Tips

1. **Start with**: [README.md](../README.md) for project overview
2. **User guides**: See [docs/guides/](guides/)
3. **Development**: See [docs/development/](development/)
4. **Architecture**: See [docs/architecture/](architecture/)
5. **API reference**: See [docs/api/](api/)

## Quick Access

- 📖 [Documentation Index](README.md)
- 🏗️ [Architecture Overview](architecture/)
- 🧪 [Integration Testing](integration_testing.md)
- 🚀 [Collection Quick Start](guides/COLLECTION_QUICK_START.md)
- 💻 [PyQt6 Development](development/PYQT6_QUICKSTART.md)

---

**Last Updated**: January 12, 2026
