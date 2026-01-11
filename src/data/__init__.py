"""
Data layer for CardForge.

Provides clients and interfaces for external data sources:
- Ollama AI server
- Scryfall API
- Local file management
"""

from .ollama_client import (
    OllamaClient,
    OllamaError,
    ConnectionError,
    ModelNotFoundError,
    GenerationError,
    GenerateResponse,
    ModelInfo,
    generate,
)

__all__ = [
    "OllamaClient",
    "OllamaError",
    "ConnectionError",
    "ModelNotFoundError",
    "GenerationError",
    "GenerateResponse",
    "ModelInfo",
    "generate",
]
