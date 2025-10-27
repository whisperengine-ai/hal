import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import json
import queue
import re

# Import your core modules
from cortex import Cortex
from hippocampus import Hippocampus
from temporal_anchor import TemporalAnchor
from thalamus import Thalamus

class HalcyonTkinterUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Halcyon Memory Workbench")
        self.geometry("1400x900")
        
        # Initialize core components
        self.cortex = Cortex()
        self.hippo = Hippocampus(self.cortex)
        self.anchor = TemporalAnchor(hippocampus=self.hippo)
        self.thalamus = Thalamus(self.cortex, self.hippo, self.anchor)
        
        # Ensure TemporalAnchor uses functional recall
        self.anchor.recall = self.hippo.recall_with_context

        # Threading Queue
        self.result_queue = queue.Queue()
        
        # Memory data storage for detail view
        self.current_memory_data = []

        self._build_ui()
        
        # Start queue checker
        self.after(100, self._check_queue)
        print("[UI] Tkinter event loop started.")

    # ========== UI Building ==========
    def _build_ui(self):
        """Build tabbed interface"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Tab 1: Chat
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="💬 Chat")
        self._build_chat_tab()
        
        # Tab 2: Memory Workspace
        self.memory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_tab, text="🧠 Memory Workspace")
        self._build_memory_tab()
        
        # Tab 3: Settings
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        self._build_settings_tab()

    # ========== TAB 1: CHAT ==========
    def _build_chat_tab(self):
        """Original chat interface"""
        self.chat_tab.grid_rowconfigure(0, weight=1)
        self.chat_tab.grid_rowconfigure(1, weight=1)
        self.chat_tab.grid_rowconfigure(2, weight=0)
        self.chat_tab.grid_columnconfigure(0, weight=1)

        # Reflection box
        ttk.Label(self.chat_tab, text="🧠 Inner Reflection", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky="w", pady=(10, 5), padx=10)
        self.reflection_box = scrolledtext.ScrolledText(self.chat_tab, height=10, state='disabled', wrap=tk.WORD, bg='#f0f0f0')
        self.reflection_box.grid(row=0, column=0, sticky="nsew", pady=(0, 10), padx=10)

        # Response box
        ttk.Label(self.chat_tab, text="💬 Halcyon Response", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky="w", pady=(0, 5), padx=10)
        self.response_box = scrolledtext.ScrolledText(self.chat_tab, height=15, state='disabled', wrap=tk.WORD)
        self.response_box.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=10)

        # Input row
        input_frame = ttk.Frame(self.chat_tab)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_entry.bind('<Return>', lambda event: self._send_query())
        
        send_button = ttk.Button(input_frame, text="Send", command=self._send_query)
        send_button.grid(row=0, column=1, sticky="e")

    # ========== TAB 2: MEMORY WORKSPACE ==========
    def _build_memory_tab(self):
        """Memory workspace with working + anchor windows + detail pane"""
        self.memory_tab.grid_rowconfigure(0, weight=1)
        self.memory_tab.grid_columnconfigure(0, weight=1)
        self.memory_tab.grid_columnconfigure(1, weight=1)

        # Left side: Memory windows (working + anchor)
        left_frame = ttk.Frame(self.memory_tab)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_frame.grid_rowconfigure(0, weight=0)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(2, weight=0)
        left_frame.grid_rowconfigure(3, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Working Window
        ttk.Label(left_frame, text="📋 Working Window (Live)", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.working_listbox = tk.Listbox(left_frame, height=12)
        self.working_listbox.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.working_listbox.bind('<<ListboxSelect>>', lambda e: self._on_memory_select(e, 'working'))

        # Visual separator
        ttk.Separator(left_frame, orient='horizontal').grid(row=2, column=0, sticky="ew", pady=10)

        # Anchor Window
        ttk.Label(left_frame, text="🔗 Anchor Window (History)", font=('Arial', 11, 'bold')).grid(row=3, column=0, sticky="w", pady=(0, 5))
        self.anchor_listbox = tk.Listbox(left_frame, height=12)
        self.anchor_listbox.grid(row=4, column=0, sticky="nsew")
        self.anchor_listbox.bind('<<ListboxSelect>>', lambda e: self._on_memory_select(e, 'anchor'))

        # Right side: Detail pane + controls
        right_frame = ttk.Frame(self.memory_tab)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        # Detail pane
        ttk.Label(right_frame, text="📖 Memory Details", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.detail_box = scrolledtext.ScrolledText(right_frame, state='disabled', wrap=tk.WORD, bg='#f5f5f5')
        self.detail_box.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="📌 Pin", command=self._pin_memory_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="💉 Inject", command=self._inject_memory_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="🔄 Refresh", command=self._refresh_memory_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="❌ Delete", command=self._delete_memory_workspace).pack(side=tk.LEFT, padx=2)

    # ========== TAB 3: SETTINGS ==========
    def _build_settings_tab(self):
        """Placeholder settings tab"""
        ttk.Label(self.settings_tab, text="Settings (Coming Soon)", font=('Arial', 12, 'bold')).pack(padx=20, pady=20)
        ttk.Label(self.settings_tab, text="Future home for:\n- Model selection\n- Temperature tuning\n- Memory parameters\n- Guardian settings").pack(padx=20, pady=20)

    # ========== CHAT TAB LOGIC ==========
    def _send_query(self):
        """Send query to Thalamus"""
        query = self.input_entry.get().strip()
        if not query:
            return
        self.input_entry.delete(0, tk.END)

        self._update_text_box(self.reflection_box, "Status: Processing...", clear=True)
        self._update_text_box(self.response_box, "Halcyon is thinking...", clear=True)
        
        worker_thread = threading.Thread(target=self._run_thalamus_turn, args=(query,), daemon=True)
        worker_thread.start()

    def _run_thalamus_turn(self, query):
        """Run turn in background thread"""
        turn_id = int(time.time())
        try:
            response_text = self.thalamus.process_turn(
                user_query=query, 
                turn_id=turn_id, 
                task_id=f"TK_{turn_id}"
            )
            
            state, reflection, _ = self.cortex._extract_sections(response_text)
            m_response = re.search(r'RESPONSE\s*:\s*(.+?)(?:\n[A-Z ]{3,}?:|\Z)', response_text, flags=re.S | re.I)
            final_response = m_response.group(1).strip() if m_response else response_text

            self.result_queue.put({
                "success": True, 
                "state": state, 
                "reflection": reflection, 
                "response": final_response
            })
            
        except Exception as e:
            self.result_queue.put({"success": False, "error": str(e)})

    def _check_queue(self):
        """Check for results from worker thread"""
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
        
        self.after(100, self._check_queue)

    def _update_text_box(self, box, text, clear=False):
        """Update text in scrolled text widget"""
        box.config(state='normal')
        if clear:
            box.delete('1.0', tk.END)
        box.insert(tk.END, text + "\n")
        box.config(state='disabled')
        box.see(tk.END)

    # ========== MEMORY WORKSPACE LOGIC ==========
    def _refresh_memory_workspace(self):
        """Load working and anchor windows"""
        self.working_listbox.delete(0, tk.END)
        self.anchor_listbox.delete(0, tk.END)
        self.current_memory_data = []

        # Working window
        working = self.anchor.get_recent(10)
        for i, turn in enumerate(working):
            snippet = turn['user_query'][:50].replace('\n', ' ')
            self.working_listbox.insert(tk.END, f"[W{i+1}] {snippet}...")
            self.current_memory_data.append(('working', turn))

        # Anchor window
        anchor_data = self.anchor.anchor_window
        for i, entry in enumerate(anchor_data):
            snippet = entry.get('query', '')[:50].replace('\n', ' ')
            self.anchor_listbox.insert(tk.END, f"[A{i+1}] {snippet}...")
            self.current_memory_data.append(('anchor', entry))

    def _on_memory_select(self, event, source):
        """Handle memory selection"""
        if source == 'working':
            selection = self.working_listbox.curselection()
        else:
            selection = self.anchor_listbox.curselection()
        
        if not selection:
            return

        # Find corresponding data
        listbox_index = selection[0]
        for i, (src, data) in enumerate(self.current_memory_data):
            if src == source and i == listbox_index:
                self._display_memory_details(data)
                break

    def _display_memory_details(self, memory):
        """Show memory details in detail pane"""
        output = "\n--- MEMORY DETAILS ---\n"
        
        if isinstance(memory, dict):
            # Extract common fields
            query = memory.get('user_query', memory.get('query', 'N/A'))
            reflection = memory.get('reflection', 'N/A')
            response = memory.get('response', 'N/A')
            timestamp = memory.get('timestamp', 'N/A')
            
            # State info
            state = memory.get('state', {})
            if isinstance(state, dict) and 'emotions' in state:
                output += "\n--- STATE ---\n"
                for emotion in state.get('emotions', []):
                    name = emotion.get('name', 'N/A')
                    intensity = emotion.get('intensity', 0.0)
                    etype = emotion.get('type', 'unknown')
                    output += f"  {etype}: {name} ({intensity:.2f})\n"
            
            output += f"\n--- TIMESTAMP ---\n{timestamp}\n"
            output += f"\n--- QUERY ---\n{query}\n"
            output += f"\n--- REFLECTION ---\n{reflection}\n"
            output += f"\n--- RESPONSE ---\n{response}\n"
        
        self._update_detail_box(output)

    def _update_detail_box(self, text):
        """Update detail pane"""
        self.detail_box.config(state='normal')
        self.detail_box.delete('1.0', tk.END)
        self.detail_box.insert(tk.END, text)
        self.detail_box.config(state='disabled')

    def _pin_memory_workspace(self):
        """Pin selected memory (increase weight)"""
        self._update_detail_box("[Pin] Feature coming soon")

    def _inject_memory_workspace(self):
        """Inject memory into anchor"""
        self._update_detail_box("[Inject] Feature coming soon")

    def _delete_memory_workspace(self):
        """Delete selected memory"""
        self._update_detail_box("[Delete] Feature coming soon")

if __name__ == "__main__":
    app = HalcyonTkinterUI()
    app.mainloop()