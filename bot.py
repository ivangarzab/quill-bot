"""
Core BookClubBot class, simplified to handle initialization and base setup
"""
import os
import json
import discord
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from discord.ext import commands

from config import BotConfig
from database import Database
from services.openai_service import OpenAIService
from utils.constants import DEFAULT_CHANNEL
from events.message_handler import setup_message_handlers
from utils.schedulers import setup_scheduled_tasks

class BookClubBot(commands.Bot):
    """Main bot class"""
    def __init__(self):
        print("[DEBUG] ~~~~~~~~~~~~ Initializing BookClubBot... ~~~~~~~~~~~~")
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

        # Setup logging
        self.setup_logging()
        self.logger.info("BookClubBot initialization started")
        
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
        """Load session details from the database"""
        self.club = self.db.get_club()

    async def setup_hook(self):
        """Setup hook called when bot is being prepared to connect"""
        await self.tree.sync()  # Sync slash commands
        setup_scheduled_tasks(self)
        self.loop.create_task(self.print_nickname())
        self.tree.on_error = self.on_command_error # Set up global error handler
        self.logger.info("Command error handler registered")
    
    async def print_nickname(self):
        """Print nickname once bot is ready"""
        await self.wait_until_ready()
        for guild in self.guilds:
            nickname = guild.me.nick or guild.me.name
            print(f"[DEBUG] ~~~~~~~~~~~~ Instance initialized as '{nickname}' ~~~~~~~~~~~~\nwith metadata: \n{json.dumps(self.club, separators=(',', ':'))}")

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
        
        print("All commands loaded")

    def setup_logging(self):
        """Set up logging with daily rotation"""
        import logging
        import os
        from datetime import datetime
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure basic logging
        logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_filename = f"logs/bot_{current_date}.log"
        
        # Configure file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(logging.Formatter(logging_format))
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(logging_format))
        
        # Get logger and configure
        logger = logging.getLogger('book_club_bot')
        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
        # Make logger available to the bot
        self.logger = logger
        self.logger.info("Logging system initialized")

    async def on_command_error(self, interaction, error):
        """Handle errors in application commands gracefully"""
        self.logger.error(f"Error in command {interaction.command.name if interaction.command else 'unknown'}: {error}")
        
        try:
            # If response hasn't been sent yet
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Something went wrong with that command. Please try again later.",
                    ephemeral=True
                )
            else:
                # If response was already sent, use followup
                await interaction.followup.send(
                    "Something went wrong completing that command.",
                    ephemeral=True
                )
        except Exception as e:
            # If responding fails, at least log it
            self.logger.error(f"Couldn't respond to interaction error: {e}")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle errors in events"""
        import traceback
        import sys
        
        self.logger.error(f"Error in event {event}")
        traceback_info = traceback.format_exc()
        self.logger.error(f"Traceback:\n{traceback_info}")
        
        # For critical errors, you might want to notify yourself
        if event == "on_ready" or event == "setup_hook":
            try:
                # Get a channel to send error notifications to
                channel = self.get_channel(self.DEFAULT_CHANNEL)
                if channel:
                    await channel.send("⚠️ The bot encountered a critical error. Please check the logs.")
            except:
                # If this fails, at least we tried
                pass