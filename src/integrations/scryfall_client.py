"""
Scryfall Integration
====================

Provides async interface to Scryfall API for card data enrichment.
Handles rate limiting (10 requests/sec), caching, and error handling.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class ScryfallCard:
    """Card data from Scryfall API."""
    scryfall_id: str
    oracle_id: str
    name: str
    set_code: str
    collector_number: str
    mana_cost: Optional[str]
    cmc: float
    type_line: str
    oracle_text: Optional[str]
    colors: Optional[str]
    color_identity: Optional[str]
    power: Optional[str]
    toughness: Optional[str]
    loyalty: Optional[str]
    rarity: str
    is_foil_available: bool
    is_reserved_list: bool
    is_commander: bool
    legalities: Optional[str]
    price_usd: Optional[Decimal]
    price_usd_foil: Optional[Decimal]
    price_eur: Optional[Decimal]
    price_tix: Optional[Decimal]
    image_uri: Optional[str]
    image_uri_small: Optional[str]


class ScryfallClient:
    """
    Async Scryfall API client with rate limiting.
    
    Rate limit: 100 requests/10 seconds = 10 requests/sec
    """
    
    BASE_URL = "https://api.scryfall.com"
    RATE_LIMIT = 10  # requests per second
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize Scryfall client.
        
        Args:
            cache_enabled: If True, cache card lookups in memory
        """
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = {} if cache_enabled else None
        self.request_times = []  # For rate limiting
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Enforce rate limiting (10 requests/sec)."""
        now = time.time()
        
        # Remove old timestamps (older than 1 second)
        self.request_times = [t for t in self.request_times if now - t < 1.0]
        
        # If we've made 10 requests in the last second, wait
        if len(self.request_times) >= self.RATE_LIMIT:
            wait_time = 1.0 - (now - self.request_times[0])
            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        self.request_times.append(time.time())
    
    async def search_card(
        self,
        name: str,
        set_code: Optional[str] = None,
    ) -> Optional[ScryfallCard]:
        """
        Search for a card by name and optional set code.
        
        Args:
            name: Card name
            set_code: MTG set code (e.g., 'cmr')
        
        Returns:
            ScryfallCard or None if not found
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        # Check cache first
        cache_key = f"{name}:{set_code or ''}"
        if self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]
        
        await self._rate_limit()
        
        try:
            # Build search query
            query = f'"{name}"'
            if set_code:
                query += f' set:{set_code}'
            
            url = f"{self.BASE_URL}/cards/search"
            params = {"q": query, "exact": "name"}
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    if data.get('total_cards', 0) > 0:
                        card_data = data['data'][0]
                        card = self._parse_card(card_data)
                        
                        # Cache the result
                        if self.cache is not None:
                            self.cache[cache_key] = card
                        
                        return card
                    else:
                        logger.debug(f"Card not found: {name} ({set_code})")
                
                elif resp.status == 404:
                    logger.debug(f"Card not found: {name}")
                
                else:
                    logger.warning(f"Scryfall API error {resp.status}: {await resp.text()}")
        
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error searching card: {e}")
        
        return None
    
    async def search_by_id(self, scryfall_id: str) -> Optional[ScryfallCard]:
        """
        Search for a card by Scryfall ID.
        
        Args:
            scryfall_id: Scryfall card ID
        
        Returns:
            ScryfallCard or None
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        # Check cache first
        if self.cache is not None and scryfall_id in self.cache:
            return self.cache[scryfall_id]
        
        await self._rate_limit()
        
        try:
            url = f"{self.BASE_URL}/cards/{scryfall_id}"
            
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    card_data = await resp.json()
                    card = self._parse_card(card_data)
                    
                    if self.cache is not None:
                        self.cache[scryfall_id] = card
                    
                    return card
                else:
                    logger.debug(f"Card not found: {scryfall_id}")
        
        except Exception as e:
            logger.error(f"Error fetching card: {e}")
        
        return None
    
    @staticmethod
    def _parse_card(data: dict) -> ScryfallCard:
        """Parse Scryfall card data into ScryfallCard object."""
        # Extract price data
        prices = data.get('prices', {})
        price_usd = prices.get('usd')
        price_usd_foil = prices.get('usd_foil')
        price_eur = prices.get('eur')
        price_tix = prices.get('tix')
        
        # Convert to Decimal if present
        if price_usd:
            price_usd = Decimal(price_usd)
        if price_usd_foil:
            price_usd_foil = Decimal(price_usd_foil)
        if price_eur:
            price_eur = Decimal(price_eur)
        if price_tix:
            price_tix = Decimal(price_tix)
        
        # Extract colors
        colors = None
        if 'colors' in data:
            colors = ','.join(data['colors']) if data['colors'] else None
        
        color_identity = None
        if 'color_identity' in data:
            color_identity = ','.join(data['color_identity']) if data['color_identity'] else None
        
        # Extract legalities
        legalities = None
        if 'legalities' in data:
            legal_formats = [f"{k}:{v}" for k, v in data['legalities'].items()]
            legalities = ','.join(legal_formats) if legal_formats else None
        
        # Check if commander
        is_commander = 'Legendary Creature' in data.get('type_line', '')
        
        # Check reserved list
        is_reserved_list = data.get('reserved', False)
        
        return ScryfallCard(
            scryfall_id=data.get('id', ''),
            oracle_id=data.get('oracle_id', ''),
            name=data.get('name', ''),
            set_code=data.get('set', ''),
            collector_number=data.get('collector_number', ''),
            mana_cost=data.get('mana_cost'),
            cmc=data.get('cmc', 0.0),
            type_line=data.get('type_line', ''),
            oracle_text=data.get('oracle_text'),
            colors=colors,
            color_identity=color_identity,
            power=data.get('power'),
            toughness=data.get('toughness'),
            loyalty=data.get('loyalty'),
            rarity=data.get('rarity', 'common'),
            is_foil_available=data.get('foil', False),
            is_reserved_list=is_reserved_list,
            is_commander=is_commander,
            legalities=legalities,
            price_usd=price_usd,
            price_usd_foil=price_usd_foil,
            price_eur=price_eur,
            price_tix=price_tix,
            image_uri=data.get('image_uris', {}).get('normal'),
            image_uri_small=data.get('image_uris', {}).get('small'),
        )
