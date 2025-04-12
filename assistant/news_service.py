import requests
import json
from datetime import datetime
import threading

class NewsService:
    def __init__(self, container=None):
        self.container = container
        self.logger = container.get_service('logger') if container else None
        self.config_manager = container.get_service('config_manager') if container else None
        
        # Get API key from config
        self.api_key = self.config_manager.config.get('news_api_key', '') if self.config_manager else ''
        self.base_url = "https://newsapi.org/v2/"
        
        # News categories
        self.categories = [
            "general", "business", "entertainment", "health", 
            "science", "sports", "technology"
        ]
        
        # News countries
        self.countries = {
            "us": "United States",
            "gb": "United Kingdom",
            "ca": "Canada",
            "au": "Australia",
            "in": "India",
            "de": "Germany",
            "fr": "France",
            "jp": "Japan",
            "cn": "China",
            "ru": "Russia",
            "br": "Brazil"
        }
        
        # Cache for news
        self.news_cache = {}
        self.cache_expiry = 30 * 60  # 30 minutes in seconds
        self.last_fetch_time = {}
    
    def get_top_headlines(self, country="us", category=None, query=None, max_results=5):
        """
        Get top headlines from News API
        
        Args:
            country (str): Country code (default: "us")
            category (str): News category (optional)
            query (str): Search query (optional)
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of news articles
        """
        # Check if we have cached results that are still valid
        cache_key = f"headlines_{country}_{category}_{query}"
        current_time = datetime.now().timestamp()
        
        if (cache_key in self.news_cache and 
            cache_key in self.last_fetch_time and
            current_time - self.last_fetch_time[cache_key] < self.cache_expiry):
            return self.news_cache[cache_key][:max_results]
        
        # Build request parameters
        params = {
            "country": country,
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
            
        if query:
            params["q"] = query
        
        try:
            response = requests.get(f"{self.base_url}top-headlines", params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("status") == "ok":
                articles = data.get("articles", [])
                
                # Process articles
                processed_articles = []
                for article in articles:
                    processed_articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "content": article.get("content", "")
                    })
                
                # Cache the results
                self.news_cache[cache_key] = processed_articles
                self.last_fetch_time[cache_key] = current_time
                
                return processed_articles[:max_results]
            else:
                error_message = f"Error fetching news: {data.get('message', 'Unknown error')}"
                if self.logger:
                    self.logger.error(error_message)
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"News API error: {str(e)}")
            return []
    
    def get_everything(self, query, sources=None, domains=None, from_date=None, to_date=None, language="en", sort_by="publishedAt", max_results=5):
        """
        Search for news articles from News API
        
        Args:
            query (str): Search query
            sources (str): Comma-separated list of sources
            domains (str): Comma-separated list of domains
            from_date (str): Start date in YYYY-MM-DD format
            to_date (str): End date in YYYY-MM-DD format
            language (str): Language code (default: "en")
            sort_by (str): Sort order (default: "publishedAt")
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of news articles
        """
        # Check if we have cached results that are still valid
        cache_key = f"everything_{query}_{sources}_{domains}_{from_date}_{to_date}_{language}_{sort_by}"
        current_time = datetime.now().timestamp()
        
        if (cache_key in self.news_cache and 
            cache_key in self.last_fetch_time and
            current_time - self.last_fetch_time[cache_key] < self.cache_expiry):
            return self.news_cache[cache_key][:max_results]
        
        # Build request parameters
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "apiKey": self.api_key
        }
        
        if sources:
            params["sources"] = sources
            
        if domains:
            params["domains"] = domains
            
        if from_date:
            params["from"] = from_date
            
        if to_date:
            params["to"] = to_date
        
        try:
            response = requests.get(f"{self.base_url}everything", params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("status") == "ok":
                articles = data.get("articles", [])
                
                # Process articles
                processed_articles = []
                for article in articles:
                    processed_articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "published_at": article.get("publishedAt", ""),
                        "content": article.get("content", "")
                    })
                
                # Cache the results
                self.news_cache[cache_key] = processed_articles
                self.last_fetch_time[cache_key] = current_time
                
                return processed_articles[:max_results]
            else:
                error_message = f"Error fetching news: {data.get('message', 'Unknown error')}"
                if self.logger:
                    self.logger.error(error_message)
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"News API error: {str(e)}")
            return []
    
    def get_news_sources(self, category=None, language=None, country=None):
        """
        Get available news sources from News API
        
        Args:
            category (str): News category (optional)
            language (str): Language code (optional)
            country (str): Country code (optional)
            
        Returns:
            list: List of news sources
        """
        # Build request parameters
        params = {
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
            
        if language:
            params["language"] = language
            
        if country:
            params["country"] = country
        
        try:
            response = requests.get(f"{self.base_url}sources", params=params)
            data = response.json()
            
            if response.status_code == 200 and data.get("status") == "ok":
                sources = data.get("sources", [])
                
                # Process sources
                processed_sources = []
                for source in sources:
                    processed_sources.append({
                        "id": source.get("id", ""),
                        "name": source.get("name", ""),
                        "description": source.get("description", ""),
                        "url": source.get("url", ""),
                        "category": source.get("category", ""),
                        "language": source.get("language", ""),
                        "country": source.get("country", "")
                    })
                
                return processed_sources
            else:
                error_message = f"Error fetching news sources: {data.get('message', 'Unknown error')}"
                if self.logger:
                    self.logger.error(error_message)
                return []
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"News API error: {str(e)}")
            return []
    
    def get_news_summary(self, country="us", category=None, max_results=5):
        """Get a formatted summary of top news"""
        articles = self.get_top_headlines(country, category, max_results=max_results)
        
        if not articles:
            return "Sorry, I couldn't fetch the latest news at this time."
        
        country_name = self.countries.get(country, country.upper())
        category_text = f" - {category.capitalize()}" if category else ""
        
        summary = f"📰 Top News from {country_name}{category_text}:\n\n"
        
        for i, article in enumerate(articles, 1):
            title = article.get("title", "").split(" - ")[0]  # Remove source from title
            source = article.get("source", "")
            summary += f"{i}. {title} ({source})\n"
        
        return summary