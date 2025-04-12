import re
from ..command_base import CommandBase

class GoogleSearchCommand(CommandBase):
    """Command to search Google"""
    
    def __init__(self, container=None):
        super().__init__(container)
        self.search_service = container.get_service('search_service') if container else None
        self.feature_toggle = container.get_service('feature_toggle') if container else None
        
    def matches(self, command):
        """Check if the command is a Google search request"""
        patterns = [
            r"^(?:search|google|look up|find)(?:\s+for)?\s+(.+)$",
            r"^(?:what|who|where|when|how|why)(?:\s+is|'s|s|'re|re|'m|m|'ve|ve|'d|d)?\s+(.+)$"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                return True
        
        return False
        
    def execute(self, command):
        """Execute the Google search command"""
        # Check if feature is enabled
        if self.feature_toggle and not self.feature_toggle.is_enabled('google_search'):
            return "Google search is currently disabled. You can enable it in Settings."
        
        if not self.search_service:
            return "Search service is not available."
            
        # Extract search query
        patterns = [
            r"^(?:search|google|look up|find)(?:\s+for)?\s+(.+)$",
            r"^(?:what|who|where|when|how|why)(?:\s+is|'s|s|'re|re|'m|m|'ve|ve|'d|d)?\s+(.+)$"
        ]
        
        query = None
        for pattern in patterns:
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                query = match.group(1)
                break
        
        if not query:
            return "I'm not sure what you want to search for."
            
        # Perform search
        return self.search_service.search_google(query, open_browser=True)


class NewsCommand(CommandBase):
    """Command to get news updates"""
    
    def __init__(self, container=None):
        super().__init__(container)
        self.news_service = container.get_service('news_service') if container else None
        self.feature_toggle = container.get_service('feature_toggle') if container else None
        
    def matches(self, command):
        """Check if the command is a news request"""
        patterns = [
            r"^(?:get|show|tell me|what's|whats|what are)(?:\s+the)?\s+(?:latest|recent|current|today's|todays)?\s*news(?:\s+(?:from|about|on|in)\s+(.+))?$",
            r"^news(?:\s+(?:from|about|on|in)\s+(.+))?$"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                return True
        
        return False
        
    def execute(self, command):
        """Execute the news command"""
        # Check if feature is enabled
        if self.feature_toggle and not self.feature_toggle.is_enabled('news_service'):
            return "News service is currently disabled. You can enable it in Settings."
        
        if not self.news_service:
            return "News service is not available."
            
        # Extract category or country
        patterns = [
            r"^(?:get|show|tell me|what's|whats|what are)(?:\s+the)?\s+(?:latest|recent|current|today's|todays)?\s*news(?:\s+(?:from|about|on|in)\s+(.+))?$",
            r"^news(?:\s+(?:from|about|on|in)\s+(.+))?$"
        ]
        
        topic = None
        for pattern in patterns:
            match = re.match(pattern, command, re.IGNORECASE)
            if match and match.group(1):
                topic = match.group(1)
                break
        
        # Check if topic is a country
        country_map = {
            "us": "us", "usa": "us", "united states": "us", "america": "us",
            "uk": "gb", "britain": "gb", "england": "gb", "united kingdom": "gb",
            "canada": "ca", "australia": "au", "india": "in",
            "germany": "de", "france": "fr", "japan": "jp",
            "china": "cn", "russia": "ru", "brazil": "br"
        }
        
        # Check if topic is a category
        categories = ["business", "entertainment", "health", "science", "sports", "technology"]
        
        if topic:
            topic_lower = topic.lower()
            if topic_lower in country_map:
                return self.news_service.get_news_summary(country=country_map[topic_lower])
            elif topic_lower in categories:
                return self.news_service.get_news_summary(category=topic_lower)
            else:
                # Treat as a search query
                articles = self.news_service.get_everything(query=topic, max_results=5)
                if not articles:
                    return f"Sorry, I couldn't find any news about {topic}."
                
                summary = f"📰 News about {topic}:\n\n"
                for i, article in enumerate(articles, 1):
                    title = article.get("title", "").split(" - ")[0]  # Remove source from title
                    source = article.get("source", "")
                    summary += f"{i}. {title} ({source})\n"
                
                return summary
        else:
            # Default to US general news
            return self.news_service.get_news_summary()