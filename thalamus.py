import datetime
import json
import os
import re  # Needed for sanitization utility at the end

from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor

DEBUG = True
def dprint(msg: str):
    if DEBUG:
        print(msg, flush=True)

# ============================================================
# Thalamus — Central Orchestrator (with automatic logging)
# ============================================================
class Thalamus:
    def __init__(self, cortex, hippocampus, anchor):
        self.cortex = cortex
        self.hippocampus = hippocampus
        self.anchor = anchor
        self.cortex.hippocampus = hippocampus
        self.cortex.anchor = anchor

        if hasattr(anchor, "hippocampus") and anchor.hippocampus is None:
            anchor.hippocampus = hippocampus
        print("[Thalamus] Anchor attached successfully.")

        self.temporal_anchor = anchor
        print("[Thalamus] TemporalAnchor bound to shared instance.")

        # 🗂️ Setup daily logging directory
        self.log_root = "./runtime_logs"
        os.makedirs(self.log_root, exist_ok=True)
        self._create_daily_dir()

    # ------------------------------------------------------------
    # Logging setup and utility
    # ------------------------------------------------------------
    def _create_daily_dir(self):
        """Create a new dated folder for today's runtime logs."""
        date_dir = datetime.date.today().isoformat()
        self.current_log_dir = os.path.join(self.log_root, date_dir)
        os.makedirs(self.current_log_dir, exist_ok=True)
        self.current_log_path = os.path.join(self.current_log_dir, "turn_log.jsonl")
        print(f"[Thalamus] Logging active :: {self.current_log_path}")

    def log_turn(self, turn_data: dict):
        """Append the full turn data to the daily JSONL log."""
        try:
            # Ensure fresh directory if day rolled over
            if datetime.date.today().isoformat() not in self.current_log_dir:
                self._create_daily_dir()

            with open(self.current_log_path, "a", encoding="utf-8") as f:
                json.dump(turn_data, f, ensure_ascii=False)
                f.write("\n")
            print(f"[Thalamus] 🧾 Logged turn {turn_data.get('turn_id')} to {self.current_log_path}")
        except Exception as e:
            print(f"[Thalamus] ⚠️ Logging failed: {e}")

    # ------------------------------------------------------------
    # Loop orchestration
    # ------------------------------------------------------------
    def get_attention_window(self, n=None):
        return self.anchor.get_recent(n)

    def process_turn(self, user_query, turn_id, task_id):
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
        if hasattr(self.anchor, "manual_context") and self.anchor.manual_context:
            print(f"[Thalamus] Injecting {len(self.anchor.manual_context)} manual memories.")
            memories.extend(self.anchor.manual_context)

        # Phase 3 — Generate response
        print("[Thalamus] Generating response...")
        recent_turns = self.anchor.get_recent(n=7)
        response_text = self.cortex.respond(
            user_query=user_query,
            state=state,
            reflection=reflection,
            recent_turns=recent_turns,
            memories=memories
        )

        # Extract structural and emotional data
        state_json, reflection_primary, keywords = self.cortex._extract_sections(response_text)
        turn_data = {
            "turn_id": turn_id,
            "task_id": f"TUI_{turn_id}",
            "timestamp": timestamp,
            "user_query": user_query,
            "reflection": reflection_primary or reflection,
            "response": response_text,
            "state": state_json or state or {},
            "keywords": keywords or [],
            "memories_used": len(memories)
        }

        # Optional short-term encode
        if hasattr(self.hippocampus, "encode"):
            self.hippocampus.encode(turn_data)
        else:
            print("[Thalamus] ⚠️ Hippocampus.encode() not found — skipping short-term encode.")

        # Anchor + continuity
        self.anchor.update_anchor(user_query, reflection, response_text, memories)
        self.anchor.clear_recall()
        self.anchor.add_turn(user_query, reflection, response_text, state, keywords, turn_id, task_id)

        # Long-term commit
        if state_json and state_json.get("emotions"):
            self.hippocampus.delayed_commit(
                user_query=user_query,
                reflection=reflection,
                response=response_text,
                state_json=state_json,
                metadata={"turn_id": turn_id, "task_id": task_id}
            )
        else:
            print("[Thalamus] ⚠️ No structured emotional state found; skipping long-term commit.")

        # Log the entire cycle
        self.log_turn(turn_data)

        print(f"[Thalamus] 🪞 Signals bypassed for TUI mode.")
        print(f"--- TURN {turn_id} COMPLETED ---")
        return response_text
