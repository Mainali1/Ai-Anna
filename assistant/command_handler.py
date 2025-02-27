import webbrowser
import os
import subprocess
import sys
import wikipedia
from datetime import datetime
from urllib.parse import quote

class CommandHandler:
    def __init__(self, gui, voice_engine, study_manager, music_controller, email_manager, config):
        self.gui = gui
        self.voice_engine = voice_engine
        self.study_manager = study_manager
        self.music_controller = music_controller
        self.email_manager = email_manager
        self.config = config
        self.is_listening = False
        self.app_map = {
            'music player': 'spotify',
            'email client': 'thunderbird',
            'browser': 'firefox',
            'text editor': 'notepad'
        }

    def process_command(self, command):
        print(f"[DEBUG] Received command: {command}")  # Debug line
        command = command.lower()
        response = "Command not recognized"
        
        try:
            # Study Commands
            if "timer" in command and ("start" in command or "minute" in command):
                response = self.handle_study_timer(command)
            elif "flashcard" in command:
                response = self.handle_flashcards(command)
            elif "assignment" in command:
                response = self.handle_assignments(command)
            elif "schedule" in command:
                response = self.handle_schedule(command)
            
            # System Commands
            elif "time" in command or "date" in command:
                response = self.get_current_time_date(command)
            elif "open" in command:
                response = self.open_application(command)
            elif "sleep" in command:
                response = self.toggle_listening()
            
            # Media Commands
            elif "music" in command or "play" in command:
                response = self.control_music(command)
            
            # Research Commands
            elif "wikipedia" in command:
                response = self.search_wikipedia(command)
            elif "search web" in command:
                response = self.search_duckduckgo(command)
            
            # File Management
            elif "open file" in command:
                response = self.open_file(command)
            
            # Email Commands
            elif "email" in command:
                response = self.handle_email(command)
            
            # Help Commands
            elif "help" in command:
                response = self.show_help()
            
        except Exception as e:
            response = f"Error processing command: {str(e)}"
        
        self.gui.display_response(response)

        if self.config['voice_response']:
            self.voice_engine.speak(response)  # Proper indentation
        return response

    def toggle_listening(self):
        """Toggle voice listening state"""
        self.is_listening = not self.is_listening
        self.gui.update_ui_state(self.is_listening)
        if self.is_listening:
            self.voice_engine.start_listening()
        else:
            self.voice_engine.stop_listening()
        return f"Voice listening {'activated' if self.is_listening else 'deactivated'}"

    # Study Management Methods
    def handle_study_timer(self, command):
        try:
            work_time = 25
            if "minute" in command:
                work_time = int(command.split("minute")[0].split()[-1])
            self.study_manager.start_pomodoro(work_time)
            return f"Started {work_time} minute study timer!"
        except Exception as e:
            return f"Timer error: {str(e)}"

    def handle_flashcards(self, command):
        if "add" in command:
            parts = command.split("add flashcard")[-1].split(":")
            if len(parts) == 2:
                front, back = parts[0].strip(), parts[1].strip()
                self.study_manager.create_flashcard(front, back)
                return f"Added flashcard: {front}"
            return "Use format: 'add flashcard Front: Back'"
        elif "review" in command:
            cards = self.study_manager.get_due_cards()
            return f"{len(cards)} cards due" if cards else "No cards due"
        return "Flashcard command not recognized"

    def handle_assignments(self, command):
        if "add" in command:
            parts = command.split("add assignment")[-1].split("due")
            if len(parts) == 2:
                task, due_date = parts[0].strip(), parts[1].strip()
                self.study_manager.db.add_assignment("General", task, due_date)
                return f"Added assignment: {task} due {due_date}"
            return "Use format: 'add assignment Task due Date'"
        elif "list" in command:
            assignments = self.study_manager.db.get_due_assignments()
            return "\n".join([f"{a[2]} (Due: {a[3]})" for a in assignments]) if assignments else "No assignments"
        return "Assignment command not recognized"

    def handle_schedule(self, command):
        if "today" in command:
            schedule = self.study_manager.db.get_daily_schedule(datetime.now().strftime("%a").lower())
            return "\n".join([f"{s[3]} at {s[2]}" for s in schedule]) if schedule else "No classes today"
        return "Schedule command not recognized"

    # System Methods
    def get_current_time_date(self, command):
        now = datetime.now()
        return f"{now.strftime('%H:%M')} on {now.strftime('%B %d, %Y')}"

    def open_application(self, command):
        for app_name, exe in self.app_map.items():
            if app_name in command:
                try:
                    if sys.platform == "win32":
                        os.system(f"start {exe}")
                    else:
                        subprocess.run([exe])
                    return f"Opening {app_name}"
                except Exception as e:
                    return f"Error opening {app_name}: {str(e)}"
        return "Application not found"

    # Media Methods
    def control_music(self, command):
        if "play" in command:
            self.music_controller.toggle_playback()
            return "Music started" if self.music_controller.is_playing() else "Music resumed"
        elif "pause" in command:
            self.music_controller.toggle_playback()
            return "Music paused"
        elif "next" in command:
            self.music_controller.next_track()
            return "Next track"
        return "Music command not recognized"

    # Research Methods
    def search_wikipedia(self, command):
        query = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple matches: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return "No Wikipedia page found"

    def search_duckduckgo(self, command):
        query = command.replace("search web for", "").strip()
        webbrowser.open(f"https://duckduckgo.com/?q={quote(query)}")
        return f"Searching for {query}"

    # File Methods
    def open_file(self, command):
        path = command.replace("open file", "").strip()
        if os.path.exists(path):
            try:
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
                return f"Opened {path}"
            except Exception as e:
                return f"Open error: {str(e)}"
        return "File not found"

    # Email Methods
    def handle_email(self, command):
        if "check" in command:
            count = self.email_manager.check_email()
            return f"You have {count} unread emails"
        elif "send" in command:
            return "Email sending not implemented"
        return "Email command not recognized"

    # Help Methods
    def show_help(self):
        return """Available Commands:
        - Start [X] minute study timer
        - Add flashcard [Front]: [Back]
        - Add assignment [Task] due [Date]
        - What's on schedule today?
        - Open [application]
        - Play/Pause music
        - Wikipedia [topic]
        - Search web for [query]
        - Open file [path]
        - Check email"""