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

        # --- QDRANT CLIENT SETUP (configurable via env) ---
        qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        print(f"[Hippo.init] Connecting to Qdrant at {qdrant_host}:{qdrant_port}")
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Single unified collection with named vectors
        self.collection_name = os.getenv("QDRANT_COLLECTION", "hal_memory")
        
        # Determine vector size from the embedding provider
        if self.cortex.embed_provider == "local" and self.cortex._local_embedder:
            VECTOR_SIZE = self.cortex._local_embedder.get_sentence_embedding_dimension()
        elif self.cortex.embed_provider == "local":
            VECTOR_SIZE = 384  # all-MiniLM-L6-v2 default
        else:
            VECTOR_SIZE = 3072  # OpenAI text-embedding-3-large
        
        print(f"[Hippo.init] Using vector size: {VECTOR_SIZE}")
        
        # Check if dual vectors are enabled
        use_dual_vectors = os.getenv("USE_DUAL_VECTORS", "false").lower() in ["true", "1", "yes"]
        
        # Create collection with named vectors for multiple search strategies
        try:
            self.client.get_collection(self.collection_name)
            print(f"[Hippo.init] Collection '{self.collection_name}' already exists")
        except:
            # Collection doesn't exist, create with appropriate vector config
            if use_dual_vectors:
                # Dual vector mode: named vectors for content and emotional search
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config={
                        "content": models.VectorParams(
                            size=VECTOR_SIZE,
                            distance=models.Distance.COSINE
                        ),
                        "emotional": models.VectorParams(
                            size=VECTOR_SIZE,
                            distance=models.Distance.COSINE
                        )
                    }
                )
                print(f"[Hippo.init] Created collection '{self.collection_name}' with dual named vectors (content + emotional)")
            else:
                # Single vector mode: simple default vector
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"[Hippo.init] Created collection '{self.collection_name}' with single vector (faster mode)")

        mode = "dual-vector" if use_dual_vectors else "single-vector"
        print(f"[Hippo.init] ✅ Connected to Qdrant in {mode} mode.")

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
    # recall_with_context (Qdrant Search with Named Vectors)
    # ============================================================
    def recall_with_context(self, query, n_results=None, search_mode="hybrid"):
        """
        Search memories using named vectors.
        
        Args:
            query: Search query text
            n_results: Maximum results to return (default: 25)
            search_mode: "content" (factual), "emotional" (feelings), or "hybrid" (both)
        
        Returns:
            List of weighted memory dictionaries
        """
        n_results = n_results or getattr(self, "MAX_MEMORIES", 25)
        now = datetime.datetime.now()
        
        # Check if dual vectors are enabled
        use_dual_vectors = os.getenv("USE_DUAL_VECTORS", "false").lower() in ["true", "1", "yes"]
        
        # Generate embeddings for the query with caching
        content_vec = self.cortex.embed(query, cache_key=f"content:{query}")
        
        # For emotional vector, prepend emotional context to the query (only if dual vectors enabled)
        if use_dual_vectors:
            emotional_query = f"[Emotional context] How does this make me feel? {query}"
            emotional_vec = self.cortex.embed(emotional_query, cache_key=f"emotional:{query}")
        else:
            emotional_vec = None

        merged_rows = []

        # Search using content vector (factual/semantic similarity)
        if search_mode in ["content", "hybrid"]:
            try:
                # Use named vector if dual vectors enabled, otherwise use single vector
                if use_dual_vectors:
                    content_results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=("content", content_vec),
                        limit=n_results,
                        with_payload=True,
                        with_vectors=False
                    )
                else:
                    # Single vector mode - search default vector
                    content_results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=content_vec,
                        limit=n_results,
                        with_payload=True,
                        with_vectors=False
                    )
                self._harvest_results(content_results, "content", merged_rows, now)
            except Exception as e:
                print(f"[Hippo.recall] ⚠️ Content search failed: {e}")

        # Search using emotional vector (feeling/tone similarity) - only if dual vectors enabled
        if use_dual_vectors and search_mode in ["emotional", "hybrid"] and emotional_vec:
            try:
                emotional_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=("emotional", emotional_vec),
                    limit=n_results,
                    with_payload=True,
                    with_vectors=False
                )
                self._harvest_results(emotional_results, "emotional", merged_rows, now)
            except Exception as e:
                print(f"[Hippo.recall] ⚠️ Emotional search failed: {e}")

        # Deduplicate and rank
        merged_rows = self._dedupe_memories(merged_rows)
        merged_rows.sort(key=lambda m: m["weight"], reverse=True)
        merged_rows = merged_rows[:n_results]

        mode_label = f"{search_mode} ({'dual' if use_dual_vectors else 'single'} vector)"
        print(f"\n[Hippo.recall] ✅ Retrieved {len(merged_rows)} memories via {mode_label} search.")

        if not merged_rows:
            print("[Hippo.recall] (no matches found)\n")
            return merged_rows

        print("─────────────────────────────────────────────")
        print(f"{'Vector':<12} | {'ID':<8} | {'Weight':<7} | {'Decay':<5} | {'Age(d)':<6} | Text Snippet")
        print("─────────────────────────────────────────────")
        for m in merged_rows:
            snippet = (m['text'] or '')[:60].replace("\n", " ")
            print(f"{m['source']:<12} | {str(m['id'])[:8]} | {m['weight']:<7.3f} | {m['decay']:<5.2f} | {m['age_days']:<6.2f} | {snippet}")
        print("─────────────────────────────────────────────\n")

        return merged_rows

    def _harvest_results(self, results, source_label, merged_rows, now):
        """Helper to process search results and add to merged_rows."""
        for point in results:
            # COSINE similarity: higher score = more similar (0 to 1)
            # Convert to distance-like metric for consistent weighting
            distance = 1.0 - point.score if point.score <= 1.0 else 0.0
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
            # Higher similarity (lower distance) = higher weight
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


    # ============================================================
    # encode (short-term capture)
    # ============================================================
    def encode(self, turn_data):
        """Short-term encode not used in this model version."""
        pass


    # ============================================================
    # delayed_commit (long-term episodic with Named Vectors)
    # ============================================================
    def delayed_commit(self, user_query, reflection, response, state_json, metadata):
        """
        Commit durable memory with dual named vectors (if enabled):
        - 'content': factual/semantic embedding of the full conversation
        - 'emotional': embedding focused on emotional tone and feelings
        
        Uses cached embeddings from recall phase if available.
        """
        try:
            # Prevent rapid-fire commits
            if time.time() - getattr(self, "last_commit_time", 0) < 3:
                time.sleep(1.5)

            reflection_text = (reflection or "").strip()
            response_text = (response or "").strip()

            # Content vector: full factual context
            fused_text = (
                f"USER QUERY:\n{user_query.strip()}\n\n"
                f"REFLECTION:\n{reflection_text}\n\n"
                f"FINAL RESPONSE:\n{response_text}"
            )

            mem_id = self._stable_id_for_fused_text(fused_text)

            # --- EXISTENCE CHECK ---
            try:
                existing = self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[mem_id],
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

            # Check if dual vectors are enabled
            use_dual_vectors = os.getenv("USE_DUAL_VECTORS", "false").lower() in ["true", "1", "yes"]

            # --- GENERATE EMBEDDINGS (with caching) ---
            content_embedding = self.cortex.embed(fused_text, cache_key=f"content:{user_query}")
            
            if use_dual_vectors:
                # Emotional vector: emphasize feelings and tone
                emotional_text = (
                    f"[Emotional Context] "
                    f"User felt: {user_query.strip()} "
                    f"I felt: {reflection_text} "
                    f"I expressed: {response_text}"
                )
                emotional_embedding = self.cortex.embed(emotional_text, cache_key=f"emotional:{user_query}")
                
                if not content_embedding or not emotional_embedding:
                    raise RuntimeError("Cortex.embed() returned no data for one or both vectors.")
            else:
                if not content_embedding:
                    raise RuntimeError("Cortex.embed() returned no data.")

            # --- METADATA (PAYLOAD) ---
            meta = {
                **(metadata or {}),
                "timestamp": datetime.datetime.now().isoformat(),
                "memory_type": "dual_perspective" if use_dual_vectors else "single_perspective",
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

            # --- UPSERT WITH NAMED VECTORS (or single vector) ---
            if use_dual_vectors:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(
                            id=mem_id,
                            vector={
                                "content": content_embedding,
                                "emotional": emotional_embedding
                            },
                            payload=meta
                        )
                    ]
                )
                vector_mode = "dual vectors"
            else:
                # Single vector mode - store as default vector
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(
                            id=mem_id,
                            vector=content_embedding,
                            payload=meta
                        )
                    ]
                )
                vector_mode = "single vector"

            self.last_commit_time = time.time()
            print(f"[Hippo.commit] ✅ Saved memory with {vector_mode} :: {meta.get('summary')} ({mem_id[:8]}...)")

        except Exception as e:
            print(f"[Hippo.commit] ❌ Error during commit: {e}")
            import traceback; traceback.print_exc()

    # ============================================================
    # adjust_weight (manual tuning / pinning)
    # ============================================================
    def adjust_weight(self, mem_id, weight):
        """Mutate manual_weight in the unified collection (Qdrant)."""
        try:
            new_weight = max(1.0, float(weight))
            
            # Qdrant uses set_payload to update specific metadata fields (manual_weight)
            self.client.set_payload(
                collection_name=self.collection_name,
                payload={"manual_weight": new_weight},
                points=[mem_id],
            )
            
            print(f"[Hippo.adjust] Set {mem_id[:8]}... manual_weight={new_weight}")
        except Exception as e:
            print(f"[Hippo.adjust] Error adjusting weight: {e}")
