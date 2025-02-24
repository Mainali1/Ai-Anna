import webbrowser
import os
from datetime import datetime
from urllib.parse import quote
from .database import DatabaseHandler
import wikipedia

class CommandHandler:
    def __init__(self, gui, voice_engine, study_manager):
        self.gui = gui
        self.voice_engine = voice_engine
        self.study_manager = study_manager
        self.allowed_apps = ["notepad", "calculator", "libreoffice"]
        self.db = DatabaseHandler()

    def process_command(self, command):
        command = command.lower()
        response = "I didn't understand that command."
        
        # Study Commands
        if "start study timer" in command:
            response = self.handle_study_timer(command)
        elif "flashcard" in command:
            response = self.handle_flashcards(command)
        elif "assignment" in command:
            response = self.handle_assignments(command)
        elif "schedule" in command:
            response = self.handle_schedule(command)
            
        # Research Commands
        elif "wikipedia" in command:
            response = self.search_wikipedia(command)
        elif "search web for" in command:
            response = self.search_duckduckgo(command)
            
        # File Management
        elif "open file" in command:
            response = self.open_file(command)
            
        # System Controls
        elif "sleep" in command:
            response = self.toggle_sleep_mode()
            
        # Educational Tools
        elif "summarize" in command:
            response = self.summarize_content(command)
            
        return response

    def handle_study_timer(self, command):
        try:
            work_time = 25
            if "minute" in command:
                work_time = int(command.split("minute")[0].split()[-1])
            self.study_manager.start_pomodoro(work_time)
            return f"Started {work_time} minute study timer!"
        except Exception as e:
            return f"Error starting timer: {str(e)}"

    def handle_flashcards(self, command):
        try:
            if "add" in command:
                parts = command.split("add flashcard")[-1].split(":")
                if len(parts) == 2:
                    front, back = parts[0].strip(), parts[1].strip()
                    self.db.add_flashcard(front, back)
                    return f"Added flashcard: {front}"
                else:
                    return "Please specify the flashcard in the format: 'add flashcard front: back'"
            elif "review" in command:
                cards = self.db.get_due_flashcards()
                if cards:
                    return f"You have {len(cards)} flashcards to review."
                else:
                    return "No flashcards due for review."
            else:
                return "Flashcard command not recognized."
        except Exception as e:
            return f"Error handling flashcards: {str(e)}"

    def handle_assignments(self, command):
        try:
            if "add" in command:
                parts = command.split("add assignment")[-1].split("due")
                if len(parts) == 2:
                    task, due_date = parts[0].strip(), parts[1].strip()
                    self.db.add_assignment("General", task, due_date)
                    return f"Added assignment: {task} due {due_date}"
                else:
                    return "Please specify the assignment in the format: 'add assignment [task] due [date]'"
            elif "list" in command:
                assignments = self.db.get_due_assignments()
                if assignments:
                    return "\n".join([f"{a[2]} (Due: {a[3]})" for a in assignments])
                else:
                    return "No assignments found!"
            else:
                return "Assignment command not recognized."
        except Exception as e:
            return f"Error handling assignments: {str(e)}"

    def handle_schedule(self, command):
        try:
            if "today" in command:
                day = datetime.now().strftime("%a").lower()
                schedule = self.db.get_daily_schedule(day)
                if schedule:
                    return "\n".join([f"{s[3]} at {s[2]}" for s in schedule])
                else:
                    return "No classes scheduled for today."
            else:
                return "Schedule command not recognized."
        except Exception as e:
            return f"Error handling schedule: {str(e)}"

    def search_wikipedia(self, command):
        query = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple matches found: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return "No Wikipedia page found for that query."

    def search_duckduckgo(self, command):
        query = command.replace("search web for", "").strip()
        safe_query = quote(query)
        webbrowser.open(f"https://duckduckgo.com/?q={safe_query}")
        return f"Searching DuckDuckGo for {query}"

    def open_file(self, command):
        try:
            file_path = command.replace("open file", "").strip()
            if os.path.exists(file_path):
                os.startfile(file_path)  # Windows-specific
                return f"Opened file: {file_path}"
            else:
                return "File not found."
        except Exception as e:
            return f"Error opening file: {str(e)}"

    def toggle_sleep_mode(self):
        try:
            # Placeholder for sleep mode functionality
            return "Sleep mode toggled."
        except Exception as e:
            return f"Error toggling sleep mode: {str(e)}"

    def summarize_content(self, command):
        text = command.replace("summarize", "").strip()
        if len(text.split()) < 10:  # If short text
            return "Please provide longer text to summarize."
        return self.study_manager.summarize_text(text)