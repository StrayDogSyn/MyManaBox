"""
CardForgeOrchestrator - AI Agent Coordination

Coordinates execution across specialized agents, handles routing, and manages results.
"""

import logging
from typing import Dict, Optional
from cardforge.ai import OllamaClient

from .base_agent import BaseAgent, AgentTask, AgentResponse, TaskType, TaskComplexity
from .agents import (
    RouterAgent,
    DeckOptimizerAgent,
    PriceAnalyzerAgent,
    CollectionManagerAgent,
    BuyListGeneratorAgent,
    MetaAnalyzerAgent,
    SynergyFinderAgent,
)


logger = logging.getLogger(__name__)


class CardForgeOrchestrator:
    """
    Orchestrates AI agent execution for CardForge.
    
    Features:
    - Automatic task routing to specialized agents
    - Model selection based on complexity
    - Session management for Ollama client
    - Result aggregation and error handling
    
    Example:
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.DECK_OPTIMIZATION,
                complexity=TaskComplexity.MODERATE,
                context={"deck_name": "Kaalia Voltron", "cards": [...]}
            )
            response = await orchestrator.execute_task(task)
            print(response.result)
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialize orchestrator with Ollama connection.
        
        Args:
            ollama_url: URL for Ollama server
        """
        self.ollama_url = ollama_url
        self.client: Optional[OllamaClient] = None
        self.agents: Dict[TaskType, BaseAgent] = {}
        self._initialized = False
        
    async def __aenter__(self):
        """Async context manager entry - initialize client and agents."""
        await self._initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup."""
        await self.close()
        
    async def _initialize(self):
        """Initialize Ollama client and create agent instances."""
        if self._initialized:
            return
            
        # Create Ollama client
        self.client = OllamaClient(base_url=self.ollama_url)
        await self.client._ensure_session()
        
        # Verify Ollama is running
        if not await self.client.check_health():
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.ollama_url}. "
                "Is Ollama running? (ollama serve)"
            )
            
        # Initialize all agents
        self.agents = {
            TaskType.ROUTE: RouterAgent(self.client),
            TaskType.DECK_OPTIMIZATION: DeckOptimizerAgent(self.client),
            TaskType.PRICE_ANALYSIS: PriceAnalyzerAgent(self.client),
            TaskType.COLLECTION_MANAGEMENT: CollectionManagerAgent(self.client),
            TaskType.BUYLIST_GENERATION: BuyListGeneratorAgent(self.client),
            TaskType.META_ANALYSIS: MetaAnalyzerAgent(self.client),
            TaskType.SYNERGY_DETECTION: SynergyFinderAgent(self.client),
        }
        
        self._initialized = True
        logger.info(f"CardForge orchestrator initialized with {len(self.agents)} agents")
        
    async def close(self):
        """Close Ollama client connection."""
        if self.client:
            await self.client.close()
            self.client = None
        self._initialized = False
        
    async def execute_task(
        self,
        task: AgentTask,
        auto_route: bool = True,
    ) -> AgentResponse:
        """
        Execute a task with appropriate agent.
        
        Args:
            task: AgentTask to execute
            auto_route: If True, use RouterAgent to classify task first
            
        Returns:
            AgentResponse from the agent
            
        Example:
            task = AgentTask(
                task_type=TaskType.DECK_OPTIMIZATION,
                complexity=TaskComplexity.MODERATE,
                context={"deck_name": "Kaalia", "cards": [...]},
                user_input="Optimize my Kaalia deck"
            )
            response = await orchestrator.execute_task(task)
        """
        if not self._initialized:
            await self._initialize()
            
        # Auto-route if requested and task type is not already specific
        if auto_route and task.task_type == TaskType.ROUTE:
            routing_response = await self._route_task(task)
            
            if not routing_response.success:
                return routing_response
                
            # Update task with routed type and complexity
            routed_type = routing_response.result.get("routed_to")
            try:
                task.task_type = TaskType(routed_type)
            except ValueError:
                # Invalid task type, default to deck optimization
                task.task_type = TaskType.DECK_OPTIMIZATION
                
            # Update complexity if router provided it
            routed_complexity = routing_response.result.get("complexity")
            if routed_complexity:
                try:
                    task.complexity = TaskComplexity(routed_complexity)
                except ValueError:
                    pass  # Keep existing complexity
                    
            logger.info(
                f"Task routed to {task.task_type.value} "
                f"(complexity: {task.complexity.value})"
            )
            
        # Get appropriate agent
        agent = self.agents.get(task.task_type)
        if not agent:
            return AgentResponse(
                agent_name="Orchestrator",
                task_type=task.task_type,
                success=False,
                result={"error": f"No agent found for task type: {task.task_type}"},
                reasoning="Invalid task type",
            )
            
        # Execute task with agent
        try:
            logger.info(f"Executing task with {agent.name} agent")
            response = await agent.execute(task)
            logger.info(
                f"Task completed: {response.success} "
                f"(time: {response.execution_time:.2f}s, "
                f"tokens: {response.token_count})"
            )
            return response
            
        except Exception as e:
            logger.exception(f"Error executing task with {agent.name}")
            return AgentResponse(
                agent_name=agent.name,
                task_type=task.task_type,
                success=False,
                result={"error": str(e)},
                reasoning=f"Execution failed: {e}",
            )
            
    async def _route_task(self, task: AgentTask) -> AgentResponse:
        """
        Route task using RouterAgent.
        
        Args:
            task: Task to route
            
        Returns:
            AgentResponse from RouterAgent
        """
        router = self.agents.get(TaskType.ROUTE)
        if not router:
            # Fallback if router not available
            return AgentResponse(
                agent_name="Orchestrator",
                task_type=TaskType.ROUTE,
                success=True,
                result={
                    "routed_to": TaskType.DECK_OPTIMIZATION.value,
                    "complexity": TaskComplexity.MODERATE.value,
                },
                reasoning="Router not available, using default routing",
            )
            
        return await router.execute(task)
        
    async def optimize_deck(
        self,
        deck_name: str,
        commander: str,
        cards: list,
        strategy: str = "Unknown",
        budget: Optional[float] = None,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
    ) -> AgentResponse:
        """
        Convenience method for deck optimization.
        
        Args:
            deck_name: Name of the deck
            commander: Commander card name
            cards: List of cards in deck
            strategy: Deck strategy description
            budget: Optional budget constraint
            complexity: Task complexity level
            
        Returns:
            AgentResponse with optimization results
        """
        task = AgentTask(
            task_type=TaskType.DECK_OPTIMIZATION,
            complexity=complexity,
            context={
                "deck_name": deck_name,
                "commander": commander,
                "cards": cards,
                "strategy": strategy,
            },
            constraints={"budget": budget} if budget else None,
            user_input=f"Optimize my {deck_name} Commander deck",
        )
        
        return await self.execute_task(task, auto_route=False)
        
    async def generate_buylist(
        self,
        missing_cards: list,
        budget: float,
        deck_strategy: str = "Unknown",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
    ) -> AgentResponse:
        """
        Convenience method for buy list generation.
        
        Args:
            missing_cards: List of cards needed
            budget: Available budget
            deck_strategy: Deck strategy description
            complexity: Task complexity level
            
        Returns:
            AgentResponse with buy list
        """
        task = AgentTask(
            task_type=TaskType.BUYLIST_GENERATION,
            complexity=complexity,
            context={
                "missing_cards": missing_cards,
                "strategy": deck_strategy,
            },
            constraints={"budget": budget},
            user_input=f"Generate buy list with ${budget} budget",
        )
        
        return await self.execute_task(task, auto_route=False)
        
    async def analyze_collection(
        self,
        cards: list,
        analysis_type: str = "full",
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
    ) -> AgentResponse:
        """
        Convenience method for collection analysis.
        
        Args:
            cards: List of cards in collection
            analysis_type: Type of analysis (full, duplicates, gaps, value)
            complexity: Task complexity level
            
        Returns:
            AgentResponse with analysis results
        """
        task = AgentTask(
            task_type=TaskType.COLLECTION_MANAGEMENT,
            complexity=complexity,
            context={
                "cards": cards,
                "analysis_type": analysis_type,
            },
            user_input=f"Analyze my collection ({analysis_type} analysis)",
        )
        
        return await self.execute_task(task, auto_route=False)
        
    def list_agents(self) -> Dict[str, str]:
        """
        List all available agents and their specializations.
        
        Returns:
            Dictionary mapping agent names to descriptions
        """
        return {
            "Router": "Task classification and routing",
            "DeckOptimizer": "Commander deck optimization and analysis",
            "PriceAnalyzer": "Market pricing and value tracking",
            "CollectionManager": "Inventory organization and management",
            "BuyListGenerator": "Prioritized shopping list creation",
            "MetaAnalyzer": "Competitive metagame analysis",
            "SynergyFinder": "Card interaction and combo detection",
        }
        
    async def health_check(self) -> Dict[str, any]:
        """
        Check health of orchestrator and Ollama connection.
        
        Returns:
            Dictionary with health status
        """
        if not self.client:
            return {
                "orchestrator": "not_initialized",
                "ollama": "not_connected",
                "agents": 0,
            }
            
        ollama_health = await self.client.check_health()
        models = await self.client.list_models() if ollama_health else []
        
        return {
            "orchestrator": "healthy" if self._initialized else "not_initialized",
            "ollama": "healthy" if ollama_health else "unreachable",
            "ollama_url": self.ollama_url,
            "agents_loaded": len(self.agents),
            "available_models": len(models),
            "model_names": [m.name for m in models[:5]],  # Show first 5
        }
