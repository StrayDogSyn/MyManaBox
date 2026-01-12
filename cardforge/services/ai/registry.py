from typing import Dict, Type, Optional, List
from .base_agent import BaseAgent
from .agents.deck_optimizer import DeckOptimizerAgent

class AgentRegistry:
    """Registry for AI agents."""
    
    _registry: Dict[str, Type[BaseAgent]] = {
        "deck_optimizer": DeckOptimizerAgent,
        # Future agents:
        # "price_analyst": PriceAnalystAgent,
        # "meta_analyst": MetaAnalystAgent,
    }
    
    _instances: Dict[str, BaseAgent] = {}

    @classmethod
    def get_agent(cls, name: str, client) -> Optional[BaseAgent]:
        """
        Get or create an agent instance.
        
        Args:
            name: ID of the agent (e.g., 'deck_optimizer')
            client: OllamaClient instance
            
        Returns:
            Initialized agent or None if not found
        """
        if name in cls._instances:
            return cls._instances[name]
            
        agent_cls = cls._registry.get(name)
        if not agent_cls:
            return None
            
        instance = agent_cls(ollama_client=client)
        cls._instances[name] = instance
        return instance

    @classmethod
    def list_agents(cls) -> List[str]:
        """List available agent IDs."""
        return list(cls._registry.keys())

    @classmethod
    def register(cls, name: str, agent_cls: Type[BaseAgent]):
        """Register a new agent dynamically."""
        cls._registry[name] = agent_cls
