"""
CardForge AI Orchestration System

Zero-cost AI agent orchestration using local Ollama models.
Provides specialized agents for deck optimization, collection management,
price analysis, and meta-game insights.
"""

__version__ = "1.0.0"
__author__ = "CardForge Development"

from .orchestration import (
    CardForgeOrchestrator,
    TaskRouter,
    DeckOptimizer,
    PriceAnalyzer,
    CollectionManager,
    BuyListGenerator,
    MetaAnalyzer,
    SynergyFinder,
)

__all__ = [
    "CardForgeOrchestrator",
    "TaskRouter",
    "DeckOptimizer",
    "PriceAnalyzer",
    "CollectionManager",
    "BuyListGenerator",
    "MetaAnalyzer",
    "SynergyFinder",
]
