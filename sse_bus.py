# ============================================================
# sse_bus.py — simple shared event queue for SSE streaming
# ============================================================

from queue import Queue
import json
import re

# Global queue used by the Flask SSE route and the brainstem
sse_streams = {
    "reflection": Queue(),
    "memory": Queue(),
    "attention": Queue(),  # 🩸 new
}

# ============================================================
# Payload Sanitizer
# ============================================================

def sanitize_text_field(text):
    """Clean and format text safely for front-end display."""
    if not isinstance(text, str):
        return text

    # Normalize newlines and trim whitespace
    text = text.strip().replace("\r\n", "\n")

    # Remove excessive backticks unless used for valid triple-fenced blocks
    # e.g. ```json ... ``` remains, but stray backticks are stripped
    code_block_pattern = re.compile(r"```(\w+)?\n[\s\S]*?```", re.MULTILINE)
    preserved_blocks = code_block_pattern.findall(text)

    # Temporarily replace preserved blocks with markers
    placeholders = []
    def preserve_block(match):
        placeholders.append(match.group(0))
        return f"__CODE_BLOCK_{len(placeholders)-1}__"

    text = code_block_pattern.sub(preserve_block, text)
    text = re.sub(r"`{1,2}", "", text)  # remove stray backticks
    # restore preserved code blocks
    for i, block in enumerate(placeholders):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)

    # Escape stray nulls or weird characters
    text = re.sub(r"[\x00-\x09\x0B\x0C\x0E-\x1F]", "", text)

    # Ensure text is UTF-8 safe
    try:
        text.encode("utf-8", "replace").decode("utf-8")
    except Exception:
        text = "[Invalid UTF-8 data removed]"

    return text


def sanitize_payload(data):
    """Clean reflections, responses, or other text fields."""
    if not isinstance(data, dict):
        return data

    clean = data.copy()
    for key in ("reflection", "response", "query", "summary"):
        if key in clean:
            clean[key] = sanitize_text_field(clean[key])

    # Ensure no unserializable objects are in payload
    try:
        json.dumps(clean)
    except Exception:
        clean = {"error": "Payload serialization failure"}

    return clean


# ============================================================
# Event Emitter
# ============================================================

def emit_sse(event_type, data):
    """Put data into the appropriate SSE queue."""
    if event_type not in sse_streams:
        print(f"[SSE BUS] ❌ Unknown event type: {event_type}")
        return

    sanitized = sanitize_payload(data)
    sse_streams[event_type].put(sanitized)
    print(f"[SSE BUS] Event emitted to '{event_type}' :: {sanitized.get('turn_id', '?')}")
