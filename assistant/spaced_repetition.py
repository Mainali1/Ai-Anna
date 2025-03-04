import math
from datetime import datetime, timedelta

class SpacedRepetitionSystem:
    def __init__(self, db_handler):
        self.db = db_handler
        self.setup_database()

    def setup_database(self):
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS flashcard_reviews (
            id INTEGER PRIMARY KEY,
            card_id INTEGER,
            review_date DATETIME,
            ease_factor REAL,
            interval INTEGER,
            quality INTEGER
        )
        """)
        
    def schedule_review(self, card_id, quality):
        """Schedule next review based on SM-2 algorithm
        quality: 0 (complete blackout) to 5 (perfect recall)"""
        review = self.get_last_review(card_id)
        
        if not review:
            ease_factor = 2.5
            interval = 1
        else:
            ease_factor = review['ease_factor']
            interval = review['interval']
            
            # Update ease factor
            ease_factor = max(1.3, ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            # Calculate next interval
            if quality < 3:
                interval = 1
            elif not review['interval']:
                interval = 1
            elif review['interval'] == 1:
                interval = 6
            else:
                interval = math.ceil(interval * ease_factor)

        next_review = datetime.now() + timedelta(days=interval)
        
        self.db.execute(
            "INSERT INTO flashcard_reviews (card_id, review_date, ease_factor, interval, quality) VALUES (?, ?, ?, ?, ?)",
            (card_id, datetime.now(), ease_factor, interval, quality)
        )
        
        return next_review
    
    def get_last_review(self, card_id):
        row = self.db.execute(
            "SELECT * FROM flashcard_reviews WHERE card_id = ? ORDER BY review_date DESC LIMIT 1",
            (card_id,)
        ).fetchone()
        
        if not row:
            return None
            
        return {
            'id': row[0],
            'card_id': row[1],
            'review_date': row[2],
            'ease_factor': row[3],
            'interval': row[4],
            'quality': row[5]
        }

    def get_card_stats(self, card_id):
        rows = self.db.execute(
            """SELECT 
                COUNT(*) as total_reviews,
                AVG(quality) as avg_quality,
                AVG(ease_factor) as avg_ease,
                MAX(interval) as max_interval
               FROM flashcard_reviews 
               WHERE card_id = ?""",
            (card_id,)
        ).fetchone()
        
        return {
            'total_reviews': rows[0],
            'average_quality': round(rows[1], 2) if rows[1] else 0,
            'average_ease': round(rows[2], 2) if rows[2] else 2.5,
            'max_interval': rows[3] if rows[3] else 0
        }

    def get_due_cards(self):
        return self.db.execute(
            """SELECT DISTINCT f.id, f.front, f.back
               FROM flashcards f
               LEFT JOIN flashcard_reviews r ON f.id = r.card_id
               WHERE r.id IS NULL
               OR r.id IN (
                   SELECT id FROM flashcard_reviews r2
                   WHERE r2.card_id = f.id
                   ORDER BY r2.review_date DESC
                   LIMIT 1
               )
               AND (r.review_date + r.interval * 86400) <= ?""",
            (datetime.now(),)
        ).fetchall()