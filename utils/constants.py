"""
Constants used throughout the bot
"""
from discord import Color

# Default channel ID
DEFAULT_CHANNEL = 1327357851827572872

# Color schemes for different embed types
COLORS = {
    "success": Color.green(),
    "info": Color.blue(),
    "warning": Color.yellow(),
    "error": Color.red(),
    "fun": Color.orange(),
    "purp": Color.purple(),
    "royal": Color.gold(),
    "misc": Color.teal(),
    "blank": Color.dark_grey()
}

# Message templates
GREETINGS = ['I am Quill', '👀', 'Let\'s get reading!']
REACTIONS = ['⚡️', '👽', '🍄', '🌙', '🔥', '👾', '🦉', '🐺', '🍁']

# Fun facts for the funfact command
FUN_FACTS = [
    'Abibliophobia is the fear of running out of reading material.',
    'The Harvard University library has four law books bound in human skin.',
    'The Adventures of Tom Sawyer is the first book written with a typewriter.',
    'The name Wendy was made up for the book Peter Pan.',
    'People in Iceland read more books per capita than any other country.',
    'J.R.R. Tolkien typed the entire Lord of the Rings trilogy with two fingers.',
    'Up to 50 books can be made from 1 tree.',
    'Bibliosmia is the word for loving the smell of old books.'
]

# Fun fact closers
FACT_CLOSERS = [
    'Did you know? 🤓',
    'Riddle me this ❔❓',
    'Knowledge is power! 💡',
    'Now you know ‼️',
    'Food for thought! 🍎',
    'Curiosity never killed the bookworm! 🐛'
]

# Daily reading reminders
READING_REMINDERS = [
    'Try to read a minimum of 10 pages per day!',
    'Have you read today?',
    'How many pages have you read today?',
    'If you read 20 minutes a day, you would have read 1.8 million words in a year.',
    'Have you been reading? I\'m watching 🦉',
    'Books are portals to new worlds—have you stepped through one today? 🌍',
    'A chapter a day keeps the boredom away!',
    'Remember, even one page is progress! 📖',
    'Reading expands your mind. What did you learn today?',
    'Take a moment to escape reality with a book!',
    'A few pages a day builds a lifetime of knowledge.',
    'Consistency is key! 💪 Keep turning those pages.',
    'Your book is waiting for you—don\'t keep it lonely!',
    'Reading is self-care. ☯️ Take some time for yourself today!',
    'Every page you read brings you closer to your goal. 🎯'
]