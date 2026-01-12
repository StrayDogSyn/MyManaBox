# CardForge Development Roadmap
## TRAE Solo Autonomous Overnight Development Plan
### Version 1.0 | January 2025

---

## 🎯 PROJECT OVERVIEW & DIRECTION

CardForge is evolving from MyManaBox into a **professional-grade MTG collection management platform** with three major new capabilities:

1. **Ollama LLM Integration** - Local AI workspace for deck optimization and collection analysis
2. **Web-Deployable Interface** - Moxfield-inspired UI deployable via GitHub Pages/Vercel
3. **Multi-Agent Architecture** - Specialized AI agents for different MTG tasks

**Think of it like upgrading from a home kitchen to a professional restaurant:** 
- The existing MyManaBox backend is your prep station (functional, organized)
- Ollama agents are your sous chefs (specialized, always ready)
- The web workspace is your front-of-house (beautiful, accessible)

---

## 📊 SECTION 1: PROJECT AUDIT SUMMARY

### Current State Assessment

**Strengths:**
- ✅ Well-architected separation of concerns (models, services, data, presentation)
- ✅ Comprehensive data models (Card, Collection, enums)
- ✅ Scryfall API integration with caching
- ✅ CSV import/export working for ManaBox, Moxfield
- ✅ Collection statistics and analytics
- ✅ Search and filtering functional
- ✅ 1,894+ cards already cataloged (1,221 batch 1 + 673 batch 2)

**Weaknesses:**
- ⚠️ Test coverage at ~5% (target: 80%+)
- ⚠️ No web interface (desktop PyQt6 only)
- ⚠️ No LLM integration yet
- ⚠️ Config files scattered (needs consolidation)
- ⚠️ Missing CI/CD pipeline

**Tech Debt:**
- Multiple entry points need consolidation (main.py, dev.py)
- Legacy code in `legacy/` directory needs cleanup or removal
- Documentation spread across multiple markdown files

**Quick Wins:**
1. Add `.env` template and configuration loader (30 min)
2. Create unified project entry point (20 min)
3. Add basic pytest structure (45 min)
4. Create Docker development setup (60 min)

### Collection Data Analysis

From your CSV files:
```
Batch 1: 1,221 unique entries
Batch 2: 673 unique entries (FIC - Final Fantasy Commander)
Total: ~1,894 cataloged cards

Rarity Distribution (estimated from batch 1):
- Common: ~600
- Uncommon: ~400
- Rare: ~150
- Mythic: ~71

Sets represented: AFR, BRO, FIN, FIC, FCA, and 50+ others
```

---

## 🌙 SECTION 2: OVERNIGHT AUTONOMOUS TASK PLAN

### Phase 1: Foundation & Environment (Tasks 1-5)
**Duration:** ~2 hours | **Dependency:** None

#### Task 1.1: Project Structure Cleanup
**Goal:** Consolidate scattered config files and create clean project root
**Files:** 
- `cardforge/config/settings.py` (create)
- `cardforge/config/default_settings.json` (create)
- `.env.template` (create)
- `pyproject.toml` (update)

**Implementation:**
```python
# cardforge/config/settings.py
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:3b"
    complex_model: str = "llama3.1:70b"
    timeout: int = 120
    
@dataclass
class DatabaseConfig:
    path: str = "data/cardforge.db"
    backup_dir: str = "data/backups"
    
@dataclass
class ApiConfig:
    scryfall_rate_limit: float = 0.1  # 10 req/sec
    cache_duration_hours: int = 24
    
@dataclass 
class Settings:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    debug: bool = False
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from JSON file and environment variables."""
        # Implementation here
        pass

settings = Settings.load()
```

**Acceptance Criteria:**
- [ ] All config in single location
- [ ] Environment variables override defaults
- [ ] `python -c "from cardforge.config import settings; print(settings)"` works

#### Task 1.2: Unified Entry Point
**Goal:** Single `cardforge` CLI command for all operations
**Files:**
- `cardforge/__main__.py` (create)
- `cardforge/cli.py` (create)

**Implementation:**
```python
# cardforge/__main__.py
"""CardForge - MTG Collection Manager CLI"""
import click
from cardforge.cli import cli

if __name__ == "__main__":
    cli()
```

```python
# cardforge/cli.py
import click

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """CardForge - Professional MTG Collection Management"""
    pass

@cli.group()
def collection():
    """Collection management commands"""
    pass

@cli.group()
def deck():
    """Deck building commands"""
    pass

@cli.group()
def agent():
    """AI agent commands"""
    pass

@cli.group()
def server():
    """Web/API server commands"""
    pass
```

