# CardForge: Parallel Development with TRAE & VS Code

## 🎯 The Two-Chef Kitchen Model

This project uses a **parallel development model** where:

- **TRAE** (Autonomous Coding Agent) = Line Cook
  - Fast scaffolding and broad implementation
  - Creates features quickly
  - Moves rapidly across all layers

- **VS Code** (You) = Sous Chef
  - Quality gates and precision work
  - Type safety, testing, validation
  - Catches edges and polishes output

## 📋 Phase 1: Foundation (COMPLETE ✅)

### What Was Built

VS Code created the quality foundation that TRAE will implement against:

#### 1. **Type Definitions & Protocols** (`cardforge/types/`)
- `__init__.py` - Core types (Rarity, Condition, Foil, Language, Format)
- `agents.py` - Agent system types (TaskComplexity, AgentCapability, MessageRole)
- All use `@runtime_checkable` protocols for type safety
- Enum base classes inherit from `str` for JSON serialization

**Usage:**
```python
from cardforge.types import Rarity, CardProtocol
from cardforge.types.agents import TaskComplexity, AgentProtocol

# TRAE implements against these contracts
```

#### 2. **Exception Hierarchy** (`cardforge/exceptions.py`)
- Centralized exception definitions
- Inheritance chain: `CardForgeError` → specific exceptions
- Covers: Config, Database, API, Agent, Validation errors

**Usage:**
```python
from cardforge.exceptions import (
    RecordNotFoundError,
    ModelNotFoundError,
    ContextTooLargeError
)

# TRAE raises these, VS Code tests them
```

#### 3. **Configuration Validators** (`cardforge/config/validators.py`)
- Pydantic v2 schemas for runtime validation
- `OllamaConfigSchema`, `DatabaseConfigSchema`, `ApiConfigSchema`
- Root `SettingsSchema` for complete config validation
- Helper functions: `validate_config()`, `validate_config_file()`

**Usage:**
```python
from cardforge.config.validators import SettingsSchema, validate_config

# TRAE writes config loader using these schemas
settings = SettingsSchema(**config_dict)  # Validates automatically
```

#### 4. **Database Schema (Hardened)** (`cardforge/database/schema.hardened.sql`)
- Production-ready SQLite schema with:
  - Foreign key constraints
  - CHECK constraints
  - Proper indexes for performance
  - FTS5 full-text search
  - Auto-update triggers
- Tables: `cards`, `collections`, `collection_cards`, `decks`, `deck_cards`

#### 5. **Migration System** (`cardforge/database/migrations.py`)
- Safe migration application with checksums
- Prevents re-application and detects corruption
- `Migration` class encapsulates version, name, SQL
- `run_migrations()` orchestrates safe application
- Default migration includes complete schema

**Usage:**
```python
from cardforge.database.migrations import run_migrations, get_default_migrations

# Initialize database
success, messages = run_migrations(db_path, get_default_migrations())
```

#### 6. **Test Infrastructure** (`tests/conftest.py`)
- Shared pytest fixtures
- Sample data fixtures for all model types
- Mock fixtures for external services
- Configuration fixtures
- Database fixtures with cleanup

**Usage:**
```python
def test_something(sample_card_data, temp_db_path, mock_ollama_response):
    # Fixtures automatically injected by pytest
```

#### 7. **Test Suite** (Initial tests)
- `test_types.py` - Type definitions and protocols
- `test_exceptions.py` - Exception hierarchy
- `test_config.py` - Validator schemas
- `test_migrations.py` - Migration system
- All with comprehensive coverage

### Quality Gates

Before TRAE's code is merged, it must pass:

```bash
# Type checking
mypy cardforge --strict

# Test coverage
pytest tests/ --cov=cardforge --cov-report=term-missing

# Test discovery
pytest tests/ -v

# Linting
black cardforge/ --check
isort cardforge/ --check-only
```

## 🚀 Phase 2: TRAE Develops (Next)

### What TRAE Will Build

Against the VS Code contracts:

1. **Settings Configuration**
   - Implements `SettingsSchema`
   - Environment variable support
   - `.env` file loading

2. **CLI Entry Point**
   - Unified `cardforge` command
   - Subcommands for collections, decks, agents

3. **Ollama Integration**
   - Implements `OllamaClientProtocol`
   - Model routing by complexity
   - Streaming support

4. **Agent System**
   - Implements `AgentProtocol`
   - `DeckOptimizerAgent`
   - `AgentRegistry` for discovery

5. **Web Foundation**
   - React + TypeScript setup
   - Vite configuration
   - API client layer

### VS Code Quality Control

As TRAE creates each module, VS Code:

1. **Adds Type Hints**
   - Fill in `Any` types
   - Add `-> ReturnType` annotations
   - Run: `mypy cardforge --strict`

2. **Writes Tests**
   - Unit tests for each module
   - Integration tests for workflows
   - Run: `pytest tests/`

3. **Validates Config**
   - Ensure validators catch errors
   - Test edge cases
   - Test environment variable support

