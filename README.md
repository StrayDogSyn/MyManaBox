<div align="center">

# CardForge

### Professional Magic: The Gathering Collection Management Platform

A modern, async-first Python application for managing MTG card collections, building decks, tracking trades, and integrating with AI assistants via Model Context Protocol. Available as CLI, PyQt6 GUI, and MCP server.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-FTS5-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6+-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-Unlicense-blue?style=for-the-badge)](LICENSE)

[![Code Quality](https://img.shields.io/badge/code%20quality-maintained-success?style=flat-square)](https://github.com/StrayDogSyn/MyManaBox)
[![Type Safety](https://img.shields.io/badge/type%20safety-pydantic%20v2-E92063?style=flat-square)](https://pydantic.dev)
[![Development Status](https://img.shields.io/badge/status-beta-yellow?style=flat-square)](https://github.com/StrayDogSyn/MyManaBox)

---

[Features](#features) •
[Quick Start](#quick-start) •
[User Interfaces](#user-interfaces) •
[MCP Integration](#model-context-protocol-integration) •
[Architecture](#architecture) •
[Documentation](#documentation)

</div>

---

## CTD Python Advanced Submission -- Scryfall Card Lookup CLI

This project was submitted for the Code The Dream Python Advanced (Python 200) pre-work. The CLI entry point lives at the project root and uses the Scryfall API as its data source.

**API:** [Scryfall](https://scryfall.com/docs/api) -- free, no API key required. Same one-request-per-record pattern as PokeAPI (CTD Option 3).

### Module layout

| File | Responsibility |
|------|----------------|
| `api_client.py` | All network calls. `requests`-based, rate-limited, timeout-guarded. |
| `card_data.py` | Data transformation. No network, no printing. Converts raw Scryfall dicts to clean Python data. |
| `display.py` | Output formatting. Standard library only. No raw dict printing. |
| `main.py` | Orchestration. `argparse` CLI that calls the three modules above and nothing else. |

### CLI Setup

```bash
git clone https://github.com/StrayDogSyn/MyManaBox.git
cd MyManaBox
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install requests
```

`requests` is the only dependency for the CLI. The full `requirements.txt` covers the larger CardForge platform.

### Usage

```bash
python main.py lookup "lightning bolt"
python main.py lookup "sol ring"
python main.py compare "black lotus" "mox pearl"
python main.py search "t:goblin c:r"
```

### Example output

```text
  Lightning Bolt
  ----------------------
  Mana Cost      {R}
  Type           Instant
  Rarity         Common
  Set            Mystery Booster
  Released       2019-11-07
  Price (USD)    $0.25
  Artist         Christopher Moeller

  Lightning Bolt deals 3 damage to any target.
```

```text
  Sol Ring
  ----------------------
  Mana Cost      {1}
  Type           Artifact
  Rarity         Uncommon
  Set            Commander Masters
  Released       2023-08-04
  Price (USD)    $1.99
  Artist         Mike Bierek

  {T}: Add {C}{C}.
```

Note that Sol Ring has no P/T row -- it is not a creature, and the field is absent entirely in the Scryfall payload. The project handles this correctly rather than printing a placeholder.

### Error handling

| Scenario | Response |
|----------|----------|
| Empty or whitespace input | `Error: Card name cannot be empty.` -- no request is made |
| No card matches the name | `Error: No card found for "zzzzzzzz".` |
| Ambiguous fuzzy match | `Error: "jace" matched several cards. Try a more specific name...` |
| Network timeout | `Error: Scryfall did not respond within 10s. Check your connection.` |
| No internet connection | `Error: Could not reach Scryfall. Check your internet connection.` |

No stack traces reach the user. Non-zero exit code on failure, zero on success.

---

## Quick Start

### Option 1: Auto-Initialize Everything (Recommended)

**Windows - Double-click launcher:**
```bash
start_cardforge.bat
```

**Any OS - Use auto-launcher:**
```bash
# One-time setup (handles everything!)
python setup_wizard.py

# Daily use (auto-starts Ollama!)
python cardforge.py stats
python cardforge.py import data/collection.csv
python cardforge.py ai "What cards synergize with Kaalia?"
```

The launcher automatically:
- ✅ Starts Ollama if not running
- ✅ Initializes database
- ✅ Creates required directories
- ✅ Manages all dependencies

### Option 2: Full Manual Control

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Use CardForge
python -m cardforge.cli stats
```

**For detailed setup guide:** See [STREAMLINED_QUICKSTART.md](docs/STREAMLINED_QUICKSTART.md)

---

## Features

### Collection Management

- Import collections from Moxfield, ManaBox, and CSV formats
- Track card quantities, conditions, foil status, and variants
- Real-time collection valuation with market price integration
- Intelligent duplicate detection with trade value suggestions
- Multi-format support for collection organization

### Deck Building

- Support for Commander, Standard, Modern, and custom formats
- Inventory-aware deck construction with ownership tracking
- Automated buy list generation with budget constraints
- Card categorization by type (creatures, removal, ramp, card draw)
- Missing card analysis with pricing optimization

### Price Intelligence

- Live market data integration via Scryfall API
- Historical price tracking and trend analysis
- Cross-set printing comparison and optimization
- Price alert system for collection monitoring
- Budget-aware purchasing recommendations

### Advanced Search Capabilities

- Full-text search powered by SQLite FTS5
- Multi-criteria filtering (color, type, CMC, rarity, price)
- Oracle text and rules text search
- EDHREC rank integration for Commander staples
- Performance-optimized query execution

### Analytics and Reporting

- Comprehensive collection value breakdown
- Set completion tracking and gap analysis
- Investment performance metrics
- Rarity and color distribution statistics
- Export capabilities for external analysis

### AI-Powered Integration

- Claude Desktop integration via Model Context Protocol
- Natural language deck building assistance
- Context-aware card suggestions and recommendations
- Automated buy list optimization
- Conversational collection management

---

## Application Screenshots

<div align="center">

### PyQt6 Desktop Interface

<table>
<tr>
<td align="center">
<img src="assets/screenshots/splash.png" alt="CardForge Main Window" width="600" />
<br><em>Main window featuring collection browser and analytics dashboard</em>
</td>
</tr>
<tr>
<td align="center">
<img src="assets/screenshots/stable.png" alt="Collection Table" width="600" />
<br><em>Collection table with sortable columns, alternating row colors, and real-time search</em>
</td>
</tr>
<tr>
<td align="center">
<img src="assets/screenshots/success.png" alt="Card Details Panel" width="600" />
<br><em>Detailed card view displaying comprehensive card information and metadata</em>
</td>
</tr>
</table>

</div>

<details>
<summary><strong>Additional Screenshots</strong></summary>

| Screenshot | Description |
|------------|-------------|
| ![Analytics](assets/screenshots/qt_analytics.png) | Analytics dashboard with comprehensive collection statistics |
| ![Search](assets/screenshots/qt_search.png) | Real-time search interface with debounced filtering |
| ![Dark Theme](assets/screenshots/qt_dark_theme.png) | Dark theme implementation with custom styling |

</details>

---

## Quick Start

### System Requirements

- Python 3.9 or higher (3.11+ recommended)
- pip package manager
- 50MB available disk space
- Windows, macOS, or Linux operating system

### Installation

```bash
# Clone the repository
git clone https://github.com/StrayDogSyn/MyManaBox.git
cd MyManaBox

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -m cardforge.cli.main db init
```

### Launching the Application

```bash
# PyQt6 GUI (recommended)
python scripts/run_qt_gui.py

# Legacy GUI (deprecated)
python scripts/run_gui.py

# CLI interface
python -m cardforge.cli.main --help
```

### Import Your Collection

```bash
# Import from Moxfield CSV export
python -m cardforge.cli.main collection import "path/to/moxfield_export.csv"

# View collection statistics
python -m cardforge.cli.main collection stats

# Search your collection
python -m cardforge.cli.main collection search "lightning bolt"
```

<details>
<summary><strong>Example CLI Output</strong></summary>

```text
Collection Statistics

Overview:
  Unique Cards:     1,769
  Total Cards:      2,222
  Foil Cards:       127
  Unique Sets:      89

Value Summary:
  Estimated Total:  $1,284.96
  Average/Card:     $0.58
```

</details>

---

## User Interfaces

CardForge offers multiple interface options to suit different workflows and preferences.

### PyQt6 Desktop Application (Recommended)

The primary interface is a professional desktop application built with PyQt6, providing native performance and modern UI/UX design.

```bash
python run_qt_gui.py
```

**Key Features:**

- Native desktop application with platform-specific styling
- High-performance rendering with hardware acceleration
- Custom QSS theming system for visual customization
- Asynchronous operations with responsive UI threading
- Advanced table views with sorting and filtering
- Integrated card detail panels with image previews
- Real-time search with debounced input handling

For comprehensive documentation, see the [PyQt6 GUI Guide](docs/PYQT6_GUI_GUIDE.md).

### Tkinter GUI (Lightweight Alternative)

A lightweight alternative interface using Python's built-in Tkinter library, ideal for systems with limited resources or simpler use cases.

```bash
python run_gui.py
```

**Key Features:**

- Minimal dependencies with built-in Python support
- Real-time collection dashboard and statistics
- Advanced search and filtering capabilities
- Detailed card information views
- Price tracking and valuation displays

For detailed usage instructions, see the [Tkinter GUI Guide](docs/GUI_GUIDE.md).

### Command-Line Interface

CardForge provides a comprehensive command-line interface for power users, automation, and scripting workflows.

### Collection Commands

| Command | Description |
|---------|-------------|
| `collection stats` | Display collection statistics and value |
| `collection search <query>` | Search cards in your collection |
| `collection import <csv>` | Import from CSV (Moxfield/ManaBox) |
| `collection export <path>` | Export collection to CSV/JSON |
| `collection duplicates` | Find duplicate cards for trading |

### Card Commands

| Command | Description |
|---------|-------------|
| `card search <query>` | Search all cards in database |
| `card lookup <name>` | Get detailed card information |

### Deck Commands

| Command | Description |
|---------|-------------|
| `deck create <name>` | Create a new deck |
| `deck list` | List all your decks |
| `deck add-card <deck> <card>` | Add a card to a deck |
| `deck missing <id>` | Show cards you need |
| `deck buy-list <deck>` | Generate prioritized buy list |

### Buy List Commands

| Command | Description |
|---------|-------------|
| `buylist show` | Display current buy list |
| `buylist add <card>` | Add card to buy list |

<details>
<summary><strong>Command Reference Examples</strong></summary>

```bash
# Search for angels under $5
python -m cardforge.cli.main card search "angel" --type creature --color W --max-price 5.00

# Create a Commander deck
python -m cardforge.cli.main deck create "Kaalia Voltron" \
    --format commander \
    --commander "Kaalia of the Vast"

# Generate buy list with budget constraint
python -m cardforge.cli.main deck buy-list "Kaalia Voltron" --budget 50

# Find valuable duplicates for trading
python -m cardforge.cli.main collection duplicates --min-value 2.00

# Export collection to CSV
python -m cardforge.cli.main collection export --format csv --output collection.csv
```

</details>

---

## Model Context Protocol Integration

CardForge includes a Model Context Protocol (MCP) server implementation for seamless integration with Claude Desktop and other MCP-compatible AI assistants, enabling natural language collection management and deck building.

### Configuration

Add the following configuration to Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cardforge": {
      "command": "python",
      "args": ["-m", "cardforge.mcp.server"],
      "cwd": "C:/path/to/MyManaBox"
    }
  }
}
```

### Available MCP Tools

The CardForge MCP server exposes the following tools for AI-assisted operations:

| Tool | Description |
|------|-------------|
| `search_cards` | Search cards with advanced filtering options |
| `check_ownership` | Verify card ownership and quantities |
| `get_collection_stats` | Retrieve comprehensive collection statistics |
| `get_deck_missing_cards` | Analyze missing cards for deck completion |
| `add_to_buy_list` | Add cards to prioritized buy list |
| `suggest_deck_upgrades` | Generate AI-powered upgrade recommendations |
| `find_duplicates` | Identify tradeable duplicate cards |
| `compare_printings` | Compare prices across different set printings |

### Usage Example

```text
User: I want to build a Kaalia deck. What angels, demons, and dragons do I own?

Claude: Analyzing your collection...
        You own 12 angels including Aurelia and Gisela,
        8 demons including Rune-Scarred Demon,
        and 6 dragons including Balefire Dragon.

User: Add the missing staples to my buy list under $100 total.

Claude: Added 8 essential cards to your buy list:
        - Master of Cruelties ($12.50)
        - Dragon Tyrant ($8.75)
        [... 6 more cards ...]
        Total: $87.50
```

For complete MCP integration documentation, see [MCP Integration Guide](docs/MCP_INTEGRATION.md).

---

## Architecture

CardForge is built following clean architecture principles with clear separation of concerns and async-first design patterns.

### System Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Presentation Layer                          │
│    PyQt6 GUI    │    Tkinter GUI    │    CLI    │    MCP Server │
├──────────────────────────────────────────────────────────────────┤
│                        Service Layer                              │
│  CardService  │  CollectionService  │  DeckService  │  Trade     │
├──────────────────────────────────────────────────────────────────┤
│                      Repository Layer                             │
│           Async Data Access with Full-Text Search                │
├──────────────────────────────────────────────────────────────────┤
│                        Data Layer                                 │
│       SQLite (FTS5)    │    Scryfall API    │    TCGPlayer       │
└──────────────────────────────────────────────────────────────────┘
```

### Project Structure

```text
cardforge/
├── api/              External API clients (Scryfall, TCGPlayer, Moxfield)
├── cli/              Command-line interface implementation
├── config/           Configuration management and settings
├── database/         SQLite schema, migrations, and connection handling
├── exporters/        Data export modules (CSV, Archidekt, Moxfield)
├── gui/              Tkinter GUI implementation
├── importers/        Data import modules (CSV, ManaBox, Moxfield)
├── mcp/              Model Context Protocol server
├── models/           Pydantic data models and validation
├── qt_gui/           PyQt6 desktop application
├── repositories/     Data access layer with async operations
├── services/         Business logic and domain services
└── tests/            Test suite (unit and integration)
```

### Design Principles

- **Async-First:** All I/O operations use async/await patterns for responsive performance
- **Type Safety:** Comprehensive type hints with Pydantic v2 validation
- **Layered Architecture:** Clear separation between presentation, business logic, and data access
- **Repository Pattern:** Abstracted data access for testability and maintainability
- **Service Layer:** Encapsulated business logic independent of presentation
- **API Clients:** Modular external API integration with error handling

For detailed architectural documentation, see [Architecture Guide](docs/architecture/ARCHITECTURE.md).

---

## Technology Stack

### Core Technologies

<table>
<tr>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python" />
<br><strong>Python 3.9+</strong>
<br><sub>Async/Await</sub>
</td>
<td align="center" width="120">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/sqlite/sqlite-original.svg" width="48" height="48" alt="SQLite" />
<br><strong>SQLite</strong>
<br><sub>FTS5 Search</sub>
</td>
<td align="center" width="120">
<img src="https://avatars.githubusercontent.com/u/110818415?s=200&v=4" width="48" height="48" alt="Pydantic" />
<br><strong>Pydantic v2</strong>
<br><sub>Validation</sub>
</td>
<td align="center" width="120">
<img src="https://www.riverbankcomputing.com/static/images/logo.svg" width="48" height="48" alt="PyQt6" />
<br><strong>PyQt6</strong>
<br><sub>Desktop GUI</sub>
</td>
</tr>
</table>

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|----------|
| `PyQt6` | 6.6.0+ | Professional desktop GUI framework |
| `aiosqlite` | 0.19.0+ | Asynchronous SQLite database access |
| `aiohttp` | 3.9.0+ | Async HTTP client for API integration |
| `pydantic` | 2.0.0+ | Data validation and serialization |
| `pandas` | 2.0.0+ | Data manipulation and CSV processing |
| `requests` | 2.31.0+ | Synchronous HTTP client |
| `click` | Latest | CLI command framework |
| `rich` | Latest | Terminal formatting and styling |
| `mcp` | 0.1.0+ | Model Context Protocol implementation |

---

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory. See the [Documentation Index](docs/README.md) for a complete guide to all available documentation.

### Quick Links

| Document | Description |
|----------|-------------|
| [📚 Documentation Index](docs/README.md) | Complete documentation guide and navigation |
| [🚀 Collection Quick Start](docs/guides/COLLECTION_QUICK_START.md) | Get started with collection management |
| [🖥️ GUI Quick Start](docs/guides/GUI_QUICKSTART.md) | Quick guide to the graphical interface |
| [🎯 PyQt6 Quick Start](docs/development/PYQT6_QUICKSTART.md) | Setting up PyQt6 development |
| [🤖 MCP Integration](docs/guides/MCP_INTEGRATION.md) | Claude Desktop and AI assistant setup |
| [📊 Import/Export Guide](docs/IMPORT_EXPORT_GUIDE.md) | Importing and exporting your collection |

### Developer Resources

| Document | Description |
|----------|-------------|
| [🏗️ Phase 2 Development Guide](docs/development/PHASE_2_DEVELOPMENT_GUIDE.md) | Current development phase documentation |
| [🧪 Integration Testing](docs/integration_testing.md) | Testing the integration system |
| [💻 VS Code Quick Reference](docs/development/VS_CODE_QUICK_REFERENCE.md) | VS Code tips and shortcuts |

---

## Development

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install optional features
pip install -e ".[charts,mcp]"
```

### Testing

```bash
# Run test suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=cardforge --cov-report=html

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest -m "not slow" -v
```

### Code Quality

```bash
# Type checking
python -m mypy cardforge/

# Linting and formatting
python -m ruff check cardforge/
python -m ruff format cardforge/
```

### Building

```bash
# Build distribution packages
python -m build

# Install from source
pip install -e .
```

---

## Development Roadmap

### Current Phase: Beta (v2.0.0)

The project is currently in beta development with active feature implementation and refinement.

### Completed Features

- Core collection management system
- SQLite database with FTS5 full-text search
- Scryfall API integration for card data and pricing
- CSV import/export for Moxfield and ManaBox
- Command-line interface with comprehensive commands
- Tkinter GUI for lightweight desktop access
- PyQt6 professional desktop application
- Model Context Protocol server for AI integration
- Deck building with inventory tracking
- Buy list generation and management

### In Progress

- Enhanced price tracking and historical data
- Advanced analytics and reporting
- Performance optimizations for large collections
- Comprehensive test coverage expansion
- Documentation improvements

### Planned Features

- Web-based interface with REST API
- Mobile companion application
- Cloud synchronization and backup
- Trade matching system with other collectors
- Deck sharing and community features
- Price alert notifications
- Advanced deck statistics and analysis
- Integration with additional marketplaces
- Automated collection photography and cataloging

---

## Contributing

Contributions to CardForge are welcome and appreciated. This project follows standard open-source contribution practices.

### How to Contribute

1. Fork the repository on GitHub
2. Create a feature branch from `main`

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Implement your changes with appropriate tests
4. Ensure all tests pass and code quality checks succeed
5. Commit your changes with clear, descriptive messages

   ```bash
   git commit -m "Add feature: description of changes"
   ```

6. Push to your fork

   ```bash
   git push origin feature/your-feature-name
   ```

7. Submit a pull request to the main repository

### Contribution Guidelines

- Follow existing code style and conventions
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting
- Keep pull requests focused on a single feature or fix
- Write clear commit messages and PR descriptions

### Development Standards

- Python 3.9+ compatibility
- Type hints for all public APIs
- Async/await patterns for I/O operations
- Comprehensive error handling
- Unit and integration test coverage

---

## License

This project is released under the Unlicense, dedicating it to the public domain. See the [LICENSE](LICENSE) file for complete details.

---

## Acknowledgments

CardForge is built for and by the Magic: The Gathering community. Special thanks to:

- Scryfall for providing comprehensive card data and pricing APIs
- The Python open-source community for excellent libraries and tools
- Wizards of the Coast for creating Magic: The Gathering
- The Commander/EDH community for inspiration and feedback

---

<div align="center">

### Built for the Magic: The Gathering Community

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?style=flat-square&logo=github)](https://github.com/StrayDogSyn/MyManaBox)
[![Version](https://img.shields.io/badge/version-2.0.0-informational?style=flat-square)](https://github.com/StrayDogSyn/MyManaBox/releases)
[![Status](https://img.shields.io/badge/status-beta-yellow?style=flat-square)](https://github.com/StrayDogSyn/MyManaBox)

Magic: The Gathering and all associated trademarks are property of Wizards of the Coast LLC.

CardForge is an independent project and is not affiliated with, endorsed by, or sponsored by Wizards of the Coast.

</div>