**Acceptance Criteria:**
- [ ] `python -m cardforge --help` shows all command groups
- [ ] `python -m cardforge collection stats` works
- [ ] `python -m cardforge agent list` shows available agents

#### Task 1.3: Test Infrastructure Setup
**Goal:** Pytest configuration with fixtures
**Files:**
- `tests/conftest.py` (create)
- `tests/test_models/test_card.py` (create)
- `pytest.ini` (create)

**Implementation:**
```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from cardforge.database import init_database

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    init_database(db_path)
    yield db_path
    db_path.unlink()

@pytest.fixture
def sample_card_data():
    """Sample card data for testing."""
    return {
        "name": "Lightning Bolt",
        "scryfall_id": "e3285e6b-3e79-4d7c-bf96-d920f973b122",
        "set_code": "LEA",
        "mana_cost": "{R}",
        "cmc": 1,
        "type_line": "Instant",
        "oracle_text": "Lightning Bolt deals 3 damage to any target.",
        "rarity": "common"
    }
```

**Acceptance Criteria:**
- [ ] `pytest` runs without errors
- [ ] `pytest --cov=cardforge` shows coverage report
- [ ] At least 3 passing tests

#### Task 1.4: Docker Development Environment
**Goal:** Containerized development with Ollama
**Files:**
- `Dockerfile` (create)
- `docker-compose.yml` (create)
- `docker-compose.dev.yml` (create)

**Implementation:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  cardforge:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5173:5173"  # Vite dev server
      - "8000:8000"  # API server
    volumes:
      - ./cardforge:/app/cardforge
      - ./data:/app/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  ollama_data:
```

**Acceptance Criteria:**
- [ ] `docker-compose up` starts both services
- [ ] Ollama responds at `localhost:11434/api/tags`
- [ ] CardForge can connect to Ollama

#### Task 1.5: Checkpoint - Foundation Verification
**Goal:** Verify all Phase 1 tasks completed successfully
**Files:**
- `scripts/verify_foundation.py` (create)

**Implementation:**
```python
#!/usr/bin/env python3
"""Verify Phase 1 foundation is complete."""

def check_config():
    from cardforge.config import settings
    assert settings.ollama.base_url
    print("✅ Config loading works")

