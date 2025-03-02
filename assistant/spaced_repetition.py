import datetime
import math
from typing import Dict, List, Optional

class SpacedRepetitionSystem:
    def __init__(self, db_handler):
        self.db = db_handler
        self.ease_factors = {}
        self.intervals = {}
        
    def calculate_next_review(self, card_id: str, quality: int) -> datetime.datetime:
        """Calculate the next review date based on SM-2 algorithm.
        
        Args:
            card_id: Unique identifier for the flashcard
            quality: Rating from 0-5 of how well the card was remembered
            
        Returns:
            datetime: Next review date
        """
        if card_id not in self.ease_factors:
            self.ease_factors[card_id] = 2.5
            self.intervals[card_id] = 1
            
        if quality >= 3:
            if self.intervals[card_id] == 1:
                self.intervals[card_id] = 6
            else:
                self.intervals[card_id] *= self.ease_factors[card_id]
                
            self.ease_factors[card_id] += 0.1
        else:
            self.intervals[card_id] = 1
            self.ease_factors[card_id] = max(1.3, self.ease_factors[card_id] - 0.2)
            
        next_date = datetime.datetime.now() + datetime.timedelta(days=self.intervals[card_id])
        return next_date
    
    def add_card(self, front: str, back: str, deck_name: str) -> str:
        """Add a new flashcard to the system.
        
        Args:
            front: Front side content of the card
            back: Back side content of the card
            deck_name: Name of the deck to add the card to
            
        Returns:
            str: Unique ID of the created card
        """
        card_data = {
            'front': front,
            'back': back,
            'deck': deck_name,
            'created_at': datetime.datetime.now(),
            'next_review': datetime.datetime.now()
        }
        return self.db.insert_card(card_data)
        
    def get_due_cards(self, deck_name: Optional[str] = None) -> List[Dict]:
        """Get all cards due for review.
        
        Args:
            deck_name: Optional deck name to filter by
            
        Returns:
            List of card dictionaries that are due for review
        """
        return self.db.get_due_cards(deck_name)
        
    def update_card_review(self, card_id: str, quality: int) -> None:
        """Update a card after review.
        
        Args:
            card_id: Unique identifier for the flashcard
            quality: Rating from 0-5 of how well the card was remembered
        """
        next_review = self.calculate_next_review(card_id, quality)
        self.db.update_card_review(card_id, next_review, quality)