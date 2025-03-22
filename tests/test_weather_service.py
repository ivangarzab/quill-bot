"""
Tests for weather service
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import asyncio

from services.weather_service import WeatherService

class TestWeatherService(unittest.TestCase):
    """Test cases for weather service"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.weather_service = WeatherService(self.api_key)
        
        # Sample API response data
        self.mock_response_data = {
            "data": [
                {
                    "city_name": "San Francisco",
                    "temp": 15.5,  # Celsius
                    "weather": {
                        "description": "Partly cloudy"
                    }
                }
            ]
        }
        
        # Response with rain
        self.mock_rain_response_data = {
            "data": [
                {
                    "city_name": "Seattle",
                    "temp": 12.0,  # Celsius
                    "weather": {
                        "description": "Light rain"
                    }
                }
            ]
        }

    @patch('requests.get')
    def test_get_weather_success(self, mock_get):
        """Test getting weather information successfully"""
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_response_data
        mock_get.return_value = mock_response
        
        # Call the method being tested using the event loop
        result = asyncio.run(self.weather_service.get_weather("San Francisco"))
        
        # Verify the API was called with the correct parameters
        mock_get.assert_called_once()
        url = mock_get.call_args[0][0]
        self.assertIn("city=San Francisco", url)  # Without URL encoding
        self.assertIn(f"key={self.api_key}", url)
        
        # Verify the response formatting
        self.assertIn("Current weather in **San Francisco**", result)
        self.assertIn("**59.9°F / 15.5°C**", result)  # Verify temperature conversion
        self.assertIn("**Partly cloudy**", result)
        self.assertNotIn("it is raining", result.lower())  # No rain in this response

    @patch('requests.get')
    def test_get_weather_with_rain(self, mock_get):
        """Test getting weather information with rain condition"""
        # Configure the mock for a rainy response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_rain_response_data
        mock_get.return_value = mock_response
        
        # Call the method being tested using the event loop
        result = asyncio.run(self.weather_service.get_weather("Seattle"))
        
        # Verify response includes the rain message
        self.assertIn("Current weather in **Seattle**", result)
        self.assertIn("**53.6°F / 12.0°C**", result)
        self.assertIn("**Light rain**", result)
        self.assertIn("it is raining", result.lower())  # Should mention rain

    @patch('requests.get')
    def test_get_weather_network_error(self, mock_get):
        """Test handling network errors"""
        # Configure the mock to raise an exception
        mock_get.side_effect = Exception("Network error")
        
        # Call the method being tested using the event loop
        result = asyncio.run(self.weather_service.get_weather("Chicago"))
        
        # Verify error handling
        self.assertIn("Error fetching weather", result)
        self.assertIn("Network error", result)

    @patch('requests.get')
    def test_get_weather_invalid_response(self, mock_get):
        """Test handling invalid API responses"""
        # Configure the mock to return a response with missing data
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}  # Empty data array
        mock_get.return_value = mock_response
        
        # This should raise an exception in the weather service
        # Call the method being tested using the event loop
        result = asyncio.run(self.weather_service.get_weather("InvalidCity"))
        
        # Verify error handling for invalid response format
        self.assertIn("Error fetching weather", result)

if __name__ == '__main__':
    unittest.main()