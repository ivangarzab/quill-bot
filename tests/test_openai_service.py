"""
Tests for OpenAI service
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from services.openai_service import OpenAIService

class TestOpenAIService(unittest.TestCase):
    """Test cases for OpenAI service"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        
        # Create a mock for the OpenAIClient
        with patch('airobot.OpenAIClient') as mock_client_class:
            self.mock_client = MagicMock()
            mock_client_class.return_value = self.mock_client
            self.openai_service = OpenAIService(self.api_key)
            
            # Verify the client was initialized with the correct API key
            mock_client_class.assert_called_once_with(self.api_key)

    def test_init(self):
        """Test service initialization"""
        # Already tested in setUp, but we can add more assertions if needed
        self.assertEqual(self.openai_service.api_key, self.api_key)
        self.assertIsNotNone(self.openai_service.client)

    @patch('builtins.print')
    def test_get_response_success(self, mock_print):
        """Test getting a successful response from OpenAI"""
        # Mock the client's create_chat_completion method
        self.mock_client.create_chat_completion.return_value = "This is a test response from OpenAI"
        
        # Call the method under test
        response = asyncio.run(self.openai_service.get_response("What is the meaning of life?"))
        
        # Verify the client was called with the right parameters
        self.mock_client.create_chat_completion.assert_called_once()
        args = self.mock_client.create_chat_completion.call_args[0][0]
        self.assertEqual(len(args), 1)
        self.assertEqual(args[0]["role"], "user")
        self.assertEqual(args[0]["content"], "What is the meaning of life?")
        
        # Verify the response is correct
        self.assertEqual(response, "This is a test response from OpenAI")
        
    @patch('builtins.print')
    def test_get_response_value_error(self, mock_print):
        """Test handling a ValueError during API call"""
        # Mock the client to raise a ValueError
        self.mock_client.create_chat_completion.side_effect = ValueError("Invalid API key")
        
        # Call the method under test
        response = asyncio.run(self.openai_service.get_response("Test prompt"))
        
        # Verify the client was called
        self.mock_client.create_chat_completion.assert_called_once()
        
        # Verify we get the expected error message
        self.assertEqual(response, "I'm having trouble accessing my AI services right now.")
        
    @patch('builtins.print')
    def test_get_response_general_exception(self, mock_print):
        """Test handling a general exception during API call"""
        # Mock the client to raise a general exception
        self.mock_client.create_chat_completion.side_effect = Exception("Network error")
        
        # Call the method under test
        response = asyncio.run(self.openai_service.get_response("Test prompt"))
        
        # Verify the client was called
        self.mock_client.create_chat_completion.assert_called_once()
        
        # Verify we get the expected error message
        self.assertEqual(response, "I encountered an error while processing your request.")
        
    @patch('builtins.print')
    def test_get_response_empty_prompt(self, mock_print):
        """Test sending an empty prompt"""
        # Call the method with an empty prompt
        response = asyncio.run(self.openai_service.get_response(""))
        
        # The service should still try to get a response
        self.mock_client.create_chat_completion.assert_called_once()
        
    @patch('builtins.print')
    def test_get_response_none_returned(self, mock_print):
        """Test handling None returned from the API client"""
        # Mock the client to return None
        self.mock_client.create_chat_completion.return_value = None
        
        # Call the method under test
        response = asyncio.run(self.openai_service.get_response("Test prompt"))
        
        # Verify the response is as expected
        self.assertEqual(response, "I couldn't generate a response at this time. Please try again later.")

if __name__ == '__main__':
    unittest.main()