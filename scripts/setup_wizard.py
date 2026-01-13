#!/usr/bin/env python3
"""
CardForge Setup Wizard
Handles all initialization including Ollama, database, and dependencies.
Run this once to get CardForge ready to use.
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path
from typing import Optional, Tuple, List
import platform


class Color:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SetupWizard:
    """CardForge setup wizard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.ollama_url = "http://localhost:11434"
        self.required_models = [
            ("llama3:8b", "8B parameter model for main tasks"),
            ("llama3:70b", "70B parameter model for complex analysis (optional)")
        ]
        self.steps_completed = []
        self.is_windows = platform.system() == "Windows"
    
    def run(self):
        """Run the complete setup wizard."""
        self.print_header()
        
        try:
            # Step 1: Check Python environment
            if self.check_python_environment():
                self.steps_completed.append("Python environment")
            
            # Step 2: Check/install dependencies
            if self.check_dependencies():
                self.steps_completed.append("Dependencies")
            
            # Step 3: Check/start Ollama
            if self.setup_ollama():
                self.steps_completed.append("Ollama setup")
            
            # Step 4: Initialize database
            if self.setup_database():
                self.steps_completed.append("Database")
            
            # Step 5: Create directories
            if self.setup_directories():
                self.steps_completed.append("Directories")
            
            # Step 6: Create config file
            if self.setup_config():
                self.steps_completed.append("Configuration")
            
            # Step 7: Verify installation
            if self.verify_installation():
                self.steps_completed.append("Verification")
            
            self.print_success()
            
        except KeyboardInterrupt:
            print(f"\n\n{Color.YELLOW}Setup cancelled by user{Color.END}")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n{Color.RED}Setup failed: {e}{Color.END}")
            self.print_troubleshooting()
            sys.exit(1)
    
    def print_header(self):
        """Print setup wizard header."""
        print(f"{Color.BOLD}{Color.BLUE}")
        print("=" * 70)
        print("  CardForge Setup Wizard")
        print("  Automated initialization for your MTG collection manager")
        print("=" * 70)
        print(f"{Color.END}\n")
    
    def print_step(self, step: str):
        """Print current step."""
        print(f"\n{Color.BOLD}► {step}{Color.END}")
    
    def print_ok(self, message: str):
        """Print success message."""
        print(f"  {Color.GREEN}✓{Color.END} {message}")
    
    def print_warning(self, message: str):
        """Print warning message."""
        print(f"  {Color.YELLOW}⚠{Color.END} {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"  {Color.RED}✗{Color.END} {message}")
    
    def check_python_environment(self) -> bool:
        """Check Python version and virtual environment."""
        self.print_step("Checking Python environment")
        
        # Check Python version
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.print_error(f"Python 3.9+ required (found {version.major}.{version.minor})")
            return False
        
        # Check if in virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.print_ok("Virtual environment active")
        else:
            self.print_warning("Not in a virtual environment (recommended)")
            response = input("  Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return False
        
        return True
    
    def check_dependencies(self) -> bool:
        """Check and install Python dependencies."""
        self.print_step("Checking dependencies")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            self.print_warning("requirements.txt not found")
            return True
        
        try:
            # Install dependencies
            print("  Installing dependencies...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "-q"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.print_ok("Dependencies installed")
                return True
            else:
                self.print_error(f"Failed to install dependencies: {result.stderr}")
                return False
        
        except Exception as e:
            self.print_error(f"Error installing dependencies: {e}")
            return False
    
    def setup_ollama(self) -> bool:
        """Setup Ollama (check if running, start if needed, download models)."""
        self.print_step("Setting up Ollama (Local LLM)")
        
        # Check if Ollama is installed
        if not self.is_ollama_installed():
            self.print_error("Ollama not installed")
            self.print_ollama_install_instructions()
            return False
        
        self.print_ok("Ollama installed")
        
        # Check if Ollama is running
        if not self.is_ollama_running():
            self.print_warning("Ollama not running")
            
            if self.start_ollama():
                self.print_ok("Ollama started")
            else:
                self.print_error("Failed to start Ollama")
                self.print_ollama_manual_start()
                return False
        else:
            self.print_ok("Ollama running")
        
        # Check/download models
        return self.setup_ollama_models()
    
    def is_ollama_installed(self) -> bool:
        """Check if Ollama is installed."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama(self) -> bool:
        """Start Ollama server."""
        try:
            if self.is_windows:
                # On Windows, Ollama runs as a service
                # Try to start the service
                result = subprocess.run(
                    ["net", "start", "Ollama"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    # Service might already be running or doesn't exist
                    # Try starting Ollama directly
                    subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            else:
                # On Unix, start Ollama in background
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Wait for Ollama to start
            print("  Waiting for Ollama to start", end="")
            for _ in range(10):
                time.sleep(1)
                print(".", end="", flush=True)
                if self.is_ollama_running():
                    print()
                    return True
            
            print()
            return False
        
        except Exception as e:
            print(f"\n  Error starting Ollama: {e}")
            return False
    
    def setup_ollama_models(self) -> bool:
        """Check and download required Ollama models."""
        print("  Checking Ollama models...")
        
        # Get list of installed models
        installed_models = self.get_installed_models()
        
        for model_name, description in self.required_models:
            if self.is_model_installed(model_name, installed_models):
                self.print_ok(f"Model available: {model_name}")
            else:
                if "optional" in description.lower():
                    self.print_warning(f"Optional model not installed: {model_name}")
                    response = input(f"  Download {model_name}? (y/n): ")
                    if response.lower() != 'y':
                        continue
                
                print(f"  Downloading {model_name} ({description})...")
                print(f"  {Color.YELLOW}This may take 5-15 minutes depending on your connection{Color.END}")
                
                if self.download_model(model_name):
                    self.print_ok(f"Downloaded: {model_name}")
                else:
                    if "optional" not in description.lower():
                        self.print_error(f"Failed to download required model: {model_name}")
                        return False
                    else:
                        self.print_warning(f"Failed to download optional model: {model_name}")
        
        return True
    
    def get_installed_models(self) -> List[str]:
        """Get list of installed Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def is_model_installed(self, model_name: str, installed_models: List[str]) -> bool:
        """Check if a model is installed."""
        # Handle both "llama3:8b" and "llama3" formats
        base_name = model_name.split(':')[0]
        return any(
            model_name in model or base_name in model
            for model in installed_models
        )
    
    def download_model(self, model_name: str) -> bool:
        """Download an Ollama model."""
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"  Error downloading model: {e}")
            return False
    
    def print_ollama_install_instructions(self):
        """Print instructions for installing Ollama."""
        print(f"\n{Color.YELLOW}Ollama Installation Required:{Color.END}")
        print("  1. Visit: https://ollama.com/download")
        print("  2. Download installer for your OS")
        print("  3. Run installer")
        print("  4. Run this setup wizard again")
        print()
    
    def print_ollama_manual_start(self):
        """Print instructions for manually starting Ollama."""
        print(f"\n{Color.YELLOW}Manual Start Required:{Color.END}")
        if self.is_windows:
            print("  Option 1: Start Ollama from Start Menu")
            print("  Option 2: Run 'ollama serve' in a terminal")
        else:
            print("  Run 'ollama serve' in a separate terminal")
        print("  Then run this setup wizard again")
        print()
    
    def setup_database(self) -> bool:
        """Initialize database."""
        self.print_step("Setting up database")
        
        data_dir = self.project_root / "data"
        db_path = data_dir / "cardforge.db"
        
        if db_path.exists():
            self.print_warning("Database already exists")
            response = input("  Reinitialize database? (y/n): ")
            if response.lower() != 'y':
                self.print_ok("Using existing database")
                return True
        
        try:
            # Run database initialization script
            init_script = self.project_root / "scripts" / "init_database.py"
            
            if not init_script.exists():
                # Create inline initialization
                self.init_database_inline(db_path)
            else:
                result = subprocess.run(
                    [sys.executable, str(init_script)],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.print_error(f"Database init failed: {result.stderr}")
                    return False
            
            self.print_ok("Database initialized")
            return True
        
        except Exception as e:
            self.print_error(f"Error initializing database: {e}")
            return False
    
    def init_database_inline(self, db_path: Path):
        """Initialize database inline (fallback method)."""
        import sqlite3
        
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scryfall_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                set_code TEXT,
                collector_number TEXT,
                rarity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                card_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                foil TEXT DEFAULT 'normal',
                condition TEXT DEFAULT 'NM',
                language TEXT DEFAULT 'English',
                FOREIGN KEY (collection_id) REFERENCES collections(id),
                FOREIGN KEY (card_id) REFERENCES cards(id),
                UNIQUE(collection_id, card_id, foil, condition, language)
            )
        """)
        
        # Create default collection
        cursor.execute("""
            INSERT OR IGNORE INTO collections (id, name, is_default)
            VALUES (1, 'My Collection', 1)
        """)
        
        conn.commit()
        conn.close()
    
    def setup_directories(self) -> bool:
        """Create required directories."""
        self.print_step("Creating directories")
        
        directories = [
            "data",
            "data/imports",
            "data/exports",
            "data/cache",
            "data/backups",
            "logs"
        ]
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.print_ok("Directories created")
        return True
    
    def setup_config(self) -> bool:
        """Create configuration file."""
        self.print_step("Creating configuration")
        
        config_file = self.project_root / ".env"
        
        if config_file.exists():
            self.print_warning("Config file already exists")
            return True
        
        config_content = f"""# CardForge Configuration
# Auto-generated by setup wizard

# Ollama Settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL_DEFAULT=llama3:8b
OLLAMA_MODEL_COMPLEX=llama3:70b

# Database
DATABASE_PATH=data/cardforge.db

# API Settings (optional)
# SCRYFALL_API_KEY=
# TCGPLAYER_API_KEY=
# MOXFIELD_API_KEY=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/cardforge.log
"""
        
        config_file.write_text(config_content)
        self.print_ok("Configuration created")
        return True
    
    def verify_installation(self) -> bool:
        """Verify the installation."""
        self.print_step("Verifying installation")
        
        checks = [
            ("Ollama running", self.is_ollama_running),
            ("Database exists", lambda: (self.project_root / "data" / "cardforge.db").exists()),
            ("Config exists", lambda: (self.project_root / ".env").exists()),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            if check_func():
                self.print_ok(check_name)
            else:
                self.print_error(check_name)
                all_passed = False
        
        return all_passed
    
    def print_success(self):
        """Print success message with next steps."""
        print(f"\n{Color.GREEN}{Color.BOLD}")
        print("=" * 70)
        print("  ✓ Setup Complete!")
        print("=" * 70)
        print(f"{Color.END}\n")
        
        print("Completed steps:")
        for step in self.steps_completed:
            print(f"  {Color.GREEN}✓{Color.END} {step}")
        
        print(f"\n{Color.BOLD}Next Steps:{Color.END}")
        print("  1. Import your collection:")
        print(f"     {Color.BLUE}python scripts/test_import.py --execute{Color.END}")
        print()
        print("  2. Test AI agents:")
        print(f"     {Color.BLUE}python -m cardforge.cli ai chat 'What cards synergize with Kaalia?'{Color.END}")
        print()
        print("  3. Start web interface:")
        print(f"     {Color.BLUE}cd web && npm run dev{Color.END}")
        print()
        print("  4. View collection stats:")
        print(f"     {Color.BLUE}python -m cardforge.cli stats{Color.END}")
        print()
    
    def print_troubleshooting(self):
        """Print troubleshooting information."""
        print(f"\n{Color.YELLOW}Troubleshooting:{Color.END}")
        print("  1. Check logs: logs/cardforge.log")
        print("  2. Verify Ollama: ollama list")
        print("  3. Test database: sqlite3 data/cardforge.db '.tables'")
        print("  4. Re-run setup: python setup_wizard.py")
        print()
        print("  For help: https://github.com/yourusername/cardforge/issues")
        print()


def main():
    """Main entry point."""
    wizard = SetupWizard()
    wizard.run()


if __name__ == '__main__':
    main()
