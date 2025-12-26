"""
CardForge Pricing Service
Multi-source price aggregation
"""

from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime

from cardforge.repositories import PriceRepository, CardRepository
from cardforge.models import PriceRecord, AggregatedPrice, PriceQuote
from cardforge.api import ScryfallClient, TCGPlayerClient
from cardforge.config import get_config


class PricingService:
    """Service for price tracking and comparison."""
    
    def __init__(self):
        self.price_repo = PriceRepository()
        self.card_repo = CardRepository()
        self.config = get_config()
    
    async def get_current_price(self, card_id: int) -> Optional[AggregatedPrice]:
        """Get current price from all sources."""
        card = await self.card_repo.get(card_id)
        if not card:
            return None
        
        prices = []
        
        # Scryfall prices (from card data)
        if card.prices:
            prices.append(PriceQuote(
                source='scryfall',
                price_usd=card.prices.usd,
                price_usd_foil=card.prices.usd_foil,
                updated_at=datetime.now(),
            ))
        
        # TCGPlayer prices (if configured)
        if self.config.tcgplayer.public_key and card.tcgplayer_id:
            try:
                async with TCGPlayerClient(
                    public_key=self.config.tcgplayer.public_key,
                    private_key=self.config.tcgplayer.private_key,
                ) as client:
                    tcg_prices = await client.get_market_prices([card.tcgplayer_id])
                    if card.tcgplayer_id in tcg_prices:
                        p = tcg_prices[card.tcgplayer_id]
                        prices.append(PriceQuote(
                            source='tcgplayer',
                            price_usd=p.get('market'),
                            price_low=p.get('low'),
                            price_high=p.get('high'),
                            updated_at=datetime.now(),
                        ))
            except Exception:
                pass
        
        if not prices:
            return None
        
        # Aggregate
        return AggregatedPrice(
            card_id=card_id,
            card_name=card.name,
            quotes=prices,
            best_price=min(p.price_usd for p in prices if p.price_usd),
            best_source=min(prices, key=lambda p: p.price_usd or Decimal('999999')).source,
        )
    
    async def record_price(
        self,
        card_id: int,
        source: str,
        price_usd: Optional[Decimal] = None,
        price_usd_foil: Optional[Decimal] = None,
    ) -> PriceRecord:
        """Record a price point for history."""
        return await self.price_repo.add_price_record(
            card_id=card_id,
            source=source,
            price_usd=price_usd,
            price_usd_foil=price_usd_foil,
        )
    
    async def get_price_history(
        self,
        card_id: int,
        days: int = 30,
    ) -> List[PriceRecord]:
        """Get price history for a card."""
        return await self.price_repo.get_history(card_id, days)
    
    async def get_price_trend(self, card_id: int, days: int = 30) -> Dict:
        """Get price trend analysis."""
        return await self.price_repo.get_price_trend(card_id, days)
    
    async def get_biggest_gainers(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get cards with biggest price increases."""
        return await self.price_repo.get_biggest_movers(days, limit, 'up')
    
    async def get_biggest_losers(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get cards with biggest price drops."""
        return await self.price_repo.get_biggest_movers(days, limit, 'down')
    
    async def update_all_prices(self) -> int:
        """Update prices for all cards in collection."""
        # Get all unique cards in collection
        from cardforge.repositories import CollectionCardRepository
        cc_repo = CollectionCardRepository()
        
        entries = await cc_repo.get_all(limit=10000)
        card_ids = list(set(e.card_id for e in entries))
        
        count = 0
        async with ScryfallClient() as client:
            for card_id in card_ids:
                card = await self.card_repo.get(card_id)
                if card and card.scryfall_id:
                    try:
                        data = await client.get_card_by_id(card.scryfall_id)
                        prices = data.get('prices', {})
                        
                        if prices.get('usd') or prices.get('usd_foil'):
                            await self.record_price(
                                card_id=card_id,
                                source='scryfall',
                                price_usd=Decimal(prices['usd']) if prices.get('usd') else None,
                                price_usd_foil=Decimal(prices['usd_foil']) if prices.get('usd_foil') else None,
                            )
                            count += 1
                    except Exception:
                        continue
        
        return count