def check_cli():
    import subprocess
    result = subprocess.run(
        ["python", "-m", "cardforge", "--help"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    print("✅ CLI entry point works")

def check_tests():
    import subprocess
    result = subprocess.run(
        ["pytest", "-q", "--collect-only"],
        capture_output=True, text=True
    )
    assert "test" in result.stdout.lower()
    print("✅ Test infrastructure works")

if __name__ == "__main__":
    check_config()
    check_cli()
    check_tests()
    print("\n🎉 Phase 1 Foundation Complete!")
```

---

### Phase 2: Ollama Integration Core (Tasks 6-10)
**Duration:** ~3 hours | **Dependency:** Phase 1

#### Task 2.1: Ollama Client Service
**Goal:** Async client for Ollama API with model selection
**Files:**
- `cardforge/services/ollama_client.py` (create)
- `tests/test_services/test_ollama_client.py` (create)

**Implementation:**
```python
# cardforge/services/ollama_client.py
"""Async Ollama client with intelligent model routing."""

import asyncio
import aiohttp
from typing import AsyncGenerator, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

class TaskComplexity(Enum):
    SIMPLE = "simple"      # Quick lookups, simple questions
    MODERATE = "moderate"  # Analysis, comparisons
    COMPLEX = "complex"    # Deep strategy, multi-step reasoning

@dataclass
class ModelConfig:
    name: str
    context_length: int
    complexity: TaskComplexity
    
MODEL_ROUTING = {
    TaskComplexity.SIMPLE: ModelConfig("llama3.2:3b", 8192, TaskComplexity.SIMPLE),
    TaskComplexity.MODERATE: ModelConfig("llama3.1:8b", 32768, TaskComplexity.MODERATE),
    TaskComplexity.COMPLEX: ModelConfig("llama3.1:70b", 131072, TaskComplexity.COMPLEX),
}

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
            
    def select_model(self, complexity: TaskComplexity) -> str:
        """Select appropriate model based on task complexity."""
        return MODEL_ROUTING[complexity].name
        
    async def generate(
        self,
        prompt: str,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        system: Optional[str] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None]:
        """Generate completion with automatic model selection."""
        model = self.select_model(complexity)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }
        if system:
            payload["system"] = system
            
        async with self.session.post(
            f"{self.base_url}/api/generate",
            json=payload
        ) as response:
            if stream:
                async for line in response.content:
                    if line:
                        yield line.decode()
            else:
                data = await response.json()
                yield data.get("response", "")
                
    async def list_models(self) -> list[str]:
        """List available models."""
        async with self.session.get(f"{self.base_url}/api/tags") as response:
            data = await response.json()
            return [m["name"] for m in data.get("models", [])]
```

**Acceptance Criteria:**
- [ ] `OllamaClient.list_models()` returns available models
- [ ] Model routing selects appropriate model for complexity
- [ ] Streaming generation works

#### Task 2.2: Agent Base Class
**Goal:** Standardized agent interface for all AI agents
**Files:**
- `cardforge/agents/base_agent.py` (create)
- `cardforge/agents/__init__.py` (create)

**Implementation:**
```python
# cardforge/agents/base_agent.py
"""Base agent class for CardForge AI agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class AgentCapability(Enum):
    DECK_ANALYSIS = "deck_analysis"
    PRICE_CHECK = "price_check"
    META_ANALYSIS = "meta_analysis"
    SYNERGY_FINDER = "synergy_finder"
    BUY_LIST = "buy_list"
    COLLECTION_STATS = "collection_stats"
    RULES_EXPERT = "rules_expert"

@dataclass
class AgentConfig:
    """Configuration for an AI agent."""
    name: str
    description: str
    capabilities: List[AgentCapability]
    model_preference: str  # Ollama model name
    system_prompt: str
    temperature: float = 0.7
    max_tokens: int = 2048
    tools: List[str] = field(default_factory=list)
    
class BaseAgent(ABC):
    """Abstract base class for CardForge agents."""
    
    def __init__(self, config: AgentConfig, ollama_client):
        self.config = config
        self.client = ollama_client
        self.conversation_history: List[Dict[str, str]] = []
        
    @property
    def name(self) -> str:
        return self.config.name
        
    @property
    def capabilities(self) -> List[AgentCapability]:
        return self.config.capabilities
        
    @abstractmethod
    async def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a query and return response."""
        pass
        
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})
        
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent config for registry."""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "capabilities": [c.value for c in self.config.capabilities],
            "model": self.config.model_preference,
            "tools": self.config.tools
        }
```

**Acceptance Criteria:**
- [ ] `BaseAgent` can be subclassed
- [ ] Agent serialization to JSON works
- [ ] Conversation history tracking works

#### Task 2.3: Deck Optimizer Agent
**Goal:** Specialized agent for deck analysis and optimization
**Files:**
- `cardforge/agents/deck_optimizer.py` (create)

**Implementation:**
```python
# cardforge/agents/deck_optimizer.py
"""Deck optimization agent using local Ollama models."""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentConfig, AgentCapability

DECK_OPTIMIZER_SYSTEM = """You are an expert Magic: The Gathering deck optimizer. 
You specialize in Commander/EDH format.

Your knowledge includes:
- Optimal mana curves and land counts for different strategies
- Card synergies and combo interactions  
- Meta analysis and competitive positioning
- Budget alternatives for expensive cards

When analyzing decks, consider:
1. Mana base (land count, color distribution, ramp sources)
2. Protection suite (hexproof, indestructible, counterspells)
3. Win conditions (combo lines, value engines, aggro paths)
4. Card draw and selection
5. Removal and interaction

