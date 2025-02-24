import os
import pvporcupine
import sounddevice as sd
import numpy as np
import winsound
from pynput import keyboard
from dotenv import load_dotenv
import speech_recognition as sr
from threading import Thread, Event

class VoiceEngine:
    def __init__(self, gui, command_handler):
        load_dotenv()
        self.command_handler = command_handler
        self.wake_word_detected = Event()
        self.listening_active = Event()
        
        # Initialize wake word detector
        self.porcupine = pvporcupine.create(
            access_key=os.getenv('PICOVOICE_ACCESS_KEY'),
            sensitivities=[0.5],
            keyword_paths=[self._get_wake_word_path()]
        )
        
        # Audio configuration
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        
        # Start continuous wake word detection
        self.wake_word_thread = Thread(target=self._detect_wake_word)
        self.wake_word_thread.daemon = True
        self.wake_word_thread.start()

    def _get_wake_word_path(self):
        path = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'wake_word.ppn'
        )
        if not os.path.exists(path):
            raise FileNotFoundError(f"Wake word file missing: {path}")
        return path

    def _detect_wake_word(self):
        """Continuously listen for wake word in background"""
        with sd.InputStream(samplerate=self.sample_rate,
                           channels=1,
                           dtype=np.int16,
                           blocksize=self.frame_length,
                           callback=self._audio_callback):
            while True:
                if self.wake_word_detected.is_set():
                    self._handle_wake_word_detected()
                    self.wake_word_detected.clear()

    def _audio_callback(self, indata, frames, time, status):
        """Process audio frames for wake word detection"""
        if status:
            print(status)
        result = self.porcupine.process(indata.flatten())
        if result >= 0:
            self.wake_word_detected.set()

    def _handle_wake_word_detected(self):
        winsound.Beep(1000, 200)
        """Handle successful wake word detection"""
        print("\nWake word detected! Listening for command...")
        self._listen_for_command()

    def _listen_for_command(self):
        """Listen and process voice command after wake word"""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=5)
                command = r.recognize_google(audio)
                print(f"Command received: {command}")
                self.command_handler.process_command(command)
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
            except Exception as e:
                print(f"Error: {str(e)}")

    def start_listening(self):
        """Manual listening trigger (for Ctrl+Space fallback)"""
        if not self.listening_active.is_set():
            self._listen_for_command()