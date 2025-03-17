# assistant/database.py
import sqlite3
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
import logging
import re

class DatabaseHandler:
    def __init__(self, db_name="student_data.db"):
        self.db_name = db_name
        self._initialize_database()
        
    @contextmanager
    def _get_cursor(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
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

    def execute(self, query, params=None):
        """Execute a SQL query with optional parameters"""
        with self._get_cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            except Exception as e:
                logging.error(f"Query execution error: {str(e)}")
                raise

    def _initialize_database(self):
        """Create tables and indexes if they don't exist"""
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
                        session_type TEXT CHECK(session_type IN ('work', 'break')))''')
            
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
            
            # Create indexes
            c.execute('''CREATE INDEX IF NOT EXISTS idx_assignments_due ON assignments(due_date)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_flashcards_review ON flashcards(next_review)''')

    # ----------------- Assignment Methods -----------------
    def add_assignment(self, subject, task, due_date, priority=1):
        if not self._validate_date(due_date):
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
            
        with self._get_cursor() as c:
            c.execute('''INSERT INTO assignments 
                        (subject, task, due_date, priority)
                        VALUES (?, ?, ?, ?)''',
                     (subject.strip(), task.strip(), due_date, priority))
            return c.lastrowid

    def get_due_assignments(self, days_ahead=7):
        with self._get_cursor() as c:
            end_date = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()
            c.execute('''SELECT * FROM assignments 
                       WHERE due_date <= ? AND completed = FALSE
                       ORDER BY due_date, priority DESC''',
                    (end_date,))
            return c.fetchall()

    # ----------------- Study Session Methods -----------------
    def start_study_session(self, session_type='work'):
        if session_type not in ('work', 'break'):
            raise ValueError("Invalid session type")
            
        with self._get_cursor() as c:
            start_time = datetime.now(timezone.utc).isoformat()
            c.execute('''INSERT INTO study_sessions
                        (start_time, session_type) VALUES (?, ?)''',
                     (start_time, session_type))
            return c.lastrowid

    def end_study_session(self, session_id):
        with self._get_cursor() as c:
            end_time = datetime.now(timezone.utc).isoformat()
            c.execute('''SELECT start_time FROM study_sessions WHERE id = ?''', (session_id,))
            result = c.fetchone()
            if not result:
                raise ValueError("Session not found")
                
            start_time = datetime.fromisoformat(result[0])
            duration = int((datetime.now(timezone.utc) - start_time).total_seconds())
            
            c.execute('''UPDATE study_sessions 
                       SET end_time = ?, duration = ?
                       WHERE id = ?''',
                    (end_time, duration, session_id))

    # ----------------- Flashcard Methods -----------------
    def add_flashcard(self, front, back):
        with self._get_cursor() as c:
            next_review = datetime.now(timezone.utc).isoformat()
            c.execute('''INSERT INTO flashcards
                        (front, back, next_review)
                        VALUES (?, ?, ?)''',
                     (front.strip(), back.strip(), next_review))
            return c.lastrowid

    def get_due_flashcards(self):
        with self._get_cursor() as c:
            now_utc = datetime.now(timezone.utc).isoformat()
            c.execute('''SELECT * FROM flashcards 
                       WHERE next_review <= ?
                       ORDER BY next_review''',
                    (now_utc,))
            return c.fetchall()

    def update_flashcard_progress(self, card_id, quality):
        """Update flashcard using SuperMemo2 algorithm"""
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
            
        with self._get_cursor() as c:
            c.execute('''SELECT interval, ease_factor FROM flashcards
                       WHERE id = ?''', (card_id,))
            result = c.fetchone()
            if not result:
                raise ValueError("Flashcard not found")
                
            interval, ease_factor = result

            if quality >= 3:
                new_interval = interval * ease_factor if interval > 1 else 6
                new_ease = max(1.3, ease_factor + 0.1 - (5 - quality)*(0.08+(5-quality)*0.02))
            else:
                new_interval = 1
                new_ease = max(1.3, ease_factor - 0.2)

            next_review = (datetime.now(timezone.utc) + timedelta(days=new_interval)).isoformat()
            c.execute('''UPDATE flashcards SET
                       interval = ?, ease_factor = ?, next_review = ?
                       WHERE id = ?''',
                    (new_interval, new_ease, next_review, card_id))

    # ----------------- Schedule Methods -----------------
    def add_class(self, day, start_time, end_time, subject, room):
        if not re.match(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", start_time):
            raise ValueError("Invalid start time format (HH:MM)")
            
        with self._get_cursor() as c:
            c.execute('''INSERT INTO schedule
                        (day, start_time, end_time, subject, room)
                        VALUES (?, ?, ?, ?, ?)''',
                     (day.lower()[:3], start_time, end_time, subject.strip(), room.strip()))

    def get_daily_schedule(self, day):
        with self._get_cursor() as c:
            c.execute('''SELECT * FROM schedule 
                       WHERE day = ?
                       ORDER BY start_time''',
                    (day.lower()[:3],))
            return c.fetchall()

    def _validate_date(self, date_str):
        try:
            datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    # ----------------- Deletion Methods -----------------
    def delete_flashcard(self, card_id):
        with self._get_cursor() as c:
            c.execute('DELETE FROM flashcards WHERE id = ?', (card_id,))
            return c.rowcount > 0

    def delete_schedule(self, schedule_id):
        with self._get_cursor() as c:
            c.execute('DELETE FROM schedule WHERE id = ?', (schedule_id,))
            return c.rowcount > 0

    def delete_assignment(self, assignment_id):
        with self._get_cursor() as c:
            c.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
            return c.rowcount > 0

    def setup_tables(self):
        """Setup all required database tables"""
        tables = [
            """CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                deck TEXT DEFAULT 'Default',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS flashcard_reviews (
                id INTEGER PRIMARY KEY,
                card_id INTEGER,
                review_date DATETIME,
                ease_factor REAL,
                interval INTEGER,
                quality INTEGER,
                FOREIGN KEY (card_id) REFERENCES flashcards(id)
            )""",
            """CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY,
                start_time DATETIME,
                end_time DATETIME,
                subject TEXT,
                notes TEXT
            )"""
        ]
        
        for table in tables:
            self.execute(table)