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
                card.type_line = Card._safe_str(data['type_line'])
                card.types = CardType.from_type_line(data['type_line'])
            
            # Mana cost
            if 'mana_cost' in data:
                card.mana_cost = Card._safe_str(data['mana_cost'])
            
            # Converted mana cost
            if 'cmc' in data:
                card.cmc = int(data['cmc'])
            
            # Oracle text
            if 'oracle_text' in data:
                card.oracle_text = Card._safe_str(data['oracle_text'])
            
            # Scryfall ID
            if 'id' in data:
                card.scryfall_id = data['id']
            
            # Market price from Scryfall
            if 'prices' in data and data['prices']:
                # Store full price object
                card.prices = data['prices']
                
                # Set market_value for calculations
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
            
            # Power/Toughness/Loyalty/Defense
            if 'power' in data:
                card.power = Card._safe_str(data['power'])
            if 'toughness' in data:
                card.toughness = Card._safe_str(data['toughness'])
            if 'loyalty' in data:
                card.loyalty = Card._safe_str(data['loyalty'])
            if 'defense' in data:
                card.defense = Card._safe_str(data['defense'])
            
            # Artist and flavor
            if 'artist' in data:
                card.artist = Card._safe_str(data['artist'])
            if 'artist_ids' in data:
                card.artist_ids = data['artist_ids']
            if 'flavor_text' in data:
                card.flavor_text = Card._safe_str(data['flavor_text'])
            if 'flavor_name' in data:
                card.flavor_name = Card._safe_str(data['flavor_name'])
            
            # Image URIs
            if 'image_uris' in data:
                card.image_uris = data['image_uris']
            
            # Set information
            if 'set_name' in data:
                card.set_name = data['set_name']
            if 'set_type' in data:
                card.set_type = data['set_type']
            if 'set_id' in data:
                card.set_id = data['set_id']
            if 'released_at' in data:
                card.released_at = data['released_at']
            if 'collector_number' in data:
                card.collector_number = data['collector_number']
            
            # Card properties
            if 'border_color' in data:
                card.border_color = data['border_color']
            if 'frame' in data:
                card.frame = data['frame']
            if 'frame_effects' in data:
                card.frame_effects = data['frame_effects']
            if 'security_stamp' in data:
                card.security_stamp = data['security_stamp']
            if 'layout' in data:
                card.layout = data['layout']
            if 'watermark' in data:
                card.watermark = data['watermark']
            
            # Keywords
            if 'keywords' in data:
                card.keywords = data['keywords']
            
            # Legalities
            if 'legalities' in data:
                card.legalities = data['legalities']
            
            # IDs and External References
            if 'arena_id' in data:
                card.arena_id = data['arena_id']
            if 'mtgo_id' in data:
                card.mtgo_id = data['mtgo_id']
            if 'mtgo_foil_id' in data:
                card.mtgo_foil_id = data['mtgo_foil_id']
            if 'tcgplayer_id' in data:
                card.tcgplayer_id = data['tcgplayer_id']
            if 'tcgplayer_etched_id' in data:
                card.tcgplayer_etched_id = data['tcgplayer_etched_id']
            if 'cardmarket_id' in data:
                card.cardmarket_id = data['cardmarket_id']
            if 'oracle_id' in data:
                card.oracle_id = data['oracle_id']
            if 'multiverse_ids' in data:
                card.multiverse_ids = data['multiverse_ids']
            
            # Additional Gameplay Fields
            if 'color_indicator' in data:
                card.color_indicator = CardColor.from_colors(data['color_indicator'])
            if 'produced_mana' in data:
                card.produced_mana = CardColor.from_colors(data['produced_mana'])
            if 'hand_modifier' in data:
                card.hand_modifier = data['hand_modifier']
            if 'life_modifier' in data:
                card.life_modifier = data['life_modifier']
            if 'all_parts' in data:
                card.all_parts = data['all_parts']
            if 'card_faces' in data:
                card.card_faces = data['card_faces']
            
            # Boolean properties
            if 'reserved' in data:
                card.reserved = data['reserved']
            if 'digital' in data:
                card.digital = data['digital']
            if 'reprint' in data:
                card.reprint = data['reprint']
            if 'variation' in data:
                card.variation = data['variation']
            if 'promo' in data:
                card.promo = data['promo']
            if 'textless' in data:
                card.textless = data['textless']
            if 'full_art' in data:
                card.full_art = data['full_art']
            if 'story_spotlight' in data:
                card.story_spotlight = data['story_spotlight']
            if 'game_changer' in data:
                card.game_changer = data['game_changer']
            if 'booster' in data:
                card.booster = data['booster']
            if 'content_warning' in data:
                card.content_warning = data['content_warning']
            if 'highres_image' in data:
                card.highres_image = data['highres_image']
            if 'oversized' in data:
                card.oversized = data['oversized']
            
            # Print-specific fields
            if 'printed_name' in data:
                card.printed_name = data['printed_name']
            if 'printed_text' in data:
                card.printed_text = data['printed_text']
            if 'printed_type_line' in data:
                card.printed_type_line = data['printed_type_line']
            if 'finishes' in data:
                card.finishes = data['finishes']
            if 'games' in data:
                card.games = data['games']
            if 'promo_types' in data:
                card.promo_types = data['promo_types']
            if 'attraction_lights' in data:
                card.attraction_lights = data['attraction_lights']
            if 'purchase_uris' in data:
                card.purchase_uris = data['purchase_uris']
            if 'related_uris' in data:
                card.related_uris = data['related_uris']
            
            # Variation and technical fields
            if 'variation_of' in data:
                card.variation_of = data['variation_of']
            if 'card_back_id' in data:
                card.card_back_id = data['card_back_id']
            if 'illustration_id' in data:
                card.illustration_id = data['illustration_id']
            if 'image_status' in data:
                card.image_status = data['image_status']
            
            # URI fields
            if 'scryfall_set_uri' in data:
                card.scryfall_set_uri = data['scryfall_set_uri']
            if 'set_search_uri' in data:
                card.set_search_uri = data['set_search_uri']
            if 'set_uri' in data:
                card.set_uri = data['set_uri']
            
            # Preview information
            if 'preview' in data:
                card.preview = data['preview']
            
            # Rankings
            if 'edhrec_rank' in data:
                card.edhrec_rank = data['edhrec_rank']
            if 'penny_rank' in data:
                card.penny_rank = data['penny_rank']
                
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
