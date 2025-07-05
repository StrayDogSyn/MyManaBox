"""Scryfall API client for card data enrichment."""

import requests
import time
import json
from decimal import Decimal
from typing import Dict, Optional, Any, Set
from pathlib import Path
from ..models import Card, CardColor, CardRarity, CardType


class ScryfallClient:
    """Client for interacting with Scryfall API."""
    
    BASE_URL = "https://api.scryfall.com"
    
    def __init__(self, cache_file: str = "card_cache.json"):
        """Initialize with optional caching."""
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MyManaBox/1.0 (https://github.com/user/MyManaBox)'
        })
    
    def _load_cache(self) -> Dict:
        """Load cached card data."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def _get_cache_key(self, name: str, set_code: str) -> str:
        """Generate cache key for card."""
        return f"{name.lower()}|{set_code.lower()}"
    
    def enrich_card(self, card: Card) -> bool:
        """Enrich card with data from Scryfall API."""
        cache_key = self._get_cache_key(card.name, card.edition)
        
        # Check cache first
        if cache_key in self.cache:
            self._apply_card_data(card, self.cache[cache_key])
            return True
        
        # Make API request
        card_data = self._fetch_card_data(card.name, card.edition)
        if card_data:
            self.cache[cache_key] = card_data
            self._apply_card_data(card, card_data)
            self._save_cache()
            return True
        
        return False
    
    def _fetch_card_data(self, name: str, set_code: str) -> Optional[Dict[str, Any]]:
        """Fetch card data from Scryfall API."""
        try:
            # Try exact search first
            url = f"{self.BASE_URL}/cards/named/exact"
            params = {"name": name}
            if set_code:
                params["set"] = set_code
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            
            # Fallback to fuzzy search
            if response.status_code == 404:
                url = f"{self.BASE_URL}/cards/named/fuzzy"
                response = self.session.get(url, params={"name": name})
                
                if response.status_code == 200:
                    return response.json()
            
            # Rate limiting
            if response.status_code == 429:
                time.sleep(0.1)
                return self._fetch_card_data(name, set_code)
            
        except requests.RequestException:
            pass
        
        return None
    
    def _apply_card_data(self, card: Card, data: Dict[str, Any]) -> None:
        """Apply Scryfall data to card object."""
        try:
            # Colors
            if 'colors' in data:
                card.colors = CardColor.from_colors(data['colors'])
            
            if 'color_identity' in data:
                card.color_identity = CardColor.from_colors(data['color_identity'])
            
            # Rarity
            if 'rarity' in data:
                rarity_map = {
                    'common': CardRarity.COMMON,
                    'uncommon': CardRarity.UNCOMMON,
                    'rare': CardRarity.RARE,
                    'mythic': CardRarity.MYTHIC,
                    'special': CardRarity.SPECIAL
                }
                card.rarity = rarity_map.get(data['rarity'])
            
            # Type line and types
            if 'type_line' in data:
                card.type_line = data['type_line']
                card.types = CardType.from_type_line(data['type_line'])
            
            # Mana cost
            if 'mana_cost' in data:
                card.mana_cost = data['mana_cost']
            
            # Converted mana cost
            if 'cmc' in data:
                card.cmc = int(data['cmc'])
            
            # Oracle text
            if 'oracle_text' in data:
                card.oracle_text = data['oracle_text']
            
            # Scryfall ID
            if 'id' in data:
                card.scryfall_id = data['id']
            
            # Market price from Scryfall
            if 'prices' in data and data['prices']:
                # Prefer non-foil USD price, fallback to foil if needed
                usd_price = data['prices'].get('usd')
                usd_foil_price = data['prices'].get('usd_foil')
                
                if card.foil and usd_foil_price:
                    try:
                        card.market_value = Decimal(str(usd_foil_price))
                    except (ValueError, TypeError):
                        pass
                elif usd_price:
                    try:
                        card.market_value = Decimal(str(usd_price))
                    except (ValueError, TypeError):
                        pass
                
        except Exception:
            pass
    
    def enrich_collection(self, cards: list[Card], progress_callback=None) -> int:
        """Enrich multiple cards with API data."""
        enriched_count = 0
        total_cards = len(cards)
        
        for i, card in enumerate(cards):
            if self.enrich_card(card):
                enriched_count += 1
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, total_cards)
            
            # Rate limiting
            time.sleep(0.05)
        
        return enriched_count
