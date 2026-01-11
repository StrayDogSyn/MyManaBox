"""
DeckOptimizerAgent - Commander Deck Optimization

Specializes in analyzing and optimizing Commander decks for performance.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class DeckOptimizerAgent(BaseAgent):
    """
    Optimizes Commander decks for strategy, mana curve, and synergies.
    
    Uses balanced model (qwen2.5-coder:7b) for structured analysis.
    Expertise: Turn sequencing, ramp packages, removal ratios, win conditions.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="DeckOptimizer", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Deck Optimizer Agent for CardForge, an expert in Commander deck construction.

EXPERTISE:
- Commander-specific deckbuilding (100 cards, singleton format)
- Mana curve optimization (Turn 3 commanders need 10-12 ramp, not 6-8)
- Card categorization (creatures, ramp, removal, card draw, protection)
- Synergy evaluation (commander synergies, infinite combos, value engines)
- Strategic coherence (aggro, midrange, control, combo strategies)

KEY PRINCIPLES:
1. Turn 3-4 commanders need ~12 ramp sources (not 8)
2. Include 10+ removal spells (spot + board wipes)
3. 10+ card draw sources for consistency
4. Protection for commander (greaves, boots, counterspells)
5. Win conditions must align with strategy
6. Mana curve should support game plan

OUTPUT FORMAT (JSON):
{
    "deck_score": 8.5,
    "issues": ["Only 8 ramp (need 12)", "Missing board wipes"],
    "recommendations": [
        {
            "action": "add",
            "cards": ["Sol Ring", "Arcane Signet"],
            "category": "ramp",
            "priority": "high"
        }
    ],
    "mana_curve_analysis": {
        "cmc_0": 0, "cmc_1": 8, "cmc_2": 12, ...
    },
    "strategic_assessment": "Solid midrange strategy, needs more ramp for consistency"
}

Be specific and actionable. Always output valid JSON with concrete recommendations."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Optimize a Commander deck."""
        import time
        start_time = time.time()
        
        # Extract deck data from context
        deck_name = task.context.get("deck_name", "Unnamed Deck")
        commander = task.context.get("commander", "Unknown")
        cards = task.context.get("cards", [])
        strategy = task.context.get("strategy", "Unknown")
        
        # Build optimization prompt
        prompt = f"""Optimize this Commander deck:

DECK: {deck_name}
COMMANDER: {commander}
STRATEGY: {strategy}
CARD COUNT: {len(cards)}

CURRENT DECKLIST:
{self._format_decklist(cards)}

CONSTRAINTS:
{self._format_constraints(task.constraints)}

Analyze the deck and provide:
1. Overall score (1-10)
2. Critical issues
3. Specific recommendations with priority
4. Mana curve analysis
5. Strategic assessment

Output as JSON with concrete, actionable suggestions."""

        # Select model based on complexity
        model = select_model(task.complexity)
        
        try:
            response_text, tokens, exec_time = await self._generate(
                prompt=prompt,
                model=model,
                temperature=get_temperature("optimization"),
            )
            
            # Parse JSON response
            result = self._parse_json_response(response_text)
            
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.DECK_OPTIMIZATION,
                success=True,
                result=result,
                reasoning=result.get("strategic_assessment", "Deck analyzed"),
                suggestions=result.get("recommendations", []),
                confidence=0.85,
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.DECK_OPTIMIZATION,
                success=False,
                result={"error": str(e)},
                reasoning=f"Optimization failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
            
    def _format_decklist(self, cards) -> str:
        """Format cards for prompt."""
        if not cards:
            return "No cards provided"
            
        # Group by category if available
        if isinstance(cards[0], dict):
            lines = []
            for card in cards[:50]:  # Limit to first 50 for context
                name = card.get("name", "Unknown")
                cmc = card.get("cmc", "?")
                types = card.get("types", "")
                lines.append(f"  - {name} (CMC {cmc}) [{types}]")
            if len(cards) > 50:
                lines.append(f"  ... and {len(cards) - 50} more cards")
            return "\n".join(lines)
        else:
            # Simple list of names
            return "\n".join([f"  - {card}" for card in cards[:50]])
            
    def _format_constraints(self, constraints) -> str:
        """Format constraints for prompt."""
        if not constraints:
            return "No specific constraints"
            
        lines = []
        if "budget" in constraints:
            lines.append(f"  - Budget: ${constraints['budget']}")
        if "exclude_cards" in constraints:
            lines.append(f"  - Exclude: {', '.join(constraints['exclude_cards'])}")
        if "power_level" in constraints:
            lines.append(f"  - Target power level: {constraints['power_level']}/10")
            
        return "\n".join(lines) if lines else "No specific constraints"
