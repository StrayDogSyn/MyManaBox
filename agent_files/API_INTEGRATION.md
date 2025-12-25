# API Integration Guide

**Comprehensive guide to integrating MTG collection manager with external services.**

---

## 🎯 Overview

This project integrates with multiple services to provide comprehensive card data, pricing, and collection management:

| Service | Purpose | Cost | Rate Limits | Auth Required |
|---------|---------|------|-------------|---------------|
| **Scryfall** | Card data, images, Oracle text | Free | 10 req/sec | No |
| **TCGPlayer** | Market prices, buy links | Free tier | 300 req/5min | API key |
| **Card Kingdom** | Buylist prices | Free | Respectful scraping | No |
| **Moxfield** | Deck building, collection sync | Free | Via CSV | Account |
| **ManaBox** | Mobile scanning | Free | Via CSV | Account |

---

## 📡 Scryfall API Integration

### Why Scryfall?

- **100% free** with generous rate limits
- **Comprehensive data**: every printing, Oracle text, images
- **Well-documented** REST API
- **No authentication** required
- **Bulk data downloads** for offline use

### Getting Started

**No signup needed!** Start using immediately.

#### Basic Card Lookup

```python
import requests
import time

BASE_URL = "https://api.scryfall.com"

def get_card_by_name(card_name, set_code=None):
    """Fetch card data from Scryfall by exact name"""
    endpoint = f"{BASE_URL}/cards/named"
    params = {"exact": card_name}
    
    if set_code:
        params["set"] = set_code
    
    response = requests.get(endpoint, params=params)
    time.sleep(0.1)  # Rate limit: 10 req/sec max
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Example usage
card = get_card_by_name("Lightning Bolt", set_code="lea")
print(f"{card['name']} - ${card['prices']['usd']}")
```

#### Bulk Data Download (Recommended for 5000+ cards)

```python
def download_bulk_data(bulk_type="oracle_cards"):
    """
    Download entire Scryfall database for offline use
    
    bulk_type options:
    - oracle_cards: Unique card names (smaller, faster)
    - default_cards: One printing per card
    - all_cards: Every printing (large!)
    """
    # Get download URL
    bulk_url = f"{BASE_URL}/bulk-data/{bulk_type}"
    meta = requests.get(bulk_url).json()
    download_url = meta["download_uri"]
    
    print(f"Downloading {meta['size'] / 1024 / 1024:.1f} MB...")
    
    # Download to file
    response = requests.get(download_url, stream=True)
    with open(f"data/cache/{bulk_type}.json", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("Download complete!")

# Run once, cache locally
download_bulk_data("oracle_cards")
```

#### Search API (Advanced)

```python
def search_cards(query, order="name", unique="cards"):
    """
    Search Scryfall with advanced queries
    
    Example queries:
    - "t:creature cmc=3 c:r" (red 3-drop creatures)
    - "set:neo r:rare" (rares from Kamigawa: Neon Dynasty)
    - "is:commander" (all legendary creatures)
    """
    endpoint = f"{BASE_URL}/cards/search"
    params = {
        "q": query,
        "order": order,
        "unique": unique
    }
    
    all_cards = []
    
    while True:
        response = requests.get(endpoint, params=params)
        time.sleep(0.1)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        all_cards.extend(data.get("data", []))
        
        if not data.get("has_more"):
            break
            
        endpoint = data["next_page"]
        params = {}  # Next page URL includes query
    
    return all_cards

# Find all foil mythics in your collection
mythics = search_cards("is:foil r:mythic set:neo")
```

### Best Practices

✅ **DO:**
- Cache responses (24h minimum for card data)
- Use bulk downloads for >100 card lookups
- Respect 10 req/sec rate limit
- Include `User-Agent` header with your app name

❌ **DON'T:**
- Make the same request repeatedly
- Use Scryfall for real-time price tracking (use TCGPlayer)
- Scrape their website (use the API!)

### Rate Limiting Implementation

```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Decorator to enforce rate limiting"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator

@rate_limit(calls_per_second=10)
def scryfall_request(url, params=None):
    """All Scryfall requests go through this"""
    return requests.get(url, params=params)
```

---

## 💰 TCGPlayer API Integration

### Why TCGPlayer?

