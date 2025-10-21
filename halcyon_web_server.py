# halcyon_web_server.py — Flask bridge for Halcyon Web Console 🧠
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import datetime, time, os, traceback
import json, re, traceback
import chromadb
from flask import jsonify

from halcyon_brainstem import Cortex, Thalamus
from hippocampus import Hippocampus

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

@app.route("/")
def index():
    """Serve the frontend."""
    return send_from_directory("web_ui", "index.html")

from flask import Flask, Response, stream_with_context
import queue

# global queue for streaming reflections
reflection_stream = queue.Queue()

@app.route("/api/reflection_raw", methods=["POST"])
def api_reflection_raw():
    """Handles pre-memory reflection emission (internal monologue coherence)."""
    try:
        data = request.get_json(force=True)
        turn_id = data.get("turn_id")
        state = data.get("state", {})
        reflection = data.get("reflection", "")

        payload = {
            "turn_id": turn_id,
            "type": "pre_memory_reflection",
            "pre_reflection_state": state,
            "pre_reflection_text": reflection
        }

        # broadcast to your front-end (SSE or WebSocket)
        reflection_stream.put(payload)
        print(f"[API] Emitted internal monologue window for turn {turn_id}")

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"[API ERROR] reflection_raw: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/reflection_raw", methods=["GET"])
def stream_reflections():
    """Stream internal monologue reflections live to the UI via SSE."""
    def event_stream():
        while True:
            payload = reflection_stream.get()  # waits for new reflection
            msg = f"data: {json.dumps(payload)}\n\n"
            yield msg

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

# ============================================================
# 🩸 Attention Layer Stream (SSE)
# ============================================================
from flask import Response, stream_with_context
import queue

attention_stream = queue.Queue()

@app.route("/api/attention_feed")
def api_attention_feed():
    """Server-Sent Events feed for attention window (final reflection + response)."""
    def stream():
        while True:
            payload = attention_stream.get()
            yield f"data: {json.dumps(payload)}\n\n"
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


@app.route("/api/memories", methods=["GET"])
def api_memories():
    """Return all stored memories as normalized objects for the UI."""
    import json, re, traceback
    import chromadb

    def parse_doc(doc: str, meta: dict):
        """Parse the stored document into fields (timestamp, query, reflection, state)."""
        # Try JSON-formatted memory first
        try:
            obj = json.loads(doc)
            ts = obj.get("timestamp") or meta.get("timestamp")
            query = obj.get("user_query", "")
            reflection = obj.get("reflection", "")
            state = obj.get("state") or state_from_meta(meta)
            return ts, query, reflection, state
        except Exception:
            pass
        # Fallback for plain text format
        ts = (meta or {}).get("timestamp", "")
        q_match = re.search(r"User\s*Query:\s*(.+)", doc, re.IGNORECASE)
        r_match = re.search(r"Reflection:\s*([\s\S]+)$", doc, re.IGNORECASE)
        query = (q_match.group(1).strip() if q_match else "")
        reflection = (r_match.group(1).strip() if r_match else "")
        state = state_from_meta(meta)
        return ts, query, reflection, state

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
    """Test recall with a query and see what comes back."""
    try:
        query = request.json.get("query", "test")
        results = hippocampus.recall(query)
        
        retrieved_docs = []
        for node in results:
            try:
                text = node.get_content()
            except:
                text = str(node)[:150]
            retrieved_docs.append({
                "text_preview": text[:150]
            })
        
        return {
            "query": query,
            "retrieved_count": len(results),
            "memories": retrieved_docs
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }, 500


if __name__ == "__main__":
    port = int(os.getenv("HALCYON_PORT", 5000))
    print(f"[Server] Running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
