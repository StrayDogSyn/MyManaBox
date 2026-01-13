# CardForge Streamlined Quick Start
**Zero-friction initialization - everything auto-starts**

---

## 🚀 One-Time Setup (5 minutes)

### Step 1: Install Ollama (if not already installed)

**Windows:**
1. Download: https://ollama.com/download
2. Run installer
3. Done! (Auto-starts as Windows service)

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Clone & Setup CardForge

```bash
# Clone repository
cd C:\Users\EHunt\Repos\Projects
git clone <your-repo> mtg-collection-manager
cd mtg-collection-manager

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run one-time setup wizard
python setup_wizard.py
```

**That's it!** The setup wizard automatically:
- ✅ Checks Python version
- ✅ Installs dependencies
- ✅ Starts Ollama if not running
- ✅ Downloads required AI models (llama3:8b)
- ✅ Initializes database
- ✅ Creates directories
- ✅ Generates config file

---

## 💡 Usage (Zero Manual Steps)

### Option A: Use the Auto-Launcher (Recommended)

The `cardforge.py` launcher handles ALL initialization automatically:

```bash
# Import collection (Ollama auto-starts!)
python cardforge.py import data/my_collection.csv

# View stats (no manual Ollama startup needed!)
python cardforge.py stats

# Search cards
python cardforge.py search "Lightning Bolt"

# Ask AI (automatically ensures Ollama is running!)
python cardforge.py ai "What cards synergize with Kaalia?"

# Start web interface (backend + frontend auto-start)
python cardforge.py web

# Start desktop GUI
python cardforge.py gui
```

**How it works:**
1. You run a command
2. Launcher checks if Ollama is running
3. If not, launcher starts Ollama automatically
4. If database missing, offers to run setup
5. Your command executes seamlessly

### Option B: Windows Batch File (Double-Click)

```bash
# Just double-click this file:
start_cardforge.bat
```

Interactive menu appears:
```
What would you like to do?

1. Import collection
2. View statistics  
3. Search cards
4. Ask AI agent
5. Start web interface
6. Start desktop GUI
7. Exit

Enter choice (1-7):
```

### Option C: Traditional (Manual Ollama)

If you prefer manual control:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Use CardForge
python -m cardforge.cli stats
```

---

## 📦 Import Your Collection

### Quick Import (Automated)

```bash
# Using launcher (auto-starts everything)
python cardforge.py import data/1st_Batch_Complete.csv

# Or use test script directly
python scripts/test_import.py --execute
```

### What Happens:
1. ✅ Ollama auto-starts if needed
2. ✅ Database initialized if missing
3. ✅ CSV parsed and validated
4. ✅ Cards imported with deduplication
5. ✅ Automatic backup created
6. ✅ Summary displayed

**Expected output:**
```
🚀 Starting Ollama...
✅ Ollama started

📦 Importing 1st_Batch_Complete.csv...

✅ Import completed successfully!

Statistics:
  Rows processed: 1,221
  Cards added: 1,183
  Cards updated: 38
  Errors: 0

Backup: data/backups/cardforge_20260112_143022.db
```

---

## 🤖 Test AI Features

### Simple AI Query

```bash
# Launcher handles Ollama automatically
python cardforge.py ai "What are the best ramp cards under $5?"
```

### Deck Optimization

```bash
# Create a Python script: test_deck_optimizer.py
from cardforge.services.ai.agents import DeckOptimizerAgent
from cardforge.ai.clients.ollama_client import OllamaClient
import asyncio

async def test():
    client = OllamaClient()
    agent = DeckOptimizerAgent(client)
    
    suggestions = await agent.optimize_deck(
        deck_id=1,
        collection_id=1
    )
    
    for s in suggestions:
        print(f"{s.action}: {s.card_name} - {s.reason}")

asyncio.run(test())
```

Run it:
```bash
python cardforge.py run test_deck_optimizer.py
```

---

## 🌐 Web Interface

### Start Web App (One Command)

```bash
# Launcher starts BOTH backend and frontend
python cardforge.py web
```

**What it does:**
1. Starts FastAPI backend on port 8000
2. Starts Vite dev server on port 5173
3. Opens browser to http://localhost:5173
4. Both stop together with Ctrl+C

### Manual (If Needed)

```bash
# Terminal 1: Backend
uvicorn cardforge.api.main:app --reload

# Terminal 2: Frontend  
cd web && npm run dev
```

---

## 🖥️ Desktop GUI

### Start GUI (One Command)

```bash
# Launcher handles everything
python cardforge.py gui
```

Or directly:
```bash
python -m gui.main
```

---

## 🔧 Troubleshooting

### Ollama Not Starting?

The launcher will warn you, but you can check manually:

```bash
# Check if Ollama is installed
ollama --version

