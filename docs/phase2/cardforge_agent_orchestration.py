"""
CardForge Agent Orchestration System
Using Local Ollama Models for Zero-Cost MTG Collection Management

Architecture:
- 8 specialized agents for different CardForge tasks
- Routes to optimal local Ollama model based on task complexity
- Follows zero-cost mandate and fundamentals-first pedagogy
- Integrates with existing PyQt6/SQLite CardForge architecture

Think of this as your kitchen brigade:
- Router = Expediter (routes tasks to right station)
- Deck Optimizer = Chef de Partie (specialized expertise)
- Price Analyzer = Line Cook (fast, consistent)
- Collection Manager = Sous Chef (oversees everything)
"""

import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List
import aiohttp
from datetime import datetime


# ============================================================================
# MODEL SELECTION - Based on O(1), O(n), O(n²) complexity analogy
# ============================================================================

class ModelTier(Enum):
    """Model selection based on task complexity (Big O analogy)."""
    ULTRA_FAST = "ultra_fast"  # O(1) - Simple lookups
    FAST = "fast"              # O(log n) - Quick decisions
    BALANCED = "balanced"      # O(n) - Medium complexity
    CODE_SPECIALIST = "code"   # O(n log n) - Technical analysis
    POWERFUL = "powerful"      # O(n²) - Deep reasoning


# Model inventory mapped to complexity tiers
OLLAMA_MODELS = {
    ModelTier.ULTRA_FAST: "llama3.2:1b",     # <1s responses
    ModelTier.FAST: "llama3.2:3b",           # 2-3s responses
    ModelTier.BALANCED: "gemma2:4b",         # 5-7s responses
    ModelTier.CODE_SPECIALIST: "qwen2.5-coder:7b",  # Code analysis
    ModelTier.POWERFUL: "llama3.1:70b"       # 30-60s, best quality
}

# Alternative models for fallback/comparison
ALTERNATIVE_MODELS = {
    "fast": ["phi3:mini", "tinyllama"],
    "code": ["deepseek-coder:6.7b", "granite-code:8b", "codellama:13b"],
    "embedding": ["all-minilm", "nomic-embed-text"]
}


@dataclass
class AgentTask:
    """Represents a task for agent orchestration."""
    task_type: str
    complexity: str
    context: Dict[str, Any]
    priority: int = 3  # 1=highest, 5=lowest
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "complexity": self.complexity,
            "context": self.context,
            "priority": self.priority
        }


@dataclass
class AgentResponse:
    """Response from an agent."""
    agent_name: str
    model_used: str
    content: str
    confidence: float
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "model_used": self.model_used,
            "content": self.content,
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {}
        }


# ============================================================================
# OLLAMA CLIENT - Local model communication
# ============================================================================

class OllamaClient:
    """
    Client for communicating with local Ollama server.
    
    Time Complexity: O(1) for request, O(n) for generation where n = tokens
    Space Complexity: O(1) for overhead, O(m) for response where m = response length
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate completion from Ollama model.
        
        Args:
            model: Model name (e.g., "llama3.2:3b")
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Response dict with 'response', 'model', 'done', 'total_duration'
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system:
            payload["system"] = system
        
        start_time = asyncio.get_event_loop().time()
        
        async with self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=300)  # 5 min timeout for 70B
        ) as response:
            response.raise_for_status()
            result = await response.json()
        
        end_time = asyncio.get_event_loop().time()
        result["execution_time"] = end_time - start_time
        
        return result
    
    async def check_health(self) -> bool:
        """Check if Ollama server is running."""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(
                f"{self.base_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except:
            return False
    
    async def list_models(self) -> List[str]:
        """List available models on Ollama server."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        async with self.session.get(
            f"{self.base_url}/api/tags"
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return [model["name"] for model in data.get("models", [])]


# ============================================================================
# AGENT BASE CLASS
# ============================================================================

