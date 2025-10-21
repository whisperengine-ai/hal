# halcyon_web_server.py — Flask bridge for Halcyon Web Console 🧠
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import datetime, time, os, traceback
import json, re, traceback
import chromadb
from flask import jsonify

from halcyon_brainstem import Cortex, Thalamus
from hippocampus import Hippocampus

from queue import Queue
attention_stream = Queue()


def state_from_meta(meta):
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

app = Flask(__name__, static_folder="web_ui", static_url_path="")
CORS(app)  # Allow local browser requests

# --- Initialize runtime ---
print("[Server] Initializing Halcyon core modules...")
cortex = Cortex()
hippocampus = Hippocampus(cortex)
thalamus = Thalamus(cortex, hippocampus)
print("[Server] Initialization complete.")

@app.route("/api/test-attention")
def api_test_attention():
    from sse_bus import emit_sse
    emit_sse("attention", {
        "type": "attention_update",
        "turn_id": 999,
        "final_reflection": "Test reflection from /api/test-attention",
        "response": "This is only a test.",
        "timestamp": datetime.datetime.now().isoformat()
    })
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory("web_ui", "index.html")

from flask import Flask, Response, stream_with_context
import queue

# global queue for streaming reflections
reflection_stream = queue.Queue()


from flask import Response, stream_with_context
import json, time
from sse_bus import sse_streams

@app.route("/api/reflection_raw")
def api_reflection_raw():
    """Continuous event stream for internal monologue (SSE)."""
    def stream():
        q = sse_streams["reflection"]
        while True:
            try:
                payload = q.get(timeout=1)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception:
                # keep-alive heartbeat
                yield ":\n\n"
                time.sleep(1)
    return Response(stream_with_context(stream()), mimetype="text/event-stream")


def emit_reflection(turn_id: int, state: dict, reflection: str):
    """Emit a pre-memory reflection event to the reflection SSE stream."""
    payload = {
        "turn_id": turn_id,
        "type": "pre_memory_reflection",
        "pre_reflection_state": state,
        "pre_reflection_text": reflection,
        "timestamp": datetime.datetime.now().isoformat()
    }
    sse_streams["reflection"].put(payload)
    print(f"[SSE BUS] Emitted reflection update for turn {turn_id}")

# ============================================================
# 🩸 Attention Layer Stream (SSE)
# ============================================================
from flask import Response, stream_with_context
import json, time
from sse_bus import sse_streams

@app.route("/api/attention_feed")
def api_attention_feed():
    """Continuous event stream for attention data (SSE)."""
    def stream():
        q = sse_streams["attention"]
        while True:
            try:
                payload = q.get(timeout=1)
                yield f"data: {json.dumps(payload)}\n\n"
            except Exception:
                # Keep connection alive
                yield ":\n\n"
                time.sleep(1)
    return Response(stream_with_context(stream()), mimetype="text/event-stream")


def emit_attention(turn_id: int, final_reflection: str, response: str):
    """Called by Thalamus after final reflection + response."""
    payload = {
        "turn_id": turn_id,
        "type": "attention_update",
        "final_reflection": final_reflection,
        "response": response,
        "timestamp": datetime.datetime.now().isoformat()
    }
    attention_stream.put(payload)
    print(f"[API] Emitted attention update for turn {turn_id}")



@app.route("/api/attention", methods=["GET"])
def api_attention():
    """Return current working attention window (short-term context)."""
    try:
        buffer = thalamus.get_attention_window()  # Implement this in Thalamus
        return jsonify(buffer), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.post("/api/turn")
def api_turn():
    """Handle chat turns."""
    try:
        data = request.get_json(force=True)
        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Empty query"}), 400

        turn_id = int(time.time())
        task_id = f"WEB_UI_{turn_id}"

        print(f"[API] Processing turn: {turn_id} :: {query[:50]}...")
        response = thalamus.process_turn(query, turn_id, task_id)

        return jsonify({"response": response, "turn_id": turn_id})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
