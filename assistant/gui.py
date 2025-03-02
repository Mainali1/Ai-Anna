import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
import os

class StudentAssistantGUI:
    def __init__(self, master, config):
        self.master = master
        self.command_handler = None
        self.config = config
        
        master.title("ANNA - AI Student Assistant")
        master.geometry("1200x800")
        master.configure(bg='#000000')
        
        self.setup_theme()
        self.create_header()
        self.create_main_interface()
        self.setup_bindings()
        
        self.voice_resp_var = tk.BooleanVar(value=self.config['voice_response'])
        self.beep_sound_var = tk.BooleanVar(value=self.config['beep_sound'])
        self.create_settings_button()

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
        self.style.configure('Mood.TLabel',
                           font=('Terminal', 12),
                           foreground='#00ffff')
        self.style.configure('Study.TFrame',
                           background='#001100')

    def create_header(self):
        header = ttk.Frame(self.master)
        header.pack(fill=tk.X, pady=5)
        title = ttk.Label(header, 
                        text="◈⃤ ANNA v2.0 - Advanced Neural Network Assistant ◈⃤", 
                        font=('OCR A Extended', 20),
                        style='TLabel')
        title.pack(pady=10)
        
        # Grid background
        canvas = tk.Canvas(self.master, bg='#000000', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        for i in range(0, 1200, 20):
            canvas.create_line(i, 0, i, 800, fill='#003300')
        for i in range(0, 800, 20):
            canvas.create_line(0, i, 1200, i, fill='#003300')

    def create_main_interface(self):
        # Main container
        main_container = ttk.Frame(self.master)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Left panel - Study Tools
        left_panel = ttk.Frame(main_container, style='Study.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_study_tools(left_panel)

        # Center panel - Main interaction
        center_panel = ttk.Frame(main_container)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_interaction_area(center_panel)

        # Right panel - Status and Mood
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_status_panel(right_panel)

    def create_study_tools(self, parent):
        ttk.Label(parent, text="STUDY TOOLS", font=('OCR A Extended', 14), style='TLabel').pack(pady=10)
        
        # Timer controls
        timer_frame = ttk.Frame(parent)
        timer_frame.pack(fill=tk.X, pady=5)
        ttk.Button(timer_frame, text="Start 25min", command=lambda: self.command_handler.process_command("start 25 minute timer")).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_frame, text="Start 45min", command=lambda: self.command_handler.process_command("start 45 minute timer")).pack(side=tk.LEFT, padx=5)

        # Flashcard controls
        flashcard_frame = ttk.Frame(parent)
        flashcard_frame.pack(fill=tk.X, pady=10)
        ttk.Button(flashcard_frame, text="Review Cards", command=lambda: self.command_handler.process_command("review flashcards")).pack(fill=tk.X, pady=5)
        ttk.Button(flashcard_frame, text="Add Card", command=self.show_add_flashcard_dialog).pack(fill=tk.X, pady=5)

    def create_interaction_area(self, parent):
        # Voice control
        input_frame = ttk.Frame(parent)
        input_frame.pack(pady=20)
        
        self.voice_button = ttk.Button(input_frame, 
                                     text="◈ INITIATE VOICE LINK", 
                                     command=self.toggle_listening)
        self.voice_button.pack(side=tk.LEFT, padx=10)
        
        # Text input
        self.text_input = ttk.Entry(input_frame, 
                                  width=60,
                                  font=('Consolas', 12))
        self.text_input.pack(side=tk.LEFT, padx=10)
        
        # Output area
        self.output_area = scrolledtext.ScrolledText(parent, 
                                                   wrap=tk.WORD,
                                                   font=('Consolas', 12),
                                                   bg='#001100',
                                                   fg='#00ff00',
                                                   height=20)
        self.output_area.pack(fill=tk.BOTH, expand=True, pady=10)

    def create_status_panel(self, parent):
        ttk.Label(parent, text="SYSTEM STATUS", font=('OCR A Extended', 14), style='TLabel').pack(pady=10)
        
        # Mood indicator
        self.mood_label = ttk.Label(parent, text="MOOD: NEUTRAL", style='Mood.TLabel')
        self.mood_label.pack(pady=5)
        
        # Language selector
        lang_frame = ttk.Frame(parent)
        lang_frame.pack(fill=tk.X, pady=10)
        ttk.Label(lang_frame, text="LANGUAGE:", style='TLabel').pack(side=tk.LEFT)
        langs = ['English', 'Spanish', 'French', 'German']
        lang_var = tk.StringVar(value=langs[0])
        lang_menu = ttk.OptionMenu(lang_frame, lang_var, *langs)
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = ttk.Label(parent, 
                                  text="SYSTEM STATUS: ONLINE",
                                  relief='sunken',
                                  style='TLabel',
                                  font=('Terminal', 10, 'bold'))
        self.status_bar.pack(fill=tk.X, pady=10)

    def show_add_flashcard_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Flashcard")
        dialog.geometry("400x300")
        dialog.configure(bg='#000000')
        
        ttk.Label(dialog, text="Front:").pack(pady=5)
        front_text = scrolledtext.ScrolledText(dialog, height=5)
        front_text.pack(padx=10, pady=5)
        
        ttk.Label(dialog, text="Back:").pack(pady=5)
        back_text = scrolledtext.ScrolledText(dialog, height=5)
        back_text.pack(padx=10, pady=5)
        
        ttk.Button(dialog, 
                  text="Save",
                  command=lambda: self.save_flashcard(front_text.get("1.0", tk.END),
                                                    back_text.get("1.0", tk.END),
                                                    dialog)).pack(pady=10)

    def save_flashcard(self, front, back, dialog):
        self.command_handler.process_command(f"add flashcard {front.strip()}: {back.strip()}")
        dialog.destroy()

    def toggle_listening(self):
        self.command_handler.toggle_listening()
        self.update_ui_state()

    def update_ui_state(self, is_listening=False):
        if is_listening:
            self.voice_button.config(text="◈ TERMINATE VOICE LINK")
            self.status_bar.config(text=" LISTENING... ", foreground='#00ff00')
            self.animate_pulse()
        else:
            self.voice_button.config(text="◈ INITIATE VOICE LINK")
            self.status_bar.config(text="SYSTEM STATUS: STANDBY", foreground='#00ff00')

    def animate_pulse(self):
        if hasattr(self.command_handler, 'is_listening') and self.command_handler.is_listening:
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
        settings_win.geometry("500x600")
        settings_win.configure(bg='#000000')
        
        # Create a scrollable frame
        canvas = tk.Canvas(settings_win, bg='#000000')
        scrollbar = ttk.Scrollbar(settings_win, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # API Settings
        api_frame = ttk.LabelFrame(scrollable_frame, text="API Configuration")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Weather API
        ttk.Label(api_frame, text="Weather API Key:").pack(pady=5)
        weather_api_entry = ttk.Entry(api_frame, width=40)
        weather_api_entry.pack(pady=5)
        if os.getenv('WEATHER_API_KEY'):
            weather_api_entry.insert(0, os.getenv('WEATHER_API_KEY'))

        # Picovoice API
        ttk.Label(api_frame, text="Picovoice API Key:").pack(pady=5)
        picovoice_api_entry = ttk.Entry(api_frame, width=40)
        picovoice_api_entry.pack(pady=5)
        if os.getenv('PICOVOICE_ACCESS_KEY'):
            picovoice_api_entry.insert(0, os.getenv('PICOVOICE_ACCESS_KEY'))

        # Location Settings
        location_frame = ttk.LabelFrame(scrollable_frame, text="Location Settings")
        location_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(location_frame, text="Default City:").pack(pady=5)
        city_entry = ttk.Entry(location_frame, width=40)
        city_entry.pack(pady=5)
        if os.getenv('DEFAULT_CITY'):
            city_entry.insert(0, os.getenv('DEFAULT_CITY'))

        # Voice Settings
        voice_frame = ttk.LabelFrame(scrollable_frame, text="Voice Settings")
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(voice_frame, 
                       text="Enable Voice Responses",
                       variable=self.voice_resp_var).pack(pady=5)
        ttk.Checkbutton(voice_frame, 
                       text="Enable Beep Sound",
                       variable=self.beep_sound_var).pack(pady=5)
        
        # Theme Settings
        theme_frame = ttk.LabelFrame(scrollable_frame, text="Theme Settings")
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        themes = ['cyberpunk', 'matrix', 'minimal']
        theme_var = tk.StringVar(value=themes[0])
        ttk.OptionMenu(theme_frame, theme_var, *themes).pack(pady=5)
        
        # Save Button
        ttk.Button(scrollable_frame, 
                  text="Save Settings",
                  command=lambda: self.save_settings(
                      weather_api=weather_api_entry.get(),
                      picovoice_api=picovoice_api_entry.get(),
                      default_city=city_entry.get()
                  )).pack(pady=10)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

    def save_settings(self, weather_api, picovoice_api, default_city):
        self.config['voice_response'] = self.voice_resp_var.get()
        self.config['beep_sound'] = self.beep_sound_var.get()
        self.config.save_config()
        
        # Update environment variables
        env_updates = {
            'WEATHER_API_KEY': weather_api,
            'PICOVOICE_ACCESS_KEY': picovoice_api,
            'DEFAULT_CITY': default_city
        }
        
        # Read existing .env file
        env_content = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        env_content[key] = value
        
        # Update with new values
        env_content.update(env_updates)
        
        # Write back to .env file
        with open('.env', 'w') as f:
            for key, value in env_content.items():
                if value:  # Only write non-empty values
                    f.write(f"{key}={value}\n")
        
        self.show_error("Settings saved successfully")