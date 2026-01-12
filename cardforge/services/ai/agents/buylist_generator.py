"""
BuyListGeneratorAgent - Shopping List Creation

Generates prioritized buy lists based on deck needs and budget constraints.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class BuyListGeneratorAgent(BaseAgent):
    """
    Creates prioritized shopping lists for deck completion.
    
    Uses balanced model for budget optimization and prioritization.
    Expertise: Budget allocation, priority ranking, alternative suggestions.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="BuyListGenerator", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the BuyList Generator Agent for CardForge, an expert in budget-conscious MTG purchasing.

EXPERTISE:
- Priority ranking (critical cards first)
- Budget allocation (maximize value per dollar)
- Alternative suggestions (budget options for expensive cards)
- TCGPlayer/vendor price comparison strategy
- Timing recommendations (buy before/after events)

PRIORITY LEVELS:
1. Commander (highest - deck identity)
2. Ramp (turn 1-3 plays enable strategy)
3. Win conditions (need path to victory)
4. Card draw (consistency)
5. Removal (interaction)
6. Protection (save commander)
7. Utility lands (nice-to-have)
8. Tech cards (meta-dependent)

OUTPUT FORMAT (JSON):
{
    "total_cost": 245.50,
    "budget_available": 200.00,
    "buy_now": [
        {
            "card": "Sol Ring",
            "priority": 1,
            "price": 3.50,
            "reason": "Essential ramp, cheap staple"
        }
    ],
    "budget_alternatives": [
        {
            "expensive": "Mana Crypt ($900)",
            "budget": "Sol Ring ($3.50)",
            "trade_off": "Slightly slower ramp"
        }
    ],
    "defer_to_later": ["Luxury lands", "Foil upgrades"],
    "total_allocated": 198.75
}

Be realistic with budgets. Prioritize function over flashiness."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Generate prioritized buy list."""
        import time
        start_time = time.time()
        
        missing_cards = task.context.get("missing_cards", [])
        budget = task.constraints.get("budget", 100) if task.constraints else 100
        deck_strategy = task.context.get("strategy", "Unknown")
        
        prompt = f"""Create a prioritized buy list:

DECK STRATEGY: {deck_strategy}
BUDGET: ${budget}
MISSING CARDS: {len(missing_cards)}

{self._format_missing_cards(missing_cards)}

Provide:
1. Total cost if buying all cards
2. Prioritized "buy now" list within budget
3. Budget alternatives for expensive cards
4. Cards to defer to later purchases
5. Total budget allocation

Output as JSON with clear priorities and reasoning."""

        model = select_model(task.complexity)
        
        try:
            response_text, tokens, exec_time = await self._generate(
                prompt=prompt,
                model=model,
                temperature=get_temperature("optimization"),
            )
            
            result = self._parse_json_response(response_text)
            
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.BUYLIST_GENERATION,
                success=True,
                result=result,
                reasoning=f"Generated buy list for ${budget} budget",
                confidence=0.85,
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.BUYLIST_GENERATION,
                success=False,
                result={"error": str(e)},
                reasoning=f"Generation failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
            
    def _format_missing_cards(self, cards) -> str:
        """Format missing cards with prices."""
        if not cards:
            return "No missing cards specified"
            
        lines = ["MISSING CARDS:"]
        for card in cards[:30]:
            if isinstance(card, dict):
                name = card.get("name", "Unknown")
                price = card.get("price_usd", 0)
                category = card.get("category", "unknown")
                lines.append(f"  - {name}: ${price:.2f} ({category})")
                
        return "\n".join(lines)
