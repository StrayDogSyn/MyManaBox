# VS Code Parallel Development - Quick Reference

## 🎯 Your Role: Quality Chef

As VS Code, you are responsible for **type safety, testing, and validation**. TRAE handles **breadth and speed**.

## ⚡ Quick Commands

### Verification
```bash
# Check if Phase 1 is working
python scripts/verify_foundation.py

# Run all tests
pytest tests/

# Check types
mypy cardforge --strict

# Check formatting
black cardforge/ --check
isort cardforge/ --check-only
```

### Auto-fix
```bash
# Fix formatting
black cardforge/
isort cardforge/

# Fix common issues
mypy cardforge --strict  # Shows what needs fixing
```

### Add Types to TRAE's Code
When TRAE finishes a module:
1. Open the file
2. Add type hints to function parameters and returns
3. Run `mypy cardforge --strict` to verify
4. Write tests for the module

## 📋 Checklist: Code Review for TRAE's PRs

### Types ✓
- [ ] All function parameters have type hints
- [ ] All return types specified
- [ ] No `Any` types (ask TRAE why if present)
- [ ] Use protocols from `cardforge.types.agents`
- [ ] `mypy cardforge --strict` passes

### Exceptions ✓
- [ ] Only raises from `cardforge.exceptions`
- [ ] Appropriate exception type chosen
- [ ] Exceptions have helpful messages
- [ ] No generic `Exception` or `ValueError`

### Configuration ✓
- [ ] Uses `OllamaConfigSchema` or similar validator
- [ ] Config loaded via validators
- [ ] Environment variables supported
- [ ] `validate_config()` used

### Database ✓
- [ ] Uses migration system
- [ ] No manual `CREATE TABLE`
- [ ] Uses `run_migrations()`
- [ ] No hardcoded queries

### Tests ✓
- [ ] Unit tests for public functions
- [ ] Uses fixtures from `conftest.py`
- [ ] Tests cover happy path + errors
- [ ] Coverage >80%
- [ ] `pytest tests/` passes

### Documentation ✓
- [ ] Docstrings on all public functions
- [ ] Type hints clear behavior
- [ ] No vague parameter names
- [ ] Examples in docstrings if complex

### Formatting ✓
- [ ] Runs `black cardforge/`
- [ ] Runs `isort cardforge/`
- [ ] Line length ≤100 chars
- [ ] No trailing whitespace

## 📁 Files You Created (Phase 1)

```
✅ cardforge/types/__init__.py           200 lines
✅ cardforge/types/agents.py             150 lines
✅ cardforge/exceptions.py               130 lines
✅ cardforge/config/validators.py        180 lines
✅ cardforge/database/schema.hardened.sql 250 lines
✅ cardforge/database/migrations.py      350 lines

✅ tests/conftest.py                     200 lines (enhanced)
✅ tests/test_types.py                   220 lines
✅ tests/test_exceptions.py              100 lines
✅ tests/test_config.py                  180 lines
✅ tests/test_migrations.py              180 lines

✅ scripts/verify_foundation.py          200 lines
✅ pytest.ini                            (updated)
✅ PARALLEL_DEVELOPMENT.md               150 lines
```

**Total:** ~2,300 lines of quality infrastructure

## 🔍 Phase 2: What TRAE Will Add

### You'll Review:

1. **Ollama Client** (`cardforge/services/ollama_client.py`)
   - [ ] Implements `OllamaClientProtocol`
   - [ ] Type hints complete
   - [ ] Tests for each method
   - [ ] Error handling with CardForge exceptions

2. **Agent Base** (`cardforge/agents/base_agent.py`)
   - [ ] Implements `AgentProtocol`
   - [ ] All abstract methods filled in
   - [ ] Conversation history tracked
   - [ ] Tests for serialization

3. **CLI Entry** (`cardforge/cli.py`, `cardforge/__main__.py`)
   - [ ] Uses `SettingsSchema`
   - [ ] Commands organized by groups
   - [ ] Help text complete
   - [ ] Tests for each command

