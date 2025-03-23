from . import Command
import tkinter as tk
from tkinter import ttk

class HelpCommand(Command):
    def validate(self, command: str) -> bool:
        return 'help' in command.lower() or 'commands' in command.lower() or 'what can you do' in command.lower()
        
    def execute(self, command: str) -> str:
        # If called from GUI, show help dialog
        if 'gui' in command.lower():
            self.show_help_dialog()
            return "Displaying help dialog."
        else:
            return self.get_help_text()
    
    def get_help_text(self):
        help_text = """
Here are the commands I can help you with:

System Control:
- "Open [application]" - Launch applications like Chrome, VS Code, Discord, etc.
- "What time is it?" - Get the current time/date
- "Search web for [query]" - Search the web for information
- "Wikipedia [query]" - Search Wikipedia for information
- "Weather in [location]" - Get weather information

Media Control:
- "Play [song/artist]" - Play music
- "Play YouTube [video]" - Play YouTube videos
- "Pause media" - Pause currently playing media
- "Stop media" - Stop currently playing media
- "Next track" - Play next track
- "Previous track" - Play previous track
- "System media" - Toggle between local and system media control

Study Tools:
- "Start 25min timer" - Start a 25-minute study timer
- "Start 45min timer" - Start a 45-minute study timer
- "Review cards" - Review flashcards

Utilities:
- "Help" - Show this help message
- "Exit" - Close the application
"""
        return help_text.strip()
    
    def show_help_dialog(self):
        # Create help dialog
        if not hasattr(self.handler, 'gui') or not self.handler.gui:
            return
            
        dialog = tk.Toplevel(self.handler.gui.root)
        dialog.title("Anna AI Assistant - Help")
        dialog.geometry("600x500")
        
        # Create notebook for categorized help
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System commands tab
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text='System')
        
        system_text = tk.Text(system_frame, wrap=tk.WORD, height=20, width=70)
        system_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        system_text.insert(tk.END, """
System Control Commands:
------------------------
• "Open [application]" - Launch any installed application
• "What time is it?" - Get the current time
• "What's today's date?" - Get the current date
• "Search web for [query]" - Search the web for information
• "Wikipedia [query]" - Search Wikipedia for information
• "Weather in [location]" - Get weather information for a location
• "Take a screenshot" - Capture the current screen
""")
        system_text.config(state=tk.DISABLED)
        
        # Media commands tab
        media_frame = ttk.Frame(notebook)
        notebook.add(media_frame, text='Media')
        
        media_text = tk.Text(media_frame, wrap=tk.WORD, height=20, width=70)
        media_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        media_text.insert(tk.END, """
Media Control Commands:
---------------------
• "Play [song/artist]" - Play music from your library
• "Play YouTube [video]" - Search and play YouTube videos
• "Pause media" - Pause currently playing media
• "Stop media" - Stop currently playing media
• "Next track" - Play next track
• "Previous track" - Play previous track
• "Volume up/down" - Adjust volume
• "System media" - Toggle between local and system media control
""")
        media_text.config(state=tk.DISABLED)
        
        # Study commands tab
        study_frame = ttk.Frame(notebook)
        notebook.add(study_frame, text='Study')
        
        study_text = tk.Text(study_frame, wrap=tk.WORD, height=20, width=70)
        study_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        study_text.insert(tk.END, """
Study Tool Commands:
------------------
• "Start 25min timer" - Start a 25-minute study timer (Pomodoro)
• "Start 45min timer" - Start a 45-minute study timer
• "Add flashcard [Front]: [Back]" - Create a new flashcard
• "Review cards" - Start a flashcard review session
• "Add assignment [Task] due [Date]" - Add a new assignment
• "What's on schedule today?" - Check today's schedule
""")
        study_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)