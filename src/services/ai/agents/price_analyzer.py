"""
PriceAnalyzerAgent - Market Pricing Analysis

Analyzes card prices, market trends, and investment opportunities.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class PriceAnalyzerAgent(BaseAgent):
    """
    Analyzes MTG card prices and market trends.
    
    Uses balanced model for market analysis and trend detection.
    Expertise: Price trends, reprints, speculation, value tracking.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="PriceAnalyzer", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Price Analyzer Agent for CardForge, an expert in MTG market analysis.

EXPERTISE:
- Price trend analysis (daily, weekly, monthly changes)
- Reprint impact assessment
- Format legality effects on pricing
- Speculation opportunities
- Value retention analysis
- Budget vs. premium alternatives

KEY FACTORS:
1. Format bans/unbans cause major price swings
2. Reprints in Commander products reduce prices 20-50%
3. Reserved List cards maintain/increase value
4. Meta shifts drive demand (competitive formats)
5. Foils and special editions command premiums

OUTPUT FORMAT (JSON):
{
    "analysis": {
        "current_value": 1234.56,
        "trend": "increasing",
        "confidence": 0.8
    },
    "price_changes": [
        {"card": "Sol Ring", "change_percent": 5.2, "reason": "Commander demand"}
    ],
    "opportunities": [
        {"card": "Rhystic Study", "action": "sell", "reason": "Peak price, reprint likely"}
    ],
    "recommendations": "Hold Reserved List cards, sell recent spikes before reprint"
}

Be data-driven and realistic. Avoid speculation without justification."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Analyze card prices and trends."""
        import time
        start_time = time.time()
        
        cards = task.context.get("cards", [])
        timeframe = task.context.get("timeframe", "30 days")
        
        prompt = f"""Analyze prices for this MTG collection:

TIMEFRAME: {timeframe}
CARDS: {len(cards)} cards

PRICE DATA:
{self._format_price_data(cards)}

Provide:
1. Overall collection value and trend
2. Significant price changes with explanations
3. Investment opportunities (buy/sell/hold)
4. Recommendations for optimizing value

Output as JSON with actionable insights."""

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
                task_type=TaskType.PRICE_ANALYSIS,
                success=True,
                result=result,
                reasoning=result.get("recommendations", "Price analysis complete"),
                confidence=0.75,
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.PRICE_ANALYSIS,
                success=False,
                result={"error": str(e)},
                reasoning=f"Analysis failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
            
    def _format_price_data(self, cards) -> str:
        """Format card price data for prompt."""
        if not cards:
            return "No cards provided"
            
        lines = []
        for card in cards[:30]:  # Limit for context
            if isinstance(card, dict):
                name = card.get("name", "Unknown")
                price = card.get("price_usd", 0)
                lines.append(f"  - {name}: ${price:.2f}")
                
        return "\n".join(lines) if lines else "No price data available"