Format your responses with clear sections and specific card recommendations.
Always cite your reasoning (e.g., "EDHrec shows 85% inclusion rate").
"""

class DeckOptimizerAgent(BaseAgent):
    """Agent specialized in deck analysis and optimization."""
    
    def __init__(self, ollama_client):
        config = AgentConfig(
            name="Deck Optimizer",
            description="Analyzes decks and suggests improvements based on strategy and budget",
            capabilities=[
                AgentCapability.DECK_ANALYSIS,
                AgentCapability.SYNERGY_FINDER,
                AgentCapability.META_ANALYSIS
            ],
            model_preference="llama3.1:8b",
            system_prompt=DECK_OPTIMIZER_SYSTEM,
            temperature=0.6,
            tools=["search_collection", "get_deck_analysis", "suggest_upgrades"]
        )
        super().__init__(config, ollama_client)
        
    async def process(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process deck optimization query."""
        # Build prompt with context
        prompt_parts = [query]
        
        if context:
            if "deck_list" in context:
                prompt_parts.insert(0, f"Deck List:\n{context['deck_list']}\n")
            if "collection" in context:
                prompt_parts.insert(0, f"Cards Owned:\n{context['collection']}\n")
            if "budget" in context:
                prompt_parts.append(f"\nBudget constraint: ${context['budget']}")
                
        full_prompt = "\n".join(prompt_parts)
        self.add_to_history("user", query)
        
        response = ""
        async for chunk in self.client.generate(
            prompt=full_prompt,
            system=self.config.system_prompt,
            complexity=TaskComplexity.MODERATE
        ):
            response += chunk
            
        self.add_to_history("assistant", response)
        return response
        
    async def analyze_deck(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive deck analysis."""
        analysis_prompt = f"""
        Analyze this Commander deck:
        
        Commander: {deck_data.get('commander', 'Unknown')}
        Colors: {deck_data.get('colors', [])}
        Card Count: {deck_data.get('card_count', 0)}
        
        Categories:
        - Lands: {deck_data.get('land_count', 0)}
        - Creatures: {deck_data.get('creature_count', 0)}
        - Ramp: {deck_data.get('ramp_count', 0)}
        - Protection: {deck_data.get('protection_count', 0)}
        - Card Draw: {deck_data.get('draw_count', 0)}
        - Removal: {deck_data.get('removal_count', 0)}
        
        Provide:
        1. Overall assessment (1-10 rating)
        2. Strengths
        3. Weaknesses  
        4. Top 5 recommended additions
        5. Top 5 recommended cuts
        """
        
        return await self.process(analysis_prompt, context=deck_data)
```

**Acceptance Criteria:**
- [ ] Agent initializes with correct config
- [ ] `analyze_deck()` returns structured analysis
- [ ] Conversation history maintained

#### Task 2.4: Agent Registry
**Goal:** Central registry for discovering and managing agents
**Files:**
- `cardforge/agents/registry.py` (create)

**Implementation:**
```python
# cardforge/agents/registry.py
"""Agent registry for discovering and managing AI agents."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent, AgentCapability

class AgentRegistry:
    """Registry for CardForge AI agents."""
    
    _instance = None
    _agents: Dict[str, BaseAgent] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def register(self, agent: BaseAgent):
        """Register an agent."""
        self._agents[agent.name] = agent
        
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name."""
        return self._agents.get(name)
        
    def list_agents(self) -> List[Dict]:
        """List all registered agents."""
        return [agent.to_dict() for agent in self._agents.values()]
        
    def find_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Find agents with specific capability."""
        return [
            agent for agent in self._agents.values()
            if capability in agent.capabilities
        ]
        
    def export_registry(self, path: Path):
        """Export registry to JSON file."""
        data = {
            "agents": self.list_agents(),
            "capabilities": [c.value for c in AgentCapability]
        }
        path.write_text(json.dumps(data, indent=2))
        
    @classmethod
    def load_from_config(cls, config_dir: Path) -> "AgentRegistry":
        """Load agents from config directory."""
        registry = cls()
        for config_file in config_dir.glob("*.agent.json"):
            # Load and instantiate agents from JSON configs
            pass
        return registry

# Singleton instance
agent_registry = AgentRegistry()
```

**Acceptance Criteria:**
- [ ] Singleton pattern works correctly
- [ ] Agents can be registered and retrieved
- [ ] Export to JSON works

#### Task 2.5: Checkpoint - Agent System Verification
**Goal:** Verify Phase 2 Ollama integration works
**Files:**
- `scripts/verify_agents.py` (create)

```python
#!/usr/bin/env python3
"""Verify Phase 2 agent system works."""

import asyncio
from cardforge.services.ollama_client import OllamaClient, TaskComplexity
from cardforge.agents.deck_optimizer import DeckOptimizerAgent
from cardforge.agents.registry import agent_registry

async def main():
    # Test Ollama connection
    async with OllamaClient() as client:
        models = await client.list_models()
        print(f"✅ Ollama connected, {len(models)} models available")
        
        # Test agent
        agent = DeckOptimizerAgent(client)
        agent_registry.register(agent)
        
        print(f"✅ Agent registered: {agent.name}")
        print(f"✅ Capabilities: {[c.value for c in agent.capabilities]}")
        
        # Test simple query
        response = await agent.process(
            "What's the optimal land count for a 3-color Commander deck?"
        )
        print(f"✅ Agent responds: {response[:100]}...")
        
    print("\n🎉 Phase 2 Agent System Complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Phase 3: Web Interface Foundation (Tasks 11-15)
**Duration:** ~3 hours | **Dependency:** Phase 2

#### Task 3.1: Vite + React Project Setup
**Goal:** Modern React frontend with TypeScript
**Files:**
- `web/` directory structure (create)
- `web/package.json` (create)
- `web/vite.config.ts` (create)

**Commands:**
```bash
cd cardforge
npm create vite@latest web -- --template react-ts
cd web
npm install
npm install @tanstack/react-query axios lucide-react tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Acceptance Criteria:**
- [ ] `npm run dev` starts dev server
- [ ] TypeScript compiles without errors
- [ ] Tailwind CSS works

#### Task 3.2: Dark Theme Design System
**Goal:** Moxfield-inspired dark theme with MTG aesthetics
**Files:**
- `web/src/styles/theme.css` (create)
- `web/tailwind.config.js` (update)

**Implementation:**
```css
/* web/src/styles/theme.css */
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* MTG Color Identity */
  --white-mana: #F8F6D8;
  --blue-mana: #0E68AB;
  --black-mana: #150B00;
  --red-mana: #D3202A;
  --green-mana: #00733E;
  --colorless: #CBC2BF;
  
  /* Dark Theme */
  --bg-primary: #0D0D0D;
  --bg-secondary: #1A1A1A;
  --bg-tertiary: #262626;
  --bg-card: #1F1F1F;
  --bg-hover: #2A2A2A;
  
  /* Text */
  --text-primary: #F5F5F5;
  --text-secondary: #A0A0A0;
  --text-muted: #666666;
  
  /* Accents */
  --accent-gold: #C9A227;
  --accent-blue: #4A9EFF;
  --accent-success: #22C55E;
  --accent-warning: #F59E0B;
  --accent-error: #EF4444;
  
  /* Rarity colors */
  --rarity-common: #1A1718;
  --rarity-uncommon: #707883;
  --rarity-rare: #A58E4A;
  --rarity-mythic: #BF4427;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', system-ui, sans-serif;
}

.font-display {
  font-family: 'Cinzel', serif;
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}
```

**Acceptance Criteria:**
- [ ] Dark theme applied globally
- [ ] Custom CSS variables available
- [ ] Typography classes work

#### Task 3.3: Core Layout Components
**Goal:** Main app shell with navigation
**Files:**
- `web/src/components/Layout/AppShell.tsx` (create)
- `web/src/components/Layout/Sidebar.tsx` (create)
- `web/src/components/Layout/Header.tsx` (create)

**Implementation:**
```tsx
// web/src/components/Layout/AppShell.tsx
import { ReactNode, useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  return (
    <div className="flex h-screen bg-bg-primary">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

```tsx
// web/src/components/Layout/Sidebar.tsx
import { 
  Library, 
  Layers, 
  TrendingUp, 
  Bot, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { icon: Library, label: 'Collection', path: '/collection' },
  { icon: Layers, label: 'Decks', path: '/decks' },
  { icon: TrendingUp, label: 'Analytics', path: '/analytics' },
  { icon: Bot, label: 'AI Workspace', path: '/ai' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside className={`
      ${collapsed ? 'w-16' : 'w-64'} 
      bg-bg-secondary border-r border-bg-tertiary
      transition-all duration-300 flex flex-col
    `}>
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-bg-tertiary">
        <span className={`font-display text-accent-gold text-xl ${collapsed ? 'hidden' : ''}`}>
          CardForge
        </span>
        {collapsed && <span className="text-accent-gold text-2xl">⚔</span>}
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 mx-2 rounded-lg
              transition-colors duration-200
              ${isActive 
                ? 'bg-accent-gold/10 text-accent-gold' 
                : 'text-text-secondary hover:bg-bg-hover hover:text-text-primary'}
            `}
          >
            <item.icon size={20} />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
      
      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className="h-12 flex items-center justify-center border-t border-bg-tertiary
                   text-text-muted hover:text-text-primary transition-colors"
      >
        {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
      </button>
    </aside>
  );
}
```

**Acceptance Criteria:**
- [ ] App shell renders correctly
- [ ] Sidebar navigation works
- [ ] Responsive collapse works

#### Task 3.4: API Client Setup
**Goal:** React Query + Axios for backend communication
**Files:**
- `web/src/api/client.ts` (create)
- `web/src/api/hooks/useCollection.ts` (create)
- `web/src/api/hooks/useAgents.ts` (create)

**Implementation:**
```typescript
// web/src/api/client.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const OLLAMA_URL = import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ollamaClient = axios.create({
  baseURL: OLLAMA_URL,
});

