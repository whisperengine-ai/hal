# ============================================================
# hippocampus.py — Halcyon Episodic + Short-Term Memory Core
# ============================================================

import datetime
import time
import uuid
import os
import chromadb
import json
import hashlib


class Hippocampus:
    def __init__(self, cortex):
        self.cortex = cortex
        self.last_commit_time = 0

        # persistent store
        memory_path = os.path.abspath("./memory_journals/halcyon_persistent")
        os.makedirs(memory_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=memory_path)

        # long-term episodic memory (stable, weighted, emotional, etc)
        self.coll = self.client.get_or_create_collection("episodic_memory")

        # short-term scratch (per-turn echo, transient-ish)
        self.short_coll = self.client.get_or_create_collection("short_term_memory")

        self.MAX_MEMORIES = 25

        print(f"[Hippo.init] Connected to persistent memory at: {memory_path}")
        print("  - episodic_memory")
        print("  - short_term_memory")

    # --------------------------------------------------------
    # INTERNAL: build a deterministic id for a fused memory
    # --------------------------------------------------------
    def _stable_id_for_fused_text(self, fused_text: str) -> str:
        """Return a deterministic hash id for the fused_text."""
        return hashlib.sha1(fused_text.encode("utf-8")).hexdigest()

    # --------------------------------------------------------
    # INTERNAL: dedupe list of memory dicts (merge short+long)
    # key = text body
    # --------------------------------------------------------
    def _dedupe_memories(self, memories):
        unique = {}
        for m in memories:
            key = m["text"].strip()
            # keep the higher-weight version if same text appears twice
            if key not in unique or m["weight"] > unique[key]["weight"]:
                unique[key] = m
        return list(unique.values())

    # ============================================================
    # recall_with_context
    # ============================================================
    def recall_with_context(self, query, n_results=None):
        """
        Retrieve semantically relevant memories from BOTH
        short_term_memory and episodic_memory, merge them,
        annotate with decay/weight, and print diagnostics.
        """
        n_results = n_results or self.MAX_MEMORIES
        now = datetime.datetime.now()

        # embed the query once
        query_vec = self.cortex.embed(query)

        # --- query episodic (long-term)
        epi_results = self.coll.query(
            query_embeddings=[query_vec],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        # --- query short-term
        st_results = self.short_coll.query(
            query_embeddings=[query_vec],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        merged_rows = []

        # helper to process results from a given source
        def harvest(results, source_label):
            if not results or not results.get("documents"):
                return
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for i, doc in enumerate(docs):
                meta = metas[i] if i < len(metas) else {}
                dist = dists[i] if i < len(dists) else 1.0

                ts_str = meta.get("timestamp")
                try:
                    ts = datetime.datetime.fromisoformat(ts_str)
                    age_days = (now - ts).total_seconds() / 86400.0
                    decay = max(0.1, 1 - (age_days / 7.0))
                except Exception:
                    age_days = 0.0
                    decay = 1.0

                manual_weight = meta.get("manual_weight", 1.0)
                base_weight = (manual_weight * (1.5 - dist)) * decay
                reinforced_decay = min(1.0, decay * 1.05)

                # rehearsal count++
                meta["rehearsal_count"] = meta.get("rehearsal_count", 0) + 1
                # NOTE: we are not writing that increment back to DB yet. TODO optional.

                merged_rows.append({
                    "text": doc,
                    "weight": base_weight,
                    "timestamp": ts_str,
                    "distance": dist,
                    "decay": reinforced_decay,
                    "age_days": age_days,
                    "source": source_label,
                })

        harvest(epi_results, "episodic")
        harvest(st_results, "short_term")

        # dedupe merged_rows by text to kill near-identical duplicates
        merged_rows = self._dedupe_memories(merged_rows)

        # sort by weight desc, take top N
        merged_rows.sort(key=lambda m: m["weight"], reverse=True)
        merged_rows = merged_rows[:n_results]

        # ---- pretty diagnostics print ----
        header = (
            f"\n[Hippo.recall] ───── Memory Diagnostics ({now.strftime('%Y-%m-%d %H:%M:%S')}) ─────"
            "\n IDX | DECAY | WEIGHT | DIST  | AGE(d) | SRC    | TEXT PREVIEW"
            "\n──────────────────────────────────────────────────────────────────────"
        )
        print(header)
        for idx, mem in enumerate(merged_rows, start=1):
            snippet = mem["text"][:60].replace("\n", " ").replace("\r", " ")
            print(
                f"{idx:>4d} | "
                f"{mem['decay']:>5.3f} | "
                f"{mem['weight']:>6.3f} | "
                f"{mem['distance']:>5.3f} | "
                f"{mem['age_days']:>6.2f} | "
                f"{mem['source'][:7]:<7} | "
                f"{snippet}..."
            )

        print(f"[Hippo.recall] ✅ Retrieved {len(merged_rows)} unique memories (weighted + decayed).")

        return merged_rows

    # ============================================================
    # encode (short-term capture)
    # ============================================================
    def encode(self, turn_data):
        """
        Capture a volatile 'in the moment' snapshot of this turn.
        Goes ONLY into short_term_memory.
        """
        try:
            doc = (
                f"USER QUERY:\n{turn_data.get('user_query', '')}\n\n"
                f"REFLECTION:\n{turn_data.get('reflection', '')}\n\n"
                f"RESPONSE:\n{turn_data.get('response', '')}"
            )
            emb = self.cortex.embed(doc)

            meta = {
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "short_term",
                "turn_id": turn_data.get("turn_id"),
                "task_id": turn_data.get("task_id"),
                # short-term sits lighter in weighting
                "manual_weight": 0.5,
                "rehearsal_count": 0,
            }

            self.short_coll.add(
                ids=[str(uuid.uuid4())],
                documents=[doc],
                embeddings=[emb],
                metadatas=[meta],
            )

            print(f"[Hippo.encode] 🧩 Short-term memory encoded (turn {turn_data.get('turn_id')})")

        except Exception as e:
            print(f"[Hippo.encode] ❌ Error encoding short-term memory: {e}")

    # ============================================================
    # delayed_commit (long-term episodic)
    # ============================================================
    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        """
        Commit durable episodic memory with emotional + cognitive state.
        We:
        - fuse query/reflection/response
        - build deterministic id
        - skip if already stored
        """
        try:
            # gentle throttle (prevents hammering embeddings vendor etc.)
            if time.time() - getattr(self, "last_commit_time", 0) < 3:
                time.sleep(1.5)

            reflection_text = (reflection or "").strip()
            response_text = (response or "").strip()

            fused_text = (
                f"USER QUERY:\n{user_query.strip()}\n\n"
                f"REFLECTION:\n{reflection_text}\n\n"
                f"FINAL RESPONSE:\n{response_text}"
            )

            # deterministic ID for dedupe
            mem_id = self._stable_id_for_fused_text(fused_text)

            # check if this fused memory is already in episodic_memory
            existing = self.coll.get(ids=[mem_id], include=["metadatas"])
            if existing and existing.get("metadatas"):
                print(f"[Hippo.commit] 🔁 Duplicate memory {mem_id[:8]}... detected — skipping add.")
                self.last_commit_time = time.time()
                return

            # embed once
            embedding = self.cortex.embed(fused_text)

            # make sure state_json is dict-ish
            if isinstance(state_json, str):
                try:
                    state_json = json.loads(state_json)
                except Exception:
                    state_json = {}

            all_states = state_json.get("emotions", [])
            keywords = (metadata or {}).get("keywords", [])

            meta = {
                **(metadata or {}),
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "dual_perspective",
                "reflection": reflection_text,
                "response_preview": response_text[:256],
                "summary": f"Fusion of query + reflection @ {metadata.get('turn_id') if metadata else 'N/A'}",
                "manual_weight": 1.0,   # episodic baseline
                "rehearsal_count": 0,
            }

            # serialize top 3 emotive + top 3 cognitive
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

            # keywords -> keyword_1 ... keyword_10
            for i, kw in enumerate(keywords[:10]):
                meta[f"keyword_{i+1}"] = kw

            # write episodic memory with stable ID
            self.coll.add(
                ids=[mem_id],
                documents=[fused_text],
                embeddings=[embedding],
                metadatas=[meta],
            )

            self.last_commit_time = time.time()
            print(f"[Hippo.commit] Saved dual-perspective memory :: {meta.get('summary')} ({mem_id[:8]}...)")

        except Exception as e:
            print(f"[Hippo.commit] Error during commit: {e}")

    # ============================================================
    # adjust_weight (manual tuning / pinning)
    # ============================================================
    def adjust_weight(self, mem_id, weight):
        """
        Raise or lower importance of a specific episodic memory.
        We mutate manual_weight in episodic_memory only.
        """
        try:
            mem = self.coll.get(ids=[mem_id], include=["metadatas"])
            if mem and mem.get("metadatas") and mem["metadatas"][0]:
                meta = mem["metadatas"][0]
                meta["manual_weight"] = max(1.0, float(weight))
                self.coll.update(ids=[mem_id], metadatas=[meta])
                print(f"[Hippo.adjust] Set {mem_id[:8]}... manual_weight={weight}")
            else:
                print(f"[Hippo.adjust] Error: Memory ID {mem_id[:8]}... not found.")
        except Exception as e:
            print(f"[Hippo.adjust] Error adjusting weight: {e}")
# ============================================================
# End of hippocampus.py