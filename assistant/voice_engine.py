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
        
        # Initialize listener with CORRECT METHOD REFERENCE
        self.listener = keyboard.Listener(on_press=self.on_key_press)  # ✅ Correct reference
        self.listener.start()

    # 🚨 Ensure this method is properly defined INSIDE the class
    def on_key_press(self, key):
        # Check for Ctrl + Space hotkey
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.space:
            if keyboard.Key.ctrl_l in self.listener.modifiers and key == keyboard.Key.space:
                self.start_listening()

    def start_listening(self):
        # Add voice recognition logic here
        print("Listening...")