# ============================================================
# halcyon_events.py — unified event emitter bridge
# ============================================================
# halcyon_events.py
import json
from queue import Queue
from sse_bus import emit_sse, sse_streams

def broadcast_event(event_type: str, payload: dict):
    """Simple alias for emit_sse to preserve legacy naming."""
    emit_sse(event_type, payload)

import datetime

reflection_stream = Queue()  # this feeds /api/reflection_raw in your web server

def emit_reflection(turn_id, reflection=None, state=None, keywords=None, timestamp=None):
    """Emit reflection events safely — tolerant of missing first-pass data."""
    if reflection is None:
        print(f"[Events] (Reflection skipped for turn {turn_id})")
        return  # no-op when reflection intentionally omitted

    payload = {
        "turn_id": turn_id,
        "timestamp": timestamp or datetime.datetime.now().isoformat(),
        "state": state or {},
        "reflection": reflection,
        "keywords": keywords or [],
    }
    try:
        broadcast_event("reflection", payload)
        print(f"[Events] Emitted reflection (turn {turn_id})")
    except Exception as e:
        print(f"[Events] Reflection emit failed: {e}")




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