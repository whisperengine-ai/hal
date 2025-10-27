# ============================================================
# hippocampus.py — Halcyon Qdrant Core (Final Version)
# ============================================================

import datetime
import time
import uuid
import os
import json
import hashlib

# 💡 QDRANT IMPORTS
from qdrant_client import QdrantClient, models 
# Removed: import chromadb

class Hippocampus:
    def __init__(self, cortex):
        self.cortex = cortex
        self.last_commit_time = 0

        # --- QDRANT CLIENT SETUP ---
        # Connect to the local Docker container
        self.client = QdrantClient(host="localhost", port=6333)

        self.episodic_collection_name = "episodic_memory"
        self.short_collection_name = "short_term_memory"
        
        VECTOR_SIZE = 3072 
        try:
            self.client.get_collection(self.episodic_collection_name)
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.episodic_collection_name,
                vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE)
            )

        try:
            self.client.get_collection(self.short_collection_name)
        except:
            self.client.create_collection(
                collection_name=self.short_collection_name,
                vectors_config=models.VectorParams(size=3072, distance=models.Distance.DOT)
            )

        print("[Hippo.init] ✅ Connected to Qdrant and dual collections verified.")

    # --------------------------------------------------------
    # INTERNAL: build a deterministic id for a fused memory
    # --------------------------------------------------------
    def _stable_id_for_fused_text(self, fused_text: str) -> str:
        """
        Return a deterministic UUID for a given fused_text.
        This ensures identical input always maps to the same Qdrant point ID.
        """
        import uuid, hashlib
        digest = hashlib.sha1(fused_text.encode("utf-8")).digest()
        # Take the first 16 bytes (128 bits) and cast to a valid UUID format
        return str(uuid.UUID(bytes=digest[:16]))


    # --------------------------------------------------------
    # INTERNAL: dedupe list of memory dicts
    # --------------------------------------------------------
    def _dedupe_memories(self, memories):
        unique = {}
        for m in memories:
            key = m["text"].strip()
            if key not in unique or m["weight"] > unique[key]["weight"]:
                unique[key] = m
        return list(unique.values())

    # ============================================================
    # recall_with_context (Qdrant Search)
    # ============================================================
    def recall_with_context(self, query, n_results=None):
        n_results = n_results or getattr(self, "MAX_MEMORIES", 25)
        now = datetime.datetime.now()
        query_vec = self.cortex.embed(query)

        def qdrant_search(collection_name, vector):
            return self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=n_results,
                with_payload=True,
                with_vectors=False
            )

        epi_results = qdrant_search(self.episodic_collection_name, query_vec)
        st_results = qdrant_search(self.short_collection_name, query_vec)

        merged_rows = []

        def harvest(results, source_label):
            for point in results:
                distance = 1.0 - point.score
                meta = point.payload or {}
                mem_id = point.id
                ts_str = meta.get("timestamp")

                try:
                    ts = datetime.datetime.fromisoformat(ts_str)
                    age_days = (now - ts).total_seconds() / 86400.0
                    decay = max(0.1, 1 - (age_days / 7.0))
                except Exception:
                    age_days = 0.0
                    decay = 1.0

                manual_weight = meta.get("manual_weight", 1.0)
                base_weight = (manual_weight * (1.5 - distance)) * decay
                reinforced_decay = min(1.0, decay * 1.05)

                meta["rehearsal_count"] = meta.get("rehearsal_count", 0) + 1

                merged_rows.append({
                    "id": mem_id,
                    "text": meta.get("fused_text", "Text Unavailable"),
                    "weight": base_weight,
                    "timestamp": ts_str,
                    "distance": distance,
                    "decay": reinforced_decay,
                    "age_days": age_days,
                    "source": source_label,
                })

        harvest(epi_results, "episodic")
        harvest(st_results, "short_term")

        merged_rows = self._dedupe_memories(merged_rows)
        merged_rows.sort(key=lambda m: m["weight"], reverse=True)
        merged_rows = merged_rows[:n_results]

        print(f"\n[Hippo.recall] ✅ Retrieved {len(merged_rows)} unique memories (weighted + decayed).")

        if not merged_rows:
            print("[Hippo.recall] (no matches found)\n")
            return merged_rows

        print("─────────────────────────────────────────────")
        print(f"{'Source':<12} | {'ID':<8} | {'Weight':<7} | {'Decay':<5} | {'Age(d)':<6} | Text Snippet")
        print("─────────────────────────────────────────────")
        for m in merged_rows:
            snippet = (m['text'] or '')[:60].replace("\n", " ")
            print(f"{m['source']:<12} | {str(m['id'])[:8]} | {m['weight']:<7.3f} | {m['decay']:<5.2f} | {m['age_days']:<6.2f} | {snippet}")
        print("─────────────────────────────────────────────\n")

        return merged_rows


    # ============================================================
    # encode (short-term capture)
    # ============================================================
    def encode(self, turn_data):
        """Short-term encode not used in this model version."""
        pass


    # ============================================================
    # delayed_commit (long-term episodic)
    # ============================================================
    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        """Commit durable episodic memory with emotional + cognitive state using OpenAI embeddings."""
        try:
            # Prevent rapid-fire commits
            if time.time() - getattr(self, "last_commit_time", 0) < 3:
                time.sleep(1.5)

            reflection_text = (reflection or "").strip()
            response_text = (response or "").strip()

            fused_text = (
                f"USER QUERY:\n{user_query.strip()}\n\n"
                f"REFLECTION:\n{reflection_text}\n\n"
                f"FINAL RESPONSE:\n{response_text}"
            )

            mem_id = self._stable_id_for_fused_text(fused_text)

            # --- EXISTENCE CHECK ---
            try:
                existing = self.client.retrieve(
                    collection_name=self.episodic_collection_name,
                    ids=[mem_id],  # Correct param for current Qdrant client
                    with_payload=False,
                    with_vectors=False
                )
                if existing and len(existing) > 0:
                    print(f"[Hippo.commit] 🔁 Duplicate memory {mem_id[:8]}... detected — skipping add.")
                    self.last_commit_time = time.time()
                    return
            except Exception:
                # Fail-safe: if retrieve check fails, continue safely
                existing = []

            # --- EMBEDDING ---
            embedding = self.cortex.embed(fused_text)
            if not embedding:
                raise RuntimeError("Cortex.embed() returned no data.")

            # --- METADATA (PAYLOAD) ---
            meta = {
                **(metadata or {}),
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "dual_perspective",
                "reflection": reflection_text,
                "response_preview": response_text[:256],
                "summary": f"Fusion of query + reflection @ {metadata.get('turn_id') if metadata else 'N/A'}",
                "manual_weight": 1.0,
                "rehearsal_count": 0,
                "fused_text": fused_text
            }

            all_states = state_json.get("emotions", [])
            emotive_count = 0
            cognitive_count = 0
            for state in all_states:
                stype = state.get("type")
                if stype == "emotive" and emotive_count < 3:
                    meta[f"emo_{emotive_count+1}_name"] = state.get("name")
                    meta[f"emo_{emotive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    emotive_count += 1
                elif stype == "cognitive" and cognitive_count < 3:
                    meta[f"cog_{cognitive_count+1}_name"] = state.get("name")
                    meta[f"cog_{cognitive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    cognitive_count += 1

            for i, kw in enumerate((metadata or {}).get("keywords", [])[:10]):
                meta[f"keyword_{i+1}"] = kw

            # --- UPSERT (WRITE) ---
            self.client.upsert(
                collection_name=self.episodic_collection_name,
                points=models.Batch(
                    ids=[mem_id],
                    vectors=[embedding],
                    payloads=[meta]
                )
            )


            self.last_commit_time = time.time()
            print(f"[Hippo.commit] ✅ Saved episodic memory :: {meta.get('summary')} ({mem_id[:8]}...)")

        except Exception as e:
            print(f"[Hippo.commit] ❌ Error during commit: {e}")
            import traceback; traceback.print_exc()

    # ============================================================
    # adjust_weight (manual tuning / pinning)
    # ============================================================
    def adjust_weight(self, mem_id, weight):
        """Mutate manual_weight in episodic_memory only (Qdrant)."""
        try:
            new_weight = max(1.0, float(weight))
            
            # Qdrant uses set_payload to update specific metadata fields (manual_weight)
            self.client.set_payload(
                collection_name=self.episodic_collection_name,
                payload={"manual_weight": new_weight},
                points=[mem_id],
            ).result()
            
            print(f"[Hippo.adjust] Set {mem_id[:8]}... manual_weight={new_weight}")
        except Exception as e:
            print(f"[Hippo.adjust] Error adjusting weight: {e}")
# ============================================================