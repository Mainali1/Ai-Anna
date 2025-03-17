import os
import wolframalpha
import wikipedia
import cv2
import pyjokes
from typing import Optional, Dict, Any

class ExternalServices:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._setup_services()

    def _setup_services(self):
        """Initialize external service clients"""
        # Initialize WolframAlpha client
        wolfram_app_id = os.getenv('WOLFRAM_APP_ID')
        self.wolfram_client = wolframalpha.Client(wolfram_app_id) if wolfram_app_id else None
        
        # Configure Wikipedia
        wikipedia.set_lang('en')
        
        # Initialize camera for image capture
        self.camera = None
        

    def query_wolfram(self, query: str) -> str:
        """Query WolframAlpha for computational and knowledge-based questions"""
        try:
            res = self.wolfram_client.query(query)
            # Get the first result that has text
            for pod in res.pods:
                if pod.text:
                    return pod.text
            return "No simple answer found. The query may be too complex."
        except Exception as e:
            return f"Error querying WolframAlpha: {str(e)}"

    def search_wikipedia(self, query: str, sentences: int = 3) -> str:
        """Search Wikipedia and return a summary"""
        try:
            return wikipedia.summary(query, sentences=sentences)
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple matches found. Please be more specific. Options: {', '.join(e.options[:5])}"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{query}'"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

    def capture_image(self, save_path: Optional[str] = None) -> str:
        """Capture an image from the camera"""
        try:
            if not self.camera:
                self.camera = cv2.VideoCapture(0)
            
            ret, frame = self.camera.read()
            if not ret:
                return "Failed to capture image"
            
            if save_path:
                cv2.imwrite(save_path, frame)
                return f"Image saved to {save_path}"
            else:
                return "Image captured but no save path provided"
        except Exception as e:
            return f"Error capturing image: {str(e)}"
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None

    def get_joke(self, category: str = 'neutral') -> str:
        """Get a random joke from PyJokes"""
        try:
            return pyjokes.get_joke(category=category)
        except Exception as e:
            return f"Error getting joke: {str(e)}"

    def cleanup(self):
        """Cleanup resources"""
        if self.camera:
            self.camera.release()
            self.camera = None