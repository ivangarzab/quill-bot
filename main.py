import os
import random
import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
import calendar
import requests
import openai
from typing import List, Optional

class BookClubBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        # Configuration
        self.DEFAULT_CHANNEL = 1327357851827572872
        self.TOKEN = os.getenv("TOKEN")
        self.KEY_WEATHER = os.getenv("KEY_WEATHER")
        self.KEY_OPENAI = os.getenv("KEY_OPEN_AI")
        
        # Session details (TODO: Move to database)
        self.session = {
            "number": 0,
            "due_date": "End of MARCH!",
            "book": {
                "title": "Farenheit 451",
                "author": "Ray Bradbury"
            }
        }
        
        # Color schemes for different embed types
        self.colors = {
            "success": discord.Color.green(),
            "info": discord.Color.blue(),
            "warning": discord.Color.yellow(),
            "error": discord.Color.red(),
            "fun": discord.Color.purple()
        }
        
        # Message templates
        self.greetings = ['I am Quill', '👀', 'Let\'s get reading!']
        self.reactions = ['⚡️', '👽', '🍄', '🌙', '🔥', '👾', '🦉', '🐺', '🍁']
        
        # Validate configuration
        if not self.TOKEN:
            raise ValueError("TOKEN environment variable is not set.")
            
        # Register commands
        self.setup_commands()
        
    def setup_commands(self):
        @self.command()
        async def usage(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Book Club Bot Commands",
                description="Here's everything I can help you with!",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="📖 Reading Commands",
                value="• `!currentBook` - Show current book\n"
                      "• `!dueDate` - Show due date\n"
                      "• `!currentSession` - Show all session details",
                inline=False
            )
            
            embed.add_field(
                name="🎲 Fun Commands",
                value="• `!rolldice` - Roll a six-sided die\n"
                      "• `!flipcoin` - Flip a coin\n"
                      "• `!choose <options>` - Choose from given options",
                inline=False
            )
            
            embed.add_field(
                name="🌤 Utility Commands",
                value="• `!weather` - Get SF weather\n"
                      "• `!funfact` - Get a random book-related fact",
                inline=False
            )
            
            embed.set_footer(text="All commands start with !")
            await ctx.send(embed=embed)

        @self.command()
        async def currentBook(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Current Book",
                description=f"**{self.session['book']['title']}**",
                color=self.colors["info"]
            )
            embed.add_field(name="Author", value=self.session['book']['author'])
            embed.set_footer(text="Happy reading! 📖")
            await ctx.send(embed=embed)

        @self.command()
        async def currentSession(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Current Session Details",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="Session Number",
                value=f"#{self.session['number']}",
                inline=True
            )
            
            embed.add_field(
                name="Book",
                value=f"{self.session['book']['title']}",
                inline=True
            )
            
            embed.add_field(
                name="Author",
                value=f"{self.session['book']['author']}",
                inline=True
            )
            
            embed.add_field(
                name="Due Date",
                value=f"{self.session['due_date']}",
                inline=False
            )
            
            embed.set_footer(text="Keep reading! 📖")
            await ctx.send(embed=embed)

        @self.command()
        async def weather(ctx: commands.Context):
            weather_info = await self.get_weather()
            
            embed = discord.Embed(
                title="🌤 San Francisco Weather",
                description=weather_info,
                color=self.colors["info"]
            )
            
            # Add timestamp to show when the weather was checked
            embed.timestamp = datetime.utcnow()
            embed.set_footer(text="Weather information last updated")
            
            await ctx.send(embed=embed)

        @self.command()
        async def funfact(ctx: commands.Context):
            facts = [
                'Abibliophobia is the fear of running out of reading material.',
                'The Harvard University library has four law books bound in human skin.',
                'The Adventures of Tom Sawyer is the first book written with a typewriter.',
                'The name Wendy was made up for the book Peter Pan.',
                'People in Iceland read more books per capita than any other country.',
                'J.R.R. Tolkien typed the entire Lord of the Rings trilogy with two fingers.',
                'Up to 50 books can be made from 1 tree.',
                'Bibliosmia is the word for loving the smell of old books.'
            ]
            
            embed = discord.Embed(
                title="📚 Book Fun Fact",
                description=random.choice(facts),
                color=self.colors["fun"]
            )
            embed.set_footer(text="Did you know? 🤓")
            await ctx.send(embed=embed)

        @self.command()
        async def rolldice(ctx: commands.Context):
            result = random.randint(1, 6)
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"You rolled a **{result}**!",
                color=self.colors["fun"]
            )
            await ctx.send(embed=embed)

        @self.command()
        async def flipcoin(ctx: commands.Context):
            result = random.choice(["HEADS", "TAILS"])
            embed = discord.Embed(
                title="🪙 Coin Flip",
                description=f"You got **{result}**!",
                color=self.colors["fun"]
            )
            await ctx.send(embed=embed)

# Create and run bot
def main():
    bot = BookClubBot()
    bot.run(bot.TOKEN)

if __name__ == "__main__":
    main()