import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
import pygame
import os
import glob
import pyautogui

class MediaController:
    def __init__(self, config=None):
        """
        Initialize the MediaController with configuration.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.music_path = None
        self.current_player = None
        self.playlist = []
        self.current_track = 0
        self.paused = False
        self.config = None  # Will be set after initialization
        self.music_path = None
        self.is_system_control = False  # Flag to determine if we're controlling system media
        
    def set_music_path(self):
        """Set the music path from config or use default"""
        try:
            # Handle different ways the config might be structured
            if self.config is None:
                # If config is None, use default path
                self.music_path = os.path.join(os.path.expanduser('~'), 'Music')
                print(f"No config provided. Using default music path: {self.music_path}")
            elif hasattr(self.config, 'get'):
                # If config is a ConfigManager object with get method
                self.music_path = self.config.get('music_path', None)
            elif isinstance(self.config, dict):
                # If config is a dictionary
                self.music_path = self.config.get('music_path', None)
            else:
                # If config is of an unexpected type
                self.music_path = None
                print("Config is of unexpected type. Using default path.")
            
            # If no music path is set, use default
            if not self.music_path:
                # Use a default path if not specified in config
                self.music_path = os.path.join(os.path.expanduser('~'), 'Music')
                print(f"Using default music path: {self.music_path}")
            
            # Ensure the directory exists
            if not os.path.exists(self.music_path):
                os.makedirs(self.music_path, exist_ok=True)
                print(f"Created music directory: {self.music_path}")
                
        except Exception as e:
            print(f"Error setting music path: {str(e)}")
            # Set a default path as fallback
            self.music_path = os.path.join(os.path.expanduser('~'), 'Music')
            print(f"Using fallback music path: {self.music_path}")
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.music_path):
            os.makedirs(self.music_path, exist_ok=True)
            
        print(f"Media path set to: {self.music_path}")
    
    # Universal media control methods
    def play(self):
        """Play or resume media (local or system)"""
        if self.is_system_control:
            return self.system_play_pause()
        
        # Local playback logic
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        elif not pygame.mixer.music.get_busy() and self.playlist:
            pygame.mixer.music.load(self.playlist[self.current_track])
            pygame.mixer.music.play()
        return True
    
    def pause(self):
        """Pause media (local or system)"""
        if self.is_system_control:
            return self.system_play_pause()
        
        # Local playback logic
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        return True
    
    def stop(self):
        """Stop media (local or system)"""
        if self.is_system_control:
            return self.system_stop()
        
        # Local playback logic
        pygame.mixer.music.stop()
        self.paused = False
        return True
    
    def next_track(self):
        """Play next track (local or system)"""
        if self.is_system_control:
            return self.system_next()
        
        # Local playback logic
        if not self.playlist:
            return False
            
        self.current_track = (self.current_track + 1) % len(self.playlist)
        pygame.mixer.music.load(self.playlist[self.current_track])
        pygame.mixer.music.play()
        return True
    
    def previous_track(self):
        """Play previous track (local or system)"""
        if self.is_system_control:
            return self.system_previous()
        
        # Local playback logic
        if not self.playlist:
            return False
            
        self.current_track = (self.current_track - 1) % len(self.playlist)
        pygame.mixer.music.load(self.playlist[self.current_track])
        pygame.mixer.music.play()
        return True
    
    def volume_up(self):
        """Increase volume (local or system)"""
        if self.is_system_control:
            return self.system_volume_up()
        
        # Local volume control would go here
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(min(current_volume + 0.1, 1.0))
        return True
    
    def volume_down(self):
        """Decrease volume (local or system)"""
        if self.is_system_control:
            return self.system_volume_down()
        
        # Local volume control would go here
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(max(current_volume - 0.1, 0.0))
        return True
    
    def set_volume(self, level):
        """Set volume level (0-100)"""
        if self.is_system_control:
            # Not easily implemented for system volume
            return False
        
        # Local volume control
        volume = max(0, min(level, 100)) / 100.0
        pygame.mixer.music.set_volume(volume)
        return True
    
    # System-specific media control methods
    def system_play_pause(self):
        """Send play/pause media key to control system-wide media playback"""
        pyautogui.press('playpause')
        return True
        
    def system_stop(self):
        """Send stop media key to control system-wide media playback"""
        pyautogui.press('stop')
        return True
        
    def system_next(self):
        """Send next track media key to control system-wide media playback"""
        pyautogui.press('nexttrack')
        return True
        
    def system_previous(self):
        """Send previous track media key to control system-wide media playback"""
        pyautogui.press('prevtrack')
        return True
        
    def system_volume_up(self):
        """Increase system volume"""
        pyautogui.press('volumeup')
        return True
        
    def system_volume_down(self):
        """Decrease system volume"""
        pyautogui.press('volumedown')
        return True
        
    def system_mute(self):
        """Mute/unmute system volume"""
        pyautogui.press('volumemute')
        return True
    
    # Local media specific methods
    def load_playlist(self, folder_path=None):
        """Load all media files from a folder"""
        if folder_path is None:
            if self.music_path is None:
                self.set_music_path()
            folder_path = self.music_path
            
        print(f"Loading playlist from: {folder_path}")
        self.playlist = []
        
        # Find all media files
        for ext in ['.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mkv']:
            self.playlist.extend(glob.glob(os.path.join(folder_path, f"*{ext}")))
            
        print(f"Found {len(self.playlist)} media files")
        return len(self.playlist) > 0
    
    def play_media(self, media_name):
        """Play media by name"""
        try:
            # Find matching files
            matches = self.find_media_files(media_name)
            if not matches:
                return False
                
            # Load and play the first match
            pygame.mixer.music.load(matches[0])
            pygame.mixer.music.play()
            self.current_track = 0
            self.playlist = matches
            return True
        except Exception as e:
            print(f"Error playing media: {str(e)}")
            return False
        if self.music_path is None:
            self.set_music_path()
            
        # Find the media in the directory
        for ext in ['.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mkv']:
            matches = glob.glob(os.path.join(self.music_path, f"*{media_name}*{ext}"))
            if matches:
                pygame.mixer.music.load(matches[0])
                pygame.mixer.music.play()
                return True
                
        # If not found, try loading playlist and finding there
        if not self.playlist:
            self.load_playlist()
            
        for media_path in self.playlist:
            if media_name.lower() in os.path.basename(media_path).lower():
                pygame.mixer.music.load(media_path)
                pygame.mixer.music.play()
                return True
                
        return False
    
    def play_by_artist(self, artist_name):
        """Play media by a specific artist"""
        if self.music_path is None:
            self.set_music_path()
            
        # Load playlist if not already loaded
        if not self.playlist:
            self.load_playlist()
            
        # Find media by artist
        artist_media = []
        for media_path in self.playlist:
            if artist_name.lower() in os.path.basename(media_path).lower():
                artist_media.append(media_path)
                
        if artist_media:
            pygame.mixer.music.load(artist_media[0])
            pygame.mixer.music.play()
            return True
        return False
    
    def play_playlist(self, playlist_name):
        """Play a specific playlist"""
        if self.music_path is None:
            self.set_music_path()
            
        # Check if there's a subfolder matching the playlist name
        playlist_path = os.path.join(self.music_path, playlist_name)
        if os.path.isdir(playlist_path):
            if self.load_playlist(playlist_path):
                pygame.mixer.music.load(self.playlist[0])
                pygame.mixer.music.play()
                return True
        return False
    
    def toggle_control_mode(self):
        """Toggle between local and system media control"""
        self.is_system_control = not self.is_system_control
        return self.is_system_control
    
    
    # Add these methods to the MediaController class
    def play_youtube(self, query):
        """Search and play a YouTube video"""
        try:
            # First try to get video directly
            video_url = self._search_youtube(query)
            if video_url:
                webbrowser.open(video_url)
                return True, f"Playing '{query}' on YouTube"
            else:
                # If no direct match, open YouTube search
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
                webbrowser.open(search_url)
                return True, f"Searching for '{query}' on YouTube"
        except Exception as e:
            print(f"Error playing YouTube: {str(e)}")
            return False, str(e)
    
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
            
            # Parse the response
            if response.status_code == 200:
                # Extract video ID using regex
                video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                if video_ids:
                    # Return the URL of the first video
                    return f"https://www.youtube.com/watch?v={video_ids[0]}"
            
            return None
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return None