"""
Service for interfacing with weather API
"""
import requests

class WeatherService:
    """Service to handle weather API interactions"""
    
    def __init__(self, api_key):
        """
        Initialize the weather service
        
        Args:
            api_key (str): The weather API key
        """
        self.api_key = api_key
    
    async def get_weather(self, location):
        """
        Get weather information for a given location
        
        Args:
            location (str): The city/location to get weather for
            
        Returns:
            str: Formatted weather information
        """
        print(f"Fetching weather for location: {location}")
        url = f"https://api.weatherbit.io/v2.0/current?city={location}&key={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            temp_c = data['data'][0]['temp']
            temp_f = (temp_c * 9/5) + 32
            city = data['data'][0]['city_name']
            description = data['data'][0]['weather']['description']
            
            message = (
                f"Current weather in **{city}**:\n"
                f"Temperature: **{temp_f:.1f}\u00b0F / {temp_c:.1f}\u00b0C**\n"
                f"Condition: **{description}**"
            )
            if "rain" in description.lower():
                message += "; and it is raining!"
            print(f"Weather fetched successfully: {message}")
            return message
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return f"Error fetching weather: {str(e)}"