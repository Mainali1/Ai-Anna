import numpy as np
import torch
from torch import nn
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Tuple, Optional

class MoodDetector:
    def __init__(self):
        self.energy_threshold = 500
        self.pitch_threshold = 200
        # Initialize sentiment analysis model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
        self.model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
        self.model.to(self.device)
        
    def analyze_audio(self, audio_data: np.ndarray) -> Tuple[str, float]:
        energy = self._calculate_energy(audio_data)
        pitch = self._estimate_pitch(audio_data)
        
        # Combine audio features with sentiment analysis
        mood, confidence = self._classify_mood(energy, pitch)
        return mood, confidence
    
    def analyze_text(self, text: str) -> Tuple[str, float]:
        """Analyze text to detect mood using the sentiment model."""
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            confidence, prediction = torch.max(probabilities, dim=1)
            
        mood = 'positive' if prediction.item() == 1 else 'negative'
        return mood, confidence.item()
    
    def _calculate_energy(self, audio_data: np.ndarray) -> float:
        return np.mean(np.abs(audio_data))
    
    def _estimate_pitch(self, audio_data: np.ndarray) -> Optional[float]:
        zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
        if len(zero_crossings) > 1:
            return len(zero_crossings) / (2 * len(audio_data))
        return None
    
    def _classify_mood(self, energy: float, pitch: Optional[float]) -> Tuple[str, float]:
        if pitch is None:
            return 'neutral', 0.5
            
        # Enhanced rule-based classification with energy and pitch
        if energy > self.energy_threshold:
            if pitch > self.pitch_threshold:
                return 'excited', 0.8
            return 'angry', 0.7
        else:
            if pitch > self.pitch_threshold:
                return 'happy', 0.6
            return 'calm', 0.6
    
    def adjust_thresholds(self, energy_threshold: float, pitch_threshold: float) -> None:
        self.energy_threshold = energy_threshold
        self.pitch_threshold = pitch_threshold