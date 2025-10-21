# ============================================================
# attention.py — Hybrid Cognitive Buffer (Working + Recall + Narrative)
# ============================================================

import threading
import datetime
from hippocampus import Hippocampus

class Attention(Hippocampus):
    """Manages layered short-term cognition: working, recall, and narrative windows."""

    def __init__(self, cortex, working_limit=10, narrative_limit=7):
        super().__init__(cortex)
        self._lock = threading.Lock()

        # --- Core short-term layers ---
        self._working_buffer = []      # immediate conversation context
        self._recall_window = []       # ephemeral recalled memories (clears each turn)
        self._narrative_window = []    # rolling storyline buffer (persists few turns)

        # --- Parameters ---
        self.working_limit = int(working_limit)
        self.narrative_limit = int(narrative_limit)

        print(f"[Attention] Initialized: working={self.working_limit}, narrative={self.narrative_limit}")

    # ============================================================
    # 🧩 Working Memory Buffer
    # ============================================================

    def push_turn(self, user_query, reflection, response):
        with self._lock:
            self._working_buffer.append({
                "user_query": user_query,
                "reflection": reflection,
                "response": response,
                "timestamp": datetime.datetime.now().isoformat()
            })
            if len(self._working_buffer) > self.working_limit:
                self._working_buffer.pop(0)
        print(f"[Attention] Working buffer updated: {len(self._working_buffer)} turns stored.")

    def get_context(self):
        with self._lock:
            return "\n".join([
                f"[{i+1}] Q: {t['user_query']}\nA: {t['response']}"
                for i, t in enumerate(self._working_buffer)
            ])

    # Hook used by Thalamus to keep short-form turn in working memory
    def sustain_context(self, payload: dict):
        try:
            self.push_turn(
                user_query=payload.get("user_query", ""),
                reflection=payload.get("reflection", ""),
                response=payload.get("response", "")
            )
        except Exception as e:
            print(f"[Attention.sustain_context] Error: {e}")

    # ============================================================
    # 🔍 Hybrid Recall (Working + Episodic)
    # ============================================================

    def recall_with_context(self, query, n_results=25):
        print("[Attention] Performing hybrid recall...")
        long_term = super().recall(query=query, n_results=n_results, top_k=15)
        with self._lock:
            live = list(self._working_buffer)
            self._recall_window = long_term[:]

        merged = []
        for item in live:
            merged.append({
                "text": f"[Live Context] {item['user_query']} → {item['response']}",
                "meta": {"timestamp": item["timestamp"], "source": "working_buffer"},
                "weight": 1.5
            })
        merged.extend(long_term)
        merged.sort(key=lambda x: x["weight"], reverse=True)

        print(f"[Attention] Hybrid recall returned {len(merged)} combined items.")
        return merged

    # ============================================================
    # 🧠 Narrative Integration Layer
    # ============================================================

    def update_narrative(self, user_query, reflection, response, recalled_memories=None):
        entry = {
            "query": user_query,
            "reflection": reflection,
            "response": response,
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

    def clear_recall_window(self):
        with self._lock:
            self._recall_window = []
        print("[Attention] Cleared recall window.")

    # ============================================================
    # 🗄️ Delayed Commit (delegates to base for now)
    # ============================================================

    def delayed_commit(self, user_query, reflection, response, state_json, metadata=None):
        """Expose the same API the Thalamus calls; defers to base encode for now."""
        return super().delayed_commit(user_query, reflection, response, state_json, metadata)
