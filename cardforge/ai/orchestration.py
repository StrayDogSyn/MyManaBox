"""
CardForge AI Orchestration Engine

Coordinates specialized agents for deck optimization, collection management,
price analysis, and meta-game insights using local Ollama models.

Architecture:
  - Router: Classifies tasks and routes to specialized agents
  - DeckOptimizer: Mana curve, ramp analysis, card recommendations
  - PriceAnalyzer: Card valuation, market trends
  - CollectionManager: Inventory tracking, duplicates, gaps
  - BuyListGenerator: Shopping list with priorities
  - MetaAnalyzer: Competitive format analysis
  - SynergyFinder: Card combo and synergy detection
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp


class TaskType(Enum):
    """Task classification for routing."""
    DECK_OPTIMIZATION = "deck_optimization"
    PRICE_ANALYSIS = "price_analysis"
    COLLECTION_MANAGEMENT = "collection_management"
    BUY_LIST_GENERATION = "buy_list_generation"
    META_ANALYSIS = "meta_analysis"
    SYNERGY_FINDING = "synergy_finding"
    UNKNOWN = "unknown"


@dataclass
class ModelConfig:
    """Configuration for an AI model."""
    model: str
    temperature: float
    max_tokens: int
    timeout: int = 60


@dataclass
class OrchestrationResult:
    """Result from orchestration task."""
    success: bool
    agent_name: str
    task_type: TaskType
    result: str
    reasoning: Optional[str] = None
    execution_time: float = 0.0
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None


DEFAULT_AGENT_MODEL = "qwen2.5-coder:7b"


class OllamaClient:
    """Client for communicating with local Ollama instance."""
    
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 60):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama server URL
            timeout: Request timeout in seconds
        """
        self.host = host
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 2000,
    ) -> Tuple[str, Optional[int]]:
        """
        Generate text using Ollama model.
        
        Time Complexity: O(n) where n is token generation count
        Space Complexity: O(n) for storing response
        
        Args:
            model: Model name (e.g., "llama3.2:3b")
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Tuple of (generated_text, token_count)
        
        Raises:
            RuntimeError: If Ollama service unavailable
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
        
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False,
        }
        
        try:
            async with self.session.post(
                url, json=payload, timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"Ollama error: {response.status} - {await response.text()}"
                    )
                data = await response.json()
                return data.get("response", ""), data.get("eval_count")
        except asyncio.TimeoutError:
            raise RuntimeError(f"Ollama request timeout after {self.timeout}s")
        except aiohttp.ClientError as e:
            raise RuntimeError(f"Failed to connect to Ollama at {self.host}: {e}")
    
    async def health_check(self) -> bool:
        """Check if Ollama service is available."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context.")
        
        try:
            async with self.session.get(
                f"{self.host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False


class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        client: OllamaClient,
    ):
        """
        Initialize agent.
        
        Args:
            name: Agent identifier
            model_config: Model configuration
            client: Ollama client instance
        """
        self.name = name
        self.model_config = model_config
        self.client = client
    
    @abstractmethod
    async def execute(self, task: str, **kwargs) -> str:
        """
        Execute specialized task.
        
        Args:
            task: Task description
            **kwargs: Task-specific parameters
        
        Returns:
            Agent response/analysis
        """
        pass
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for agent. Override in subclasses."""
        return f"You are {self.name}, a specialized AI agent for CardForge."
    
    async def _generate(self, prompt: str) -> str:
        """
        Generate response using Ollama.
        
        Time Complexity: O(n) where n is response length
        Space Complexity: O(n) for response storage
        """
        response, _ = await self.client.generate(
            self.model_config.model,
            prompt,
            self.model_config.temperature,
            self.model_config.max_tokens,
        )
        return response.strip()


class DefaultAgent(BaseAgent):
    """Fallback agent for unclassified tasks."""

    def _build_system_prompt(self) -> str:
        return (
            "You are the default CardForge agent. Handle general MTG tasks, "
            "delegate-style reasoning, and provide concise, actionable answers."
        )

    async def execute(self, task: str, **kwargs) -> str:
        prompt = f"{self._build_system_prompt()}\n\nTask: {task}"
        return await self._generate(prompt)


class TaskRouter(BaseAgent):
    """Routes tasks to appropriate specialized agents."""
    
    def _build_system_prompt(self) -> str:
        return """You are TaskRouter, an expert at classifying CardForge tasks.
