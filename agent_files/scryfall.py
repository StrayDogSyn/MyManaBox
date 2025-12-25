#!/usr/bin/env python3
"""
Scryfall API Client

Provides access to Scryfall's comprehensive Magic card database with:
- Rate limiting (10 req/sec max)
- Response caching (reduces API calls)
- Bulk data downloads for offline use
- Card search and lookup
"""

import requests
import time
import json
from pathlib import Path
from typing import Optional, Dict, List
from functools import wraps
from datetime import datetime, timedelta


class RateLimiter:
    """Enforce rate limiting for API calls"""
    
    def __init__(self, calls_per_second: int = 10):
        self.min_interval = 1.0 / calls_per_second
        self.last_called = 0.0
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - self.last_called
            left_to_wait = self.min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            self.last_called = time.time()
            return result
        
        return wrapper


class ScryfallClient:
    """
    Client for Scryfall API
    
    Usage:
        client = ScryfallClient(cache_enabled=True)
        card = client.get_card("Lightning Bolt", set_code="lea")
        print(f"{card['name']} - ${card['prices']['usd']}")
    """
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self, cache_enabled: bool = True, cache_dir: str = "data/cache"):
        self.cache_enabled = cache_enabled
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load cache index
        self.cache_index_path = self.cache_dir / "scryfall_cache.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict:
        """Load cache index from disk"""
        if self.cache_index_path.exists():
            with open(self.cache_index_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        with open(self.cache_index_path, 'w') as f:
            json.dump(self.cache_index, f, indent=2)
    
    def _get_from_cache(self, cache_key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Retrieve data from cache if not expired"""
        if not self.cache_enabled or cache_key not in self.cache_index:
            return None
        
        cached_entry = self.cache_index[cache_key]
        cached_time = datetime.fromisoformat(cached_entry["timestamp"])
        
        if datetime.now() - cached_time > timedelta(hours=max_age_hours):
            # Cache expired
            return None
        
        cache_file = self.cache_dir / cached_entry["file"]
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        if not self.cache_enabled:
            return
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{cache_key.replace('/', '_')}_{timestamp}.json"
        cache_file = self.cache_dir / filename
        
        # Save data
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Update index
        self.cache_index[cache_key] = {
            "file": filename,
            "timestamp": datetime.now().isoformat()
        }
        self._save_cache_index()
    
    @RateLimiter(calls_per_second=10)
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited request to Scryfall API"""
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {
            "User-Agent": "MTG-Collection-Manager/1.0",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"❌ Not found: {endpoint}")
                return None
            else:
                print(f"⚠️  API Error {response.status_code}: {response.text}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Network error: {e}")
            return None
    
    def get_card(self, name: str, set_code: Optional[str] = None) -> Optional[Dict]:
        """
        Get card by exact name, optionally filtered by set
        
        Args:
            name: Exact card name (case-insensitive)
            set_code: Three-letter set code (e.g., 'NEO', 'LEA')
        
        Returns:
            Card data dict or None if not found
        """
        cache_key = f"card/{name}/{set_code or 'any'}"
        
        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        # Make API request
        endpoint = "/cards/named"
        params = {"exact": name}
        
        if set_code:
            params["set"] = set_code
        
        card_data = self._request(endpoint, params)
        
        if card_data:
            self._save_to_cache(cache_key, card_data)
        
        return card_data
    
    def get_card_by_id(self, scryfall_id: str) -> Optional[Dict]:
        """Get card by Scryfall ID"""
        cache_key = f"id/{scryfall_id}"
        
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        endpoint = f"/cards/{scryfall_id}"
        card_data = self._request(endpoint)
        
        if card_data:
            self._save_to_cache(cache_key, card_data)
        
        return card_data
    
    def search_cards(self, query: str, order: str = "name", unique: str = "cards") -> List[Dict]:
        """
        Search for cards using Scryfall query syntax
        
        Query examples:
        - "t:creature cmc=3 c:r" (red 3-drop creatures)
        - "set:neo r:rare" (rares from Kamigawa: Neon Dynasty)
        - "is:commander" (all legendary creatures)
        
        Args:
            query: Scryfall search query
            order: Sort order (name, set, released, cmc, etc.)
            unique: Deduplication mode (cards, art, prints)
        
        Returns:
            List of card data dicts
        """
        all_cards = []
        endpoint = "/cards/search"
        params = {
            "q": query,
            "order": order,
            "unique": unique
        }
        
        while True:
            data = self._request(endpoint, params)
            
            if not data:
                break
            
            all_cards.extend(data.get("data", []))
            
            if not data.get("has_more"):
                break
            
            # Get next page
            endpoint = data["next_page"].replace(self.BASE_URL, "")
            params = {}  # Next page URL includes all params
        
        return all_cards
    
    def get_set_cards(self, set_code: str) -> List[Dict]:
        """Get all cards from a specific set"""
        return self.search_cards(f"set:{set_code}", order="collector_number")
    
    def download_bulk_data(self, bulk_type: str = "oracle_cards") -> Path:
        """
        Download Scryfall's bulk data for offline use
        
        bulk_type options:
        - oracle_cards: Unique card names (smallest, fastest)
        - default_cards: One printing per card
        - all_cards: Every printing (largest)
        - rulings: Card rulings
        
        Returns:
            Path to downloaded JSON file
        """
        print(f"📥 Downloading bulk data: {bulk_type}...")
        
        # Get download URL
        meta_url = f"{self.BASE_URL}/bulk-data/{bulk_type}"
        meta = requests.get(meta_url).json()
        
        download_url = meta["download_uri"]
        size_mb = meta["size"] / 1024 / 1024
        
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Updated: {meta['updated_at']}")
        
        # Download to cache
        output_path = self.cache_dir / f"{bulk_type}.json"
        
        response = requests.get(download_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                
                # Progress indicator
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"   Progress: {percent:.1f}%", end='\r')
        
        print(f"\n✅ Downloaded to: {output_path}")
        return output_path
    
    def enrich_card_data(self, card: Dict) -> Dict:
        """
        Enrich a basic card dict with full Scryfall data
        
        Input card should have at minimum:
        - name: Card name
        - set (optional): Set code
        
        Returns:
            Enhanced card dict with Scryfall data merged in
        """
        scryfall_data = self.get_card(
            card["name"],
            set_code=card.get("set") or card.get("set_code")
        )
        
        if not scryfall_data:
            print(f"⚠️  Could not find: {card['name']}")
            return card
        
        # Merge Scryfall data
        enriched = card.copy()
        enriched.update({
            "scryfall_id": scryfall_data["id"],
            "type_line": scryfall_data.get("type_line"),
            "mana_cost": scryfall_data.get("mana_cost"),
            "cmc": scryfall_data.get("cmc"),
            "colors": scryfall_data.get("colors", []),
            "rarity": scryfall_data.get("rarity"),
            "image_url": scryfall_data.get("image_uris", {}).get("normal"),
            "market_price": float(scryfall_data.get("prices", {}).get("usd") or 0),
            "foil_price": float(scryfall_data.get("prices", {}).get("usd_foil") or 0),
            "price_updated_at": datetime.now().isoformat()
        })
        
        return enriched
    
    def bulk_enrich(self, cards: List[Dict], progress: bool = True) -> List[Dict]:
        """
        Enrich multiple cards with Scryfall data
        
        Args:
            cards: List of basic card dicts
            progress: Show progress indicator
        
        Returns:
            List of enriched card dicts
        """
        enriched_cards = []
        total = len(cards)
        
        for i, card in enumerate(cards, 1):
            enriched = self.enrich_card_data(card)
            enriched_cards.append(enriched)
            
            if progress:
                print(f"   Enriching: {i}/{total} ({i/total*100:.1f}%)", end='\r')
        
        if progress:
            print(f"\n✅ Enriched {total} cards")
        
        return enriched_cards


# Convenience function
def get_scryfall_client(cache: bool = True) -> ScryfallClient:
    """Get a configured Scryfall client"""
    return ScryfallClient(cache_enabled=cache)


if __name__ == "__main__":
    # Example usage
    client = ScryfallClient(cache_enabled=True)
    
    # Single card lookup
    print("Testing card lookup...")
    bolt = client.get_card("Lightning Bolt", set_code="lea")
    if bolt:
        print(f"✅ {bolt['name']} ({bolt['set_name']})")
        print(f"   Price: ${bolt['prices']['usd']}")
        print(f"   Scryfall ID: {bolt['id']}")
    
    # Search
    print("\nTesting search...")
    results = client.search_cards("t:creature cmc=3 c:r", unique="cards")
    print(f"✅ Found {len(results)} red 3-drop creatures")
    
    # Bulk enrichment
    print("\nTesting bulk enrichment...")
    test_cards = [
        {"name": "Sol Ring", "set": "cmr"},
        {"name": "Command Tower", "set": "cmr"},
        {"name": "Arcane Signet", "set": "cmr"}
    ]
    enriched = client.bulk_enrich(test_cards)
    print(f"✅ Enriched {len(enriched)} cards")
    for card in enriched:
        print(f"   {card['name']}: ${card['market_price']}")
