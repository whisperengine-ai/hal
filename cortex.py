# ============================================================
# Cortex — Cognitive Reflection and Response Engine (Final Clean)
# ============================================================

import json, time, requests
import datetime
import re
# Imports all static prompts and state lists for clean code
from halcyon_prompts import SYSTEM_PROMPT, STRICT_OUTPUT_EXAMPLE, EMOTIVE_STATES, COGNITIVE_STATES, MEMORY_RECALL_INSTRUCTION, FINAL_RESPONSE_INSTRUCTION

class Cortex:
    """Handles emotional reasoning, reflection, and context-grounded response generation."""

    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or "http://192.168.1.70:1234"
        self.model = model or "google/gemma-3n-e4b"
        
        # References injected by Thalamus at runtime
        self.hippocampus = None
        self.anchor = None 

        # Assign system prompt from the external file
        self.system_prompt = SYSTEM_PROMPT 

    # ------------------------------------------------------------
    def chat(self, messages, temperature=0.7):
        """Sends structured prompt payloads to local model endpoint."""
        try:
            payload = {
                "model": self.model,
                "temperature": temperature,
                "messages": [{"role": "system", "content": self.system_prompt}] + messages
            }
            r = requests.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=90)
            r.raise_for_status()
            data = r.json()
            if "choices" not in data or not data["choices"]:
                print("[Cortex.chat] Warning: malformed response ->", data)
                return "(no content)"
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[Cortex.chat] Error: {e}")
            return f"(error: {e})"

    # ------------------------------------------------------------
    def embed(self, text, model="text-embedding-nomic-embed-text-v1.5"):
        """Generate embeddings for recall and associative memory."""
        try:
            url = f"{self.base_url}/v1/embeddings"
            payload = {"model": model, "input": text}
            r = requests.post(url, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            if "data" in data and data["data"]:
                vec = data["data"][0].get("embedding")
                return vec
            print(f"[Cortex.embed] Warning: malformed embedding response -> {data.get('error','no data')}")
            return [0.0] * 768
        except Exception as e:
            print(f"[Cortex.embed] Error: {e}")
            return [0.0] * 768

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
        # 💡 CLEANUP/FIX: Injecting the required prompt structure from the external file.
        msg = (
            f"{MEMORY_RECALL_INSTRUCTION}\n\n"
            f"***VALID EMOTIVE STATES***: {', '.join(EMOTIVE_STATES)}\n"
            f"***VALID COGNITIVE STATES***: {', '.join(COGNITIVE_STATES)}\n\n"
            f"Time: {timestamp}\nTurn: {turn_id}\nUser: {user_query}"
        )

        raw = self.chat([{"role": "user", "content": msg}], temperature=0.6)

        print(f"[Cortex] self.chat = {getattr(self.chat, '__name__', type(self.chat))}")
        print(f"[Cortex.feel_and_reflect] Raw output:\n{raw}\n--- End of raw output ---")
        try:
            state, reflection, keywords = self._extract_sections(raw)
        except Exception as e:
            print(f"[💥 FEEL PARSE ERROR] {e}")
            print(f"[💥 RAW OUTPUT] {raw}")
            return None, None

        return state, reflection

    # ------------------------------------------------------------
    def respond(self, user_query, state, reflection, recent_turns, memories):
        """Compose a context-rich prompt integrating emotion, memory, and continuity."""

        # === Step 1: Short-term continuity from working turns ===
        short_context = "\n\n".join([
            f"User: {t['user_query']}\nHalcyon: {t['response']}"
            for t in (recent_turns or [])
        ]) or "(no recent turns)"

        # === Step 2: Summarize memory recall ===
        memory_context = "\n".join([
            f"- {m.get('text', str(m))[:300]}" for m in (memories or [])[:10]
        ]) or "(no relevant memories retrieved)"


        # === Step 3: Full prompt construction ===
        # 💡 CLEANUP/FIX: Injecting the required prompt structure from the external file.
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
        raw = self.chat(messages, temperature=0.7)
        return raw.strip()