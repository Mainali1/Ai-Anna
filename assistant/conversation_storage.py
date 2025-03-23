import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import random

class ConversationStorage:
    def __init__(self, base_dir: str = 'conversations'):
        self.base_dir = Path(os.path.dirname(__file__)).parent / base_dir
        self.base_dir.mkdir(exist_ok=True)
        self.current_conversation = []
        self.patterns_cache = {}

    def _get_conversation_path(self, date: datetime = None) -> Path:
        """Get the path for storing conversation based on date"""
        if date is None:
            date = datetime.now()
        return self.base_dir / f"{date.strftime('%Y-%m-%d')}.json"

    def add_interaction(self, user_input: str, assistant_response: str, context: Dict[str, Any] = None) -> None:
        """Add a new interaction to the current conversation"""
        timestamp = datetime.now().isoformat()
        interaction = {
            'timestamp': timestamp,
            'user_input': user_input,
            'assistant_response': assistant_response,
            'context': context or {}
        }
        self.current_conversation.append(interaction)
        self._save_conversation()

    def _save_conversation(self) -> None:
        """Save the current conversation to a date-based JSON file"""
        file_path = self._get_conversation_path()
        existing_data = []
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        existing_data.extend(self.current_conversation)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        self.current_conversation = []

    def store_interaction(self, user_input: str, assistant_response: str, context: Dict[str, Any] = None) -> None:
        """Alias for add_interaction to maintain backward compatibility"""
        self.add_interaction(user_input, assistant_response, context)

    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze conversation patterns from stored history"""
        patterns = {
            'common_queries': {},
            'time_patterns': {},
            'context_patterns': {},
            'response_effectiveness': {}
        }

        for file_path in self.base_dir.glob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                    self._process_conversations(conversations, patterns)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

        self.patterns_cache = patterns
        return patterns

    def _process_conversations(self, conversations: List[Dict], patterns: Dict) -> None:
        """Process conversations to extract patterns"""
        for interaction in conversations:
            query = interaction['user_input'].lower()
            timestamp = datetime.fromisoformat(interaction['timestamp'])
            context = interaction.get('context', {})

            # Analyze common queries
            patterns['common_queries'][query] = patterns['common_queries'].get(query, 0) + 1

            # Analyze time patterns
            hour = timestamp.hour
            time_slot = f"{hour:02d}:00-{hour:02d}:59"
            patterns['time_patterns'][time_slot] = patterns['time_patterns'].get(time_slot, 0) + 1

            # Analyze context patterns
            for key, value in context.items():
                if key not in patterns['context_patterns']:
                    patterns['context_patterns'][key] = {}
                patterns['context_patterns'][key][str(value)] = \
                    patterns['context_patterns'][key].get(str(value), 0) + 1

    def get_relevant_history(self, query: str, limit: int = 5) -> List[Dict]:
        """Get relevant historical interactions based on query"""
        relevant_interactions = []
        
        for file_path in sorted(self.base_dir.glob('*.json'), reverse=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversations = json.load(f)
                    for interaction in conversations:
                        if self._is_relevant(query, interaction['user_input']):
                            relevant_interactions.append(interaction)
                            if len(relevant_interactions) >= limit:
                                return relevant_interactions
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
        
        return relevant_interactions

    def _is_relevant(self, query: str, stored_query: str) -> bool:
        """Check if a stored query is relevant to the current query"""
        query_words = set(query.lower().split())
        stored_words = set(stored_query.lower().split())
        return len(query_words.intersection(stored_words)) > 0

    def get_user_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from conversation history"""
        if not self.patterns_cache:
            self.analyze_patterns()

        preferences = {
            'active_hours': self._get_active_hours(),
            'common_topics': self._get_common_topics(),
            'interaction_style': self._analyze_interaction_style()
        }

        return preferences

    def _get_active_hours(self) -> List[int]:
        """Get user's most active hours based on conversation timestamps"""
        if 'time_patterns' not in self.patterns_cache:
            return []

        time_patterns = self.patterns_cache['time_patterns']
        sorted_hours = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)
        return [int(hour.split(':')[0]) for hour, _ in sorted_hours[:3]]

    def _get_common_topics(self) -> List[str]:
        """Get user's most common conversation topics"""
        if 'common_queries' not in self.patterns_cache:
            return []

        queries = self.patterns_cache['common_queries']
        return [query for query, count in 
                sorted(queries.items(), key=lambda x: x[1], reverse=True)[:5]]

    def _analyze_interaction_style(self) -> str:
        """Analyze user's interaction style based on conversation patterns"""
        if not self.patterns_cache:
            return 'neutral'

        # Analyze based on context patterns
        context_patterns = self.patterns_cache.get('context_patterns', {})
        mood_patterns = context_patterns.get('mood', {})
        formality_patterns = context_patterns.get('formality', {})
        engagement_patterns = context_patterns.get('engagement', {})
        
        # Calculate dominant mood
        dominant_mood = 'neutral'
        if mood_patterns:
            dominant_mood = max(mood_patterns.items(), key=lambda x: x[1])[0]
        
        # Calculate formality level
        formality_level = 'neutral'
        if formality_patterns:
            formality_level = max(formality_patterns.items(), key=lambda x: x[1])[0]
        
        # Calculate engagement style
        engagement_style = 'balanced'
        if engagement_patterns:
            engagement_style = max(engagement_patterns.items(), key=lambda x: x[1])[0]
        
        return {
            'mood': dominant_mood,
            'formality': formality_level,
            'engagement': engagement_style
        }

    def get_response_variation(self, base_response: str, context: Dict[str, Any] = None) -> str:
        """Generate dynamic variations of responses based on user interaction style and context"""
        interaction_style = self._analyze_interaction_style()
        
        # Apply mood-based modifications
        if interaction_style['mood'] in ['positive', 'excited']:
            base_response = self._add_enthusiasm(base_response)
        elif interaction_style['mood'] in ['professional', 'formal']:
            base_response = self._add_professionalism(base_response)
        
        # Apply formality adjustments
        if interaction_style['formality'] == 'casual':
            base_response = self._make_casual(base_response)
        elif interaction_style['formality'] == 'formal':
            base_response = self._make_formal(base_response)
        
        # Add contextual elements
        if context:
            base_response = self._add_context_awareness(base_response, context)
        
        return base_response
    
    def _add_enthusiasm(self, response: str) -> str:
        """Add enthusiastic elements to the response"""
        import random
        enthusiasm_markers = [
            '!', ' :)', ' 😊', ' Great!',
            'Awesome', 'Fantastic', 'Excellent'
        ]
        
        if random.random() < 0.7:  # 70% chance to add enthusiasm
            if not any(marker in response for marker in enthusiasm_markers):
                response = response.rstrip('.!?') + random.choice(enthusiasm_markers)
        
        return response
    
    def _add_professionalism(self, response: str) -> str:
        """Add professional elements to the response"""
        import random
        professional_phrases = [
            'I recommend', 'Based on the analysis',
            'From my assessment', 'In my professional opinion'
        ]
        
        if response.lower().startswith(('yes', 'no', 'okay', 'sure')):
            response = random.choice(professional_phrases) + ', ' + response.lower()
        
        return response
    
    def _make_casual(self, response: str) -> str:
        """Make the response more casual and friendly"""
        import random
        casual_replacements = {
            'would like to': 'want to',
            'however': 'but',
            'additionally': 'also',
            'assist': 'help',
            'utilize': 'use'
        }
        
        for formal, casual in casual_replacements.items():
            if random.random() < 0.8:  # 80% chance to replace
                response = response.replace(formal, casual)
        
        return response
    
    def _make_formal(self, response: str) -> str:
        """Make the response more formal and professional"""
        import random
        formal_replacements = {
            'want to': 'would like to',
            'but': 'however',
            'also': 'additionally',
            'help': 'assist',
            'use': 'utilize'
        }
        
        for casual, formal in formal_replacements.items():
            if random.random() < 0.8:  # 80% chance to replace
                response = response.replace(casual, formal)
        
        return response
    
    def _add_context_awareness(self, response: str, context: Dict[str, Any]) -> str:
        """Add contextual elements to the response"""
        import random
        
        # Time-based context
        if 'time_of_day' in context:
            time_greetings = {
                'morning': ['Good morning!', 'Hope your morning is going well!'],
                'afternoon': ['Good afternoon!', 'Hope you\'re having a good afternoon!'],
                'evening': ['Good evening!', 'Hope you\'re having a nice evening!']
            }
            if random.random() < 0.3:  # 30% chance to add time greeting
                greeting = random.choice(time_greetings.get(context['time_of_day'], []))
                response = f"{greeting} {response}"
        
        # Previous interaction context
        if 'previous_topic' in context:
            topic_transitions = [
                f"Following up on {context['previous_topic']}, ",
                f"Regarding our previous discussion about {context['previous_topic']}, ",
                f"Coming back to {context['previous_topic']}, "
            ]
            if random.random() < 0.4:  # 40% chance to add topic transition
                response = random.choice(topic_transitions) + response
        
        return response