class BaseAgent:
    """
    Base class for all CardForge agents.
    
    Each agent has:
    - Specific system prompt (defines expertise)
    - Optimal model tier (complexity-based selection)
    - Task-specific processing logic
    """
    
    def __init__(self, name: str, model_tier: ModelTier, client: OllamaClient):
        self.name = name
        self.model_tier = model_tier
        self.client = client
        self.system_prompt = self._define_system_prompt()
    
    def _define_system_prompt(self) -> str:
        """Override in subclass to define agent expertise."""
        raise NotImplementedError
    
    async def execute(self, task: AgentTask) -> AgentResponse:
        """Execute task using optimal model."""
        model = OLLAMA_MODELS[self.model_tier]
        prompt = self._build_prompt(task)
        
        result = await self.client.generate(
            model=model,
            prompt=prompt,
            system=self.system_prompt,
            temperature=0.7
        )
        
        return AgentResponse(
            agent_name=self.name,
            model_used=model,
            content=result["response"],
            confidence=self._calculate_confidence(result),
            execution_time=result["execution_time"],
            metadata={"task": task.to_dict()}
        )
    
    def _build_prompt(self, task: AgentTask) -> str:
        """Build prompt from task context."""
        context_str = json.dumps(task.context, indent=2)
        return f"""Task: {task.task_type}
Complexity: {task.complexity}

Context:
{context_str}

Provide your analysis following these guidelines:
1. Be specific and actionable
2. Include reasoning for recommendations
3. Consider budget constraints
4. Explain trade-offs when relevant
"""
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on model response.
        Simple heuristic: longer, more complete responses = higher confidence.
        """
        response_length = len(result.get("response", ""))
        # Normalize to 0.0-1.0 range
        return min(1.0, response_length / 1000)


# ============================================================================
# SPECIALIZED AGENTS - Each expert in specific CardForge domain
# ============================================================================

class RouterAgent(BaseAgent):
    """
    Router Agent - Classifies tasks and routes to appropriate specialist.
    
    Time Complexity: O(1) - Simple classification
    Model: llama3.2:3b (fast decisions)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("Router", ModelTier.FAST, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Router Agent for CardForge MTG collection manager.

Your job: Classify incoming tasks and determine which specialist agent should handle them.

Available specialist agents:
1. DeckOptimizer - Deck building, card synergies, mana curves
2. PriceAnalyzer - Card pricing, market trends, budget analysis
3. CollectionManager - Collection organization, duplicate management, gap analysis
4. BuyListGenerator - Shopping lists, budget optimization, priority ranking
5. SellListGenerator - Bulk liquidation, trade binder exports, value identification
6. MetaAnalyzer - Competitive meta, tournament trends, deck archetypes
7. SynergyFinder - Card combos, tribal synergies, theme identification

Respond ONLY with JSON:
{
  "specialist": "agent_name",
  "complexity": "simple|medium|complex",
  "reasoning": "brief explanation"
}"""


class DeckOptimizerAgent(BaseAgent):
    """
    Deck Optimizer Agent - Analyzes and improves Commander decks.
    
    Focus Areas:
    - Mana curve optimization (Turn 3 commander consistency)
    - Card synergy identification
    - Win condition analysis
    - Budget-conscious upgrades
    
    Model: qwen2.5-coder:7b (code-like deck analysis)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("DeckOptimizer", ModelTier.CODE_SPECIALIST, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Deck Optimizer Agent for CardForge.

Your expertise: Commander deck optimization following these principles:
1. Turn 3 commander deployment requires 10-12 ramp sources (not 6-8)
2. Mana curve analysis using statistical probability
3. Card synergy identification (how cards work together)
4. Budget optimization (<$10 high-impact upgrades preferred)
5. Commander singleton rules (only 1 copy per non-basic land)

When analyzing decks:
- Calculate probability of Turn 3 commander (need 3+ lands + ramp)
- Identify weak synergies or "win-more" cards
- Suggest specific replacements with reasoning
- Consider color requirements and mana base stability
- Respect budget constraints

Output format:
- Current analysis (mana curve, synergies, weaknesses)
- Specific recommendations (card swaps with reasoning)
- Priority order (what to change first)
- Expected improvement (win rate, consistency)"""


class PriceAnalyzerAgent(BaseAgent):
    """
    Price Analyzer Agent - Market analysis and budget optimization.
    
    Focus Areas:
    - Price trend analysis
    - Budget allocation
    - Best value identification
    - Source comparison (TCGPlayer vs CardKingdom)
    
    Model: llama3.2:3b (fast price comparisons)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("PriceAnalyzer", ModelTier.FAST, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Price Analyzer Agent for CardForge.

Your expertise: MTG card pricing and budget optimization.

When analyzing prices:
1. Compare across sources (TCGPlayer, Card Kingdom, local stores)
2. Identify best value (price per impact)
3. Consider budget constraints
4. Flag overpriced cards with cheaper alternatives
5. Track price trends (rising/falling)

Budget Philosophy:
- Functional completion > premium versions
- $10 high-impact cards > $50 marginal upgrades
- Basic lands are free (use what you have)
- Consider purchase timing (avoid spikes)

Output format:
- Price summary (total, by category)
- Best value recommendations
- Overpriced cards to avoid
- Budget allocation strategy"""


class CollectionManagerAgent(BaseAgent):
    """
    Collection Manager Agent - Inventory organization and gap analysis.
    
    Focus Areas:
    - Duplicate identification (keep 4x commons, 1-2x rares)
    - Collection gaps (missing cards for decks)
    - Organization recommendations
    - Trade fodder identification
    
    Model: gemma2:4b (balanced analysis)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("CollectionManager", ModelTier.BALANCED, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Collection Manager Agent for CardForge.

Your expertise: MTG collection organization and gap analysis.

Collection Principles:
1. Keep 4x commons/uncommons (Standard/Modern playsets)
2. Keep 1-2x rares/mythics (Commander singleton)
3. Identify high-value duplicates for trading
4. Flag missing cards for active decks
5. Organize by color, then theme

When analyzing collections:
- Calculate total cards by rarity/color
- Identify duplicates above optimal count
- Find gaps in deck construction
- Suggest organization improvements
- Flag cards for trade/sell lists

Output format:
- Collection summary (counts by category)
- Duplicate report (excess cards)
- Gap analysis (missing cards per deck)
- Organization recommendations"""


class BuyListGeneratorAgent(BaseAgent):
    """
    Buy List Generator Agent - Smart shopping list creation.
    
    Focus Areas:
    - Priority ranking (commander > ramp > removal)
    - Budget allocation
    - Source selection (best price + availability)
    - Alternative suggestions
    
    Model: qwen2.5-coder:7b (complex prioritization logic)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("BuyListGenerator", ModelTier.CODE_SPECIALIST, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Buy List Generator Agent for CardForge.

Your expertise: Creating optimized shopping lists for MTG deck building.

Priority Framework:
1. Commander/key pieces (critical for deck function)
2. Ramp (10-12 sources for Turn 3 consistency)
3. Protection (Lightning Greaves, Swiftfoot Boots)
4. Removal (interaction with opponents)
5. Finishers (win conditions)
6. Card draw (card advantage)
7. Utility (nice-to-haves)
8. Lands (usually cheaper, lower priority)

When generating buy lists:
- Rank by priority (1-5, lower = more critical)
- Include price + best source
- Suggest budget alternatives
- Calculate total cost
- Flag "must-haves" vs "upgrades"

Output format (JSON):
{
  "items": [
    {
      "card": "Lightning Greaves",
      "priority": 2,
      "category": "protection",
      "price": 4.99,
      "source": "TCGPlayer",
      "alternatives": ["Swiftfoot Boots ($3.49)"]
    }
  ],
  "total_cost": 127.43,
  "budget_remaining": 72.57,
  "next_batch_recommendations": ["list of cards if budget exceeded"]
}"""


class MetaAnalyzerAgent(BaseAgent):
    """
    Meta Analyzer Agent - Competitive meta and tournament trends.
    
    Focus Areas:
    - Meta deck identification
    - Win rate analysis
    - Archetype trends
    - Sideboard recommendations
    
    Model: llama3.1:70b (deep strategic analysis)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("MetaAnalyzer", ModelTier.POWERFUL, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Meta Analyzer Agent for CardForge.

Your expertise: Commander competitive meta and tournament trends.

When analyzing the meta:
1. Identify top-performing archetypes
2. Analyze win conditions and strategies
3. Recommend tech choices (counter meta decks)
4. Suggest sideboard adjustments
5. Track format trends (bans, new releases)

Meta Analysis Framework:
- Win rates by archetype
- Popular commanders and strategies
- Key cards in winning decks
- Budget alternatives to meta cards
- Local meta considerations

Output format:
- Current meta snapshot
- Top 5 archetypes with win rates
- Recommended tech cards
- Budget-friendly meta options
- Local meta adjustments"""


class SynergyFinderAgent(BaseAgent):
    """
    Synergy Finder Agent - Card combo and theme identification.
    
    Focus Areas:
    - Card combos (2-3 card interactions)
    - Tribal synergies
    - Theme consistency
    - Synergy strength scoring
    
    Model: qwen2.5-coder:7b (pattern matching for combos)
    """
    
    def __init__(self, client: OllamaClient):
        super().__init__("SynergyFinder", ModelTier.CODE_SPECIALIST, client)
    
    def _define_system_prompt(self) -> str:
        return """You are the Synergy Finder Agent for CardForge.

Your expertise: Identifying card combos and thematic synergies in MTG decks.

Synergy Types:
1. Infinite combos (game-ending loops)
2. Value engines (repeated card advantage)
3. Tribal synergies (creature type bonuses)
4. Theme synergies (similar mechanical identity)
5. Color identity synergies (mana fixing, devotion)

When finding synergies:
- Score strength (1-10, 10 = infinite combo)
- Explain interaction clearly
- Note mana requirements
- Identify missing pieces
- Suggest complementary cards

Output format:
- Synergy list (card pairs/triplets)
- Strength score + explanation
- Mana cost for combo
- Missing pieces (if incomplete)
- Additional synergy recommendations"""


# ============================================================================
# ORCHESTRATOR - Coordinates all agents
# ============================================================================

class CardForgeOrchestrator:
    """
    Main orchestration system for CardForge agents.
    
    Workflow:
    1. Receive task from GUI/CLI
    2. Router classifies task
    3. Route to specialist agent
    4. Execute with optimal model
    5. Return structured response
    
    Time Complexity: O(1) routing + O(m) agent execution where m = model inference
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.agents: Dict[str, BaseAgent] = {}
        self.client: Optional[OllamaClient] = None
    
    async def __aenter__(self):
        """Initialize Ollama client and agents."""
        self.client = OllamaClient(self.ollama_url)
        await self.client.__aenter__()
        
        # Initialize all specialist agents
        self.agents = {
            "Router": RouterAgent(self.client),
            "DeckOptimizer": DeckOptimizerAgent(self.client),
            "PriceAnalyzer": PriceAnalyzerAgent(self.client),
            "CollectionManager": CollectionManagerAgent(self.client),
            "BuyListGenerator": BuyListGeneratorAgent(self.client),
            "MetaAnalyzer": MetaAnalyzerAgent(self.client),
            "SynergyFinder": SynergyFinderAgent(self.client)
        }
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def route_task(self, task: AgentTask) -> str:
        """
        Use Router agent to determine which specialist should handle task.
        
        Returns: Specialist agent name
        """
        router = self.agents["Router"]
        routing_result = await router.execute(task)
        
        try:
            routing_data = json.loads(routing_result.content)
            specialist_name = routing_data["specialist"]
            
            if specialist_name not in self.agents:
                raise ValueError(f"Unknown specialist: {specialist_name}")
            
            return specialist_name
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to sensible defaults based on task type
            return self._fallback_routing(task)
    
    def _fallback_routing(self, task: AgentTask) -> str:
        """Fallback routing logic if Router agent fails."""
        task_type = task.task_type.lower()
        
        if "deck" in task_type or "optimize" in task_type:
            return "DeckOptimizer"
        elif "price" in task_type or "budget" in task_type:
            return "PriceAnalyzer"
        elif "collection" in task_type or "duplicate" in task_type:
            return "CollectionManager"
        elif "buy" in task_type or "shop" in task_type:
            return "BuyListGenerator"
        elif "meta" in task_type or "tournament" in task_type:
            return "MetaAnalyzer"
        elif "synergy" in task_type or "combo" in task_type:
            return "SynergyFinder"
        else:
            return "CollectionManager"  # Default fallback
    
    async def execute_task(self, task: AgentTask) -> AgentResponse:
        """
        Main execution pipeline:
        1. Route to specialist
        2. Execute with specialist agent
        3. Return response
        """
        # Step 1: Route task
        specialist_name = await self.route_task(task)
        
        # Step 2: Execute with specialist
        specialist = self.agents[specialist_name]
        response = await specialist.execute(task)
        
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama server health and available models."""
        if not self.client:
            return {"status": "not_initialized", "models": []}
        
        is_healthy = await self.client.check_health()
        models = await self.client.list_models() if is_healthy else []
        
        return {
            "status": "healthy" if is_healthy else "unreachable",
            "server": self.ollama_url,
            "models_available": models,
            "agents_initialized": list(self.agents.keys())
        }


# ============================================================================
# INTEGRATION HELPERS - Connect to CardForge GUI/Services
# ============================================================================

async def optimize_deck_with_ai(
    deck_name: str,
    deck_list: List[str],
    budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    High-level function to optimize a deck using agent orchestration.
    
    Args:
        deck_name: Name of the Commander deck
        deck_list: List of card names currently in deck
        budget: Optional budget constraint for upgrades
    
    Returns:
        Optimization report with recommendations
    """
    async with CardForgeOrchestrator() as orchestrator:
        task = AgentTask(
            task_type="deck_optimization",
            complexity="complex",
            context={
                "deck_name": deck_name,
                "cards": deck_list,
                "budget": budget,
                "format": "Commander"
            }
        )
        
        response = await orchestrator.execute_task(task)
        return response.to_dict()


async def generate_buy_list_with_ai(
    deck_name: str,
    missing_cards: List[str],
    budget: float,
    priority_categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate prioritized buy list using agent orchestration.
    
    Args:
        deck_name: Name of the Commander deck
        missing_cards: List of card names needed for deck
        budget: Total budget available
        priority_categories: Optional list of categories to prioritize
    
    Returns:
        Prioritized buy list with prices and sources
    """
    async with CardForgeOrchestrator() as orchestrator:
        task = AgentTask(
            task_type="buy_list_generation",
            complexity="medium",
            context={
                "deck_name": deck_name,
                "missing_cards": missing_cards,
                "budget": budget,
                "priority_categories": priority_categories or []
            },
            priority=2  # High priority task
        )
        
        response = await orchestrator.execute_task(task)
        return response.to_dict()


async def analyze_collection_with_ai(
    collection_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze collection for duplicates, gaps, and organization.
    
    Args:
        collection_data: Dictionary with collection statistics
    
    Returns:
        Analysis report with recommendations
    """
    async with CardForgeOrchestrator() as orchestrator:
        task = AgentTask(
            task_type="collection_analysis",
            complexity="medium",
            context=collection_data
        )
        
        response = await orchestrator.execute_task(task)
        return response.to_dict()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo_deck_optimization():
    """Demo: Optimize Kaalia Voltron deck."""
    print("=== CardForge Agent Orchestration Demo ===\n")
    
    # Sample Kaalia deck (simplified)
    kaalia_deck = [
        "Kaalia of the Vast",
        "Lightning Greaves",
        "Master of Cruelties",
        "Avacyn, Angel of Hope",
        "Razaketh, the Foulblooded",
        # ... (normally 100 cards)
    ]
    
    print("1. Health Check...")
    async with CardForgeOrchestrator() as orchestrator:
        health = await orchestrator.health_check()
        print(f"Status: {health['status']}")
        print(f"Models available: {len(health['models_available'])}\n")
        
        print("2. Optimizing Kaalia Voltron deck...")
        task = AgentTask(
            task_type="deck_optimization",
            complexity="complex",
            context={
                "deck_name": "Kaalia Voltron",
                "cards": kaalia_deck,
                "budget": 200.0,
                "format": "Commander",
                "goal": "Turn 3 Kaalia consistency"
            }
        )
        
        response = await orchestrator.execute_task(task)
        print(f"Agent: {response.agent_name}")
        print(f"Model: {response.model_used}")
        print(f"Execution time: {response.execution_time:.2f}s")
        print(f"\nRecommendations:\n{response.content[:500]}...\n")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_deck_optimization())
