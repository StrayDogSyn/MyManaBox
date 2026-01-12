"""
CardForge CLI
Rich terminal interface
"""

import asyncio
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from decimal import Decimal

console = Console()


def async_command(f):
    """Decorator to run async click commands."""
    import functools
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@click.group()
@click.version_option(version="1.0.0", prog_name="CardForge")
def cli():
    """CardForge - MTG Collection Manager"""
    pass


# =====================
# Card Commands
# =====================

@cli.group()
def card():
    """Card search and lookup commands."""
    pass


@card.command("search")
@click.argument("query")
@click.option("--type", "-t", "card_type", help="Filter by type (creature, instant, etc.)")
@click.option("--color", "-c", "colors", help="Filter by color (W, U, B, R, G)")
@click.option("--set", "-s", "set_code", help="Filter by set code")
@click.option("--limit", "-l", default=20, help="Max results")
@async_command
async def card_search(query: str, card_type: str, colors: str, set_code: str, limit: int):
    """Search all cards in database."""
    from cardforge.services import CardService
    svc = CardService()
    
    color_list = colors.upper().split(',') if colors else None
    
    cards = await svc.search(
        query=query, 
        colors=color_list,
        set_code=set_code,
        type_filter=card_type,
        limit=limit
    )
    
    table = Table(title=f"Card Search: {query}")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Set", style="yellow")
    table.add_column("Price", style="green")
    
    for c in cards:
        price = f"${c.prices.usd}" if c.prices and c.prices.usd else "N/A"
        type_short = (c.type_line or "")[:30]
        table.add_row(c.name, type_short, (c.set_code or "").upper(), price)
    
    console.print(table)
    console.print(f"\n[dim]Found {len(cards)} cards[/dim]")


@card.command("lookup")
@click.argument("name")
@click.option("--set", "-s", "set_code", help="Specific set code")
@async_command
async def card_lookup(name: str, set_code: str):
    """Look up a specific card by name."""
    from cardforge.services import CardService
    from cardforge.api import ScryfallClient
    
    svc = CardService()
    
    # Try local first
    card = await svc.get_by_name(name, set_code)
    
    # Fetch from Scryfall if not found
    if not card:
        console.print("[dim]Not in local DB, fetching from Scryfall...[/dim]")
        card = await svc.fetch_from_scryfall(name, set_code)
    
    if not card:
        console.print(f"[red]Card not found: {name}[/red]")
        return
    
    # Display card info
    panel_content = f"""[bold cyan]{card.name}[/bold cyan]
{card.mana_cost or ''}  •  {(card.type_line or '')}

[italic]{card.oracle_text or ''}[/italic]

[dim]Set: {(card.set_code or '').upper()}  •  Rarity: {card.rarity or 'unknown'}[/dim]
[green]Price: ${card.prices.usd if card.prices and card.prices.usd else 'N/A'}[/green]"""
    
    console.print(Panel(panel_content, title="Card Details"))


# =====================
# Collection Commands
# =====================

@cli.group()
def collection():
    """Collection management commands."""
    pass


@collection.command("stats")
@async_command
async def collection_stats():
    """Show collection statistics."""
    from cardforge.services import CollectionService
    svc = CollectionService()
    
    coll = await svc.get_or_create_default()
    stats = await svc.get_stats(coll.id)
    
    table = Table(title="Collection Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Unique Cards", str(stats.unique_cards))
    table.add_row("Total Cards", str(stats.total_cards))
    table.add_row("Total Value", f"${stats.total_value:,.2f}")
    table.add_row("Foil Count", str(stats.foil_count))
    table.add_row("Unique Sets", str(stats.unique_sets))
    
    console.print(table)


@collection.command("add")
@click.argument("card_name")
@click.option("--quantity", "-q", default=1, help="Quantity to add")
@click.option("--foil", is_flag=True, help="Foil card")
@click.option("--condition", "-c", default="NM", help="Card condition")
@async_command
async def collection_add(card_name: str, quantity: int, foil: bool, condition: str):
    """Add a card to collection."""
    from cardforge.services import CollectionService
    svc = CollectionService()
    
    foil_type = "foil" if foil else "normal"
    result = await svc.add_card(card_name, quantity, foil_type, condition)
    
    if result:
        console.print(f"[green]Added {quantity}x {card_name}[/green]")
    else:
        console.print(f"[red]Card not found: {card_name}[/red]")


