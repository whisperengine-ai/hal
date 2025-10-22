# ============================================================
# halcyon_web_server.py — Flask bridge for Halcyon Web Console 🧠
# ============================================================
from flask import (
    Flask, request, jsonify, send_from_directory,
    Response, stream_with_context
)
from flask_cors import CORS
import os
import time
import json
import re
import datetime
import traceback
import chromadb
from halcyon_brainstem import Cortex, Thalamus
from hippocampus import Hippocampus
from attention import Attention

# Unified SSE bus (monologue + attention)
from sse_bus import sse_streams

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def state_from_meta(meta: dict):
    """Extract emotions from metadata keys like emo_1_name/intensity."""
    if not meta:
        return {"emotions": []}
    emotions = []
    for i in range(1, 4):
        name = meta.get(f"emo_{i}_name")
        intensity = meta.get(f"emo_{i}_intensity")
        if name:
            try:
                emotions.append({"name": name, "intensity": float(intensity)})
            except Exception:
                emotions.append({"name": name, "intensity": 0.0})
    return {"emotions": emotions}

# ------------------------------------------------------------
# App bootstrap
# ------------------------------------------------------------
app = Flask(__name__, static_folder="web_ui", static_url_path="")
CORS(app)  # local browser requests

print("[Server] Initializing Halcyon core modules...")
cortex = Cortex()
hippocampus = Hippocampus(cortex)
attention = Attention(hippocampus)
attention.load_narrative()
thalamus = Thalamus(cortex, hippocampus, attention)
app.cortex = cortex
app.hippocampus = hippocampus
app.attention = attention
app.thalamus = thalamus


print("[Server] Initialization complete.")

# ------------------------------------------------------------
# Static UI
# ------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("web_ui", "index.html")

# ------------------------------------------------------------
# SSE: Internal Monologue (pre-memory reflection)
# ------------------------------------------------------------
@app.route("/api/reflection_raw")
def api_reflection_raw():
    """Continuous SSE stream for internal monologue."""
    def stream():
        q = sse_streams["reflection"]
        while True:
            try:
                payload = q.get(timeout=1)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception:
                # heartbeat to keep the connection alive
                yield ":\n\n"
                time.sleep(1)
    return Response(stream_with_context(stream()), mimetype="text/event-stream")

# ------------------------------------------------------------
# SSE: Attention (final reflection + response)
# ------------------------------------------------------------
@app.route("/api/attention_feed")
def api_attention_feed():
    """Continuous SSE stream for attention (final reflection + response)."""
    def stream():
        q = sse_streams["attention"]
        while True:
            try:
                payload = q.get(timeout=1)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception:
                yield ":\n\n"
                time.sleep(1)
    return Response(stream_with_context(stream()), mimetype="text/event-stream")

# ------------------------------------------------------------
# Manual test endpoints for SSE (handy for debugging UI)
# ------------------------------------------------------------
@app.get("/api/test-reflection")
def api_test_reflection():
    sse_streams["reflection"].put({
        "type": "pre_memory_reflection",
        "turn_id": 777,
        "timestamp": datetime.datetime.now().isoformat(),
        "pre_reflection_state": {"emotions": [{"name": "Curiosity", "intensity": 0.7}]},
        "pre_reflection_text": "Test pre-memory reflection emitted from /api/test-reflection."
    })
    return jsonify({"status": "ok"})

@app.get("/api/test-attention")
def api_test_attention():
    sse_streams["attention"].put({
        "type": "attention_update",
        "turn_id": 999,
        "timestamp": datetime.datetime.now().isoformat(),
        "final_reflection": "Test final reflection from /api/test-attention",
        "response": "This is only a test."
    })
    return jsonify({"status": "ok"})

