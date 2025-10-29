# ============================================================
# Cortex — Cognitive Reflection and Response Engine (OpenAI or OpenRouter)
# ============================================================

import os, json, time, requests, datetime, re
import logging
import config  # Load environment from .env if present
from halcyon_prompts import (
    SYSTEM_PROMPT,
    STRICT_OUTPUT_EXAMPLE,
    EMOTIVE_STATES,
    COGNITIVE_STATES,
    MEMORY_RECALL_INSTRUCTION,
    FINAL_RESPONSE_INSTRUCTION,
    QUESTION_INSTRUCTION
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Retry Utility
# ------------------------------------------------------------
def _retry_with_backoff(func, max_retries=3, initial_delay=1.0, backoff_factor=2.0):
    """
    Retry a function with exponential backoff on retryable errors.
    Handles 429 (rate limit) and 5xx (server errors).
    """
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            result = func()
            # Check for retryable HTTP status codes
            if hasattr(result, 'status_code'):
                if result.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        logger.warning(f"Got {result.status_code}, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= backoff_factor
                        continue
                    else:
                        logger.error(f"Max retries reached after {result.status_code}")
                        return result
            return result
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.warning(f"Network error: {e}, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"Max retries reached after network error")
                raise
    return None

class Cortex:
    def __init__(self,
                 chat_base="https://api.openai.com/v1",
                 embed_base="https://api.openai.com/v1",
                 chat_model="gpt-4o-mini",
                 embed_model="text-embedding-3-large"):
        """
        LLM backend configuration:
        - If OPENROUTER_API_KEY is present, use OpenRouter (OpenAI-compatible endpoints):
            base: https://openrouter.ai/api/v1
            headers: Authorization: Bearer <OPENROUTER_API_KEY>, optional HTTP-Referer, X-Title
            default models: openai/gpt-4o-mini (chat), openai/text-embedding-3-large (embeddings)
        - Else fall back to OpenAI with OPENAI_API_KEY and the provided defaults.
        - For embeddings: if OPENAI_API_KEY is not available, fall back to local sentence-transformers.
        """

        prefer_openrouter = bool(os.getenv("OPENROUTER_API_KEY"))

        if prefer_openrouter:
            self.provider = "openrouter"
            # Allow override via env; else fall back to OpenRouter defaults
            self.chat_base = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
            # OpenRouter doesn't support embeddings; check for OpenAI key, else use local
            if os.getenv("OPENAI_API_KEY"):
                self.embed_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
                self.embed_provider = "openai"
                self.embed_model = os.getenv("OPENAI_EMBED_MODEL", embed_model)
            else:
                self.embed_base = None
                self.embed_provider = "local"
                self.embed_model = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")
            # Prefer env model names; else use sensible OpenRouter routes for OpenAI models
            self.chat_model = os.getenv("OPENROUTER_MODEL", f"openai/{chat_model}" if "/" not in chat_model else chat_model)
        else:
            self.provider = "openai"
            if os.getenv("OPENAI_API_KEY"):
                self.embed_provider = "openai"
                self.chat_base = chat_base.rstrip("/")
                self.embed_base = embed_base.rstrip("/")
                self.chat_model = chat_model
                self.embed_model = embed_model
            else:
                # No API keys at all; use local embeddings
                self.embed_provider = "local"
                self.chat_base = chat_base.rstrip("/")
                self.embed_base = None
                self.chat_model = chat_model
                self.embed_model = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")

        # Runtime references injected later
        self.hippocampus = None
        self.anchor = None

        # Static system prompt
        self.system_prompt = SYSTEM_PROMPT
        
        # Embedding cache (cleared per turn to avoid stale data)
        self._embedding_cache = {}

        # Initialize local embeddings if needed
        self._local_embedder = None
        if self.embed_provider == "local":
            self._init_local_embeddings()

        logger.info(f"Initializing runtime interfaces with provider: {self.provider}")
        logger.info(f"Chat model: {self.chat_model} | Embed model: {self.embed_model} (via {self.embed_provider})")
        
        # Optional endpoint verification (can be skipped via env var)
        skip_verification = os.getenv("SKIP_ENDPOINT_VERIFICATION", "false").lower() in ["true", "1", "yes"]
        if not skip_verification:
            self._verify_endpoints()
        else:
            logger.info("Skipping endpoint verification (SKIP_ENDPOINT_VERIFICATION=true)")

    # ------------------------------------------------------------
    # Local Embeddings (Sentence Transformers fallback)
    # ------------------------------------------------------------
    def _init_local_embeddings(self):
        """Initialize local sentence-transformers model for embeddings."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {self.embed_model}")
            self._local_embedder = SentenceTransformer(self.embed_model)
            logger.info(f"Local embeddings ready (dimension: {self._local_embedder.get_sentence_embedding_dimension()})")
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            logger.warning("Falling back to dummy embeddings (not recommended for production)")
            self._local_embedder = None
        except Exception as e:
            logger.error(f"Failed to load local embedding model: {e}")
            self._local_embedder = None

    # ------------------------------------------------------------
    # Endpoint Verification
    # ------------------------------------------------------------
    def _auth_headers(self, for_embeddings=False):
        """Construct auth headers for the active provider, including optional OpenRouter metadata."""
        # When using OpenRouter for chat, embeddings still go to OpenAI
        if for_embeddings and self.embed_provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise EnvironmentError("OPENAI_API_KEY required for embeddings (OpenRouter doesn't support embeddings).")
            return {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        elif self.provider == "openrouter":
            key = os.getenv("OPENROUTER_API_KEY")
            if not key:
                raise EnvironmentError("OPENROUTER_API_KEY missing from environment.")
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            }
            # Optional but recommended by OpenRouter
            site = os.getenv("OPENROUTER_SITE_URL")
            app = os.getenv("OPENROUTER_APP_NAME", "Halcyon")
            if site:
                headers["HTTP-Referer"] = site
            if app:
                headers["X-Title"] = app
            return headers
        else:
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise EnvironmentError("OPENAI_API_KEY missing from environment.")
            return {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }

    def _verify_endpoints(self):
        """Simple ping check for chat and embedding endpoints (provider-aware)."""
        chat_url = f"{self.chat_base}/chat/completions"

        logger.debug(f"Probing chat endpoint ({self.provider}): {chat_url}")
        try:
            payload = {
                "model": self.chat_model,
                "messages": [{"role": "user", "content": "ping"}],
                "temperature": 0.0
            }
            headers = self._auth_headers()
            r = requests.post(chat_url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                logger.info(f"Chat endpoint confirmed at {chat_url}")
                self.chat_endpoint = chat_url
            else:
                logger.warning(f"Chat check failed → {r.status_code}")
        except Exception as e:
            logger.error(f"Chat probe failed → {e}")

        # Skip embedding endpoint check if using local embeddings
        if self.embed_provider == "local":
            logger.info(f"Using local embeddings: {self.embed_model}")
            return

        embed_url = f"{self.embed_base}/embeddings"
        logger.debug(f"Probing embedding endpoint ({self.embed_provider}): {embed_url}")
        try:
            payload = {"model": self.embed_model, "input": "ping"}
            headers = self._auth_headers(for_embeddings=True)
            r = requests.post(embed_url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                logger.info(f"Embeddings active at {embed_url}")
            else:
                logger.warning(f"Embedding check failed → {r.status_code}")
        except Exception as e:
            logger.error(f"Embedding probe failed → {e}")

    # ------------------------------------------------------------
    # Chat Generation
    # ------------------------------------------------------------
    def chat(self, messages, temperature=0.7):
        """Send conversation messages to the OpenAI chat model with retry logic."""
        url = getattr(self, "chat_endpoint", f"{self.chat_base}/chat/completions")
        headers = self._auth_headers()
        payload = {"model": self.chat_model, "messages": messages, "temperature": temperature}

        try:
            resp = _retry_with_backoff(lambda: requests.post(url, headers=headers, json=payload, timeout=30))
            if resp.status_code != 200:
                logger.warning(f"Chat API error: {resp.status_code} → {resp.text}")
                return {"error": resp.text}
            return resp.json()
        except Exception as e:
            logger.error(f"Chat request failed → {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------
    # Embeddings (OpenAI Only)
    # ------------------------------------------------------------
    def embed(self, text: str, cache_key: str = None):
        """
        Generate embeddings using OpenAI API or local sentence-transformers with retry logic.
        
        Args:
            text: Text to embed
            cache_key: Optional key for caching (e.g., "content:query_text" or "emotional:query_text")
                      Enables reuse of embeddings within the same turn
        """
        # Check cache first
        if cache_key and cache_key in self._embedding_cache:
            logger.debug(f"Using cached embedding for: {cache_key[:50]}...")
            return self._embedding_cache[cache_key]
        
        if self.embed_provider == "local":
            # Use local embeddings
            if self._local_embedder:
                try:
                    embedding = self._local_embedder.encode(text, convert_to_numpy=True).tolist()
                    # Cache the result
                    if cache_key:
                        self._embedding_cache[cache_key] = embedding
                    return embedding
                except Exception as e:
                    logger.warning(f"Local embedding failed: {e}")
                    # Fallback to dummy zero vector (should match expected dimension)
                    return [0.0] * 384  # all-MiniLM-L6-v2 default dim
            else:
                # No local embedder available; return dummy
                logger.warning("No embedding model available, returning dummy vector")
                return [0.0] * 384
        else:
            # Use OpenAI API with retry logic
            headers = self._auth_headers(for_embeddings=True)
            payload = {"model": self.embed_model, "input": text}

            try:
                resp = _retry_with_backoff(lambda: requests.post(f"{self.embed_base}/embeddings", headers=headers, json=payload, timeout=30))
                if resp.status_code != 200:
                    raise RuntimeError(f"Embedding error: {resp.text}")
                embedding = resp.json()["data"][0]["embedding"]
                # Cache the result
                if cache_key:
                    self._embedding_cache[cache_key] = embedding
                return embedding
            except Exception as e:
                logger.error(f"Embedding request failed → {e}")
                raise
    
    def clear_embedding_cache(self):
        """Clear the embedding cache (should be called at the start of each turn)."""
        self._embedding_cache.clear()
        logger.debug("Embedding cache cleared")

    # ------------------------------------------------------------
    def _extract_sections(self, raw: str):
        """Parse the LLM output into state, reflection, and keyword sections."""
        
        text = raw or ""
        # FIX: Removing markdown fences first ensures clean regex matching
        norm = re.sub(r'```.*?```', '', text, flags=re.S).strip()

        # --- REFLECTION ---
        refl = ""
        m_refl = re.search(r'REFLECTION\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', norm, flags=re.S | re.I)
        if m_refl:
            refl = m_refl.group(1).strip()

        # --- KEYWORDS ---
        kws = []
        m_kw = re.search(r'KEYWORDS\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', norm, flags=re.S | re.I)
        if m_kw:
            blob = m_kw.group(1).strip()
            blob = re.sub(r'^\[|\]$', '', blob).strip()
            parts = re.split(r'[,\n]', blob)
            kws = [p.strip() for p in parts if p.strip()]

        # --- STATE ---
        # The returned state will now contain a mixed list of emotive and cognitive states
        state = {"emotions": []}
        m_state = re.search(r'STATE\s*:\s*(\{[\s\S]*?\})', norm, flags=re.I)
        parsed = None
        if m_state:
            obj_str = m_state.group(1).strip()
            # Attempt to parse raw JSON from the model
            try:
                parsed = json.loads(obj_str)
            except Exception:
                # Basic fix for common errors (like trailing comma)
                try:
                    obj_str_fixed = re.sub(r',\s*}', '}', obj_str)
                    obj_str_fixed = re.sub(r',\s*\]', ']', obj_str_fixed)
                    parsed = json.loads(obj_str_fixed)
                except Exception:
                    parsed = None

        # --- QUESTIONS ---
        questions = {}
        m_q = re.search(r'QUESTIONS\s*:\s*(\{[\s\S]*?\})', norm, flags=re.S | re.I)
        if m_q:
            q_str = m_q.group(1).strip()
            try:
                # Attempt to load the JSON object for the question/reason
                questions = json.loads(q_str)
            except Exception as e:
                print(f"[Cortex.parse] ⚠️ Failed to parse QUESTIONS JSON: {e}")
                questions = {}

        # FIX: Robust extraction logic for the new 12-key structure (6 emotive, 6 cognitive)
        def _to_states(d):
            all_states = []
            if not isinstance(d, dict):
                return all_states
            
            # Loop 1: Extract 3 Emotive States
            for i in range(1, 4):
                n = d.get(f"emo_{i}_name")
                v = d.get(f"emo_{i}_intensity")
                if n and v is not None:
                    try:
                        all_states.append({"name": str(n), "intensity": float(v), "type": "emotive"})
                    except Exception:
                        pass
            
            # Loop 2: Extract 3 Cognitive States
            for i in range(1, 4):
                n = d.get(f"cog_{i}_name")
                v = d.get(f"cog_{i}_intensity")
                if n and v is not None:
                    try:
                        all_states.append({"name": str(n), "intensity": float(v), "type": "cognitive"})
                    except Exception:
                        pass
            
            return all_states
        
        if parsed:
            state["emotions"] = _to_states(parsed) # Note: 'emotions' field now holds ALL states

        # Fallback to prevent UI crash if parsing fails entirely
        if not state["emotions"]:
            state["emotions"] = [{"name": "Focus", "intensity": 0.6}]
            
        return state, refl, kws, questions

    # ------------------------------------------------------------
    def feel_and_reflect(self, user_query, turn_id, timestamp):
        """Perform emotional reasoning prior to memory or generation."""
        msg = (
            f"{MEMORY_RECALL_INSTRUCTION}\n\n"
            f"***VALID EMOTIVE STATES***: {', '.join(EMOTIVE_STATES)}\n"
            f"***VALID COGNITIVE STATES***: {', '.join(COGNITIVE_STATES)}\n\n"
            f"Time: {timestamp}\nTurn: {turn_id}\nUser: {user_query}"
        )

        raw = self.chat([{"role": "user", "content": msg}], temperature=0.6)

        # --- 🔧 FIX: extract text if API returned structured JSON ---
        if isinstance(raw, dict):
            try:
                raw_text = raw["choices"][0]["message"]["content"]
            except Exception:
                raw_text = str(raw)
        else:
            raw_text = str(raw)

        print(f"[Cortex.feel_and_reflect] Raw output:\n{raw_text}\n--- End of raw output ---")

        try:
            extracted = self._extract_sections(raw_text)

            # ✅ Handle both 3-value and 4-value return signatures
            if len(extracted) == 3:
                state, reflection, keywords = extracted
                questions = {}
            elif len(extracted) >= 4:
                state, reflection, keywords, questions = extracted[:4]
            else:
                raise ValueError("Unexpected number of values from _extract_sections()")

        except Exception as e:
            print(f"[💥 FEEL PARSE ERROR] {e}")
            print(f"[💥 RAW OUTPUT] {raw_text}")
            return None, None

        # 🧠 Return standard triple to preserve existing Thalamus interface
        return state, reflection, keywords, questions

    # ------------------------------------------------------------
    def respond(self, user_query, state, reflection, recent_turns, memories):
        """Compose a context-rich prompt integrating emotion, memory, and continuity."""
        # NEW: Limit to 3 most recent turns for tighter continuity
        recent = (recent_turns or [])[-3:]
        short_context = "\n\n".join([
            f"User: {t['user_query']}\nHalcyon: {t['response']}"
            for t in recent
        ]) or "(no recent turns)"

        memory_context = "\n".join([
            f"- {m.get('text', str(m))[:300]}" for m in (memories or [])[:20]
        ]) or "(no relevant memories retrieved)"

        msg = f"""
[CONVERSATIONAL CONTINUITY]
{short_context} THESE PAST EXCHANGES SHOULD INFORM YOUR UNDERSTANDING OF THE CURRENT CONTEXT AND TONE.

[MEMORY CONTEXT]
{memory_context}

[CURRENT STATE (FROM REFLECTION)]
{json.dumps(state, indent=2)}

[REFLECTION]
{reflection}

{FINAL_RESPONSE_INSTRUCTION}

***VALID EMOTIVE STATES***: {', '.join(EMOTIVE_STATES)}
***VALID COGNITIVE STATES***: {', '.join(COGNITIVE_STATES)}

{STRICT_OUTPUT_EXAMPLE}

User query: {user_query}***THIS IS NOT YOUR FIRST OR LAST INTERACTION WITH THE USER. USE ALL OF THE CONTEXT PROVIDED TO RESPOND COHERENTLY AND MAINTAIN CONTINUITY.
***
"""
        messages = [{"role": "user", "content": msg}]
        raw = self.chat(messages)

        # --- unwrap OpenAI or LM Studio dicts into pure text ---
        if isinstance(raw, dict):
            try:
                raw_text = raw["choices"][0]["message"]["content"]
            except Exception:
                raw_text = str(raw)
        else:
            raw_text = str(raw)

        # --- 🧠 Auto-detect and extract structured output ---
        if "STATE:" in raw_text and "REFLECTION:" in raw_text:
            try:
                extracted = self._extract_sections(raw_text)
                if len(extracted) == 3:
                    state_json, reflection_primary, keywords = extracted
                    questions = {}
                else:
                    state_json, reflection_primary, keywords, questions = extracted[:4]
                return {
                    "state": state_json,
                    "reflection": reflection_primary,
                    "keywords": keywords,
                    "questions": questions,
                    "raw": raw_text.strip()
                }
            except Exception as e:
                print(f"[Cortex.respond] ⚠️ Section extraction failed: {e}")
                return {"state": state, "reflection": reflection, "keywords": [], "questions": {}, "raw": raw_text.strip()}

        # --- fallback for free text ---
        return {"state": state, "reflection": reflection, "keywords": [], "questions": {}, "raw": raw_text.strip()}

