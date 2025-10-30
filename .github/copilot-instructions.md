# Copilot Instructions for this Repo

## Big picture
- Hal is an LLM agent with an orchestrator and brain-metaphor components:
  - `thalamus.py` orchestrates a turn (reflect → recall → respond → commit → log).
  - `cortex.py` wraps chat/embeddings (OpenAI or OpenRouter for chat; OpenAI or local sentence-transformers for embeddings) and parses structured output.
  - `hippocampus.py` is long‑term memory over Qdrant (single vector by default, or dual named vectors via env) with search and upsert.
  - `temporal_anchor.py` is short‑term/working memory + anchor history + curiosity queue (used by UI).
  - `hal_ui.py` is a Tkinter desktop UI wiring everything together.
  - `halcyon_prompts.py` contains prompt constants and valid state vocab.

## Runtime and environment tips
- .env is auto‑loaded via `config` import; useful vars:
  - Chat provider: `OPENROUTER_API_KEY` (uses OpenRouter base), otherwise `OPENAI_API_KEY`.
  - Embeddings: if no `OPENAI_API_KEY`, falls back to local `sentence-transformers` (`LOCAL_EMBED_MODEL`, default all‑MiniLM‑L6‑v2).
  - Qdrant: `QDRANT_HOST` (default localhost), `QDRANT_PORT` (default 6333), `QDRANT_COLLECTION` (default hal_memory).
  - Dual vectors: `USE_DUAL_VECTORS=true` to store/search both `content` and `emotional` vectors; default is single vector for speed.
- Embedding cache: `Cortex.embed(text, cache_key)` caches per turn; `Thalamus.process_turn` clears it at start.
- Vector dims: OpenAI `text-embedding-3-large` → 3072; local MiniLM → 384. Hippocampus infers size from provider.

## Data flow (per turn)
1) `Cortex.feel_and_reflect()` produces state, reflection, keywords (and optional question).
2) `Hippocampus.recall_with_context(query, n_results=25, search_mode='hybrid')`:
   - Single‑vector mode queries default vector; dual‑vector mode queries named vectors `content` and `emotional` and merges.
   - Cache keys used: `content:{query}` and `emotional:{query}`.
3) `Cortex.respond(...)` re‑parses structured sections if present.
4) `Hippocampus.delayed_commit(...)` upserts memory (deterministic id by SHA1 of fused text) with payload metadata.
5) `Thalamus.log_turn(...)` appends to `runtime_logs/YYYY-MM-DD/turn_log.jsonl`.

## Qdrant conventions
- Collection is created on startup if missing.
  - Single vector: `models.VectorParams(size=<inferred>, distance=COSINE)`.
  - Dual named vectors: `{ 'content': VectorParams(...), 'emotional': VectorParams(...) }` when `USE_DUAL_VECTORS=true`.
- Collection vector schema is immutable; if you change `USE_DUAL_VECTORS`, delete the collection to recreate.
- Search modes in `recall_with_context`: `content`, `emotional`, `hybrid` (default). Prints tabular debug of results.

## UI and short‑term memory
- `hal_ui.py` wires: Cortex + Hippocampus + TemporalAnchor + Thalamus; calls run on a worker thread, results posted to UI.
- `TemporalAnchor` keeps:
  - `working_window` recent turns; `anchor_window` short history; `curiosity_queue` for questions the model raises.
  - Persistence helpers `save()`/`load()` write to `memory_journals/` (not auto‑invoked by Thalamus).

## Developer workflows
- Run desktop UI: `python hal_ui.py`.
- Start Qdrant locally (example): `docker run --rm -p 6333:6333 qdrant/qdrant`.
- Nuke collection from a shell: `python -c "from qdrant_client import QdrantClient; QdrantClient(host='localhost',port=6333).delete_collection('hal_memory')"`.
- Logs to inspect behavior: `runtime_logs/<date>/turn_log.jsonl` and console prints from each component.

## Project‑specific patterns
- Structured output contract: the model returns 3 labeled sections (STATE, REFLECTION, RESPONSE). See `STRICT_OUTPUT_EXAMPLE`.
- State format is a flat 12‑key JSON (3 emotive + 3 cognitive name/intensity pairs); `Cortex._extract_sections` normalizes it.
- Recent‑turn continuity: `Hippocampus.get_recent_turns(n=3)` loads from logs to feed `Cortex.respond`.
- Memory payload fields include `manual_weight`; pinning in UI calls `Hippocampus.adjust_weight` (Qdrant `set_payload`).

## Gotchas
- OpenRouter doesn’t serve embeddings; use OpenAI for embeddings or local sentence‑transformers.
- Keep embedding dimension consistent with collection schema; switching providers may require recreating the collection.
- If `SKIP_ENDPOINT_VERIFICATION=true`, Cortex skips startup probes; otherwise it pings chat/embedding endpoints.
