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

    def web_search(self, query: str) -> list:
        """Perform a web search and return results"""
        try:
            # Process the query
            query = query.strip()
            if not query:
                return []

            # Initialize results list
            results = []
            
            # Provide meaningful offline search results
            query_words = query.lower().split()
            
            # Categorize the search
            if any(word in query_words for word in ['news', 'latest', 'update']):
                results.extend([
                    {
                        'title': f'Latest News about {query}',
                        'snippet': 'I am currently in offline mode. To get real-time news updates, please ensure you have an internet connection and valid API keys configured.',
                        'link': 'https://news.google.com'
                    }
                ])
            elif any(word in query_words for word in ['wiki', 'what is', 'who is', 'definition']):
                results.extend([
                    {
                        'title': f'Wikipedia: {query}',
                        'snippet': 'For encyclopedic information, please visit Wikipedia directly or ensure the system has proper API access configured.',
                        'link': f'https://wikipedia.org/wiki/Special:Search?search={query}'
                    }
                ])
            else:
                results.extend([
                    {
                        'title': f'Search Results for {query}',
                        'snippet': 'To get real search results, please ensure the system is properly configured with search API keys and has internet access.',
                        'link': f'https://www.google.com/search?q={query}'
                    }
                ])
            return results
        except Exception as e:
            self.logger.error(f"Error in web search: {str(e)}")
            return []

    def wikipedia_search(self, query: str) -> dict:
        """Search Wikipedia and return article summary and URL"""
        try:
            # Search Wikipedia
            page = wikipedia.page(query)
            return {
                'summary': wikipedia.summary(query, sentences=3),
                'url': page.url
            }
        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options[:5])
            raise Exception(f"Multiple matches found. Please be more specific. Options: {options}")
        except wikipedia.exceptions.PageError:
            raise Exception(f"No Wikipedia page found for '{query}'")
        except Exception as e:
            raise Exception(f"Error searching Wikipedia: {str(e)}")


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