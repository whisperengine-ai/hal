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

def emit_sse(event_type: str, data: dict):
    """Put data into the appropriate SSE queue."""
    if event_type in sse_streams:
        sse_streams[event_type].put(data)
        print(f"[SSE BUS] Emitted {event_type} event.")
    else:
        print(f"[SSE BUS] ⚠️ Unknown event type: {event_type}")
