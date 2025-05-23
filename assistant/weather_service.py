import os
import requests
from datetime import datetime

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.default_city = os.getenv('DEFAULT_CITY', 'London')
        self.units = os.getenv('WEATHER_UNITS', 'metric')
        self.offline_mode = not bool(self.api_key)  # Enable offline mode if no API key

    def get_current_weather(self, city=None):
        if self.offline_mode:
            return self._get_offline_weather(city or self.default_city)

        try:
            city = city or self.default_city
            if not self.api_key:
                return self._get_offline_weather(city)

            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Format weather information in a natural way
            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            response_text = f"In {city}, it's {weather_desc} with a temperature of {temp}°C. "
            response_text += f"The humidity is {humidity}% and wind speed is {wind_speed} meters per second."

            # Add weather advice
            if temp < 10:
                response_text += " You might want to wear warm clothes today."
            elif temp > 25:
                response_text += " Remember to stay hydrated in this warm weather."

            return response_text

        except requests.RequestException as e:
            return f"I'm sorry, I couldn't fetch the weather information. {str(e)}"

    def _get_offline_weather(self, city):
        # Provide a simulated response when in offline mode
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Simulate different weather conditions based on time of day
        if 5 <= current_hour < 12:
            temp = 18
            desc = "partly cloudy"
        elif 12 <= current_hour < 17:
            temp = 23
            desc = "mostly sunny"
        else:
            temp = 16
            desc = "clear"
            
        # Make sure city is not None
        city = city or self.default_city
            
        response = f"Since I'm in offline mode, I'll give you a simulated weather report for {city}. "
        response += f"It's currently {desc} with an approximate temperature of {temp}°C. "
        
        if temp < 20:
            response += "You might want to bring a light jacket."
        else:
            response += "It's quite pleasant outside."
            
        return response

    def get_daily_forecast(self, city=None):
        if self.offline_mode:
            return self._get_offline_weather(city or self.default_city)

        try:
            city = city or self.default_city
            if not self.api_key:
                return self._get_offline_weather(city)

            forecast_url = 'http://api.openweathermap.org/data/2.5/forecast'
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units
            }
            response = requests.get(forecast_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Get today's date
            today = datetime.now().date()
            forecast_text = f"Here's the forecast for {city}:\n"

            # Process only one forecast per day
            processed_dates = set()
            for item in data['list']:
                forecast_date = datetime.fromtimestamp(item['dt']).date()
                if forecast_date != today and forecast_date not in processed_dates:
                    processed_dates.add(forecast_date)
                    temp = item['main']['temp']
                    weather_desc = item['weather'][0]['description']
                    forecast_text += f"{forecast_date.strftime('%A')}: {weather_desc}, {temp}°C\n"

            return forecast_text

        except requests.RequestException as e:
            return f"I'm sorry, I couldn't fetch the forecast information. {str(e)}"