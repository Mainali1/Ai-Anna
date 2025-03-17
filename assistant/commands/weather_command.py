from . import Command
from typing import Optional

class WeatherCommand(Command):
    def validate(self, command: str) -> bool:
        # Only validate weather-related queries
        weather_keywords = ['weather', 'temperature', 'forecast', 'humidity']
        time_keywords = ['time', "what's the time", 'what time']
        
        # Check if command is specifically about weather or time
        is_weather_query = any(word in command for word in weather_keywords)
        is_time_query = any(phrase in command for phrase in time_keywords)
        
        return is_weather_query or is_time_query

    def execute(self, command: str) -> str:
        try:
            if any(word in command for word in ['time', "what's the time", 'what time']):
                from datetime import datetime
                current_time = datetime.now().strftime('%I:%M %p')
                return f"The current time is {current_time}."
            elif 'forecast' in command:
                return self._handle_forecast(command)
            return self._handle_current_weather(command)
        except Exception as e:
            return f"Sorry, I couldn't get the weather information: {str(e)}"

    def _handle_current_weather(self, command: str) -> str:
        try:
            # Extract location if provided
            location = None
            if 'in' in command:
                location = command.split('in')[-1].strip()
            
            # The weather service now returns a formatted string
            return self.handler.weather_service.get_current_weather(location)
        except Exception as e:
            return f"Failed to get current weather: {str(e)}"

    def _handle_forecast(self, command: str) -> str:
        try:
            # Extract location and time period if provided
            location = None
            if 'in' in command:
                location = command.split('in')[-1].strip()
            
            # The weather service now returns a formatted string
            return self.handler.weather_service.get_daily_forecast(location)
        except Exception as e:
            return f"Failed to get forecast: {str(e)}"