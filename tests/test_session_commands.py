"""
Tests for session commands (book, duedate, session, discussions)
"""
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from cogs.session_commands import setup_session_commands
from utils.embeds import create_embed

class TestSessionCommands(unittest.TestCase):
    """Test cases for session commands"""
    
    def setUp(self):
        """Set up common test fixtures"""
        # Create a mock bot
        self.bot = MagicMock()
        self.bot.tree = MagicMock()
        
        # Create mock club data
        self.bot.club = {
            'name': 'Test Book Club',
            'activeSession': {
                'id': 'session-1',
                'book': {
                    'title': 'Test Book Title',
                    'author': 'Test Author'
                },
                'dueDate': '2025-05-01',
                'discussions': [
                    {
                        'id': 'discussion-1',
                        'date': '2025-04-15',
                        'title': 'First Discussion'
                    }
                ]
            }
        }
        
        # Set up mock for OpenAI service
        self.bot.openai_service = MagicMock()
        self.bot.openai_service.get_response = AsyncMock(return_value="This is a test book summary.")
        
        # Store the registered commands
        self.commands = {}
        
        # Mock the bot.tree.command decorator
        def mock_command(**kwargs):
            def decorator(func):
                # Store the command and its properties
                self.commands[kwargs.get('name')] = {
                    'func': func,
                    'kwargs': kwargs
                }
                return func
            return decorator
        
        self.bot.tree.command = mock_command
        
        # Register the commands
        setup_session_commands(self.bot)
        
        # Verify commands were registered
        self.assertIn('book', self.commands)
        self.assertIn('duedate', self.commands)
        self.assertIn('session', self.commands)
        self.assertIn('discussions', self.commands)
        self.assertIn('book_summary', self.commands)

    @patch('utils.embeds.create_embed')
    async def test_book_command(self, mock_create_embed):
        """Test the book command"""
        # Mock an interaction
        interaction = AsyncMock()
        interaction.response = AsyncMock()
        
        # Mock the embed creation
        mock_embed = MagicMock()
        mock_create_embed.return_value = mock_embed
        
        # Run the command
        book_command = self.commands['book']['func']
        await book_command(interaction)
        
        # Verify the embed was created with the right parameters
        mock_create_embed.assert_called_once()
        args, kwargs = mock_create_embed.call_args
        self.assertEqual(kwargs['title'], "📚 Current Book")
        self.assertEqual(kwargs['description'], "**Test Book Title**")
        self.assertEqual(kwargs['color_key'], "info")
        
        # Verify fields contain book info
        fields = kwargs.get('fields', [])
        self.assertTrue(any(field['name'] == 'Author' and field['value'] == 'Test Author' for field in fields))
        
        # Verify footer
        self.assertEqual(kwargs['footer'], "Happy reading! 📖")
        
        # Verify the interaction response was sent
        interaction.response.send_message.assert_called_once_with(embed=mock_embed)

    @patch('utils.embeds.create_embed')
    async def test_duedate_command(self, mock_create_embed):
        """Test the duedate command"""
        # Mock an interaction
        interaction = AsyncMock()
        interaction.response = AsyncMock()
        
        # Mock the embed creation
        mock_embed = MagicMock()
        mock_create_embed.return_value = mock_embed
        
        # Run the command
        duedate_command = self.commands['duedate']['func']
        await duedate_command(interaction)
        
        # Verify the embed was created with the right parameters
        mock_create_embed.assert_called_once()
        args, kwargs = mock_create_embed.call_args
        self.assertEqual(kwargs['title'], "📅 Due Date")
        self.assertEqual(kwargs['description'], "Session due date: **2025-05-01**")
        self.assertEqual(kwargs['color_key'], "warning")
        
        # Verify the interaction response was sent
        interaction.response.send_message.assert_called_once_with(embed=mock_embed)

    @patch('utils.embeds.create_embed')
    async def test_session_command(self, mock_create_embed):
        """Test the session command"""
        # Mock an interaction
        interaction = AsyncMock()
        interaction.response = AsyncMock()
        
        # Mock the embed creation
        mock_embed = MagicMock()
        mock_create_embed.return_value = mock_embed
        
        # Run the command
        session_command = self.commands['session']['func']
        await session_command(interaction)
        
        # Verify the embed was created with the right parameters
        mock_create_embed.assert_called_once()
        args, kwargs = mock_create_embed.call_args
        self.assertEqual(kwargs['title'], "📚 Current Session Details")
        self.assertEqual(kwargs['color_key'], "info")
        
        # Verify fields contain book info, author, and due date
        fields = kwargs.get('fields', [])
        self.assertTrue(any(field['name'] == 'Book' and field['value'] == 'Test Book Title' for field in fields))
        self.assertTrue(any(field['name'] == 'Author' and field['value'] == 'Test Author' for field in fields))
        self.assertTrue(any(field['name'] == 'Due Date' and field['value'] == '2025-05-01' for field in fields))
        
        # Verify footer
        self.assertEqual(kwargs['footer'], "Keep reading! 📖")
        
        # Verify the interaction response was sent
        interaction.response.send_message.assert_called_once_with(embed=mock_embed)

    @patch('utils.embeds.create_embed')
    async def test_discussions_command(self, mock_create_embed):
        """Test the discussions command"""
        # Mock an interaction
        interaction = AsyncMock()
        interaction.response = AsyncMock()
        
        # Mock the embed creation
        mock_embed = MagicMock()
        mock_create_embed.return_value = mock_embed
        
        # Run the command
        discussions_command = self.commands['discussions']['func']
        await discussions_command(interaction)
        
        # Verify the embed was created with the right parameters
        mock_create_embed.assert_called_once()
        args, kwargs = mock_create_embed.call_args
        self.assertEqual(kwargs['title'], "📚 Book Discussion Details")
        self.assertEqual(kwargs['color_key'], "info")
        
        # Verify fields contain discussion info
        fields = kwargs.get('fields', [])
        self.assertTrue(any(field['name'] == 'Number of Discussions' and field['value'] == '#1' for field in fields))
        self.assertTrue(any(field['name'] == 'Next discussion' and field['value'] == '2025-04-15' for field in fields))
        
        # Verify footer
        self.assertEqual(kwargs['footer'], "Don't stop reading! 📖")
        
        # Verify the interaction response was sent
        interaction.response.send_message.assert_called_once_with(embed=mock_embed)

    @patch('utils.embeds.create_embed')
    async def test_book_summary_command(self, mock_create_embed):
        """Test the book_summary command"""
        # Mock an interaction
        interaction = AsyncMock()
        interaction.response = AsyncMock()
        
        # Mock the embed creation
        mock_embed = MagicMock()
        mock_create_embed.return_value = mock_embed
        
        # Run the command
        book_summary_command = self.commands['book_summary']['func']
        await book_summary_command(interaction)
        
        # Verify OpenAI service was called with the book title
        self.bot.openai_service.get_response.assert_called_once()
        args, _ = self.bot.openai_service.get_response.call_args
        self.assertIn("Test Book Title", args[0])
        
        # Verify the embed was created with the right parameters
        mock_create_embed.assert_called_once()
        args, kwargs = mock_create_embed.call_args
        self.assertEqual(kwargs['title'], "🤖 Book Summary")
        self.assertEqual(kwargs['description'], "This is a test book summary.")
        self.assertEqual(kwargs['color_key'], "info")
        
        # Verify the interaction response was sent
        interaction.response.send_message.assert_called_once_with(embed=mock_embed)

if __name__ == '__main__':
    unittest.main()