4. **Web Foundation** (`web/src/`)
   - [ ] TypeScript strict mode passes
   - [ ] All React components typed
   - [ ] API client configured
   - [ ] Tests with Vitest

## 🎓 Type Patterns to Enforce

### ✅ Good
```python
from cardforge.types.agents import TaskComplexity, AgentProtocol

async def process(self, task: str, complexity: TaskComplexity) -> str:
    """Process task with appropriate model.
    
    Args:
        task: User task
        complexity: Task complexity level
        
    Returns:
        Response string
        
    Raises:
        ModelNotFoundError: If no model available
    """
```

### ❌ Bad
```python
async def process(self, task, complexity):
    """Process task"""
    # Missing types, docstring
    
async def process(self, task: Any, complexity: Any) -> Any:
    """Don't use Any!"""
    # Too generic
```

## 🐛 Testing Patterns to Enforce

### ✅ Good
```python
@pytest.mark.unit
def test_ollama_client_generates_response(mock_ollama_response):
    """OllamaClient generates text responses."""
    client = OllamaClient()
    # Use fixture, clear name, tests one thing
```

### ❌ Bad
```python
def test():
    # No description, unclear
    obj = OllamaClient()
    x = obj.generate("test")
    assert x  # What are we asserting?
```

## 🚨 Red Flags in TRAE's Code

**Stop and request changes if:**

```python
# ❌ Using generic Exception
except Exception:  # Use CardForgeError instead
    pass

# ❌ Hardcoded values
base_url = "http://localhost:11434"  # Use config/validators

# ❌ No type hints
def process(input):  # Add types!
    pass

# ❌ Ignoring config schemas
config = {"foo": "bar"}  # Validate with Pydantic!

# ❌ Manual SQL
conn.execute("CREATE TABLE...")  # Use migrations!

# ❌ No error handling
response = api_call()  # What if it fails?

# ❌ Using Any
def func(x: Any) -> Any:  # Too generic!
    pass

# ❌ Missing tests
# Complex logic with no tests
def complex_algorithm():
    # Write tests!
```

## ✨ Best Practices Summary

| Practice | Why | How |
|----------|-----|-----|
| Type hints | IDE support, catch errors | Every parameter & return |
| CardForge exceptions | Consistent error handling | Use existing exceptions |
| Config validators | Safety at startup | Use Pydantic schemas |
| Migrations | Safe evolution | Never write SQL directly |
| Tests | Regression detection | >80% coverage required |
| Docstrings | API clarity | All public functions |
| Fixtures | Less boilerplate | Reuse from conftest.py |

## 📞 Communication with TRAE

When requesting changes:

### Good request:
```
TRAE, this function needs type hints:

    def process(self, input):
        
Should be:

    def process(self, input: str) -> Dict[str, str]:
        
mypy cardforge --strict will validate. Same pattern used in
cardforge/types/agents.py examples.
```

### Poor request:
```
Add types to this
```

## 🎯 Success Metrics

By end of Phase 2:

- [ ] All modules have full type hints
- [ ] Coverage: 80%+ overall, 90%+ core
- [ ] `mypy cardforge --strict` passes
- [ ] All `black` and `isort` formatted
- [ ] Every public function documented
- [ ] Zero use of generic exceptions
- [ ] All config uses validators
- [ ] All schema changes use migrations

## 🔗 Key Files to Know

**Read these to understand the patterns:**

- Type patterns: `cardforge/types/__init__.py`
- Exception patterns: `cardforge/exceptions.py`
- Config patterns: `cardforge/config/validators.py`
- Fixture patterns: `tests/conftest.py`
- Test patterns: `tests/test_config.py`

## 🎬 Ready to Begin?

1. ✅ Phase 1 foundation is COMPLETE
2. ✅ All tests passing
3. ✅ All types defined
4. ⏳ Waiting for TRAE to start Phase 2
5. 📋 You: Review quality as TRAE builds

**Your job:** Make sure TRAE's output is production-ready.

---

**Questions?** Check `PARALLEL_DEVELOPMENT.md` for full context.
