from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from cardforge.services import DeckService

router = APIRouter()
deck_service = DeckService()

class CreateDeckRequest(BaseModel):
    name: str
    format: str
    description: Optional[str] = None
    commander: Optional[str] = None

class AddCardRequest(BaseModel):
    card_name: str
    quantity: int = 1
    is_sideboard: bool = False
    category: Optional[str] = None

@router.post("/")
async def create_deck(request: CreateDeckRequest):
    """Create a new deck."""
    deck = await deck_service.create_deck(
        name=request.name,
        format=request.format,
        description=request.description,
        commander_name=request.commander
    )
    return {"id": deck.id, "name": deck.name}

@router.get("/{deck_id}")
async def get_deck(deck_id: int):
    """Get deck details and cards."""
    deck = await deck_service.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    return {
        "id": deck.id,
        "name": deck.name,
        "format": deck.format,
        "cards": [
            {
                "name": c.card.name,
                "quantity": c.quantity,
                "cmc": float(c.card.cmc) if c.card.cmc is not None else 0,
                "type": c.card.type_line
            }
            for c in deck.cards
        ]
    }

@router.post("/{deck_id}/cards")
async def add_card_to_deck(deck_id: int, request: AddCardRequest):
    """Add card to deck."""
    result = await deck_service.add_card(
        deck_id=deck_id,
        card_name=request.card_name,
        quantity=request.quantity,
        is_sideboard=request.is_sideboard,
        category=request.category
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Card not found")
        
    return {"status": "success"}

@router.get("/{deck_id}/analysis")
async def analyze_deck(deck_id: int):
    """Get deck analysis (mana curve, etc)."""
    return await deck_service.analyze_deck(deck_id)

@router.get("/{deck_id}/missing")
async def get_missing_cards(deck_id: int):
    """Get missing cards for deck."""
    missing = await deck_service.get_missing_cards(deck_id)
    return [
        {
            "name": m.card.name,
            "needed": m.quantity_needed
        }
        for m in missing
    ]
