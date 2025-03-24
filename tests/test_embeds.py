"""
Tests for embed utility functions
"""
import unittest
from unittest.mock import patch, MagicMock
import discord
from datetime import datetime
import pytz

# Import the module to test
from utils.embeds import create_embed
from utils.constants import COLORS

class TestEmbeds(unittest.TestCase):
    """Test cases for embed creation utilities"""

    def test_create_embed_minimal(self):
        """Test creating an embed with minimal parameters"""
        # Call the function with just the required parameters
        embed = create_embed("Test Title")
        
        # Assert that the embed has the expected properties
        self.assertEqual(embed.title, "Test Title")
        self.assertIsNone(embed.description)
        self.assertEqual(embed.color, COLORS["info"])  # Default color
        self.assertIsNone(embed.footer.text)
        
    def test_create_embed_full(self):
        """Test creating an embed with all parameters"""
        # Call the function with all parameters
        embed = create_embed(
            title="Full Test",
            description="This is a test description",
            color_key="error",
            fields=[
                {"name": "Field 1", "value": "Value 1", "inline": True},
                {"name": "Field 2", "value": "Value 2", "inline": False}
            ],
            footer="Test Footer",
            timestamp=True
        )
        
        # Assert that the embed has the expected properties
        self.assertEqual(embed.title, "Full Test")
        self.assertEqual(embed.description, "This is a test description")
        self.assertEqual(embed.color, COLORS["error"])
        self.assertEqual(embed.footer.text, "Test Footer")
        
        # Check fields
        self.assertEqual(len(embed.fields), 2)
        self.assertEqual(embed.fields[0].name, "Field 1")
        self.assertEqual(embed.fields[0].value, "Value 1")
        self.assertTrue(embed.fields[0].inline)
        self.assertEqual(embed.fields[1].name, "Field 2")
        self.assertEqual(embed.fields[1].value, "Value 2")
        self.assertFalse(embed.fields[1].inline)
        
        # Verify timestamp exists (exact value depends on test execution time)
        self.assertIsNotNone(embed.timestamp)
    
    def test_create_embed_custom_color(self):
        """Test creating an embed with a custom color"""
        # Test each color key
        for color_key in COLORS.keys():
            embed = create_embed("Color Test", color_key=color_key)
            self.assertEqual(embed.color, COLORS[color_key])
            
    def test_create_embed_invalid_color(self):
        """Test creating an embed with an invalid color key"""
        # Call with invalid color key - should default to "info"
        embed = create_embed("Invalid Color", color_key="not_a_real_color")
        self.assertEqual(embed.color, COLORS["info"])
        
    def test_create_embed_fields(self):
        """Test creating an embed with various field configurations"""
        # Case 1: No fields
        embed1 = create_embed("No Fields")
        self.assertEqual(len(embed1.fields), 0)
        
        # Case 2: One field
        embed2 = create_embed("One Field", fields=[
            {"name": "Single Field", "value": "Single Value"}
        ])
        self.assertEqual(len(embed2.fields), 1)
        self.assertEqual(embed2.fields[0].name, "Single Field")
        self.assertEqual(embed2.fields[0].value, "Single Value")
        self.assertFalse(embed2.fields[0].inline)  # Default should be False
        
        # Case 3: Multiple fields with mixed inline settings
        embed3 = create_embed("Multiple Fields", fields=[
            {"name": "Field 1", "value": "Value 1", "inline": True},
            {"name": "Field 2", "value": "Value 2", "inline": False},
            {"name": "Field 3", "value": "Value 3"}  # No inline specified
        ])
        self.assertEqual(len(embed3.fields), 3)
        self.assertTrue(embed3.fields[0].inline)
        self.assertFalse(embed3.fields[1].inline)
        self.assertFalse(embed3.fields[2].inline)  # Should default to False
    
    @patch('utils.embeds.datetime')
    def test_timestamp_timezone(self, mock_datetime):
        """Test that timestamp uses the correct timezone"""
        # Create a mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Set up the mock to return our datetime when called with the timezone
        mock_datetime.now.side_effect = lambda tz=None: mock_now
        
        # Create embed with timestamp
        embed = create_embed("Timestamp Test", timestamp=True)
        
        # Verify datetime.now was called with a timezone parameter
        mock_datetime.now.assert_called_once()
        args, kwargs = mock_datetime.now.call_args
        self.assertIn('tz', kwargs)
        
        # Verify the timezone is a tzinfo object
        self.assertTrue(hasattr(kwargs['tz'], 'zone'))
        
        # Verify the timezone is US/Pacific
        self.assertEqual(kwargs['tz'].zone, 'US/Pacific')
        
        # Verify the timestamp was set on the embed
        self.assertIsNotNone(embed.timestamp)

if __name__ == '__main__':
    unittest.main()