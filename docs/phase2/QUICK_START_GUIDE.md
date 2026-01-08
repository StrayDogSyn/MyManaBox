# ⚡ CardForge Agent Orchestration - Quick Start Guide

## 🎯 **Get Running in 10 Minutes**

### **Step 1: Start Ollama Server** (1 min)
```bash
# Open PowerShell/Terminal
ollama serve

# Keep this terminal open!
```

### **Step 2: Pull Essential Model** (3-5 min)
```bash
# Open another terminal
ollama pull llama3.2:3b

# This is enough to test! Pull others later.
```

### **Step 3: Install Dependencies** (1 min)
```bash
pip install aiohttp PyQt6 --break-system-packages
```

### **Step 4: Place Files** (1 min)
```
Your CardForge project:
C:\Users\EHunt\Repos\Projects\mtg-collection-manager\
├── src\
│   ├── ai\
│   │   ├── __init__.py                    # Empty file
│   │   ├── orchestration.py               # Main agent system
│   │   └── config.json                    # Configuration
│   └── gui\
│       └── ai_assistant_panel.py          # GUI widget
└── scripts\
    └── setup_agents.py                     # Setup validator
```

### **Step 5: Test It!** (2 min)
```bash
cd C:\Users\EHunt\Repos\Projects\mtg-collection-manager

# Run setup validation
python scripts\setup_agents.py

# If all checks pass, run demo
python src\ai\orchestration.py
```

---

## 🔌 **Integration with CardForge Main Window**

### **Option A: Add as Tab** (Recommended)

In your `CardForge` main window file (probably `main_window.py` or similar):

```python
# At the top, add import
from src.gui.ai_assistant_panel import AIAssistantPanel

class CardForgeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Your existing setup...
        self.setup_ui()
        
        # Add AI Assistant tab
        self.ai_panel = AIAssistantPanel(self)
        
        # Assuming you have a tab widget already:
        self.tab_widget.addTab(self.ai_panel, "🤖 AI Assistant")
        
        # Or if you're creating tabs from scratch:
        # self.tab_widget = QTabWidget()
        # self.tab_widget.addTab(self.collection_panel, "Collection")
        # self.tab_widget.addTab(self.deck_panel, "Decks")
        # self.tab_widget.addTab(self.ai_panel, "🤖 AI Assistant")
```

### **Option B: Add as Dock Widget**

```python
from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtCore import Qt
from src.gui.ai_assistant_panel import AIAssistantPanel

class CardForgeMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Your existing setup...
        
        # Add AI Assistant dock
        self.ai_dock = QDockWidget("AI Assistant", self)
        self.ai_panel = AIAssistantPanel(self)
        self.ai_dock.setWidget(self.ai_panel)
        
        # Add to right side of window
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.ai_dock)
```

---

## 📝 **First Usage Example**

### **Task: Optimize Kaalia Voltron Deck**

1. **Open CardForge** → Navigate to AI Assistant tab
2. **Select task:** "Optimize Deck"
3. **Choose deck:** "Kaalia Voltron" (from dropdown)
4. **Set budget:** $200
5. **Select goal:** "Turn 3 Commander Consistency"
6. **Click:** 🚀 Execute

**What happens:**
- Router routes to DeckOptimizer agent
- Uses qwen2.5-coder:7b (7-10 seconds)
- Analyzes mana curve, ramp sources, synergies
- Returns specific recommendations

**Example Output:**
```
Agent: DeckOptimizer
Model: qwen2.5-coder:7b
Execution Time: 8.4s

MANA CURVE ANALYSIS:
- Current ramp sources: 8 (below optimal)
- Target for Turn 3 Kaalia: 10-12
- Probability of Turn 3 deployment: 54%

RECOMMENDATIONS:
1. Add: Arcane Signet ($2.49) - Priority: HIGH
   Reason: Fast ramp, fixes colors
   
2. Add: Mind Stone ($1.99) - Priority: HIGH
   Reason: Ramp + card draw when needed
   
3. Add: Talisman of Conviction ($3.49) - Priority: MEDIUM
   Reason: T2 ramp, fixes colors

EXPECTED IMPROVEMENT:
- Turn 3 probability: 54% → 78% (+24%)
- Total cost: $7.97 (within budget)
```

---

## 🎮 **Common Tasks Examples**

### **1. Generate Buy List**
```python
# Via Python API
import asyncio
from src.ai.orchestration import generate_buy_list_with_ai

async def create_shopping_list():
    result = await generate_buy_list_with_ai(
        deck_name="Kaalia Voltron",
        missing_cards=[
            "Lightning Greaves",
            "Swiftfoot Boots",
            "Master of Cruelties",
            # ...
        ],
        budget=150.0
    )
    print(result["content"])

asyncio.run(create_shopping_list())
```

### **2. Analyze Collection**
```python
from src.ai.orchestration import analyze_collection_with_ai

async def check_collection():
    result = await analyze_collection_with_ai({
        "total_cards": 1894,
        "unique_cards": 1200,
        "active_decks": 6
    })
    print(result["content"])

asyncio.run(check_collection())
```

