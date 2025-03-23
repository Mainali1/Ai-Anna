import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import random
import time

class EnhancedContextManager:
    def __init__(self, conversation_storage):
        self.conversation_storage = conversation_storage
        self.current_context = {
            'session_start': datetime.now().isoformat(),
            'user_state': 'unknown',
            'conversation_topics': [],
            'active_tasks': [],
            'environment': self._detect_environment(),
            'time_awareness': self._get_time_awareness(),
            'interaction_count': 0,
            'mood_trajectory': [],
            'last_greeting_time': None
        }
        self.context_history = []
        self.max_context_history = 10
        
    def _detect_environment(self) -> str:
        """Detect the current environment (professional, home, school)"""
        # This is a placeholder. In a real implementation, this would use
        # system information, time of day, and other signals to guess the environment
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:
            return "professional"
        elif 8 <= current_hour <= 15:
            return "school"
        else:
            return "home"
    
    def _get_time_awareness(self) -> Dict[str, Any]:
        """Get time-related context information"""
        now = datetime.now()
        current_hour = now.hour
        
        # Determine time of day
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
            
        return {
            'timestamp': now.isoformat(),
            'time_of_day': time_of_day,
            'day_of_week': now.strftime('%A'),
            'is_weekend': now.weekday() >= 5
        }
    
    def update_context(self, user_input: str, assistant_response: str) -> None:
        """Update context based on the latest interaction"""
        # Update time awareness
        self.current_context['time_awareness'] = self._get_time_awareness()
        
        # Increment interaction count
        self.current_context['interaction_count'] += 1
        
        # Extract topics from user input (simplified implementation)
        potential_topics = [word for word in user_input.lower().split() 
                          if len(word) > 4 and word not in ['about', 'would', 'could', 'should']]
        
        if potential_topics:
            # Add new topics to the list without duplicates
            for topic in potential_topics:
                if topic not in self.current_context['conversation_topics']:
                    self.current_context['conversation_topics'].append(topic)
            
            # Keep only the 5 most recent topics
            self.current_context['conversation_topics'] = self.current_context['conversation_topics'][-5:]
        
        # Store context history
        self.context_history.append(self.current_context.copy())
        if len(self.context_history) > self.max_context_history:
            self.context_history.pop(0)
    
    def should_greet_user(self) -> bool:
        """Determine if the assistant should greet the user based on context"""
        # Check if this is the first interaction of a new session
        if self.current_context['interaction_count'] == 0:
            return True
            
        # Check if enough time has passed since the last greeting
        last_greeting = self.current_context['last_greeting_time']
        if last_greeting is None:
            return True
            
        last_greeting_time = datetime.fromisoformat(last_greeting)
        time_since_greeting = datetime.now() - last_greeting_time
        
        # Greet if it's been more than 2 hours
        if time_since_greeting.total_seconds() > 7200:  # 2 hours in seconds
            return True
            
        return False
    
    def generate_greeting(self) -> str:
        """Generate a contextually appropriate greeting"""
        time_awareness = self.current_context['time_awareness']
        time_of_day = time_awareness['time_of_day']
        
        greetings = {
            'morning': [
                "Good morning! Hope you're ready for a productive day.",
                "Morning! How can I help you start your day?",
                "Good morning! I'm here and ready to assist you."
            ],
            'afternoon': [
                "Good afternoon! How's your day going so far?",
                "Hello there! Need any assistance this afternoon?",
                "Good afternoon! I'm here if you need anything."
            ],
            'evening': [
                "Good evening! How was your day?",
                "Evening! What can I help you with tonight?",
                "Good evening! I'm here and ready to assist you."
            ],
            'night': [
                "Working late? How can I help you tonight?",
                "Good evening! Need any assistance at this hour?",
                "Hello there! I'm here to help, even at night."
            ]
        }
        
        # Update last greeting time
        self.current_context['last_greeting_time'] = datetime.now().isoformat()
        
        return random.choice(greetings.get(time_of_day, ["Hello! How can I help you today?"]))
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get the current context"""
        return self.current_context
    
    def get_context_summary(self) -> str:
        """Generate a human-readable summary of the current context"""
        context = self.current_context
        time_awareness = context['time_awareness']
        
        summary = f"It's {time_awareness['time_of_day']} on {time_awareness['day_of_week']}. "
        
        if context['conversation_topics']:
            summary += f"We've been discussing {', '.join(context['conversation_topics'])}. "
            
        if context['environment'] != 'unknown':
            summary += f"You seem to be in a {context['environment']} environment. "
            
        return summary