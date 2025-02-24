# assistant/database.py
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
import logging

class DatabaseHandler:
    def __init__(self, db_name="student_data.db"):
        self.db_name = db_name
        self._initialize_database()
        
    @contextmanager
    def _get_cursor(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Create tables if they don't exist"""
        with self._get_cursor() as c:
            # Academic Assignments
            c.execute('''CREATE TABLE IF NOT EXISTS assignments
                        (id INTEGER PRIMARY KEY,
                        subject TEXT NOT NULL,
                        task TEXT NOT NULL,
                        due_date TEXT NOT NULL,
                        priority INTEGER DEFAULT 1,
                        completed BOOLEAN DEFAULT FALSE)''')
            
            # Study Sessions (Pomodoro)
            c.execute('''CREATE TABLE IF NOT EXISTS study_sessions
                        (id INTEGER PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration INTEGER,
                        type TEXT CHECK(type IN ('work', 'break')))''')
            
            # Flashcards with Spaced Repetition
            c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                        (id INTEGER PRIMARY KEY,
                        front TEXT NOT NULL,
                        back TEXT NOT NULL,
                        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        next_review TEXT NOT NULL,
                        interval INTEGER DEFAULT 1,
                        ease_factor REAL DEFAULT 2.5)''')
            
            # Class Schedule
            c.execute('''CREATE TABLE IF NOT EXISTS schedule
                        (id INTEGER PRIMARY KEY,
                        day TEXT CHECK(day IN ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')),
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        room TEXT)''')

    # ----------------- Assignment Methods -----------------
    def add_assignment(self, subject, task, due_date, priority=1):
        with self._get_cursor() as c:
            c.execute('''INSERT INTO assignments 
                        (subject, task, due_date, priority)
                        VALUES (?, ?, ?, ?)''',
                     (subject, task, due_date, priority))
            return c.lastrowid

    def get_due_assignments(self, days_ahead=7):
        with self._get_cursor() as c:
            end_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()
            c.execute('''SELECT * FROM assignments 
                       WHERE due_date <= ? AND completed = FALSE
                       ORDER BY due_date, priority DESC''',
                    (end_date,))
            return c.fetchall()

    # ----------------- Study Session Methods -----------------
    def start_study_session(self, session_type='work'):
        with self._get_cursor() as c:
            start_time = datetime.now().isoformat()
            c.execute('''INSERT INTO study_sessions
                        (start_time, type) VALUES (?, ?)''',
                     (start_time, session_type))
            return c.lastrowid

    def end_study_session(self, session_id, duration):
        with self._get_cursor() as c:
            end_time = datetime.now().isoformat()
            c.execute('''UPDATE study_sessions 
                       SET end_time = ?, duration = ?
                       WHERE id = ?''',
                    (end_time, duration, session_id))

    # ----------------- Flashcard Methods -----------------
    def add_flashcard(self, front, back):
        with self._get_cursor() as c:
            next_review = datetime.now().isoformat()
            c.execute('''INSERT INTO flashcards
                        (front, back, next_review)
                        VALUES (?, ?, ?)''',
                     (front, back, next_review))
            return c.lastrowid

    def get_due_flashcards(self):
        with self._get_cursor() as c:
            c.execute('''SELECT * FROM flashcards 
                       WHERE next_review <= datetime('now')
                       ORDER BY next_review''')
            return c.fetchall()

    def update_flashcard_progress(self, card_id, quality):
        """Update flashcard using SuperMemo2 algorithm"""
        with self._get_cursor() as c:
            c.execute('''SELECT interval, ease_factor FROM flashcards
                       WHERE id = ?''', (card_id,))
            interval, ease_factor = c.fetchone()

            if quality >= 3:
                if interval == 0:
                    new_interval = 1
                elif interval == 1:
                    new_interval = 6
                else:
                    new_interval = interval * ease_factor
                new_ease = max(1.3, ease_factor + 0.1 - (5 - quality)*(0.08+(5-quality)*0.02))
            else:
                new_interval = 1
                new_ease = max(1.3, ease_factor - 0.2)

            next_review = (datetime.now() + timedelta(days=new_interval)).isoformat()
            c.execute('''UPDATE flashcards SET
                       interval = ?, ease_factor = ?, next_review = ?
                       WHERE id = ?''',
                    (new_interval, new_ease, next_review, card_id))

    # ----------------- Schedule Methods -----------------
    def add_class(self, day, start_time, end_time, subject, room):
        with self._get_cursor() as c:
            c.execute('''INSERT INTO schedule
                        (day, start_time, end_time, subject, room)
                        VALUES (?, ?, ?, ?, ?)''',
                     (day.lower()[:3], start_time, end_time, subject, room))

    def get_daily_schedule(self, day):
        with self._get_cursor() as c:
            c.execute('''SELECT * FROM schedule 
                       WHERE day = ?
                       ORDER BY start_time''',
                    (day.lower()[:3],))
            return c.fetchall()

# Example usage
if __name__ == "__main__":
    db = DatabaseHandler()
    
    # Test assignment
    db.add_assignment(
        subject="Math",
        task="Complete chapter 5 exercises",
        due_date="2023-12-15",
        priority=2
    )
    
    # Test flashcard
    card_id = db.add_flashcard("Photosynthesis", "Process by which plants convert light energy to chemical energy")
    db.update_flashcard_progress(card_id, quality=4)
    
    # Test class schedule
    db.add_class(
        day="Monday",
        start_time="09:00",
        end_time="10:30",
        subject="Physics",
        room="Lab B"
    )