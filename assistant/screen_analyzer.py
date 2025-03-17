import cv2
import numpy as np
import pyautogui
from PIL import Image
import pytesseract
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

class ScreenAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.last_analysis = None
        self.context_history = []
        self.max_history = 10
        
    def capture_screen_region(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture the screen or a specific region"""
        try:
            # Capture the entire screen if no region specified
            screenshot = pyautogui.screenshot(region=region)
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Error capturing screen: {str(e)}")
            return None

    def extract_text_from_image(self, image: np.ndarray) -> str:
        """Extract text from the captured image using OCR"""
        try:
            # Convert the image to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(gray)
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return ""

    def analyze_screen_content(self) -> Dict[str, Any]:
        """Analyze the current screen content and return relevant information"""
        try:
            # Capture the current screen
            screen = self.capture_screen_region()
            if screen is None:
                return {}

            # Extract text content
            text_content = self.extract_text_from_image(screen)

            # Get active window information
            active_window = pyautogui.getActiveWindow()
            window_title = active_window.title if active_window else "Unknown"

            # Create analysis result
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'window_title': window_title,
                'text_content': text_content,
                'screen_resolution': pyautogui.size()
            }

            # Update history
            self.context_history.append(analysis)
            if len(self.context_history) > self.max_history:
                self.context_history.pop(0)

            self.last_analysis = analysis
            return analysis

        except Exception as e:
            print(f"Error analyzing screen content: {str(e)}")
            return {}

    def get_context_summary(self) -> str:
        """Generate a summary of the current screen context"""
        if not self.last_analysis:
            return "No screen analysis available"

        window_title = self.last_analysis['window_title']
        text_preview = self.last_analysis['text_content'][:200] + '...' if len(self.last_analysis['text_content']) > 200 else self.last_analysis['text_content']

        return f"Currently viewing: {window_title}\nContent preview: {text_preview}"

    def get_relevant_response(self, user_query: str) -> str:
        """Generate a contextually relevant response based on screen content and user query"""
        if not self.last_analysis:
            return "I need to analyze your screen first to provide relevant assistance."

        # Simple keyword matching for demonstration
        window_title = self.last_analysis['window_title'].lower()
        text_content = self.last_analysis['text_content'].lower()
        query = user_query.lower()

        # Context-aware responses
        if 'browser' in window_title:
            return "I notice you're browsing. Would you like me to help you find specific information?"
        elif any(app in window_title for app in ['word', 'document']):
            return "I see you're working on a document. Need help with writing or formatting?"
        elif any(app in window_title for app in ['excel', 'spreadsheet']):
            return "Working with spreadsheets? I can help with formulas and data analysis."
        elif 'code' in window_title or any(ext in window_title for ext in ['.py', '.js', '.java']):
            return "I see you're coding. Need help with syntax or debugging?"

        return "I'm here to help! What would you like to know about what you're viewing?"

    def get_screen_context(self) -> Dict[str, Any]:
        """Get the current screen context including analysis and relevant information"""
        try:
            # Perform screen analysis
            analysis = self.analyze_screen_content()
            if not analysis:
                return {'status': 'error', 'message': 'Failed to analyze screen content'}

            # Get context summary
            context_summary = self.get_context_summary()

            # Combine all context information
            context = {
                'status': 'success',
                'analysis': analysis,
                'summary': context_summary,
                'history': self.context_history[-3:] if self.context_history else []
            }

            return context

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error getting screen context: {str(e)}'
            }