Analyze the user's request and determine which agent should handle it.

Respond with ONLY the agent type in brackets, e.g.: [DECK_OPTIMIZATION]

Categories:
- [DECK_OPTIMIZATION]: Optimize deck lists, mana curves, ramp analysis
- [PRICE_ANALYSIS]: Card prices, market trends, valuation
- [COLLECTION_MANAGEMENT]: Inventory, duplicates, organization
- [BUY_LIST_GENERATION]: Shopping lists, budget allocation
- [META_ANALYSIS]: Competitive format, metagame insights
- [SYNERGY_FINDING]: Card combos, synergies, interactions
- [UNKNOWN]: Cannot classify"""
    
    async def execute(self, task: str, **kwargs) -> TaskType:
        """
        Classify task and return appropriate task type.
        
        Time Complexity: O(1) for routing logic
        Space Complexity: O(1)
        """
        prompt = f"{self._build_system_prompt()}\n\nUser request: {task}"
        response = await self._generate(prompt)
        
        # Parse response for task type
        response_upper = response.upper()
        if "DECK_OPTIMIZATION" in response_upper:
            return TaskType.DECK_OPTIMIZATION
        elif "PRICE_ANALYSIS" in response_upper:
            return TaskType.PRICE_ANALYSIS
        elif "COLLECTION_MANAGEMENT" in response_upper:
            return TaskType.COLLECTION_MANAGEMENT
        elif "BUY_LIST_GENERATION" in response_upper:
            return TaskType.BUY_LIST_GENERATION
        elif "META_ANALYSIS" in response_upper:
            return TaskType.META_ANALYSIS
        elif "SYNERGY_FINDING" in response_upper:
            return TaskType.SYNERGY_FINDING
        else:
            return TaskType.UNKNOWN


class DeckOptimizer(BaseAgent):
    """Optimizes Magic decks for consistency and power level."""
    
    def _build_system_prompt(self) -> str:
        return """You are DeckOptimizer, expert at analyzing Magic: The Gathering decks.

Provide deck analysis including:
1. Mana curve evaluation
2. Ramp source analysis
3. Card recommendations for improvement
4. Turn 3 consistency calculations
5. Budget-conscious alternatives

Consider:
- Commander format (100 cards, singleton except basic lands)
- Turn 3 ramp target: 12 ramp pieces minimum
- Budget-friendly upgrades under $10
- Card synergies with commander

Be specific with card names and explain WHY each card improves the deck."""
    
    async def execute(self, task: str, deck_list: Optional[str] = None, **kwargs) -> str:
        """
        Optimize deck list.
        
        Time Complexity: O(c) where c is card count
        Space Complexity: O(c) for analysis storage
        """
        context = f"Deck to optimize:\n{deck_list}\n\n" if deck_list else ""
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class PriceAnalyzer(BaseAgent):
    """Analyzes card prices and market trends."""
    
    def _build_system_prompt(self) -> str:
        return """You are PriceAnalyzer, expert at Magic card valuation.

Analyze card prices considering:
1. Current market price ranges
2. Price trends (increasing/decreasing)
3. Reprint likelihood
4. Foil vs. non-foil premiums
5. Buy list vs. retail prices

Provide actionable insights for collectors and players."""
    
    async def execute(self, task: str, cards: Optional[List[str]] = None, **kwargs) -> str:
        """Analyze prices for specified cards."""
        context = f"Cards to analyze: {', '.join(cards)}\n\n" if cards else ""
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class CollectionManager(BaseAgent):
    """Manages and organizes card collections."""
    
    def _build_system_prompt(self) -> str:
        return """You are CollectionManager, expert at organizing Magic collections.

Help with:
1. Identifying duplicates for trade
2. Finding missing pieces for decks
3. Suggesting organization systems
4. Collection valuation
5. Trade recommendations

