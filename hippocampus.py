# ============================================================
# hippocampus.py — Halcyon Episodic Memory Core (v3.2)
# ============================================================

import datetime
import time
import uuid
import os
import chromadb
import json

class Hippocampus:
    def __init__(self, cortex):
        self.cortex = cortex
        self.last_commit_time = 0

        memory_path = os.path.abspath("./memory_journals/halcyon_persistent")
        os.makedirs(memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=memory_path)
        self.coll = self.client.get_collection("episodic_memory")

        print(f"[Hippo.init] Connected to persistent memory at: {memory_path}/episodic_memory")

    # ============================================================
    # Memory recall + encode stubs
    # ============================================================
    def recall(self, query: str, n_results: int = 10):
        """
        Minimal recall placeholder.
        Returns a few dummy entries for now until Chroma or vector recall is wired.
        """
        print(f"[Hippocampus] 🔍 recall() requested for query='{query[:50]}' (limit={n_results})")
        # You can later replace this with a ChromaDB or FAISS lookup.
        return [
            {"timestamp": "2025-10-25T00:00:00Z", "memory": "This is a placeholder memory."},
            {"timestamp": "2025-10-24T23:50:00Z", "memory": "Another sample memory entry."}
        ]

    def encode(self, turn_data: dict):
        """
        Minimal encode placeholder.
        Logs and appends to an in-memory list for debug visibility.
        """
        if not hasattr(self, "_encoded"):
            self._encoded = []
        self._encoded.append(turn_data)
        print(f"[Hippocampus] 💾 Encoded turn {turn_data.get('turn_id')}")
    # ---------------------------
    # Advanced recall with context and diagnostics
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
        """
        Commits a dual-perspective memory entry:
        includes user query, internal reflection, model response,
        emotion parsing, and safe metadata for display + recall.
        """
        try:
            # Gentle throttle to prevent API bursts
            if time.time() - getattr(self, "last_commit_time", 0) < 3:
                time.sleep(1.5)

            # Merge reflections and response text cleanly
            reflection_text = (reflection or "").strip()
            response_text = (response or "").strip()

            fused_text = (
                f"USER QUERY:\n{user_query.strip()}\n\n"
                f"REFLECTION:\n{reflection_text}\n\n"
                f"FINAL RESPONSE:\n{response_text}"
            )

            # Generate embedding
            embedding = self.cortex.embed(fused_text)

            # Defensive emotion/keyword parsing
            if isinstance(state_json, str):
                try:
                    state_json = json.loads(state_json)
                except Exception:
                    state_json = {}
            emotions = state_json.get("emotions", [])
            keywords = state_json.get("keywords", [])

            # Base metadata
            meta = {
                **(metadata or {}),
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "dual_perspective",
                "reflection": reflection_text,
                "response_preview": response_text[:256],
                "summary": f"Fusion of query + reflection @ {metadata.get('turn_id') if metadata else 'N/A'}",
            }

            # Emotional serialization (safe up to 3)
            for i, e in enumerate(emotions[:3]):
                meta[f"emo_{i+1}_name"] = e.get("name")
                meta[f"emo_{i+1}_intensity"] = float(e.get("intensity") or 0.0)

            # Keyword serialization (safe up to 10)
            for i, kw in enumerate(keywords[:10]):
                meta[f"keyword_{i+1}"] = kw

            # Clean weight baseline
            meta["weight"] = float(meta.get("weight", 1.0) or 1.0)

            # Save memory record
            self.coll.add(
                ids=[str(uuid.uuid4())],
                documents=[fused_text],
                embeddings=[embedding],
                metadatas=[meta],
            )

            self.last_commit_time = time.time()
            print(f"[Hippo.commit] Saved dual-perspective memory :: {meta.get('summary')}")

        except Exception as e:
            print(f"[Hippo.commit] Error during commit: {e}")


# ============================================================
#TEMPORAL HELPERS
# ============================================================
    def promote_to_core(self, mem_id):
        """Move a memory to the permanent core collection."""
        doc = self.coll.get(ids=[mem_id], include=["documents", "metadatas"])
        core = self.client.get_or_create_collection("core_memory")
        core.add(ids=doc["ids"], documents=doc["documents"], metadatas=doc["metadatas"])
        print(f"[Hippo.core] Promoted {mem_id} to core memory")

    def demote_from_core(self, mem_id):
        """Remove a memory from the core collection."""
        core = self.client.get_or_create_collection("core_memory")
        core.delete(ids=[mem_id])
        print(f"[Hippo.core] Demoted {mem_id}")

    def promote_to_dream(self, mem_id):
        """Queue a memory for symbolic consolidation."""
        doc = self.coll.get(ids=[mem_id], include=["documents", "metadatas"])
        dream = self.client.get_or_create_collection("dream_memory_queue")
        dream.add(ids=doc["ids"], documents=doc["documents"], metadatas=doc["metadatas"])
        print(f"[Hippo.dream] Added {mem_id} to dream queue")

    def adjust_weight(self, mem_id, weight):
        """Adjust stored importance of a memory."""
        try:
            mem = self.coll.get(ids=[mem_id], include=["metadatas"])
            if mem and mem["metadatas"][0]:
                meta = mem["metadatas"][0]
                meta["manual_weight"] = weight
                self.coll.update(ids=[mem_id], metadatas=[meta])
                print(f"[Hippo.adjust] Set {mem_id} weight={weight}")
        except Exception as e:
            print(f"[Hippo.adjust] Error adjusting weight: {e}")

