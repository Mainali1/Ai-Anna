import json
import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self):
        self.config_file = Path("config.json")
        self.default_config = {
            "ai_services": {
                "timeout": 30,
                "max_retries": 3
            },
            "study": {
                "session_duration": 25,
                "break_duration": 5
            },
            "security": {
                "allowed_paths": [],
                "blocked_paths": []
            }
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
            return self.default_config
        except Exception:
            return self.default_config

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value