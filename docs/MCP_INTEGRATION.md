# MCP Integration Guide

CardForge includes a Model Context Protocol (MCP) server for integration with Claude Desktop, enabling AI-assisted deck building and collection management.

## Setup

### 1. Configure Claude Desktop

Add CardForge to your Claude Desktop configuration file:

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

### 2. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the CardForge MCP server.

## Available Tools

Once connected, Claude can use these tools:

### `search_cards`

Search for MTG cards with filters.

**Parameters:**

- `query` (string) - Search query
- `colors` (array) - Color filter (W, U, B, R, G)
- `type_filter` (string) - Card type filter
- `max_price` (number) - Maximum price
- `limit` (number) - Result limit

**Example prompt:** "Find me blue instant cards that draw cards under $5"

### `check_ownership`

Check if you own specific cards.

**Parameters:**

- `card_names` (array) - List of card names to check

**Example prompt:** "Do I own Sol Ring and Lightning Greaves?"

### `get_collection_stats`

Get collection overview and statistics.

**Example prompt:** "What's my collection worth?"

### `get_deck_cards`

Get all cards in a specific deck.

**Parameters:**

- `deck_id` (number) - Deck ID

### `get_deck_missing_cards`

Find cards needed for a deck that aren't owned.

**Parameters:**

- `deck_id` (number) - Deck ID

**Example prompt:** "What cards am I missing for my Kaalia deck?"

### `add_to_buy_list`

Add cards to the buy list.

**Parameters:**

- `card_name` (string) - Card name
- `quantity` (number) - Quantity needed
- `priority` (number) - Priority 1-5
- `max_price` (number) - Maximum price

### `suggest_deck_upgrades`

Get AI-suggested upgrades for a deck.

**Parameters:**

- `deck_id` (number) - Deck ID
- `budget` (number) - Budget for upgrades
- `strategy` (string) - Deck strategy focus

**Example prompt:** "Suggest $50 worth of upgrades for my Kaalia deck focusing on aggro"

### `find_duplicates`

Find duplicate cards worth trading/selling.

**Parameters:**

- `min_copies` (number) - Minimum copies to flag
- `min_value` (number) - Minimum card value

**Example prompt:** "What duplicates do I have worth more than $2?"

### `get_price_history`

Get price trends for a card.

**Parameters:**

- `card_name` (string) - Card name

### `compare_printings`

Compare prices across different printings.

**Parameters:**

- `card_name` (string) - Card name

**Example prompt:** "What's the cheapest printing of Smothering Tithe?"

## Example Conversations

### Deck Building

```text
You: I want to build a Kaalia of the Vast commander deck. What angels, demons, and dragons do I already own?

Claude: [Uses search_cards and check_ownership tools]
Based on your collection, you own:
- Angels: Aurelia, Akroma, Gisela...
- Demons: Master of Cruelties, Rune-Scarred Demon...
- Dragons: Balefire Dragon, Hellkite Tyrant...

You: Great! Add the missing staples to my buy list with a $100 budget.

Claude: [Uses add_to_buy_list tool]
Added to buy list:
- Avacyn, Angel of Hope ($25.00) - Priority 1
- Razaketh, the Foulblooded ($8.50) - Priority 2
...
```

### Collection Management

```text
You: I have duplicates I want to trade. Find any cards I have 5+ copies of worth over $1.

Claude: [Uses find_duplicates tool]
Found 12 cards with trade potential:
- Lightning Bolt (7 copies, $2.50 each)
- Sol Ring (6 copies, $1.25 each)
...
```

## Troubleshooting

### Server Not Loading

1. Check the path in `claude_desktop_config.json`
2. Ensure Python is in your PATH
3. Check Claude Desktop logs for errors

### Tools Not Appearing

1. Restart Claude Desktop after config changes
2. Verify the MCP server starts without errors:

```bash
python -m cardforge.mcp.server
```

### Database Errors

Initialize the database before using MCP:

```bash
python -m cardforge.cli.main db init
```
