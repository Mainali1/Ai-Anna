from . import Command
import requests
import json
import os
from datetime import datetime

class WeatherCommand(Command):
    def __init__(self, handler):
        super().__init__(handler)
        self.api_key = os.getenv('WEATHER_API_KEY', '')
        if not self.api_key:
            print("Warning: WEATHER_API_KEY not found in environment variables")
            
    def validate(self, command: str) -> bool:
        return 'weather' in command.lower() or 'temperature' in command.lower() or 'forecast' in command.lower()
        
    def execute(self, command: str) -> str:
        try:
            # Extract location from command
            location = self._extract_location(command)
            if not location:
                location = "current location"  # Default to current location
                
            # Get weather data
            weather_data = self._get_weather(location)
            if not weather_data:
                return f"I couldn't get weather information for {location}."
                
            # Format response
            return self._format_weather_response(weather_data, location)
        except Exception as e:
            print(f"Error in weather command: {str(e)}")
            return f"I encountered an error getting weather information: {str(e)}"
            
    def _extract_location(self, command: str) -> str:
        # Extract location from command
        # Examples: "weather in New York", "what's the weather like in London"
        command = command.lower()
        if "in" in command:
            location = command.split("in")[-1].strip()
            return location
        elif "for" in command:
            location = command.split("for")[-1].strip()
            return location
        return ""
        
    def _get_weather(self, location: str) -> dict:
        if not self.api_key:
            return self._get_mock_weather(location)
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Weather API error: {response.status_code} - {response.text}")
                return self._get_mock_weather(location)
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return self._get_mock_weather(location)
            
    def _get_mock_weather(self, location: str) -> dict:
        # Return mock weather data for testing
        return {
            "name": location,
            "main": {
                "temp": 22,
                "feels_like": 23,
                "humidity": 65
            },
            "weather": [
                {
                    "main": "Clear",
                    "description": "clear sky"
                }
            ]
        }
        
    def _format_weather_response(self, data: dict, location: str) -> str:
        try:
            city = data.get("name", location)
            temp = data.get("main", {}).get("temp", "unknown")
            feels_like = data.get("main", {}).get("feels_like", "unknown")
            humidity = data.get("main", {}).get("humidity", "unknown")
            condition = data.get("weather", [{}])[0].get("main", "unknown")
            description = data.get("weather", [{}])[0].get("description", "unknown")
            
            return f"Weather in {city}: {temp}°C, feels like {feels_like}°C. Conditions: {description.capitalize()}. Humidity: {humidity}%."
        except Exception as e:
            print(f"Error formatting weather response: {str(e)}")
            return f"The weather in {location} is currently {data.get('main', {}).get('temp', 'unknown')}°C."