import datetime
import json
from urllib import response
import requests
from llama_index.core import Settings

from halcyon_ui import SignalBus
from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor
from signal_bus import SignalBus

DEBUG = True
def dprint(msg: str):
    if DEBUG:
        print(msg, flush=True)

# ============================================================
# Thalamus
# ============================================================
class Thalamus:
    def __init__(self, cortex, hippocampus, anchor, bus=None):
        self.cortex = cortex
        self.hippocampus = hippocampus
        self.anchor = anchor
        self.cortex.hippocampus = hippocampus
        self.cortex.anchor = anchor  # keep reference symmetry

        # Anchor binding
        if hasattr(anchor, "hippocampus") and anchor.hippocampus is None:
            anchor.hippocampus = hippocampus
        print("[Thalamus] Anchor attached successfully.")

        # Signal bus setup
        self.bus = bus or SignalBus()
        print("[Thalamus] Signal bus ready.")

        # Bind existing temporal anchor (don’t recreate)
        self.temporal_anchor = anchor
        print("[Thalamus] TemporalAnchor bound to shared instance.")

    def bind_temporal_anchor(self, anchor_ref):
        """Attach or rebind a live TemporalAnchor reference."""
        self.temporal_anchor = anchor_ref
        print("[Thalamus] Bound external TemporalAnchor reference.")


    def get_attention_window(self, n=None):
        """Expose recent working turns for inspectors."""
        return self.anchor.get_recent(n)

    def process_turn(self, user_query, turn_id, task_id):
        import datetime
        from signal_bus import SignalBus

        timestamp = datetime.datetime.now().isoformat()
        print(f"--- TURN {turn_id} INITIATED ---")
        print(f"[Thalamus] user_query={user_query!r}")

        # Phase 1 — Internal emotional initialization
        state, reflection = self.cortex.feel_and_reflect(user_query, turn_id, timestamp)
        if state is None or reflection is None:
            print("[Thalamus] ⚠️ Reflection phase failed — halting turn to preserve integrity.")
            return "(reflection phase failed)"

        # Phase 2 — Hybrid recall through TemporalAnchor
        print("[Thalamus] Recalling memories (hybrid)...")
        memories = self.anchor.recall(user_query, n_results=25)

        # Merge injected memories
        if hasattr(self.anchor, "manual_context") and self.anchor.manual_context:
            print(f"[Thalamus] Injecting {len(self.anchor.manual_context)} manual memories into recall context.")
            memories.extend(self.anchor.manual_context)

        # Phase 3 — Generate response using recent working turns
        print("[Thalamus] Generating response...")
        recent_turns = self.anchor.get_recent(n=7)
        response_text = self.cortex.respond(
            user_query=user_query,
            state=state,
            reflection=reflection,
            recent_turns=recent_turns,
            memories=memories
        )

        # Extract emotional and structural data
        state_json, reflection_primary, keywords = self.cortex._extract_sections(response_text)

        # Build turn metadata
        turn_data = {
            "turn_id": turn_id,
            "task_id": f"WEB_UI_{turn_id}",
            "reflection": reflection_primary or reflection,
            "response": response_text,
            "state": state_json or state or {},
            "weight": 1.0,
        }

        # Optional: short-term encode, if implemented
        if hasattr(self.hippocampus, "encode"):
            self.hippocampus.encode(turn_data)
        else:
            print("[Thalamus] ⚠️ Hippocampus.encode() not found — skipping short-term encode.")

        # Phase 4 — Commit to anchors + short-term continuity
        self.anchor.update_anchor(user_query, reflection, response_text, memories)
        self.anchor.clear_recall()
        self.anchor.add_turn(
            user_query=user_query,
            reflection=reflection,
            response=response_text,
            state=state,
            keywords=keywords or [],
            turn_id=turn_id,
            task_id=task_id
        )

        # Phase 4b — Integrity-protected long-term commit
        if state_json and state_json.get("emotions"):
            self.hippocampus.delayed_commit(
                user_query=user_query,
                reflection=reflection,
                response=response_text,
                state_json=state_json,
                metadata={"turn_id": turn_id, "task_id": task_id}
            )
        else:
            print("[Thalamus] ⚠️ No structured emotional state found; skipping long-term commit to preserve memory integrity.")

        # Phase 5 — Emit reflection and attention events
        try:
            reflection_payload = {
                "turn_id": turn_id,
                "timestamp": timestamp,
                "state": state_json or state or {},
                "reflection": reflection_primary or reflection,
                "response": response_text,
                "keywords": keywords or [],
            }
            self.bus.reflection_update.emit(reflection_payload)
            print(f"[Thalamus] 🪞 Emitted reflection_update for turn {turn_id}")

            self.bus.attention_update.emit({
                "turn_id": turn_id,
                "reflection": reflection,
                "response": response_text,
                "state": state_json or state
            })
            print(f"[Thalamus] 🩸 Emitted attention_update for turn {turn_id}")

            self.bus.memory_update.emit({
                "timestamp": timestamp,
                "query": user_query,
                "reflection": reflection,
                "response": response_text
            })
            print(f"[Thalamus] 🧠 Emitted memory_update for turn {turn_id}")

        except Exception as e:
            print(f"[Thalamus] ❌ SSE emission failed: {e}")
        print(f"--- TURN {turn_id} COMPLETED ---")  
        return response_text

# ============================================================
# SSE Sanitization Utilities
import re
import json


def sanitize_sse_data(data):
    """Sanitize data for Server-Sent Events (SSE) transmission."""
    if not isinstance(data, str):
        data = json.dumps(data)
    # Remove control characters that are not allowed in SSE
    data = re.sub(r"[\x00-\x1F\x7F]", "", data)
    return data