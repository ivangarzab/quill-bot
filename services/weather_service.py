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
    
    """
    Properly fixed version of the get_weather method
    """
    async def get_weather(self, location):
        """
        Get weather information for a given location
        
        Args:
            location (str): The city/location to get weather for
                
        Returns:
            str: Formatted weather information
        """
        print(f"Fetching weather for location: {location}")
        try:
            url = f"https://api.weatherbit.io/v2.0/current?city={location}&key={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract city name and weather data from response
            city_name = data['data'][0]['city_name']
            temp_c = data['data'][0]['temp']
            temp_f = (temp_c * 9/5) + 32
            description = data['data'][0]['weather']['description']
            
            message = (
                f"Current weather in **{city_name}**:\n"
                f"Temperature: **{temp_f:.1f}\u00b0F / {temp_c:.1f}\u00b0C**\n"
                f"Condition: **{description}**"
            )
            if "rain" in description.lower():
                message += "; and it is raining!"
            
            print(f"Weather fetched successfully: {message}")
            return message
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return f"Error getting weather for '{location}': {str(e)}"