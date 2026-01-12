#!/usr/bin/env python
"""CardForge Consolidation Validation Script.

Validates the clean architecture structure after consolidation.
Run this script to verify all layers are properly configured.

Usage:
    python scripts/validate_consolidation.py
"""

import sys
import importlib
from pathlib import Path
from typing import NamedTuple

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class ValidationResult(NamedTuple):
    """Result of a validation check."""
    passed: bool
    message: str
    category: str


def validate_imports() -> list[ValidationResult]:
    """Validate all architecture layer imports."""
    results = []
    
    # Core layer imports
    core_imports = [
        ("cardforge.core", "Card"),
        ("cardforge.core", "Collection"),
        ("cardforge.core", "Deck"),
        ("cardforge.core", "CardForgeError"),
        ("cardforge.core", "Rarity"),
        ("cardforge.core", "CardProtocol"),
    ]
    
    for module, attr in core_imports:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            results.append(ValidationResult(True, f"{module}.{attr}", "core"))
        except (ImportError, AttributeError) as e:
            results.append(ValidationResult(False, f"{module}.{attr}: {e}", "core"))
    
    # Data layer imports
    data_imports = [
        ("cardforge.data", "CardRepository"),
        ("cardforge.data", "CollectionRepository"),
        ("cardforge.data", "DatabaseConnection"),
        ("cardforge.data", "get_connection"),
    ]
    
    for module, attr in data_imports:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            results.append(ValidationResult(True, f"{module}.{attr}", "data"))
        except (ImportError, AttributeError) as e:
            results.append(ValidationResult(False, f"{module}.{attr}: {e}", "data"))
    
    # Integrations layer imports
    integrations_imports = [
        ("cardforge.integrations", "ScryfallClient"),
        ("cardforge.integrations", "TCGPlayerClient"),
        ("cardforge.integrations", "MoxfieldClient"),
    ]
    
    for module, attr in integrations_imports:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            results.append(ValidationResult(True, f"{module}.{attr}", "integrations"))
        except (ImportError, AttributeError) as e:
            results.append(ValidationResult(False, f"{module}.{attr}: {e}", "integrations"))
    
    # Services layer imports
    services_imports = [
        ("cardforge.services", "CollectionService"),
        ("cardforge.services", "DeckService"),
        ("cardforge.services", "CardService"),
    ]
    
    for module, attr in services_imports:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            results.append(ValidationResult(True, f"{module}.{attr}", "services"))
        except (ImportError, AttributeError) as e:
            results.append(ValidationResult(False, f"{module}.{attr}: {e}", "services"))
    
    # GUI imports
    gui_imports = [
        ("gui", "CardForgeApp"),
        ("gui", "MainWindow"),
        ("gui", "main"),
    ]
    
    for module, attr in gui_imports:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            results.append(ValidationResult(True, f"{module}.{attr}", "gui"))
        except (ImportError, AttributeError) as e:
            results.append(ValidationResult(False, f"{module}.{attr}: {e}", "gui"))
    
    return results


def validate_directory_structure() -> list[ValidationResult]:
    """Validate the directory structure exists."""
    results = []
    root = Path(__file__).parent.parent
    
    required_dirs = [
        "cardforge/core",
        "cardforge/data",
        "cardforge/integrations",
        "cardforge/services",
        "cardforge/ai",
        "cardforge/cli",
        "cardforge/config",
        "cardforge/models",
        "cardforge/repositories",
        "cardforge/database",
        "gui",
        "archive",
    ]
    
    for dir_path in required_dirs:
        full_path = root / dir_path
        if full_path.exists() and full_path.is_dir():
            results.append(ValidationResult(True, f"Directory: {dir_path}", "structure"))
        else:
            results.append(ValidationResult(False, f"Missing: {dir_path}", "structure"))
    
    return results


def validate_init_files() -> list[ValidationResult]:
    """Validate __init__.py files exist in all packages."""
    results = []
    root = Path(__file__).parent.parent
    
    required_inits = [
        "cardforge/core/__init__.py",
        "cardforge/data/__init__.py",
        "cardforge/integrations/__init__.py",
        "gui/__init__.py",
        "gui/__main__.py",
        "archive/__init__.py",
    ]
    
    for init_path in required_inits:
        full_path = root / init_path
        if full_path.exists():
            results.append(ValidationResult(True, f"File: {init_path}", "init_files"))
        else:
            results.append(ValidationResult(False, f"Missing: {init_path}", "init_files"))
    
    return results


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("CardForge Consolidation Validation")
    print("=" * 70)
    print()
    
    all_results = []
    
    # Run all validators
    print("Checking directory structure...")
    all_results.extend(validate_directory_structure())
    
    print("Checking __init__.py files...")
    all_results.extend(validate_init_files())
    
    print("Checking imports...")
    all_results.extend(validate_imports())
    
    # Group results by category
    categories = {}
    for result in all_results:
        if result.category not in categories:
            categories[result.category] = {"passed": [], "failed": []}
        if result.passed:
            categories[result.category]["passed"].append(result)
        else:
            categories[result.category]["failed"].append(result)
    
    # Print results by category
    print()
    print("=" * 70)
    print("RESULTS BY CATEGORY")
    print("=" * 70)
    
    for category, results in categories.items():
        passed = len(results["passed"])
        failed = len(results["failed"])
        total = passed + failed
        status = "PASS" if failed == 0 else "FAIL"
        print(f"\n[{status}] {category.upper()}: {passed}/{total} passed")
        
        for r in results["failed"]:
            print(f"  ❌ {r.message}")
        
        if failed == 0:
            print(f"  ✅ All {total} checks passed")
    
    # Summary
    total_passed = sum(len(r["passed"]) for r in categories.values())
    total_failed = sum(len(r["failed"]) for r in categories.values())
    total = total_passed + total_failed
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total checks: {total}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print()
    
    if total_failed == 0:
        print("✅ CONSOLIDATION VALIDATION PASSED")
        print("All architecture layers are properly configured!")
        return 0
    else:
        print("❌ CONSOLIDATION VALIDATION FAILED")
        print("Please review the failed checks above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
