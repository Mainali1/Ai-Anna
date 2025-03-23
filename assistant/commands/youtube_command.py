from . import Command
import webbrowser
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup  # Make sure to use BeautifulSoup

class YouTubeCommand(Command):
    def validate(self, command: str) -> bool:
        return 'youtube' in command.lower()
        
    def execute(self, command: str) -> str:
        try:
            # Extract query from command
            query = self._extract_query(command)
            if not query:
                return "I couldn't understand what you want to search for on YouTube."
                
            # Search YouTube
            video_url = self._search_youtube(query)
            if video_url:
                webbrowser.open(video_url)
                return f"Playing '{query}' on YouTube."
            else:
                # If no direct match, open YouTube search
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
                webbrowser.open(search_url)
                return f"Searching for '{query}' on YouTube."
        except Exception as e:
            print(f"Error in YouTube command: {str(e)}")
            return f"I encountered an error with YouTube: {str(e)}"
            
    def _extract_query(self, command: str) -> str:
        # Extract query from command
        # Examples: "youtube nepal", "play youtube mount everest"
        command = command.lower()
        if "youtube" in command:
            if "play" in command:
                return command.replace("play", "").replace("youtube", "").strip()
            else:
                return command.replace("youtube", "").strip()
        return ""
        
    def _search_youtube(self, query):
        """Search YouTube for a video and return the URL of the first result"""
        try:
            # Format the search query
            search_query = urllib.parse.quote_plus(query)
            url = f"https://www.youtube.com/results?search_query={search_query}"
            
            # Send request to YouTube
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            # Parse the response with BeautifulSoup for more reliable extraction
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # First try to extract using data attributes (more reliable)
                video_elements = soup.find_all('a', {'href': re.compile(r'/watch\?v=')})
                if video_elements:
                    for element in video_elements:
                        href = element.get('href', '')
                        if '/watch?v=' in href and 'list=' not in href:  # Avoid playlists
                            video_id = href.split('/watch?v=')[1]
                            return f"https://www.youtube.com/watch?v={video_id}"
                
                # Fallback to regex if BeautifulSoup approach fails
                video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                if video_ids:
                    return f"https://www.youtube.com/watch?v={video_ids[0]}"
            
            return None
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return None