import time
import sqlite3
from datetime import datetime
from pygame import mixer

class StudyManager:
    def __init__(self):
        self.timer_active = False
        self.flashcards = []
        self.current_card = 0
        mixer.init()
        
        # Initialize spaced repetition database
        self.conn = sqlite3.connect('study_data.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                         (id INTEGER PRIMARY KEY,
                         front TEXT,
                         back TEXT,
                         next_review DATE,
                         interval INTEGER)''')
        self.conn.commit()

    def start_pomodoro(self, work_mins=25, break_mins=5):
        def timer(countdown):
            while countdown > 0 and self.timer_active:
                mins, secs = divmod(countdown, 60)
                time_str = f"{mins:02d}:{secs:02d}"
                yield time_str
                time.sleep(1)
                countdown -= 1

        try:
            self.timer_active = True
            # Work period
            for t in timer(work_mins * 60):
                print(f"Work Time Remaining: {t}", end='\r')
            mixer.Sound('bell.wav').play()
            
            # Break period
            for t in timer(break_mins * 60):
                print(f"Break Time Remaining: {t}", end='\r')
            mixer.Sound('bell.wav').play()
            
        finally:
            self.timer_active = False

    def create_flashcard(self, front, back):
        self.c.execute('''INSERT INTO flashcards 
                        (front, back, next_review, interval)
                        VALUES (?, ?, DATE('now'), 1)''',
                        (front, back))
        self.conn.commit()

    def get_due_cards(self):
        self.c.execute('''SELECT front, back FROM flashcards
                        WHERE next_review <= DATE('now')''')
        return self.c.fetchall()

    def summarize_text(self, text, ratio=0.2):
        # Simple summarization using NLTK
        from nltk.tokenize import sent_tokenize
        from nltk.probability import FreqDist
        from nltk.corpus import stopwords
        
        words = [word.lower() for word in nltk.word_tokenize(text) 
                if word.isalnum()]
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word not in stop_words]
        
        freq_dist = FreqDist(words)
        ranking = {sent: sum(freq_dist[word] for word in sent_tokenize(sent.lower()))
                   for sent in sent_tokenize(text)}
        
        top_sents = sorted(ranking, key=ranking.get, reverse=True)[:int(len(ranking)*ratio)]
        return ' '.join(top_sents)