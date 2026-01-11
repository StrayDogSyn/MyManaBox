"""
SynergyFinderAgent - Card Synergy and Combo Detection

Finds powerful card interactions, infinite combos, and synergistic packages.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType
from ..model_selection import select_model, get_temperature


class SynergyFinderAgent(BaseAgent):
    """
    Detects card synergies and combo interactions.
    
    Uses balanced model for pattern recognition and combo detection.
    Expertise: Card interactions, infinite combos, value engines, tribal synergies.
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="SynergyFinder", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Synergy Finder Agent for CardForge, an expert in MTG card interactions and combos.

EXPERTISE:
- Infinite combo detection (mana, damage, draw, turns)
- Synergy packages (cards that work well together)
- Value engines (repeatable advantages)
- Tribal synergies (creature type interactions)
- Commander-specific interactions

COMBO TYPES:
1. Infinite Mana: Basalt Monolith + Rings of Brighthearth
2. Infinite Damage: Kiki-Jiki + Pestermite/Deceiver Exarch
3. Infinite Draws: Niv-Mizzet + Curiosity
4. Game-Winning: Thoracle + Demonic Consultation
5. Value Engines: Rhystic Study + many opponents

OUTPUT FORMAT (JSON):
{
    "synergies_found": [
        {
            "cards": ["Kaalia", "Master of Cruelties"],
            "type": "combat_combo",
            "description": "Kaalia cheats MoC, deals 21 commander damage instantly",
            "power_level": 9,
            "pieces_owned": ["Kaalia"]
        }
    ],
    "infinite_combos": [
        {
            "cards": ["Kiki-Jiki", "Pestermite"],
            "result": "Infinite creature tokens",
            "requirements": "Both creatures on board, Kiki untapped"
        }
    ],
    "synergy_packages": [
        {
            "theme": "Reanimator",
            "cards": ["Animate Dead", "Necromancy", "Dance of the Dead"],
            "description": "Cheat big creatures from graveyard"
        }
    ],
    "recommendations": "Add Pestermite to enable Kiki-Jiki combo"
}

Be specific about combo requirements and power levels."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Find synergies and combos in deck."""
        import time
        start_time = time.time()
        
        cards = task.context.get("cards", [])
        commander = task.context.get("commander", "Unknown")
        
        prompt = f"""Find synergies and combos:

COMMANDER: {commander}
DECK CARDS: {len(cards)}

{self._format_card_list(cards)}

Identify:
1. Card synergies (2-3 cards working together)
2. Infinite combos (if any)
3. Value engines
4. Commander-specific interactions
5. Missing combo pieces

Output as JSON with specific card interactions."""

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
                task_type=TaskType.SYNERGY_DETECTION,
                success=True,
                result=result,
                reasoning=result.get("recommendations", "Synergies identified"),
                confidence=0.8,
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.SYNERGY_DETECTION,
                success=False,
                result={"error": str(e)},
                reasoning=f"Detection failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
            
    def _format_card_list(self, cards) -> str:
        """Format card list for synergy analysis."""
        if not cards:
            return "No cards provided"
            
        lines = ["CARDS IN DECK:"]
        for card in cards[:40]:  # Show subset
            if isinstance(card, dict):
                name = card.get("name", "Unknown")
                types = card.get("types", "")
                lines.append(f"  - {name} ({types})")
            else:
                lines.append(f"  - {card}")
                
        if len(cards) > 40:
            lines.append(f"  ... and {len(cards) - 40} more cards")
            
        return "\n".join(lines)
