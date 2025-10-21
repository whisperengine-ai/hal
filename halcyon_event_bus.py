# halcyon_event_bus.py
from queue import Queue

# Shared inter-module communication channels
attention_stream = Queue()
reflection_stream = Queue()
