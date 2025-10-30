# Hal — Emotional Memory Agent

Hal is an LLM-driven agent with emotional state, reflection, and long-term memory. It supports Qdrant's optional **named vectors** for dual-perspective memory (factual/semantic and emotional/tonal). By default it runs in a single‑vector mode for speed; enable dual vectors via `USE_DUAL_VECTORS=true`.

## Overview

- UI: `hal_ui.py` (Tkinter)
- Orchestrator: `thalamus.py`
- LLM I/O: `cortex.py` (OpenAI or OpenRouter; OpenAI-compatible HTTP)
- Long-term memory: `hippocampus.py` (Qdrant with named vectors; 384-d or 3072-d embeddings)
- Working/anchor windows: `temporal_anchor.py` (used by UI)
- Prompts and state vocab: `halcyon_prompts.py`

### Memory Architecture

Hal can store each memory with either a single vector (default) or two named vectors:
- Single vector (default): One embedding representing overall content; fastest path.
- Dual named vectors (when `USE_DUAL_VECTORS=true`):
  - **`content`**: Factual/semantic embedding of the full conversation
  - **`emotional`**: Embedding focused on emotional tone and feelings

Search modes in `hippocampus.py`:
- **Hybrid**: Merge `content` and `emotional` results (only meaningful in dual‑vector mode)
- **Content**: Factual similarity
- **Emotional**: Feeling/tone similarity (dual‑vector mode)

Turn flow (simplified):
1) Feel + reflect → structured emotional/cognitive state
2) Recall memories via Qdrant (dual named vector search)
3) Compose response using state + reflection + context
4) Log turn to `runtime_logs/YYYY-MM-DD/turn_log.jsonl`
5) Commit memory to Qdrant (single vector by default; both vectors when dual mode is enabled)

## Prerequisites

- macOS (tested), Python 3.10+
- Docker (to run Qdrant locally)
- Either an OpenAI API key (`OPENAI_API_KEY`) or an OpenRouter API key (`OPENROUTER_API_KEY`)

## Setup

```zsh
# 1) Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# 2) Install Python dependencies
pip install -r requirements.txt

# 3) Start Qdrant locally (data will be ephemeral unless you mount storage)
docker run --rm -p 6333:6333 qdrant/qdrant
# Optional: persist data to a local folder
# docker run --rm -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant

# 4) Set your API key (OpenAI or OpenRouter) in the environment (zsh) or via a .env file
# Option A: OpenAI
# export OPENAI_API_KEY=sk-...

# Option B: OpenRouter (recommended headers for best rate limits)
# export OPENROUTER_API_KEY=or-...
# export OPENROUTER_SITE_URL="https://yourapp.example.com"   # optional, helps OpenRouter attribute traffic
# export OPENROUTER_APP_NAME="Halcyon"                       # optional, app title shown in OpenRouter

# Alternatively, create a .env file in the project root:
# Option A: OpenRouter for chat + OpenAI for embeddings
# OPENROUTER_API_KEY=or-...
# OPENAI_API_KEY=sk-...           # Required for embeddings (OpenRouter doesn't support embeddings)
# OPENROUTER_SITE_URL=https://yourapp.example.com
# OPENROUTER_APP_NAME=Halcyon
#
# Option B: OpenRouter for chat + local embeddings (no OpenAI key needed)
# OPENROUTER_API_KEY=or-...
# LOCAL_EMBED_MODEL=all-MiniLM-L6-v2  # requires: pip install sentence-transformers
#
# Option C: OpenAI for both chat and embeddings:
# OPENAI_API_KEY=sk-...
#
# Qdrant configuration (optional, defaults shown):
# Single unified collection with named vectors
# QDRANT_HOST=localhost
# QDRANT_PORT=6333
# QDRANT_COLLECTION=hal_memory
```

## Run the desktop UI

```zsh
python hal_ui.py
```

- Chat tab: type a message and press Enter or Send; you’ll see the inner reflection and the final response.
- Memory Workspace: browse working turns, anchor history, and curiosity items.
- Settings tab: placeholder for future tuning.

### Run headless (no Tkinter required)

