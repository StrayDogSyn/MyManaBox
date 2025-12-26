# CardForge

## Professional Magic: The Gathering Collection Manager

A modern, async-first Python application for managing MTG card collections, building decks, tracking trades, and integrating with Claude Desktop via MCP.

## Features

- **Collection Management** - Import, track, and analyze your MTG collection
- **Deck Building** - Create and manage Commander/Standard decks with buy lists
- **Price Tracking** - Real-time pricing from Scryfall API
- **Smart Search** - Full-text search with color, type, and price filters
- **Buy/Sell Lists** - Track cards to acquire and duplicates to trade
- **MCP Integration** - Use with Claude Desktop for AI-assisted deck building
- **Rich CLI** - Beautiful terminal interface with progress bars and tables

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m cardforge.cli.main db init

# Import your collection (Moxfield CSV export)
python -m cardforge.cli.main collection import "path/to/export.csv"

# View collection stats
python -m cardforge.cli.main collection stats
```

## CLI Commands

### Collection

```bash
collection stats              # View collection statistics
collection search <query>     # Search your cards
collection import <csv>       # Import from CSV
collection export <path>      # Export collection
collection duplicates         # Find duplicate cards
```

### Cards

```bash
card search <query>           # Search all cards
card lookup <name>            # Get card details
```

### Decks

```bash
deck create <name>            # Create a new deck
deck list                     # List all decks
deck add-card <deck> <card>   # Add card to deck
deck missing <id>             # Show missing cards
deck buy-list <deck>          # Generate buy list
```

### Buy List

```bash
buylist show                  # View current buy list
buylist add <card>            # Add card to buy list
```

## Project Structure

```text
cardforge/
├── api/           # External API clients (Scryfall, TCGPlayer)
├── cli/           # Command-line interface
├── config/        # Configuration management
├── database/      # SQLite schema and migrations
├── models/        # Pydantic data models
├── repositories/  # Data access layer
├── services/      # Business logic
├── mcp/           # Claude Desktop MCP server
└── tests/         # Test suite
```

## Technology Stack

- **Python 3.11+** with async/await
- **SQLite** with FTS5 full-text search
- **Pydantic v2** for data validation
- **Click + Rich** for CLI
- **aiohttp/httpx** for async HTTP
- **MCP** for Claude Desktop integration

## Development

```bash
# Run tests
python -m pytest cardforge/tests/

# Type checking
python -m mypy cardforge/

# Format code
python -m black cardforge/
```

## Documentation

- [API Reference](docs/API.md) - Full CLI and Python API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design and patterns
- [MCP Integration](docs/MCP_INTEGRATION.md) - Claude Desktop setup guide

## License

MIT License - See LICENSE file for details.
