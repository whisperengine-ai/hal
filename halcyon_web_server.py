# ============================================================
# halcyon_web_server.py — Flask bridge for Halcyon Web Console 🧠
# ============================================================
from flask import (
    Flask, request, jsonify, send_from_directory,
    Response, stream_with_context
)
from flask_cors import CORS
import os, time, json, re, datetime, traceback, chromadb
from halcyon_brainstem import Cortex, Thalamus
from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor

# Unified SSE bus
from sse_bus import sse_streams, sanitize_payload

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
CORS(app)

print("[Server] Initializing Halcyon core modules...")
cortex = Cortex()
hippocampus = Hippocampus(cortex)
anchor = TemporalAnchor(hippocampus)
thalamus = Thalamus(cortex, hippocampus, anchor)
anchor.load()
app.cortex, app.hippocampus, app.anchor, app.thalamus = cortex, hippocampus, anchor, thalamus
print("[Server] Initialization complete.")



# ------------------------------------------------------------
# Static UI
# ------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory("web_ui", "index.html")

# ------------------------------------------------------------
# SSE Stream Utility
# ------------------------------------------------------------
def make_sse_stream(queue_name: str):
    """Return a generator that streams sanitized SSE data safely."""
    from flask import stream_with_context
    import sys

    def stream():
        q = sse_streams[queue_name]
        while True:
            try:
                payload = q.get(timeout=1)

                # Defensive check — wait for emotional data to finalize
                if not payload or not isinstance(payload, dict) or not payload.get("state"):
                    print(f"[SSE] Warning: empty state in {queue_name}, delaying emission...")
                    time.sleep(0.25)

                clean = sanitize_payload(payload)
                chunk = f"data: {json.dumps(clean, ensure_ascii=False)}\n\n"
                sys.stdout.flush()  # ensure logs flush immediately
                yield chunk.encode("utf-8")
            except Exception:
                yield b": keepalive\n\n"
                time.sleep(1)

    headers = {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",   # 🚨 disables proxy buffering
        "Transfer-Encoding": "chunked",  # 🚨 ensures immediate flush
    }

    return Response(stream_with_context(stream()), headers=headers)

# ------------------------------------------------------------
# SSE: Reflection (internal monologue)
# ------------------------------------------------------------
@app.route("/api/reflection_raw")
def api_reflection_raw():
    return make_sse_stream("reflection")

# ------------------------------------------------------------
# SSE: Attention (final reflection + response)
# ------------------------------------------------------------
@app.route("/api/attention_feed")
def api_attention_feed():
    return make_sse_stream("attention")

# ------------------------------------------------------------
# Manual test endpoints
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
        "reflection": "Test final reflection from /api/test-attention",
        "response": "This is only a test.",
        "state": {"emotions": [{"name": "Stability", "intensity": 0.9}]}
    })
    return jsonify({"status": "ok"})

# ------------------------------------------------------------
# Attention snapshot
# ------------------------------------------------------------
@app.get("/api/attention")
def api_attention_snapshot():
    try:
        buffer = thalamus.get_attention_window()
        return jsonify(buffer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------------------------------------
# Chat turn
# ------------------------------------------------------------
@app.post("/api/turn")
def api_turn():
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
# Memory inspection
# ------------------------------------------------------------
@app.get("/api/memories")
def api_memories():
    """Return recent reflections only (clean view, no fake emotion JSON)."""
    try:
        client = hippocampus.client
        coll = hippocampus.coll
        results = coll.get(include=["documents", "metadatas"], limit=200)

        ids = results.get("ids", [])
        docs = results.get("documents", [])
        metas = results.get("metadatas", [])
        entries = []

        for id_, doc, meta in zip(ids, docs, metas):
            try:
                # Try parsing as JSON (modern memory format)
                obj = json.loads(doc)
                ts = obj.get("timestamp") or meta.get("timestamp")
                query = obj.get("user_query", "")
                reflection = obj.get("reflection", "")
            except Exception:
                # Fallback for legacy raw-text memories
                ts = (meta or {}).get("timestamp", "")
                q_match = re.search(r"USER\s*QUERY:\s*(.+)", doc, re.IGNORECASE)
                r_match = re.search(r"INTERNAL\s*MONOLOGUE:\s*([\s\S]+?)MODEL\s*RESPONSE:", doc, re.IGNORECASE)
                query = (q_match.group(1).strip() if q_match else "")
                reflection = (r_match.group(1).strip() if r_match else "")

            # Skip emotion and keyword parsing completely
            entries.append({
                "id": id_,
                "timestamp": ts or "",
                "query": query.strip(),
                "reflection": reflection.strip(),
            })

        entries.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
        return jsonify(entries)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# Memory recall test
# ------------------------------------------------------------
@app.post("/api/memory/test-recall")
def test_recall():
    try:
        query = (request.json or {}).get("query", "test")
        results = hippocampus.recall_with_context(query)
        retrieved = []
        for node in results:
            try:
                text = node.get("text", None) or getattr(node, "text", None) or str(node)
            except Exception:
                text = str(node)[:200]
            retrieved.append({
                "text_preview": text[:250],
                "weight": node.get("weight", 1.0) if isinstance(node, dict) else 1.0
            })
        return jsonify({"query": query, "retrieved_count": len(results), "memories": retrieved})
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
    
#------------------------------------------------------------
# Memory injection
# ------------------------------------------------------------

@app.post("/api/memory/inject")
def api_inject_memory():
    try:
        data = request.get_json(force=True)
        memories = data.get("memories", [])
        thalamus.anchor.inject_memories(memories)
        return jsonify({"status": "ok", "injected": len(memories)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# Run
# ------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("HALCYON_PORT", 5000))
    print(f"[Server] Running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
