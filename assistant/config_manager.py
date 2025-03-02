import json
import os

class ConfigManager:
    def __init__(self):
        self.config_file = 'config.json'
        self.default_config = {
            'offline_mode': False,
            'voice_response': True,
            'beep_sound': False,
            'wake_phrase': "Anna ready",
            'music_path': "~/Music",
            'speech_rate': 150,
            'voice_gender': 'female'
        }
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file) as f:
                self.config = {**self.default_config, **json.load(f)}
        except FileNotFoundError:
            self.config = self.default_config
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value