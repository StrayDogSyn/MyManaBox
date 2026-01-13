# CardForge Auto-Initialization Integration Checklist

**Ensure seamless startup with zero manual steps**

---

## 📋 Files to Add to Consolidated Repository

### Core Auto-Start Files
- [ ] `setup_wizard.py` - One-time setup with Ollama check
- [ ] `cardforge.py` - Main launcher with auto-initialization
- [ ] `start_cardforge.bat` - Windows double-click launcher
- [ ] `STREAMLINED_QUICKSTART.md` - Updated quick start guide

### Updated Documentation
- [ ] Update `README.md` with new launcher usage
- [ ] Update `GETTING_STARTED.md` to use auto-launcher
- [ ] Add troubleshooting for Ollama auto-start

---

## 🔧 Integration Steps

### Step 1: Add Files to Repository Root

```bash
cd C:\Users\EHunt\Repos\Projects\mtg-collection-manager

# Copy new files
cp /path/to/setup_wizard.py .
cp /path/to/cardforge.py .
cp /path/to/start_cardforge.bat .
cp /path/to/STREAMLINED_QUICKSTART.md docs/
```

### Step 2: Update Main README.md

Add this section at the top:

```markdown
## Quick Start (Automated)

**Windows:** Double-click `start_cardforge.bat`

**Any OS:**
```bash
# One-time setup
python setup_wizard.py

# Daily use (auto-starts Ollama!)
python cardforge.py stats
python cardforge.py import data/collection.csv
python cardforge.py ai "What cards synergize with Kaalia?"
```

No need to manually start Ollama - the launcher handles it!
```

### Step 3: Update Dependencies

Add to `requirements.txt`:
```
requests>=2.31.0  # For Ollama health checks
```

### Step 4: Create .env.example

```bash
# Create .env.example with defaults
cat > .env.example << EOF
# CardForge Configuration
# Copy to .env and customize

# Ollama Settings
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL_DEFAULT=llama3:8b
OLLAMA_MODEL_COMPLEX=llama3:70b
OLLAMA_AUTO_START=true

# Database
DATABASE_PATH=data/cardforge.db

# API Keys (optional)
SCRYFALL_API_KEY=
TCGPLAYER_API_KEY=

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/cardforge.log
EOF
```

### Step 5: Test Auto-Start System

```bash
# Test 1: Setup wizard
python setup_wizard.py
# Expected: Completes without errors, starts Ollama, downloads models

# Test 2: Launcher (cold start)
# Stop Ollama first
taskkill /F /IM ollama.exe  # Windows
# or
killall ollama  # Unix

# Run launcher
python cardforge.py stats
# Expected: Auto-starts Ollama, shows stats

# Test 3: Batch file (Windows only)
start_cardforge.bat
# Expected: Interactive menu appears

# Test 4: Multiple commands
python cardforge.py import data/test.csv
python cardforge.py ai "test query"
python cardforge.py stats
# Expected: All work without manual Ollama management
```

---

## ✅ Verification Checklist

### Installation
- [ ] Setup wizard runs without errors
- [ ] Ollama detected or installation instructions shown
- [ ] Ollama auto-starts if not running
- [ ] Required models downloaded (llama3:8b)
- [ ] Database initialized with schema
- [ ] Directories created (data/, logs/, etc.)
- [ ] Config file generated (.env)

### Launcher Functionality
- [ ] `python cardforge.py` shows help
- [ ] `python cardforge.py import` works
- [ ] `python cardforge.py stats` works
- [ ] `python cardforge.py ai` works
- [ ] `python cardforge.py web` starts both servers
- [ ] Ollama auto-starts when needed
- [ ] Graceful cleanup on Ctrl+C

### Windows Batch File
- [ ] Double-click opens correctly
- [ ] Menu displays properly
- [ ] All menu options work
- [ ] Virtual environment activates
- [ ] Errors handled gracefully

### Error Handling
- [ ] Ollama not installed → Clear error + instructions
- [ ] Ollama won't start → Fallback message
- [ ] Database missing → Offers to run setup
- [ ] Import file missing → Clear error message
- [ ] Network issues → Timeout handled

### Documentation
- [ ] README updated with new launcher
- [ ] Quick start guide uses auto-launcher
- [ ] Troubleshooting includes Ollama issues
- [ ] Examples use `cardforge.py` syntax

---

## 🚀 Deployment Steps

### For Fresh Installation

```bash
# 1. Clone repository
git clone <repo> mtg-collection-manager
cd mtg-collection-manager

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix

# 3. Run setup wizard (handles everything!)
python setup_wizard.py

# 4. Start using
python cardforge.py stats
```

### For Existing Installation

