# ============================================================
# Cortex — Cognitive Reflection and Response Engine (Final Clean)
# ============================================================

import hashlib
import json, time, requests
import datetime
import re
# Imports all static prompts and state lists for clean code
from halcyon_prompts import SYSTEM_PROMPT, STRICT_OUTPUT_EXAMPLE, EMOTIVE_STATES, COGNITIVE_STATES, MEMORY_RECALL_INSTRUCTION, FINAL_RESPONSE_INSTRUCTION

class Cortex:
    def __init__(self,
                 chat_base="https://api.openai.com/v1",
                 embed_base="http://127.0.0.1:1234",
                 chat_model="gpt-4o-mini",
                 embed_model="text-embedding-nomic-embed-text-v1.5"):
        self.chat_base = chat_base.rstrip("/")
        self.embed_base = embed_base.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model

        
        # References injected by Thalamus at runtime
        self.hippocampus = None
        self.anchor = None 

        # Assign system prompt from the external file
        self.system_prompt = SYSTEM_PROMPT 

        print("[Cortex] Initializing runtime interfaces...")
        self._verify_endpoints()

    # --------------------------------------------------------
    # Runtime Diagnostics
    # --------------------------------------------------------
    def _verify_endpoints(self):
        """Test all candidate chat endpoints to confirm model reachability."""
        import os
        openai_key = os.getenv("OPENAI_API_KEY")
        candidates = [
            f"{self.chat_base}/v1/chat/completions",
            f"{self.chat_base}/chat/completions",
            f"{self.chat_base}/v1/completions",
            f"{self.chat_base}/completions"
        ]

        print(f"[Cortex] 🔍 Probing chat endpoints on {self.chat_base} ...")
        found = False
        for url in candidates:
            try:
                headers = {"Authorization": f"Bearer {openai_key}"} if "openai.com" in self.chat_base.lower() else {}
                payload = {
                    "model": self.chat_model,
                    "messages": [{"role": "user", "content": "ping"}],
                    "temperature": 0.0
                }
                r = requests.post(url, headers=headers, json=payload, timeout=5)
                if r.status_code == 200:
                    print(f"[Cortex] ✅ Chat OK at {url}")
                    self.chat_endpoint = url
                    found = True
                    break
                else:
                    print(f"[Cortex] ⚠️ {url} → {r.status_code}")
            except Exception as e:
                print(f"[Cortex] ❌ {url} → {e}")

        if not found:
            print("[Cortex] ❌ No working chat endpoint found; verify model or path.")

        # Embeddings test
        emb_url = f"{self.embed_base}/v1/embeddings"
        try:
            r = requests.get(f"{self.embed_base}/v1/models", timeout=3)
            print(f"[Cortex] ✅ Embeddings online via {self.embed_base} ({len(r.text)}B)")
        except Exception as e:
            print(f"[Cortex] ❌ Embeddings endpoint failed → {e}")

    # ------------------------------------------------------------
    def chat(self, messages, temperature=0.7):
        payload = {"model": self.chat_model, "messages": messages, "temperature": temperature}
        try:
            if "openai.com" in self.chat_base.lower():
                import os
                openai_key = os.getenv("OPENAI_API_KEY")
                if not openai_key:
                    raise ValueError("Missing OPENAI_API_KEY in environment variables.")
                headers = {
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                }
                url = getattr(self, "chat_endpoint", f"{self.chat_base}/v1/chat/completions")

                resp = requests.post(url, headers=headers, json=payload, timeout=30)
            else:
                url = getattr(self, "chat_endpoint", f"{self.chat_base}/v1/chat/completions")

                resp = requests.post(url, json=payload, timeout=30)

            if resp.status_code != 200:
                print(f"[Cortex.chat] Warning: malformed response -> {resp.text}")
                return {"error": resp.text}

            return resp.json()

        except Exception as e:
            print(f"[Cortex.chat] Network error -> {e}")
            return {"error": str(e)}


    # ------------------------------------------------------------
    def embed(self, text: str):
        payload = {
            "model": self.embed_model,
            "input": text,
        }

        try:
            resp = requests.post(
                f"{self.embed_base}/v1/embeddings",  # again, exactly one /v1
                json=payload,
                timeout=30
            )
        except Exception as e:
            print(f"[Cortex.embed] Network error -> {e}")
            print("[Cortex.embed] Falling back to naive local embedding (hash).")
            return self._fallback_embedding(text)

        if resp.status_code != 200:
            print(f"[Cortex.embed] Warning: malformed embedding response -> {resp.text}")
            print("[Cortex.embed] Falling back to naive local embedding (hash).")
            return self._fallback_embedding(text)

        data = resp.json()
        # LM Studio-style usually returns {"data":[{"embedding":[...]}], ...}
        try:
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"[Cortex.embed] Parse fail -> {e}")
            return self._fallback_embedding(text)
        
    import hashlib
    import math

    def _fallback_embedding(self, text: str, dim: int = 256):
        """
        deterministic fake embedding so the rest of the pipeline still works.
        Not semantic, just stable.
        """
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # repeat the hash to fill dim
        raw = (h * ((dim // len(h)) + 1))[:dim]
        # normalize to floats in [-1, 1]
        vec = [((b / 255.0) * 2.0 - 1.0) for b in raw]
        return vec



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
            
        return state, refl, kws

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
            state, reflection, keywords = self._extract_sections(raw_text)
        except Exception as e:
            print(f"[💥 FEEL PARSE ERROR] {e}")
            print(f"[💥 RAW OUTPUT] {raw_text}")
            return None, None

        return state, reflection


    # ------------------------------------------------------------
    def respond(self, user_query, state, reflection, recent_turns, memories):
        """Compose a context-rich prompt integrating emotion, memory, and continuity."""
        short_context = "\n\n".join([
            f"User: {t['user_query']}\nHalcyon: {t['response']}"
            for t in (recent_turns or [])
        ]) or "(no recent turns)"

        memory_context = "\n".join([
            f"- {m.get('text', str(m))[:300]}" for m in (memories or [])[:10]
        ]) or "(no relevant memories retrieved)"

        msg = f"""
    [CONVERSATIONAL CONTINUITY]
    {short_context}

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

    User query: {user_query}
    """
        messages = [{"role": "user", "content": msg}]
        raw = self.chat(messages)

        # --- 🔧 FIX: unwrap OpenAI or LM Studio dicts into pure text ---
        if isinstance(raw, dict):
            try:
                raw_text = raw["choices"][0]["message"]["content"]
            except Exception:
                raw_text = str(raw)
        else:
            raw_text = str(raw)

        return raw_text.strip()
