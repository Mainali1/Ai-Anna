import tkinter as tk
from tkinter import ttk
import webbrowser
from urllib.parse import quote_plus
import threading
import requests
from bs4 import BeautifulSoup

class BrowserFrame(ttk.Frame):
    def __init__(self, master, container=None):
        super().__init__(master)
        self.container = container
        self.logger = container.get_service('logger') if container else None
        
        # Create browser UI components
        self.create_browser_ui()
        
    def create_browser_ui(self):
        # URL bar and navigation controls
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Back button
        self.back_button = ttk.Button(nav_frame, text="←", width=2, command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=2)
        
        # Forward button
        self.forward_button = ttk.Button(nav_frame, text="→", width=2, command=self.go_forward)
        self.forward_button.pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        self.refresh_button = ttk.Button(nav_frame, text="↻", width=2, command=self.refresh)
        self.refresh_button.pack(side=tk.LEFT, padx=2)
        
        # URL entry
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(nav_frame, textvariable=self.url_var)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.url_entry.bind("<Return>", self.navigate)
        
        # Go button
        self.go_button = ttk.Button(nav_frame, text="Go", command=self.navigate)
        self.go_button.pack(side=tk.LEFT, padx=2)
        
        # Content area (using Text widget as a simple viewer)
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_area = tk.Text(self.content_frame, wrap=tk.WORD, bg='white', fg='black')
        self.content_area.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_area, command=self.content_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_area.config(yscrollcommand=scrollbar.set)
        
        # History
        self.history = []
        self.current_index = -1
        
        # Set default page
        self.url_var.set("https://www.google.com")
        
    def navigate(self, event=None):
        url = self.url_var.get()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_var.set(url)
        
        # For simplicity, we'll open in the default browser
        # In a real implementation, you'd render the page in the content area
        webbrowser.open(url)
        
        # Add to history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        self.history.append(url)
        self.current_index = len(self.history) - 1
        
        # In a simple implementation, we can fetch and display basic HTML
        self.fetch_page_content(url)
        
    def fetch_page_content(self, url):
        """Fetch and display basic page content"""
        self.content_area.config(state=tk.NORMAL)
        self.content_area.delete(1.0, tk.END)
        self.content_area.insert(tk.END, f"Loading {url}...\n\n")
        self.content_area.config(state=tk.DISABLED)
        
        # Fetch in a separate thread to avoid freezing the UI
        threading.Thread(target=self._fetch_content, args=(url,), daemon=True).start()
    
    def _fetch_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text()
            
            # Update UI in the main thread
            self.after(0, self._update_content, text_content)
            
        except Exception as e:
            error_message = f"Error loading page: {str(e)}"
            self.after(0, self._update_content, error_message)
            if self.logger:
                self.logger.error(f"Browser error: {error_message}")
    
    def _update_content(self, content):
        self.content_area.config(state=tk.NORMAL)
        self.content_area.delete(1.0, tk.END)
        self.content_area.insert(tk.END, content)
        self.content_area.config(state=tk.DISABLED)
    
    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            url = self.history[self.current_index]
            self.url_var.set(url)
            self.fetch_page_content(url)
    
    def go_forward(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            url = self.history[self.current_index]
            self.url_var.set(url)
            self.fetch_page_content(url)
    
    def refresh(self):
        if self.current_index >= 0 and self.current_index < len(self.history):
            url = self.history[self.current_index]
            self.fetch_page_content(url)
    
    def search_google(self, query):
        """Search Google for the given query"""
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        self.url_var.set(search_url)
        self.navigate()
        return f"Searching Google for: {query}"