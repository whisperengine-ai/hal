import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
import queue # <--- NEW: For thread-safe communication

# Import your core modules
from cortex import Cortex
from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor
from thalamus import Thalamus

class HalcyonTkinterUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Halcyon Memory Workbench")
        self.geometry("1000x800")
        
        # Initialize core components
        self.cortex = Cortex()
        self.hippo = Hippocampus(self.cortex)
        self.anchor = TemporalAnchor(hippocampus=self.hippo)
        
        # Ensure your Thalamus constructor is updated to accept bus=None if SignalBus is stripped
        self.thalamus = Thalamus(self.cortex, self.hippo, self.anchor) 
        
        # 🛠️ CRITICAL FIX: Ensure the TemporalAnchor uses the functional recall method
        self.anchor.recall = self.hippo.recall_with_context

        # Threading Queue for results
        self.result_queue = queue.Queue()

        self._build_ui()
        
        # Start the queue checker loop in the main thread
        self.after(100, self._check_queue)
        print("[UI] Tkinter event loop started.")

    # --- UI Building ---
    def _build_ui(self):
        # Configure layout weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Main Chat Area
        self.grid_columnconfigure(1, weight=1) # Memory Control Panel

        # Main Content Frame (Chat/Reflection)
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=0)
        main_frame.grid_columnconfigure(0, weight=1)

        # 1. Reflection/State Display
        ttk.Label(main_frame, text="🧠 Inner Reflection", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.reflection_box = scrolledtext.ScrolledText(main_frame, height=10, state='disabled', wrap=tk.WORD, bg='#f0f0f0')
        self.reflection_box.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # 2. Response Display
        ttk.Label(main_frame, text="💬 Halcyon Response", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky="w", pady=(0, 5))
        self.response_box = scrolledtext.ScrolledText(main_frame, height=15, state='disabled', wrap=tk.WORD)
        self.response_box.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # 3. Input Row
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_entry.bind('<Return>', lambda event: self._send_query())
        
        send_button = ttk.Button(input_frame, text="Send", command=self._send_query)
        send_button.grid(row=0, column=1, sticky="e")

        # Memory Control Panel Frame
        memory_frame = ttk.Frame(self)
        memory_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        # TODO: Add specific controls for Pinning, Context Injection, and Memory List here

        ttk.Label(memory_frame, text="💾 Memory Controls", font=('Arial', 12, 'bold')).pack(fill='x', pady=5)
        self.memory_list = tk.Listbox(memory_frame, height=30)
        self.memory_list.pack(fill='both', expand=True, pady=(0, 10))
        ttk.Button(memory_frame, text="Load Recent Memories", command=self._load_memory_preview).pack(fill='x', pady=2)
        ttk.Button(memory_frame, text="Inject Context", command=self._inject_context).pack(fill='x', pady=2)
        ttk.Button(memory_frame, text="Pin Memory", command=self._pin_memory).pack(fill='x', pady=2)

    # --- Worker Thread ---
    def _run_thalamus_turn(self, query):
        turn_id = int(time.time())
        try:
            # 💡 Thalamus call is now run in the background thread
            response_text = self.thalamus.process_turn(
                user_query=query, 
                turn_id=turn_id, 
                task_id=f"TK_{turn_id}"
            )
            
            # Parse the strict LLM output
            state, reflection, _ = self.cortex._extract_sections(response_text)
            import re
            m_response = re.search(r'RESPONSE\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', response_text, flags=re.S | re.I)
            final_response = m_response.group(1).strip() if m_response else response_text

            # Push the successful result to the queue
            self.result_queue.put({
                "success": True, 
                "state": state, 
                "reflection": reflection, 
                "response": final_response
            })
            
        except Exception as e:
            # Push the error to the queue
            self.result_queue.put({"success": False, "error": str(e)})

    # --- Main Thread Handlers ---
    def _send_query(self):
        query = self.input_entry.get().strip()
        if not query:
            return
        self.input_entry.delete(0, tk.END)

        # Clear and update boxes to show processing state
        self._update_text_box(self.reflection_box, "Status: Processing...\nReflection: Connecting to LLM.", clear=True)
        self._update_text_box(self.response_box, "Halcyon is thinking...", clear=True)
        
        # Start the blocking task in a new thread
        worker_thread = threading.Thread(target=self._run_thalamus_turn, args=(query,), daemon=True)
        worker_thread.start()

    def _check_queue(self):
        """Checks the queue for results from the worker thread."""
        try:
            result = self.result_queue.get_nowait()
            if result["success"]:
                self._update_text_box(
                    self.reflection_box, 
                    f"STATE:\n{json.dumps(result['state'], indent=2)}\n\nREFLECTION:\n{result['reflection']}", 
                    clear=True
                )
                self._update_text_box(self.response_box, result['response'], clear=True)
            else:
                error_msg = f"THALAMUS ERROR: {result['error']}"
                self._update_text_box(self.response_box, error_msg, clear=True)
                print(error_msg)
        except queue.Empty:
            pass
        
        # Schedule the next check
        self.after(100, self._check_queue)

    def _update_text_box(self, box, text, clear=False):
        box.config(state='normal')
        if clear:
            box.delete('1.0', tk.END)
        box.insert(tk.END, text + "\n")
        box.config(state='disabled')
        box.see(tk.END) # Scroll to bottom

    # --- Memory Control Stubs (To be implemented later) ---
    def _load_memory_preview(self):
        # Placeholder to load recent memories from self.hippo or self.anchor
        self.memory_list.delete(0, tk.END)
        recent_turns = self.anchor.get_recent(5)
        self.memory_list.insert(tk.END, "--- Recent Context ---")
        for turn in recent_turns:
             self.memory_list.insert(tk.END, f"[Live] {turn['user_query'][:30]}...")
        # Add a mechanism to load long-term memories here
        self.memory_list.insert(tk.END, "--- Long-Term (Example) ---")
        self.memory_list.insert(tk.END, "Click memory to see full text.")

    def _inject_context(self):
        # Logic to take selected memory from listbox and add it to anchor.manual_injections
        pass

    def _pin_memory(self):
        # Logic to use hippocampus.promote_to_core or adjust_weight on selected memory
        pass

if __name__ == "__main__":
    app = HalcyonTkinterUI()
    app.mainloop()