// Request interceptor for auth (future)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

```typescript
// web/src/api/hooks/useAgents.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { ollamaClient } from '../client';

interface AgentMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatRequest {
  agentId: string;
  message: string;
  context?: Record<string, unknown>;
}

export function useAgentChat() {
  return useMutation({
    mutationFn: async ({ agentId, message, context }: ChatRequest) => {
      const response = await ollamaClient.post('/api/generate', {
        model: 'llama3.1:8b',
        prompt: message,
        stream: false,
        context,
      });
      return response.data;
    },
  });
}

export function useAvailableModels() {
  return useQuery({
    queryKey: ['ollama', 'models'],
    queryFn: async () => {
      const response = await ollamaClient.get('/api/tags');
      return response.data.models;
    },
  });
}
```

**Acceptance Criteria:**
- [ ] API client configured
- [ ] React Query hooks work
- [ ] Ollama connection tested

#### Task 3.5: Checkpoint - Web Foundation Verification
**Goal:** Verify web interface foundation
**Files:**
- `web/src/App.tsx` (update)

```tsx
// web/src/App.tsx - Checkpoint test
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/Layout/AppShell';
import { useAvailableModels } from './api/hooks/useAgents';

const queryClient = new QueryClient();

function OllamaStatus() {
  const { data: models, isLoading, error } = useAvailableModels();
  
  if (isLoading) return <div>Connecting to Ollama...</div>;
  if (error) return <div className="text-accent-error">Ollama offline</div>;
  
  return (
    <div className="p-4 bg-bg-secondary rounded-lg">
      <h2 className="text-accent-gold font-display mb-2">Ollama Status</h2>
      <p className="text-accent-success">✓ Connected</p>
      <p className="text-text-secondary">{models?.length || 0} models available</p>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={
              <div className="space-y-6">
                <h1 className="text-3xl font-display text-accent-gold">
                  CardForge
                </h1>
                <OllamaStatus />
                <p className="text-text-secondary">
                  Phase 3 Web Foundation Complete! 🎉
                </p>
              </div>
            } />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
```

