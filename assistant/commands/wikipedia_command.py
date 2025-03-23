from . import Command
import wikipedia
import webbrowser

class WikipediaCommand(Command):
    def validate(self, command: str) -> bool:
        return 'wikipedia' in command.lower()
        
    def execute(self, command: str) -> str:
        try:
            # Extract search query
            query = self._extract_query(command)
            if not query:
                return "I couldn't understand what you want to search for on Wikipedia."
                
            # Try to get a summary from Wikipedia
            try:
                # Set language to English
                wikipedia.set_lang("en")
                
                # Search for the query
                search_results = wikipedia.search(query)
                if not search_results:
                    return f"I couldn't find any Wikipedia articles about '{query}'."
                    
                # Get the first result
                page_title = search_results[0]
                
                # Get a summary of the page
                summary = wikipedia.summary(page_title, sentences=3)
                
                # Open the Wikipedia page in a browser
                page = wikipedia.page(page_title)
                webbrowser.open(page.url)
                
                return f"Here's what I found about '{page_title}' on Wikipedia:\n\n{summary}\n\nI've opened the full article in your browser."
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation pages
                options = e.options[:5]  # Limit to first 5 options
                options_str = ", ".join(options)
                return f"There are multiple Wikipedia articles related to '{query}'. Did you mean one of these: {options_str}?"
            except wikipedia.exceptions.PageError:
                # Handle page not found
                return f"I couldn't find a Wikipedia article about '{query}'."
                
        except Exception as e:
            print(f"Error in Wikipedia command: {str(e)}")
            return f"I encountered an error searching Wikipedia: {str(e)}"
            
    def _extract_query(self, command: str) -> str:
        # Extract query from command
        command = command.lower()
        if "wikipedia" in command:
            if "for" in command.split("wikipedia")[1]:
                return command.split("for")[-1].strip()
            else:
                return command.split("wikipedia")[-1].strip()
        return ""