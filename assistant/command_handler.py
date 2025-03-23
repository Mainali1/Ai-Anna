import logging
import os
import random
from datetime import datetime
from typing import Dict, Any, Optional
from .commands import CommandRegistry
from .commands.music_command import MediaCommand  # Changed from MusicCommand
from .commands.weather_command import WeatherCommand
from .commands.web_search_command import WebSearchCommand
from .commands.wikipedia_command import WikipediaCommand
from .weather_service import WeatherService
from .system_controller import SystemController
from .conversation_storage import ConversationStorage
from .screen_analyzer import ScreenAnalyzer

class CommandHandler:
    def __init__(self, gui, voice_engine, study_manager, music_controller, email_manager, config, spaced_repetition, ai_service, file_system, external_services):
        # Setup logging first
        import logging
        from datetime import datetime
        import random
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize core services
        self.external_services = external_services
        self.ai_service = ai_service
        self.file_system = file_system
        self.gui = gui
        self.voice_engine = voice_engine
        self.study_manager = study_manager
        self.music_controller = music_controller
        self.email_manager = email_manager
        self.config = config
        self.spaced_repetition = spaced_repetition
        self.weather_service = WeatherService()
        self.system_controller = SystemController()
        self.screen_analyzer = ScreenAnalyzer(config)
        self.conversation_storage = ConversationStorage()
        self.is_listening = False
        self.ai_mode = False
        
        # Get enhanced context manager and dynamic response generator if available
        self.enhanced_context = None
        self.dynamic_response = None
        if hasattr(gui, 'container') and gui.container:
            try:
                self.enhanced_context = gui.container.get_service('enhanced_context')
                self.dynamic_response = gui.container.get_service('dynamic_response')
            except KeyError:
                pass

        # Initialize command registry
        self.command_registry = CommandRegistry()
        self._register_commands()
        
        # Initialize last command time
        self.last_command_time = None
        
        # Auto-greeting if enabled
        if self.config.get('auto_greeting', True) and self.enhanced_context:
            self._auto_greeting()
            
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

    def _register_commands(self):
        """Register all available commands"""
        try:
            # Import all command classes
            from .commands.music_command import MediaCommand
            from .commands.weather_command import WeatherCommand
            from .commands.web_search_command import WebSearchCommand
            from .commands.wikipedia_command import WikipediaCommand
            from .commands.time_command import TimeCommand
            from .commands.system_command import SystemCommand
            from .commands.help_command import HelpCommand
            from .commands.youtube_command import YouTubeCommand  # Add this line
            
            # Register core commands with proper error handling
            commands_to_register = [
                ('media', MediaCommand),
                ('weather', WeatherCommand),
                ('time', TimeCommand),
                ('web_search', WebSearchCommand),
                ('wikipedia', WikipediaCommand),
                ('system', SystemCommand),
                ('help', HelpCommand),
                ('youtube', YouTubeCommand)  # Add this line
            ]
            
            for intent, command_class in commands_to_register:
                try:
                    self.command_registry.register(intent, command_class)
                    self.logger.info(f"Successfully registered {intent} command")
                except Exception as e:
                    self.logger.error(f"Failed to register {intent} command: {str(e)}")
                    
            # Initialize command instances to verify they work
            for intent, command_class in self.command_registry.get_all_commands().items():
                try:
                    command_instance = command_class(self)
                    self.logger.info(f"Successfully initialized {intent} command")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {intent} command: {str(e)}")
                    # Remove failed command from registry
                    self.command_registry._commands.pop(intent, None)
        except Exception as e:
            self.logger.error(f"Error in command registration: {str(e)}")
            # Don't raise error, just log it
            self.logger.warning("Continuing with partial command registration")

    
    def determine_intent(self, command: str) -> str:
        """Determine the intent of the command"""
        command = command.lower()
        
        # Check each registered command's validation
        for intent, command_class in self.command_registry.get_all_commands().items():
            command_instance = command_class(self)
            if command_instance.validate(command):
                return intent
        
        # Default to conversation if no specific intent is found
        return 'conversation'

    def get_contextual_response(self, command_type, command=""):
        response = ""
        intent = self.determine_intent(command)
        
        # Update conversation context
        if intent != self.conversation_context.get('last_topic'):
            self.conversation_context['last_topic'] = intent
            response += random.choice(self.casual_acknowledgments) + " "
        
        # Add follow-up suggestions based on intent
        if intent == 'study' and 'timer' not in command:
            response += "Would you like me to set a study timer? "
        elif intent == 'music' and 'play' in command:
            if not any(genre in command for genre in ['study', 'focus', 'ambient']):
                response += "I can suggest some focus-friendly music if you're studying. "
        elif intent == 'weather':
            response += "Would you like to know the forecast for the rest of the day? "
        
        return response

    def process_command(self, command: str) -> str:
        """Process the command and return response"""
        try:
            if not command:
                return "I didn't receive any command. Could you please try again?"
                
            self.logger.info(f"Processing command: {command}")
            command = command.lower()
            
            # Initialize response variable
            response = ""
            
            # Update enhanced context if available
            if self.enhanced_context:
                self.enhanced_context.update_context(command, "")
            
            # Determine intent and get command handler
            intent = self.determine_intent(command)
            command_class = self.command_registry.get_command(intent)
            
            if command_class:
                try:
                    # Execute command through command pattern
                    command_instance = command_class(self)
                    if command_instance.validate(command):
                        command_response = command_instance.execute(command)
                        if command_response:
                            # Return the response but don't display it here
                            # The display will be handled by the caller
                            return command_response
                        else:
                            return "I processed your command but didn't get a response. Please try again."
                    else:
                        return "I'm not sure how to handle that command."
                except Exception as e:
                    self.logger.error(f"Error executing command {intent}: {str(e)}")
                    return f"Sorry, I encountered an error: {str(e)}"
            else:
                # Handle specific commands based on intent
                try:
                    if intent == 'task':
                        if 'timer' in command:
                            timer_response = self.handle_study_timer(command)
                            response += timer_response if timer_response else ""
                        elif 'reminder' in command:
                            reminder_response = self.handle_reminder(command)
                            response += reminder_response if reminder_response else ""
                        elif 'schedule' in command:
                            schedule_response = self.handle_schedule(command)
                            response += schedule_response if schedule_response else ""
                    elif intent == 'study':
                        if 'flashcard' in command:
                            response += self.handle_flashcards(command)
                        elif 'assignment' in command:
                            response += self.handle_assignments(command)
                    elif intent == 'music':
                        response += self.control_music(command)
                    elif intent == 'weather':
                        if hasattr(self, 'weather_service'):
                            if 'forecast' in command:
                                response += self.weather_service.get_daily_forecast()
                            else:
                                response += self.weather_service.get_current_weather()
                        else:
                            response += "I'm sorry, the weather service is not properly configured."
                    elif intent == 'app':
                        response += self.launch_application(command)
                    elif intent == 'search':
                        if hasattr(self, 'external_services'):
                            search_query = command.lower().replace('search', '').replace('web', '').strip()
                            search_results = self.external_services.web_search(search_query)
                            if search_results:
                                response += "Here's what I found:\n\n"
                                for result in search_results[:3]:
                                    response += f"- {result['title']}\n  {result['snippet']}\n  {result['link']}\n\n"
                            else:
                                response += "I couldn't find any results for that search."
                        else:
                            response += "I'm sorry, the search service is not properly configured."
                    elif intent == 'conversation':
                        if self.conversation_context['last_topic']:
                            response += self.handle_follow_up(command)
                        else:
                            response += self._handle_general_conversation(command)
                    
                    # Handle study-related follow-up
                    if 'study' in self.conversation_context['last_topic']:
                        response += "\nI can help you find some focus-friendly music if you'd like."
                    
                    # Add application opening command handling
                    elif any(app_name in command for app_name in self.app_map.keys()) or "open" in command:
                        response += self.open_application(command)
                except Exception as e:
                    self.logger.error(f"Error handling command: {str(e)}")
                    response += f"Sorry, I couldn't process that command: {str(e)}"
            
            # Update conversation context
            if "study" in command or "assignment" in command or "flashcard" in command:
                self.conversation_context['last_topic'] = 'study'
            elif "music" in command or "play" in command:
                self.conversation_context['last_topic'] = 'entertainment'
            
            # Store conversation history
            self.conversation_storage.store_interaction(command, response)
            
            # Store the interaction with context
            screen_context = self.screen_analyzer.get_screen_context() if hasattr(self, 'screen_analyzer') else {}
            context = {
                'screen_context': screen_context,
                'mood': self.conversation_context['mood'],
                'last_topic': self.conversation_context['last_topic']
            }
            self.conversation_storage.add_interaction(command, response, context)
            
            # Update enhanced context with the response
            if self.enhanced_context:
                self.enhanced_context.update_context(command, response)
            
            if hasattr(self, 'gui'):
                self.gui.display_response(response)

            if hasattr(self, 'config') and self.config.get('voice_response'):
                self.voice_engine.speak(response)
                
            return response.strip()
            
        except Exception as e:
            error_msg = f"Oops! Something went wrong there. Mind trying that again? Error: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def handle_follow_up(self, command):
        """Handle follow-up interactions based on previous conversation context
        Args:
            command (str): The user's follow-up command
        Returns:
            str: Response to the follow-up command
        """
        try:
            last_topic = self.conversation_context['last_topic']
            response = ""
            
            if last_topic == 'study':
                if 'yes' in command:
                    response = "Great! Let me help you set that up. "
                    if self.conversation_context.get('timer_suggested'):
                        response += self.handle_study_timer("start timer 25 minutes")
                elif 'no' in command:
                    response = "No problem! Let me know if you need anything else. "
            elif last_topic == 'weather':
                if 'yes' in command:
                    response = self.get_weather("forecast")
                elif 'no' in command:
                    response = "Alright! Let me know if you want to check the weather later."
            
            return response
            
        except KeyError:
            return "I don't have context from our previous conversation."
        except Exception as e:
            return f"Error processing follow-up: {str(e)}"

    def _handle_time_based_greeting(self, current_time: datetime) -> str:
        """Handle time-based greetings"""
        
    def _auto_greeting(self):
        """Automatically greet the user when the application starts"""
        if not self.enhanced_context:
            return
            
        if self.enhanced_context.should_greet_user():
            greeting = self.enhanced_context.generate_greeting()
            self.gui.show_response(greeting)
            if self.config.get('voice_response', True):
                self.voice_engine.speak(greeting)
        
        # Initialize current_time before using it
        current_time = datetime.now()
        if self.last_command_time is None or (current_time - self.last_command_time).seconds > 300:
            self.last_command_time = current_time
            hour = current_time.hour
            
            if 5 <= hour < 12:
                return "Good morning! Hope you're ready for a productive day! "
            elif 12 <= hour < 17:
                return "Good afternoon! How's your day going? "
            else:
                return "Good evening! Still working hard, I see! "
        return ""
    
    def _handle_general_conversation(self, command: str) -> str:
        """Handle general conversation when no specific intent is found"""
        try:
            if any(word in command for word in ['hi', 'hello', 'hey']):
                return "Hello! How can I help you today? "
            elif any(word in command for word in ['what', 'how', 'why', 'when', 'where']):
                if 'you' in command:
                    return "I'm your AI assistant, designed to help you with various tasks. "
                return "That's an interesting question. How can I help you with that? "
            elif any(word in command for word in ['thanks', 'thank', 'appreciate']):
                return "You're welcome! I'm happy to help. "
            elif any(word in command for word in ['bye', 'goodbye', 'see you']):
                return "Goodbye! Have a great day! "
            return "I'm here to help! You can ask me about the weather, play music, or help with your studies. "
        except Exception as e:
            self.logger.error(f"Error in general conversation: {str(e)}")
            return "I'm not sure how to respond to that. Could you try rephrasing?"

    def handle_reminder(self, command):
        response = ""
        if 'set' in command:
            # Extract time and task from command
            response = "I'll remind you about that. "
            self.conversation_context['follow_up_needed'] = True
        elif 'list' in command:
            response = "Here are your current reminders: "
            # Implement reminder listing logic
        return response

    def handle_schedule(self, command):
        response = ""
        if "today" in command:
            response = "Here's your schedule for today: "
            # Implement schedule retrieval logic
        elif "add" in command:
            response = "I'll add that to your schedule. "
            # Implement schedule addition logic
        elif "delete" in command:
            try:
                schedule_id = int(command.split("delete schedule")[-1].strip())
                if self.study_manager.db.delete_schedule(schedule_id):
                    return f"Schedule {schedule_id} deleted successfully"
                return "Schedule not found"
            except ValueError:
                return "Use format: 'delete schedule [ID]'"
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

    # Add this to the control_music method
    def control_music(self, command):
        """Handle music control commands"""
        try:
            # Check for YouTube commands first
            if "youtube" in command.lower():
                query = command.lower().replace("play youtube", "").replace("youtube", "").strip()
                if query:
                    success, message = self.music_controller.play_youtube(query)
                    return message
                else:
                    return "Please specify what you want to play on YouTube."
                
            # Make sure music controller is initialized
            if not hasattr(self, 'music_controller') or not self.music_controller:
                print("Media controller not initialized")
                return "Media controller is not available."
                
            # Make sure music path is set
            if not hasattr(self.music_controller, 'music_path') or not self.music_controller.music_path:
                self.music_controller.set_music_path()
                
            # Process media commands
            if "play" in command.lower():
                # Check for specific media or artist
                if "by" in command.lower():
                    artist = command.split("by")[-1].strip()
                    if self.music_controller.play_by_artist(artist):
                        return f"Playing media by {artist}."
                    else:
                        return f"Couldn't find media by {artist}."
                elif "playlist" in command.lower():
                    playlist = command.replace('play playlist', '').strip()
                    if self.music_controller.play_playlist(playlist):
                        return f"Playing playlist: {playlist}."
                    else:
                        return f"Couldn't find playlist: {playlist}."
                else:
                    # Extract media name if present
                    media_name = command.replace('play', '').strip()
                    if media_name:
                        if self.music_controller.play_media(media_name):
                            return f"Playing {media_name}."
                        else:
                            return f"Couldn't find {media_name}."
                    else:
                        # General play command
                        self.music_controller.play()
                        return "Playing media."
            elif "pause" in command.lower() or "stop" in command.lower():
                self.music_controller.pause()
                return "Media paused."
            elif "resume" in command.lower():
                self.music_controller.resume()
                return "Resuming media."
            elif "next" in command.lower():
                self.music_controller.next_track()
                return "Playing next track."
            elif "previous" in command.lower() or "prev" in command.lower():
                self.music_controller.previous_track()
                return "Playing previous track."
            elif "volume" in command.lower():
                if "up" in command.lower():
                    self.music_controller.volume_up()
                    return "Volume increased."
                elif "down" in command.lower():
                    self.music_controller.volume_down()
                    return "Volume decreased."
                else:
                    try:
                        level = int(command.split("volume")[-1].strip())
                        self.music_controller.set_volume(level)
                        return f"Volume set to {level}%."
                    except ValueError:
                        return "Please specify a volume level (0-100)."
            return "Media command not recognized."
        except Exception as e:
            self.logger.error(f"Error in music control: {str(e)}")
            return f"Sorry, I couldn't control the media: {str(e)}"

    def launch_application(self, command):
        """Launch applications based on command"""
        try:
            command = command.lower()
            # Extract app name from command
            app_name = None
            for key in self.app_map.keys():
                if key in command:
                    app_name = self.app_map[key]
                    break
            
            if not app_name:
                return "I'm not sure which application you want to open."
            
            # Launch the application
            try:
                os.startfile(app_name)
                return f"Opening {app_name}."
            except Exception as e:
                self.logger.error(f"Error launching application {app_name}: {str(e)}")
                return f"Sorry, I couldn't open {app_name}."
                
        except Exception as e:
            self.logger.error(f"Error in launch_application: {str(e)}")
            return f"Sorry, I couldn't process that command: {str(e)}"

    def open_application(self, command):
        """Open applications or folders based on command"""
        try:
            command = command.lower()
            # Check if it's a folder path
            for key, path in self.app_map.items():
                if key in command and os.path.isdir(path):
                    os.startfile(path)
                    return f"Opening {key} folder."
                    
            # Check if it's an application
            for key, app in self.app_map.items():
                if key in command:
                    try:
                        os.startfile(app)
                        return f"Opening {key}."
                    except Exception as e:
                        self.logger.error(f"Error opening {key}: {str(e)}")
                        return f"Sorry, I couldn't open {key}."
                        
            return "I'm not sure what you want me to open."
            
        except Exception as e:
            self.logger.error(f"Error in open_application: {str(e)}")
            return f"Sorry, I couldn't process that command: {str(e)}"
