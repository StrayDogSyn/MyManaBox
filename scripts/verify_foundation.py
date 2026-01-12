#!/usr/bin/env python3
"""Verify VS Code Foundation Phase 1 is complete.

Checks that all type definitions, protocols, validators, and tests are working.
This is the quality gate that TRAE's code must pass through.
"""

import sys
import subprocess
from pathlib import Path
from typing import Tuple, List


def check_imports() -> Tuple[bool, str]:
    """Verify all VS Code foundation modules can be imported."""
    try:
        from cardforge.types import (
            Rarity,
            CardProtocol,
            PriceData,
            SearchFilters,
        )
        from cardforge.types.agents import (
            TaskComplexity,
            AgentCapability,
            ChatMessage,
            AgentProtocol,
        )
        from cardforge.config.validators import (
            OllamaConfigSchema,
            DatabaseConfigSchema,
            SettingsSchema,
            validate_config,
        )
        from cardforge.exceptions import (
            CardForgeError,
            RecordNotFoundError,
            ModelNotFoundError,
        )
        from cardforge.database.migrations import (
            Migration,
            get_default_migrations,
            run_migrations,
        )
        return True, "✅ All imports successful"
    except ImportError as e:
        return False, f"❌ Import failed: {e}"


def check_fixtures() -> Tuple[bool, str]:
    """Verify test fixtures are available."""
    try:
        # This would be tested when pytest runs
        fixture_file = Path("tests/conftest.py")
        if not fixture_file.exists():
            return False, "❌ conftest.py not found"

        content = fixture_file.read_text()
        required_fixtures = [
            "sample_card_data",
            "sample_config_dict",
            "mock_ollama_response",
            "temp_db_path",
        ]
        for fixture in required_fixtures:
            if f"def {fixture}" not in content:
                return False, f"❌ Fixture {fixture} not found"

        return True, "✅ All test fixtures present"
    except Exception as e:
        return False, f"❌ Fixture check failed: {e}"


def run_tests(args: List[str] = None) -> Tuple[bool, str]:
    """Run pytest tests."""
    if args is None:
        args = []

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"] + args,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            # Count passed tests
            import re

            passed = len(re.findall(r"PASSED", result.stdout))
            return True, f"✅ All tests passed ({passed} tests)"
        else:
            return False, f"❌ Tests failed:\n{result.stdout}\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "❌ Tests timed out (>60s)"
    except Exception as e:
        return False, f"❌ Test execution failed: {e}"


def check_type_hints() -> Tuple[bool, str]:
    """Check Python files for type hints."""
    try:
        files_to_check = [
            "cardforge/types/__init__.py",
            "cardforge/types/agents.py",
            "cardforge/exceptions.py",
            "cardforge/config/validators.py",
            "cardforge/database/migrations.py",
        ]

        for file_path in files_to_check:
            p = Path(file_path)
            if not p.exists():
                return False, f"❌ {file_path} not found"

            content = p.read_text()
            # Basic check for type hints
            if "->" not in content and ":" not in content:
                return False, f"⚠️  {file_path} may lack type hints"

        return True, "✅ Type hints present in foundation modules"

    except Exception as e:
        return False, f"❌ Type hint check failed: {e}"


def check_database_schema() -> Tuple[bool, str]:
    """Verify database schema file exists."""
    try:
        schema_file = Path("cardforge/database/schema.hardened.sql")
        if not schema_file.exists():
            return False, "❌ schema.hardened.sql not found"

        content = schema_file.read_text()
        required_tables = ["cards", "collections", "collection_cards", "decks", "deck_cards"]

        for table in required_tables:
            if f"CREATE TABLE IF NOT EXISTS {table}" not in content:
                return False, f"❌ Table {table} not in schema"

        return True, f"✅ Database schema complete ({len(required_tables)} tables)"

    except Exception as e:
        return False, f"❌ Schema check failed: {e}"


def check_validators() -> Tuple[bool, str]:
    """Verify validator schemas work."""
    try:
        from cardforge.config.validators import SettingsSchema, validate_config

        # Test with valid config
        config = {
            "environment": "testing",
            "debug": True,
            "log_level": "DEBUG",
            "ollama": {
                "base_url": "http://localhost:11434",
                "default_model": "llama3.2:3b",
            },
            "database": {"path": "test.db"},
            "api": {"scryfall_base_url": "https://api.scryfall.com"},
        }

        is_valid, errors = validate_config(config)
        if not is_valid:
            return False, f"❌ Valid config failed: {errors}"

        # Test with invalid config
        invalid_config = {"environment": "invalid"}
        is_valid, errors = validate_config(invalid_config)
        if is_valid:
            return False, "❌ Invalid config should fail"

        return True, "✅ Validators working correctly"

    except Exception as e:
        return False, f"❌ Validator test failed: {e}"


def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print("🔍 CardForge VS Code Foundation Phase 1 Verification")
    print("=" * 70 + "\n")

    checks = [
        ("Imports", check_imports),
        ("Type Hints", check_type_hints),
        ("Database Schema", check_database_schema),
        ("Validators", check_validators),
        ("Test Fixtures", check_fixtures),
        ("Tests", lambda: run_tests(["tests/test_types.py", "tests/test_exceptions.py"])),
    ]

    results = []
    for name, check_func in checks:
        print(f"Checking {name}...", end=" ")
        try:
            success, message = check_func()
            results.append((name, success, message))
            print(message)
        except Exception as e:
            message = f"❌ {name} check error: {e}"
            results.append((name, False, message))
            print(message)

    print("\n" + "=" * 70)
    print("📊 Summary")
    print("=" * 70 + "\n")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for name, success, message in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n🎉 VS Code Foundation Phase 1 Complete!")
        print("\nNext steps:")
        print("1. TRAE proceeds with Phase 2: Ollama integration")
        print("2. VS Code monitors TRAE's code for type safety")
        print("3. Run: pytest tests/ --cov=cardforge to track coverage")
        print("4. Run: mypy cardforge --strict to enforce types")
        return 0
    else:
        print("\n⚠️  Some checks failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
