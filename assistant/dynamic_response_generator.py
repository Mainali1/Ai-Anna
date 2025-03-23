import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class DynamicResponseGenerator:
    def __init__(self, conversation_storage=None, enhanced_context=None):
        self.conversation_storage = conversation_storage
        self.enhanced_context = enhanced_context
        self.filler_phrases = [
            "Let me think about that",
            "Hmm",
            "Let's see",
            "Well",
            "So",
            "Actually",
            "You know"
        ]
        self.acknowledgment_phrases = [
            "I understand",
            "Got it",
            "I see what you mean",
            "That makes sense",
            "I hear you"
        ]
        self.thinking_phrases = [
            "Let me process that",
            "Thinking...",
            "Analyzing that request",
            "Working on it",
            "Computing..."
        ]
        self.personality_traits = {
            'professional': {
                'formality': 0.8,
                'verbosity': 0.5,
                'enthusiasm': 0.3,
                'fillers': 0.1
            },
            'casual': {
                'formality': 0.3,
                'verbosity': 0.7,
                'enthusiasm': 0.7,
                'fillers': 0.4
            },
            'friendly': {
                'formality': 0.4,
                'verbosity': 0.6,
                'enthusiasm': 0.8,
                'fillers': 0.3
            },
            'technical': {
                'formality': 0.7,
                'verbosity': 0.8,
                'enthusiasm': 0.2,
                'fillers': 0.1
            }
        }
        self.current_personality = 'friendly'  # Default personality
        
    def set_personality(self, personality_type: str) -> None:
        """Set the current personality type for response generation"""
        if personality_type in self.personality_traits:
            self.current_personality = personality_type
    
    def adapt_personality_to_context(self) -> None:
        """Adapt personality based on context if available"""
        if not self.enhanced_context:
            return
            
        context = self.enhanced_context.get_current_context()
        environment = context.get('environment', 'home')
        
        # Map environment to personality
        personality_map = {
            'professional': 'professional',
            'school': 'friendly',
            'home': 'casual'
        }
        
        self.current_personality = personality_map.get(environment, 'friendly')
    
    def humanize_response(self, response: str) -> str:
        """Make AI responses sound more natural and human-like"""
        # Adapt personality based on context
        self.adapt_personality_to_context()
        
        # Get personality traits
        traits = self.personality_traits[self.current_personality]
        
        # Add filler phrases occasionally based on personality
        if random.random() < traits['fillers']:
            filler = random.choice(self.filler_phrases)
            response = f"{filler}, {response}"
        
        # Adjust formality
        if traits['formality'] < 0.5:
            # Make less formal
            response = self._reduce_formality(response)
        
        # Adjust verbosity
        if traits['verbosity'] > 0.7 and len(response.split()) < 15:
            # Make more verbose for high verbosity
            response = self._increase_verbosity(response)
        elif traits['verbosity'] < 0.3 and len(response.split()) > 20:
            # Make more concise for low verbosity
            response = self._decrease_verbosity(response)
        
        # Add enthusiasm based on personality
        if traits['enthusiasm'] > 0.6:
            response = self._add_enthusiasm(response)
        
        # Add natural variations and contractions
        response = self._add_contractions(response)
        
        # Add pauses with commas and ellipses for more natural speech rhythm
        response = self._add_speech_rhythm(response)
        
        return response
    
    def _reduce_formality(self, text: str) -> str:
        """Reduce the formality of text"""
        # Replace formal phrases with casual ones
        replacements = {
            'I apologize': "I'm sorry",
            'assistance': 'help',
            'utilize': 'use',
            'require': 'need',
            'additional': 'more',
            'inquire': 'ask',
            'commence': 'start',
            'terminate': 'end',
            'subsequently': 'then',
            'nevertheless': 'still',
            'regarding': 'about'
        }
        
        for formal, casual in replacements.items():
            text = re.sub(r'\b' + formal + r'\b', casual, text, flags=re.IGNORECASE)
        
        return text
    
    def _increase_verbosity(self, text: str) -> str:
        """Make text more verbose"""
        # Add elaborative phrases
        elaborations = [
            " which should help you with what you're trying to do",
            " as you might expect",
            " which is generally considered a good approach",
            " based on what you've told me",
            " which I think will work well for your situation"
        ]
        
        # 50% chance to add an elaboration
        if random.random() < 0.5 and "." in text:
            # Find a sentence to elaborate on
            sentences = text.split(".")
            if len(sentences) > 1:
                idx = random.randint(0, len(sentences) - 2)
                if len(sentences[idx]) > 10:  # Only elaborate on substantial sentences
                    sentences[idx] += random.choice(elaborations)
                text = ".".join(sentences)
        
        return text
    
    def _decrease_verbosity(self, text: str) -> str:
        """Make text more concise"""
        # Remove common filler phrases
        fillers_to_remove = [
            "as you may know", 
            "it is worth noting that",
            "it should be mentioned that",
            "needless to say",
            "for what it's worth",
            "as a matter of fact"
        ]
        
        for filler in fillers_to_remove:
            text = re.sub(filler, "", text, flags=re.IGNORECASE)
        
        # Simplify overly complex sentences (basic implementation)
        text = re.sub(r"\, (which|that|where|when) ", ". ", text)
        
        return text
    
    def _add_enthusiasm(self, text: str) -> str:
        """Add enthusiasm to text"""
        # Add enthusiastic phrases at the end of sentences
        enthusiasm_markers = [
            "!",
            "! ",
            "! That's great",
            "! Awesome",
            "! Perfect"
        ]
        
        # Replace some periods with exclamation marks (30% chance per sentence)
        sentences = text.split(".")
        for i in range(len(sentences) - 1):  # Skip the last element which might be empty
            if sentences[i] and random.random() < 0.3:
                sentences[i] += random.choice(enthusiasm_markers)
            else:
                sentences[i] += "."
        
        # Rejoin the text
        text = "".join(sentences)
        
        return text
    
    def _add_contractions(self, text: str) -> str:
        """Add natural contractions to text"""
        contractions = {
            "I am": "I'm",
            "You are": "You're",
            "They are": "They're",
            "We are": "We're",
            "He is": "He's",
            "She is": "She's",
            "It is": "It's",
            "That is": "That's",
            "What is": "What's",
            "Who is": "Who's",
            "There is": "There's",
            "Here is": "Here's",
            "How is": "How's",
            "do not": "don't",
            "does not": "doesn't",
            "did not": "didn't",
            "has not": "hasn't",
            "have not": "haven't",
            "had not": "hadn't",
            "will not": "won't",
            "would not": "wouldn't",
            "could not": "couldn't",
            "should not": "shouldn't",
            "is not": "isn't",
            "are not": "aren't",
            "was not": "wasn't",
            "were not": "weren't"
        }
        
        for full, contraction in contractions.items():
            # Use word boundaries to avoid partial matches
            text = re.sub(r'\b' + full + r'\b', contraction, text, flags=re.IGNORECASE)
        
        return text
    
    def _add_speech_rhythm(self, text: str) -> str:
        """Add natural speech rhythm with pauses"""
        # Add occasional ellipses for thoughtful pauses (10% chance)
        if random.random() < 0.1:
            sentences = text.split(". ")
            if len(sentences) > 2:
                idx = random.randint(1, len(sentences) - 1)
                sentences[idx] = "... " + sentences[idx]
                text = ". ".join(sentences)
        
        # Add occasional commas for brief pauses (20% chance)
        words = text.split()
        if len(words) > 8:
            for i in range(3, len(words) - 3, 5):
                if random.random() < 0.2 and not (words[i].endswith(',') or words[i].endswith('.') or words[i].endswith('!') or words[i].endswith('?')):
                    words[i] = words[i] + ','
            text = ' '.join(words)
        
        return text
    
    def generate_thinking_phrase(self) -> str:
        """Generate a phrase to indicate the assistant is thinking"""
        return random.choice(self.thinking_phrases)
    
    def generate_acknowledgment(self) -> str:
        """Generate an acknowledgment phrase"""
        return random.choice(self.acknowledgment_phrases)
    
    def add_context_awareness(self, response: str) -> str:
        """Add context awareness to response based on enhanced context"""
        if not self.enhanced_context:
            return response
            
        context = self.enhanced_context.get_current_context()
        time_awareness = context.get('time_awareness', {})
        
        # Add time-based references occasionally
        if random.random() < 0.3 and time_awareness:
            time_of_day = time_awareness.get('time_of_day')
            if time_of_day:
                time_references = {
                    'morning': ["this morning", "early today", "as we start the day"],
                    'afternoon': ["this afternoon", "during lunch", "midday"],
                    'evening': ["this evening", "tonight", "as the day winds down"],
                    'night': ["at this late hour", "tonight", "this late"]
                }
                
                if time_of_day in time_references:
                    reference = random.choice(time_references[time_of_day])
                    response = f"Since it's {reference}, {response.lower()}"
        
        # Reference previous topics occasionally
        if random.random() < 0.2 and context.get('conversation_topics'):
            topics = context['conversation_topics']
            if topics:
                topic = random.choice(topics)
                topic_references = [
                    f"Speaking of {topic}, ",
                    f"Relating to our discussion about {topic}, ",
                    f"On the topic of {topic}, "
                ]
                response = random.choice(topic_references) + response
        
        return response