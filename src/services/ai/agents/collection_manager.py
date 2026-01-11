"""
CollectionManagerAgent - Collection Organization and Management

Manages inventory, detects duplicates, identifies gaps, and suggests organization.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class CollectionManagerAgent(BaseAgent):
    """
    Manages MTG collection organization and inventory.
    
    Uses fast/balanced models for collection analysis.
    Expertise: Organization, duplicate detection, gap analysis, value tracking.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="CollectionManager", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Collection Manager Agent for CardForge, an expert in MTG collection organization.

EXPERTISE:
- Collection organization strategies
- Duplicate detection and consolidation
- Gap analysis (missing staples, incomplete sets)
- Value distribution (high-value cards, bulk)
- Storage and cataloging recommendations

ANALYSIS TYPES:
1. Duplicates: Find cards with >1 copy, suggest which to trade/sell
2. Gaps: Identify missing Commander staples or set completions
3. Value: Highlight high-value cards needing protection
4. Organization: Suggest storage by set, color, type, or value

OUTPUT FORMAT (JSON):
{
    "summary": {
        "total_cards": 1834,
        "unique_cards": 1250,
        "duplicates": 584,
        "total_value": 12450.50
    },
    "duplicates": [
        {"name": "Sol Ring", "quantity": 5, "suggestion": "Keep 3, trade 2"}
    ],
    "gaps": [
        {"category": "Commander staples", "missing": ["Mana Crypt", "Rhystic Study"]}
    ],
    "organization_suggestions": "Organize by color identity for Commander deck building",
    "high_value_cards": [
        {"name": "Gaea's Cradle", "value": 950.00, "note": "Store in binder with insurance"}
    ]
}

Be practical and helpful. Focus on actionable organization strategies."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Analyze and organize collection."""
        import time
        start_time = time.time()
        
        cards = task.context.get("cards", [])
        analysis_type = task.context.get("analysis_type", "full")
        
        prompt = f"""Analyze this MTG collection:

COLLECTION SIZE: {len(cards)} cards
ANALYSIS TYPE: {analysis_type}

{self._format_collection_summary(cards)}

Provide:
1. Collection summary (unique, duplicates, value)
2. Duplicate analysis with suggestions
3. Gap analysis (missing staples)
4. High-value cards needing protection
5. Organization recommendations

Output as JSON with practical suggestions."""

        model = select_model(task.complexity)
        
        try:
            response_text, tokens, exec_time = await self._generate(
                prompt=prompt,
                model=model,
                temperature=get_temperature("analysis"),
            )
            
            result = self._parse_json_response(response_text)
            
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.COLLECTION_MANAGEMENT,
                success=True,
                result=result,
                reasoning=result.get("organization_suggestions", "Collection analyzed"),
                confidence=0.9,
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.COLLECTION_MANAGEMENT,
                success=False,
                result={"error": str(e)},
                reasoning=f"Analysis failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
            
    def _format_collection_summary(self, cards) -> str:
        """Format collection summary for prompt."""
        if not cards:
            return "No cards in collection"
            
        # Basic stats
        total = len(cards)
        sample = cards[:20] if len(cards) > 20 else cards
        
        lines = [f"SAMPLE CARDS ({len(sample)} shown):"]
        for card in sample:
            if isinstance(card, dict):
                name = card.get("name", "Unknown")
                qty = card.get("quantity", 1)
                price = card.get("price_usd", 0)
                lines.append(f"  - {name} x{qty} (${price:.2f})")
                
        return "\n".join(lines)
