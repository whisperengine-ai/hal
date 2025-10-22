# ============================================================
# hippocampus.py — Halcyon Episodic Memory Core (v3.2)
# ============================================================

import datetime
import time
import uuid
import os
import chromadb

class Hippocampus:
    def __init__(self, cortex):
        self.cortex = cortex
        self.last_commit_time = 0

        memory_path = os.path.abspath("./memory_journals/halcyon_persistent")
        os.makedirs(memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=memory_path)
        self.coll = self.client.get_collection("episodic_memory")

        print(f"[Hippo.init] Connected to persistent memory at: {memory_path}/episodic_memory")

    # ---------------------------
    # Recall
    # ---------------------------
    def recall_with_context(self, query, n_results=None):
        """Retrieve semantically relevant memories and print readable diagnostics."""
        import datetime

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
            id_ = results["ids"][0][i]  # 🧠 added this line

            timestamp_str = meta.get("timestamp")
            try:
                ts = datetime.datetime.fromisoformat(timestamp_str)
                age_days = (now - ts).total_seconds() / 86400
                decay = max(0.1, 1 - (age_days / 7.0))  # fades after ~1 week
            except Exception:
                decay = 1.0

            distance = results["distances"][0][i]
            weight = (1.5 - distance) * decay
            snippet = doc[:120].replace("\n", " ").replace("\r", " ")

            # Reinforcement: if a memory is retrieved, strengthen its decay factor and record access
            if meta.get("rehearsal_count") is None:
                meta["rehearsal_count"] = 1
            else:
                meta["rehearsal_count"] += 1

            # Re-consolidation bonus (cap at 1.0 to prevent runaway weights)
            reinforced_decay = min(1.0, decay * 1.05)
            meta["decay"] = reinforced_decay

            # Optional debug log
            print(f"[Hippo.recall] Reinforced memory '{id_}' -> decay={reinforced_decay:.3f}, rehearsals={meta['rehearsal_count']}")

            memories.append({
                "text": doc,
                "weight": weight,
                "timestamp": timestamp_str,
                "distance": distance,
                "decay": reinforced_decay,  # 👈 this now reflects the reinforced value
            })

            # 🧠 Debug log per memory
            print(
                f"[Hippo.recall] {i+1:02d} | "
                f"weight={weight:.3f} | dist={distance:.3f} | decay={decay:.3f} | "
                f"ts={timestamp_str or 'n/a'} | preview='{snippet}...'"
            )

        memories.sort(key=lambda m: m["weight"], reverse=True)
        memories = memories[:10]

        print(f"[Hippo.recall] ✅ Retrieved {len(memories)} memories (weighted + decayed).")
        self.recall_window = memories
        return memories


    # ---------------------------
    # Commit
    # ---------------------------
    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        if time.time() - getattr(self, "last_commit_time", 0) < 3:
            time.sleep(1.5)

        fused_text = (
            f"USER QUERY:\n{user_query.strip()}\n\n"
            f"INTERNAL MONOLOGUE:\n{reflection.strip()}\n\n"
            f"MODEL RESPONSE:\n{response.strip()}"
        )

        embedding = self.cortex.embed(fused_text)
        emotions = state_json.get("emotions", [])
        keywords = state_json.get("keywords", [])
        meta = {
            **(metadata or {}),
            "timestamp": datetime.datetime.now().isoformat(),
            "memory_type": "dual_perspective",
            "reflection": reflection,
            "summary": f"Fusion of user query + reflection @ {metadata.get('turn_id') if metadata else 'N/A'}",
        }

        for i, e in enumerate(emotions[:3]):
            meta[f"emo_{i+1}_name"] = e.get("name")
            meta[f"emo_{i+1}_intensity"] = e.get("intensity")
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