If your Python doesn’t include Tk, use the CLI:

```zsh
python cli.py
```

Type your message and press Enter. Type `exit` to quit.

## Configuration

Provider auto-detection and defaults are handled in `cortex.py` (and `.env` is loaded automatically at startup):
- If `OPENROUTER_API_KEY` is present, the app uses OpenRouter at `https://openrouter.ai/api/v1` for chat completions, adding `HTTP-Referer` and `X-Title` headers when provided.
  - **Embeddings**: OpenRouter doesn't support embeddings, so:
    - If `OPENAI_API_KEY` is also set, embeddings use OpenAI (recommended for production).
    - Otherwise, local sentence-transformers embeddings are used (requires `pip install sentence-transformers`).
  - Default models (override with env):
    - Chat: `OPENROUTER_MODEL` (default: `openai/gpt-4o-mini`)
    - Embeddings (OpenAI): `OPENAI_EMBED_MODEL` (default: `text-embedding-3-large`)
    - Embeddings (local): `LOCAL_EMBED_MODEL` (default: `all-MiniLM-L6-v2`)
- Otherwise it uses OpenAI for both:
  - Chat model: `gpt-4o-mini`
  - Embeddings: `text-embedding-3-large`
- Qdrant configuration (all optional, defaults shown):
  - `QDRANT_HOST` (default: `localhost`)
  - `QDRANT_PORT` (default: `6333`)
  - `QDRANT_COLLECTION` (default: `hal_memory`) — single collection; schema depends on `USE_DUAL_VECTORS`
  - `USE_DUAL_VECTORS` (default: false) — when true, creates named vectors `content` and `emotional`
  - `SKIP_ENDPOINT_VERIFICATION` (default: false) — when true, skips startup probes of chat/embedding endpoints

Embedding cache: `Cortex.embed(text, cache_key)` caches per‑turn; `Thalamus.process_turn()` clears the cache at the start of each turn.

### Named Vectors Architecture (optional)

When `USE_DUAL_VECTORS=true`, each memory stores two embeddings:
1. **Content** — semantic/factual ("what was discussed")
2. **Emotional** — tone/feeling ("how it felt")

Search modes (in `Hippocampus.recall_with_context`):
- `"hybrid"` (default): Query both vectors and merge
- `"content"`: Factual similarity only
- `"emotional"`: Feeling similarity (dual‑vector mode)

Important: Qdrant collection schemas are immutable. If you toggle `USE_DUAL_VECTORS`, delete the existing collection so it can be recreated with the new schema.

## Logging and data

- Turn logs: `runtime_logs/YYYY-MM-DD/turn_log.jsonl`
- Narrative/anchor journals: `memory_journals/` (persisted by `TemporalAnchor.save()`/`load()`; not auto‑invoked by `Thalamus`)
- These paths are ignored by Git via `.gitignore`.

## Troubleshooting

- Missing API key:
  - OpenAI: ensure `export OPENAI_API_KEY=...`
  - OpenRouter: ensure `export OPENROUTER_API_KEY=...` (and optionally `OPENROUTER_SITE_URL`, `OPENROUTER_APP_NAME`)
- Qdrant connection refused: verify Docker container is running and port 6333 is available.
- Tkinter issues on macOS: if using a non-system Python, ensure it has Tk support (some setups need `brew install python-tk`).
- Embedding dimension changes: `Hippocampus` infers vector size from the active embedding provider/model. If you switch providers/models (e.g., OpenAI 3072‑d ↔ local 384‑d) or toggle `USE_DUAL_VECTORS`, delete the Qdrant collection so it can be recreated with the correct schema.
- OpenRouter does not provide embeddings; use OpenAI for embeddings or local `sentence-transformers`.

## Notes

- External Python deps: `qdrant-client`, `requests` (and optionally `sentence-transformers` for local embeddings).
- `.env` is loaded automatically via `config` import.
- The Tkinter UI wires `TemporalAnchor` for working/anchor/curiosity, while `Thalamus` runs the main turn pipeline.

---

MIT-style use encouraged. Be mindful not to commit logs or secrets; `.gitignore` excludes common transient files and folders.