Consider value, playability, and collector interest."""
    
    async def execute(self, task: str, collection: Optional[Dict] = None, **kwargs) -> str:
        """Analyze and manage collection."""
        context = f"Collection data: {json.dumps(collection, indent=2)}\n\n" if collection else ""
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class BuyListGenerator(BaseAgent):
    """Generates prioritized shopping lists for missing cards."""
    
    def _build_system_prompt(self) -> str:
        return """You are BuyListGenerator, expert at creating Magic shopping lists.

Generate buy lists that consider:
1. Priority ranking (mana base > ramp > draw > removal)
2. Budget allocation
3. Price-to-impact ratio
4. Availability and reprint status
5. Bulk purchase discounts

Format: Card Name | Price Range | Priority | Reason"""
    
    async def execute(
        self,
        task: str,
        missing_cards: Optional[List[str]] = None,
        budget: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate prioritized buy list."""
        context = ""
        if missing_cards:
            context += f"Missing cards: {', '.join(missing_cards)}\n"
        if budget:
            context += f"Budget: ${budget}\n"
        context += "\n"
        
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class MetaAnalyzer(BaseAgent):
    """Analyzes competitive meta-game trends."""
    
    def _build_system_prompt(self) -> str:
        return """You are MetaAnalyzer, expert at competitive Magic analysis.

Analyze meta-game considering:
1. Dominant deck archetypes
2. Sideboard strategies
3. Meta shifts and trends
4. Format health indicators
5. Emergence of new strategies

Provide strategic deck-building recommendations based on meta."""
    
    async def execute(self, task: str, format_name: Optional[str] = None, **kwargs) -> str:
        """Analyze competitive meta."""
        context = f"Format: {format_name}\n\n" if format_name else ""
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class SynergyFinder(BaseAgent):
    """Finds card synergies and combo potential."""
    
    def _build_system_prompt(self) -> str:
        return """You are SynergyFinder, expert at finding Magic card synergies.

Identify:
1. Two-card combos
2. Engine synergies
3. Tribal synergies
4. Keyword interaction chains
5. Theme synergies

Explain HOW cards work together and WHY they improve the deck."""
    
    async def execute(self, task: str, cards: Optional[List[str]] = None, **kwargs) -> str:
        """Find synergies among cards."""
        context = f"Cards: {', '.join(cards)}\n\n" if cards else ""
        prompt = f"{self._build_system_prompt()}\n\n{context}Task: {task}"
        return await self._generate(prompt)