4. **Hardens Database**
   - Add missing constraints
   - Create indexes
   - Test migrations

5. **Documents**
   - Add docstrings
   - Create API docs
   - Update README

## 📁 Project Structure (Phase 1 Complete)

```
cardforge/
├── types/
│   ├── __init__.py           ✅ Core types
│   └── agents.py             ✅ Agent types
├── exceptions.py             ✅ Exception hierarchy
├── config/
│   └── validators.py         ✅ Pydantic schemas
├── database/
│   ├── schema.hardened.sql   ✅ Hardened schema
│   └── migrations.py         ✅ Migration system
└── (TRAE will add: ai/, services/, cli/, gui/, etc)

tests/
├── conftest.py               ✅ Fixtures
├── test_types.py            ✅ Type tests
├── test_exceptions.py       ✅ Exception tests
├── test_config.py           ✅ Validator tests
└── test_migrations.py       ✅ Migration tests
```

## 🔄 Parallel Development Workflow

### Timeline

```
Hour 1-2: ✅ COMPLETE
  TRAE → Config, CLI setup
  VS Code → Type definitions, protocols, fixtures

Hour 3-4: ⏳ TRAE STARTS
  TRAE → Ollama client, base agent
  VS Code → Add types to TRAE's code, write tests

Hour 5-6:
  TRAE → Deck optimizer, registry
  VS Code → Type annotations, integration tests

Hour 7-8:
  TRAE → Web foundation, React setup
  VS Code → TypeScript strict mode, API types

Hour 9-10:
  TRAE → UI components
  VS Code → Integration tests, performance tests
```

### Command Reference

**Verify foundation:**
```bash
python scripts/verify_foundation.py
```

**Run tests:**
```bash
pytest tests/
pytest tests/ --cov=cardforge --cov-report=term-missing
pytest tests/test_types.py -v
```

**Type checking:**
```bash
mypy cardforge --strict
```

**Linting:**
```bash
black cardforge/ --check
isort cardforge/ --check-only
flake8 cardforge/ --max-line-length=100
```

**Auto-fix:**
```bash
black cardforge/
isort cardforge/
```

## 🎯 Quality Metrics

### Target Coverage
- Overall: **80%+**
- Critical paths: **90%+**
- Types: **0 `Any` types** (strict mode)
- Linting: **0 errors**

### Success Criteria

✅ Phase 1 Foundation Complete:
- [ ] All types defined and protocols created
- [ ] Exception hierarchy in place
- [ ] Validators working
- [ ] Schema hardened
- [ ] Migration system working
- [ ] Test fixtures available
- [ ] Initial test suite passing

⏳ Phase 2 (TRAE's Work):
- [ ] Ollama client typed and tested
- [ ] Agent base class with tests
- [ ] CLI entry point working
- [ ] Web foundation with React + TypeScript

## 📚 For TRAE: Implementation Checklist

When building Phase 2, follow this pattern:

1. **Start with existing types/protocols**
   ```python
   from cardforge.types.agents import AgentProtocol, TaskComplexity
   from cardforge.exceptions import ModelNotFoundError, AgentTimeoutError
   ```

2. **Implement against contracts**
   ```python
   class OllamaClient(OllamaClientProtocol):
       async def generate(self, request: OllamaGenerateRequest) -> str:
           # Implement meeting the protocol
   ```

3. **Use existing validators**
   ```python
   from cardforge.config.validators import OllamaConfigSchema
   
   config = OllamaConfigSchema(
       base_url=os.getenv("OLLAMA_URL", "http://localhost:11434")
   )
   ```

4. **Raise proper exceptions**
   ```python
   from cardforge.exceptions import ModelNotFoundError
   
   if model not in available_models:
       raise ModelNotFoundError(f"Model {model} not found")
   ```

5. **Write docstrings**
   ```python
   def process(self, input: str) -> str:
       """Process input and return response.
       
       Args:
           input: User input
           
       Returns:
           Response string
           
       Raises:
           ModelNotFoundError: If model unavailable
       """
   ```

## 🛡️ Code Review Checklist

Before merging TRAE's PRs:

- [ ] Type hints: `mypy cardforge --strict` passes
- [ ] Tests: `pytest tests/` passes with >80% coverage
- [ ] Linting: `black` and `isort` formatted
- [ ] Docstrings: All public functions documented
- [ ] Exception handling: Uses CardForge exceptions
- [ ] Config: Uses validators
- [ ] Database: Uses migrations
- [ ] No hardcoded strings: Uses config/constants

## 🚀 Deployment Ready (After Phase 6)

Once all phases complete:

1. **Quality metrics met**
   - Type coverage: 100%
   - Test coverage: 80%+
   - All linting passes

2. **Docker deployable**
   ```bash
   docker-compose up
   ```

3. **CI/CD ready**
   - GitHub Actions for testing
   - Automated coverage reporting
   - Pre-commit hooks

4. **Production ready**
   - Database migrations safe
   - Error handling comprehensive
   - Types strictly enforced

---

**This is a living document. Update as the project evolves.**
