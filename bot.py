"""
Core BookClubBot class, simplified to handle initialization and base setup
"""
import json
import discord
from discord.ext import commands

from config import BotConfig
from database import Database
from services.openai_service import OpenAIService
from utils.constants import DEFAULT_CHANNEL
from events.message_handler import setup_message_handlers
from utils.schedulers import setup_scheduled_tasks

class BookClubBot(commands.Bot):
    """Main bot class, significantly simplified from the original monolithic design"""
    def __init__(self):
        print("~~~~~~~~~~~~ Initializing BookClubBot... ~~~~~~~~~~~~")
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        # Load configuration
        self.config = BotConfig()
        
        # Initialize services
        self.db = Database()
        self.openai_service = OpenAIService(self.config.KEY_OPENAI)
        
        # Load club data
        self.load_session_details()
        
        # Register cogs
        self.load_cogs()
        
        # Setup message handlers
        setup_message_handlers(self)
        
    def load_session_details(self):
        """Load session details from the database."""
        self.club = self.db.get_club()

    async def setup_hook(self):
        """Setup hook called when bot is being prepared to connect"""
        await self.tree.sync()  # Sync slash commands
        setup_scheduled_tasks(self)
        self.loop.create_task(self.print_nickname())
    
    async def print_nickname(self):
        """Print nickname once bot is ready"""
        await self.wait_until_ready()
        for guild in self.guilds:
            nickname = guild.me.nick or guild.me.name
            print(f"~~~~~~~~~~~~ Instance initialized as '{nickname}' ~~~~~~~~~~~~\nwith metadata: \n{json.dumps(self.club, separators=(',', ':'))}")

    def load_cogs(self):
        """Load all command cogs"""
        from cogs.general_commands import setup_general_commands
        from cogs.session_commands import setup_session_commands
        from cogs.fun_commands import setup_fun_commands
        from cogs.utility_commands import setup_utility_commands
        
        # Setup commands directly on the command tree
        setup_general_commands(self)
        setup_session_commands(self)
        setup_fun_commands(self)
        setup_utility_commands(self)
        
        print("All commands loaded.")