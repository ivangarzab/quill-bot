"""
Tests for task scheduling utilities
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from datetime import datetime
import random
import pytz

from utils.schedulers import setup_scheduled_tasks
from utils.constants import READING_REMINDERS

class TestSchedulers(unittest.TestCase):
    """Test cases for task schedulers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bot = MagicMock()
        self.bot.config = MagicMock()
        self.bot.config.DEFAULT_CHANNEL = 12345
        
        # Mock channel
        self.mock_channel = MagicMock()
        self.bot.get_channel.return_value = self.mock_channel
        
        # Store the task
        self.reminder_task = None
        
        # Mock the tasks.loop decorator
        def mock_loop(**kwargs):
            def decorator(func):
                # Store the original function
                self.loop_func = func
                
                # Create a mock for the task
                mock_task = MagicMock()
                
                # Add a start method that calls the function once
                async def start_method():
                    await self.loop_func()
                
                mock_task.start = start_method
                self.reminder_task = mock_task
                
                return mock_task
            return decorator
        
        # Apply the patch
        self.loop_patcher = patch('discord.ext.tasks.loop', mock_loop)
        self.mock_loop = self.loop_patcher.start()
        
    def tearDown(self):
        """Clean up after tests"""
        self.loop_patcher.stop()
    
    @patch('random.random')
    @patch('utils.embeds.create_embed')
    async def test_reminder_message_sent(self, mock_create_embed, mock_random):
        """Test reminder message is sent at the right time with correct content"""
        # Configure random to trigger sending (0.3 < 0.4)
        mock_random.return_value = 0.3
        
        # Configure random choice for the reminder message
        with patch('random.choice', return_value="Have you read today?"):
            # Mock the embed
            mock_embed = MagicMock()
            mock_create_embed.return_value = mock_embed
            
            # Mock the time to be 5 PM Pacific
            mock_now = datetime(2025, 3, 22, 17, 0, 0)
            mock_now = pytz.timezone('US/Pacific').localize(mock_now)
            
            with patch('datetime.datetime') as mock_datetime:
                # Configure now to return our fixed time
                mock_datetime.now.return_value = mock_now
                
                # Configure timezone to work with our mock
                mock_datetime.now.side_effect = lambda tz=None: mock_now
                
                # Setup and run the task
                task = setup_scheduled_tasks(self.bot)
                await self.reminder_task.start()
                
                # Verify channel was retrieved
                self.bot.get_channel.assert_called_once_with(12345)
                
                # Verify embed was created with the right parameters
                mock_create_embed.assert_called_once()
                args, kwargs = mock_create_embed.call_args
                self.assertEqual(kwargs['title'], "📚 Daily Reading Reminder")
                self.assertEqual(kwargs['description'], "Have you read today?")
                self.assertEqual(kwargs['color_key'], "purp")
                
                # Verify the message was sent
                self.mock_channel.send.assert_called_once_with(embed=mock_embed)
    
    @patch('random.random')
    async def test_reminder_message_not_sent_wrong_time(self, mock_random):
        """Test reminder message is not sent at times other than 5 PM Pacific"""
        # Configure random to trigger sending if time was right
        mock_random.return_value = 0.3
        
        # Mock the time to be 3 PM Pacific (not 5 PM)
        mock_now = datetime(2025, 3, 22, 15, 0, 0)
        mock_now = pytz.timezone('US/Pacific').localize(mock_now)
        
        with patch('datetime.datetime') as mock_datetime:
            # Configure now to return our fixed time
            mock_datetime.now.return_value = mock_now
            
            # Configure timezone to work with our mock
            mock_datetime.now.side_effect = lambda tz=None: mock_now
            
            # Setup and run the task
            task = setup_scheduled_tasks(self.bot)
            await self.reminder_task.start()
            
            # Verify channel was NOT retrieved (task shouldn't run)
            self.bot.get_channel.assert_not_called()
            
            # Verify no message was sent
            self.mock_channel.send.assert_not_called()
    
    @patch('random.random')
    async def test_reminder_message_not_sent_random_check(self, mock_random):
        """Test reminder message is not sent when random check fails"""
        # Configure random to prevent sending (0.5 >= 0.4)
        mock_random.return_value = 0.5
        
        # Mock the time to be 5 PM Pacific
        mock_now = datetime(2025, 3, 22, 17, 0, 0)
        mock_now = pytz.timezone('US/Pacific').localize(mock_now)
        
        with patch('datetime.datetime') as mock_datetime:
            # Configure now to return our fixed time
            mock_datetime.now.return_value = mock_now
            
            # Configure timezone to work with our mock
            mock_datetime.now.side_effect = lambda tz=None: mock_now
            
            # Setup and run the task
            task = setup_scheduled_tasks(self.bot)
            await self.reminder_task.start()
            
            # Verify channel was NOT retrieved (random check failed)
            self.bot.get_channel.assert_not_called()
            
            # Verify no message was sent
            self.mock_channel.send.assert_not_called()
    
    @patch('random.random')
    @patch('random.choice')
    async def test_reminder_message_content(self, mock_choice, mock_random):
        """Test the content of reminder messages"""
        # Configure random to trigger sending
        mock_random.return_value = 0.3
        
        # Test with each reminder message
        for reminder in READING_REMINDERS:
            # Configure the random choice
            mock_choice.return_value = reminder
            
            # Reset the mocks
            self.bot.get_channel.reset_mock()
            self.mock_channel.send.reset_mock()
            
            # Mock the time to be 5 PM Pacific
            mock_now = datetime(2025, 3, 22, 17, 0, 0)
            mock_now = pytz.timezone('US/Pacific').localize(mock_now)
            
            with patch('datetime.datetime') as mock_datetime:
                # Configure now to return our fixed time
                mock_datetime.now.return_value = mock_now
                
                # Configure timezone to work with our mock
                mock_datetime.now.side_effect = lambda tz=None: mock_now
                
                # Setup and run the task
                task = setup_scheduled_tasks(self.bot)
                await self.reminder_task.start()
                
                # Verify the message was sent
                self.mock_channel.send.assert_called_once()
                
                # Verify the embed contains the right reminder
                args, kwargs = self.mock_channel.send.call_args
                embed = kwargs['embed']
                self.assertEqual(embed.description, reminder)

if __name__ == '__main__':
    unittest.main()