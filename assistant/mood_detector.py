import numpy as np
from typing import Tuple, Optional

class MoodDetector:
    def __init__(self):
        self.energy_threshold = 500  # Adjustable energy threshold
        self.pitch_threshold = 200   # Adjustable pitch threshold
        
    def analyze_audio(self, audio_data: np.ndarray) -> Tuple[str, float]:
        """Analyze audio data to detect mood.
        
        Args:
            audio_data: numpy array of audio samples
            
        Returns:
            Tuple of (mood, confidence)
        """
        energy = self._calculate_energy(audio_data)
        pitch = self._estimate_pitch(audio_data)
        
        mood, confidence = self._classify_mood(energy, pitch)
        return mood, confidence
    
    def _calculate_energy(self, audio_data: np.ndarray) -> float:
        """Calculate the energy of the audio signal."""
        return np.mean(np.abs(audio_data))
    
    def _estimate_pitch(self, audio_data: np.ndarray) -> Optional[float]:
        """Estimate the fundamental frequency (pitch) of the audio."""
        # Simple zero-crossing rate based pitch estimation
        zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
        if len(zero_crossings) > 1:
            return len(zero_crossings) / (2 * len(audio_data))
        return None
    
    def _classify_mood(self, energy: float, pitch: Optional[float]) -> Tuple[str, float]:
        """Classify mood based on audio features.
        
        Returns:
            Tuple of (mood, confidence)
        """
        if pitch is None:
            return 'neutral', 0.5
            
        # Simple rule-based classification
        if energy > self.energy_threshold:
            if pitch > self.pitch_threshold:
                return 'excited', 0.8
            return 'angry', 0.7
        else:
            if pitch > self.pitch_threshold:
                return 'happy', 0.6
            return 'calm', 0.6
    
    def adjust_thresholds(self, energy_threshold: float, pitch_threshold: float) -> None:
        """Adjust the classification thresholds."""
        self.energy_threshold = energy_threshold
        self.pitch_threshold = pitch_threshold