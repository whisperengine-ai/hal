import os
import threading
import datetime
import json

class TemporalAnchor:
    def __init__(self, hippocampus=None, working_limit=10, anchor_limit=7):
        self.hippocampus = hippocampus
        self.lock = threading.Lock()
        self.working_window = []
        self.anchor_window = []
        self.recall_cache = []
        self.manual_context = []
        self.curiosity_queue = []
        self.working_limit = working_limit
        self.anchor_limit = anchor_limit
        print(f"[TemporalAnchor] Initialized :: working={working_limit} anchor={anchor_limit}")

    def add_turn(self, user_query, reflection, response, state=None, keywords=None, turn_id=None, task_id=None):
        turn = {
            "turn_id": turn_id,
            "task_id": task_id,
            "user_query": user_query,
            "reflection": reflection,
            "response": response,
            "state": state or {},
            "keywords": keywords or [],
            "timestamp": datetime.datetime.now().isoformat()
        }
        with self.lock:
            self.working_window.append(turn)
            if len(self.working_window) > self.working_limit:
                self.working_window.pop(0)
        print(f"[TemporalAnchor] Turn added :: {len(self.working_window)} tracked")

    def get_recent(self, n=None):
        with self.lock:
            return self.working_window[-(n or self.working_limit):]

    def update_anchor(self, user_query, reflection, response, recalled):
        entry = {
            "query": user_query,
            "reflection": reflection[:400],
            "response": response[:400],
            "linked": [m.get("timestamp") for m in recalled[:5] if isinstance(m, dict)],
            "timestamp": datetime.datetime.now().isoformat()
        }
        with self.lock:
            self.anchor_window.append(entry)
            if len(self.anchor_window) > self.anchor_limit:
                self.anchor_window.pop(0)
        print(f"[TemporalAnchor] Anchor updated :: {len(self.anchor_window)} total")

    def recall(self, query, n_results=10):
        if not self.hippocampus:
            print("[TemporalAnchor] ⚠️ No hippocampus linked; skipping recall.")
            return []
        try:
            results = self.hippocampus.recall_with_context(query, n_results=n_results)
            self.recall_cache = results or []
            print(f"[TemporalAnchor] Recall merged :: {len(self.recall_cache)} entries")
            return self.recall_cache
        except Exception as e:
            print(f"[TemporalAnchor] ❌ Recall failed: {e}")
            self.recall_cache = []
            return []

    def inject_memories(self, memories):
        for mem in memories:
            entry = {
                "query": mem.get("query", ""),
                "reflection": mem.get("reflection", ""),
                "timestamp": mem.get("timestamp", ""),
                "source": "manual_inject"
            }
            self.manual_context.append(entry)
        self.recall_cache += self.manual_context
        print(f"[TemporalAnchor] Injected {len(memories)} memories manually.")

    def add_curiosity_query(self, turn_id, source_reflection, question, reason, source_keywords):
        entry = {
            "turn_id": turn_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "question": question,
            "reason": reason,
            "reflection": source_reflection[:400],
            "keywords": source_keywords
        }
        with self.lock:
            self.curiosity_queue.append(entry)
        print(f"[TemporalAnchor] 🧠 Queued Curiosity: {question[:50]}...")

    def get_curiosity_queue(self):
        with self.lock:
            return list(self.curiosity_queue)

    def clear_curiosity_queue(self, index=None):
        with self.lock:
            if index is None:
                self.curiosity_queue.clear()
                print("[TemporalAnchor] Cleared all curiosity.")
            elif 0 <= index < len(self.curiosity_queue):
                del self.curiosity_queue[index]
                print(f"[TemporalAnchor] Cleared curiosity index {index}.")

    def save(self, path="./memory_journals/anchor.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.anchor_window, f, indent=2)
        print(f"[TemporalAnchor] Anchor saved ({len(self.anchor_window)} entries)")

    def load(self, path="./memory_journals/anchor.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.anchor_window = json.load(f)
            print(f"[TemporalAnchor] Anchor loaded ({len(self.anchor_window)})")
        else:
            print("[TemporalAnchor] No saved anchor found.")

    def build_anchor_frame(self, n_turns=3):
        turns = self.get_recent(n_turns)
        return "\n\n".join([f"User: {t['user_query']}\nHalcyon: {t['response']}" for t in turns])

    def clear_recall(self):
        with self.lock:
            self.recall_cache.clear()
        print("[TemporalAnchor] Recall cache cleared")
