"""
Model Selection Framework for CardForge

Maps task complexity to optimal Ollama models.
Uses Big O analogy: simple tasks → fast models, complex tasks → powerful models.
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

from .base_agent import TaskComplexity


class ModelTier(str, Enum):
    """
    Model tiers based on capability and speed.
    
    Similar to Big O notation:
    - FAST: O(1) - Instant responses, simple tasks
    - BALANCED: O(log n) - Quick but capable
    - POWERFUL: O(n) - Slower but highest quality
    """
    FAST = "fast"              # < 5s response time
    BALANCED = "balanced"      # 5-15s response time
    POWERFUL = "powerful"      # 15-60s response time


@dataclass
class ModelConfig:
    """Configuration for an Ollama model."""
    name: str
    tier: ModelTier
    size_gb: float
    context_length: int
    best_for: List[str]
    avg_response_time: float  # seconds
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.tier.value}, {self.size_gb}GB)"


# Available model configurations
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    # Fast models (2-4 GB) - Simple tasks
    "llama3.2:3b": ModelConfig(
        name="llama3.2:3b",
        tier=ModelTier.FAST,
        size_gb=2.0,
        context_length=4096,
        best_for=["routing", "classification", "simple queries"],
        avg_response_time=3.0,
    ),
    "gemma2:4b": ModelConfig(
        name="gemma2:4b",
        tier=ModelTier.FAST,
        size_gb=3.3,
        context_length=4096,
        best_for=["quick analysis", "summarization"],
        avg_response_time=4.0,
    ),
    "qwen2.5-coder:1.5b-base": ModelConfig(
        name="qwen2.5-coder:1.5b-base",
        tier=ModelTier.FAST,
        size_gb=1.0,
        context_length=4096,
        best_for=["code snippets", "basic queries"],
        avg_response_time=2.0,
    ),
    
    # Balanced models (4-8 GB) - Moderate complexity
    "qwen2.5-coder:7b": ModelConfig(
        name="qwen2.5-coder:7b",
        tier=ModelTier.BALANCED,
        size_gb=4.7,
        context_length=8192,
        best_for=["deck optimization", "synergy detection", "structured output"],
        avg_response_time=8.0,
    ),
    "llama3.1:8b": ModelConfig(
        name="llama3.1:8b",
        tier=ModelTier.BALANCED,
        size_gb=4.9,
        context_length=8192,
        best_for=["analysis", "recommendations", "reasoning"],
        avg_response_time=10.0,
    ),
    "deepseek-coder:6.7b": ModelConfig(
        name="deepseek-coder:6.7b",
        tier=ModelTier.BALANCED,
        size_gb=3.8,
        context_length=16384,
        best_for=["code analysis", "technical tasks"],
        avg_response_time=9.0,
    ),
    
    # Powerful models (40+ GB) - Complex reasoning
    "llama3.1:70b": ModelConfig(
        name="llama3.1:70b",
        tier=ModelTier.POWERFUL,
        size_gb=42.5,
        context_length=8192,
        best_for=["strategic analysis", "complex reasoning", "meta analysis"],
        avg_response_time=45.0,
    ),
}


# Model selection based on task complexity
COMPLEXITY_TO_TIER: Dict[TaskComplexity, ModelTier] = {
    TaskComplexity.SIMPLE: ModelTier.FAST,
    TaskComplexity.MODERATE: ModelTier.BALANCED,
    TaskComplexity.COMPLEX: ModelTier.POWERFUL,
}


# Default models for each tier
DEFAULT_MODELS: Dict[ModelTier, str] = {
    ModelTier.FAST: "llama3.2:3b",
    ModelTier.BALANCED: "qwen2.5-coder:7b",
    ModelTier.POWERFUL: "llama3.1:70b",
}


def select_model(complexity: TaskComplexity, preferred_model: str = None) -> str:
    """
    Select optimal model based on task complexity.
    
    Args:
        complexity: Task complexity level
        preferred_model: Optional specific model to use
        
    Returns:
        Model name string
        
    Example:
        >>> select_model(TaskComplexity.SIMPLE)
        'llama3.2:3b'
        >>> select_model(TaskComplexity.COMPLEX)
        'llama3.1:70b'
    """
    # Use preferred model if specified and available
    if preferred_model and preferred_model in AVAILABLE_MODELS:
        return preferred_model
        
    # Map complexity to tier
    tier = COMPLEXITY_TO_TIER.get(complexity, ModelTier.BALANCED)
    
    # Return default model for tier
    return DEFAULT_MODELS[tier]


def get_model_config(model_name: str) -> ModelConfig:
    """
    Get configuration for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        ModelConfig object
        
    Raises:
        KeyError: If model not found
    """
    return AVAILABLE_MODELS[model_name]


def list_models_by_tier(tier: ModelTier) -> List[ModelConfig]:
    """
    List all models in a specific tier.
    
    Args:
        tier: Model tier to filter by
        
    Returns:
        List of ModelConfig objects
    """
    return [
        config for config in AVAILABLE_MODELS.values()
        if config.tier == tier
    ]


def recommend_model(
    task_description: str,
    max_response_time: float = None,
    max_size_gb: float = None,
) -> str:
    """
    Recommend a model based on task requirements.
    
    Args:
        task_description: Description of the task
        max_response_time: Maximum acceptable response time (seconds)
        max_size_gb: Maximum model size (GB)
        
    Returns:
        Recommended model name
    """
    candidates = list(AVAILABLE_MODELS.values())
    
    # Filter by size constraint
    if max_size_gb:
        candidates = [m for m in candidates if m.size_gb <= max_size_gb]
        
    # Filter by response time constraint
    if max_response_time:
        candidates = [m for m in candidates if m.avg_response_time <= max_response_time]
        
    # If no candidates, return fastest model
    if not candidates:
        return "llama3.2:3b"
        
    # Check if task description mentions keywords
    task_lower = task_description.lower()
    
    # Look for best match based on "best_for" tags
    for model in candidates:
        for tag in model.best_for:
            if tag.lower() in task_lower:
                return model.name
                
    # Default to balanced tier
    balanced_candidates = [m for m in candidates if m.tier == ModelTier.BALANCED]
    if balanced_candidates:
        return balanced_candidates[0].name
        
    # Fallback to first candidate
    return candidates[0].name


def estimate_cost(
    model_name: str,
    num_tasks: int,
    avg_tokens_per_task: int = 500,
) -> Dict[str, float]:
    """
    Estimate time and resource cost for running tasks.
    
    Args:
        model_name: Name of the model to use
        num_tasks: Number of tasks to run
        avg_tokens_per_task: Average tokens per task
        
    Returns:
        Dictionary with cost estimates
    """
    config = AVAILABLE_MODELS.get(model_name)
    if not config:
        return {"error": "Model not found"}
        
    total_time = config.avg_response_time * num_tasks
    total_tokens = avg_tokens_per_task * num_tasks
    
    return {
        "model": model_name,
        "num_tasks": num_tasks,
        "total_time_seconds": total_time,
        "total_time_minutes": total_time / 60,
        "total_tokens": total_tokens,
        "avg_time_per_task": config.avg_response_time,
        "tier": config.tier.value,
    }


# Temperature settings for different task types
TEMPERATURE_PRESETS: Dict[str, float] = {
    "routing": 0.1,           # Deterministic classification
    "analysis": 0.3,          # Consistent analysis
    "optimization": 0.5,      # Balanced creativity
    "creative": 0.7,          # More variation
    "brainstorming": 0.9,     # High creativity
}


def get_temperature(task_type: str, default: float = 0.5) -> float:
    """
    Get recommended temperature for task type.
    
    Args:
        task_type: Type of task
        default: Default temperature if not found
        
    Returns:
        Temperature value (0.0-1.0)
    """
    return TEMPERATURE_PRESETS.get(task_type.lower(), default)
