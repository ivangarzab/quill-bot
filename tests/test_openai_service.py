"""
Tests for bot error handling functionality
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import discord
import logging
import os
from datetime import datetime

class TestErrorHandling(unittest.TestCase):
    """Test cases for bot error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock bot
        self.bot = MagicMock()
        self.bot.logger = MagicMock()
        
        # Mock objects for interaction testing
        self.interaction = AsyncMock()
        self.interaction.command = MagicMock()
        self.interaction.command.name = "test_command"
        self.interaction.response = AsyncMock()
        self.interaction.response.is_done = MagicMock(return_value=False)
        self.interaction.followup = AsyncMock()
        
    def test_setup_logging(self):
        """Test logging setup"""
        # Create a temporary directory for logs
        test_log_dir = "test_logs"
        os.makedirs(test_log_dir, exist_ok=True)
        
        try:
            # Import the actual setup_logging method
            from bot import BookClubBot
            bot_instance = BookClubBot.__new__(BookClubBot)  # Create instance without calling __init__
            
            # Patch os.makedirs to avoid creating real directories
            with patch('os.makedirs') as mock_makedirs:
                # Patch logging configuration to avoid side effects
                with patch('logging.getLogger') as mock_get_logger:
                    with patch('logging.FileHandler') as mock_file_handler:
                        mock_logger = MagicMock()
                        mock_get_logger.return_value = mock_logger
                        
                        # Call the method
                        bot_instance.setup_logging()
                        
                        # Verify logger was configured
                        mock_get_logger.assert_called_once_with('book_club_bot')
                        mock_logger.setLevel.assert_called_once_with(logging.INFO)
                        mock_logger.addHandler.assert_called()
                        
                        # Verify logger was stored on the bot
                        self.assertEqual(bot_instance.logger, mock_logger)
        finally:
            # Clean up test directory
            import shutil
            if os.path.exists(test_log_dir):
                shutil.rmtree(test_log_dir)
    
    @patch('logging.FileHandler')
    @patch('logging.Formatter')
    def test_log_rotation(self, mock_formatter, mock_file_handler):
        """Test log file rotation by date"""
        # Create a test logger
        logger = logging.getLogger('test_logger')
        
        # Import and run the function directly
        from bot import BookClubBot
        bot_instance = BookClubBot.__new__(BookClubBot)  # Create instance without calling __init__
        
        # Create expected filename based on current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        expected_filename = f"logs/bot_{current_date}.log"
        
        # Run the function with patched components
        with patch('os.makedirs'):
            with patch('logging.getLogger', return_value=logger):
                bot_instance.setup_logging()
                
                # Verify file handler was created with expected filename
                mock_file_handler.assert_called()
                args, kwargs = mock_file_handler.call_args
                self.assertEqual(args[0], expected_filename)
    
    async def test_on_command_error(self):
        """Test the command error handler"""
        # Create a simulated error
        error = discord.app_commands.CommandInvokeError(Exception("Test error"))
        
        # Import the actual method
        from bot import BookClubBot
        bot_instance = BookClubBot.__new__(BookClubBot)  # Create instance without calling __init__
        bot_instance.logger = MagicMock()
        
        # Run the error handler
        await bot_instance.on_command_error(self.interaction, error)
        
        # Verify error was logged
        bot_instance.logger.error.assert_called()
        
        # Verify user was notified
        self.interaction.response.send_message.assert_called_once()
        args, kwargs = self.interaction.response.send_message.call_args
        self.assertIn("went wrong", args[0])
        self.assertTrue(kwargs.get('ephemeral', False))
    
    async def test_on_command_error_with_response_done(self):
        """Test error handling when response is already sent"""
        # Create a simulated error
        error = discord.app_commands.CommandInvokeError(Exception("Test error"))
        
        # Mock response already sent
        self.interaction.response.is_done.return_value = True
        
        # Import the actual method
        from bot import BookClubBot
        bot_instance = BookClubBot.__new__(BookClubBot)  # Create instance without calling __init__
        bot_instance.logger = MagicMock()
        
        # Run the error handler
        await bot_instance.on_command_error(self.interaction, error)
        
        # Verify error was logged
        bot_instance.logger.error.assert_called()
        
        # Verify followup was used
        self.interaction.response.send_message.assert_not_called()
        self.interaction.followup.send.assert_called_once()
    
    async def test_on_command_error_with_exception(self):
        """Test error handling when responding raises an exception"""
        # Create a simulated error
        error = discord.app_commands.CommandInvokeError(Exception("Test error"))
        
        # Make response throw an exception
        self.interaction.response.send_message.side_effect = Exception("Failed to respond")
        
        # Import the actual method
        from bot import BookClubBot
        bot_instance = BookClubBot.__new__(BookClubBot)  # Create instance without calling __init__
        bot_instance.logger = MagicMock()
        
        # Run the error handler
        await bot_instance.on_command_error(self.interaction, error)
        
        # Verify both errors were logged
        self.assertEqual(bot_instance.logger.error.call_count, 2)

if __name__ == '__main__':
    unittest.main()