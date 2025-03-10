import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import threading

class AssistantGUI:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.command_handler = None  # Will be set after initialization
        self.root.title("Anna AI Assistant")
        self.root.geometry("400x600")
        
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status frame
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # AI Mode indicator
        self.ai_mode_var = tk.StringVar(value="AI Mode: OFF")
        self.ai_mode_label = ttk.Label(
            self.status_frame,
            textvariable=self.ai_mode_var,
            font=("Helvetica", 10)
        )
        self.ai_mode_label.pack(side=tk.LEFT)
        
        # Processing indicator
        self.processing_label = ttk.Label(
            self.status_frame,
            text="",
            font=("Helvetica", 10)
        )
        self.processing_label.pack(side=tk.RIGHT)
        
        # Response display
        self.response_frame = ttk.Frame(self.main_frame)
        self.response_frame.pack(fill=tk.BOTH, expand=True)
        
        self.response_text = tk.Text(
            self.response_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            state=tk.DISABLED
        )
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for response text
        scrollbar = ttk.Scrollbar(self.response_frame, command=self.response_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.response_text.configure(yscrollcommand=scrollbar.set)
        
        # Input frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        # Input field
        self.input_field = ttk.Entry(self.input_frame)
        self.input_field.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.input_field.bind('<Return>', self.process_input)
        
        # Send button
        self.send_button = ttk.Button(
            self.input_frame,
            text="Send",
            command=self.process_input
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))

        # Status bar
        self.status_bar = ttk.Label(
            self.main_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        
        self.processing_animation = None
        self.dots_count = 0

    def update_ui_state(self, is_listening):
        if is_listening:
            self.start_processing_animation("Listening")
        else:
            self.stop_processing_animation()
            self.status_bar.config(text="Ready")
    
    def start_processing_animation(self, prefix="Processing"):
        self.dots_count = (self.dots_count + 1) % 4
        dots = "." * self.dots_count
        self.processing_label.config(text=f"{prefix}{dots}")
        self.processing_animation = self.root.after(500, lambda: self.start_processing_animation(prefix))
    
    def stop_processing_animation(self):
        if self.processing_animation:
            self.root.after_cancel(self.processing_animation)
            self.processing_animation = None
        self.processing_label.config(text="")
    
    def update_ai_mode(self, is_active):
        self.ai_mode_var.set(f"AI Mode: {'ON' if is_active else 'OFF'}")
        if is_active:
            self.ai_mode_label.config(foreground="green")
        else:
            self.ai_mode_label.config(foreground="red")
    
    def show_response(self, text):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.insert(tk.END, f"{text}\n\n")
        self.response_text.see(tk.END)
        self.response_text.config(state=tk.DISABLED)
    
    def show_error(self, error_message):
        self.status_bar.config(text=f"Error: {error_message}")
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))
    
    def run(self):
        self.root.mainloop()

    def process_input(self, event=None):
        if not self.command_handler:
            self.show_error("Command handler not initialized")
            return
            
        text = self.input_field.get().strip()
        if not text:
            return
            
        self.input_field.delete(0, tk.END)
        self.start_processing_animation()
        
        # Process command in a separate thread to avoid UI freezing
        threading.Thread(
            target=self._process_command_thread,
            args=(text,),
            daemon=True
        ).start()
    
    def _process_command_thread(self, text):
        try:
            response = self.command_handler.process_command(text)
            self.root.after(0, self.display_response, response)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.stop_processing_animation)
    
    def display_response(self, response):
        """Display the response in the UI"""
        if response:
            self.show_response(response)
            self.status_bar.config(text="Ready")



    def create_sidebar_content(self):
        # Settings section
        settings_frame = ttk.LabelFrame(self.sidebar, text='Settings', style='Custom.TButton')
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice response toggle
        voice_check = ttk.Checkbutton(settings_frame, text='Voice Response',
                                    variable=self.voice_resp_var,
                                    style='Custom.TButton',
                                    command=self.update_settings)
        voice_check.pack(fill=tk.X, padx=2, pady=2)
        
        # Sound effects toggle
        beep_check = ttk.Checkbutton(settings_frame, text='Sound Effects',
                                   variable=self.beep_sound_var,
                                   style='Custom.TButton',
                                   command=self.update_settings)
        beep_check.pack(fill=tk.X, padx=2, pady=2)

        # Study tools section
        tools_frame = ttk.LabelFrame(self.sidebar, text='Study Tools', style='Custom.TButton')
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(tools_frame, text='Start 25min', style='Custom.TButton',
                   command=lambda: self.command_handler.process_command("start 25 minute timer")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(tools_frame, text='Start 45min', style='Custom.TButton',
                   command=lambda: self.command_handler.process_command("start 45 minute timer")).pack(fill=tk.X, padx=2, pady=2)
        
        # Flashcards section
        cards_frame = ttk.LabelFrame(self.sidebar, text='Flashcards', style='Custom.TButton')
        cards_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(cards_frame, text='Review Cards', style='Custom.TButton',
                   command=lambda: self.command_handler.process_command("review flashcards")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(cards_frame, text='Add Card', style='Custom.TButton',
                   command=self.show_add_flashcard_dialog).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(cards_frame, text='Delete Card', style='Custom.TButton',
                   command=self.show_delete_flashcard_dialog).pack(fill=tk.X, padx=2, pady=2)

        # Schedule section
        schedule_frame = ttk.LabelFrame(self.sidebar, text='Schedule', style='Custom.TButton')
        schedule_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(schedule_frame, text='View Today', style='Custom.TButton',
                   command=lambda: self.command_handler.process_command("schedule today")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(schedule_frame, text='Delete Schedule', style='Custom.TButton',
                   command=self.show_delete_schedule_dialog).pack(fill=tk.X, padx=2, pady=2)

    def create_main_content(self):
        # Header with title and status
        header = ttk.Frame(self.content, style='Content.TFrame')
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header, text='ANNA', style='Title.TLabel').pack(side=tk.LEFT)
        self.status_label = ttk.Label(header, text='ONLINE', style='Subtitle.TLabel')
        self.status_label.pack(side=tk.RIGHT)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.content)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Chat tab
        chat_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(chat_frame, text='Chat')
        
        # Output area with custom styling
        self.output_area = scrolledtext.ScrolledText(chat_frame,
                                                   wrap=tk.WORD,
                                                   font=('Consolas', 11),
                                                   bg='#2d2d2d',
                                                   fg='#ffffff',
                                                   insertbackground='#ffffff',
                                                   selectbackground='#404040',
                                                   height=20)
        self.output_area.pack(fill=tk.BOTH, expand=True)
        
        # Assignments tab
        assignments_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(assignments_frame, text='Assignments')
        self.assignments_area = scrolledtext.ScrolledText(assignments_frame,
                                                        wrap=tk.WORD,
                                                        font=('Segoe UI', 11),
                                                        bg='#2d2d2d',
                                                        fg='#ffffff')
        self.assignments_area.pack(fill=tk.BOTH, expand=True)
        
        # Flashcards tab
        flashcards_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(flashcards_frame, text='Flashcards')
        self.flashcards_area = scrolledtext.ScrolledText(flashcards_frame,
                                                       wrap=tk.WORD,
                                                       font=('Segoe UI', 11),
                                                       bg='#2d2d2d',
                                                       fg='#ffffff')
        self.flashcards_area.pack(fill=tk.BOTH, expand=True)
        
        # Schedule tab
        schedule_frame = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(schedule_frame, text='Schedule')
        self.schedule_area = scrolledtext.ScrolledText(schedule_frame,
                                                     wrap=tk.WORD,
                                                     font=('Segoe UI', 11),
                                                     bg='#2d2d2d',
                                                     fg='#ffffff')
        self.schedule_area.pack(fill=tk.BOTH, expand=True)
        
        # Input area
        input_frame = ttk.Frame(self.content, style='Content.TFrame')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.voice_button = ttk.Button(input_frame,
                                      text='🎤',
                                      style='Custom.TButton',
                                      command=self.toggle_listening)
        self.voice_button.pack(side=tk.LEFT, padx=2)
        
        self.text_input = ttk.Entry(input_frame,
                                   font=('Segoe UI', 11),
                                   background='#2d2d2d',
                                   foreground='#ffffff')
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        ttk.Button(input_frame,
                   text='Send',
                   style='Custom.TButton',
                   command=self.send_message).pack(side=tk.RIGHT, padx=2)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
            self.sidebar_visible = True

    def send_message(self):
        query = self.text_input.get()
        if query.strip():
            self.text_input.delete(0, tk.END)
            self.output_area.insert(tk.END, f"\n[You]: {query}")
            self.command_handler.process_command(query)

    def display_response(self, text):
        self.output_area.insert(tk.END, f"\n[ANNA]: {text}")
        self.output_area.see(tk.END)

    def update_assignments(self, assignments):
        """Update assignments tab with current assignments"""
        self.assignments_area.delete('1.0', tk.END)
        if not assignments:
            self.assignments_area.insert(tk.END, "No assignments yet.")
            return
        
        for assignment in assignments:
            due_date = assignment.get('due_date', 'No due date')
            status = assignment.get('status', 'Pending')
            task = assignment.get('task', '')
            
            self.assignments_area.insert(tk.END, 
                f"\n📝 Task: {task}\n")
            self.assignments_area.insert(tk.END,
                f"   Due: {due_date} | Status: {status}\n")
            self.assignments_area.insert(tk.END, "   " + "-"*40 + "\n")

    def update_flashcards(self, flashcards):
        """Update flashcards tab with current flashcards"""
        self.flashcards_area.delete('1.0', tk.END)
        if not flashcards:
            self.flashcards_area.insert(tk.END, "No flashcards yet.")
            return
            
        for card in flashcards:
            front = card.get('front', '')
            back = card.get('back', '')
            deck = card.get('deck', 'Default')
            next_review = card.get('next_review', 'Not scheduled')
            
            self.flashcards_area.insert(tk.END,
                f"\n📚 Deck: {deck}\n")
            self.flashcards_area.insert(tk.END,
                f"Front: {front}\n")
            self.flashcards_area.insert(tk.END,
                f"Back: {back}\n")
            self.flashcards_area.insert(tk.END,
                f"Next Review: {next_review}\n")
            self.flashcards_area.insert(tk.END, "   " + "-"*40 + "\n")

    def update_schedule(self, schedule):
        """Update schedule tab with current schedule"""
        self.schedule_area.delete('1.0', tk.END)
        if not schedule:
            self.schedule_area.insert(tk.END, "No scheduled events.")
            return
            
        for event in schedule:
            title = event.get('title', '')
            time = event.get('time', 'No time set')
            duration = event.get('duration', '')
            status = event.get('status', 'Scheduled')
            
            self.schedule_area.insert(tk.END,
                f"\n📅 {title}\n")
            self.schedule_area.insert(tk.END,
                f"   Time: {time}\n")
            if duration:
                self.schedule_area.insert(tk.END,
                    f"   Duration: {duration}\n")
            self.schedule_area.insert(tk.END,
                f"   Status: {status}\n")
            self.schedule_area.insert(tk.END, "   " + "-"*40 + "\n")

    def setup_bindings(self):
        self.text_input.bind("<Return>", lambda e: self.send_message())
        self.master.bind("<Control-b>", lambda e: self.toggle_sidebar())

    def toggle_listening(self):
        self.command_handler.toggle_listening()
        self.update_ui_state()

    def update_ui_state(self, is_listening=False):
        if is_listening:
            self.voice_button.configure(text='⏹')
            self.status_label.configure(text='LISTENING...')
        else:
            self.voice_button.configure(text='🎤')
            self.status_label.configure(text='ONLINE')
    def show_add_flashcard_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Add Flashcard")
        dialog.geometry("400x300")
        dialog.configure(bg='#1a1a1a')
        dialog.transient(self.master)
        dialog.grab_set()

        # Create and pack the front side entry
        front_frame = ttk.Frame(dialog, style='Content.TFrame')
        front_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(front_frame, text="Front:", style='Subtitle.TLabel').pack(anchor='w')
        front_text = scrolledtext.ScrolledText(front_frame, height=4, width=40,
                                            bg='#2d2d2d', fg='#ffffff',
                                            font=('Segoe UI', 10))
        front_text.pack(fill=tk.X)

        # Create and pack the back side entry
        back_frame = ttk.Frame(dialog, style='Content.TFrame')
        back_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(back_frame, text="Back:", style='Subtitle.TLabel').pack(anchor='w')
        back_text = scrolledtext.ScrolledText(back_frame, height=4, width=40,
                                           bg='#2d2d2d', fg='#ffffff',
                                           font=('Segoe UI', 10))
        back_text.pack(fill=tk.X)

        def save_flashcard():
            front = front_text.get("1.0", tk.END).strip()
            back = back_text.get("1.0", tk.END).strip()
            if front and back:
                self.command_handler.process_command(f"add flashcard {front}: {back}")
                dialog.destroy()
            else:
                tk.messagebox.showwarning("Warning", "Both front and back must be filled out")

        # Button frame
        button_frame = ttk.Frame(dialog, style='Content.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Save", style='Custom.TButton',
                  command=save_flashcard).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", style='Custom.TButton',
                  command=dialog.destroy).pack(side=tk.RIGHT)

    def show_delete_flashcard_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Delete Flashcard")
        dialog.geometry("300x150")
        dialog.configure(bg='#1a1a1a')
        dialog.transient(self.master)
        dialog.grab_set()

        # Create and pack the ID entry
        input_frame = ttk.Frame(dialog, style='Content.TFrame')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(input_frame, text="Flashcard ID:", style='Subtitle.TLabel').pack(anchor='w')
        id_entry = ttk.Entry(input_frame, font=('Segoe UI', 10))
        id_entry.pack(fill=tk.X, pady=5)

        def delete_flashcard():
            try:
                card_id = int(id_entry.get().strip())
                if tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this flashcard?"):
                    self.command_handler.process_command(f"delete flashcard {card_id}")
                    dialog.destroy()
            except ValueError:
                tk.messagebox.showwarning("Warning", "Please enter a valid ID number")

        # Button frame
        button_frame = ttk.Frame(dialog, style='Content.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Delete", style='Custom.TButton',
                  command=delete_flashcard).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", style='Custom.TButton',
                  command=dialog.destroy).pack(side=tk.RIGHT)

    def show_delete_schedule_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Delete Schedule")
        dialog.geometry("300x150")
        dialog.configure(bg='#1a1a1a')
        dialog.transient(self.master)
        dialog.grab_set()

        # Create and pack the ID entry
        input_frame = ttk.Frame(dialog, style='Content.TFrame')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(input_frame, text="Schedule ID:", style='Subtitle.TLabel').pack(anchor='w')
        id_entry = ttk.Entry(input_frame, font=('Segoe UI', 10))
        id_entry.pack(fill=tk.X, pady=5)

        def delete_schedule():
            try:
                schedule_id = int(id_entry.get().strip())
                if tk.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this schedule?"):
                    self.command_handler.process_command(f"delete schedule {schedule_id}")
                    dialog.destroy()
            except ValueError:
                tk.messagebox.showwarning("Warning", "Please enter a valid ID number")

        # Button frame
        button_frame = ttk.Frame(dialog, style='Content.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(button_frame, text="Delete", style='Custom.TButton',
                  command=delete_schedule).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", style='Custom.TButton',
                  command=dialog.destroy).pack(side=tk.RIGHT)
    def update_settings(self):
        """Update configuration with new settings"""
        self.config['voice_response'] = self.voice_resp_var.get()
        self.config['beep_sound'] = self.beep_sound_var.get()
        # Trigger config save
        if hasattr(self.command_handler, 'config'):
            self.command_handler.config.save_config()