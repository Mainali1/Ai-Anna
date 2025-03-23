from . import Command
import webbrowser
import urllib.parse

class WebSearchCommand(Command):
    def validate(self, command: str) -> bool:
        return ('search' in command.lower() and 'web' in command.lower()) or 'google' in command.lower()
        
    def execute(self, command: str) -> str:
        try:
            # Extract search query
            query = self._extract_query(command)
            if not query:
                return "I couldn't understand what you want to search for."
                
            # Encode query for URL
            encoded_query = urllib.parse.quote_plus(query)
            
            # Open web browser with search
            search_url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(search_url)
            
            return f"I've searched the web for '{query}'."
        except Exception as e:
            print(f"Error in web search command: {str(e)}")
            return f"I encountered an error performing the web search: {str(e)}"
            
    def _extract_query(self, command: str) -> str:
        # Extract query from command
        # Examples: "search web for python programming", "google nepal"
        command = command.lower()
        if "search web for" in command:
            return command.split("search web for")[-1].strip()
        elif "search for" in command:
            return command.split("search for")[-1].strip()
        elif "google" in command:
            return command.split("google")[-1].strip()
        return ""