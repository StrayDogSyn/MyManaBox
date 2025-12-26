"""
CardForge MCP Server
Claude Desktop integration for AI-powered MTG assistance
"""

import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

from cardforge.services import (
    CardService,
    CollectionService,
    DeckService,
    TradeService,
    PricingService,
)


# Initialize MCP server
server = Server("cardforge")

# Service instances
card_service = CardService()
collection_service = CollectionService()
deck_service = DeckService()
trade_service = TradeService()
pricing_service = PricingService()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available CardForge tools for Claude."""
    return [
        Tool(
            name="search_cards",
            description="Search MTG cards by name, colors, type, set, or price range",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Card name or text search"},
                    "colors": {"type": "array", "items": {"type": "string"}, "description": "Color filter (W,U,B,R,G)"},
                    "type_filter": {"type": "string", "description": "Card type (Creature, Instant, etc.)"},
                    "set_code": {"type": "string", "description": "Set code (e.g., MKM, ONE)"},
                    "max_price": {"type": "number", "description": "Maximum price in USD"},
                },
            },
        ),
        Tool(
            name="check_ownership",
            description="Check if a card is owned and how many copies",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_name": {"type": "string", "description": "Card name to check"},
                },
                "required": ["card_name"],
            },
        ),
        Tool(
            name="get_deck_missing_cards",
            description="Get list of cards needed to complete a deck",
            inputSchema={
                "type": "object",
                "properties": {
                    "deck_id": {"type": "integer", "description": "Deck ID"},
                },
                "required": ["deck_id"],
            },
        ),
        Tool(
            name="get_buy_list",
            description="Get current buy list with prices and priorities",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_to_buy_list",
            description="Add a card to the buy list",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_name": {"type": "string", "description": "Card name"},
                    "quantity": {"type": "integer", "description": "Quantity needed", "default": 1},
                    "priority": {"type": "integer", "description": "Priority 1-5 (1=highest)", "default": 3},
                    "max_price": {"type": "number", "description": "Maximum price willing to pay"},
                },
                "required": ["card_name"],
            },
        ),
        Tool(
            name="find_duplicates",
            description="Find duplicate cards that could be sold",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_copies": {"type": "integer", "description": "Minimum copies to consider duplicate", "default": 5},
                    "min_value": {"type": "number", "description": "Minimum card value in USD", "default": 0.50},
                },
            },
        ),
        Tool(
            name="get_collection_stats",
            description="Get collection statistics and total value",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_price_trend",
            description="Get price history and trend for a card",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_name": {"type": "string", "description": "Card name"},
                    "days": {"type": "integer", "description": "Days of history", "default": 30},
                },
                "required": ["card_name"],
            },
        ),
        Tool(
            name="suggest_deck_upgrades",
            description="Analyze deck and suggest card upgrades based on budget",
            inputSchema={
                "type": "object",
                "properties": {
                    "deck_id": {"type": "integer", "description": "Deck ID to analyze"},
                    "budget": {"type": "number", "description": "Budget for upgrades in USD"},
                    "focus": {"type": "string", "description": "Focus area: ramp, removal, card_draw, wincon"},
                },
                "required": ["deck_id"],
            },
        ),
        Tool(
            name="optimize_buy_list",
            description="Optimize buy list by finding best prices across sources",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool calls from Claude."""
    
    if name == "search_cards":
        cards = await card_service.search(
            query=arguments.get("query"),
            colors=arguments.get("colors"),
            type_filter=arguments.get("type_filter"),
            set_code=arguments.get("set_code"),
            max_price=arguments.get("max_price"),
            limit=20,
        )
        result = [{"name": c.name, "set": c.set_code, "price": str(c.prices.usd) if c.prices else "N/A"} for c in cards]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "check_ownership":
        info = await collection_service.check_ownership(arguments["card_name"])
        return [TextContent(type="text", text=json.dumps({
            "card_name": info.card_name,
            "total_owned": info.total_quantity,
            "by_condition": info.by_condition,
            "by_foil": info.by_foil,
            "total_value": str(info.total_value),
        }, indent=2))]
    
    elif name == "get_deck_missing_cards":
        missing = await deck_service.get_missing_cards(arguments["deck_id"])
        result = [{"name": m.card_name, "needed": m.quantity_needed, "price": str(m.current_price)} for m in missing]
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_buy_list":
        items = await trade_service.get_buy_list()
        summary = await trade_service.get_buy_list_summary()
        return [TextContent(type="text", text=json.dumps({
            "total_items": summary.total_items,
            "total_cost": str(summary.total_cost),
            "items": [{"card": i.card_name, "priority": i.priority, "price": str(i.best_price)} for i in items[:20]],
        }, indent=2))]
    
    elif name == "add_to_buy_list":
        item = await trade_service.add_to_buy_list(
            card_name=arguments["card_name"],
            quantity=arguments.get("quantity", 1),
            priority=arguments.get("priority", 3),
            max_price=arguments.get("max_price"),
        )
        return [TextContent(type="text", text=f"Added {arguments['card_name']} to buy list" if item else "Card not found")]
    
    elif name == "find_duplicates":
        duplicates = await collection_service.find_duplicates(
            min_copies=arguments.get("min_copies", 5),
            min_value=arguments.get("min_value", 0.50),
        )
        return [TextContent(type="text", text=json.dumps(duplicates[:20], indent=2))]
    
    elif name == "get_collection_stats":
        collection = await collection_service.get_or_create_default()
        stats = await collection_service.get_stats(collection.id)
        return [TextContent(type="text", text=json.dumps({
            "unique_cards": stats.unique_cards,
            "total_cards": stats.total_cards,
            "total_value": str(stats.total_value),
            "foil_count": stats.foil_count,
        }, indent=2))]
    
    elif name == "get_price_trend":
        card = await card_service.get_by_name(arguments["card_name"])
        if card:
            trend = await pricing_service.get_price_trend(card.id, arguments.get("days", 30))
            return [TextContent(type="text", text=json.dumps(trend, indent=2))]
        return [TextContent(type="text", text="Card not found")]
    
    elif name == "suggest_deck_upgrades":
        # AI-assisted deck analysis
        deck = await deck_service.get_deck(arguments["deck_id"])
        if not deck:
            return [TextContent(type="text", text="Deck not found")]
        
        # Get current deck composition for Claude to analyze
        cards = [{"name": c.card.name, "category": c.category, "cmc": c.card.cmc} for c in deck.cards if c.card]
        return [TextContent(type="text", text=json.dumps({
            "deck_name": deck.name,
            "format": deck.format,
            "card_count": len(cards),
            "cards": cards,
            "budget": arguments.get("budget"),
            "focus": arguments.get("focus"),
        }, indent=2))]
    
    elif name == "optimize_buy_list":
        items = await trade_service.get_buy_list()
        # Return data for Claude to analyze and optimize
        return [TextContent(type="text", text=json.dumps({
            "items": [{"name": i.card_name, "qty": i.quantity_needed, "best_price": str(i.best_price)} for i in items],
            "instruction": "Analyze and group by vendor for optimal shipping",
        }, indent=2))]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="cardforge://collection/stats",
            name="Collection Statistics",
            description="Current collection stats and value",
        ),
        Resource(
            uri="cardforge://buylist/summary",
            name="Buy List Summary",
            description="Current buy list status",
        ),
    ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
