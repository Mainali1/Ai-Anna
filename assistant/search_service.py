import requests
from bs4 import BeautifulSoup
import webbrowser
from urllib.parse import quote_plus
import threading

class SearchService:
    def __init__(self, container=None):
        self.container = container
        self.logger = container.get_service('logger') if container else None
        self.search_history = []
        self.max_history = 50
        
    def search_google(self, query, open_browser=False):
        """
        Search Google for the given query
        
        Args:
            query (str): The search query
            open_browser (bool): Whether to open the results in a browser
            
        Returns:
            str: A message indicating the search was performed
        """
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        
        # Add to history
        self.search_history.append({"query": query, "url": search_url})
        if len(self.search_history) > self.max_history:
            self.search_history.pop(0)
        
        if open_browser:
            webbrowser.open(search_url)
            return f"Opened Google search for: {query}"
        
        # Start a thread to fetch search results
        threading.Thread(target=self._fetch_search_results, 
                         args=(query, search_url), 
                         daemon=True).start()
        
        return f"Searching Google for: {query}. Results will be displayed shortly."
    
    def _fetch_search_results(self, query, url):
        """Fetch search results in a background thread"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract search results
                search_results = []
                for result in soup.select('div.g'):
                    title_element = result.select_one('h3')
                    link_element = result.select_one('a')
                    snippet_element = result.select_one('div.VwiC3b')
                    
                    if title_element and link_element:
                        title = title_element.get_text()
                        link = link_element.get('href')
                        snippet = snippet_element.get_text() if snippet_element else ""
                        
                        if link.startswith('/url?q='):
                            link = link.split('/url?q=')[1].split('&')[0]
                        
                        search_results.append({
                            'title': title,
                            'link': link,
                            'snippet': snippet
                        })
                
                # Notify about results
                if self.container and self.container.get_service('events'):
                    self.container.get_service('events').emit(
                        'search_results', 
                        {'query': query, 'results': search_results[:5]}
                    )
            else:
                if self.logger:
                    self.logger.error(f"Search error: HTTP {response.status_code}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Search error: {str(e)}")
    
    def get_search_history(self):
        """Get the search history"""
        return self.search_history
    
    def clear_search_history(self):
        """Clear the search history"""
        self.search_history = []
        return "Search history cleared."