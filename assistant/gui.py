import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedTk
import threading
import math

class AssistantGUI:
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.command_handler = None  # Will be set after initialization
        self.root.title("Anna AI Assistant")
        self.root.geometry("800x600")
        
        # Initialize variables for settings first
        self.voice_resp_var = tk.BooleanVar(value=self.config['voice_response'])
        self.beep_sound_var = tk.BooleanVar(value=self.config['beep_sound'])
        self.ai_mode_var = tk.StringVar(value="AI Mode: OFF")
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.sidebar = ttk.Frame(self.main_container)
        self.main_container.add(self.sidebar, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.main_frame, weight=3)
        
        # Create content frame
        self.content = ttk.Frame(self.main_frame)
        self.content.pack(fill=tk.BOTH, expand=True)
        
        # Initialize UI components
        self.create_sidebar_content()
        self.create_main_content()
        
        # Create Siri-like animation canvas
        self.animation_canvas = tk.Canvas(self.main_frame, width=60, height=60, bg=self.root['bg'], highlightthickness=0)
        self.animation_canvas.pack(side=tk.BOTTOM, pady=5)
        self.animation_points = []
        self.animation_angle = 0
        self.is_animating = False
        
        # Create status bar and processing label
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.processing_label = ttk.Label(self.main_frame, text="")
        self.processing_label.pack(side=tk.BOTTOM, pady=5)
        
        # Create response text area with proper colors
        self.response_text = tk.Text(self.main_frame, wrap=tk.WORD, height=10, bg='white', fg='black')
        self.response_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.response_text.config(state=tk.DISABLED)
        
        # Create input field with proper colors
        self.input_field = ttk.Entry(self.main_frame, style='Custom.TEntry')
        self.input_field.pack(fill=tk.X, padx=5, pady=5)
        self.input_field.bind('<Return>', self.process_input)
        
        # Create custom style for input field with proper colors
        style = ttk.Style()
        style.configure('Custom.TEntry',
                        fieldbackground='white',
                        foreground='black')
        style.map('Custom.TEntry',
                  fieldbackground=[('readonly', 'white')],
                  foreground=[('readonly', 'black')])
        
        # Create Siri-like animation canvas with white background
        self.animation_canvas = tk.Canvas(self.main_frame, width=60, height=60, bg='white', highlightthickness=0)
        self.animation_canvas.pack(side=tk.BOTTOM, pady=5)
        self.animation_points = []
        self.animation_angle = 0
        self.is_animating = False
        self.update_siri_animation()
        
    def draw_ai_mode_icon(self, is_active):
        self.ai_mode_icon.delete('all')
        color = 'green' if is_active else 'red'
        self.ai_mode_icon.create_oval(2, 2, 14, 14, fill=color, outline=color)
        
    def update_siri_animation(self):
        if not self.is_animating:
            return
            
        self.animation_canvas.delete('all')
        center_x = 30
        center_y = 30
        radius = 20
        num_points = 12
        
        for i in range(num_points):
            angle = self.animation_angle + (i * (360 / num_points))
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            size = 3 + 2 * math.sin(math.radians(angle - self.animation_angle))
            color = f'#{int(128 + 127 * math.sin(math.radians(angle - self.animation_angle))):02x}0000'
            self.animation_canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline=color)
        
        self.animation_angle = (self.animation_angle + 5) % 360
        self.animation_canvas.after(50, self.update_siri_animation)
        
    def start_siri_animation(self):
        self.is_animating = True
        self.update_siri_animation()
        
    def stop_siri_animation(self):
        self.is_animating = False
        self.animation_canvas.delete('all')
        
    def update_ui_state(self, is_listening):
        if is_listening:
            self.start_siri_animation()
            self.start_processing_animation("Listening")
        else:
            self.stop_siri_animation()
            self.stop_processing_animation()
            self.status_bar.config(text="Ready")
    
    def update_ai_mode(self, is_active):
        self.ai_mode_var.set(f"AI Mode: {'ON' if is_active else 'OFF'}")
        self.draw_ai_mode_icon(is_active)
        if is_active:
            self.ai_mode_label.config(foreground="green")
        else:
            self.ai_mode_label.config(foreground="red")
    
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
        settings_frame = ttk.LabelFrame(self.sidebar, text='Settings', style='Custom.TLabelframe')
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice response toggle
        voice_check = ttk.Checkbutton(settings_frame, text='Voice Response',
                                    variable=self.voice_resp_var,
                                    command=self.update_settings)
        voice_check.pack(fill=tk.X, padx=2, pady=2)
        
        # Sound effects toggle
        beep_check = ttk.Checkbutton(settings_frame, text='Sound Effects',
                                   variable=self.beep_sound_var,
                                   command=self.update_settings)
        beep_check.pack(fill=tk.X, padx=2, pady=2)

        # Time and Date section
        time_frame = ttk.LabelFrame(self.sidebar, text='Time & Date', style='Custom.TLabelframe')
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(time_frame, text='Current Time',
                   command=lambda: self.command_handler.process_command("what time is it")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(time_frame, text='Current Date',
                   command=lambda: self.command_handler.process_command("what's the date")).pack(fill=tk.X, padx=2, pady=2)

        # Weather section
        weather_frame = ttk.LabelFrame(self.sidebar, text='Weather', style='Custom.TLabelframe')
        weather_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(weather_frame, text='Weather Update',
                   command=lambda: self.command_handler.process_command("weather update")).pack(fill=tk.X, padx=2, pady=2)

        # Music section
        music_frame = ttk.LabelFrame(self.sidebar, text='Music Controls', style='Custom.TLabelframe')
        music_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(music_frame, text='Play Music',
                   command=lambda: self.command_handler.process_command("play music")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(music_frame, text='Stop Music',
                   command=lambda: self.command_handler.process_command("stop music")).pack(fill=tk.X, padx=2, pady=2)

        # Study tools section
        tools_frame = ttk.LabelFrame(self.sidebar, text='Study Tools', style='Custom.TLabelframe')
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(tools_frame, text='Start 25min Timer',
                   command=lambda: self.command_handler.process_command("start 25 minute timer")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(tools_frame, text='Start 45min Timer',
                   command=lambda: self.command_handler.process_command("start 45 minute timer")).pack(fill=tk.X, padx=2, pady=2)
        
        # Flashcards section
        cards_frame = ttk.LabelFrame(self.sidebar, text='Flashcards', style='Custom.TLabelframe')
        cards_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(cards_frame, text='Review Cards',
                   command=lambda: self.command_handler.process_command("review flashcards")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(cards_frame, text='Create New Card',
                   command=self.show_add_flashcard_dialog).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(cards_frame, text='Manage Cards',
                   command=self.show_manage_flashcards_dialog).pack(fill=tk.X, padx=2, pady=2)

        # Schedule section
        schedule_frame = ttk.LabelFrame(self.sidebar, text='Schedule', style='Custom.TLabelframe')
        schedule_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(schedule_frame, text='View Today',
                   command=lambda: self.command_handler.process_command("show today's schedule")).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(schedule_frame, text='Add Task',
                   command=self.show_add_task_dialog).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(schedule_frame, text='Manage Schedule',
                   command=self.show_manage_schedule_dialog).pack(fill=tk.X, padx=2, pady=2)

        # Applications section
        apps_frame = ttk.LabelFrame(self.sidebar, text='Quick Launch', style='Custom.TLabelframe')
        apps_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(apps_frame, text='Launch App',
                   command=self.show_app_launcher_dialog).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(apps_frame, text='Manage Apps',
                   command=self.show_manage_apps_dialog).pack(fill=tk.X, padx=2, pady=2)

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
                                   foreground='#000000')
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
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Flashcard")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Question:").pack(padx=5, pady=5)
        question_entry = ttk.Entry(dialog, width=50)
        question_entry.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Answer:").pack(padx=5, pady=5)
        answer_text = tk.Text(dialog, height=5, width=50)
        answer_text.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Tags (comma-separated):").pack(padx=5, pady=5)
        tags_entry = ttk.Entry(dialog, width=50)
        tags_entry.pack(padx=5, pady=5)
        
        def save_card():
            question = question_entry.get().strip()
            answer = answer_text.get("1.0", tk.END).strip()
            tags = [tag.strip() for tag in tags_entry.get().split(",") if tag.strip()]
            
            if question and answer:
                self.command_handler.process_command(f"create flashcard {question}|{answer}|{','.join(tags)}")
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_card).pack(pady=10)

    def show_add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x350")
        
        ttk.Label(dialog, text="Title:").pack(padx=5, pady=5)
        title_entry = ttk.Entry(dialog, width=50)
        title_entry.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Description:").pack(padx=5, pady=5)
        desc_text = tk.Text(dialog, height=3, width=50)
        desc_text.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Due Date (YYYY-MM-DD):").pack(padx=5, pady=5)
        date_entry = ttk.Entry(dialog, width=50)
        date_entry.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Priority (1-5):").pack(padx=5, pady=5)
        priority_var = tk.StringVar(value="3")
        priority_scale = ttk.Scale(dialog, from_=1, to=5, variable=priority_var, orient=tk.HORIZONTAL)
        priority_scale.pack(padx=5, pady=5)
        
        def save_task():
            title = title_entry.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            date = date_entry.get().strip()
            priority = priority_var.get()
            
            if title and date:
                self.command_handler.process_command(f"add task {title}|{desc}|{date}|{priority}")
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_task).pack(pady=10)

    def show_app_launcher_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Launch Application")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Application Name:").pack(padx=5, pady=5)
        app_entry = ttk.Entry(dialog, width=40)
        app_entry.pack(padx=5, pady=5)
        
        # Create listbox for common apps
        apps_list = tk.Listbox(dialog, width=40, height=10)
        apps_list.pack(padx=5, pady=5)
        
        # Add common applications
        common_apps = ['chrome', 'firefox', 'spotify', 'discord', 'vscode', 'word', 'excel', 'powerpoint']
        for app in common_apps:
            apps_list.insert(tk.END, app)
        
        def launch_selected_app():
            app_name = app_entry.get().strip() or apps_list.get(apps_list.curselection()[0])
            if app_name:
                self.command_handler.process_command(f"open {app_name}")
                dialog.destroy()
        
        ttk.Button(dialog, text="Launch", command=launch_selected_app).pack(pady=10)

    def update_settings(self):
        self.config['voice_response'] = self.voice_resp_var.get()
        self.config['beep_sound'] = self.beep_sound_var.get()
        self.command_handler.process_command("save settings")

    def show_manage_flashcards_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Flashcards")
        dialog.geometry("600x400")
        
        # Create notebook for different views
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # All cards tab
        all_cards_frame = ttk.Frame(notebook)
        notebook.add(all_cards_frame, text='All Cards')
        
        # Search frame
        search_frame = ttk.Frame(all_cards_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Cards list
        cards_frame = ttk.Frame(all_cards_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        cards_list = ttk.Treeview(cards_frame, columns=('Question', 'Answer', 'Tags', 'Review Date'))
        cards_list.heading('Question', text='Question')
        cards_list.heading('Answer', text='Answer')
        cards_list.heading('Tags', text='Tags')
        cards_list.heading('Review Date', text='Next Review')
        cards_list.pack(fill=tk.BOTH, expand=True)
        
        # By tag tab
        by_tag_frame = ttk.Frame(notebook)
        notebook.add(by_tag_frame, text='By Tag')
        
        tags_list = ttk.Treeview(by_tag_frame, columns=('Tag', 'Count'))
        tags_list.heading('Tag', text='Tag')
        tags_list.heading('Count', text='Cards')
        tags_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def show_manage_schedule_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Schedule")
        dialog.geometry("800x600")
        
        # Create notebook for different views
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Calendar view
        calendar_frame = ttk.Frame(notebook)
        notebook.add(calendar_frame, text='Calendar')
        
        # Tasks view
        tasks_frame = ttk.Frame(notebook)
        notebook.add(tasks_frame, text='Tasks')
        
        # Task list
        tasks_list = ttk.Treeview(tasks_frame, columns=('Title', 'Due Date', 'Priority', 'Status'))
        tasks_list.heading('Title', text='Title')
        tasks_list.heading('Due Date', text='Due Date')
        tasks_list.heading('Priority', text='Priority')
        tasks_list.heading('Status', text='Status')
        tasks_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(tasks_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Task", command=self.show_add_task_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit Task", command=lambda: self.edit_selected_task(tasks_list)).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Task", command=lambda: self.delete_selected_task(tasks_list)).pack(side=tk.LEFT, padx=5)

    def show_manage_apps_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Applications")
        dialog.geometry("500x400")
        
        # Apps list
        apps_frame = ttk.Frame(dialog)
        apps_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        apps_list = ttk.Treeview(apps_frame, columns=('Name', 'Command'))
        apps_list.heading('Name', text='Name')
        apps_list.heading('Command', text='Command')
        apps_list.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        controls_frame = ttk.Frame(dialog)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add App", command=self.show_add_app_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit App", command=lambda: self.edit_selected_app(apps_list)).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete App", command=lambda: self.delete_selected_app(apps_list)).pack(side=tk.LEFT, padx=5)