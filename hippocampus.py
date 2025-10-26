# ============================================================
# hippocampus.py — Halcyon Episodic Memory Core (Cleaned/Fixed)
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
        self.coll = self.client.get_or_create_collection("episodic_memory")
        self.MAX_MEMORIES = 25

        print(f"[Hippo.init] Connected to persistent memory at: {memory_path}/episodic_memory")

    # ============================================================
    # Memory recall (Functional method)
    # ============================================================
    # 💡 CLEANUP: Removed the obsolete 'recall' and 'encode' stub functions.
    
    # ---------------------------
    # Advanced recall with context and diagnostics
    def recall_with_context(self, query, n_results=None):
        """Retrieve semantically relevant memories and print readable diagnostics."""
        n_results = n_results or self.MAX_MEMORIES

        vec = self.cortex.embed(query)
        results = self.coll.query(
            query_embeddings=[vec],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        memories = []
        now = datetime.datetime.now()

        header = (
            f"\n[Hippo.recall] ───── Memory Diagnostics ({now.strftime('%Y-%m-%d %H:%M:%S')}) ─────"
            "\n IDX | DECAY | WEIGHT | DIST  | AGE(d) | TEXT PREVIEW"
            "\n────────────────────────────────────────────────────────"
        )
        print(header)

        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            timestamp_str = meta.get("timestamp")

            # compute decay
            try:
                ts = datetime.datetime.fromisoformat(timestamp_str)
                age_days = (now - ts).total_seconds() / 86400
                decay = max(0.1, 1 - (age_days / 7.0))
            except Exception:
                age_days = 0
                decay = 1.0

            distance = results["distances"][0][i]
            manual_weight = meta.get("manual_weight", 1.0)
            weight = (manual_weight * (1.5 - distance)) * decay

            meta["rehearsal_count"] = meta.get("rehearsal_count", 0) + 1
            reinforced_decay = min(1.0, decay * 1.05)

            snippet = doc[:60].replace("\n", " ").replace("\r", " ")

            # aligned printout
            print(
                f" {i+1:>3d} | {reinforced_decay:>5.3f} | {weight:>6.3f} | "
                f"{distance:>5.3f} | {age_days:>6.2f} | {snippet}..."
            )

            memories.append({
                "text": doc,
                "weight": weight,
                "timestamp": timestamp_str,
                "distance": distance,
                "decay": reinforced_decay,
            })

        print(f"[Hippo.recall] ✅ Retrieved {len(memories)} memories (weighted + decayed).")

        memories.sort(key=lambda m: m["weight"], reverse=True)
        return memories



    # ---------------------------
    # Commit
    # ---------------------------
    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        """
        Commits a dual-perspective memory entry, updated to handle 
        Emotive and Cognitive states (12 keys total).
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

            # Defensive emotion/keyword parsing (state_json now contains ALL 6 states)
            if isinstance(state_json, str):
                try:
                    state_json = json.loads(state_json)
                except Exception:
                    state_json = {}
            
            # The 'emotions' list from Cortex now contains objects with {"name": X, "intensity": Y, "type": Z}
            all_states = state_json.get("emotions", []) 
            keywords = metadata.get("keywords", []) # Keywords are passed via metadata in Thalamus

            # Base metadata
            meta = {
                **(metadata or {}),
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "dual_perspective",
                "reflection": reflection_text,
                "response_preview": response_text[:256],
                "summary": f"Fusion of query + reflection @ {metadata.get('turn_id') if metadata else 'N/A'}",
                "manual_weight": 1.0, # Base for pinning control
                "rehearsal_count": 0,
            }

            # 💡 FIX: Emotional & Cognitive serialization (safe up to 3 of each)
            emotive_count = 0
            cognitive_count = 0
            for state in all_states:
                if state.get('type') == 'emotive' and emotive_count < 3:
                    meta[f"emo_{emotive_count+1}_name"] = state.get("name")
                    meta[f"emo_{emotive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    emotive_count += 1
                elif state.get('type') == 'cognitive' and cognitive_count < 3:
                    meta[f"cog_{cognitive_count+1}_name"] = state.get("name")
                    meta[f"cog_{cognitive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    cognitive_count += 1

            # Keyword serialization (safe up to 10)
            for i, kw in enumerate(keywords[:10]):
                meta[f"keyword_{i+1}"] = kw

            # Clean weight baseline
            # 💡 FIX: This should ensure manual_weight is used if present, but since we set 1.0 above, 
            # we keep this simple. ChromaDB will handle the base weight.
            # meta["weight"] = float(meta.get("weight", 1.0) or 1.0)

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
# TEMPORAL HELPERS (Only Adjust Weight Retained)
# ============================================================
# 💡 CLEANUP: Removed promote_to_core, demote_from_core, and promote_to_dream helper functions.
    
    def adjust_weight(self, mem_id, weight):
        """Adjust stored importance (manual_weight) of a memory."""
        try:
            # We must use include=["metadatas"] to get the metadata to update it
            mem = self.coll.get(ids=[mem_id], include=["metadatas"]) 
            
            if mem and mem["metadatas"][0]:
                meta = mem["metadatas"][0]
                # Update the specific manual_weight field, ensuring a minimum weight of 1.0
                meta["manual_weight"] = max(1.0, float(weight))
                
                self.coll.update(ids=[mem_id], metadatas=[meta])
                print(f"[Hippo.adjust] Set {mem_id[:8]}... weight={weight}")
            else:
                 print(f"[Hippo.adjust] Error: Memory ID {mem_id[:8]}... not found.")
        except Exception as e:
            print(f"[Hippo.adjust] Error adjusting weight: {e}")