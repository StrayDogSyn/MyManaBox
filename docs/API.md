# CardForge API Reference

## CLI Commands

### Database Commands

#### `db init`

Initialize or reset the database schema.

```bash
python -m cardforge.cli.main db init
```

---

### Collection Commands

#### `collection stats`

Display collection statistics.

```bash
python -m cardforge.cli.main collection stats
```

**Output:**

- Unique cards count
- Total cards (with quantities)
- Total estimated value
- Foil count
- Sets represented

#### `collection search <query>`

Search cards in your collection.

```bash
python -m cardforge.cli.main collection search "lightning"
python -m cardforge.cli.main collection search "bolt" --limit 10
```

**Options:**

- `--limit, -l` - Maximum results (default: 20)

#### `collection import <csv_path>`

Import collection from CSV file.

```bash
python -m cardforge.cli.main collection import "./my_cards.csv"
python -m cardforge.cli.main collection import "./export.csv" --mode replace
```

**Options:**

- `--mode` - Import mode: `merge` (default) or `replace`

**Supported CSV formats:**

- Moxfield: `Count,Name,Edition,Condition,Foil`
- ManaBox: `Quantity,Name,Set Code,Condition,Foil`

#### `collection export <output_path>`

Export collection to file.

```bash
python -m cardforge.cli.main collection export "./backup.csv"
python -m cardforge.cli.main collection export "./backup.json" --format json
```

**Options:**

- `--format` - Output format: `csv` (default) or `json`

#### `collection duplicates`

Find duplicate cards worth selling.

```bash
python -m cardforge.cli.main collection duplicates
python -m cardforge.cli.main collection duplicates --min-copies 6 --min-value 1.00
```

**Options:**

- `--min-copies` - Minimum copies to flag (default: 5)
- `--min-value` - Minimum card value (default: $0.50)

---

### Card Commands

#### `card search <query>`

Search all cards in database.

```bash
python -m cardforge.cli.main card search "angel"
python -m cardforge.cli.main card search "draw" --type instant --color U
python -m cardforge.cli.main card search "mana" --set khm
```

**Options:**

- `--type, -t` - Filter by type (creature, instant, etc.)
- `--color, -c` - Filter by color (W, U, B, R, G)
- `--set, -s` - Filter by set code
- `--limit, -l` - Maximum results (default: 20)

#### `card lookup <name>`

Get detailed information about a specific card.

```bash
python -m cardforge.cli.main card lookup "Sol Ring"
python -m cardforge.cli.main card lookup "Lightning Bolt" --set m10
```

**Options:**

- `--set, -s` - Specific set code

---

### Deck Commands

#### `deck create <name>`

Create a new deck.

```bash
python -m cardforge.cli.main deck create "Kaalia Voltron"
python -m cardforge.cli.main deck create "Storm" --format commander --commander "Kess, Dissident Mage"
```

**Options:**

- `--format, -f` - Deck format (default: commander)
- `--commander, -c` - Commander card name
- `--description, -d` - Deck description

#### `deck list`

List all decks.

```bash
python -m cardforge.cli.main deck list
```

#### `deck add-card <deck_name_or_id> <card_name>`

Add a card to a deck.

```bash
python -m cardforge.cli.main deck add-card "Kaalia Voltron" "Aurelia, the Warleader"
python -m cardforge.cli.main deck add-card 1 "Sol Ring" --quantity 1 --category mana
```

**Options:**

- `--quantity, -q` - Number of copies (default: 1)
- `--category, -c` - Card category (creature, removal, etc.)

#### `deck missing <deck_id>`

Show cards needed for a deck that you don't own.

```bash
python -m cardforge.cli.main deck missing 1
```

#### `deck buy-list <deck_name_or_id>`

Generate a buy list for missing deck cards.

```bash
python -m cardforge.cli.main deck buy-list "Kaalia Voltron" --budget 50
```

**Options:**

- `--budget, -b` - Budget limit in USD
- `--priority, -p` - Priority level 1-5 (default: 2)

---

### Buy List Commands

#### `buylist show`

Display current buy list.

```bash
python -m cardforge.cli.main buylist show
```

#### `buylist add <card_name>`

Add a card to the buy list.

```bash
python -m cardforge.cli.main buylist add "Smothering Tithe"
python -m cardforge.cli.main buylist add "Dockside Extortionist" --priority 1 --max-price 50
```

**Options:**

- `--quantity, -q` - Number needed (default: 1)
- `--priority, -p` - Priority 1-5 (default: 3)
- `--max-price` - Maximum price willing to pay

---

### Sync Commands

#### `sync sets`

Sync set metadata from Scryfall.

```bash
python -m cardforge.cli.main sync sets
```

---

## Python API

### CardService

```python
from cardforge.services.card_service import CardService

async with CardService() as service:
    cards = await service.search("angel", colors=["W"])
    card = await service.get_by_name("Sol Ring")
```

### CollectionService

```python
from cardforge.services.collection_service import CollectionService

async with CollectionService() as service:
    stats = await service.get_stats()
    await service.import_csv("export.csv")
```
