# ============================================================
# hippocampus.py — Halcyon Episodic Memory (v3.1, 32K config)
# ============================================================

import datetime
import json
import time
import uuid
import chromadb
import os

class Hippocampus:
    def __init__(self, cortex):
        self.cortex = cortex
        self.recent_turns = []
        self.recall_window = []
        self.narrative_window = []
        self.last_reflection = {}
        self.last_commit_time = time.time()


        # Use the same memory folder and collection as the web UI
        memory_path = os.path.abspath("./memory_journals/halcyon_persistent")
        os.makedirs(memory_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=memory_path)
        self.coll = self.client.get_collection("episodic_memory")

        print(f"[Hippo.init] Connected to persistent memory at: {memory_path}/episodic_memory")



        # Canonical limits for Gemma-3n 32K
        self.MAX_TURNS = 20
        self.MAX_MEMORIES = 50
        self.NARRATIVE_TOKENS = 1000

    # ---------------------------
    # TURN + NARRATIVE MANAGEMENT
    # ---------------------------

    def get_recent_turns(self, n=None):
        """Return up to the last n turns of immediate context."""
        n = n or self.MAX_TURNS
        return self.recent_turns[-n:]

    def update_narrative(self, user_query, reflection, response, recalled_memories):
        snippet = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": user_query.strip(),
            "reflection": reflection.strip()[:400],
            "response": response.strip()[:400],
        }
        self.narrative_window.append(snippet)
        if len(self.narrative_window) > 10:
            self.narrative_window.pop(0)

        print(f"[Hippo.update_narrative] Appended turn — total narrative items: {len(self.narrative_window)}")
        return f"[Narrative] now {len(self.narrative_window)} segments."

    def get_narrative_summary(self):
        """Compact summary for context blending."""
        if not self.narrative_window:
            return "(narrative empty)"
        summary = "\n".join([
            f"{i+1}. {n['query']} → {n['response'][:150]}"
            for i, n in enumerate(self.narrative_window[-5:])
        ])
        return summary

    # ---------------------------
    # MEMORY CORE
    # ---------------------------

    def recall_with_context(self, query, n_results=None):
        n_results = n_results or self.MAX_MEMORIES
        vec = self.cortex.embed(query)
        results = self.coll.query(
            query_embeddings=[vec],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        memories = []
        now = datetime.datetime.now()

        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            timestamp_str = meta.get("timestamp")
            try:
                ts = datetime.datetime.fromisoformat(timestamp_str)
                age_days = (now - ts).total_seconds() / 86400
                decay = max(0.1, 1 - (age_days / 7.0))  # fades after ~1 week
            except Exception:
                decay = 1.0  # if timestamp missing, assume fresh

            distance = results["distances"][0][i]
            weight = (1.5 - distance) * decay
            memories.append({
                "text": doc,
                "weight": weight,
                "timestamp": timestamp_str,
                "distance": distance,
                "decay": decay
            })

        # Sort and trim to top 10 for context stability
        memories.sort(key=lambda m: m["weight"], reverse=True)
        memories = memories[:10]

        print(f"[Hippo.recall] Retrieved {len(memories)} memories (weighted + decayed).")
        self.recall_window = memories
        return memories


    def clear_recall_window(self):
        self.recall_window.clear()
        print("[Hippo] Cleared recall window after narrative update.")

    # ---------------------------
    # SAVE + COMMIT
    # ---------------------------

    def sustain_context(self, turn_data):
        """Keep a rolling log of short-term context."""
        self.recent_turns.append(turn_data)
        if len(self.recent_turns) > self.MAX_TURNS:
            self.recent_turns.pop(0)

    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        """Commit a dual-perspective memory entry, including keywords + emotions."""
        import uuid, datetime, time
        if time.time() - getattr(self, "last_commit_time", 0) < 3:
            time.sleep(1.5)

        fused_text = (
            f"USER QUERY:\n{user_query.strip()}\n\n"
            f"INTERNAL MONOLOGUE:\n{reflection.strip()}\n\n"
            f"MODEL RESPONSE:\n{response.strip()}"
        )

        embedding = self.cortex.embed(fused_text)

        # === Extract top emotions + keywords ===
        emotions = state_json.get("emotions", [])
        keywords = state_json.get("keywords", [])
        meta = {
            **metadata,
            "timestamp": datetime.datetime.now().isoformat(),
            "memory_type": "dual_perspective",
            "reflection": reflection,
            "summary": f"Fusion of user query + reflection @ {metadata.get('turn_id')}",
        }

        # Add top-3 emotion tags
        for i, e in enumerate(emotions[:3]):
            meta[f"emo_{i+1}_name"] = e.get("name")
            meta[f"emo_{i+1}_intensity"] = e.get("intensity")

        # Add keyword tags (up to 10)
        for i, kw in enumerate(keywords[:10]):
            meta[f"keyword_{i+1}"] = kw

        self.coll.add(
            ids=[str(uuid.uuid4())],
            documents=[fused_text],
            embeddings=[embedding],
            metadatas=[meta]
        )

        self.last_commit_time = time.time()
        print(f"[Hippo.encode] Saved dual-perspective memory with metadata: {meta}")


    def store_raw_reflection(self, turn_id, state, reflection):
        """Keep latest reflection for UI display or debugging."""
        self.last_reflection = {
            "turn_id": turn_id,
            "state": state,
            "reflection": reflection
        }
        print(f"[Hippo] Stored raw reflection for turn {turn_id}")