- **Real-time market prices** (updated hourly)
- **Buy links** for deck shopping
- **Historical price data** (with premium account)
- **Official marketplace** (most accurate pricing)

### Getting API Access

1. **Create account**: [TCGPlayer Developer Portal](https://developer.tcgplayer.com/)
2. **Request API key**: Apply for access (approval ~24-48h)
3. **Get credentials**: Public Key + Private Key

### Authentication

TCGPlayer uses **Bearer token** authentication:

```python
import requests
import base64
from datetime import datetime, timedelta

class TCGPlayerClient:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key
        self.token = None
        self.token_expires = None
        self.base_url = "https://api.tcgplayer.com"
    
    def get_token(self):
        """Authenticate and get access token"""
        if self.token and datetime.now() < self.token_expires:
            return self.token
        
        # Create credentials string
        creds = f"{self.public_key}:{self.private_key}"
        encoded = base64.b64encode(creds.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(
            f"{self.base_url}/token",
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            expires_in = token_data["expires_in"]
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            return self.token
        else:
            raise Exception(f"Auth failed: {response.text}")
    
    def request(self, endpoint, params=None):
        """Make authenticated request"""
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        
        return response.json() if response.status_code == 200 else None
```

### Getting Product IDs

TCGPlayer requires **product IDs**, not card names:

```python
def find_product_id(client, card_name, set_name=None):
    """Search for MTG card and get product ID"""
    endpoint = "/catalog/products"
    params = {
        "categoryId": 1,  # 1 = Magic: The Gathering
        "productName": card_name,
        "limit": 10
    }
    
    results = client.request(endpoint, params)
    
    if not results or not results.get("results"):
        return None
    
    # If set specified, filter by set name
    if set_name:
        for product in results["results"]:
            if set_name.lower() in product.get("groupName", "").lower():
                return product["productId"]
    
    # Otherwise, return first result (usually most recent printing)
    return results["results"][0]["productId"]

# Usage
tcg = TCGPlayerClient(public_key="YOUR_KEY", private_key="YOUR_SECRET")
product_id = find_product_id(tcg, "Lightning Bolt", "Alpha")
```

### Getting Prices

```python
def get_market_price(client, product_id):
    """Get current market price for a product"""
    endpoint = f"/pricing/product/{product_id}"
    
    data = client.request(endpoint)
    
    if not data or not data.get("results"):
        return None
    
    prices = data["results"][0]
    
    return {
        "low": prices.get("lowPrice"),
        "mid": prices.get("midPrice"),
        "high": prices.get("highPrice"),
        "market": prices.get("marketPrice"),  # Most accurate
        "foil_market": prices.get("foilMarketPrice"),
        "updated": prices.get("subTypeName")
    }

# Get price for Lightning Bolt
price_data = get_market_price(tcg, product_id)
print(f"Market price: ${price_data['market']}")
```

### Bulk Price Lookups

```python
def get_bulk_prices(client, product_ids):
    """Get prices for multiple cards (max 250 per request)"""
    # Split into chunks of 250
    chunks = [product_ids[i:i+250] for i in range(0, len(product_ids), 250)]
    
    all_prices = {}
    
    for chunk in chunks:
        endpoint = "/pricing/product/" + ",".join(map(str, chunk))
        data = client.request(endpoint)
        
        if data and data.get("results"):
            for price in data["results"]:
                pid = price["productId"]
                all_prices[pid] = {
                    "market": price.get("marketPrice"),
                    "foil": price.get("foilMarketPrice")
                }
    
    return all_prices
```

### Rate Limits

- **Free tier**: 300 requests per 5 minutes
- **Premium**: Higher limits (requires paid account)
- **Best practice**: Cache prices for 1-4 hours

---

## 🏪 Card Kingdom Integration

### Why Card Kingdom?

- **Buylist prices** (selling your cards)
- **Store credit bonuses** (typically +30%)
- **Condition-based pricing**
- **No API** (requires web scraping)

### Web Scraping Approach

**Important**: Respect robots.txt and rate limit aggressively.

```python
import requests
from bs4 import BeautifulSoup
import time

class CardKingdomScraper:
    def __init__(self):
        self.base_url = "https://www.cardkingdom.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MTG-Collection-Manager/1.0"
        })
    
    def get_buylist_price(self, card_name, set_code=None, foil=False):
        """Scrape buylist price for a card"""
        search_url = f"{self.base_url}/purchasing/mtg_singles"
        params = {"filter[name]": card_name}
        
        if set_code:
            params["filter[edition]"] = set_code
        
        # Rate limit: 1 request per 2 seconds
        time.sleep(2)
        
        response = self.session.get(search_url, params=params)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find buylist table
        buylist_rows = soup.find_all("tr", class_="productItemWrapper")
        
        for row in buylist_rows:
            name_elem = row.find("span", class_="productDetailTitle")
            if not name_elem or card_name.lower() not in name_elem.text.lower():
                continue
            
            # Check if foil matches
            is_foil = "foil" in row.text.lower()
            if foil != is_foil:
                continue
            
            # Extract prices
            cash_elem = row.find("td", class_="sellCash")
            credit_elem = row.find("td", class_="sellCredit")
            
            if cash_elem and credit_elem:
                return {
                    "cash": float(cash_elem.text.strip().replace("$", "")),
                    "credit": float(credit_elem.text.strip().replace("$", "")),
                    "foil": foil
                }
        
        return None

# Usage
ck = CardKingdomScraper()
price = ck.get_buylist_price("Force of Will", set_code="ALL", foil=False)
if price:
    print(f"Cash: ${price['cash']}, Credit: ${price['credit']}")
```

### Ethical Scraping Guidelines

✅ **DO:**
- Cache results for 24-48 hours
- Use 2-3 second delays between requests
- Identify your bot in User-Agent
- Only scrape during off-peak hours

❌ **DON'T:**
- Make parallel requests
- Scrape entire catalog
- Use scraped data commercially
- Ignore robots.txt

---

## 🃏 Moxfield Integration

### Why Moxfield?

- **Best deck builder** UI
- **Collection tracking**
- **Playtest tools**
- **No public API** (uses CSV import/export)

### Export Format

Moxfield expects CSV with these columns:

```csv
Count,Tradelist Count,Name,Edition,Condition,Language,Foil,Tags,Last Modified,Collector Number,Alter,Proxy,Purchase Price
```

### Python Exporter

```python
import csv
from datetime import datetime

def export_to_moxfield(collection, output_file):
    """Export collection to Moxfield-compatible CSV"""
    
    headers = [
        "Count", "Tradelist Count", "Name", "Edition",
        "Condition", "Language", "Foil", "Tags",
        "Last Modified", "Collector Number", "Alter",
        "Proxy", "Purchase Price"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for card in collection:
            row = [
                card.get("quantity", 1),
                card.get("tradelist_count", 0),
                card["name"],
                card.get("set", ""),
                card.get("condition", "NM"),
                card.get("language", "English"),
                "foil" if card.get("foil") else "",
                ";".join(card.get("tags", [])),
                datetime.now().strftime("%Y-%m-%d"),
                card.get("collector_number", ""),
                "",  # Alter
                "",  # Proxy
                card.get("purchase_price", "")
            ]
            writer.writerow(row)
    
    print(f"Exported {len(collection)} cards to {output_file}")

# Usage
from src.catalogue import load_collection

my_cards = load_collection("data/collections/main.db")
export_to_moxfield(my_cards, "exports/moxfield_import.csv")
```

### Import to Moxfield

1. Go to **Moxfield.com** → **Collection**
2. Click **Import** button
3. Select **CSV** format
4. Upload your generated file
5. Review import summary
6. Click **Confirm Import**

### Moxfield Deck Export

Download deck as TXT from Moxfield, import to your catalog:

```python
def import_moxfield_deck(deck_file):
    """Parse Moxfield deck list (TXT format)"""
    deck = {"main": [], "sideboard": [], "commander": []}
    current_section = "main"
    
    with open(deck_file, 'r') as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue
            
            # Section headers
            if line.lower() == "commander":
                current_section = "commander"
                continue
            elif line.lower() == "sideboard":
                current_section = "sideboard"
                continue
            
            # Parse card line: "1 Lightning Bolt"
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[0].isdigit():
                quantity = int(parts[0])
                card_name = parts[1]
                
                deck[current_section].append({
                    "name": card_name,
                    "quantity": quantity
                })
    
    return deck
```

---

## 📱 ManaBox Integration

### Why ManaBox?

- **Best mobile scanner** accuracy
- **Bulk scan mode**
- **Export to CSV**
- **No API** (uses CSV export)

### ManaBox Export Format

```csv
Card Name,Set Name,Set Code,Card Number,Quantity,Language,Condition,Foil,Purchase Price,Misprint
```

### Python Importer

```python
import csv

def import_manabox_export(manabox_csv):
    """Import cards from ManaBox CSV export"""
    cards = []
    
    with open(manabox_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            card = {
                "name": row["Card Name"],
                "set": row["Set Code"],
                "set_name": row["Set Name"],
                "collector_number": row["Card Number"],
                "quantity": int(row["Quantity"]),
                "language": row.get("Language", "English"),
                "condition": row.get("Condition", "NM"),
                "foil": row.get("Foil", "").lower() == "foil",
                "purchase_price": row.get("Purchase Price", ""),
                "misprint": row.get("Misprint", "").lower() == "yes"
            }
            cards.append(card)
    
    print(f"Imported {len(cards)} cards from ManaBox")
    return cards

# Usage
manabox_cards = import_manabox_export("data/exports/manabox_2025-12-25.csv")
```

### Syncing ManaBox → Moxfield

```python
def sync_manabox_to_moxfield(manabox_csv, output_csv):
    """Convert ManaBox export to Moxfield import format"""
    
    # Import from ManaBox
    manabox_cards = import_manabox_export(manabox_csv)
    
    # Export to Moxfield format
    export_to_moxfield(manabox_cards, output_csv)
    
    print(f"Sync complete: {manabox_csv} → {output_csv}")
    print(f"Upload {output_csv} to Moxfield Collection → Import")

# Run sync
sync_manabox_to_moxfield(
    "data/exports/manabox_scan_session_1.csv",
    "exports/moxfield_import_session_1.csv"
)
```

---

## 🔄 Complete Integration Workflow

### Catalog 5000 Cards: Full Pipeline

```python
#!/usr/bin/env python3
"""
Complete workflow: Scan → Catalog → Price → Export
"""

from src.api_clients.scryfall import ScryfallClient
from src.api_clients.tcgplayer import TCGPlayerClient
from src.importers.manabox import import_manabox_export
from src.exporters.csv_exporter import export_to_moxfield
from src.catalogue import Collection

def full_pipeline(manabox_csv, output_dir="exports"):
    """Run complete cataloging pipeline"""
    
    print("Step 1: Import ManaBox scan...")
    cards = import_manabox_export(manabox_csv)
    
    print("Step 2: Enrich with Scryfall data...")
    scryfall = ScryfallClient(cache_enabled=True)
    for card in cards:
        oracle_data = scryfall.get_card(card["name"], card["set"])
        if oracle_data:
            card["scryfall_id"] = oracle_data["id"]
            card["image_url"] = oracle_data["image_uris"]["normal"]
            card["type"] = oracle_data["type_line"]
            card["rarity"] = oracle_data["rarity"]
    
    print("Step 3: Add pricing (TCGPlayer)...")
    tcg = TCGPlayerClient.from_env()  # Loads from .env file
    for card in cards:
        product_id = tcg.find_product_id(card["name"], card["set_name"])
        if product_id:
            prices = tcg.get_market_price(product_id)
            card["market_price"] = prices["market"]
    
    print("Step 4: Save to local database...")
    collection = Collection("data/collections/main.db")
    collection.bulk_insert(cards)
    
    print("Step 5: Export to Moxfield...")
    export_path = f"{output_dir}/moxfield_import.csv"
    export_to_moxfield(cards, export_path)
    
    print(f"\n✅ Pipeline complete!")
    print(f"   - {len(cards)} cards processed")
    print(f"   - Export ready: {export_path}")
    print(f"   - Upload to Moxfield.com → Collection → Import")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pipeline.py <manabox_export.csv>")
        sys.exit(1)
    
    full_pipeline(sys.argv[1])
```

Run with:
```bash
python scripts/pipeline.py data/exports/manabox_session1.csv
```

---

## 🎯 Next Steps

1. **Set up API keys** in `config/api_keys.env`
2. **Test each integration** individually
3. **Run first scan session** (100 cards)
4. **Validate pipeline** before bulk scanning
5. **Schedule price updates** (weekly cron job)

See `docs/WORKFLOWS.md` for detailed step-by-step guides.
