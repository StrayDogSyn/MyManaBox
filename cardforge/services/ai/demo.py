"""
Demo script for CardForge AI Agents

Demonstrates orchestrator, routing, and agent execution.
Run: python -m src.services.ai.demo
"""

import asyncio
from src.services.ai import (
    CardForgeOrchestrator,
    AgentTask,
    TaskType,
    TaskComplexity,
)


async def demo_health_check():
    """Demo: Check orchestrator health."""
    print("\n" + "="*60)
    print("DEMO 1: Health Check")
    print("="*60)
    
    async with CardForgeOrchestrator() as orchestrator:
        health = await orchestrator.health_check()
        
        print(f"[OK] Orchestrator: {health['orchestrator']}")
        print(f"[OK] Ollama: {health['ollama']} ({health['ollama_url']})")
        print(f"[OK] Agents Loaded: {health['agents_loaded']}")
        print(f"[OK] Available Models: {health['available_models']}")
        print(f"   Models: {', '.join(health['model_names'])}")


async def demo_list_agents():
    """Demo: List available agents."""
    print("\n" + "="*60)
    print("DEMO 2: List Agents")
    print("="*60)
    
    async with CardForgeOrchestrator() as orchestrator:
        agents = orchestrator.list_agents()
        
        for name, description in agents.items():
            print(f"  • {name:20} - {description}")


async def demo_routing():
    """Demo: Automatic task routing."""
    print("\n" + "="*60)
    print("DEMO 3: Task Routing")
    print("="*60)
    
    test_inputs = [
        "I want to optimize my Kaalia Commander deck",
        "What's the value of my collection?",
        "Help me organize my duplicate cards",
        "Create a shopping list for my deck with $150 budget",
        "Find combos with Kiki-Jiki",
        "Analyze the current Commander meta",
    ]
    
    async with CardForgeOrchestrator() as orchestrator:
        for user_input in test_inputs:
            print(f"\n[USER] \"{user_input}\"")
            
            task = AgentTask(
                task_type=TaskType.ROUTE,
                complexity=TaskComplexity.SIMPLE,
                context={},
                user_input=user_input
            )
            
            response = await orchestrator.execute_task(task, auto_route=True)
            
            if response.success:
                routed_to = response.result.get("routed_to", "unknown")
                confidence = response.result.get("confidence", 0)
                print(f"   -> Routed to: {routed_to} (confidence: {confidence:.0%})")
                print(f"   Time: {response.execution_time:.2f}s")
            else:
                print(f"   [ERROR] Routing failed: {response.reasoning}")


async def demo_deck_optimization():
    """Demo: Deck optimization."""
    print("\n" + "="*60)
    print("DEMO 4: Deck Optimization")
    print("="*60)
    
    sample_deck = [
        {"name": "Sol Ring", "cmc": 1, "types": "Artifact"},
        {"name": "Lightning Greaves", "cmc": 2, "types": "Artifact - Equipment"},
        {"name": "Command Tower", "cmc": 0, "types": "Land"},
        {"name": "Arcane Signet", "cmc": 2, "types": "Artifact"},
        {"name": "Swiftfoot Boots", "cmc": 2, "types": "Artifact - Equipment"},
    ]
    
    async with CardForgeOrchestrator() as orchestrator:
        print(f"📊 Optimizing 'Kaalia Voltron' with {len(sample_deck)} cards...")
        
        response = await orchestrator.optimize_deck(
            deck_name="Kaalia Voltron",
            commander="Kaalia of the Vast",
            cards=sample_deck,
            strategy="Fast aggro/voltron",
            budget=200.0,
            complexity=TaskComplexity.MODERATE
        )
        
        print(f"\n✅ Agent: {response.agent_name}")
        print(f"⏱️  Time: {response.execution_time:.2f}s")
        print(f"🔢 Tokens: {response.token_count}")
        print(f"🤖 Model: {response.model_used}")
        
        if response.success:
            result = response.result
            if isinstance(result, dict):
                score = result.get("deck_score", "N/A")
                issues = result.get("issues", [])
                recommendations = result.get("recommendations", [])
                
                print(f"\n📈 Deck Score: {score}/10")
                
                if issues:
                    print(f"\n⚠️  Issues Found:")
                    for issue in issues[:3]:
                        print(f"   • {issue}")
                        
                if recommendations:
                    print(f"\n💡 Recommendations:")
                    for rec in recommendations[:3]:
                        if isinstance(rec, dict):
                            action = rec.get("action", "unknown")
                            cards = rec.get("cards", [])
                            priority = rec.get("priority", "medium")
                            print(f"   • [{priority.upper()}] {action}: {', '.join(cards)}")
            else:
                print(f"\nResult: {result}")
        else:
            print(f"❌ Optimization failed: {response.reasoning}")


async def demo_buylist():
    """Demo: Buy list generation."""
    print("\n" + "="*60)
    print("DEMO 5: Buy List Generation")
    print("="*60)
    
    missing_cards = [
        {"name": "Sol Ring", "price_usd": 3.50, "category": "ramp"},
        {"name": "Lightning Greaves", "price_usd": 5.00, "category": "protection"},
        {"name": "Mana Crypt", "price_usd": 900.00, "category": "ramp"},
        {"name": "Rhystic Study", "price_usd": 45.00, "category": "card draw"},
    ]
    
    budget = 50.0
    
    async with CardForgeOrchestrator() as orchestrator:
        print(f"🛒 Generating buy list with ${budget} budget...")
        print(f"📝 Missing {len(missing_cards)} cards\n")
        
        response = await orchestrator.generate_buylist(
            missing_cards=missing_cards,
            budget=budget,
            deck_strategy="Aggro Commander"
        )
        
        print(f"✅ Agent: {response.agent_name}")
        print(f"⏱️  Time: {response.execution_time:.2f}s")
        print(f"🤖 Model: {response.model_used}")
        
        if response.success and isinstance(response.result, dict):
            buy_now = response.result.get("buy_now", [])
            alternatives = response.result.get("budget_alternatives", [])
            
            if buy_now:
                print(f"\n🎯 Priority Purchases (within budget):")
                for item in buy_now[:5]:
                    if isinstance(item, dict):
                        card = item.get("card", "Unknown")
                        price = item.get("price", 0)
                        reason = item.get("reason", "")
                        print(f"   • {card} (${price:.2f}) - {reason}")
                        
            if alternatives:
                print(f"\n💰 Budget Alternatives:")
                for alt in alternatives[:3]:
                    if isinstance(alt, dict):
                        expensive = alt.get("expensive", "")
                        budget_opt = alt.get("budget", "")
                        print(f"   • Instead of {expensive}, consider {budget_opt}")


async def main():
    """Run all demos."""
    print("\n*** CardForge AI Agent Demo ***")
    print("=" * 60)
    
    try:
        await demo_health_check()
        await demo_list_agents()
        await demo_routing()
        await demo_deck_optimization()
        await demo_buylist()
        
        print("\n" + "="*60)
        print("✅ All demos completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
