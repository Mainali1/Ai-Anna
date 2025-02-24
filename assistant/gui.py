import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk

class StudentAssistantGUI:
    def __init__(self, master, command_handler):
        self.master = master
        self.command_handler = command_handler
        master.title("Anannya - Student AI")
        master.geometry("800x600")
        
        self.setup_theme()
        self.create_widgets()
        self.setup_bindings()

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('equilux')
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=20)
        
        self.voice_button = ttk.Button(input_frame, text="🎤 Start Listening", 
                                     command=self.toggle_listening)
        self.voice_button.pack(side=tk.LEFT, padx=10)
        
        self.text_input = ttk.Entry(input_frame, width=50)
        self.text_input.pack(side=tk.LEFT, padx=10)
        
        # Output Area
        self.output_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, 
                                                    font=('Consolas', 12))
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Status Bar
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def toggle_listening(self):
        self.command_handler.toggle_listening()
        self.update_ui_state()

    def update_ui_state(self):
        if self.command_handler.is_listening:
            self.voice_button.config(text="⏹ Stop Listening")
            self.status_bar.config(text="Listening...")
        else:
            self.voice_button.config(text="🎤 Start Listening")
            self.status_bar.config(text="Ready")

    def display_response(self, text):
        self.output_area.insert(tk.END, f"\nAnannya: {text}")
        self.output_area.see(tk.END)

    def show_error(self, message):
        self.status_bar.config(text=f"Error: {message}", foreground="red")

    def setup_bindings(self):
        self.text_input.bind("<Return>", self.handle_text_input)

    def handle_text_input(self, event):
        query = self.text_input.get()
        self.text_input.delete(0, tk.END)
        self.command_handler.process_command(query)