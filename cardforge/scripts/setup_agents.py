#!/usr/bin/env python3
"""
CardForge AI System Setup & Validation

Checks Ollama installation, verifies required models, validates dependencies,
and performs health checks before running the orchestration system.

Usage:
    python setup_cardforge_agents.py
    
    Or with specific checks:
    python setup_cardforge_agents.py --check-models
    python setup_cardforge_agents.py --pull-models
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

import aiohttp


class Colors:
    """Terminal color codes."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class CardForgeSetup:
    """Setup and validation for CardForge AI system."""
    
    REQUIRED_MODELS = [
        "llama3.2:3b",
        "qwen2.5-coder:7b",
        "gemma2:4b",
    ]
    
    OPTIONAL_MODELS = [
        "llama3.1:70b",
        "llava:7b",
        "all-minilm",
    ]
    
    PYTHON_PACKAGES = [
        "aiohttp>=3.8.0",
        "PyQt6>=6.0.0",
    ]
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """Initialize setup."""
        self.ollama_host = ollama_host
        self.session = None
        self.project_root = Path(__file__).parent.parent
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def print_header(self, text: str):
        """Print section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
        print(f"{text:^60}")
        print(f"{'='*60}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        """Print success message."""
        print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        """Print error message."""
        print(f"{Colors.RED}✗ {text}{Colors.RESET}")
    
    def print_warning(self, text: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        """Print info message."""
        print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")
    
    async def check_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        if not self.session:
            return False
        try:
            async with self.session.get(
                f"{self.ollama_host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        if not self.session:
            return []
        try:
            async with self.session.get(
                f"{self.ollama_host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    return [m["name"] for m in models]
        except Exception:
            pass
        
        return []
    
    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama registry."""
        print(f"    Pulling {model}...", end=" ", flush=True)
        
        if not self.session:
            print(f"{Colors.RED}session not initialized{Colors.RESET}")
            return False
        
        try:
            async with self.session.post(
                f"{self.ollama_host}/api/pull",
                json={"name": model},
                timeout=aiohttp.ClientTimeout(total=600)  # 10 minutes
            ) as response:
                if response.status == 200:
                    print(f"{Colors.GREEN}done{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.RED}failed (HTTP {response.status}){Colors.RESET}")
                    return False
        except asyncio.TimeoutError:
            print(f"{Colors.RED}timeout{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}error: {e}{Colors.RESET}")
            return False
    
    def check_python_packages(self) -> bool:
        """Check if required Python packages are installed."""
        self.print_header("Python Dependencies")
        
        all_ok = True
        for package in self.PYTHON_PACKAGES:
            # Parse package name and version
            if ">=" in package:
                pkg_name = package.split(">=")[0]
            else:
                pkg_name = package
            
            try:
                __import__(pkg_name.replace("-", "_"))
                self.print_success(f"{package}")
            except ImportError:
                self.print_error(f"{package} - not installed")
                all_ok = False
        
        if not all_ok:
            self.print_warning("Install missing packages with:")
            print(f"    pip install {' '.join(self.PYTHON_PACKAGES)}\n")
        
        return all_ok
    
    async def check_ollama_installation(self) -> bool:
        """Check if Ollama is installed and running."""
        self.print_header("Ollama Status")
        
        # Check if running
        is_running = await self.check_ollama_running()
        
        if is_running:
            self.print_success(f"Ollama running at {self.ollama_host}")
        else:
            self.print_error(f"Ollama not responding at {self.ollama_host}")
            self.print_info("Start Ollama with: ollama serve")
            return False
        
        return True
    
    async def check_models(self) -> Tuple[List[str], List[str]]:
        """Check available models."""
        self.print_header("Model Status")
        
        available = await self.get_available_models()
        
        required_missing = []
        optional_missing = []
        
        # Check required
        for model in self.REQUIRED_MODELS:
            if model in available:
                self.print_success(f"{model} (required)")
            else:
                self.print_error(f"{model} (required) - missing")
                required_missing.append(model)
        
        # Check optional
        for model in self.OPTIONAL_MODELS:
            if model in available:
                self.print_success(f"{model} (optional)")
            else:
                self.print_warning(f"{model} (optional) - missing")
                optional_missing.append(model)
        
        # Show additional installed models
        extra = set(available) - set(self.REQUIRED_MODELS) - set(self.OPTIONAL_MODELS)
        if extra:
            self.print_info(f"Additional models: {', '.join(sorted(extra))}")
        
        return required_missing, optional_missing
    
    async def validate_system(self) -> bool:
        """Perform complete system validation."""
        self.print_header("CardForge AI System Setup")
        
        # Check Ollama
        if not await self.check_ollama_installation():
            return False
        
        # Check models
        required_missing, optional_missing = await self.check_models()
        
        if required_missing:
            self.print_warning("Missing required models. Install with:")
            for model in required_missing:
                print(f"    ollama pull {model}")
            return False
        
        # Check Python packages
        if not self.check_python_packages():
            return False
        
        return True
    
    async def pull_required_models(self):
        """Pull required models."""
        self.print_header("Pulling Required Models")
        
        available = await self.get_available_models()
        missing = [m for m in self.REQUIRED_MODELS if m not in available]
        
        if not missing:
            self.print_success("All required models already installed")
            return
        
        for model in missing:
            success = await self.pull_model(model)
            if not success:
                self.print_error(f"Failed to pull {model}")
    
    async def run_health_check(self) -> bool:
        """Run orchestration health check."""
        self.print_header("System Health Check")
        
        try:
            from cardforge.ai import CardForgeOrchestrator
            
            orchestrator = CardForgeOrchestrator()
            
            # Test task
            test_task = "What is Magic: The Gathering?"
            self.print_info(f"Running test task: '{test_task}'")
            
            result = await orchestrator.execute(test_task)
            
            if result.success:
                self.print_success(f"Health check passed ({result.execution_time:.2f}s)")
                self.print_info(f"Agent: {result.agent_name}")
                self.print_info(f"Model: {result.model_used}")
                return True
            else:
                self.print_error(f"Health check failed: {result.result}")
                return False
        
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False


async def main():
    """Main setup routine."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CardForge AI System Setup & Validation"
    )
    parser.add_argument(
        "--check-models",
        action="store_true",
        help="Check available models"
    )
    parser.add_argument(
        "--pull-models",
        action="store_true",
        help="Pull required models from Ollama registry"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run orchestration health check"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all checks"
    )
    parser.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama server URL"
    )
    
    args = parser.parse_args()
    
    async with CardForgeSetup(args.ollama_host) as setup:
        if args.all or (
            not args.check_models
            and not args.pull_models
            and not args.health_check
        ):
            # Default: full validation
            success = await setup.validate_system()
            if success:
                setup.print_success("System ready for use!")
            sys.exit(0 if success else 1)
        
        if args.check_models or args.all:
            await setup.check_models()
        
        if args.pull_models or args.all:
            await setup.pull_required_models()
        
        if args.health_check or args.all:
            await setup.run_health_check()


if __name__ == "__main__":
    asyncio.run(main())
