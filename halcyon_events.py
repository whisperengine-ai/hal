# ============================================================
# halcyon_events.py — unified event emitter bridge
# ============================================================
# halcyon_events.py
import json
from queue import Queue
from sse_bus import sse_streams
import datetime

reflection_stream = Queue()  # this feeds /api/reflection_raw in your web server

def emit_reflection(turn_id, reflection, state, keywords=None, timestamp=None):
    payload = {
        "type": "pre_memory_reflection",
        "turn_id": turn_id,
        "timestamp": timestamp,
        "pre_reflection_text": reflection.strip(),
        "pre_reflection_state": state,
        "keywords": keywords or []
    }
    try:
        reflection_stream.put(json.dumps(payload))
        print(f"[Events] Emitted reflection (turn {turn_id})")
    except Exception as e:
        print(f"[Events] Reflection emission failed: {e}")



def emit_attention(turn_id, reflection, response, recalled_memories=None):
    """Send final reflection + response (and optional memory trace) to the attention SSE stream."""
    from sse_bus import sse_streams
    import datetime, json

    payload = {
        "type": "attention_update",
        "turn_id": turn_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "final_reflection": reflection,
        "response": response,
    }

    # 👁️ Include recalled memories if provided
    if recalled_memories:
        payload["recalled_memories"] = recalled_memories

    sse_streams["attention"].put(payload)
    print(f"[Events] Emitted attention ({len(recalled_memories or [])} memories)")

    
def emit_memory(turn_id, memory_summary, metadata):
    payload = {
        "type": "memory_commit",
        "turn_id": turn_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "memory_summary": memory_summary,
        "metadata": metadata
    }
    sse_streams["memory"].put(payload)
    print(f"[Events] Emitted memory for turn {turn_id}")