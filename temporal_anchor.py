import os
import threading
import datetime
import json

class TemporalAnchor:
    """
    Holds the short-term turns, manages recall fusion, and stabilizes the immediate cognitive field.
    Replaces ContextWindowManager.
    """
    def __init__(self, hippocampus=None, working_limit=10, anchor_limit=7):
        self.hippocampus = hippocampus
        self.lock = threading.Lock()
        self.working_window = []
        self.recall_cache = []
        self.anchor_window = []
        self.working_limit = int(working_limit)
        self.anchor_limit = int(anchor_limit)
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
        print(f"[TemporalAnchor] Turn added :: {len(self.working_window)} turns tracked")

    def get_recent(self, n=None):
        with self.lock:
            return self.working_window[-(n or self.working_limit):]

    def recall(self, query, n_results=25):
        long_term = self.hippocampus.recall_with_context(query, n_results) if self.hippocampus else []
        with self.lock:
            live = list(self.working_window)
            self.recall_cache = list(long_term)
        merged = [{"text": f"[Recent] {t['user_query']} → {t['response']}", "meta": {"src": "working"}, "weight": 1.5} for t in live] + long_term
        merged.sort(key=lambda x: x.get("weight", 0.0), reverse=True)
        print(f"[TemporalAnchor] Recall merged :: {len(merged)} entries")
        return merged

    def update_anchor(self, user_query, reflection, response, recalled):
        entry = {
            "query": user_query,
            "reflection": (reflection or "")[:400],
            "response": (response or "")[:400],
            "linked": [(m.get("meta") or {}).get("timestamp") for m in (recalled or [])[:5]],
            "timestamp": datetime.datetime.now().isoformat()
        }
        with self.lock:
            self.anchor_window.append(entry)
            if len(self.anchor_window) > self.anchor_limit:
                self.anchor_window.pop(0)
        print(f"[TemporalAnchor] Anchor updated ({len(self.anchor_window)} entries)")

    def build_anchor_frame(self, n_turns=3):
        """Return a text block of recent user/AI exchanges."""
        turns = self.get_recent(n_turns)
        return "\n\n".join([f"User: {t['user_query']}\nHalcyon: {t['response']}" for t in turns])

    def clear_recall(self):
        with self.lock:
            self.recall_cache.clear()
        print("[TemporalAnchor] Recall cache cleared")

    def load(self, path="./memory_journals/anchor.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.anchor_window = json.load(f)
            print(f"[TemporalAnchor] Anchor loaded ({len(self.anchor_window)})")
        else:
            self.anchor_window = []
            print("[TemporalAnchor] No prior anchor found; fresh start.")

    def save(self, path="./memory_journals/anchor.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.anchor_window, f, indent=2)

    def inject_memories(self, memories: list):
        """
        Manually push selected memories into the current conversational anchor.
        Each item should be a dict with at least {'query': str, 'reflection': str, 'timestamp': str}.
        """
        if not hasattr(self, "manual_context"):
            self.manual_context = []

        for mem in memories:
            entry = {
                "query": mem.get("query", ""),
                "reflection": mem.get("reflection", ""),
                "timestamp": mem.get("timestamp", ""),
                "source": "manual_inject"
            }
            self.manual_context.append(entry)
            print(f"[TemporalAnchor] Injected manual memory: {entry['timestamp']} — {entry['query'][:50]}...")

        # Optionally preload this into the active recall window
        self.recall_cache = (self.recall_cache or []) + self.manual_context
        print(f"[TemporalAnchor] Total manual memories injected: {len(self.manual_context)}")
