#!/usr/bin/env python3
"""
MyManaBox Setup Verification

Checks that everything is properly configured and ready to use.

Usage:
    python scripts/verify_setup.py
    python scripts/verify_setup.py --detailed
"""

import sys
from pathlib import Path
import argparse


def check_python_version() -> tuple[bool, str]:
    """Check Python version."""
    version = sys.version_info
    required = (3, 9)
    
    if version >= required:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)"


def check_venv() -> tuple[bool, str]:
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        return True, f"Virtual environment: {sys.prefix}"
    else:
        return False, "Not in virtual environment (recommended to use .venv)"


def check_dependencies() -> tuple[bool, str]:
    """Check required packages."""
    required = ['pandas', 'requests', 'colorama', 'tabulate']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        return True, f"All dependencies installed: {', '.join(required)}"
    else:
        return False, f"Missing: {', '.join(missing)}"


def check_project_structure() -> tuple[bool, str]:
    """Check project directory structure."""
    project_root = Path(__file__).parent.parent
    
    required_dirs = [
        'src',
        'src/models',
        'src/data',
        'src/services',
        'src/presentation',
        'data',
        'scripts'
    ]
    
    missing = []
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing.append(dir_path)
    
    if not missing:
        return True, "All required directories present"
    else:
        return False, f"Missing directories: {', '.join(missing)}"


def check_collection_file() -> tuple[bool, str]:
    """Check for collection CSV file."""
    project_root = Path(__file__).parent.parent
    
    possible_files = [
        'data/enriched_collection_complete.csv',
        'data/moxfield_export.csv',
        'data/collection.csv'
    ]
    
    found_files = []
    for file_path in possible_files:
        full_path = project_root / file_path
        if full_path.exists():
            # Get file size and line count
            size_mb = full_path.stat().st_size / (1024 * 1024)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f) - 1  # Minus header
                found_files.append(f"{file_path} ({line_count} cards, {size_mb:.1f} MB)")
            except:
                found_files.append(f"{file_path} ({size_mb:.1f} MB)")
    
    if found_files:
        return True, "Collection files:\n    " + "\n    ".join(found_files)
    else:
        return False, "No collection CSV files found in data/"


def check_card_cache() -> tuple[bool, str]:
    """Check card cache file."""
    project_root = Path(__file__).parent.parent
    cache_file = project_root / "card_cache.json"
    
    if cache_file.exists():
        size_mb = cache_file.stat().st_size / (1024 * 1024)
        return True, f"Card cache: {size_mb:.1f} MB"
    else:
        return False, "No card cache found (will be created on first API call)"


def check_scripts() -> tuple[bool, str]:
    """Check enhancement scripts."""
    project_root = Path(__file__).parent.parent
    
    scripts = [
        'scripts/auto_enrich.py',
        'scripts/import_mobile.py',
        'scripts/export_collection.py',
        'scripts/setup_automation.py'
    ]
    
    found = []
    missing = []
    
    for script in scripts:
        if (project_root / script).exists():
            found.append(script.split('/')[-1])
        else:
            missing.append(script.split('/')[-1])
    
    if not missing:
        return True, f"Enhancement scripts: {', '.join(found)}"
    else:
        return False, f"Missing: {', '.join(missing)}"


def check_main_app() -> tuple[bool, str]:
    """Check main application."""
    project_root = Path(__file__).parent.parent
    main_file = project_root / "main.py"
    
    if main_file.exists():
        return True, "main.py present"
    else:
        return False, "main.py not found"


def test_import() -> tuple[bool, str]:
    """Test importing core modules."""
    try:
        project_root = Path(__file__).parent.parent
        
        # Check if src directory has __init__.py files
        src_path = project_root / "src"
        if not (src_path / "__init__.py").exists():
            return False, "src/__init__.py not found (required for imports)"
        
        # Add parent directory to path (not src itself)
        parent_str = str(project_root)
        if parent_str not in sys.path:
            sys.path.insert(0, parent_str)
        
        # Try imports
        import src.models
        import src.data
        import src.services
        
        return True, "All core modules can be imported"
    except Exception as e:
        return False, f"Import error: {str(e)}"


def run_checks(detailed: bool = False) -> list[tuple[str, bool, str]]:
    """Run all checks."""
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_venv),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Main Application", check_main_app),
        ("Core Modules", test_import),
        ("Enhancement Scripts", check_scripts),
        ("Collection Files", check_collection_file),
        ("Card Cache", check_card_cache),
    ]
    
    results = []
    
    for name, check_func in checks:
        success, message = check_func()
        results.append((name, success, message))
    
    return results


def print_results(results: list, detailed: bool = False):
    """Print check results."""
    
    print("\n" + "=" * 60)
    print("MyManaBox Setup Verification")
    print("=" * 60)
    
    all_passed = True
    
    for name, success, message in results:
        status = "✓" if success else "✗"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        
        print(f"\n{color}{status}{reset} {name}")
        
        if detailed or not success:
            print(f"  {message}")
        
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✓ All checks passed! Your MyManaBox is ready to use.")
        print("\nQuick start:")
        print("  python main.py --summary")
        print("  python scripts/auto_enrich.py")
        print("  python scripts/export_collection.py --format moxfield")
    else:
        print("✗ Some checks failed. See above for details.")
        print("\nCommon fixes:")
        print("  Missing dependencies: pip install -r requirements.txt")
        print("  Not in venv: .venv\\Scripts\\Activate.ps1")
        print("  No collection: Import CSV with python scripts/import_mobile.py")
    
    print("=" * 60 + "\n")
    
    return all_passed


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Verify MyManaBox setup and configuration"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information for all checks"
    )
    
    args = parser.parse_args()
    
    results = run_checks(args.detailed)
    all_passed = print_results(results, args.detailed)
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