@collection.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=20, help="Max results")
@async_command
async def collection_search(query: str, limit: int):
    """Search collection."""
    from cardforge.services import CardService
    svc = CardService()
    
    cards = await svc.search(query=query, limit=limit)
    
    table = Table(title=f"Search: {query}")
    table.add_column("Name", style="cyan")
    table.add_column("Set", style="yellow")
    table.add_column("Price", style="green")
    
    for card in cards:
        price = f"${card.prices.usd}" if card.prices and card.prices.usd else "N/A"
        table.add_row(card.name, card.set_code.upper(), price)
    
    console.print(table)


@collection.command("duplicates")
@click.option("--min-copies", default=5, help="Minimum copies")
@click.option("--min-value", default=0.50, help="Minimum value")
@async_command
async def collection_duplicates(min_copies: int, min_value: float):
    """Find duplicate cards."""
    from cardforge.services import CollectionService
    svc = CollectionService()
    
    dups = await svc.find_duplicates(min_copies, Decimal(str(min_value)))
    
    table = Table(title="Duplicate Cards")
    table.add_column("Name", style="cyan")
    table.add_column("Copies", style="yellow")
    table.add_column("Value", style="green")
    
    for d in dups[:20]:
        table.add_row(d['name'], str(d['total_copies']), f"${d['highest_price']}")
    
    console.print(table)


@collection.command("import")
@click.argument("csv_path", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(['merge', 'replace']), default='merge', help="Import mode")
@async_command
async def collection_import(csv_path: str, mode: str):
    """Import collection from CSV (ManaBox/Moxfield format)."""
    import csv
    from pathlib import Path
    from cardforge.database import init_database, get_connection
    from cardforge.services import CollectionService, CardService
    from cardforge.repositories import CardRepository
    from cardforge.models import Card
    
    # Initialize database if needed
    await init_database()
    
    coll_svc = CollectionService()
    card_svc = CardService()
    card_repo = CardRepository()
    collection = await coll_svc.get_or_create_default()

    # If replace mode, clear existing entries in default collection
    if mode == 'replace':
        async with get_connection() as conn:
            await conn.execute("DELETE FROM collection_cards WHERE collection_id = ?", (collection.id,))
            await conn.commit()
        console.print(f"[yellow]Cleared existing collection entries (mode=replace).[/yellow]")
    
    csv_file = Path(csv_path)
    console.print(f"[cyan]Importing from {csv_file.name}...[/cyan]")
    
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    console.print(f"Found {len(rows)} card entries")
    
    imported = 0
    skipped = 0
    fetched = 0
    errors = []
    error_msg = ""
    
    with Progress(console=console) as progress:
        task = progress.add_task("[green]Importing...", total=len(rows))
        
        for row in rows:
            # Handle different CSV formats (ManaBox, Moxfield, etc.)
            name = (row.get('Name') or row.get('name') or row.get('Card Name') or 
                    row.get('card_name') or row.get('Card') or '')
            quantity = int(row.get('Count') or row.get('Quantity') or row.get('quantity') or 
                          row.get('Qty') or 1)
            set_code = (row.get('Edition') or row.get('Set Code') or row.get('set_code') or 
                       row.get('Set') or row.get('set') or '').lower()
            foil_raw = row.get('Foil') or row.get('foil') or row.get('Finish') or ''
            condition = row.get('Condition') or row.get('condition') or 'NM'
            
            # Normalize condition
            condition = condition.replace('Near Mint', 'NM').replace('Lightly Played', 'LP').replace('Moderately Played', 'MP')
            if condition not in ['NM', 'LP', 'MP', 'HP', 'DMG']:
                condition = 'NM'
            
            if not name:
                skipped += 1
                progress.update(task, advance=1)
                continue
            
            foil = 'foil' if foil_raw.lower() in ['foil', 'yes', 'true', 'f', 'etched'] else 'normal'
            
            # Check if card exists in DB
            card = await card_repo.get_by_name(name, set_code if set_code else None)
            
            if not card:
                # Fetch from Scryfall via CardService (handles set creation)
                try:
                    card = await card_svc.fetch_from_scryfall(name, set_code if set_code else None)
                    if card:
                        fetched += 1
                    else:
                        # Try fuzzy match
                        card = await card_svc.fetch_from_scryfall(name, None)
                        if card:
                            fetched += 1
                except Exception as e:
                    errors.append(f"{name}: {str(e)}")
                    skipped += 1
                    progress.update(task, advance=1)
                    continue
                
                if not card:
                    skipped += 1
                    progress.update(task, advance=1)
                    continue
            
            # Add to collection
            try:
                result = await coll_svc.add_card(
                    card_name=card.name,
                    quantity=quantity,
                    foil=foil,
                    condition=condition,
                    set_code=card.set_code,
                )
                
                if result:
                    imported += 1
                else:
                    skipped += 1
            except Exception as e:
                errors.append(f"{name} (add): {str(e)}")
                skipped += 1
            
            progress.update(task, advance=1)
    if errors and len(errors) <= 5:
        error_msg = f"\n[red]Errors: {chr(10).join(errors)}[/red]"
    elif errors:
        error_msg = f"\n[red]First 5 errors: {chr(10).join(errors[:5])}...[/red]"
    
    console.print(Panel(
        f"[green]Imported: {imported} cards[/green]\n"
        f"[cyan]Fetched from Scryfall: {fetched} new cards[/cyan]\n"
        f"[yellow]Skipped: {skipped} cards[/yellow]" + error_msg,
        title="Import Complete"
    ))


