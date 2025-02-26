import os
import pvporcupine
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from threading import Thread, Event
import pyttsx3
import platform
import wave
import json
import time
from vosk import Model, KaldiRecognizer

class VoiceEngine:
    def __init__(self, gui, command_handler, config):
        self.gui = gui
        self.command_handler = command_handler
        self.config = config
        self.wake_word_detected = Event()
        self.listening_active = Event()
        self.is_processing = False
        
        # Initialize wake word detector
        self.porcupine = pvporcupine.create(
            access_key=os.getenv('PICOVOICE_ACCESS_KEY'),
            sensitivities=[self.config['wake_word_sensitivity']],
            keyword_paths=[self.get_wake_word_path()]
        )
        
        # Audio configuration
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length
        
        # Start wake word detection thread
        self.wake_word_thread = Thread(target=self.detect_wake_word, daemon=True)
        self.wake_word_thread.start()
        
        # Initialize Vosk model for offline recognition
        self.vosk_model = Model(lang="en-us") if self.config['offline_mode'] else None

    def get_wake_word_path(self):
        path = os.path.join(os.path.dirname(__file__), 'resources', 'wake_word.ppn')
        if not os.path.exists(path):
            raise FileNotFoundError("Wake word file missing. See README for setup instructions.")
        return path

    def detect_wake_word(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype=np.int16, 
                          blocksize=self.frame_length, callback=self.audio_callback):
            while True:
                time.sleep(0.1)  # Reduced CPU usage
                if self.wake_word_detected.is_set() and not self.is_processing:
                    self.handle_wake_word()
                    self.wake_word_detected.clear()

    def audio_callback(self, indata, frames, time, status):
        if status:
            self.gui.show_error(f"Audio error: {status}")
        if self.porcupine.process(indata.flatten()) >= 0:
            self.wake_word_detected.set()

    def handle_wake_word(self):
        self.is_processing = True
        try:
            if self.config['beep_sound']:
                self.play_notification_sound()
            if self.config['voice_response']:
                self.speak(self.config['wake_phrase'])
            self.listen_for_command()
        finally:
            self.is_processing = False

    def play_notification_sound(self):
        try:
            if platform.system() == 'Windows':
                import winsound
                winsound.Beep(1000, 200)
            else:
                sd.play(0.5 * np.sin(2 * np.pi * 940 * np.arange(44100) / 44100), samplerate=44100)
                sd.wait()
        except Exception as e:
            self.gui.show_error(f"Sound error: {str(e)}")

    def listen_for_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.gui.update_ui_state(True)
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=8, phrase_time_limit=15)
                command = self.recognize_audio(audio)
                if command:
                    if self.command_handler:  # Proper indentation added here
                        self.command_handler.process_command(command)  # And here
            except sr.WaitTimeoutError:
                self.gui.show_error("Listening timed out")
            except Exception as e:
                self.gui.show_error(f"Recognition error: {str(e)}")
            finally:
                self.gui.update_ui_state(False)

    def recognize_audio(self, audio):
        try:
            # Resample audio to 16kHz for Vosk compatibility
            wav_data = audio.get_wav_data(convert_rate=16000)
            return sr.Recognizer().recognize_google(audio)
        except sr.UnknownValueError:
            self.gui.show_error("Could not understand audio")
        except sr.RequestError:
            return self.offline_recognition(wav_data)
        return None

    def offline_recognition(self, wav_data):
        if not self.vosk_model:
            self.gui.show_error("Offline mode not enabled")
            return None
            
        try:
            recognizer = KaldiRecognizer(self.vosk_model, 16000)
            if recognizer.AcceptWaveform(wav_data):
                result = json.loads(recognizer.Result())
                return result.get('text', '')
            return None
        except Exception as e:
            self.gui.show_error(f"Offline recognition failed: {str(e)}")
            return None

    def speak(self, text):
        def _speak():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', self.config['speech_rate'])
                engine.setProperty('volume', self.config['speech_volume'])
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                self.gui.show_error(f"Speech error: {str(e)}")
        
        if self.config['voice_response']:
            Thread(target=_speak, daemon=True).start()

    def cleanup(self):
        if self.porcupine:
            self.porcupine.delete()
        sd.stop()