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
        master.geometry("1000x700")
        master.configure(bg='#1a1a1a')
        
        self.setup_theme()
        self.create_layout()
        self.setup_bindings()
        
        self.voice_resp_var = tk.BooleanVar(value=self.config['voice_response'])
        self.beep_sound_var = tk.BooleanVar(value=self.config['beep_sound'])
        self.sidebar_visible = True

    def setup_theme(self):
        self.style = ttk.Style()
        self.style.theme_use('black')
        
        # Modern button style
        self.style.configure('Custom.TButton',
                           font=('Segoe UI', 10),
                           foreground='#ffffff',
                           background='#2d2d2d',
                           bordercolor='#3d3d3d',
                           padding=5)
        self.style.map('Custom.TButton',
                      foreground=[('active', '#ffffff'), ('pressed', '#cccccc')],
                      background=[('active', '#3d3d3d'), ('pressed', '#2d2d2d')])
        
        # Label styles
        self.style.configure('Title.TLabel',
                           font=('Segoe UI', 16, 'bold'),
                           foreground='#ffffff',
                           background='#1a1a1a')
        self.style.configure('Subtitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground='#cccccc',
                           background='#1a1a1a')
        
        # Frame styles
        self.style.configure('Sidebar.TFrame',
                           background='#2d2d2d')
        self.style.configure('Content.TFrame',
                           background='#1a1a1a')

    def create_layout(self):
        # Main container
        self.main_container = ttk.Frame(self.master, style='Content.TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Collapsible sidebar
        self.sidebar = ttk.Frame(self.main_container, style='Sidebar.TFrame', width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        self.sidebar.pack_propagate(False)
        
        # Toggle sidebar button
        self.toggle_btn = ttk.Button(self.sidebar,
                                   text='≡',
                                   style='Custom.TButton',
                                   command=self.toggle_sidebar)
        self.toggle_btn.pack(anchor='ne', padx=5, pady=5)
        
        # Create sidebar content
        self.create_sidebar_content()
        
        # Main content area
        self.content = ttk.Frame(self.main_container, style='Content.TFrame')
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create main content
        self.create_main_content()

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