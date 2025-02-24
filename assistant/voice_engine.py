import os
import pvporcupine
from pynput import keyboard
from dotenv import load_dotenv

class VoiceEngine:
    def __init__(self, gui, command_handler):
        # Load environment variables from .env file
        load_dotenv()  # Load from project root
        
        # Get path to wake word file
        wake_word_path = os.path.join(
            os.path.dirname(__file__),  # Path to assistant folder
            'resources',
            'wake_word.ppn'
        )
        
        # Verify file exists
        if not os.path.exists(wake_word_path):
            raise FileNotFoundError(f"Wake word file not found at: {wake_word_path}")

        # Create Porcupine instance
        self.porcupine = pvporcupine.create(
            access_key=os.getenv('PICOVOICE_ACCESS_KEY'),
            keyword_paths=[wake_word_path]
        )
        
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def start_listening(self):
        # Voice recognition logic here
        pass