import pygame
import os

class MusicController:
    def __init__(self):
        pygame.mixer.init()
        self.playlist = []
        self.current_track = 0
        self.paused = False

    def toggle_playback(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
        else:
            pygame.mixer.music.unpause()
            self.paused = False

    def load_playlist(self, folder_path):
        self.playlist = [os.path.join(folder_path, f) 
                        for f in os.listdir(folder_path)
                        if f.endswith(('.mp3', '.wav'))]
        
    def next_track(self):
        self.current_track = (self.current_track + 1) % len(self.playlist)
        pygame.mixer.music.load(self.playlist[self.current_track])
        pygame.mixer.music.play()

    def is_playing(self):
        return pygame.mixer.music.get_busy() 