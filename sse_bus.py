# ============================================================
# sse_bus.py — simple shared event queue for SSE streaming
# ============================================================

import queue

# Global queue used by the Flask SSE route and the brainstem
reflection_stream = queue.Queue()
