"""
MetaAnalyzerAgent - Competitive Meta Analysis

Analyzes competitive metagame trends, deck archetypes, and win rates.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class MetaAnalyzerAgent(BaseAgent):
    """
    Analyzes competitive Magic metagame and trends.
    
    Uses powerful model (llama3.1:70b) for strategic meta analysis.
    Expertise: Tournament results, deck archetypes, matchup analysis.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="MetaAnalyzer", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Meta Analyzer Agent for CardForge, an expert in competitive MTG metagame analysis.

EXPERTISE:
- Tournament meta trends (Standard, Modern, Pioneer, Commander)
- Deck archetype classification (aggro, midrange, control, combo)
- Matchup analysis (favorable/unfavorable matchups)
- Sideboard strategies
- Power level assessment (casual to cEDH)

META FACTORS:
1. Format bans/unbans shift metagame dramatically
2. New set releases introduce new archetypes
3. Pro Tour results drive deck adoption
4. Local metas differ from global trends
5. Commander is multiplayer (different dynamics)

OUTPUT FORMAT (JSON):
{
    "meta_snapshot": {
        "format": "Commander",
        "top_archetypes": ["Stax", "Fast Combo", "Midrange Value"],
        "emerging_threats": ["Kinnan Combo", "Tymna/Kraum Tempo"]
    },
    "deck_positioning": {
        "favorable_matchups": ["Aggro decks", "Big mana"],
        "unfavorable_matchups": ["Fast combo", "Stax"],
        "win_rate_estimate": "55-60%"
    },
    "recommendations": [
        "Add more interaction for combo matchups",
        "Include graveyard hate for Muldrotha strategies"
    ],
    "meta_prediction": "Expect more stax as combo increases"
}

Be strategic and forward-thinking. Consider multiplayer dynamics for Commander."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Analyze competitive metagame."""
        import time
        start_time = time.time()
        
        format_name = task.context.get("format", "Commander")
        deck_archetype = task.context.get("archetype", "Unknown")
        
        prompt = f"""Analyze the competitive meta:

FORMAT: {format_name}
DECK ARCHETYPE: {deck_archetype}

Provide:
1. Current meta snapshot (top archetypes)
2. Deck positioning (favorable/unfavorable matchups)
3. Strategic recommendations
4. Meta predictions for next 3-6 months

Output as JSON with strategic insights."""

        # Use powerful model for complex strategic analysis
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
                task_type=TaskType.META_ANALYSIS,
                success=True,
                result=result,
                reasoning=result.get("meta_prediction", "Meta analyzed"),
                confidence=0.7,  # Meta is always uncertain
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.META_ANALYSIS,
                success=False,
                result={"error": str(e)},
                reasoning=f"Analysis failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
