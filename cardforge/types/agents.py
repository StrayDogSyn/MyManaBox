"""Type definitions for AI agent system.

Protocols and TypedDicts for agent architecture.
"""

from typing import Protocol, AsyncIterator, Any, TypedDict, Literal, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# ENUMS - Agent system
# ============================================================================


class TaskComplexity(str, Enum):
    """Task complexity levels for intelligent model routing."""

    SIMPLE = "simple"  # Quick lookups, simple questions → 3B model
    MODERATE = "moderate"  # Analysis tasks, multi-step → 13B model
    COMPLEX = "complex"  # Deep strategy, multi-step reasoning → 70B model


class AgentCapability(str, Enum):
    """Capabilities an agent can provide."""

    DECK_ANALYSIS = "deck_analysis"
    DECK_OPTIMIZATION = "deck_optimization"
    CARD_SEARCH = "card_search"
    RULES_EXPERT = "rules_expert"
    META_ANALYSIS = "meta_analysis"
    BUDGET_ALTERNATIVE = "budget_alternative"
    COLLECTION_MANAGEMENT = "collection_management"
    PRICE_TRACKING = "price_tracking"


class MessageRole(str, Enum):
    """Chat message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ============================================================================
# DATA CLASSES - Agent domain objects
# ============================================================================


@dataclass(frozen=True)
class ChatMessage:
    """Immutable chat message."""

    role: MessageRole
    content: str
    timestamp: float = field(default_factory=lambda: __import__("time").time())

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
        }


# ============================================================================
# TYPEDDICTS - API contracts
# ============================================================================


class AgentConfigDict(TypedDict, total=False):
    """TypedDict for agent JSON configuration files."""

    id: str
    name: str
    description: str
    capabilities: list[str]
    system_prompt: str
    model: str
    temperature: float
    top_p: float
    top_k: int
    parameters: dict[str, float | int]


class OllamaGenerateRequest(TypedDict, total=False):
    """TypedDict for Ollama API generate request."""

    model: str
    prompt: str
    stream: bool
    raw: bool
    temperature: float
    top_k: int
    top_p: float
    num_ctx: int
    options: dict[str, Any]


class OllamaGenerateResponse(TypedDict):
    """TypedDict for Ollama API generate response."""

    model: str
    created_at: str
    response: str
    done: bool
    context: list[int]
    total_duration: int | None
    load_duration: int | None
    prompt_eval_count: int | None
    prompt_eval_duration: int | None
    eval_count: int | None
    eval_duration: int | None


class OllamaModelInfo(TypedDict):
    """TypedDict for Ollama model information."""

    name: str
    modified_at: str
    size: int
    digest: str


class OllamaModelsResponse(TypedDict):
    """TypedDict for Ollama models list response."""

    models: list[OllamaModelInfo]


# ============================================================================
# PROTOCOLS - Agent interfaces
# ============================================================================


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol for AI agents."""

    @property
    def id(self) -> str:
        """Unique agent identifier."""
        ...

    @property
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    @property
    def capabilities(self) -> list[AgentCapability]:
        """What this agent can do."""
        ...

    async def initialize(self) -> None:
        """Initialize agent with dependencies."""
        ...

    async def process(self, user_input: str, context: dict[str, Any] | None = None) -> str:
        """Process user input and return response."""
        ...

    async def chat(
        self, messages: list[ChatMessage], context: dict[str, Any] | None = None
    ) -> AsyncIterator[str]:
        """Multi-turn chat with streaming response."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent to dictionary."""
        ...


@runtime_checkable
class OllamaClientProtocol(Protocol):
    """Protocol for Ollama client implementations."""

    async def list_models(self) -> list[OllamaModelInfo]:
        """List available models."""
        ...

    async def generate(self, request: OllamaGenerateRequest) -> str:
        """Generate text from prompt."""
        ...

    async def stream_generate(
        self, request: OllamaGenerateRequest
    ) -> AsyncIterator[str]:
        """Stream text generation."""
        ...

    async def select_model(self, complexity: TaskComplexity) -> str:
        """Select appropriate model for task complexity."""
        ...

    async def is_available(self) -> bool:
        """Check if Ollama service is available."""
        ...


__all__ = [
    "TaskComplexity",
    "AgentCapability",
    "MessageRole",
    "ChatMessage",
    "AgentConfigDict",
    "OllamaGenerateRequest",
    "OllamaGenerateResponse",
    "OllamaModelInfo",
    "OllamaModelsResponse",
    "AgentProtocol",
    "OllamaClientProtocol",
]