class CardForgeOrchestrator:
    """
    Main orchestration system coordinating all specialized agents.
    
    Architecture:
      TaskRouter → Specialized Agent → Result
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize orchestrator with configuration.
        
        Args:
            config_path: Path to config.json file
        """
        self.config = self._load_config(config_path)
        self.ollama_host = self.config.get("ollama_host", "http://localhost:11434")
        self.agents: Dict[TaskType, BaseAgent] = {}
        self.default_agent: Optional[BaseAgent] = None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path is None:
            # Try to find config.json in same directory
            current_dir = os.path.dirname(__file__)
            config_path = os.path.join(current_dir, "config.json")
        
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return defaults if config not found
            return {
                "ollama_host": "http://localhost:11434",
                "default_timeout": 60,
                "agents": {},
            }
    
    def _get_model_config(self, agent_name: str) -> ModelConfig:
        """Get model config for agent."""
        agent_config = self.config.get("agents", {}).get(agent_name, {})
        return ModelConfig(
            model=agent_config.get("model", "llama3.2:3b"),
            temperature=agent_config.get("temperature", 0.5),
            max_tokens=agent_config.get("max_tokens", 2000),
            timeout=self.config.get("default_timeout", 60),
        )
    
    async def _initialize_agents(self, client: OllamaClient):
        """Initialize all specialized agents."""
        agents_config: Dict[str, type] = {
            "router": TaskRouter,
            "deck_optimizer": DeckOptimizer,
            "price_analyzer": PriceAnalyzer,
            "collection_manager": CollectionManager,
            "buy_list_generator": BuyListGenerator,
            "meta_analyzer": MetaAnalyzer,
            "synergy_finder": SynergyFinder,
        }
        
        task_types: Dict[str, TaskType] = {
            "router": TaskType.UNKNOWN,
            "deck_optimizer": TaskType.DECK_OPTIMIZATION,
            "price_analyzer": TaskType.PRICE_ANALYSIS,
            "collection_manager": TaskType.COLLECTION_MANAGEMENT,
            "buy_list_generator": TaskType.BUY_LIST_GENERATION,
            "meta_analyzer": TaskType.META_ANALYSIS,
            "synergy_finder": TaskType.SYNERGY_FINDING,
        }
        
        for agent_name, agent_class in agents_config.items():
            config = self._get_model_config(agent_name)
            agent = agent_class(agent_name, config, client)
            task_type = task_types.get(agent_name, TaskType.UNKNOWN)
            self.agents[task_type] = agent

        # Default fallback agent for unknown tasks
        default_config = ModelConfig(
            model=DEFAULT_AGENT_MODEL,
            temperature=0.4,
            max_tokens=2000,
            timeout=self.config.get("default_timeout", 60),
        )
        self.default_agent = DefaultAgent("default_agent", default_config, client)
    
    async def execute(
        self,
        task: str,
        **kwargs
    ) -> OrchestrationResult:
        """
        Execute task through orchestration pipeline.
        
        Time Complexity: O(n) where n is task complexity
        Space Complexity: O(1) amortized
        
        Pipeline:
          1. Router classifies task type
          2. Route to specialized agent
          3. Agent executes task
          4. Return result with metadata
        
        Args:
            task: Task description
            **kwargs: Task-specific parameters (e.g., deck_list, cards, etc.)
        
        Returns:
            OrchestrationResult with success status, agent info, and result
        """
        import time
        start_time = time.time()
        
        try:
            async with OllamaClient(self.ollama_host) as client:
                # Check health
                health = await client.health_check()
                if not health:
                    return OrchestrationResult(
                        success=False,
                        agent_name="System",
                        task_type=TaskType.UNKNOWN,
                        result=f"Ollama service unavailable at {self.ollama_host}",
                    )
                
                # Initialize agents
                await self._initialize_agents(client)
                
                # Route task
                router: Optional[BaseAgent] = self.agents.get(TaskType.UNKNOWN)
                if not router:
                    raise RuntimeError("Router agent not initialized")
                
                task_type: TaskType = await router.execute(task)
                
                # Get specialized agent
                agent: Optional[BaseAgent] = self.agents.get(task_type)
                if not agent:
                    # Fallback to default agent if specialized agent not found
                    agent = self.default_agent or self.agents.get(TaskType.UNKNOWN)
                    task_type = TaskType.UNKNOWN
                
                # Execute task
                if agent:
                    result = await agent.execute(task, **kwargs)
                else:
                    raise RuntimeError("Agent not properly initialized")
                
                execution_time = time.time() - start_time
                
                # Safely access agent attributes
                agent_name = agent.name if agent else "Unknown"
                model_used = agent.model_config.model if agent else None
                
                return OrchestrationResult(
                    success=True,
                    agent_name=agent_name,
                    task_type=task_type,
                    result=result,
                    execution_time=execution_time,
                    model_used=model_used,
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return OrchestrationResult(
                success=False,
                agent_name="System",
                task_type=TaskType.UNKNOWN,
                result=f"Error: {str(e)}",
                execution_time=execution_time,
            )


async def main():
    """Demo execution."""
    print("CardForge AI Orchestration System - Demo")
    print("=" * 60)
    
    orchestrator = CardForgeOrchestrator()
    
    # Demo task
    demo_task = "Optimize my Kaalia of the Vast deck for Turn 3 consistency. I want to hit 12+ ramp sources but keep it budget-friendly."
    
    print(f"\nTask: {demo_task}")
    print("=" * 60)
    
    result = await orchestrator.execute(demo_task)
    
    print(f"Agent: {result.agent_name}")
    print(f"Task Type: {result.task_type.value}")
    print(f"Model: {result.model_used}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"\nResult:\n{result.result}")


if __name__ == "__main__":
    asyncio.run(main())
