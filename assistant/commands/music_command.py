from . import Command
from typing import Optional

class MusicCommand(Command):
    def validate(self, command: str) -> bool:
        return any(word in command for word in ['play', 'pause', 'stop', 'next', 'previous', 'volume'])

    def execute(self, command: str) -> str:
        try:
            if 'play' in command:
                if 'playlist' in command:
                    return self._handle_playlist(command)
                return self._handle_play(command)
            elif 'pause' in command:
                self.handler.music_controller.pause()
                return "Music paused."
            elif 'stop' in command:
                self.handler.music_controller.stop()
                return "Music stopped."
            elif 'next' in command:
                self.handler.music_controller.next_track()
                return "Playing next track."
            elif 'previous' in command:
                self.handler.music_controller.previous_track()
                return "Playing previous track."
            elif 'volume' in command:
                return self._handle_volume(command)
            return "I didn't understand that music command."
        except Exception as e:
            return f"Sorry, I couldn't control the music: {str(e)}"

    def _handle_play(self, command: str) -> str:
        try:
            # Extract song or artist name
            if 'by' in command:
                artist = command.split('by')[-1].strip()
                self.handler.music_controller.play_by_artist(artist)
                return f"Playing music by {artist}."
            else:
                song = command.replace('play', '').strip()
                if song:
                    self.handler.music_controller.play_song(song)
                    return f"Playing {song}."
                else:
                    self.handler.music_controller.play()
                    return "Resuming music playback."
        except Exception as e:
            return f"Failed to play music: {str(e)}"

    def _handle_playlist(self, command: str) -> str:
        try:
            playlist = command.replace('play playlist', '').strip()
            self.handler.music_controller.play_playlist(playlist)
            return f"Playing playlist: {playlist}."
        except Exception as e:
            return f"Failed to play playlist: {str(e)}"

    def _handle_volume(self, command: str) -> str:
        try:
            if 'up' in command:
                self.handler.music_controller.volume_up()
                return "Volume increased."
            elif 'down' in command:
                self.handler.music_controller.volume_down()
                return "Volume decreased."
            else:
                # Try to extract volume level
                words = command.split()
                for word in words:
                    if word.isdigit():
                        level = int(word)
                        if 0 <= level <= 100:
                            self.handler.music_controller.set_volume(level)
                            return f"Volume set to {level}%."
                return "Please specify a volume level between 0 and 100."
        except Exception as e:
            return f"Failed to adjust volume: {str(e)}"