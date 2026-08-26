#!/usr/bin/env python3
"""
CardForge Auto-Launcher
Automatically starts Ollama and handles all initialization before running CardForge.
Use this instead of running CardForge commands directly.

Usage:
    python cardforge.py import data/cards.csv
    python cardforge.py stats
    python cardforge.py ai "What cards synergize with Kaalia?"
    python cardforge.py web
"""

import sys
import subprocess
import time
import requests
import os
import signal
from pathlib import Path
from typing import Optional, List
import atexit

# Windows cp1252 terminals cannot encode emoji -- use UTF-8 with replacement
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class OllamaManager:
    """Manages Ollama lifecycle automatically."""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.ollama_process: Optional[subprocess.Popen] = None
        self.started_by_us = False
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def ensure_running(self) -> bool:
        """
        Ensure Ollama is running, start it if necessary.
        Returns True if Ollama is available.
        """
        # Check if already running
        if self.is_running():
            return True
        
        # Try to start Ollama
        print("🚀 Starting Ollama...")
        
        if not self.is_installed():
            print("❌ Ollama not installed!")
            print("   Install from: https://ollama.com/download")
            return False
        
        if self.start():
            print("✅ Ollama started")
            return True
        else:
            print("❌ Failed to start Ollama")
            print("   Try running 'ollama serve' manually")
            return False
    
    def is_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def is_running(self) -> bool:
        """Check if Ollama is responding."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start(self) -> bool:
        """Start Ollama server."""
        try:
            # Start Ollama in background
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent
            )
            
            self.started_by_us = True
            
            # Wait for it to be ready
            for i in range(15):
                time.sleep(1)
                if self.is_running():
                    return True
            
            return False
        
        except Exception as e:
            print(f"Error starting Ollama: {e}")
            return False
    
    def cleanup(self):
        """Stop Ollama if we started it."""
        if self.started_by_us and self.ollama_process:
            try:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=5)
            except:
                try:
                    self.ollama_process.kill()
                except:
                    pass
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.cleanup()
        sys.exit(0)


class CardForgeLauncher:
    """Main launcher that ensures all dependencies are ready."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ollama_manager = OllamaManager()
    
    def run(self, args: List[str]):
        """Run CardForge command with auto-initialization."""
        # Ensure Ollama is running
        if not self.ollama_manager.ensure_running():
            print("\n⚠️  Ollama is required but not available")
            print("CardForge will run but AI features will be disabled")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
        
        # Check database exists
        db_path = self.project_root / "data" / "cardforge.db"
        if not db_path.exists():
            print("\n⚠️  Database not initialized")
            print("Run setup first: python setup_wizard.py")
            response = input("Initialize now? (y/n): ")
            if response.lower() == 'y':
                self.run_setup()
            else:
                sys.exit(1)
        
        # Execute command
        if not args:
            self.print_help()
            return
        
        command = args[0]
        
        if command == "import":
            self.run_import(args[1:])
        elif command == "stats":
            self.run_stats()
        elif command == "search":
            self.run_search(args[1:])
        elif command == "ai":
            self.run_ai(args[1:])
        elif command == "web":
            self.run_web()
        elif command == "gui":
            self.run_gui()
        elif command == "setup":
            self.run_setup()
        else:
            self.print_help()
    
    def run_import(self, args: List[str]):
        """Import collection from CSV."""
        if not args:
            print("Usage: cardforge.py import <csv_file>")
            return
        
        csv_file = args[0]
        
        print(f"📦 Importing {csv_file}...")
        
        result = subprocess.run(
            [sys.executable, "scripts/test_import.py", csv_file, "--execute"],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def run_stats(self):
        """Show collection statistics."""
        print("📊 Collection Statistics")
        print("=" * 60)
        
        result = subprocess.run(
            [sys.executable, "-m", "cardforge.cli", "stats"],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def run_search(self, args: List[str]):
        """Search for cards."""
        if not args:
            print("Usage: cardforge.py search <query>")
            return
        
        query = " ".join(args)
        
        result = subprocess.run(
            [sys.executable, "-m", "cardforge.cli", "search", query],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def run_ai(self, args: List[str]):
        """Run AI agent."""
        if not args:
            print("Usage: cardforge.py ai <query>")
            return
        
        query = " ".join(args)
        
        print(f"🤖 AI Agent: {query}")
        print("=" * 60)
        
        result = subprocess.run(
            [sys.executable, "-m", "cardforge.services.ai.demo", "--query", query],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def run_web(self):
        """Start web interface."""
        web_dir = self.project_root / "web"
        
        if not web_dir.exists():
            print("❌ Web interface not found")
            return
        
        print("🌐 Starting web interface...")
        print("   URL: http://localhost:5173")
        print("   Press Ctrl+C to stop")
        print()
        
        try:
            # Start API backend
            api_process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "cardforge.api.main:app", "--reload"],
                cwd=self.project_root
            )
            
            # Start frontend
            frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=web_dir
            )
            
            # Wait for processes
            try:
                api_process.wait()
                frontend_process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Shutting down...")
                api_process.terminate()
                frontend_process.terminate()
                api_process.wait()
                frontend_process.wait()
        
        except Exception as e:
            print(f"❌ Error starting web interface: {e}")
    
    def run_gui(self):
        """Start GUI application."""
        print("🖥️  Starting GUI...")
        
        result = subprocess.run(
            [sys.executable, "-m", "gui.main"],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def run_setup(self):
        """Run setup wizard."""
        print("🔧 Running setup wizard...")
        
        result = subprocess.run(
            [sys.executable, "setup_wizard.py"],
            cwd=self.project_root
        )
        
        sys.exit(result.returncode)
    
    def print_help(self):
        """Print help message."""
        print("""
CardForge - MTG Collection Manager
Auto-starts Ollama and handles initialization automatically

Usage:
    python cardforge.py <command> [args]

Commands:
    import <file>     Import collection from CSV
    stats             Show collection statistics
    search <query>    Search for cards
    ai <query>        Ask AI agent a question
    web               Start web interface
    gui               Start desktop GUI
    setup             Run setup wizard

Examples:
    python cardforge.py import data/my_collection.csv
    python cardforge.py search "Lightning Bolt"
    python cardforge.py ai "What cards synergize with Kaalia?"
    python cardforge.py stats
    python cardforge.py web

First time setup:
    python cardforge.py setup

Tips:
    - Ollama starts automatically (no need to run 'ollama serve')
    - Database initializes automatically on first run
    - Press Ctrl+C to stop any running command
        """)


def main():
    """Main entry point."""
    launcher = CardForgeLauncher()
    launcher.run(sys.argv[1:])


if __name__ == '__main__':
    main()