```bash
# 1. Pull latest changes
git pull

# 2. Add new launcher files
# (already in repo after consolidation)

# 3. Update dependencies
pip install -r requirements.txt

# 4. Update .env with new settings
# (setup_wizard.py can regenerate if needed)

# 5. Test launcher
python cardforge.py stats
```

---

## 🎯 User Experience Goals

### Before Auto-Initialization
```
❌ Complex:
1. Remember to start Ollama
2. Check if database exists
3. Activate virtual environment
4. Remember correct command syntax
5. Debug when step missed

Time: 2-5 minutes (if you remember)
Friction: HIGH
```

### After Auto-Initialization
```
✅ Simple:
1. Run: python cardforge.py <command>

Time: Instant
Friction: ZERO
```

---

## 📊 Testing Matrix

| Scenario | Expected Result | Status |
|----------|----------------|--------|
| First run, Ollama not installed | Error + install instructions | ⬜ |
| First run, Ollama installed | Auto-starts, downloads models | ⬜ |
| Ollama running | Uses existing instance | ⬜ |
| Ollama stopped | Auto-starts gracefully | ⬜ |
| Database missing | Offers to initialize | ⬜ |
| Import command | Works immediately | ⬜ |
| AI command | Works immediately | ⬜ |
| Web command | Starts backend + frontend | ⬜ |
| Ctrl+C shutdown | Cleans up properly | ⬜ |
| Multiple commands | No repeated startups | ⬜ |

---

## 🔄 CI/CD Integration

### GitHub Actions Test

```yaml
# .github/workflows/test-launcher.yml
name: Test Auto-Launcher

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.9', '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Ollama
      run: |
        # Install Ollama for testing
        curl -fsSL https://ollama.com/install.sh | sh
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Test setup wizard
      run: python setup_wizard.py
    
    - name: Test launcher help
      run: python cardforge.py
    
    - name: Test launcher stats
      run: python cardforge.py stats
```

---

## 📝 Commit Message Template

```
feat: Add auto-initialization system for seamless startup

- Add setup_wizard.py for one-time initialization
- Add cardforge.py launcher with auto-Ollama management
- Add start_cardforge.bat for Windows double-click
- Update documentation for new launcher
- Add .env.example with auto-start settings

BREAKING CHANGE: Users should now use `python cardforge.py` 
instead of direct CLI calls. Old method still works but 
requires manual Ollama management.

Benefits:
- Zero-friction startup (Ollama auto-starts)
- Automatic dependency checks
- Graceful error handling
- Unified interface for all commands

Closes #XX (if applicable)
```

---

## 🎓 Training Materials Update

### For Students (Teaching Moment)

**Before:**
```python
# Manual dependency management
import subprocess
import sys

# Student must remember to:
# 1. Start Ollama manually
# 2. Check database
# 3. Handle errors

# Lots of boilerplate
```

**After:**
```python
# Automatic dependency management
from cardforge.core.launcher import ensure_ollama

# Just focus on logic
if ensure_ollama():
    # Do work
    pass

# Launcher handles complexity
```

**Lesson:** "Good software handles complexity so users don't have to"

---

## 🚨 Rollback Plan

If auto-initialization causes issues:

```bash
# Option 1: Disable auto-start
export OLLAMA_AUTO_START=false
python cardforge.py stats

# Option 2: Use direct CLI (bypass launcher)
python -m cardforge.cli stats

# Option 3: Manual Ollama management
ollama serve &
python -m cardforge.cli stats

# Option 4: Revert to previous commit
git revert <commit-hash>
```

---

## ✅ Final Validation

Before considering auto-initialization complete:

- [ ] 3+ developers test on different machines
- [ ] Windows, Mac, Linux all tested
- [ ] Fresh installation works end-to-end
- [ ] Existing installation upgrades smoothly
- [ ] Documentation accurate and complete
- [ ] Error messages helpful and clear
- [ ] No performance degradation
- [ ] Cleanup works properly
- [ ] Student feedback positive
- [ ] Production-ready

---

## 📞 Support Resources

### For Issues

1. Check logs: `logs/cardforge.log`
2. Verify Ollama: `ollama list`
3. Test manually: `ollama serve`
4. Disable auto-start: `.env` → `OLLAMA_AUTO_START=false`
5. Reinstall: `python setup_wizard.py`

### For Questions

- Documentation: `docs/STREAMLINED_QUICKSTART.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- GitHub Issues: `<repo>/issues`
- Discord/Slack: (if applicable)

---

**Integration Status:** ⬜ Not Started | 🔄 In Progress | ✅ Complete  
**Last Updated:** January 12, 2026  
**Next Review:** After first production use