# ============================================================
# get recent turns
# ============================================================
    def get_recent_turns(self, n=3):
        """Fetch the most recent N conversational turns from log files, pulling from previous day if today's count is insufficient."""
        from glob import glob
        from datetime import datetime, timedelta

        def load_turns_from_dir(log_dir):
            turns = []
            log_path = os.path.join(log_dir, "turn_log.jsonl")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        for line in f:
                            try:
                                turns.append(json.loads(line.strip()))
                            except Exception:
                                continue
                except Exception as e:
                    print(f"[Hippocampus] ⚠️ Error reading {log_path}: {e}")
            return turns

        try:
            today = datetime.today().date()
            yesterday = today - timedelta(days=1)

            today_dir = os.path.join("runtime_logs", today.isoformat())
            yest_dir = os.path.join("runtime_logs", yesterday.isoformat())

            all_turns = load_turns_from_dir(today_dir)

            if len(all_turns) < n:
                needed = n - len(all_turns)
                yest_turns = load_turns_from_dir(yest_dir)
                all_turns.extend(yest_turns[::-1][:needed])  # Grab most recent first from yesterday

            # Sort and return only the most recent N
            return sorted(all_turns, key=lambda x: x.get("timestamp", ""), reverse=True)[:n]

        except Exception as e:
            print(f"[Hippocampus] ⚠️ Failed to fetch recent turns: {e}")
            return []
