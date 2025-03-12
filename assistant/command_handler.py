import webbrowser
import os
import subprocess
import sys
import wikipedia
from datetime import datetime
from urllib.parse import quote
from .weather_service import WeatherService
from .system_controller import SystemController

import random

class CommandHandler:
    def __init__(self, gui, voice_engine, study_manager, music_controller, email_manager, config, spaced_repetition):
        self.gui = gui
        self.voice_engine = voice_engine
        self.study_manager = study_manager
        self.music_controller = music_controller
        self.email_manager = email_manager
        self.config = config
        self.spaced_repetition = spaced_repetition
        self.weather_service = WeatherService()
        self.system_controller = SystemController()
        self.is_listening = False
        self.app_map = {
            'music player': 'spotify',
            'email client': 'thunderbird',
            'browser': 'Opera Gx Browser',
            'text editor': 'Vs Code',
            'downloads': os.path.expanduser('~\Downloads'),
            'documents': os.path.expanduser('~\Documents'),
            'desktop': os.path.expanduser('~\Desktop'),
            'chrome': 'chrome',
            'edge': 'msedge',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'calculator': 'calc',
            'paint': 'mspaint',
            'notepad': 'notepad',
            'explorer': 'explorer',
            'task manager': 'taskmgr',
            'control panel': 'control',
            'settings': 'ms-settings:',
            'cmd': 'cmd',
            'powershell': 'powershell',
            'terminal': 'wt',
            'discord': 'discord'
        }
        self.custom_apps = {}
        # Add conversation context
        self.conversation_context = {
            'last_topic': None,
            'follow_up_needed': False,
            'user_name': None,
            'mood': 'neutral'
        }
        self.casual_acknowledgments = [
            "Sure thing!", "Got it!", "I'm on it!",
            "No problem!", "Alright!", "You got it!"
        ]
        self.empathy_responses = {
            'stress': ["I understand this might be stressful.", "Let's tackle this together."],
            'success': ["That's fantastic!", "I'm glad to hear that!"],
            'tired': ["Maybe we should take a short break?", "Remember to rest when needed."]
        }
        self.mood_transitions = {
            'neutral': ['happy', 'curious', 'focused'],
            'happy': ['excited', 'playful', 'neutral'],
            'curious': ['focused', 'playful', 'neutral'],
            'focused': ['satisfied', 'neutral', 'tired'],
            'tired': ['neutral', 'concerned'],
            'concerned': ['empathetic', 'neutral']
        }
        
        self.mood_responses = {
            'happy': ["I'm having a great time helping you!", "This is fun!"],
            'curious': ["That's interesting!", "Tell me more about that!"],
            'focused': ["Let's stay on track.", "We're making good progress."],
            'tired': ["Maybe we should take a break soon?", "Remember to rest!"],
            'concerned': ["Everything okay?", "Let me know if you need help."],
            'empathetic': ["I understand how you feel.", "We'll figure this out together."]
        }

    def update_mood(self, command):
        current_mood = self.conversation_context['mood']
        
        # Update mood based on command content and context
        if any(word in command for word in ['tired', 'exhausted', 'break']):
            new_mood = 'tired'
        elif any(word in command for word in ['worried', 'stress', 'anxious']):
            new_mood = 'concerned'
        elif any(word in command for word in ['fun', 'great', 'awesome']):
            new_mood = 'happy'
        elif any(word in command for word in ['interesting', 'what', 'how', 'why']):
            new_mood = 'curious'
        elif any(word in command for word in ['focus', 'study', 'work']):
            new_mood = 'focused'
        else:
            # Randomly transition to a related mood
            new_mood = random.choice(self.mood_transitions.get(current_mood, ['neutral']))
        
        self.conversation_context['mood'] = new_mood
        return self.mood_responses.get(new_mood, [])[0] if self.mood_responses.get(new_mood) else ""

    def get_contextual_response(self, command_type, command=""):
        response = random.choice(self.casual_acknowledgments) + " "
        
        # Add mood-based response
        mood_response = self.update_mood(command)
        if mood_response:
            response = mood_response + " " + response
        
        if command_type == 'study':
            if self.conversation_context['last_topic'] == 'study':
                response += "Still focusing on your studies? That's great! "
            self.conversation_context['follow_up_needed'] = True
        
        elif command_type == 'timer':
            if command and 'stress' in command.lower():
                response += random.choice(self.empathy_responses['stress'])
        
        return response

    def process_command(self, command):
        print(f"[DEBUG] Received command: {command}")  # Debug line
        command = command.lower()
        response = ""
        
        # Add personality and contextual awareness
        self.last_command_time = getattr(self, 'last_command_time', None)
        current_time = datetime.now()
        
        # Add time-based greetings with personality
        if self.last_command_time is None or (current_time - self.last_command_time).seconds > 300:
            hour = current_time.hour
            if 5 <= hour < 12:
                response = "Good morning! Hope you're ready for a productive day! "
            elif 12 <= hour < 17:
                response = "Good afternoon! How's your day going? "
            else:
                response = "Good evening! Still working hard, I see! "
        
        self.last_command_time = current_time
        
        try:
            # Study Commands
            if "timer" in command and ("start" in command or "minute" in command):
                base_response = self.get_contextual_response('timer')
                response += base_response + self.handle_study_timer(command)
                if self.conversation_context['follow_up_needed']:
                    response += "\nWould you like me to set up any study materials while the timer runs?"
            
            elif "flashcard" in command:
                base_response = self.get_contextual_response('study')
                response += base_response + self.handle_flashcards(command)
                if 'create' in command:
                    response += "\nGreat job adding flashcards! Would you like to do a quick review session?"
            
            elif "assignment" in command:
                base_response = self.get_contextual_response('study')
                response += base_response + self.handle_assignments(command)
                if 'due' in command:
                    response += "\nI can help you break this down into manageable tasks. Would that be helpful?"
            
            # Keep existing command handling with added personality
            elif "time" in command or "date" in command:
                response += self.get_current_time_date(command)
                response += "\nNeed me to set any reminders for you?"
            
            elif "music" in command or "play" in command:
                response += self.get_contextual_response('entertainment')
                response += self.control_music(command)
                if 'study' in self.conversation_context['last_topic']:
                    response += "\nI can help you find some focus-friendly music if you'd like."
            
            # Add application opening command handling
            elif any(app_name in command for app_name in self.app_map.keys()) or "open" in command:
                response += self.open_application(command)
            
            # Update conversation context
            if "study" in command or "assignment" in command or "flashcard" in command:
                self.conversation_context['last_topic'] = 'study'
            elif "music" in command or "play" in command:
                self.conversation_context['last_topic'] = 'entertainment'
            
            if not response:
                response = "I'm not quite sure about that one. Could you rephrase it, or would you like to know what I can help you with?"
            
        except Exception as e:
            response = f"Oops! Something went wrong there. Mind trying that again? Error: {str(e)}"
        
        self.gui.display_response(response)

        if self.config['voice_response']:
            self.voice_engine.speak(response)
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
        elif "delete" in command:
            try:
                card_id = int(command.split("delete flashcard")[-1].strip())
                if self.study_manager.db.delete_flashcard(card_id):
                    return f"Flashcard {card_id} deleted successfully"
                return "Flashcard not found"
            except ValueError:
                return "Use format: 'delete flashcard [ID]'"
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
        elif "delete" in command:
            try:
                assignment_id = int(command.split("delete assignment")[-1].strip())
                if self.study_manager.db.delete_assignment(assignment_id):
                    return f"Assignment {assignment_id} deleted successfully"
                return "Assignment not found"
            except ValueError:
                return "Use format: 'delete assignment [ID]'"
        elif "list" in command:
            assignments = self.study_manager.db.get_due_assignments()
            return "\n".join([f"{a[2]} (Due: {a[3]})" for a in assignments]) if assignments else "No assignments"
        return "Assignment command not recognized"

    def handle_schedule(self, command):
        if "today" in command:
            schedule = self.study_manager.db.get_daily_schedule(datetime.now().strftime("%a").lower())
            return "\n".join([f"{s[3]} at {s[2]}" for s in schedule]) if schedule else "No classes today"
        elif "delete" in command:
            try:
                schedule_id = int(command.split("delete schedule")[-1].strip())
                if self.study_manager.db.delete_schedule(schedule_id):
                    return f"Schedule {schedule_id} deleted successfully"
                return "Schedule not found"
            except ValueError:
                return "Use format: 'delete schedule [ID]'"
        return "Schedule command not recognized"

    # System Methods
    def get_current_time_date(self, command):
        current_time = datetime.now()
        time_str = current_time.strftime("%I:%M %p")
        date_str = current_time.strftime("%A, %B %d, %Y")
        
        responses = [
            f"It's {time_str} on {date_str}.",
            f"The time is {time_str}, and today is {date_str}.",
            f"Right now it's {time_str} on {date_str}."
        ]
        return random.choice(responses)

    def control_music(self, command):
        try:
            if "play" in command:
                if "study" in command:
                    return self.music_controller.play_study_music()
                elif "relax" in command:
                    return self.music_controller.play_relaxing_music()
                else:
                    return self.music_controller.play_music()
            elif "stop" in command or "pause" in command:
                return self.music_controller.stop_music()
            elif "next" in command:
                return self.music_controller.next_track()
            elif "previous" in command:
                return self.music_controller.previous_track()
            return "I'm not sure what you want me to do with the music. Try saying play, stop, next, or previous."
        except Exception as e:
            return f"I couldn't control the music: {str(e)}"

    def open_application(self, command):
        try:
            app_name = next((name for name in self.app_map.keys() if name in command), None)
            if app_name:
                app = self.app_map[app_name]
                if os.path.exists(app):
                    subprocess.Popen([app], shell=True)
                else:
                    subprocess.Popen(app, shell=True)
                return f"Opening {app_name}..."
            return "I'm not sure which application you want to open."
        except Exception as e:
            return f"I couldn't open that application: {str(e)}"
    def register_custom_app(self, name, path):
        """Register a custom application or file path"""
        if os.path.exists(path):
            self.custom_apps[name.lower()] = path
            return f"Registered {name} successfully"
        return f"Path not found: {path}"

    def open_application(self, command):
        command = command.lower()
        
        # Handle web URLs first
        if any(prefix in command for prefix in ['http://', 'https://', 'www.']):
            url = command.replace('open', '').strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return f"Opening {url}"

        # Handle web shortcuts
        web_shortcuts = {
            'google': 'https://www.google.com',
            'youtube': 'https://www.youtube.com',
            'github': 'https://www.github.com',
            'gmail': 'https://mail.google.com',
            'maps': 'https://www.google.com/maps',
            'drive': 'https://drive.google.com',
            'calendar': 'https://calendar.google.com'
        }

        for shortcut, url in web_shortcuts.items():
            if shortcut in command:
                webbrowser.open(url)
                return f"Opening {shortcut}"

        # First check custom apps
        for app_name, path in self.custom_apps.items():
            if app_name in command:
                try:
                    if sys.platform == "win32":
                        os.startfile(path)
                    else:
                        subprocess.run([path])
                    return f"Opening {app_name}"
                except Exception as e:
                    return f"Error opening {app_name}: {str(e)}"

        # Then check default apps
        for app_name, exe in self.app_map.items():
            if app_name in command:
                try:
                    # Handle directory paths
                    if os.path.isdir(exe):
                        if sys.platform == "win32":
                            os.startfile(exe)
                        else:
                            subprocess.run(['xdg-open', exe])
                        return f"Opening {app_name}"

                    # Additional search paths for Windows
                    search_paths = [
                        os.environ.get('ProgramFiles', ''),
                        os.environ.get('ProgramFiles(x86)', ''),
                        os.environ.get('LocalAppData', ''),
                        os.environ.get('AppData', ''),
                        os.path.join(os.environ.get('LocalAppData', ''), 'Programs'),
                        os.path.join(os.environ.get('AppData', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
                    ]
                    
                    # Search for the executable
                    for search_path in search_paths:
                        if not search_path:
                            continue
                            
                        # Direct path check
                        direct_path = os.path.join(search_path, f"{exe}.exe")
                        if os.path.exists(direct_path):
                            if sys.platform == "win32":
                                os.startfile(direct_path)
                            else:
                                subprocess.run([direct_path])
                            return f"Opening {app_name}"
                        
                        # Recursive search
                        for root, dirs, files in os.walk(search_path):
                            if f"{exe}.exe" in files:
                                full_path = os.path.join(root, f"{exe}.exe")
                                if sys.platform == "win32":
                                    os.startfile(full_path)
                                else:
                                    subprocess.run([full_path])
                                return f"Opening {app_name}"
                    
                    # Fallback to simple command
                    if sys.platform == "win32":
                        try:
                            subprocess.run([exe], shell=True)
                            return f"Opening {app_name}"
                        except Exception:
                            os.system(f"start {exe}")
                            return f"Opening {app_name}"
                    else:
                        subprocess.run([exe])
                        return f"Opening {app_name}"
                except Exception as e:
                    return f"Error opening {app_name}: {str(e)}"

        # If no application found, try to open as a file path
        try:
            path = command.replace("open", "").strip()
            if os.path.exists(path):
                if sys.platform == "win32":
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
                return f"Opened {path}"
        except Exception as e:
            return f"Error opening file: {str(e)}"

        return "Application or file not found"

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