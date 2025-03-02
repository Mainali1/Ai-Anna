import time
import os
from pygame import mixer
from datetime import datetime, timedelta
import nltk

from weakref import WeakValueDictionary

class StudyManager:
    def __init__(self):
        # Use WeakValueDictionary for better memory management
        self.cache = WeakValueDictionary()
    def __init__(self, db_handler):
        self.db = db_handler
        self.timer_active = False
        self.current_card = 0
        mixer.init()
        
        # Ensure NLTK resources are available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def start_pomodoro(self, work_mins=25, break_mins=5):
        def timer(countdown):
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < countdown and self.timer_active:
                remaining = countdown - (datetime.now() - start_time).total_seconds()
                mins, secs = divmod(int(remaining), 60)
                yield f"{mins:02d}:{secs:02d}"
                time.sleep(1)

        try:
            self.timer_active = True
            
            # Work session
            work_session_id = self.db.start_study_session('work')
            for t in timer(work_mins * 60):
                print(f"Work Time Remaining: {t}", end='\r')
            self._play_bell()
            self.db.end_study_session(work_session_id)
            
            # Break session
            break_session_id = self.db.start_study_session('break')
            for t in timer(break_mins * 60):
                print(f"Break Time Remaining: {t}", end='\r')
            self._play_bell()
            self.db.end_study_session(break_session_id)
            
        finally:
            self.timer_active = False

    def _play_bell(self):
        """Handle bell sound with fallback"""
        try:
            if os.path.exists("bell.wav"):
                mixer.Sound("bell.wav").play()
            else:
                # Generate fallback beep
                freq = 1000  # Hz
                dur = 500  # ms
                if os.name == 'nt':
                    import winsound
                    winsound.Beep(freq, dur)
                else:
                    os.system(f'play -nq -t alsa synth {dur/1000} sine {freq}')
        except Exception as e:
            print(f"Couldn't play sound: {str(e)}")

    def create_flashcard(self, front, back):
        return self.db.add_flashcard(front.strip(), back.strip())

    def get_due_cards(self):
        return self.db.get_due_flashcards()

    def summarize_text(self, text, ratio=0.2):
        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text)
        return ' '.join(sentences[:int(len(sentences)*ratio)])