from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict
from pydantic import BaseModel

from cardforge.services import CollectionService, AnalyticsService

router = APIRouter()
collection_service = CollectionService()
analytics_service = AnalyticsService()

class CardAddRequest(BaseModel):
    name: str
    quantity: int = 1
    foil: str = "normal"
    condition: str = "NM"
    set_code: Optional[str] = None

@router.get("/stats")
async def get_collection_stats(collection_id: int = 1):
    """Get overall collection statistics."""
    summary = await analytics_service.get_collection_summary(collection_id)
    return summary

@router.get("/cards")
async def get_cards(
    collection_id: int = 1,
    limit: int = 50,
    offset: int = 0
):
    """Get cards in collection."""
    cards = await collection_service.get_cards(collection_id, limit, offset)
    # Convert to JSON-friendly format
    return [
        {
            "id": c.id,
            "name": c.card.name,
            "set": c.card.set_code,
            "quantity": c.quantity,
            "condition": c.condition,
            "foil": c.foil,
            "price": float(c.purchase_price) if c.purchase_price else None
        }
        for c in cards
    ]

@router.post("/cards")
async def add_card(request: CardAddRequest, collection_id: int = 1):
    """Add card to collection."""
    result = await collection_service.add_card(
        card_name=request.name,
        quantity=request.quantity,
        foil=request.foil,
        condition=request.condition,
        collection_id=collection_id,
        set_code=request.set_code
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Card not found")
        
    return {"status": "success", "id": result.id}

@router.get("/analytics/colors")
async def get_color_analytics(collection_id: int = 1):
    """Get color distribution."""
    return await analytics_service.get_color_distribution(collection_id)

@router.get("/analytics/sets")
async def get_set_analytics(collection_id: int = 1):
    """Get top sets by count."""
    return await analytics_service.get_set_completion(collection_id)
