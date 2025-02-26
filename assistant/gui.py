import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk

class StudentAssistantGUI:
    def __init__(self, master,  config):
        self.master = master
        self.command_handler = None
        self.config = config
        
        master.title("ANNAᵝ - Cybernetic Interface")
        master.geometry("1000x720")
        master.configure(bg='#000000')
        
        self.setup_theme()
        self.create_header()
        self.create_widgets()
        self.setup_bindings()
        
        self.voice_resp_var = tk.BooleanVar(value=self.config['voice_response'])
        self.beep_sound_var = tk.BooleanVar(value=self.config['beep_sound'])
        self.create_settings_button()
        self.create_command_panel()

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('black')
        self.style.configure('TButton', 
                           font=('Terminal', 12), 
                           foreground='#00ff00', 
                           background='#002200', 
                           bordercolor='#00ff00')
        self.style.map('TButton', 
                      foreground=[('active', '#00ff00'), ('pressed', '#000000')],
                      background=[('active', '#004400'), ('pressed', '#00ff00')])
        self.style.configure('TLabel', 
                           font=('Terminal', 10), 
                           foreground='#00ff00', 
                           background='#000000')
        self.style.configure('TEntry', 
                           fieldbackground='#001100', 
                           foreground='#00ff00', 
                           insertcolor='#00ff00')

    def create_header(self):
        header = ttk.Frame(self.master)
        header.pack(fill=tk.X, pady=5)
        title = ttk.Label(header, 
                        text="◈⃤ ANNA v1.0.1 ◈⃤", 
                        font=('OCR A Extended', 18),
                        style='TLabel')
        title.pack(pady=10)
        
        canvas = tk.Canvas(self.master, bg='#000000', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        for i in range(0, 1000, 20):
            canvas.create_line(i, 0, i, 720, fill='#003300')
        for i in range(0, 720, 20):
            canvas.create_line(0, i, 1000, i, fill='#003300')

    def create_widgets(self):
        input_frame = ttk.Frame(self.master)
        input_frame.pack(pady=20)
        
        self.voice_button = ttk.Button(input_frame, 
                                     text="◈ INITIATE VOICE LINK", 
                                     command=self.toggle_listening,
                                     style='TButton')
        self.voice_button.pack(side=tk.LEFT, padx=10)
        
        self.text_input = ttk.Entry(input_frame, 
                                  width=60,
                                  style='TEntry',
                                  font=('Consolas', 12))
        self.text_input.pack(side=tk.LEFT, padx=10)
        
        self.output_area = scrolledtext.ScrolledText(self.master, 
                                                   wrap=tk.WORD,
                                                   font=('Consolas', 12),
                                                   bg='#001100',
                                                   fg='#00ff00',
                                                   insertbackground='#00ff00')
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.status_bar = ttk.Label(self.master, 
                                  text="SYSTEM STATUS: ONLINE",
                                  relief='sunken',
                                  style='TLabel',
                                  font=('Terminal', 10, 'bold'))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def create_command_panel(self):
        command_canvas = tk.Canvas(self.master, bg='#000000', highlightthickness=0)
        command_canvas.place(x=20, y=100, width=300, height=200)
        
        # Cyberpunk-style commands display
        commands = [
            ("Wake Word", '"Anna Ready"'),
            ("Start Timer", '"25 minute timer"'),
            ("Open App", '"Open music player"')
        ]
        
        command_canvas.create_text(10, 10, 
                                 text="VOICE COMMANDS",
                                 fill='#00ff00',
                                 font=('OCR A Extended', 12),
                                 anchor='nw')
        
        y = 40
        for cmd, example in commands:
            command_canvas.create_text(20, y, 
                                      text=f"◈ {cmd}:",
                                      fill='#00ff99',
                                      font=('Consolas', 10),
                                      anchor='nw')
            command_canvas.create_text(40, y+20,
                                      text=f"» {example}",
                                      fill='#009900',
                                      font=('Terminal', 9),
                                      anchor='nw')
            y += 50
        
        # Border effects
        command_canvas.create_rectangle(2, 2, 298, 198, outline='#00ff00')

    def toggle_listening(self):
        self.command_handler.toggle_listening()
        self.update_ui_state()

    def update_ui_state(self, is_listening):
        if is_listening:
            self.voice_button.config(text="◈ TERMINATE VOICE LINK", style='Active.TButton')
            self.status_bar.config(text=" LISTENING... ", foreground='#00ff00')
            self.animate_pulse()
        else:
            self.voice_button.config(text="◈ INITIATE VOICE LINK", style='TButton')
            self.status_bar.config(text="SYSTEM STATUS: STANDBY", foreground='#00ff00')

    def animate_pulse(self):
        if self.command_handler.is_listening:
            current_color = self.status_bar.cget('foreground')
            new_color = '#009900' if current_color == '#00ff00' else '#00ff00'
            self.status_bar.config(foreground=new_color)
            self.master.after(500, self.animate_pulse)

    def display_response(self, text):
        self.output_area.insert(tk.END, f"\n◈ ANNA: {text}")
        self.output_area.see(tk.END)

    def show_error(self, message):
        self.status_bar.config(text=f"ERROR: {message}", foreground='#ff0055')

    def setup_bindings(self):
        self.text_input.bind("<Return>", self.handle_text_input)

    def handle_text_input(self, event):
        query = self.text_input.get()
        self.text_input.delete(0, tk.END)
        self.output_area.insert(tk.END, f"\n◈ USER: {query}")
        self.command_handler.process_command(query)

    def create_settings_button(self):
        settings_btn = ttk.Button(self.master, 
                                 text="⚙",
                                 command=self.create_settings_panel)
        settings_btn.place(relx=0.95, rely=0.02, anchor="ne")

    def create_settings_panel(self):
        settings_win = tk.Toplevel(self.master)
        settings_win.title("Settings")
        
        ttk.Label(settings_win, text="API Key:").grid(row=0, column=0)
        api_entry = ttk.Entry(settings_win, width=40)
        api_entry.grid(row=0, column=1)
        
        ttk.Checkbutton(settings_win, 
                       text="Voice Responses",
                       variable=self.voice_resp_var).grid(row=1, columnspan=2)
        ttk.Checkbutton(settings_win, 
                       text="Beep Sound",
                       variable=self.beep_sound_var).grid(row=2, columnspan=2)
        
        ttk.Button(settings_win, 
                  text="Save",
                  command=lambda: self.save_settings(api_entry.get())).grid(row=3, columnspan=2)

    def save_settings(self, api_key):
        self.config['voice_response'] = self.voice_resp_var.get()
        self.config['beep_sound'] = self.beep_sound_var.get()
        self.config.save_config()
        
        if api_key:
            with open('.env', 'a') as f:
                f.write(f"\nPICOVOICE_ACCESS_KEY={api_key}")
        
        self.show_error("Settings saved")