---

### Phase 4: Moxfield-Style UI Components (Tasks 16-20)
**Duration:** ~3 hours | **Dependency:** Phase 3

#### Task 4.1: Card Grid/List View Component
**Goal:** Moxfield-inspired card display with multiple view modes
**Files:**
- `web/src/components/Cards/CardGrid.tsx` (create)
- `web/src/components/Cards/CardListItem.tsx` (create)
- `web/src/components/Cards/CardImage.tsx` (create)

#### Task 4.2: Card Detail Panel
**Goal:** Side panel for card details with price, rulings, and synergies
**Files:**
- `web/src/components/Cards/CardDetailPanel.tsx` (create)

#### Task 4.3: Deck Builder Interface
**Goal:** Drag-and-drop deck building with category grouping
**Files:**
- `web/src/components/Decks/DeckBuilder.tsx` (create)
- `web/src/components/Decks/DeckStats.tsx` (create)
- `web/src/components/Decks/ManaCurve.tsx` (create)

#### Task 4.4: Search and Filter Bar
**Goal:** Advanced search with autocomplete and filters
**Files:**
- `web/src/components/Search/SearchBar.tsx` (create)
- `web/src/components/Search/FilterPanel.tsx` (create)

#### Task 4.5: Checkpoint - UI Components Verification
**Goal:** All UI components render correctly

---

### Phase 5: AI Workspace Integration (Tasks 21-25)
**Duration:** ~3 hours | **Dependency:** Phase 4

#### Task 5.1: Chat Interface Component
**Goal:** Chat UI for AI agent interaction
**Files:**
- `web/src/components/AI/ChatInterface.tsx` (create)
- `web/src/components/AI/ChatMessage.tsx` (create)
- `web/src/components/AI/AgentSelector.tsx` (create)

#### Task 5.2: Streaming Response Handler
**Goal:** Handle streaming responses from Ollama
**Files:**
- `web/src/api/streaming.ts` (create)
- `web/src/hooks/useStreamingChat.ts` (create)

#### Task 5.3: Context Injection System
**Goal:** Pass deck/collection context to AI agents
**Files:**
- `web/src/components/AI/ContextPanel.tsx` (create)

#### Task 5.4: Strategy Session View
**Goal:** Combined deck view + AI workspace
**Files:**
- `web/src/pages/StrategySession.tsx` (create)

#### Task 5.5: Checkpoint - AI Workspace Verification
**Goal:** Full AI interaction flow works

---

### Phase 6: Deployment Setup (Tasks 26-30)
**Duration:** ~2 hours | **Dependency:** Phase 5

#### Task 6.1: GitHub Actions CI/CD
**Goal:** Automated testing and deployment
**Files:**
- `.github/workflows/ci.yml` (create)
- `.github/workflows/deploy.yml` (create)

#### Task 6.2: Vercel Configuration
**Goal:** Vercel deployment config
**Files:**
- `vercel.json` (create)
- `web/vercel.json` (create)

#### Task 6.3: Environment Configuration
**Goal:** Production vs development env handling
**Files:**
- `web/.env.example` (create)
- `web/src/config/env.ts` (create)

#### Task 6.4: Static Export for GitHub Pages
**Goal:** Alternative static deployment
**Files:**
- `web/vite.config.ts` (update for static)

#### Task 6.5: Final Checkpoint
**Goal:** Full deployment verification

---