@collection.command("export")
@click.argument("output_path", type=click.Path())
@click.option("--format", "fmt", type=click.Choice(['csv', 'json']), default='csv')
@async_command
async def collection_export(output_path: str, fmt: str):
    """Export collection to CSV or JSON."""
    from cardforge.services import SyncService
    import csv
    import json
    
    svc = SyncService()
    
    with console.status("Exporting collection..."):
        data = await svc.export_collection_json()
    
    if fmt == 'json':
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'quantity', 'set_code', 'foil', 'condition'])
            writer.writeheader()
            for card in data.get('cards', []):
                writer.writerow({
                    'name': card.get('name'),
                    'quantity': card.get('quantity'),
                    'set_code': card.get('set_code'),
                    'foil': card.get('foil'),
                    'condition': card.get('condition'),
                })
    
    console.print(f"[green]Exported to {output_path}[/green]")


# =====================
# Deck Commands
# =====================

@cli.group()
def deck():
    """Deck management commands."""
    pass


@deck.command("create")
@click.argument("name")
@click.option("--format", "-f", "fmt", default="commander", help="Deck format")
@click.option("--commander", "-c", help="Commander card name")
@click.option("--description", "-d", help="Deck description")
@async_command
async def deck_create(name: str, fmt: str, commander: str, description: str):
    """Create a new deck."""
    from cardforge.services import DeckService
    from cardforge.database import init_database
    
    await init_database()
    svc = DeckService()
    
    deck = await svc.create_deck(
        name=name,
        format=fmt,
        description=description,
        commander_name=commander,
    )
    
    console.print(f"[green]Created deck: {deck.name} (ID: {deck.id})[/green]")
    if commander:
        console.print(f"[cyan]Commander: {commander}[/cyan]")


@deck.command("list")
@async_command
async def deck_list():
    """List all decks."""
    from cardforge.repositories import DeckRepository
    from cardforge.database import init_database
    
    await init_database()
    repo = DeckRepository()
    
    decks = await repo.get_all(limit=50)
    
    if not decks:
        console.print("[yellow]No decks found. Create one with 'deck create'[/yellow]")
        return
    
    table = Table(title="Decks")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Format", style="yellow")
    table.add_column("Cards", style="green")
    
    for d in decks:
        table.add_row(str(d.id), d.name, d.format, str(d.card_count or 0))
    
    console.print(table)


@deck.command("missing")
@click.argument("deck_id", type=int)
@async_command
async def deck_missing(deck_id: int):
    """Show cards missing from a deck."""
    from cardforge.services import DeckService
    svc = DeckService()
    
    missing = await svc.get_missing_cards(deck_id)
    
    table = Table(title="Missing Cards")
    table.add_column("Name", style="cyan")
    table.add_column("Needed", style="yellow")
    table.add_column("Price", style="green")
    
    total = Decimal('0')
    for m in missing:
        price = m.current_price or Decimal('0')
        total += price * m.quantity_needed
        table.add_row(m.card_name, str(m.quantity_needed), f"${price}")
    
    console.print(table)
    console.print(f"\n[bold]Total cost: ${total:,.2f}[/bold]")


