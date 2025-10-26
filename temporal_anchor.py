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
        self.anchor_context = []
        self.manual_injections = []
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

    def recall(self, query, n_results=10):
        """Retrieve recent or relevant memories from Hippocampus."""
        try:
            if not hasattr(self, "hippocampus") or self.hippocampus is None:
                print("[TemporalAnchor] ⚠️ No hippocampus linked; skipping recall.")
                return []

            results = self.hippocampus.recall_with_context(query, n_results=n_results)
            self.recall_cache = results or []
            print(f"[TemporalAnchor] Recall merged :: {len(self.recall_cache)} entries")
            return self.recall_cache

        except Exception as e:
            print(f"[TemporalAnchor] ❌ Recall failed: {e}")
            self.recall_cache = []
            return []

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

    def dump_current(self):
        """Return both active anchor memories and manual injections."""
        all_items = []
        if hasattr(self, "anchor_context"):
            all_items.extend(self.anchor_context)
        if hasattr(self, "manual_injections"):
            all_items.extend(self.manual_injections)

        entries = []
        for m in all_items:
            entries.append({
                "id": m.get("id", ""),
                "timestamp": m.get("timestamp", ""),
                "text": (m.get("text", "")[:120] + "...") if m.get("text") else "",
                "weight": m.get("weight", 1.0),
                "pinned": m.get("pinned", False),
                "dream_promoted": m.get("dream_promoted", False),
                "emotions": m.get("emotions", []),
                "keywords": m.get("keywords", []),
            })
        print(f"[TemporalAnchor] Dumped {len(entries)} anchor + injected memories.")
        return entries

temporal_anchor = TemporalAnchor()