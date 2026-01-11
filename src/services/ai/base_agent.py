"""
Base Agent Architecture for CardForge AI System

Provides abstract base class and data structures for specialized AI agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    """Types of tasks that can be routed to agents."""
    ROUTE = "route"  # Router classifies task
    DECK_OPTIMIZATION = "deck_optimization"
    PRICE_ANALYSIS = "price_analysis"
    COLLECTION_MANAGEMENT = "collection_management"
    BUYLIST_GENERATION = "buylist_generation"
    META_ANALYSIS = "meta_analysis"
    SYNERGY_DETECTION = "synergy_detection"


class TaskComplexity(str, Enum):
    """Complexity levels for model selection."""
    SIMPLE = "simple"        # Fast models (llama3.2:3b, gemma2:4b)
    MODERATE = "moderate"    # Balanced models (qwen2.5-coder:7b)
    COMPLEX = "complex"      # Powerful models (llama3.1:70b)


@dataclass
class AgentTask:
    """
    Task request sent to an AI agent.
    
    Attributes:
        task_type: Type of task (routing, optimization, etc.)
        complexity: Complexity level for model selection
        context: Task-specific context data
        user_input: Optional raw user input
        constraints: Optional constraints (budget, time, etc.)
        metadata: Additional metadata for tracking
    """
    task_type: TaskType
    complexity: TaskComplexity
    context: Dict[str, Any]
    user_input: Optional[str] = None
    constraints: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_type": self.task_type.value,
            "complexity": self.complexity.value,
            "context": self.context,
            "user_input": self.user_input,
            "constraints": self.constraints,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AgentResponse:
    """
    Response from an AI agent after task execution.
    
    Attributes:
        agent_name: Name of the agent that executed the task
        task_type: Type of task that was executed
        success: Whether task completed successfully
        result: Primary result data
        reasoning: Agent's reasoning/explanation
        suggestions: Optional suggestions or recommendations
        confidence: Confidence score (0.0-1.0)
        model_used: Name of the model used
        execution_time: Time taken in seconds
        token_count: Number of tokens used
        metadata: Additional metadata
    """
    agent_name: str
    task_type: TaskType
    success: bool
    result: Any
    reasoning: str = ""
    suggestions: Optional[List[str]] = None
    confidence: float = 1.0
    model_used: str = ""
    execution_time: float = 0.0
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "agent_name": self.agent_name,
            "task_type": self.task_type.value,
            "success": self.success,
            "result": self.result,
            "reasoning": self.reasoning,
            "suggestions": self.suggestions,
            "confidence": self.confidence,
            "model_used": self.model_used,
            "execution_time": self.execution_time,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        }


class BaseAgent(ABC):
    """
    Abstract base class for all CardForge AI agents.
    
    Each agent specializes in a specific domain (deck optimization,
    price analysis, etc.) and uses appropriate models based on task complexity.
    """
    
    def __init__(self, name: str, ollama_client):
        """
        Initialize the agent.
        
        Args:
            name: Unique name for this agent
            ollama_client: OllamaClient instance for AI inference
        """
        self.name = name
        self.client = ollama_client
        self._system_prompt = self._define_system_prompt()
        
    @abstractmethod
    def _define_system_prompt(self) -> str:
        """
        Define the system prompt that establishes agent's expertise.
        
        This prompt should:
        - Define the agent's role and expertise
        - Establish tone and style
        - Set expectations for output format
        - Include domain-specific knowledge
        
        Returns:
            System prompt string
        """
        pass
        
    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResponse:
        """
        Execute the task and return a response.
        
        Args:
            task: AgentTask with context and requirements
            
        Returns:
            AgentResponse with results and metadata
        """
        pass
        
    def _build_prompt(self, task: AgentTask) -> str:
        """
        Build the user prompt from task context.
        
        Override this method in subclasses for custom prompt formatting.
        
        Args:
            task: AgentTask with context
            
        Returns:
            Formatted user prompt string
        """
        parts = []
        
        # Add user input if provided
        if task.user_input:
            parts.append(f"User Request: {task.user_input}\n")
            
        # Add context
        if task.context:
            parts.append("Context:")
            for key, value in task.context.items():
                parts.append(f"  - {key}: {value}")
            parts.append("")
            
        # Add constraints
        if task.constraints:
            parts.append("Constraints:")
            for key, value in task.constraints.items():
                parts.append(f"  - {key}: {value}")
            parts.append("")
            
        return "\n".join(parts)
        
    async def _generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
    ) -> tuple[str, int, float]:
        """
        Generate response using Ollama.
        
        Args:
            prompt: User prompt
            model: Model name to use
            temperature: Sampling temperature
            
        Returns:
            Tuple of (response_text, token_count, execution_time_seconds)
        """
        import time
        start_time = time.time()
        
        response = await self.client.generate(
            model=model,
            prompt=prompt,
            system=self._system_prompt,
            temperature=temperature,
        )
        
        execution_time = time.time() - start_time
        
        return (
            response.response,
            response.eval_count or 0,
            execution_time
        )
        
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from response, handling markdown code blocks.
        
        Args:
            response_text: Raw response from model
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        import re
        
        # Try direct JSON parse first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
            
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
                
        # Try to find any JSON object in the text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
                
        # If all else fails, return empty dict
        return {}
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