# Check if running
curl http://localhost:11434/api/tags

# Start manually if needed
ollama serve
```

### Database Issues?

```bash
# Reinitialize database
python cardforge.py setup

# Or manually
python scripts/init_database.py
```

### Import Fails?

```bash
# Check CSV format
python -c "
import pandas as pd
df = pd.read_csv('data/my_collection.csv')
print(df.columns.tolist())
print(df.head())
"

# Test with smaller sample
head -100 data/my_collection.csv > data/test.csv
python cardforge.py import data/test.csv
```

### AI Not Responding?

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check models installed
ollama list

# Download model if missing
ollama pull llama3:8b
```

---

## 📊 Daily Workflow

### Morning Routine (5 minutes)

```bash
# 1. Update prices (automated)
python scripts/automation/daily_price_update.py

# 2. Check collection stats
python cardforge.py stats

# 3. Review deck optimization
python cardforge.py ai "Suggest budget upgrades for my Kaalia deck"
```

### After Game Night (10 minutes)

```bash
# 1. Add new cards from draft
python cardforge.py import data/new_cards.csv

# 2. Update deck with new cards
# (via web interface or GUI)

# 3. Run backup
python scripts/automation/daily_backup.py
```

### Weekly Maintenance (15 minutes)

```bash
# 1. Sync with Moxfield
python scripts/automation/sync_collections.py

# 2. Generate buylist for trade binder
python cardforge.py ai "Generate buylist for cards over $10 I don't use"

# 3. Review price spikes
python cardforge.py stats --price-spikes
```

---

## 🎓 Teaching with CardForge

### Show Students the Difference

**Before (Legacy MyManaBox):**
```python
# Manual Ollama startup required
# No auto-initialization
# Lots of manual steps
```

**After (Modern CardForge):**
```python
# Just run the command
python cardforge.py ai "Help me build a Commander deck"

# Everything auto-starts:
# - Ollama (if not running)
# - Database (if not initialized)
# - AI agents (connected to real data)
```

### Demo Flow

1. Show `start_cardforge.bat` - double-click simplicity
2. Explain auto-initialization in `cardforge.py`
3. Walk through Ollama manager code
4. Show how launchers improve UX
5. Demonstrate seamless AI integration

---

## 🚨 Common Mistakes (Now Fixed!)

### ❌ OLD WAY:
```bash
# Forgot to start Ollama
python -m cardforge.cli ai "query"
# ERROR: Connection refused

# Start Ollama manually
ollama serve

# Try again...
python -m cardforge.cli ai "query"
# Finally works!
```

### ✅ NEW WAY:
```bash
# Just run the command
python cardforge.py ai "query"

# Output:
# 🚀 Starting Ollama...
# ✅ Ollama started
# 🤖 AI Agent: query
# [Response here]
```

---

## 📈 Next Steps

After getting comfortable with the launcher:

### Week 1: Import & Explore
- Import your collection
- Browse with web interface
- Test AI agents
- Run statistics

### Week 2: Optimization
- Optimize your decks
- Identify budget upgrades
- Track price changes
- Generate buy/sell lists

### Week 3: Automation
- Set up daily price updates
- Configure automatic backups
- Schedule collection syncing
- Enable email notifications (future)

### Week 4: Advanced Features
- Custom AI agents
- Advanced analytics
- Trading optimization
- Meta analysis

---

## 💡 Pro Tips

1. **Alias the launcher** for even faster access:
   ```bash
   # Add to .bashrc or .zshrc
   alias cf='python /path/to/cardforge.py'
   
   # Usage
   cf stats
   cf ai "query"
   ```

2. **Pin the batch file** to taskbar (Windows)
   - Right-click `start_cardforge.bat`
   - Send to > Desktop
   - Drag to taskbar

3. **Use tab completion** (if implemented)
   ```bash
   cf im<TAB>  # Expands to 'cf import'
   cf st<TAB>  # Expands to 'cf stats'
   ```

4. **Chain commands** with scripts:
   ```bash
   # morning_routine.bat
   python cardforge.py stats
   python cardforge.py ai "Any price spikes yesterday?"
   ```

---

## 📝 Summary

**Old CardForge initialization:**
1. Remember to start Ollama ❌
2. Check database exists ❌
3. Activate virtual environment ❌
4. Run command ❌
5. Debug when forgot step ❌

**New CardForge initialization:**
1. Run command ✅

**That's it!** 🎉

The launcher handles everything:
- ✅ Ollama auto-start
- ✅ Database check
- ✅ Environment validation
- ✅ Error handling
- ✅ Graceful cleanup

---

**Created:** January 12, 2026  
**Status:** Production-ready auto-initialization  
**Next:** Just run `python cardforge.py setup` and start using!
