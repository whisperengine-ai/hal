# ============================================================
# halcyon_ui.py — Unified PyQt Runtime + Interface for Halcyon
# ============================================================

import sys, time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QLineEdit
)
from signal_bus import SignalBus
from cortex import Cortex
from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor
from thalamus import Thalamus


class HalcyonUI(QWidget):
    """Realtime visualization and runtime driver for Halcyon."""

    def __init__(self):
        super().__init__()
        # --- Initialize core runtime components ---
        self.bus = SignalBus()
        self.cortex = Cortex()
        self.hippo = Hippocampus(self.cortex)
        self.anchor = TemporalAnchor(hippocampus=self.hippo)
        self.thalamus = Thalamus(self.cortex, self.hippo, self.anchor, self.bus)
        self.thalamus.bind_temporal_anchor(self.anchor)

        # --- Connect signal bus to handlers ---
        self.bus.reflection_update.connect(self._on_reflection)
        self.bus.attention_update.connect(self._on_attention)
        self.bus.memory_update.connect(self._on_memory)

        # --- Window setup ---
        self.setWindowTitle("Halcyon Core Monitor 🧠")
        self.setGeometry(100, 100, 1200, 700)
        self._build_ui()

        print("[HalcyonUI] Runtime initialized and signal bus connected.")

    # ============================================================
    # UI Layout
    # ============================================================
    def _build_ui(self):
        layout = QVBoxLayout()
        header = QLabel("<h2>🧠 Halcyon Runtime Monitor</h2>")
        header.setAlignment(Qt.AlignCenter)

        # --- Reflection panel ---
        self.reflection_box = QTextEdit(readOnly=True)
        self.reflection_box.setPlaceholderText("Waiting for reflection updates...")

        # --- Attention panel ---
        self.attention_box = QTextEdit(readOnly=True)
        self.attention_box.setPlaceholderText("Awaiting attention updates...")

        # --- Memory panel ---
        self.memory_box = QTextEdit(readOnly=True)
        self.memory_box.setPlaceholderText("No memory commits yet...")

        # --- Input row ---
        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your query here...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_query)
        self.input_box.returnPressed.connect(self._send_query)
        input_row.addWidget(self.input_box)
        input_row.addWidget(self.send_button)

        # --- Clear button ---
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_all)

        # --- Assemble layout ---
        layout.addWidget(header)
        layout.addWidget(QLabel("<b>Reflection</b>"))
        layout.addWidget(self.reflection_box)
        layout.addWidget(QLabel("<b>Attention</b>"))
        layout.addWidget(self.attention_box)
        layout.addWidget(QLabel("<b>Memory</b>"))
        layout.addWidget(self.memory_box)
        layout.addLayout(input_row)
        layout.addWidget(clear_btn)
        self.setLayout(layout)

        # --- Style ---
        for box in [self.reflection_box, self.attention_box, self.memory_box]:
            box.setStyleSheet("""
                QTextEdit {
                    background-color: #0f111a;
                    color: #d3d7e8;
                    border: 1px solid #444;
                    font-family: Consolas, monospace;
                    font-size: 12pt;
                    padding: 8px;
                }
            """)
        self.setStyleSheet("background-color: #1a1c25; color: #e3e3e3;")

    # ============================================================
    # Signal Slots
    # ============================================================
    def _on_reflection(self, data: dict):
        text = f"[Reflection Update]\nTurn: {data.get('turn_id')}\n{data.get('reflection')}\n\n"
        self.reflection_box.append(text)

    def _on_attention(self, data: dict):
        text = f"[Attention Update]\nTurn: {data.get('turn_id')}\n{data.get('response')}\n\n"
        self.attention_box.append(text)

    def _on_memory(self, data: dict):
        text = f"[Memory Commit]\n{data.get('timestamp')} :: {data.get('query')}\n{data.get('reflection')}\n\n"
        self.memory_box.append(text)

    def clear_all(self):
        self.reflection_box.clear()
        self.attention_box.clear()
        self.memory_box.clear()
        print("[HalcyonUI] Cleared all panels.")

    # ============================================================
    # Input Handler
    # ============================================================
    def _send_query(self):
        """Send user input to Thalamus and clear the field."""
        query = self.input_box.text().strip()
        if not query:
            return
        self.input_box.clear()

        turn_id = int(time.time())
        print(f"[UI] Sending query to Thalamus: {query!r}")
        try:
            response = self.thalamus.process_turn(query, turn_id, f"UI_{turn_id}")
            print(f"[UI] Thalamus responded: {response[:120]}...")
        except Exception as e:
            print(f"[UI] ❌ Error during Thalamus loop: {e}")


# ============================================================
# Runtime entrypoint
# ============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = HalcyonUI()
    ui.show()
    print("[HalcyonUI] Runtime loop started.")
    sys.exit(app.exec_())
