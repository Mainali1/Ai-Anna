import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk

class StudentAssistantGUI:
    def __init__(self, master, command_handler):
        self.master = master
        self.command_handler = command_handler
        master.title("ANNAᵝ - Cybernetic Interface")
        master.geometry("1000x720")
        master.configure(bg='#000000')
        
        self.setup_theme()
        self.create_widgets()
        self.setup_bindings()
        self.create_header()

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('black')
        self.style.configure('TButton', font=('Terminal', 12), foreground='#00ff00', 
                           background='#002200', bordercolor='#00ff00', lightcolor='#002200', 
                           darkcolor='#002200')
        self.style.map('TButton', 
                      foreground=[('active', '#00ff00'), ('pressed', '#000000')],
                      background=[('active', '#004400'), ('pressed', '#00ff00')])
        self.style.configure('TLabel', font=('Terminal', 10), foreground='#00ff00', background='#000000')
        self.style.configure('TEntry', fieldbackground='#001100', foreground='#00ff00', 
                            insertcolor='#00ff00', bordercolor='#005500', lightcolor='#005500')

    def create_header(self):
        header = ttk.Frame(self.master, style='TFrame')
        header.pack(fill=tk.X, pady=5)
        title = ttk.Label(header, text="◈⃤ ANNANYA v1.0.0 ◈⃤", style='TLabel', 
                        font=('OCR A Extended', 18))
        title.pack(pady=10)
        
        # Grid effect
        canvas = tk.Canvas(self.master, bg='#000000', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        for i in range(0, 1000, 20):
            canvas.create_line(i, 0, i, 720, fill='#003300')
        for i in range(0, 720, 20):
            canvas.create_line(0, i, 1000, i, fill='#003300')

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=20)
        
        self.voice_button = ttk.Button(input_frame, text="◈ INITIATE VOICE LINK", 
                                     command=self.toggle_listening, style='TButton')
        self.voice_button.pack(side=tk.LEFT, padx=10)
        
        self.text_input = ttk.Entry(input_frame, width=60, style='TEntry', 
                                  font=('Consolas', 12))
        self.text_input.pack(side=tk.LEFT, padx=10)
        
        # Output Area
        self.output_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, 
                                                   font=('Consolas', 12), bg='#001100',
                                                   fg='#00ff00', insertbackground='#00ff00',
                                                   relief='ridge', borderwidth=2)
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status Bar
        self.status_bar = ttk.Label(self.master, text="SYSTEM STATUS: ONLINE", 
                                  relief='sunken', style='TLabel', 
                                  font=('Terminal', 10, 'bold'))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        
        # Add cyber lines
        self.separator = ttk.Separator(self.master, orient='horizontal')
        self.separator.pack(fill=tk.X, pady=5)

    def toggle_listening(self):
        self.command_handler.toggle_listening()
        self.update_ui_state()

    def update_ui_state(self):
        if self.command_handler.is_listening:
            self.voice_button.config(text="◈ TERMINATE VOICE LINK")
            self.status_bar.config(text="SYSTEM STATUS: AUDIO INPUT ACTIVE", foreground='#00ff00')
        else:
            self.voice_button.config(text="◈ INITIATE VOICE LINK")
            self.status_bar.config(text="SYSTEM STATUS: STANDBY", foreground='#00ff00')

    def display_response(self, text):
        self.output_area.insert(tk.END, f"\n◈ ANNA: {text}")
        self.output_area.tag_config('response', foreground='#00ff99')
        self.output_area.see(tk.END)

    def show_error(self, message):
        self.status_bar.config(text=f"ERROR: {message.upper()}", foreground='#ff0055')

    def setup_bindings(self):
        self.text_input.bind("<Return>", self.handle_text_input)
        self.text_input.bind("<FocusIn>", lambda e: self.text_input.configure(style='Active.TEntry'))
        self.text_input.bind("<FocusOut>", lambda e: self.text_input.configure(style='TEntry'))

    def handle_text_input(self, event):
        query = self.text_input.get()
        self.text_input.delete(0, tk.END)
        self.output_area.insert(tk.END, f"\n◈ USER: {query}", 'user')
        self.command_handler.process_command(query)