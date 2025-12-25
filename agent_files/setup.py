#!/usr/bin/env python3
"""
MTG Collection Manager - Quick Setup

First-time setup wizard to get you started quickly.

Usage:
    python setup.py
"""

import sys
from pathlib import Path
import subprocess


def check_python_version():
    """Ensure Python 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        print(f"   Current version: {sys.version}")
        return False
    return True


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    
    packages = [
        "requests",
        "python-dotenv"
    ]
    
    try:
        for package in packages:
            print(f"   Installing {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q"]
            )
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directory structure...")
    
    dirs = [
        "data/collections",
        "data/exports",
        "data/cache",
        "data/decks",
        "exports",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}")
    
    print("✅ Directories created")
    return True


def initialize_database():
    """Create initial database"""
    print("\n🗄️  Initializing database...")
    
    try:
        # Import after dependencies are installed
        sys.path.insert(0, str(Path(__file__).parent))
        from src.catalogue import Collection
        
        collection = Collection("data/collections/main.db")
        collection.close()
        
        print("✅ Database initialized: data/collections/main.db")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False


def test_scryfall():
    """Test Scryfall API connection"""
    print("\n🔍 Testing Scryfall API...")
    
    try:
        from src.api_clients.scryfall import ScryfallClient
        
        client = ScryfallClient(cache_enabled=True)
        card = client.get_card("Lightning Bolt", set_code="lea")
        
        if card:
            print(f"✅ Scryfall connected successfully")
            print(f"   Test card: {card['name']} - ${card['prices']['usd']}")
            return True
        else:
            print("⚠️  Scryfall test failed (card not found)")
            return False
    except Exception as e:
        print(f"❌ Scryfall test failed: {e}")
        return False


def setup_api_keys():
    """Guide user through API key setup"""
    print("\n🔑 API Key Configuration")
    print()
    print("Scryfall API: ✅ No key required (free)")
    print()
    
    response = input("Do you want to set up TCGPlayer API for pricing? (y/N): ")
    
    if response.lower() == 'y':
        print("\n📝 TCGPlayer Setup:")
        print("   1. Go to https://developer.tcgplayer.com/")
        print("   2. Sign up for a developer account")
        print("   3. Create an application to get your API keys")
        print()
        print("   Once you have your keys, edit:")
        print("   config/api_keys.env")
        print()
        input("Press Enter to continue...")
    else:
        print("   Skipping TCGPlayer setup (can configure later)")
    
    return True


def print_next_steps():
    """Show what to do next"""
    print("\n" + "="*60)
    print("🎉 Setup Complete!")
    print("="*60)
    print()
    print("📋 Next Steps:")
    print()
    print("1️⃣  Start scanning cards with ManaBox:")
    print("   • Install ManaBox on your phone")
    print("   • Scan 100-200 cards as a test")
    print("   • Export to CSV from ManaBox")
    print()
    print("2️⃣  Import your first batch:")
    print("   python src/catalogue.py --import your_export.csv")
    print()
    print("3️⃣  Enrich with Scryfall data:")
    print("   python scripts/enrich_collection.py --update-prices")
    print()
    print("4️⃣  Check your collection stats:")
    print("   python src/catalogue.py --stats")
    print()
    print("5️⃣  Export to Moxfield:")
    print("   python src/catalogue.py --export exports/moxfield.csv --format moxfield")
    print()
    print("📚 Documentation:")
    print("   • Full guide: docs/WORKFLOWS.md")
    print("   • API setup: docs/API_INTEGRATION.md")
    print()
    print("="*60)


def main():
    """Run setup wizard"""
    print("="*60)
    print("MTG Collection Manager - Setup Wizard")
    print("="*60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directories),
        ("Initializing database", initialize_database),
        ("Testing Scryfall API", test_scryfall),
        ("Configuring API keys", setup_api_keys),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            print("   Please fix the error and run setup.py again")
            return False
    
    print_next_steps()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
