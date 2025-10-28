# ============================================================
# Cortex — Cognitive Reflection and Response Engine (OpenAI Only)
# ============================================================

import os, json, time, requests, datetime, re
from halcyon_prompts import (
    SYSTEM_PROMPT,
    STRICT_OUTPUT_EXAMPLE,
    EMOTIVE_STATES,
    COGNITIVE_STATES,
    MEMORY_RECALL_INSTRUCTION,
    FINAL_RESPONSE_INSTRUCTION,
    QUESTION_INSTRUCTION
)

class Cortex:
    def __init__(self,
                 chat_base="https://api.openai.com/v1",
                 embed_base="https://api.openai.com/v1",
                 chat_model="gpt-4o-mini",
                 embed_model="text-embedding-3-large"):
        self.chat_base = chat_base.rstrip("/")
        self.embed_base = embed_base.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model

        # Runtime references injected later
        self.hippocampus = None
        self.anchor = None

        # Static system prompt
        self.system_prompt = SYSTEM_PROMPT

        print("[Cortex] Initializing runtime interfaces...")
        self._verify_endpoints()

    # ------------------------------------------------------------
    # Endpoint Verification
    # ------------------------------------------------------------
    def _verify_endpoints(self):
        """Simple ping check for chat and embedding endpoints."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise EnvironmentError("OPENAI_API_KEY missing from environment.")

        chat_url = f"{self.chat_base}/chat/completions"
        embed_url = f"{self.embed_base}/embeddings"

        print(f"[Cortex] 🔍 Probing chat endpoint: {chat_url}")
        try:
            payload = {
                "model": self.chat_model,
                "messages": [{"role": "user", "content": "ping"}],
                "temperature": 0.0
            }
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            r = requests.post(chat_url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[Cortex] ✅ Chat endpoint confirmed at {chat_url}")
                self.chat_endpoint = chat_url
            else:
                print(f"[Cortex] ⚠️ Chat check failed → {r.status_code}")
        except Exception as e:
            print(f"[Cortex] ❌ Chat probe failed → {e}")

        print(f"[Cortex] 🔍 Probing embedding endpoint: {embed_url}")
        try:
            payload = {"model": self.embed_model, "input": "ping"}
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            r = requests.post(embed_url, headers=headers, json=payload, timeout=5)
            if r.status_code == 200:
                print(f"[Cortex] ✅ Embeddings active at {embed_url}")
            else:
                print(f"[Cortex] ⚠️ Embedding check failed → {r.status_code}")
        except Exception as e:
            print(f"[Cortex] ❌ Embedding probe failed → {e}")

    # ------------------------------------------------------------
    # Chat Generation
    # ------------------------------------------------------------
    def chat(self, messages, temperature=0.7):
        """Send conversation messages to the OpenAI chat model."""
        url = getattr(self, "chat_endpoint", f"{self.chat_base}/chat/completions")
        openai_key = os.getenv("OPENAI_API_KEY")
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        payload = {"model": self.chat_model, "messages": messages, "temperature": temperature}

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                print(f"[Cortex.chat] ⚠️ {resp.status_code} → {resp.text}")
                return {"error": resp.text}
            return resp.json()
        except Exception as e:
            print(f"[Cortex.chat] ❌ Network error → {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------
    # Embeddings (OpenAI Only)
    # ------------------------------------------------------------
    def embed(self, text: str):
        """Generate embeddings using OpenAI's official endpoint."""
        openai_key = os.getenv("OPENAI_API_KEY")
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        payload = {"model": self.embed_model, "input": text}

        try:
            resp = requests.post(f"{self.embed_base}/embeddings", headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                raise RuntimeError(f"Embedding error: {resp.text}")
            return resp.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"[Cortex.embed] ❌ Embedding request failed → {e}")
            raise

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

User query: {user_query} PLEASE RESPOND ACCORDINGLY. IF YOU DO NOT UNDERSTAND, STATE WHAT ADDITIONAL INFORMATION YOU NEED
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

