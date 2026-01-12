"""
AI Service Layer for CardForge

Provides agent orchestration, model selection, and specialized AI agents
for deck optimization, price analysis, and collection management.
"""

from .base_agent import (
    BaseAgent,
    AgentTask,
    AgentResponse,
    TaskType,
    TaskComplexity,
)
from .model_selection import (
    ModelTier,
    ModelConfig,
    select_model,
    get_temperature,
    AVAILABLE_MODELS,
)
from .orchestrator import CardForgeOrchestrator
from .agents import (
    RouterAgent,
    DeckOptimizerAgent,
    PriceAnalyzerAgent,
    CollectionManagerAgent,
    BuyListGeneratorAgent,
    MetaAnalyzerAgent,
    SynergyFinderAgent,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentTask",
    "AgentResponse",
    "TaskType",
    "TaskComplexity",
    # Model selection
    "ModelTier",
    "ModelConfig",
    "select_model",
    "get_temperature",
    "AVAILABLE_MODELS",
    # Orchestrator
    "CardForgeOrchestrator",
    # Agents
    "RouterAgent",
    "DeckOptimizerAgent",
    "PriceAnalyzerAgent",
    "CollectionManagerAgent",
    "BuyListGeneratorAgent",
    "MetaAnalyzerAgent",
    "SynergyFinderAgent",
]
