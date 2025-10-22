# ============================================================
# attention.py — Halcyon Working & Hybrid Recall Buffer
# ============================================================

import threading
import datetime
import os
import json

class Attention:
    """Manages layered short-term cognition: working, recall, and narrative windows."""

    def __init__(self, hippocampus=None, working_limit=10, narrative_limit=7):
        # Reference to long-term memory (Hippocampus) for hybrid recall
        self.hippocampus = hippocampus
        self._lock = threading.Lock()

        # Short-term layers
        self._working_buffer = []      # immediate conversation context (turn snapshots)
        self._recall_window = []       # ephemeral recalled memories (clears per turn)
        self._narrative_window = []    # rolling storyline buffer (few recent turns persisted)

        # Parameters
        self.working_limit = int(working_limit)
        self.narrative_limit = int(narrative_limit)

        print(f"[Attention] Initialized: working={self.working_limit}, narrative={self.narrative_limit}")

    # ---------------------------
    # Working Memory
    # ---------------------------
    def push_turn(self, user_query, reflection, response, state=None, keywords=None, turn_id=None, task_id=None):
        with self._lock:
            self._working_buffer.append({
                "turn_id": turn_id,
                "task_id": task_id,
                "user_query": user_query,
                "reflection": reflection,
                "response": response,
                "state": state or {},
                "keywords": keywords or [],
                "timestamp": datetime.datetime.now().isoformat(),
            })
            if len(self._working_buffer) > self.working_limit:
                self._working_buffer.pop(0)
        print(f"[Attention] Working buffer updated: {len(self._working_buffer)} turns stored.")

    def sustain_context(self, payload: dict):
        """Hook for Thalamus to update live working memory."""
        try:
            self.push_turn(
                user_query=payload.get("user_query", ""),
                reflection=payload.get("reflection", ""),
                response=payload.get("response", ""),
                state=payload.get("state") or {},
                keywords=payload.get("keywords") or [],
                turn_id=payload.get("turn_id"),
                task_id=payload.get("task_id"),
            )
        except Exception as e:
            print(f"[Attention.sustain_context] Error: {e}")

    def get_recent_turns(self, n=None):
        with self._lock:
            buf = list(self._working_buffer)
        return buf[-(n or self.working_limit):]

    def get_focus(self):
        with self._lock:
            return self._working_buffer[-1] if self._working_buffer else None

    # ---------------------------
    # Hybrid Recall (Working + Episodic)
    # ---------------------------
    def recall_with_context(self, query, n_results=25):
        print("[Attention] Performing hybrid recall...")
        long_term = []
        if self.hippocampus:
            long_term = self.hippocampus.recall_with_context(query=query, n_results=n_results)

        with self._lock:
            live = list(self._working_buffer)
            self._recall_window = list(long_term)

        merged = []
        for item in live:
            merged.append({
                "text": f"[Live Context] {item['user_query']} → {item['response']}",
                "meta": {"timestamp": item["timestamp"], "source": "working_buffer"},
                "weight": 1.5
            })
        merged.extend(long_term)
        merged.sort(key=lambda x: x.get("weight", 0.0), reverse=True)

        print(f"[Attention] Hybrid recall returned {len(merged)} combined items.")
        return merged

    def clear_recall_window(self):
        with self._lock:
            self._recall_window = []
        print("[Attention] Cleared recall window.")

    # ---------------------------
    # Narrative Thread
    # ---------------------------
    def update_narrative(self, user_query, reflection, response, recalled_memories=None):
        entry = {
            "query": user_query,
            "reflection": (reflection or "")[:400],
            "response": (response or "")[:400],
            "linked_memories": [
                (m.get('meta') or {}).get('timestamp') for m in (recalled_memories or [])[:5]
            ],
            "timestamp": datetime.datetime.now().isoformat(),
        }
        with self._lock:
            self._narrative_window.append(entry)
            if len(self._narrative_window) > self.narrative_limit:
                self._narrative_window.pop(0)
        print(f"[Attention] Narrative window updated ({len(self._narrative_window)} entries).")
        return "[Attention.update_narrative] OK"

    def get_narrative_summary(self):
        with self._lock:
            if not self._narrative_window:
                return "(no narrative yet)"
            summary = []
            for i, n in enumerate(self._narrative_window):
                snippet = (n.get('response') or '')[:160].replace("\n", " ")
                summary.append(f"{i+1}. {n.get('query','')} → {snippet}")
            return "\n".join(summary)

    def get_narrative_window(self):
        with self._lock:
            return list(self._narrative_window)

# ============================================================
# 💾 Narrative Persistence (load/save across restarts)
# ============================================================

    def save_narrative(self, path="./memory_journals/narrative_window.json"):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._narrative_window, f, indent=2)
            print(f"[Attention] Saved narrative ({len(self._narrative_window)} entries).")
        except Exception as e:
            print(f"[Attention.save_narrative] Error: {e}")

    def load_narrative(self, path="./memory_journals/narrative_window.json"):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self._narrative_window = json.load(f)
                print(f"[Attention] Loaded narrative ({len(self._narrative_window)} entries).")
            else:
                self._narrative_window = []
                print("[Attention] No prior narrative found — starting fresh.")
        except Exception as e:
            print(f"[Attention.load_narrative] Error: {e}")
            self._narrative_window = []

    def get_context(self, window_size: int = 10):
        """
        Retrieve the recent turn context for narrative continuity.
        Returns a list of the most recent 'window_size' stored turns
        from the working buffer or sustained context.
        """
        if hasattr(self, "working_buffer") and self.working_buffer:
            recent = self.working_buffer[-window_size:]
            print(f"[Attention] Returning {len(recent)} recent turns from working buffer.")
            return recent
        elif hasattr(self, "context_window") and self.context_window:
            recent = self.context_window[-window_size:]
            print(f"[Attention] Returning {len(recent)} recent turns from context_window.")
            return recent
        else:
            print("[Attention] No recent context found; returning empty list.")
            return []

