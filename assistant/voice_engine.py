import os
import pvporcupine
import sounddevice as sd
import numpy as np
import speech_recognition as sr
from threading import Thread, Event
import pyttsx3
import platform
import json
import time
from vosk import Model, KaldiRecognizer
import requests
from gtts import gTTS
from io import BytesIO
import pygame
from .ai_service_handler import AIServiceHandler

class VoiceEngine:
    def __init__(self, gui, command_handler, config):
        if not gui or not config:
            raise ValueError("GUI and config must be provided")
            
        self.gui = gui
        self.command_handler = command_handler
        self.config = config
        self.wake_word_detected = Event()
        self.listening_active = Event()
        self.is_processing = False
        self.joke_api_url = "https://v2.jokeapi.dev/joke/Programming,Miscellaneous?safe-mode"
        self.tts_engine = None
        self.pygame_initialized = False
        self.ai_mode = False
        self.ai_service = None
        
        try:
            # Initialize components in order
            self.init_ai_service()
            self.init_wake_word_detector()
            self.init_audio_config()
            self.init_vosk_model()
            self.init_tts_engine()
            self.start_wake_word_thread()
        except Exception as e:
            self.gui.show_error(f"Initialization error: {str(e)}")
            raise

    def init_ai_service(self):
        try:
            self.ai_service = AIServiceHandler(self.config)
        except Exception as e:
            self.gui.show_error(f"AI service initialization error: {str(e)}")
            raise

    def init_wake_word_detector(self):
        try:
            access_key = os.getenv('PICOVOICE_ACCESS_KEY')
            if not access_key:
                raise ValueError("PICOVOICE_ACCESS_KEY not found in environment variables")
                
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                sensitivities=[self.config.get('wake_word_sensitivity', 0.5)],
                keyword_paths=[self.get_wake_word_path()]
            )
        except Exception as e:
            self.gui.show_error(f"Wake word detector initialization error: {str(e)}")
            raise

    def init_audio_config(self):
        if not hasattr(self, 'porcupine'):
            raise RuntimeError("Wake word detector must be initialized before audio config")
        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length

    def init_vosk_model(self):
        try:
            self.vosk_model = Model(lang="en-us") if self.config.get('offline_mode', False) else None
        except Exception as e:
            self.gui.show_error(f"Vosk model initialization error: {str(e)}")
            # Don't raise here as Vosk is optional

    def start_wake_word_thread(self):
        self.wake_word_thread = Thread(target=self.detect_wake_word, daemon=True)
        self.wake_word_thread.start()

    def init_tts_engine(self):
        try:
            # Try pyttsx3 first
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            female_voice = None
            for voice in voices:
                if 'female' in voice.name.lower():
                    female_voice = voice
                    break
            
            if female_voice:
                self.engine.setProperty('voice', female_voice.id)
                self.engine.setProperty('rate', self.config['speech_rate'])
                self.engine.setProperty('volume', self.config['speech_volume'])
                self.tts_engine = 'pyttsx3'
            else:
                # If no female voice found, use gTTS
                self.tts_engine = 'gtts'
                if not self.pygame_initialized:
                    pygame.mixer.init()
                    self.pygame_initialized = True
        except Exception as e:
            # Fallback to gTTS if pyttsx3 fails
            self.tts_engine = 'gtts'
            if not self.pygame_initialized:
                pygame.mixer.init()
                self.pygame_initialized = True
            self.gui.show_error(f"Primary TTS initialization error: {str(e)}. Falling back to gTTS.")

    def get_random_joke(self):
        try:
            response = requests.get(self.joke_api_url)
            if response.status_code == 200:
                joke_data = response.json()
                if joke_data['type'] == 'single':
                    return joke_data['joke']
                else:
                    return f"{joke_data['setup']}\n{joke_data['delivery']}"
        except Exception:
            return "Why did the AI assistant go to therapy? It had too many processing issues!"

    def speak(self, text):
        def _speak(txt):
            try:
                # Add personality to responses
                if 'joke' in txt.lower():
                    txt = self.get_random_joke()
                elif any(greeting in txt.lower() for greeting in ['hello', 'hi', 'hey']):
                    txt = f"{txt} I'm your AI assistant, how can I help you today?"
                
                if self.tts_engine == 'pyttsx3':
                    if not hasattr(self, 'engine'):
                        self.init_tts_engine()
                    self.engine.say(txt)
                    self.engine.runAndWait()
                    self.engine.stop()
                else:  # Use gTTS
                    tts = gTTS(text=txt, lang='en', slow=False)
                    fp = BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    if not self.pygame_initialized:
                        pygame.mixer.init()
                        self.pygame_initialized = True
                    pygame.mixer.music.load(fp)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
            except Exception as e:
                self.gui.show_error(f"Speech error: {str(e)}")
                # Reinitialize TTS engine on error
                self.init_tts_engine()

        if self.config['voice_response']:
            Thread(target=_speak, args=(text,), daemon=True).start()

    def get_wake_word_path(self):
        path = os.path.join(os.path.dirname(__file__), 'resources', 'wake_word.ppn')
        if not os.path.exists(path):
            raise FileNotFoundError("Wake word file missing. See README for setup instructions.")
        return path

    def detect_wake_word(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype=np.int16, 
                          blocksize=self.frame_length, callback=self.audio_callback):
            while True:
                time.sleep(0.1)
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
                if command and self.command_handler:
                    self.command_handler.process_command(command)
            except sr.WaitTimeoutError:
                self.gui.show_error("Listening timed out")
            except Exception as e:
                self.gui.show_error(f"Recognition error: {str(e)}")
            finally:
                self.gui.update_ui_state(False)

    def recognize_audio(self, audio):
        try:
            wav_data = audio.get_wav_data(convert_rate=16000)
            command = sr.Recognizer().recognize_google(audio)
            
            # Check for AI mode commands
            if command:
                command = command.lower()
                if 'ai mode on' in command:
                    self.ai_mode = True
                    self.speak("AI mode activated")
                    return None
                elif 'ai mode off' in command:
                    self.ai_mode = False
                    self.speak("AI mode deactivated")
                    return None
                elif self.ai_mode:
                    response = self.ai_service.generate_response(command)
                    self.speak(response)
                    return None
            
            return command
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

    def cleanup(self):
        if self.porcupine:
            self.porcupine.delete()
        if self.pygame_initialized:
            pygame.mixer.quit()
        if hasattr(self, 'llm_handler'):
            self.llm_handler.cleanup()
        sd.stop()