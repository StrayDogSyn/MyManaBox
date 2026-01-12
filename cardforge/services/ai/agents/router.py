"""
RouterAgent - Task Classification and Routing

Routes incoming tasks to specialized agents based on task type and complexity.
"""

from ..base_agent import BaseAgent, AgentTask, AgentResponse, TaskType, TaskComplexity
from ..model_selection import select_model, get_temperature


class RouterAgent(BaseAgent):
    """
    Routes tasks to appropriate specialized agents.
    
    Uses fast model (llama3.2:3b) for quick classification.
    Analyzes user input to determine:
    - Task type (which agent should handle it)
    - Task complexity (which model tier to use)
    """
    
    def __init__(self, ollama_client):
        super().__init__(name="Router", ollama_client=ollama_client)
        
    def _define_system_prompt(self) -> str:
        return """You are the Router Agent for CardForge, an AI-powered MTG collection manager.

Your role is to analyze user requests and classify them into specific task types.

TASK TYPES:
1. deck_optimization - Optimizing Commander decks (mana curve, synergies, strategy)
2. price_analysis - Market pricing, value tracking, investment analysis
3. collection_management - Inventory organization, duplicate detection, gaps
4. buylist_generation - Creating shopping lists with priorities and budgets
5. meta_analysis - Competitive meta trends, deck archetypes, win rates
6. synergy_detection - Finding card combos and interactions

COMPLEXITY LEVELS:
- simple: Quick queries, lookups, basic recommendations
- moderate: Standard optimization, typical analysis tasks
- complex: Deep strategic analysis, large-scale optimization

OUTPUT FORMAT (JSON):
{
    "task_type": "deck_optimization",
    "complexity": "moderate",
    "confidence": 0.95,
    "reasoning": "User wants to optimize their Commander deck structure"
}

Be decisive and accurate. Always output valid JSON."""

    async def execute(self, task: AgentTask) -> AgentResponse:
        """Route the task by classifying its type and complexity."""
        import time
        start_time = time.time()
        
        # Build classification prompt
        prompt = f"""Classify this MTG-related request:

User Request: {task.user_input or 'No specific request provided'}

Context: {task.context if task.context else 'None'}

Analyze and output JSON with task_type, complexity, confidence, and reasoning."""

        # Use fast model for routing (O(1) operation)
        model = select_model(TaskComplexity.SIMPLE)
        
        try:
            response_text, tokens, exec_time = await self._generate(
                prompt=prompt,
                model=model,
                temperature=get_temperature("routing"),
            )
            
            # Parse JSON response
            result = self._parse_json_response(response_text)
            
            # Validate and normalize task_type
            task_type_str = result.get("task_type", "deck_optimization")
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                # Default to deck optimization if invalid
                task_type = TaskType.DECK_OPTIMIZATION
                
            # Validate and normalize complexity
            complexity_str = result.get("complexity", "moderate")
            try:
                complexity = TaskComplexity(complexity_str)
            except ValueError:
                complexity = TaskComplexity.MODERATE
                
            return AgentResponse(
                agent_name=self.name,
                task_type=task_type,
                success=True,
                result={
                    "routed_to": task_type.value,
                    "complexity": complexity.value,
                    "confidence": result.get("confidence", 0.8),
                },
                reasoning=result.get("reasoning", "Task classified"),
                confidence=result.get("confidence", 0.8),
                model_used=model,
                execution_time=time.time() - start_time,
                token_count=tokens,
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                task_type=TaskType.ROUTE,
                success=False,
                result={"error": str(e)},
                reasoning=f"Routing failed: {e}",
                model_used=model,
                execution_time=time.time() - start_time,
            )
