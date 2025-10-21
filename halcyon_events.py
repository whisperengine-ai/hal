# ============================================================
# halcyon_events.py — unified event emitter bridge
# ============================================================
from sse_bus import sse_streams
import datetime, json

def emit_reflection(turn_id, state, reflection):
    """Send internal monologue to the reflection SSE stream."""
    payload = {
        "type": "pre_memory_reflection",
        "turn_id": turn_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "pre_reflection_state": state,
        "pre_reflection_text": reflection,
    }
    sse_streams["reflection"].put(payload)  # 👈 important: use 'reflection', not 'attention'


def emit_attention(turn_id, reflection, response):
    """Send final reflection + response to the attention SSE stream."""
    payload = {
        "type": "attention_update",
        "turn_id": turn_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "final_reflection": reflection,
        "response": response,
    }
    sse_streams["attention"].put(payload)  # 👈 final output only here
    
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