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
        Get weather information for a given location with improved error handling
        
        Args:
            location (str): The city/location to get weather for
            
        Returns:
            str: Formatted weather information or error message
        """
        print(f"Fetching weather for location: {location}")
        try:
            url = f"https://api.weatherbit.io/v2.0/current?city={location}&key={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()  # Raises exception for 4XX/5XX responses
            
            data = response.json()
            # Process data as before...
            
            # Format message
            message = (
                f"Current weather in **{city}**:\n"
                f"Temperature: **{temp_f:.1f}\u00b0F / {temp_c:.1f}\u00b0C**\n"
                f"Condition: **{description}**"
            )
            if "rain" in description.lower():
                message += "; and it is raining!"
            
            print(f"Weather fetched successfully: {message}")
            return message
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error fetching weather: {str(e)}")
            # More specific error based on status code
            if e.response.status_code == 401:
                return f"Error: Weather service authentication failed."
            elif e.response.status_code == 404:
                return f"Could not find weather data for '{location}'."
            else:
                return f"Weather service error: {e.response.status_code}"
        except requests.exceptions.ConnectionError:
            print(f"Connection error fetching weather")
            return f"Could not connect to weather service. Please try again later."
        except requests.exceptions.Timeout:
            print(f"Timeout fetching weather")
            return f"Weather service timed out. Please try again later."
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return f"Error getting weather for '{location}': {str(e)}"