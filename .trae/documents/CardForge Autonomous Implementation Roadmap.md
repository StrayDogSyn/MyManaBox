# CardForge Autonomous Implementation Roadmap

This comprehensive roadmap outlines the transformation of CardForge into a professional-grade MTG collection management platform with AI capabilities and a modern web interface.

## Phase 1: Foundation (2h)
**Goal:** Establish a robust project structure, configuration management, and testing infrastructure.

1.  **Consolidate Configuration**
    *   Update `cardforge/config/settings.py` to include `OllamaConfig` dataclass for AI model settings (base URL, timeout, default models).
    *   Ensure all settings are loadable from `.env` with sensible defaults.
    *   Verify `AppConfig` aggregates all sub-configs (Database, Scryfall, Ollama, API, etc.).

2.  **Unified CLI Entry Point**
    *   Enhance `cardforge/cli/main.py` to include missing command groups: `agent` (AI tasks) and `server` (web backend).
    *   Ensure `python -m cardforge` works correctly as the single entry point.
    *   Implement `agent list` and `agent run` commands in the CLI.

3.  **Test Infrastructure**
    *   Create `pytest.ini` for test configuration (markers, coverage settings).
    *   Expand `tests/conftest.py` with fixtures for `OllamaClient` mocking and database state.
    *   Create `tests/test_models/test_card.py` to test the core Card model.

4.  **Docker Environment**
    *   Create `Dockerfile` for the CardForge application (Python 3.12+).
    *   Create `docker-compose.yml` to orchestrate CardForge and a local Ollama service.
    *   Configure volumes for persistent data (SQLite DB, Ollama models).

## Phase 2: Ollama Integration (3h)
**Goal:** Enable local AI agents to perform complex MTG tasks using intelligent model routing.

1.  **Async Ollama Client & Routing**
    *   Refine `src/data/ollama_client.py` to ensure robust error handling (retries, timeouts).
    *   Leverage `src/services/ai/model_selection.py` for intelligent routing:
        *   **Simple**: `llama3.2:3b` for classification/routing.
        *   **Balanced**: `llama3.1:8b` (or `qwen2.5-coder:7b`) for deck optimization.
        *   **Complex**: `llama3.1:70b` for deep strategic analysis.

2.  **Base Agent & Implementation**
    *   Review and enhance `src/services/ai/base_agent.py` to standardize `execute()` and `_generate()` methods.
    *   Finalize `DeckOptimizerAgent` (`src/services/ai/agents/deck_optimizer.py`) with specific system prompts for Commander optimization.

3.  **Agent Registry System**
    *   Create `src/services/ai/registry.py` to register and discover available agents.
    *   Implement a factory pattern to instantiate agents with the shared `OllamaClient`.

## Phase 3: Web Foundation (3h)
**Goal:** Create a modern, responsive web interface using React and Vite.

1.  **Project Initialization**
    *   Initialize a new Vite project in `web/` directory with React and TypeScript.
    *   Install core dependencies: `react-router-dom`, `@tanstack/react-query`, `axios`, `lucide-react`.

2.  **Theming & Layout**
    *   Implement Moxfield-inspired dark theme using CSS variables (Tailwind CSS recommended).
    *   Define color palette: Backgrounds (`#0f0f0f`), Accents (Gold/Mana colors).
    *   Build `AppShell` layout with `Sidebar` navigation and `Header` user controls.

3.  **State Management**
    *   Configure `QueryClient` for React Query to handle server state.
    *   Set up Axios instance with base URL and interceptors for error handling.

## Phase 4: UI Components (3h)
**Goal:** Build the core visual components for managing collections and decks.

1.  **Card Display**
    *   Develop `CardGrid` and `CardList` components with virtualization for performance.
    *   Create `CardCard` component showing image, price, and basic stats.

2.  **Card Details Panel**
    *   Build a detailed view overlay/page showing:
        *   Pricing history (using Recharts or similar).
        *   Oracle text, rulings, and legalities.
        *   Synergy scores (placeholder for AI analysis).

3.  **Deck Builder Interface**
    *   Create a drag-and-drop interface for deck construction.
    *   Implement grouping by card type (Creature, Instant, etc.) and custom categories.
    *   Add a "Mana Curve" visualization chart.

4.  **Advanced Search**
    *   Implement a robust search bar with autocomplete.
    *   Add filter modals for Color, Rarity, Set, Format, and Price.

## Phase 5: AI Workspace (3h)
**Goal:** Integrate AI agents directly into the user workflow.

1.  **Chat Interface**
    *   Build a `ChatWindow` component with message history and typing indicators.
    *   Implement markdown rendering for AI responses (using `react-markdown`).

2.  **Context Injection**
    *   Develop a mechanism to serialize the current deck/collection context and send it with the prompt.
    *   Allow users to "Ask AI about this deck" with a single click.

3.  **Strategy Session View**
    *   Create a dedicated view for deep-dive analysis.
    *   Display AI recommendations side-by-side with the deck list for easy application.

## Phase 6: Deployment (2h)
**Goal:** Automate testing and deployment pipelines.

1.  **CI/CD Pipeline**
    *   Create `.github/workflows/ci.yml` for automated testing (pytest) and linting.
    *   Add a build step for the Vite web application.

2.  **Vercel & GitHub Pages**
    *   Configure `vercel.json` for production deployment of the web frontend.
    *   Add a GitHub Actions job to deploy the static web build to GitHub Pages (optional backup).

3.  **Environment Management**
    *   Document all required environment variables in `.env.example`.
    *   Ensure the application handles missing keys gracefully in production.
