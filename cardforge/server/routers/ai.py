from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging

from cardforge.services import DeckService
from cardforge.services.ai.orchestrator import CardForgeOrchestrator
from cardforge.services.ai.base_agent import TaskComplexity

logger = logging.getLogger(__name__)

router = APIRouter()
deck_service = DeckService()

# In a real app, orchestrator might be a singleton dependency
orchestrator = CardForgeOrchestrator()
ollama_available = False

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class DeckAnalysisRequest(BaseModel):
    deck_id: int
    focus: str = "general" # general, mana, synergy, budget

class OptimizeDeckRequest(BaseModel):
    deck_id: int
    budget: Optional[float] = None
    strategy: Optional[str] = None

@router.on_event("startup")
async def startup_event():
    global ollama_available
    try:
        await orchestrator._initialize()
        ollama_available = True
        logger.info("Ollama orchestrator initialized successfully")
    except ConnectionError as e:
        ollama_available = False
        logger.warning(f"Ollama not available: {e}. AI features will be disabled.")
    except Exception as e:
        ollama_available = False
        logger.warning(f"Failed to initialize orchestrator: {e}")

@router.on_event("shutdown")
async def shutdown_event():
    if ollama_available:
        await orchestrator.close()

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    """General chat with the AI router."""
    # This would route to the appropriate agent based on the message
    # For now, we'll just return a placeholder or implement simple routing
    # Ideally, we construct an AgentTask here
    pass # TODO: Implement general chat task creation

@router.post("/analyze/deck")
async def analyze_deck(request: DeckAnalysisRequest):
    """Analyze a deck using AI."""
    deck = await deck_service.get_deck(request.deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    # Format cards for context
    cards = [
        {
            "name": c.card.name,
            "quantity": c.quantity,
            "type": c.card.type_line,
            "cmc": float(c.card.cmc) if c.card.cmc else 0,
            "oracle_text": c.card.oracle_text
        }
        for c in deck.cards
    ]
    
    # We might use MetaAnalyzer or DeckOptimizer here depending on focus
    # For now, let's assume DeckOptimizer for analysis
    response = await orchestrator.optimize_deck(
        deck_name=deck.name,
        commander=deck.commander.name if deck.commander else "Unknown",
        cards=cards,
        strategy=deck.description or "Unknown",
        complexity=TaskComplexity.SIMPLE
    )
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.result.get("error", "Analysis failed"))
        
    return response.result

@router.post("/optimize/deck")
async def optimize_deck(request: OptimizeDeckRequest):
    """Optimize a deck with suggestions."""
    deck = await deck_service.get_deck(request.deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
        
    cards = [
        {
            "name": c.card.name,
            "quantity": c.quantity,
            "type": c.card.type_line,
            "cmc": float(c.card.cmc) if c.card.cmc else 0,
            "oracle_text": c.card.oracle_text
        }
        for c in deck.cards
    ]
    
    response = await orchestrator.optimize_deck(
        deck_name=deck.name,
        commander=deck.commander.name if deck.commander else "Unknown",
        cards=cards,
        strategy=request.strategy or deck.description or "Unknown",
        budget=request.budget,
        complexity=TaskComplexity.MODERATE
    )
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.result.get("error", "Optimization failed"))
        
    return response.result

@router.get("/health")
async def ai_health():
    """Check AI system health."""
    return await orchestrator.health_check()
