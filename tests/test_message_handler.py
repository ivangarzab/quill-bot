"""
Tests for message and event handlers
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import discord
import random

from events.message_handler import setup_message_handlers
from utils.constants import GREETINGS, REACTIONS

class TestMessageHandler(unittest.TestCase):
    """Test cases for message handler"""
    
    def setUp(self):
        """Set up common test fixtures"""
        self.bot = MagicMock()
        
        # Store event handlers
        self.handlers = {}
        
        # Mock the bot.event decorator
        def mock_event(func):
            # Store the event handler
            self.handlers[func.__name__] = func
            return func
        
        self.bot.event = mock_event
        
        # Set fixed random seed for predictable results
        random.seed(42)
        
        # Register the event handlers
        setup_message_handlers(self.bot)
        
        # Verify event handlers were registered
        self.assertIn('on_message', self.handlers)
        self.assertIn('on_member_join', self.handlers)

    async def test_on_message_from_bot(self):
        """Test message handler ignores bot's own messages"""
        # Create a message from the bot itself
        message = MagicMock()
        message.author = self.bot.user
        
        # Run the handler
        on_message = self.handlers['on_message']
        await on_message(message)
        
        # Verify nothing happened (no methods called on message)
        message.channel.send.assert_not_called()
        message.add_reaction.assert_not_called()

    async def test_on_message_with_bot_mention(self):
        """Test message handler responds to bot mentions"""
        # Create a message with bot mention
        message = MagicMock()
        message.author = MagicMock()  # Not the bot
        message.content = "Hey @bot, how are you?"
        message.mentions = [self.bot.user]
        
        # Force the random values for predictable testing
        with patch('random.random', return_value=0.2):  # 0.2 < 0.4, should send greeting
            # Run the handler
            on_message = self.handlers['on_message']
            await on_message(message)
            
            # Verify a greeting was sent
            message.channel.send.assert_called_once()
            args, _ = message.channel.send.call_args
            self.assertIn(args[0], GREETINGS)

    async def test_on_message_with_keyword(self):
        """Test message handler responds to keywords"""
        # Create a message with the 'together' keyword
        message = MagicMock()
        message.author = MagicMock()  # Not the bot
        message.content = "We should read together next week."
        message.mentions = []
        
        # Run the handler
        on_message = self.handlers['on_message']
        await on_message(message)
        
        # Verify the response was sent
        message.channel.send.assert_called_once_with('Reading is done best in community.')

    async def test_on_message_random_reaction(self):
        """Test message handler sometimes adds random reactions"""
        # Create a normal message
        message = MagicMock()
        message.author = MagicMock()  # Not the bot
        message.content = "I'm reading a great book."
        message.mentions = []
        
        # Force random value to trigger reaction (0.1 < 0.3)
        with patch('random.random', return_value=0.1):
            # Force a specific reaction choice
            with patch('random.choice', return_value="🦉"):
                # Run the handler
                on_message = self.handlers['on_message']
                await on_message(message)
                
                # Verify a reaction was added
                message.add_reaction.assert_called_once_with("🦉")

    async def test_on_member_join(self):
        """Test member join handler sends welcome message"""
        # Create a new member
        member = MagicMock()
        member.name = "NewUser"
        member.mention = "@NewUser"
        member.id = 12345
        
        # Mock the bot.get_channel method
        channel = MagicMock()
        self.bot.get_channel.return_value = channel
        
        # Force a specific greeting choice
        with patch('random.choice', return_value="Welcome"):
            # Run the handler
            on_member_join = self.handlers['on_member_join']
            await on_member_join(member)
            
            # Verify the welcome message was sent
            channel.send.assert_called_once()
            args, kwargs = channel.send.call_args
            self.assertIn('embed', kwargs)
            
            # Verify the embed has the correct properties
            embed = kwargs['embed']
            self.assertEqual(embed.title, "👋 New Member!")
            self.assertIn("Welcome", embed.description)
            self.assertIn("@NewUser", embed.description)
            
            # Verify the database was updated
            self.bot.db.save_club.assert_called_once()
            args, _ = self.bot.db.save_club.call_args
            club_data = args[0]
            self.assertEqual(club_data['name'], "Quill's Bookclub")
            self.assertEqual(len(club_data['members']), 1)
            self.assertEqual(club_data['members'][0]['id'], 12345)
            self.assertEqual(club_data['members'][0]['name'], "NewUser")

if __name__ == '__main__':
    unittest.main()