## 🔌 SECTION 3: OLLAMA INTEGRATION PLAN

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CardForge Web Interface                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Collection │  │    Decks    │  │ AI Workspace│             │
│  │    View     │  │   Builder   │  │    Chat     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                       │
│  /api/collection  /api/decks  /api/agents  /api/ollama-proxy   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    SQLite DB    │  │  Agent Registry │  │  Ollama Server  │
│   (cardforge)   │  │   (JSON/Py)     │  │  localhost:11434│
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Model Selection Strategy

| Task Type | Model | Context | Use Case |
|-----------|-------|---------|----------|
| Quick lookup | llama3.2:3b | 8K | Card search, simple stats |
| Analysis | llama3.1:8b | 32K | Deck analysis, comparisons |
| Deep strategy | llama3.1:70b | 128K | Complex optimization, meta analysis |

### API Endpoints

```python
# cardforge/api/routes/ollama.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

@router.post("/generate")
async def generate(request: GenerateRequest):
    """Proxy to Ollama with agent context injection."""
    pass

@router.post("/chat/{agent_id}")
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """Chat with specific agent."""
    pass

@router.get("/models")
async def list_models():
    """List available Ollama models."""
    pass
```

### Deployment Modes

**Local Development:**
- Ollama runs on localhost:11434
- Direct connection from frontend

**Vercel Deployment:**
- Frontend static on Vercel
- Backend API serverless functions OR
- Separate API server (Railway/Render)
- Ollama accessible via tunnel (ngrok/cloudflared)

**GitHub Pages (Static Only):**
- No backend, localStorage for data
- Ollama connection requires user's local instance
- Configuration UI for Ollama URL

---

## 🎨 SECTION 4: MOXFIELD-STYLE UX/UI PLAN

### Design Principles

1. **Dark-first, MTG-themed** - Deep blacks, gold accents, mana color highlights
2. **Information density** - Show more data without clutter (like Moxfield)
3. **Keyboard-friendly** - Power users navigate without mouse
4. **Responsive** - Desktop-first, mobile-functional

### Key Views

#### Collection Browser
```
┌────────────────────────────────────────────────────────────────┐
│ [Search...      ] [Colors▾] [Types▾] [Sets▾] [Grid│List│Table] │
├────────────────────────────────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│ │     │ │     │ │     │ │     │ │     │ │     │              │
│ │Card │ │Card │ │Card │ │Card │ │Card │ │Card │              │
│ │     │ │     │ │     │ │     │ │     │ │     │              │
│ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘              │
│ $2.50   $0.25   $15.00  $0.50   $8.00   $1.25               │
├────────────────────────────────────────────────────────────────┤
│ 1,894 cards │ $2,847.50 value │ 81 mythics │ 309 rares       │
└────────────────────────────────────────────────────────────────┘
```

#### Deck Builder
```
┌────────────────────────────────────────┬───────────────────────┐
│ Kaalia of the Vast                     │ STATS                 │
│ [Creature▾] [Instant▾] [...]           │ ═══════════════════   │
├────────────────────────────────────────┤ Avg CMC: 3.4          │
│ ▼ Commanders (1)                       │ Lands: 35 (35%)       │
│   ├ Kaalia of the Vast       $45.00    │ Creatures: 28         │
│ ▼ Protection (12)                      │                       │
│   ├ Lightning Greaves        $5.00     │ MANA CURVE            │
│   ├ Swiftfoot Boots          $2.50     │ █                     │
│   ├ Mother of Runes          $3.00     │ █ █                   │
│ ▼ Angels (12)                          │ █ █ █                 │
│   ├ Avacyn, Angel of Hope    $30.00    │ █ █ █ █               │
│   ├ Aurelia, the Warleader   $15.00    │ 1 2 3 4 5 6 7+        │
├────────────────────────────────────────┼───────────────────────┤
│ [+ Add Card] [Import] [Export]         │ Total: $847.50        │
└────────────────────────────────────────┴───────────────────────┘
```

#### AI Strategy Session
```
┌────────────────────────────────────────┬───────────────────────┐
│ [Deck Optimizer▾] llama3.1:8b          │ Kaalia of the Vast    │
├────────────────────────────────────────┤ (Context loaded)      │
│ 🤖 I've analyzed your Kaalia deck.     │                       │
│    Here are my findings:               │ ▼ Current deck list   │
│                                        │ ▼ Cards in collection │
│    **Strengths:**                      │ ▼ Budget: $50         │
│    - Strong protection suite (12)      │                       │
│    - Good tribal density (28)          │───────────────────────│
│                                        │ Quick Actions:        │
│    **Recommendations:**                │ [Analyze Mana Base]   │
│    1. Add Champion's Helm ($1.26)      │ [Find Upgrades <$5]   │
│    2. Cut Darksteel Ingot (3CMC rock)  │ [Generate Buy List]   │
│                                        │ [Compare to EDHrec]   │
├────────────────────────────────────────┤                       │
│ [Type message...]              [Send]  │                       │
└────────────────────────────────────────┴───────────────────────┘
```

