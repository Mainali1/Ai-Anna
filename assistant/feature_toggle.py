import json
import os

class FeatureToggleManager:
    def __init__(self, container=None):
        self.container = container
        self.logger = container.get_service('logger') if container else None
        self.config_manager = container.get_service('config_manager') if container else None
        
        # Default features and their states
        self.default_features = {
            "voice_control": True,
            "sound_effects": True,
            "ai_mode": True,
            "web_browser": True,
            "google_search": True,
            "news_service": True,
            "weather_service": True,
            "file_system": True,
            "email_integration": True,
            "screen_analysis": True,
            "flashcards": True,
            "pomodoro_timer": True,
            "assignments": True,
            "schedule": True,
            "media_controls": True
        }
        
        # Load features from config
        self.features = self.load_features()
        
    def load_features(self):
        """Load feature toggles from config"""
        if self.config_manager:
            config = self.config_manager.config
            features = config.get('features', self.default_features)
        else:
            # If no config manager, try to load from file
            features_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'features.json')
            try:
                if os.path.exists(features_file):
                    with open(features_file, 'r') as f:
                        features = json.load(f)
                else:
                    features = self.default_features
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error loading features: {str(e)}")
                features = self.default_features
        
        # Ensure all default features exist
        for feature, default_state in self.default_features.items():
            if feature not in features:
                features[feature] = default_state
                
        return features
    
    def save_features(self):
        """Save feature toggles to config"""
        if self.config_manager:
            config = self.config_manager.config
            config['features'] = self.features
            self.config_manager.save_config()
        else:
            # If no config manager, save to file
            features_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'features.json')
            try:
                os.makedirs(os.path.dirname(features_file), exist_ok=True)
                with open(features_file, 'w') as f:
                    json.dump(self.features, f, indent=4)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error saving features: {str(e)}")
    
    def is_enabled(self, feature):
        """Check if a feature is enabled"""
        return self.features.get(feature, False)
    
    def enable_feature(self, feature):
        """Enable a feature"""
        if feature in self.features:
            self.features[feature] = True
            self.save_features()
            return f"Feature '{feature}' has been enabled."
        else:
            return f"Feature '{feature}' does not exist."
    
    def disable_feature(self, feature):
        """Disable a feature"""
        if feature in self.features:
            self.features[feature] = False
            self.save_features()
            return f"Feature '{feature}' has been disabled."
        else:
            return f"Feature '{feature}' does not exist."
    
    def toggle_feature(self, feature):
        """Toggle a feature on/off"""
        if feature in self.features:
            self.features[feature] = not self.features[feature]
            self.save_features()
            status = "enabled" if self.features[feature] else "disabled"
            return f"Feature '{feature}' has been {status}."
        else:
            return f"Feature '{feature}' does not exist."
    
    def get_all_features(self):
        """Get all features and their states"""
        return self.features
    
    def get_enabled_features(self):
        """Get all enabled features"""
        return {feature: state for feature, state in self.features.items() if state}
    
    def get_disabled_features(self):
        """Get all disabled features"""
        return {feature: state for feature, state in self.features.items() if not state}
    
    def reset_to_defaults(self):
        """Reset all features to their default states"""
        self.features = self.default_features.copy()
        self.save_features()
        return "All features have been reset to their default states."