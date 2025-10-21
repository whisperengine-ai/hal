# ============================================================
# sse_bus.py — simple shared event queue for SSE streaming
# ============================================================

from queue import Queue

# Global queue used by the Flask SSE route and the brainstem
sse_streams = {
    "reflection": Queue(),
    "memory": Queue(),
    "attention": Queue(),  # 🩸 new
}

def emit_sse(event_type, data):
    """Put data into the appropriate SSE queue."""
    if event_type in sse_streams:
        sse_streams[event_type].put(data)
        print(f"[SSE BUS] Event emitted to '{event_type}' :: {data.get('turn_id', '?')}")

