
# ============================================================
# context_window_manager.py — Unified Context Orchestrator
# ============================================================
import threading
import datetime
import json
import os

class ContextWindowManager:
    """
    Consolidates working, recall, and narrative windows into a single orchestrator.
    Manages temporal layers of cognition (short-term, hybrid recall, long-term summary)
    with deterministic lifecycles and explicit access methods.
    """

    def __init__(self, hippocampus=None, working_limit=10, narrative_limit=7):
        self.hippocampus = hippocampus
        self.lock = threading.Lock()

        self.working_window = []    # current conversation turns
        self.recall_cache = []      # combined long-term + working recall (ephemeral per turn)
        self.narrative_window = []  # compact storyline (persisted)
        self.working_limit = int(working_limit)
        self.narrative_limit = int(narrative_limit)

        print(f"[ContextManager] Initialized :: working={working_limit} narrative={narrative_limit}")

    # -------------------------
    # WORKING CONTEXT
    # -------------------------
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
        print(f"[ContextManager] Turn added :: {len(self.working_window)} turns tracked")

    def get_recent(self, n=None):
        with self.lock:
            return self.working_window[-(n or self.working_limit):]

    def get_focus(self):
        with self.lock:
            return self.working_window[-1] if self.working_window else None

    # -------------------------
    # HYBRID RECALL
    # -------------------------
    def recall(self, query, n_results=25):
        """Fuse short-term context with hippocampal semantic recall."""
        long_term = self.hippocampus.recall_with_context(query, n_results) if self.hippocampus else []
        with self.lock:
            live = list(self.working_window)
            self.recall_cache = list(long_term)

        merged = [
            {"text": f"[Recent] {t['user_query']} → {t['response']}", "meta": {"src": "working", "timestamp": t["timestamp"]}, "weight": 1.5}
            for t in live
        ] + long_term
        merged.sort(key=lambda x: x.get("weight", 0.0), reverse=True)
        print(f"[ContextManager] Recall merged :: {len(merged)} entries")
        return merged

    def clear_recall(self):
        with self.lock:
            self.recall_cache.clear()
        print("[ContextManager] Recall cache cleared")

    # -------------------------
    # NARRATIVE
    # -------------------------
    def update_narrative(self, user_query, reflection, response, recalled):
        entry = {
            "query": user_query,
            "reflection": (reflection or "")[:400],
            "response": (response or "")[:400],
            "linked": [ (m.get('meta') or {}).get('timestamp') for m in (recalled or [])[:5] ],
            "timestamp": datetime.datetime.now().isoformat()
        }
        with self.lock:
            self.narrative_window.append(entry)
            if len(self.narrative_window) > self.narrative_limit:
                self.narrative_window.pop(0)
        print(f"[ContextManager] Narrative updated ({len(self.narrative_window)} entries)")

    def summarize(self):
        with self.lock:
            if not self.narrative_window:
                return "(no narrative yet)"
            summary_lines = []
            for i, n in enumerate(self.narrative_window):
                resp = (n.get("response") or "").replace("\n", " ")[:160]
                summary_lines.append(f"{i+1}. {n.get('query', '')} → {resp}")
            return "\n".join(summary_lines)


    def get_narrative_window(self):
        with self.lock:
            return list(self.narrative_window)

    # -------------------------
    # PERSISTENCE
    # -------------------------
    def save(self, path="./memory_journals/narrative.json"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.narrative_window, f, indent=2)
        print(f"[ContextManager] Narrative saved ({len(self.narrative_window)})")

    def load(self, path="./memory_journals/narrative.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.narrative_window = json.load(f)
            print(f"[ContextManager] Narrative loaded ({len(self.narrative_window)})")
        else:
            self.narrative_window = []
            print("[ContextManager] No prior narrative found; fresh start.")
