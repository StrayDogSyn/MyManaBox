from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict

from cardforge.services import PricingService

router = APIRouter()
pricing_service = PricingService()

@router.get("/card/{card_id}")
async def get_current_price(card_id: int):
    """Get current price for a card."""
    price = await pricing_service.get_current_price(card_id)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")
        
    return {
        "card_name": price.card_name,
        "best_price": float(price.best_price) if price.best_price else None,
        "best_source": price.best_source,
        "quotes": [
            {
                "source": q.source,
                "price": float(q.price_usd) if q.price_usd else None,
                "updated": q.updated_at
            }
            for q in price.quotes
        ]
    }

@router.get("/trends/{card_id}")
async def get_price_trend(card_id: int, days: int = 30):
    """Get price trend for a card."""
    return await pricing_service.get_price_trend(card_id, days)

@router.get("/movers/gainers")
async def get_biggest_gainers(days: int = 7, limit: int = 10):
    """Get biggest price gainers."""
    return await pricing_service.get_biggest_gainers(days, limit)

@router.get("/movers/losers")
async def get_biggest_losers(days: int = 7, limit: int = 10):
    """Get biggest price losers."""
    return await pricing_service.get_biggest_losers(days, limit)