# ------------------------------------------------------------
# Optional: Inspect current attention buffer (if implemented)
# ------------------------------------------------------------
@app.get("/api/attention")
def api_attention_snapshot():
    """Return current working attention window (short-term context)."""
    try:
        buffer = thalamus.get_attention_window()  # Implement in Thalamus if you want
        return jsonify(buffer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------
# Chat turn
# ------------------------------------------------------------
@app.post("/api/turn")
def api_turn():
    """Handle chat turns end-to-end."""
    try:
        data = request.get_json(force=True)
        query = (data.get("query") or "").strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400

        turn_id = int(time.time())
        task_id = f"WEB_UI_{turn_id}"

        print(f"[API] Processing turn: {turn_id} :: {query[:80]}...")
        response = thalamus.process_turn(query, turn_id, task_id)

        return jsonify({"response": response, "turn_id": turn_id})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------
# Memory: fetch + inspect
# ------------------------------------------------------------
@app.get("/api/memories")
def api_memories():
    """Return all stored memories, including emotion + keyword metadata."""
    def parse_doc(doc: str, meta: dict):
        # Try JSON doc first
        try:
            obj = json.loads(doc)
            ts = obj.get("timestamp") or meta.get("timestamp")
            query = obj.get("user_query", "")
            reflection = obj.get("reflection", "")
            state = obj.get("state") or state_from_meta(meta)
        except Exception:
            # Fallback for fused/plain text
            ts = (meta or {}).get("timestamp", "")
            q_match = re.search(r"USER\s*QUERY:\s*(.+)", doc, re.IGNORECASE)
            r_match = re.search(r"INTERNAL\s*MONOLOGUE:\s*([\s\S]+?)MODEL\s*RESPONSE:", doc, re.IGNORECASE)
            query = (q_match.group(1).strip() if q_match else "")
            reflection = (r_match.group(1).strip() if r_match else "")
            state = state_from_meta(meta)

        # collect keyword_* entries from metadata
        keywords = [v for k, v in (meta or {}).items() if k.startswith("keyword_") and v]
        return ts, query, reflection, state, keywords

    try:
        client = chromadb.PersistentClient(path="./memory_journals/halcyon_persistent")
        coll = client.get_collection("episodic_memory")
        results = coll.get(include=["documents", "metadatas"], limit=200)

        ids = results.get("ids", []) or []
        docs = results.get("documents", []) or []
        metas = results.get("metadatas", []) or []

        entries = []
        for id_, doc, meta in zip(ids, docs, metas):
            ts, query, reflection, state, keywords = parse_doc(doc or "", meta or {})
            entries.append({
                "id": id_,
                "timestamp": ts or "",
                "query": query,
                "reflection": reflection,
                "state": state or {"emotions": []},
                "keywords": keywords,
                "content": doc or "",
                "meta": meta or {}
            })

        entries.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
        return jsonify(entries)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.get("/api/memory/inspect")
def inspect_memory():
    """Legacy list of stored memories (without keyword extraction)."""
    try:
        client = chromadb.PersistentClient(path="./memory_journals/halcyon_persistent")
        coll = client.get_collection("episodic_memory")
        results = coll.get(include=["documents", "metadatas"], limit=200)

        ids = results.get("ids", list(range(len(results.get("documents", []))))) or []
        docs = results.get("documents", []) or []
        metas = results.get("metadatas", []) or []

        def parse_doc(doc: str, meta: dict):
            try:
                obj = json.loads(doc)
                ts = obj.get("timestamp") or meta.get("timestamp")
                query = obj.get("user_query", "")
                reflection = obj.get("reflection", "")
                state = obj.get("state") or state_from_meta(meta)
                return ts, query, reflection, state
            except Exception:
                ts = (meta or {}).get("timestamp", "")
                q_match = re.search(r"User\s*Query:\s*(.+)", doc, re.IGNORECASE)
                r_match = re.search(r"Reflection:\s*([\s\S]+)$", doc, re.IGNORECASE)
                query = (q_match.group(1).strip() if q_match else "")
                reflection = (r_match.group(1).strip() if r_match else "")
                state = state_from_meta(meta)
                return ts, query, reflection, state

        entries = []
        for id_, doc, meta in zip(ids, docs, metas):
            ts, query, reflection, state = parse_doc(doc or "", meta or {})
            entries.append({
                "id": id_,
                "timestamp": ts or "",
                "query": query,
                "reflection": reflection,
                "state": state or {"emotions": []},
                "content": doc or "",
                "meta": meta or {}
            })

        entries.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
        return jsonify(entries)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# ------------------------------------------------------------
# Monologue history
    
@app.route("/api/monologue")
def api_monologue():
    try:
        from hippocampus import Hippocampus
        hippo = Hippocampus()
        monologues = hippo.get_recent_monologues(limit=10)  # you can define this helper
        return jsonify({"monologues": monologues})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# ------------------------------------------------------------
# Inspector: current state (from Attention focus)
# ------------------------------------------------------------
@app.get("/api/state")
def api_state():
    try:
        focus = attention.get_focus()
        if not focus:
            return jsonify({"error": "No focus yet"}), 404
        return jsonify(focus), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------
# Inspector: narrative summary + window (from Attention)
# ------------------------------------------------------------
@app.get("/api/narrative")
def api_narrative():
    try:
        summary = attention.get_narrative_summary()
        window = attention.get_narrative_window()
        return jsonify({"summary": summary, "window": window}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# ------------------------------------------------------------
# Memory: recall test
# ------------------------------------------------------------
@app.post("/api/memory/test-recall")
def test_recall():
    """Test recall with a query and show retrieved entries."""
    try:
        query = (request.json or {}).get("query", "test")
        results = hippocampus.recall_with_context(query)

        retrieved_docs = []
        for node in results:
            try:
                text = node.get("text", None) or getattr(node, "text", None) or str(node)
            except Exception:
                text = str(node)[:200]
            retrieved_docs.append({
                "text_preview": text[:250],
                "weight": node.get("weight", 1.0) if isinstance(node, dict) else 1.0
            })

        return jsonify({
            "query": query,
            "retrieved_count": len(results),
            "memories": retrieved_docs
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

# ------------------------------------------------------------
# Run
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("HALCYON_PORT", 5000))
    print(f"[Server] Running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