### **3. Custom Agent Task**
```python
from src.ai.orchestration import CardForgeOrchestrator, AgentTask

async def custom_analysis():
    async with CardForgeOrchestrator() as orchestrator:
        task = AgentTask(
            task_type="custom_analysis",
            complexity="medium",
            context={
                "question": "What's the best Final Fantasy card for Cloud deck?",
                "budget": 50.0,
                "theme": "Final Fantasy only"
            }
        )
        
        response = await orchestrator.execute_task(task)
        print(response.content)

asyncio.run(custom_analysis())
```

---

## 🔧 **Configuration Quick Reference**

### **Change Default Models**

Edit `src/ai/config.json`:

```json
{
  "models": {
    "deck_optimizer": "qwen2.5-coder:7b",    // Change to "codellama:13b"
    "price_analyzer": "llama3.2:3b",         // Change to "phi3:mini"
    // ...
  }
}
```

### **Adjust Agent Behavior**

```json
{
  "agent_settings": {
    "temperature": 0.7,           // 0.0 = deterministic, 1.0 = creative
    "max_tokens": 2000,           // Longer responses = higher max
    
    "deck_optimization": {
      "turn_3_commander_ramp_target": 12,  // Your proven target
      "budget_threshold": 10.0             // Prefer cards under $10
    }
  }
}
```

---

## 📊 **System Requirements**

### **Minimum (Testing Only)**
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Storage:** 5 GB (for llama3.2:3b)
- **Models:** llama3.2:3b only

### **Recommended (Full Features)**
- **CPU:** 8+ cores
- **RAM:** 16 GB
- **Storage:** 25 GB
- **Models:** Essential 4 models

### **Optimal (70B Model Support)**
- **CPU:** 12+ cores
- **RAM:** 32+ GB (64 GB ideal)
- **Storage:** 50 GB
- **Models:** All 12 models

---

## ⚡ **Performance Tips**

### **Faster Execution:**
```python
# Use fastest models for simple tasks
"router": "llama3.2:1b",          # <1s (instead of 3b)
"price_analyzer": "phi3:mini",    # 1-2s (instead of 3b)
```

### **Better Quality:**
```python
# Use larger models for important decisions
"deck_optimizer": "codellama:13b",   # Slower but better analysis
"meta_analyzer": "llama3.1:70b",     # Best strategic insights
```

### **Balanced (Recommended):**
```python
# Default config strikes good balance
"router": "llama3.2:3b",             # Fast routing
"deck_optimizer": "qwen2.5-coder:7b" // Quality + speed
```

---

## 🐛 **Quick Troubleshooting**

| Problem | Solution |
|---------|----------|
| "Ollama not running" | Open terminal: `ollama serve` |
| "Model not found" | Pull model: `ollama pull llama3.2:3b` |
| "Import error" | Install deps: `pip install aiohttp PyQt6 --break-system-packages` |
| Task too slow | Use faster model (3b instead of 7b) |
| Poor quality | Use larger model (7b instead of 3b) |

---

## 🎓 **Learning Resources**

### **Understanding Agents:**
1. Each agent has a **system prompt** (defines expertise)
2. Tasks are **routed** to the right specialist
3. Models are **selected** based on complexity
4. Results are **formatted** for clarity

### **Example: How Deck Optimization Works**

```
User Request: "Optimize Kaalia deck for Turn 3 consistency"
      ↓
Router Agent: Classifies as "deck_optimization" (complex)
      ↓
Routes to: DeckOptimizer agent
      ↓
Selects Model: qwen2.5-coder:7b (code specialist)
      ↓
Builds Prompt:
  - System: "You are a Commander deck optimization expert..."
  - User: "Analyze Kaalia deck, focus on Turn 3 deployment..."
  - Context: Deck list, budget, current stats
      ↓
Ollama Generates: Detailed analysis with recommendations
      ↓
Returns: Structured result with mana curve, upgrades, rationale
```

---

## 🚀 **Next Steps After Integration**

1. **Test with Kaalia deck** - Optimize your most complete deck first
2. **Generate buy list** - Export prioritized shopping list
3. **Analyze collection** - Find duplicates and gaps
4. **Pull more models** - Add specialized models as needed
5. **Customize prompts** - Tune agent expertise for your needs

---

## 💡 **Pro Tips**

### **Model Selection Rule of Thumb:**
- **3B models** = Fast enough for user interaction (2-5s)
- **7B models** = Best balance of speed/quality (5-10s)
- **13B+ models** = Deep analysis (10-30s)
- **70B model** = Strategic decisions only (30-60s)

### **Task Complexity Mapping:**
- **Simple** → 1B-3B models
- **Medium** → 3B-7B models
- **Complex** → 7B-13B models
- **Strategic** → 70B model

### **Development Workflow:**
1. Start with 3B for iteration/debugging
2. Test with 7B for production quality
3. Use 70B for final validation

---

## ✅ **Verification Checklist**

Before going live:
- [ ] Ollama serve running
- [ ] At least llama3.2:3b installed
- [ ] Dependencies installed (aiohttp, PyQt6)
- [ ] Setup script passes all checks
- [ ] Demo runs successfully
- [ ] GUI panel displays correctly
- [ ] Test task completes without errors

---

**You're ready to use AI-powered CardForge! 🎉**

**Remember:** This system is:
- 🆓 **100% Free** (no API costs)
- 🏠 **Local** (works offline)
- 🎓 **Educational** (teach concepts)
- 🔧 **Customizable** (modify for your needs)
- 💪 **Powerful** (12 specialized models)

**Start with simple tasks, build confidence, then tackle complex optimizations!**