# ============================================================
# MEMORY INSPECTION + TESTING
# ============================================================

@app.route("/api/memories", methods=["GET"])
def api_memories():
    """Return all stored memories, including emotion + keyword metadata."""
    import json, re, traceback, chromadb

    def parse_doc(doc: str, meta: dict):
        """Parse stored document into fields (timestamp, query, reflection, state, keywords)."""
        try:
            obj = json.loads(doc)
            ts = obj.get("timestamp") or meta.get("timestamp")
            query = obj.get("user_query", "")
            reflection = obj.get("reflection", "")
            state = obj.get("state") or state_from_meta(meta)
        except Exception:
            ts = (meta or {}).get("timestamp", "")
            q_match = re.search(r"USER\s*QUERY:\s*(.+)", doc, re.IGNORECASE)
            r_match = re.search(r"INTERNAL\s*MONOLOGUE:\s*([\s\S]+?)MODEL\s*RESPONSE:", doc, re.IGNORECASE)
            query = (q_match.group(1).strip() if q_match else "")
            reflection = (r_match.group(1).strip() if r_match else "")
            state = state_from_meta(meta)

        # --- Extract keyword list from metadata ---
        keywords = []
        for k, v in meta.items():
            if k.startswith("keyword_") and v:
                keywords.append(v)
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
            meta = meta or {}
            ts, query, reflection, state, keywords = parse_doc(doc or "", meta or {})
            entries.append({
                "id": id_,
                "timestamp": ts or "",
                "query": query,
                "reflection": reflection,
                "state": state or {"emotions": []},
                "keywords": keywords,
                "content": (doc or ""),
                "meta": meta or {}
            })

        # Sort newest first
        entries.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
        return jsonify(entries)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/inspect', methods=['GET'])
def inspect_memory():
    """List all stored memories from persistent Halcyon memory."""
    try:
        client = chromadb.PersistentClient(path="./memory_journals/halcyon_persistent")
        coll = client.get_collection("episodic_memory")
        results = coll.get(include=["documents", "metadatas"], limit=200)
        ids = results.get("ids", list(range(len(results.get("documents", [])))))  # fallback IDs
        docs = results.get("documents", []) or []
        metas = results.get("metadatas", []) or []

        def parse_doc(doc: str, meta: dict):
            """Parse stored document into fields (timestamp, query, reflection, state)."""
            # Try JSON path first
            try:
                obj = json.loads(doc)
                ts = obj.get("timestamp") or meta.get("timestamp")
                query = obj.get("user_query", "")
                reflection = obj.get("reflection", "")
                state = obj.get("state") or state_from_meta(meta)
                return ts, query, reflection, state
            except Exception:
                pass
            # Fallback for older/plain entries
            ts = (meta or {}).get("timestamp", "")
            q_match = re.search(r"User\s*Query:\s*(.+)", doc, re.IGNORECASE)
            r_match = re.search(r"Reflection:\s*([\s\S]+)$", doc, re.IGNORECASE)
            query = (q_match.group(1).strip() if q_match else "")
            reflection = (r_match.group(1).strip() if r_match else "")
            state = state_from_meta(meta)
            return ts, query, reflection, state

        entries = []
        for id_, doc, meta in zip(ids, docs, metas):
            meta = meta or {}
            ts, query, reflection, state = parse_doc(doc or "", meta or {})
            entries.append({
                "id": id_,
                "timestamp": ts or "",
                "query": query,
                "reflection": reflection,
                "state": state or {"emotions": []},
                "content": (doc or ""),
                "meta": meta or {}
            })

        # Sort newest-first by timestamp
        entries.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
        return jsonify(entries)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/memory/test-recall', methods=['POST'])
def test_recall():
    """Test memory recall and visualize retrieved entries."""
    try:
        query = request.json.get("query", "test")

        # Use recall_with_context instead of the old recall()
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
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("HALCYON_PORT", 5000))
    print(f"[Server] Running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
