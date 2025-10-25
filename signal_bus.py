# ============================================================
# signal_bus.py — Halcyon Internal Signal System 🧠
# ============================================================

from PyQt5.QtCore import QObject, pyqtSignal

class SignalBus(QObject):
    """
    Centralized signal system for the Halcyon runtime.
    Replaces the Flask SSE emitter model. 
    All major subsystems (Thalamus, Cortex, Hippocampus, UI)
    can emit and listen to these signals.
    """

    # Cognitive update channels
    reflection_update = pyqtSignal(dict)   # emitted when new reflection generated
    attention_update = pyqtSignal(dict)    # emitted when attention focus changes
    memory_update = pyqtSignal(dict)       # emitted when new memory committed

    # Optional status/heartbeat channels
    status_update = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        print("[SignalBus] Initialized with PyQt signal channels ready.")

    # Debug helper
    def debug_emit(self, channel: str, data: dict):
        """Helper to test signal emissions manually."""
        if hasattr(self, channel):
            getattr(self, channel).emit(data)
            print(f"[SignalBus] 🔔 Emitted test event on {channel}")
        else:
            print(f"[SignalBus] ⚠️ Unknown signal: {channel}")
