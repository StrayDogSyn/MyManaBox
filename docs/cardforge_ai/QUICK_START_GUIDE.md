# CardForge AI - Quick Start Guide

**⏱️ Time to working system: ~10 minutes**

## Step 1: Start Ollama (2 minutes)

```bash
# Windows: Download and install from ollama.ai
# Then:
ollama serve

# macOS:
open -a Ollama

# Linux:
ollama serve
```

Keep this terminal running in the background.

## Step 2: Pull Required Models (3-5 minutes)

In a new terminal:

```bash
# Core models needed
ollama pull llama3.2:3b      # Router (2 min)
ollama pull qwen2.5-coder:7b # Deck optimizer, buy list (3 min)
ollama pull gemma2:4b        # Collection manager (2 min)
```

**Optional (for premium analysis):**

```bash
ollama pull llama3.1:70b     # Meta analysis (15+ min, 40GB)
```

Verify installation:

```bash
ollama list
```

## Step 3: Validate Setup (2 minutes)

```bash
# From MyManaBox project root
cd c:\Users\EHunt\Repos\Projects\MyManaBox

# Run validation
python cardforge/scripts/setup_agents.py
```

Expected output:

```text
✓ Ollama running at http://localhost:11434
✓ llama3.2:3b (required)
✓ qwen2.5-coder:7b (required)
✓ gemma2:4b (required)
✓ aiohttp>=3.8.0
✓ PyQt6>=6.0.0
✓ System ready for use!
```

## Step 4: Test It (1-2 minutes)

### Option A: Quick Test (Command Line)

```bash
python cardforge/ai/orchestration.py
```

You'll see output like:

```text
CardForge AI Orchestration System - Demo
============================================================

Task: Optimize my Kaalia of the Vast deck for Turn 3 consistency...
Agent: DeckOptimizer
Task Type: deck_optimization
Model: qwen2.5-coder:7b
Execution Time: 8.23s

Result:
[AI-generated deck optimization advice...]
```

### Option B: GUI Demo

```bash
python cardforge/qt_gui/ai_assistant_panel.py
```

A window will open with:
- Task type selector
- Custom task input
- Dynamic parameter form
- Results display
- Copy/export buttons

## Step 5: Integration into CardForge (5 minutes)

### Find Your Main Window File

In `cardforge/qt_gui/main_window.py` or your main PyQt6 file, add:

```python
# At top of file
from cardforge.qt_gui.ai_assistant_panel import AIAssistantPanel

# In main window __init__
class CardForgeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... existing setup ...
        
        # Add AI Assistant tab
        self.ai_panel = AIAssistantPanel(self)
        self.tab_widget.addTab(self.ai_panel, "🤖 AI Assistant")
```

That's it! The AI Assistant panel is now integrated.

## Common Tasks

### Optimize a Deck

1. Open CardForge
2. Click "AI Assistant" tab
3. Select "Deck Optimization"
4. Paste deck list (one card per line)
5. Click "Execute Task"
6. Wait 8-10 seconds for analysis

**Example deck list:**
```
1x Kaalia of the Vast
1x Command Tower
1x Sol Ring
1x Rampant Growth
1x Cultivate
... (continue with your deck)
```

### Generate a Buy List

1. Select "Buy List Generation"
2. Enter missing cards (comma-separated)
3. Set budget (e.g., $500)
4. Execute
5. Get prioritized shopping list in seconds

**Example:**
```
Cards: Craterhoof Behemoth, Doubling Season, Cyclonic Rift
Budget: $300
```

### Analyze Collection

1. Select "Collection Management"
2. Describe what you want (e.g., "Find duplicates for trade")
3. Execute
4. Get analysis and recommendations

### Find Synergies

1. Select "Synergy Finding"
2. Enter card names you want to combine
3. Execute
4. See how they work together

## Performance Reference

| Task | Time | Models Used |
|------|------|-------------|
| Deck optimization | 8-10s | Router → DeckOptimizer |
| Price analysis | 3-5s | Router → PriceAnalyzer |
| Collection analysis | 5-8s | Router → CollectionManager |
| Buy list (20 cards) | 10-12s | Router → BuyListGenerator |
| Meta analysis | 40-60s | Router → MetaAnalyzer |
| Synergy finding | 8-12s | Router → SynergyFinder |

**Includes ~2 seconds for task routing.**

## Model Customization

### Use Different Model for Faster/Better Results

Edit `cardforge/ai/config.json`:

```json
{
  "agents": {
    "deck_optimizer": {
      "model": "llama3.1:70b",  // More powerful analysis
      "temperature": 0.5,
      "max_tokens": 2000
    }
  }
}
```

Available models (after pulling):
- Ultra-fast: `llama3.2:1b`, `tinyllama:2.1b`
- Fast: `llama3.2:3b`, `phi3:3.8b`
- Balanced: `gemma2:4b`, `qwen2.5-coder:7b`
- Powerful: `granite-code:8b`, `codellama:13b`
- Top-tier: `llama3.1:70b`

### Adjust Temperature

Lower = more deterministic (0.1-0.3 for routing)  
Higher = more creative (0.6-0.8 for analysis)

## Troubleshooting

### "Ollama not responding"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If error, restart:
# Windows: Stop and restart Ollama.exe
# macOS: Quit and reopen Ollama app
# Linux: systemctl restart ollama
```

### "Model not found: qwen2.5-coder:7b"

```bash
# Pull missing model
ollama pull qwen2.5-coder:7b

# Verify
ollama list
```

### "Memory error" or "GPU out of memory"

1. Reduce `max_tokens` in config.json (lower values = less memory)
2. Use smaller models (e.g., `llama3.2:3b` instead of `70b`)
3. Close other GPU-heavy applications
4. Check available VRAM: `nvidia-smi`

### "Task takes 30+ seconds"

Likely using 70B model. For faster responses:

- Use `qwen2.5-coder:7b` for code tasks
- Use `llama3.2:3b` for quick analysis
- Only use `llama3.1:70b` for complex reasoning

### GUI shows "Orchestration not initialized"

1. Ensure Ollama is running: `ollama serve`
2. Run health check: `python cardforge/scripts/setup_agents.py --health-check`
3. Check models are installed: `ollama list`

## Next Steps

1. ✅ Optimize your Kaalia deck
2. ✅ Generate a buy list for missing cards
3. ✅ Analyze your collection
4. ✅ Find hidden synergies in your decks
5. 🎯 Customize agents for your MTG format

## Questions?

See `CARDFORGE_AGENT_README.md` for full documentation including:
- Architecture details
- Agent-by-agent explanations
- Advanced configuration
- Integration examples
- Educational use cases

---

**Welcome to CardForge AI! 🎉**

Your collection management just got a whole lot smarter.
