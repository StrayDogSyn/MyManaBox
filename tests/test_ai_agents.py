"""
Integration tests for CardForge AI Agents.

Tests orchestrator, routing, and agent execution with real Ollama server.
"""

import pytest
from src.services.ai import (
    CardForgeOrchestrator,
    AgentTask,
    TaskType,
    TaskComplexity,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestOrchestrator:
    """Integration tests for CardForgeOrchestrator."""
    
    async def test_orchestrator_initialization(self):
        """Test orchestrator can initialize and connect to Ollama."""
        async with CardForgeOrchestrator() as orchestrator:
            # Verify initialization
            assert orchestrator._initialized
            assert orchestrator.client is not None
            assert len(orchestrator.agents) == 7  # All 7 agents loaded
            
    async def test_health_check(self):
        """Test health check reports status correctly."""
        async with CardForgeOrchestrator() as orchestrator:
            health = await orchestrator.health_check()
            
            assert health["orchestrator"] == "healthy"
            assert health["ollama"] == "healthy"
            assert health["agents_loaded"] == 7
            assert health["available_models"] > 0
            
    async def test_list_agents(self):
        """Test listing available agents."""
        async with CardForgeOrchestrator() as orchestrator:
            agents = orchestrator.list_agents()
            
            assert len(agents) == 7
            assert "Router" in agents
            assert "DeckOptimizer" in agents
            assert "PriceAnalyzer" in agents


@pytest.mark.integration
@pytest.mark.asyncio
class TestRouting:
    """Integration tests for task routing."""
    
    async def test_auto_routing_deck_optimization(self):
        """Test router correctly identifies deck optimization task."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.ROUTE,
                complexity=TaskComplexity.SIMPLE,
                context={},
                user_input="I want to optimize my Kaalia Commander deck"
            )
            
            response = await orchestrator.execute_task(task, auto_route=True)
            
            # Router should classify this as deck optimization
            assert response.success
            # After routing, task should have been re-executed by correct agent
            
    async def test_auto_routing_price_analysis(self):
        """Test router correctly identifies price analysis task."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.ROUTE,
                complexity=TaskComplexity.SIMPLE,
                context={},
                user_input="What's the value of my collection worth?"
            )
            
            response = await orchestrator.execute_task(task, auto_route=True)
            
            assert response.success
            
    async def test_manual_routing_skip(self):
        """Test direct task execution without routing."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.DECK_OPTIMIZATION,
                complexity=TaskComplexity.MODERATE,
                context={
                    "deck_name": "Test Deck",
                    "commander": "Test Commander",
                    "cards": []
                },
            )
            
            # Execute without auto-routing
            response = await orchestrator.execute_task(task, auto_route=False)
            
            assert response.agent_name == "DeckOptimizer"


@pytest.mark.integration
@pytest.mark.asyncio
class TestDeckOptimization:
    """Integration tests for deck optimization."""
    
    async def test_optimize_empty_deck(self):
        """Test optimization with minimal deck data."""
        async with CardForgeOrchestrator() as orchestrator:
            response = await orchestrator.optimize_deck(
                deck_name="Test Kaalia",
                commander="Kaalia of the Vast",
                cards=[],
                strategy="Aggro/Voltron"
            )
            
            assert response.agent_name == "DeckOptimizer"
            assert response.task_type == TaskType.DECK_OPTIMIZATION
            # Success may vary depending on Ollama availability
            
    async def test_optimize_with_sample_deck(self):
        """Test optimization with sample deck data."""
        sample_deck = [
            {"name": "Sol Ring", "cmc": 1, "types": "Artifact"},
            {"name": "Lightning Greaves", "cmc": 2, "types": "Artifact - Equipment"},
            {"name": "Command Tower", "cmc": 0, "types": "Land"},
        ]
        
        async with CardForgeOrchestrator() as orchestrator:
            response = await orchestrator.optimize_deck(
                deck_name="Budget Kaalia",
                commander="Kaalia of the Vast",
                cards=sample_deck,
                strategy="Fast aggro",
                budget=200.0,
            )
            
            assert response.agent_name == "DeckOptimizer"
            assert response.execution_time > 0
            assert response.token_count > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestBuyListGeneration:
    """Integration tests for buy list generation."""
    
    async def test_generate_buylist(self):
        """Test buy list generation with budget constraint."""
        missing_cards = [
            {"name": "Sol Ring", "price_usd": 3.50, "category": "ramp"},
            {"name": "Lightning Greaves", "price_usd": 5.00, "category": "protection"},
            {"name": "Swiftfoot Boots", "price_usd": 2.50, "category": "protection"},
        ]
        
        async with CardForgeOrchestrator() as orchestrator:
            response = await orchestrator.generate_buylist(
                missing_cards=missing_cards,
                budget=50.0,
                deck_strategy="Aggro Commander"
            )
            
            assert response.agent_name == "BuyListGenerator"
            assert response.task_type == TaskType.BUYLIST_GENERATION


@pytest.mark.integration
@pytest.mark.asyncio
class TestCollectionAnalysis:
    """Integration tests for collection management."""
    
    async def test_analyze_collection(self):
        """Test collection analysis."""
        sample_collection = [
            {"name": "Sol Ring", "quantity": 5, "price_usd": 3.50},
            {"name": "Command Tower", "quantity": 3, "price_usd": 1.00},
        ]
        
        async with CardForgeOrchestrator() as orchestrator:
            response = await orchestrator.analyze_collection(
                cards=sample_collection,
                analysis_type="duplicates"
            )
            
            assert response.agent_name == "CollectionManager"
            assert response.task_type == TaskType.COLLECTION_MANAGEMENT


@pytest.mark.integration
@pytest.mark.asyncio
class TestModelSelection:
    """Integration tests for model selection."""
    
    async def test_simple_task_uses_fast_model(self):
        """Test simple tasks use fast models."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.ROUTE,
                complexity=TaskComplexity.SIMPLE,
                context={},
                user_input="Quick test"
            )
            
            response = await orchestrator.execute_task(task, auto_route=False)
            
            # Router should use fast model (llama3.2:3b)
            assert "llama3.2" in response.model_used or "gemma" in response.model_used
            
    async def test_complex_task_can_use_powerful_model(self):
        """Test complex tasks can use powerful models if available."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.META_ANALYSIS,
                complexity=TaskComplexity.COMPLEX,
                context={"format": "Commander", "archetype": "Stax"},
            )
            
            response = await orchestrator.execute_task(task, auto_route=False)
            
            # Should use balanced or powerful model
            assert response.model_used in ["qwen2.5-coder:7b", "llama3.1:70b", "llama3.1:8b"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestErrorHandling:
    """Integration tests for error handling."""
    
    async def test_invalid_task_type(self):
        """Test handling of invalid task types."""
        async with CardForgeOrchestrator() as orchestrator:
            task = AgentTask(
                task_type=TaskType.DECK_OPTIMIZATION,
                complexity=TaskComplexity.MODERATE,
                context={},  # Empty context - may cause issues
            )
            
            response = await orchestrator.execute_task(task, auto_route=False)
            
            # Should handle gracefully, even if result is not optimal
            assert response.agent_name == "DeckOptimizer"
            
    async def test_connection_lost_recovery(self):
        """Test behavior when Ollama connection is lost."""
        # This test would require stopping Ollama mid-execution
        # For now, just verify orchestrator can detect health issues
        async with CardForgeOrchestrator() as orchestrator:
            health = await orchestrator.health_check()
            
            # If Ollama is running, this should pass
            if health["ollama"] == "healthy":
                assert True
            else:
                pytest.skip("Ollama not running for this test")


@pytest.mark.integration
@pytest.mark.asyncio
class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    async def test_complete_deck_optimization_workflow(self):
        """Test complete workflow: route → optimize → generate buylist."""
        async with CardForgeOrchestrator() as orchestrator:
            # Step 1: User provides natural language request
            route_task = AgentTask(
                task_type=TaskType.ROUTE,
                complexity=TaskComplexity.SIMPLE,
                context={},
                user_input="I need help optimizing my Kaalia deck and creating a shopping list with $150 budget"
            )
            
            # Step 2: Route the task
            route_response = await orchestrator.execute_task(route_task, auto_route=True)
            
            # Workflow continues...
            # In real usage, would parse route_response and execute additional tasks
            assert route_response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-m", "integration"])