---

## 🤖 SECTION 5: AGENT ARCHITECTURE AND AGENT FILES

### Agent File Format (JSON)

```json
{
  "id": "deck-optimizer",
  "name": "Deck Optimizer",
  "version": "1.0.0",
  "description": "Analyzes Commander decks and suggests improvements",
  "icon": "⚔️",
  
  "model": {
    "default": "llama3.1:8b",
    "fallback": "llama3.2:3b",
    "context_window": 32768
  },
  
  "capabilities": [
    "deck_analysis",
    "synergy_finder", 
    "meta_analysis",
    "budget_optimization"
  ],
  
  "tools": [
    "search_collection",
    "get_deck_analysis",
    "suggest_upgrades",
    "get_price_check"
  ],
  
  "system_prompt": "You are an expert MTG deck optimizer...",
  
  "parameters": {
    "temperature": 0.6,
    "max_tokens": 2048,
    "top_p": 0.9
  },
  
  "examples": [
    {
      "user": "Analyze my Kaalia deck",
      "assistant": "I'll analyze your Kaalia deck..."
    }
  ],
  
  "guardrails": {
    "max_budget_suggestion": 500,
    "require_card_ownership_check": true,
    "cite_sources": true
  }
}
```

### Planned Agents

| Agent | Model | Capabilities | Status |
|-------|-------|--------------|--------|
| Deck Optimizer | llama3.1:8b | deck_analysis, synergy, meta | 🔄 In Progress |
| Price Analyst | llama3.2:3b | price_check, buylist | 📋 Planned |
| Rules Expert | llama3.1:8b | rules, interactions | 📋 Planned |
| Meta Analyst | llama3.1:70b | meta, competitive | 📋 Planned |
| Collection Curator | llama3.2:3b | stats, duplicates | 📋 Planned |
| Synergy Finder | llama3.1:8b | combos, synergies | 📋 Planned |

---

## 🚀 SECTION 6: DEPLOYMENT AND DEVOPS

### Vercel Deployment

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "web/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/web/$1"
    }
  ],
  "env": {
    "VITE_API_URL": "@api_url",
    "VITE_OLLAMA_URL": "@ollama_url"
  }
}
```

### GitHub Pages (Static)

```yaml
# .github/workflows/deploy-pages.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install and Build
        run: |
          cd web
          npm ci
          npm run build
          
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./web/dist
```

### Environment Variables

```bash
# .env.example
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_OLLAMA_URL=http://localhost:11434

# Feature Flags
VITE_ENABLE_AI=true
VITE_ENABLE_STREAMING=true

# Analytics (optional)
VITE_POSTHOG_KEY=
```

---

## ✅ AUTONOMOUS EXECUTION CHECKLIST

### For TRAE Solo Tonight:

```
□ Phase 1: Foundation (2h)
  □ Task 1.1: Config cleanup
  □ Task 1.2: CLI entry point
  □ Task 1.3: Test infrastructure
  □ Task 1.4: Docker setup
  □ Task 1.5: Checkpoint verification

□ Phase 2: Ollama Integration (3h)
  □ Task 2.1: Ollama client
  □ Task 2.2: Agent base class
  □ Task 2.3: Deck optimizer agent
  □ Task 2.4: Agent registry
  □ Task 2.5: Checkpoint verification

□ Phase 3: Web Foundation (3h)
  □ Task 3.1: Vite + React setup
  □ Task 3.2: Dark theme design
  □ Task 3.3: Layout components
  □ Task 3.4: API client setup
  □ Task 3.5: Checkpoint verification

□ Phase 4: UI Components (3h) [if time permits]
  □ Task 4.1: Card grid/list
  □ Task 4.2: Card detail panel
  □ Task 4.3: Deck builder
  □ Task 4.4: Search/filter
  □ Task 4.5: Checkpoint verification
```

### Human Review Required:

- [ ] Security review of API endpoints
- [ ] Final UI/UX approval
- [ ] Production deployment configuration
- [ ] API key management for TCGPlayer

---

## 📝 CHANGELOG TEMPLATE

```markdown
# TRAE Solo Development Log

## [Session Date]

### Completed Tasks
- Task X.Y: Description
  - Files modified: [list]
  - Tests: [pass/fail]

### Issues Encountered
- Issue: Description
- Resolution: How it was fixed

### Next Steps
- What remains to be done
- Blockers identified

### Verification Results
- Phase N checkpoint: [pass/fail]
- Test coverage: X%
```

---

**Ready for autonomous execution! Let's build something amazing. ⚔️🔥**
