import datetime
import json
import os

from hippocampus import Hippocampus  # TemporalAnchor gone

DEBUG = True
def dprint(msg: str):
    if DEBUG:
        print(msg, flush=True)

# ============================================================
# Thalamus — Central Orchestrator (Anchorless Version)
# ============================================================
class Thalamus:
    def __init__(self, cortex, hippocampus):
        self.cortex = cortex
        self.hippocampus = hippocampus
        self.cortex.hippocampus = hippocampus

        print("[Thalamus] Hippocampus + Cortex bound.")

        self.log_root = "./runtime_logs"
        os.makedirs(self.log_root, exist_ok=True)
        self._create_daily_dir()

    def _create_daily_dir(self):
        date_dir = datetime.date.today().isoformat()
        self.current_log_dir = os.path.join(self.log_root, date_dir)
        os.makedirs(self.current_log_dir, exist_ok=True)
        self.current_log_path = os.path.join(self.current_log_dir, "turn_log.jsonl")
        print(f"[Thalamus] Logging active :: {self.current_log_path}")

    def log_turn(self, turn_data: dict):
        try:
            if datetime.date.today().isoformat() not in self.current_log_dir:
                self._create_daily_dir()
            with open(self.current_log_path, "a", encoding="utf-8") as f:
                json.dump(turn_data, f, ensure_ascii=False)
                f.write("\n")
            print(f"[Thalamus] 🧾 Logged turn {turn_data.get('turn_id')}")
        except Exception as e:
            print(f"[Thalamus] ⚠️ Logging failed: {e}")

    def process_turn(self, user_query, turn_id, task_id):
        timestamp = datetime.datetime.now().isoformat()
        print(f"--- TURN {turn_id} INITIATED ---")
        print(f"[Thalamus] user_query={user_query!r}")
        
        # Clear embedding cache at the start of each turn
        self.cortex.clear_embedding_cache()

        try:
            result = self.cortex.feel_and_reflect(user_query, turn_id, timestamp)
            state, reflection, keywords, questions = (result + ([], {}))[:4]
        except Exception as e:
            print(f"[Thalamus] ⚠️ Reflection phase crashed: {e}")
            return "(reflection phase failed)"

        print("[Thalamus] Recalling memories...")
        memories = self.hippocampus.recall_with_context(user_query, n_results=25)

        print("[Thalamus] Fetching recent turns...")
        recent_turns = self.hippocampus.get_recent_turns(n=3)  # New assumption

        print("[Thalamus] Generating response...")
        response_data = self.cortex.respond(
            user_query=user_query,
            state=state,
            reflection=reflection,
            recent_turns=recent_turns,
            memories=memories
        )

        response_text = response_data.get("raw", "")
        state = response_data.get("state", state)
        reflection = response_data.get("reflection", reflection)
        keywords = response_data.get("keywords", [])
        questions = response_data.get("questions", {})

        turn_data = {
            "turn_id": turn_id,
            "task_id": f"TUI_{turn_id}",
            "timestamp": timestamp,
            "user_query": user_query,
            "reflection": reflection,
            "response": response_text,
            "state": state or {},
            "keywords": keywords or [],
            "memories_used": len(memories)
        }

        self.log_turn(turn_data)

        try:
            self.hippocampus.delayed_commit(
                user_query=user_query,
                reflection=reflection,
                response=response_text,
                state_json=state,
                metadata={
                    "turn_id": turn_id,
                    "task_id": task_id,
                    "keywords": keywords or [],
                },
            )
        except Exception as e:
            print(f"[Thalamus] ⚠️ Memory commit failed: {e}")

        print(f"--- TURN {turn_id} COMPLETED ---\n")
        return state, reflection, response_text
# ============================================================