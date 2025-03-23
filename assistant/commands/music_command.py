from . import Command
from typing import Optional

class MediaCommand(Command):
    def validate(self, command: str) -> bool:
        return any(word in command for word in ['play', 'pause', 'stop', 'next', 'previous', 'volume', 'media'])

    def execute(self, command: str) -> str:
        try:
            # Check if we should toggle control mode
            if 'system media' in command or 'browser media' in command:
                is_system = self.handler.music_controller.toggle_control_mode()
                mode = "system/browser" if is_system else "local"
                return f"Switched to {mode} media control mode."
                
            # Handle dynamic media commands
            if 'play' in command:
                if 'playlist' in command:
                    return self._handle_playlist(command)
                return self._handle_play(command)
            elif 'pause' in command:
                self.handler.music_controller.pause()
                return "Media paused."
            elif 'stop' in command:
                self.handler.music_controller.stop()
                return "Media stopped."
            elif 'next' in command:
                self.handler.music_controller.next_track()
                return "Playing next track."
            elif 'previous' in command:
                self.handler.music_controller.previous_track()
                return "Playing previous track."
            elif 'volume' in command:
                return self._handle_volume(command)
            return "I didn't understand that media command."
        except Exception as e:
            return f"Sorry, I couldn't control the media: {str(e)}"

    def _handle_play(self, command: str) -> str:
        try:
            # Extract media or artist name
            if 'by' in command:
                artist = command.split('by')[-1].strip()
                self.handler.music_controller.play_by_artist(artist)
                return f"Playing media by {artist}."
            else:
                media = command.replace('play', '').strip()
                if media:
                    self.handler.music_controller.play_media(media)
                    return f"Playing {media}."
                else:
                    self.handler.music_controller.play()
                    return "Resuming media playback."
        except Exception as e:
            return f"Failed to play media: {str(e)}"

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