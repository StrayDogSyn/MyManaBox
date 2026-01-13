# CardForge Quick Start Guide

**Your immediate next steps to complete the project**

---

## ✅ What We Just Fixed (Today)

1. **All tests passing** - 23/23 foundation tests ✅
2. **Import pipeline verified** - Detected 3,953 cards in your Moxfield CSV ✅
3. **Test fixtures complete** - Added missing `temp_db_path` ✅

---

## 🚀 Execute This Week

### Option 1: Import Your Collection NOW (5 minutes)

```bash
# Navigate to project
cd C:\Users\EHunt\Repos\Projects\MyManaBox

# Activate virtual environment
.venv\Scripts\activate

# Import your Moxfield collection
python scripts/test_import.py --execute

# Verify the import
python -c "from cardforge.database.connection import DatabaseConnection; import asyncio; asyncio.run((lambda: DatabaseConnection('data/cardforge.db').execute('SELECT COUNT(*) FROM cards'))())"
```

**What this does:**

- Creates `data/cardforge.db` with full schema
- Imports 3,953 cards from your Moxfield export
- Creates automatic backup
- Validates all data during import

### Option 2: Test AI Agents First (10 minutes)

```bash
# Check if Ollama is running
ollama list

# If not, start it:
ollama serve

# Test agent registry
python -c "
from cardforge.services.ai.registry import AgentRegistry
registry = AgentRegistry()
print('Available agents:', [agent.name for agent in registry.list_agents()])
"

# Test a simple query
python -m cardforge.services.ai.demo --query 'What cards synergize with Kaalia?'
```

### Option 3: Quick Type Safety Pass (30 minutes)

Add return types to the highest-traffic modules:

**File 1:** `cardforge/config/settings.py`
```python

# Add these return type hints:
def get_env(key: str, default: str = '') -> str:
def load_config() -> Dict[str, Any]:
def get_ollama_config() -> OllamaConfigSchema:
def get_database_config() -> DatabaseConfigSchema:
```

**File 2:** Run mypy check


```bash
python -m mypy cardforge/config/ --strict
```

---

## 📋 This Week's Checklist

Priority order for completing CardForge:

### Day 1: Data Import ✅

- [x] Verify CSV detection
- [ ] Import collection data
- [ ] Test queries on imported data

### Day 2: Integration Tests

- [ ] Add test for database connection
- [ ] Add test for CSV import end-to-end
- [ ] Add test for basic agent initialization

### Day 3: AI Agent Testing

- [ ] Verify Ollama connection
- [ ] Test DeckOptimizer with a deck list
- [ ] Test SynergyFinder with sample cards

### Day 4: Type Safety

- [ ] Add return types to `settings.py`
- [ ] Add return types to `connection.py`
- [ ] Run mypy on core modules

### Day 5: Review & Decide

- [ ] Run full test suite
- [ ] Check test coverage
- [ ] Decide: Continue vs. Pivot vs. Hybrid

---

## 🎯 Decision Framework

After this week, you'll have:

- ✅ Real data in the system
- ✅ AI agents tested
- ✅ Integration points verified
- ✅ Clear picture of remaining work

**Then choose:**

### Path A: Complete CardForge (2-3 more weeks)

**Choose if:** You want the modern architecture and AI features  
**Effort:** 15-20 hours

- Week 2: Expand test suite to 50% coverage
- Week 3: Polish UI components
- Week 4: Deploy and document

### Path B: Enhance MyManaBox (Faster)

**Choose if:** You need working features NOW  
**Effort:** 5-10 hours per feature

- Keep existing UI
- Add specific features to working system
- Use CardForge components as libraries

### Path C: Hybrid Approach (Recommended)

**Choose if:** You want best of both worlds  
**Use:** MyManaBox for daily work, CardForge for advanced features

- Import collection to CardForge
- Use AI agents via CLI
- Keep MyManaBox GUI for browsing
- Gradually migrate as CardForge matures

---

## 📊 Success Metrics

You'll know CardForge is ready when:

- [ ] 3,953+ cards imported
- [ ] 50%+ test coverage
- [ ] All AI agents responding
- [ ] Web UI loads and displays cards
- [ ] Can create and optimize a deck
- [ ] Export works to Moxfield format

---

## 🆘 If You Get Stuck

### Common Issues

**Import fails:**


```bash
# Check file encoding
file data/moxfield_collection_2026-01-12-0154Z.csv

# Try with smaller sample
head -100 data/moxfield_collection_2026-01-12-0154Z.csv > data/sample.csv
python scripts/test_import.py data/sample.csv --execute
```

**Tests fail:**


```bash
# Run with verbose output
pytest tests/ -vv --tb=long

# Run specific test
pytest tests/test_types.py::TestEnumValues -vv
```

**Ollama not responding:**


```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Restart Ollama service
# On Windows: Restart from Services (services.msc)
```

**Type errors:**


```bash
# Check specific file
mypy cardforge/config/settings.py --show-error-codes

# Ignore unavailable imports
mypy cardforge/ --ignore-missing-imports
```

---

## 📞 Quick Commands Reference

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=cardforge --cov-report=html

# Import collection
python scripts/test_import.py --execute

# Start web server
cd web && npm run dev

# Check type hints
mypy cardforge/ --strict

# Run AI demo
python -m cardforge.services.ai.demo

# Database query
sqlite3 data/cardforge.db "SELECT COUNT(*) FROM cards;"
```

---

## 🎓 For Your Students

**Demo Flow:**

1. Show MyManaBox (working legacy system)
2. Explain CardForge architecture (modern refactor)
3. Walk through one module transformation:
   - Legacy: Simple function
   - Modern: Async, typed, tested, with AI
4. Show test-driven development workflow
5. Demonstrate AI agent integration

**Key Lessons:**

- Why async matters (I/O bound operations)
- Type safety catches bugs early
- Repository pattern separates concerns
- Testing enables refactoring confidence
- Modern tools (Pydantic, pytest) save time

---

**Created:** January 12, 2026  
**Status:** Ready to execute ✅  
**Next Action:** Choose Option 1, 2, or 3 above