@deck.command("import")
@click.argument("moxfield_url")
@async_command
async def deck_import(moxfield_url: str):
    """Import deck from Moxfield."""
    from cardforge.services import DeckService
    svc = DeckService()
    
    with console.status("Importing from Moxfield..."):
        deck = await svc.import_from_moxfield(moxfield_url)
    
    if deck:
        console.print(f"[green]Imported: {deck.name}[/green]")
    else:
        console.print("[red]Import failed[/red]")


@deck.command("buy-list")
@click.argument("deck_name_or_id")
@click.option("--budget", "-b", type=float, help="Budget limit in USD")
@click.option("--priority", "-p", type=int, default=2, help="Priority level (1-5)")
@async_command
async def deck_buy_list(deck_name_or_id: str, budget: float, priority: int):
    """Generate buy list for missing deck cards."""
    from cardforge.services import DeckService, TradeService
    from cardforge.repositories import DeckRepository
    from cardforge.database import init_database
    
    await init_database()
    deck_svc = DeckService()
    trade_svc = TradeService()
    deck_repo = DeckRepository()
    
    # Find deck by ID or name
    try:
        deck_id = int(deck_name_or_id)
        deck = await deck_repo.get(deck_id)
    except ValueError:
        deck = await deck_repo.get_by_name(deck_name_or_id)
    
    if not deck:
        console.print(f"[red]Deck not found: {deck_name_or_id}[/red]")
        return
    
    # Get missing cards
    missing = await deck_svc.get_missing_cards(deck.id)
    
    if not missing:
        console.print(f"[green]Deck '{deck.name}' is complete![/green]")
        return
    
    # Add to buy list with budget filtering
    added = 0
    total_cost = Decimal('0')
    budget_dec = Decimal(str(budget)) if budget else None
    
    table = Table(title=f"Buy List for {deck.name}")
    table.add_column("Card", style="cyan")
    table.add_column("Qty", style="yellow")
    table.add_column("Price", style="green")
    table.add_column("Status", style="magenta")
    
    for m in missing:
        price = m.current_price or Decimal('0')
        card_total = price * m.quantity_needed
        
        if budget_dec and (total_cost + card_total) > budget_dec:
            table.add_row(m.card_name, str(m.quantity_needed), f"${price}", "[yellow]Over budget[/yellow]")
            continue
        
        # Add to buy list
        await trade_svc.add_to_buy_list(
            card_name=m.card_name,
            quantity=m.quantity_needed,
            priority=priority,
            deck_id=deck.id,
            max_price=price * Decimal('1.2'),  # 20% margin
        )
        
        total_cost += card_total
        added += 1
        table.add_row(m.card_name, str(m.quantity_needed), f"${price}", "[green]Added[/green]")
    
    console.print(table)
    console.print(Panel(
        f"[green]Added {added} cards to buy list[/green]\n"
        f"[cyan]Estimated cost: ${total_cost:,.2f}[/cyan]"
        + (f"\n[yellow]Budget: ${budget:,.2f}[/yellow]" if budget else ""),
        title="Buy List Generated"
    ))


@deck.command("add-card")
@click.argument("deck_name_or_id")
@click.argument("card_name")
@click.option("--quantity", "-q", default=1)
@click.option("--sideboard", "-s", is_flag=True)
@click.option("--category", "-c", help="Category (ramp, removal, etc.)")
@async_command
async def deck_add_card(deck_name_or_id: str, card_name: str, quantity: int, sideboard: bool, category: str):
    """Add a card to a deck."""
    from cardforge.services import DeckService
    from cardforge.repositories import DeckRepository
    from cardforge.database import init_database
    
    await init_database()
    deck_svc = DeckService()
    deck_repo = DeckRepository()
    
    # Find deck
    try:
        deck_id = int(deck_name_or_id)
        deck = await deck_repo.get(deck_id)
    except ValueError:
        deck = await deck_repo.get_by_name(deck_name_or_id)
    
    if not deck:
        console.print(f"[red]Deck not found: {deck_name_or_id}[/red]")
        return
    
    result = await deck_svc.add_card(
        deck_id=deck.id,
        card_name=card_name,
        quantity=quantity,
        is_sideboard=sideboard,
        category=category,
    )
    
    if result:
        console.print(f"[green]Added {quantity}x {card_name} to {deck.name}[/green]")
    else:
        console.print(f"[red]Card not found: {card_name}[/red]")


# =====================
# Buy List Commands
# =====================

@cli.group()
def buylist():
    """Buy list management."""
    pass


