import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog
import threading
import time
import json
import queue
import re
import uuid
import datetime

# Import your core modules
import config  # Load environment from .env early
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
        self.thalamus = Thalamus(self.cortex, self.hippo)
        
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
        """Memory workspace with working + anchor windows + detail pane + Curiosity."""
        self.memory_tab.grid_rowconfigure(0, weight=1)
        self.memory_tab.grid_columnconfigure(0, weight=1) # Left Frame
        self.memory_tab.grid_columnconfigure(1, weight=1) # Right Frame

        # ----------------------------------------
        # Left side: Working/Anchor Windows
        # ----------------------------------------
        left_frame = ttk.Frame(self.memory_tab)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Configure layout for two listboxes (Working/Anchor)
        left_frame.grid_rowconfigure(0, weight=0); left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_rowconfigure(2, weight=0); left_frame.grid_rowconfigure(3, weight=0)
        left_frame.grid_rowconfigure(4, weight=1)
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

        # ----------------------------------------
        # Right side: Detail pane + Curiosity Window (NEW)
        # ----------------------------------------
        right_frame = ttk.Frame(self.memory_tab)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=0) # Curiosity Label
        right_frame.grid_rowconfigure(1, weight=1) # Curiosity Listbox
        right_frame.grid_rowconfigure(2, weight=0) # Detail Label
        right_frame.grid_rowconfigure(3, weight=2) # Detail Box (More height)
        right_frame.grid_rowconfigure(4, weight=0) # Buttons
        right_frame.grid_columnconfigure(0, weight=1)

        # 🧠 Curiosity Window (NEW)
        ttk.Label(right_frame, text="🧠 Curiosity Window (Self-Generated Questions)", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.curiosity_listbox = tk.Listbox(right_frame, height=10)
        self.curiosity_listbox.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        # Add a placeholder binding for the new listbox
        self.curiosity_listbox.bind('<<ListboxSelect>>', lambda e: self._on_memory_select(e, 'curiosity')) 

        # Detail pane
        ttk.Label(right_frame, text="📖 Memory Details", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.detail_box = scrolledtext.ScrolledText(right_frame, state='disabled', wrap=tk.WORD, bg='#f5f5f5')
        self.detail_box.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # Control buttons
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=4, column=0, sticky="ew")
        
        # NOTE: You will need to remove the placeholder functions in your class later!
        ttk.Button(button_frame, text="📌 Pin", command=self._pin_memory_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="💉 Inject", command=self._inject_memory_workspace).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="💡 Activate Curiosity", command=self._activate_curiosity_workspace).pack(side=tk.LEFT, padx=2) # NEW Button
        ttk.Button(button_frame, text="🔄 Refresh", command=self._refresh_memory_workspace).pack(side=tk.LEFT, padx=2) 
        ttk.Button(button_frame, text="❌ Delete", command=self._delete_memory_workspace).pack(side=tk.LEFT, padx=2)

    # 💡 NEW PLACEHOLDER METHOD for the new button
    def _activate_curiosity_workspace(self):
        """Placeholder for activating a selected curiosity question into the chat input."""
        self._update_detail_box("[Activate Curiosity] Feature coming soon")

    def _get_selected_memory(self):
        """Helper to safely retrieve the selected item from any active listbox."""
        source = None
        listbox = None
        
        # Determine which listbox is active
        if self.working_listbox.curselection():
            source = 'working'
            listbox = self.working_listbox
        elif self.anchor_listbox.curselection():
            source = 'anchor'
            listbox = self.anchor_listbox
        elif self.curiosity_listbox.curselection():
            source = 'curiosity'
            listbox = self.curiosity_listbox
        
        if not listbox:
            return None, None, None

        listbox_index = listbox.curselection()[0]
        
        # Logic to map listbox index to the memory data array
        data_source = None
        if source == 'working':
            data_source = self.anchor.get_recent(10)
        elif source == 'anchor':
            data_source = self.anchor.anchor_window
        elif source == 'curiosity':
            data_source = self.anchor.get_curiosity_queue()

        if listbox_index < len(data_source):
            return source, listbox_index, data_source[listbox_index]
            
        return None, None, None

    # 💡 IMPORTANT: Update the detail logic to include the new listbox
    def _on_memory_select(self, event, source):
        """Handle memory selection across all three listboxes."""
        listbox = getattr(self, f'{source}_listbox')
        selection = listbox.curselection()
        
        if not selection:
            return

        listbox_index = selection[0]
        
        # We need a robust way to map the listbox index back to the stored data.
        # Since the provided listboxes only use index 0, we'll keep the logic simple for now:
        if source == 'working':
            data_source = self.anchor.get_recent(10)
        elif source == 'anchor':
            data_source = self.anchor.anchor_window
        elif source == 'curiosity':
            # This relies on you implementing a get_curiosity_queue() method in TemporalAnchor
            try:
                data_source = self.anchor.get_curiosity_queue() 
            except AttributeError:
                self._update_detail_box("[Error] Curiosity queue not yet implemented in TemporalAnchor.")
                return
        
        if listbox_index < len(data_source):
            self._display_memory_details(data_source[listbox_index])

    def _delete_memory_workspace(self):
        """Delete selected memory from the database."""
        # ⚠️ NOTE: Deleting points requires specific Qdrant logic (client.delete)
        self._update_detail_box("[Delete] Feature logic coming soon: Requires Qdrant client.delete().")
        # You will implement the full Qdrant deletion logic here later

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
            state, reflection, response_text = response_text
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

    def _update_detail_box(self, text, clear=False): # <--- FIX: Added 'clear=False' argument
        """Update detail pane"""
        self.detail_box.config(state='normal')
        if clear: # <--- FIX: Implement clearing logic
            self.detail_box.delete('1.0', tk.END)
        self.detail_box.insert(tk.END, text)
        self.detail_box.config(state='disabled')

    def _pin_memory_workspace(self):
        """Pin selected episodic memory (increase weight)."""
        source, index, mem_obj = self._get_selected_memory()

        if source != 'anchor' or not mem_obj.get('id'):
            self._update_text_box(self.detail_box, "\n[Pin] ⚠️ Please select a committed memory from the Anchor Window.", clear=True)
            return

        mem_id = mem_obj['id']
        
        # Show weight adjustment dialog (Simplified stub - copy logic from previous answer)
        # NOTE: You'll need to define this Tkinter Toplevel dialog separately if you want the popup.
        try:
             # --- SIMPLIFIED DIRECT INPUT FOR DEMO ---
             # In a real app, this would use a Toplevel window.
             new_weight = simpledialog.askfloat("Set Weight", "Enter new manual weight (Min 1.0):", initialvalue=mem_obj.get('weight', 1.0))
             if new_weight is None or new_weight < 1.0:
                 return
                 
             self.hippo.adjust_weight(mem_id, new_weight)
             self._update_text_box(self.detail_box, f"\n[Pin] ✅ Adjusted memory {mem_id[:8]}... to weight {new_weight:.2f}.", clear=True)
             self._refresh_memory_workspace()
             
        except Exception as e:
            self._update_text_box(self.detail_box, f"\n[Pin] ❌ Error: {e}", clear=True)
            print(f"Pinning Error: {e}")


    def _inject_memory_workspace(self):
            """Inject selected memory into anchor's manual context list."""
            # 1. Safely retrieve the selected memory object
            source, index, mem_obj = self._get_selected_memory()
            
            # 2. Validation: We can inject anything that is a memory (working turn, anchor history, or hippo data)
            if not mem_obj:
                self._update_detail_box("\n[Inject] ⚠️ Please select an item to inject.", clear=True)
                return
            
            # 3. Prepare data for TemporalAnchor.inject_memories
            # We need to ensure the memory object has the minimum keys expected by the Anchor
            injection_data = [{
                # Prioritize retrieving combined text for full context
                "text": mem_obj.get('fused_text', mem_obj.get('user_query', mem_obj.get('query', ''))),
                "query": mem_obj.get('user_query', mem_obj.get('query', '')),
                "reflection": mem_obj.get('reflection', ''),
                "id": mem_obj.get('id', str(uuid.uuid4())), 
                "timestamp": mem_obj.get('timestamp', datetime.datetime.now().isoformat()),
            }]

            try:
                # 4. Call the TemporalAnchor's injection method
                self.anchor.inject_memories(injection_data)
                
                self._update_detail_box(f"\n[Inject] ✅ Injected memory from {source} into next turn's context.", clear=True)
                self._refresh_memory_workspace() # Refresh to update the listbox (if you implement a visual queue)

            except Exception as e:
                self._update_detail_box(f"\n[Inject] ❌ Error during memory injection: {e}", clear=True)
                print(f"Injection Error: {e}")


    def _activate_curiosity_workspace(self):
        """Take selected curiosity question and place it in the chat input."""
        source, index, question_obj = self._get_selected_memory()
        
        if source != 'curiosity' or not question_obj:
            self._update_detail_box("\n[Activate] ⚠️ Select a question from the Curiosity Window.", clear=True)
            return
            
        question_text = question_obj.get("question", "N/A")
        
        # 1. Place question in chat input
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, question_text)
        
        # 2. Clear the question from the queue
        self.anchor.clear_curiosity_queue(index=index)
        
        self._update_detail_box(f"\n[Activate] ✅ Question '{question_text[:50]}...' moved to chat input.", clear=True)
        self._refresh_memory_workspace() # Refresh to show the item is gone


    def _refresh_memory_workspace(self):
        """Load working, anchor, and curiosity windows."""
        self.working_listbox.delete(0, tk.END)
        self.anchor_listbox.delete(0, tk.END)
        self.curiosity_listbox.delete(0, tk.END) # <--- CLEAR NEW LISTBOX
        self.current_memory_data = [] # Reset for safety

        # 1. Working window (Live turns)
        working = self.anchor.get_recent(10)
        for i, turn in enumerate(working):
            snippet = turn['user_query'][:50].replace('\n', ' ')
            self.working_listbox.insert(tk.END, f"[W{i+1}] {snippet}...")
            self.current_memory_data.append(('working', turn))

        # 2. Anchor window (History)
        anchor_data = self.anchor.anchor_window
        for i, entry in enumerate(anchor_data):
            snippet = entry.get('query', '')[:50].replace('\n', ' ')
            self.anchor_listbox.insert(tk.END, f"[A{i+1}] {snippet}...")
            self.current_memory_data.append(('anchor', entry))
            
        # 3. Curiosity Window (NEW)
        curiosity_data = self.anchor.get_curiosity_queue()
        for i, entry in enumerate(curiosity_data):
            snippet = entry.get('question', '')[:50].replace('\n', ' ')
            self.curiosity_listbox.insert(tk.END, f"[Q{i+1}] {snippet}...")
            self.current_memory_data.append(('curiosity', entry)) # Add curiosity to the overall data set

    # NOTE: You still need to add a small import for simpledialog and uuid/datetime at the top of your file
    # from tkinter import simpledialog
    # import uuid, datetime
    
    # NOTE: _delete_memory_workspace is still stubbed out, as it requires Qdrant's client.delete method.

if __name__ == "__main__":
    app = HalcyonTkinterUI()
    app.mainloop()