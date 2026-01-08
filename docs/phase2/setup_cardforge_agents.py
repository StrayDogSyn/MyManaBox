"""
CardForge Agent Orchestration Setup Script
Validates Ollama installation and configures agent system
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Color output helpers
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def print_header(msg: str):
    print(f"\n{Colors.BOLD}{msg}{Colors.END}")
    print("=" * 60)


async def check_ollama_installation() -> bool:
    """Check if Ollama is installed and running."""
    print_header("Checking Ollama Installation")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:11434/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    print_success("Ollama server is running at localhost:11434")
                    return True
                else:
                    print_error(f"Ollama server returned status {response.status}")
                    return False
    except Exception as e:
        print_error("Ollama server is not running")
        print_info(f"Error: {e}")
        print()
        print("To start Ollama:")
        print("  1. Open a new terminal")
        print("  2. Run: ollama serve")
        print("  3. Keep that terminal open")
        print()
        return False


async def check_required_models() -> Dict[str, bool]:
    """Check which required models are installed."""
    print_header("Checking Required Models")
    
    required_models = [
        "llama3.2:1b",
        "llama3.2:3b",
        "gemma2:4b",
        "qwen2.5-coder:7b",
        "llama3.1:70b"
    ]
    
    optional_models = [
        "phi3:mini",
        "tinyllama",
        "deepseek-coder:6.7b",
        "granite-code:8b",
        "codellama:13b",
        "all-minilm",
        "nomic-embed-text"
    ]
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                data = await response.json()
                installed = [m["name"] for m in data.get("models", [])]
        
        results = {}
        missing_required = []
        
        print("\nRequired Models:")
        for model in required_models:
            is_installed = any(model in inst for inst in installed)
            results[model] = is_installed
            
            if is_installed:
                print_success(f"{model} - Installed")
            else:
                print_error(f"{model} - Missing")
                missing_required.append(model)
        
        print("\nOptional Models:")
        for model in optional_models:
            is_installed = any(model in inst for inst in installed)
            if is_installed:
                print_success(f"{model} - Installed")
            else:
                print_info(f"{model} - Not installed (optional)")
        
        if missing_required:
            print()
            print_warning("Missing required models. To install:")
            for model in missing_required:
                print(f"  ollama pull {model}")
            print()
        
        return results
        
    except Exception as e:
        print_error(f"Failed to check models: {e}")
        return {}


def check_python_dependencies() -> bool:
    """Check if required Python packages are installed."""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        ("aiohttp", "aiohttp"),
        ("PyQt6", "PyQt6"),
        ("asyncio", None)  # Built-in, just verify
    ]
    
    all_installed = True
    
    for package_name, import_name in required_packages:
        try:
            if import_name:
                __import__(import_name)
            print_success(f"{package_name} - Installed")
        except ImportError:
            print_error(f"{package_name} - Missing")
            all_installed = False
    
    if not all_installed:
        print()
        print_warning("Missing Python packages. To install:")
        print("  pip install aiohttp PyQt6 --break-system-packages")
        print()
    
    return all_installed


def create_config_file() -> bool:
    """Create configuration file if it doesn't exist."""
    print_header("Checking Configuration")
    
    config_path = Path("cardforge_agent_config.json")
    
    if config_path.exists():
        print_success("Configuration file exists")
        return True
    
    print_info("Creating default configuration file...")
    
    default_config = {
        "orchestration": {
            "enabled": True,
            "ollama_url": "http://localhost:11434",
            "fallback_to_claude_mcp": True,
            "max_retries": 3,
            "timeout_seconds": 300
        },
        "models": {
            "router": "llama3.2:3b",
            "deck_optimizer": "qwen2.5-coder:7b",
            "price_analyzer": "llama3.2:3b",
            "collection_manager": "gemma2:4b",
            "buy_list_generator": "qwen2.5-coder:7b",
            "meta_analyzer": "llama3.1:70b",
            "synergy_finder": "qwen2.5-coder:7b"
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        print_success("Created configuration file")
        return True
    except Exception as e:
        print_error(f"Failed to create config: {e}")
        return False


async def run_system_test() -> bool:
    """Run a quick system test."""
    print_header("Running System Test")
    
    try:
        from cardforge_agent_orchestration import CardForgeOrchestrator, AgentTask
        
        print_info("Testing agent orchestration...")
        
        async with CardForgeOrchestrator() as orchestrator:
            # Health check
            health = await orchestrator.health_check()
            
            if health["status"] == "healthy":
                print_success("Orchestrator initialized successfully")
                print_info(f"Available agents: {', '.join(health['agents_initialized'])}")
                print_info(f"Available models: {len(health['models_available'])}")
                
                # Quick test task
                print_info("Testing simple task routing...")
                task = AgentTask(
                    task_type="collection_analysis",
                    complexity="simple",
                    context={"test": True}
                )
                
                specialist = await orchestrator.route_task(task)
                print_success(f"Router correctly routed to: {specialist}")
                
                return True
            else:
                print_error("Orchestrator health check failed")
                return False
        
    except Exception as e:
        print_error(f"System test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_next_steps(all_checks_passed: bool):
    """Print next steps based on setup results."""
    print_header("Setup Complete")
    
    if all_checks_passed:
        print_success("All checks passed! CardForge agent orchestration is ready.")
        print()
        print("Next steps:")
        print("  1. Run demo: python cardforge_agent_orchestration.py")
        print("  2. Launch GUI: python cardforge_gui_integration.py")
        print("  3. Integrate with CardForge main app")
        print()
    else:
        print_warning("Some checks failed. Please resolve issues above.")
        print()
        print("Common fixes:")
        print("  • Start Ollama: ollama serve")
        print("  • Install models: ollama pull llama3.2:3b")
        print("  • Install packages: pip install aiohttp PyQt6 --break-system-packages")
        print()


async def main():
    """Run full setup and validation."""
    print()
    print(f"{Colors.BOLD}╔══════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.BOLD}║  CardForge Agent Orchestration Setup & Validation       ║{Colors.END}")
    print(f"{Colors.BOLD}╚══════════════════════════════════════════════════════════╝{Colors.END}")
    
    # Track overall status
    checks = {}
    
    # 1. Check Ollama
    checks["ollama"] = await check_ollama_installation()
    
    if checks["ollama"]:
        # 2. Check models (only if Ollama is running)
        model_status = await check_required_models()
        checks["models"] = all(model_status.values()) if model_status else False
    else:
        checks["models"] = False
    
    # 3. Check Python dependencies
    checks["python"] = check_python_dependencies()
    
    # 4. Check/create config
    checks["config"] = create_config_file()
    
    # 5. Run system test (only if everything else passed)
    if all(checks.values()):
        checks["system_test"] = await run_system_test()
    else:
        checks["system_test"] = False
    
    # Print summary and next steps
    all_passed = all(checks.values())
    print_next_steps(all_passed)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