@buylist.command("show")
@async_command
async def buylist_show():
    """Show current buy list."""
    from cardforge.services import TradeService
    svc = TradeService()
    
    items = await svc.get_buy_list()
    summary = await svc.get_buy_list_summary()
    
    table = Table(title="Buy List")
    table.add_column("Card", style="cyan")
    table.add_column("Qty", style="yellow")
    table.add_column("Priority", style="magenta")
    table.add_column("Price", style="green")
    
    for item in items[:30]:
        table.add_row(
            item.card_name or "Unknown",
            str(item.quantity_needed),
            str(item.priority),
            f"${item.best_price or 0}"
        )
    
    console.print(table)
    console.print(Panel(f"Total: {summary.total_items} items | ${summary.total_cost:,.2f}"))


@buylist.command("add")
@click.argument("card_name")
@click.option("--quantity", "-q", default=1)
@click.option("--priority", "-p", default=3, help="1-5, 1=highest")
@async_command
async def buylist_add(card_name: str, quantity: int, priority: int):
    """Add card to buy list."""
    from cardforge.services import TradeService
    svc = TradeService()
    
    result = await svc.add_to_buy_list(card_name, quantity, priority)
    if result:
        console.print(f"[green]Added {card_name} to buy list[/green]")
    else:
        console.print(f"[red]Card not found[/red]")


@buylist.command("generate")
@async_command
async def buylist_generate():
    """Generate buy list from deck needs."""
    from cardforge.services import TradeService
    svc = TradeService()
    
    with console.status("Analyzing decks..."):
        count = await svc.generate_buy_list_from_decks()
    
    console.print(f"[green]Added {count} cards to buy list[/green]")


# =====================
# Sync Commands
# =====================

@cli.group()
def sync():
    """Sync and backup commands."""
    pass


@sync.command("backup")
@async_command
async def sync_backup():
    """Backup collection to Google Drive."""
    from cardforge.services import SyncService
    svc = SyncService()
    
    with console.status("Backing up to Google Drive..."):
        file_id = await svc.backup_to_google_drive()
    
    if file_id:
        console.print(f"[green]Backup complete: {file_id}[/green]")
    else:
        console.print("[red]Backup failed - check credentials[/red]")


@sync.command("moxfield")
@async_command
async def sync_moxfield():
    """Sync decks from Moxfield."""
    from cardforge.services import SyncService
    svc = SyncService()
    
    with console.status("Syncing Moxfield decks..."):
        count = await svc.sync_moxfield_decks()
    
    console.print(f"[green]Synced {count} new decks[/green]")


# =====================
# Database Commands
# =====================

@cli.group()
def db():
    """Database commands."""
    pass


@db.command("init")
@async_command
async def db_init():
    """Initialize database."""
    from cardforge.database import init_database
    
    with console.status("Initializing database..."):
        await init_database()
    
    console.print("[green]Database initialized[/green]")


@db.command("sync-cards")
@click.argument("set_code")
@async_command
async def db_sync_cards(set_code: str):
    """Sync cards from Scryfall for a set."""
    from cardforge.services import CardService
    svc = CardService()
    
    with console.status(f"Syncing {set_code.upper()}..."):
        count = await svc.sync_set(set_code)
    
    console.print(f"[green]Synced {count} cards[/green]")


# =====================
# Agent Commands
# =====================

@cli.group()
def agent():
    """AI agent commands."""
    pass


@agent.command("list")
def agent_list():
    """List available AI agents."""
    from cardforge.services.ai.registry import AgentRegistry
    
    agents = AgentRegistry.list_agents()
    if not agents:
        console.print("[yellow]No agents registered.[/yellow]")
        return
        
    table = Table(title="Available AI Agents")
    table.add_column("ID", style="cyan")
    table.add_column("Status", style="green")
    
    for agent_id in agents:
        table.add_row(agent_id, "Active")
        
    console.print(table)


@agent.command("run")
@click.argument("agent_name")
@click.argument("task")
def agent_run(agent_name: str, task: str):
    """Run an AI agent task."""
    console.print(f"[yellow]Running agent {agent_name} on task: {task}[/yellow]")


# =====================
# Server Commands
# =====================

@cli.group()
def server():
    """Web/API server commands."""
    pass


@server.command("start")
@click.option("--port", default=8000, help="Port to listen on")
def server_start(port: int):
    """Start the CardForge server."""
    console.print(f"[green]Starting server on port {port}...[/green]")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
