import pvporcupine  # Free for non-commercial use
from pynput import keyboard

class VoiceEngine:
    def __init__(self, gui, command_handler):
        self.porcupine = pvporcupine.create(
            access_key='FREE_KEY_FROM_PICOVOICE_CONSOLE',  # Get free key
            keyword_paths=['wake_word.ppn']
        )
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_key_press(self, key):
        # Use hotkey (e.g., Ctrl+Space) as free alternative
        if key == keyboard.Key.ctrl_l and keyboard.Key.space:
            self.start_listening()

    def start_listening(self):
        # Voice recognition logic here
        pass