import os
import random
import discord
from discord import Color
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
            },
            "discussions": {
                "amount": 3,
                "frequency": "End of month, for 3 months",
                "expectation": "3 chapters per session"
            }
        }
        
        # Color schemes for different embed types
        self.colors = {
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
        self.greetings = ['I am Quill', '👀', 'Let\'s get reading!']
        self.reactions = ['⚡️', '👽', '🍄', '🌙', '🔥', '👾', '🦉', '🐺', '🍁']
        
        # Validate configuration
        if not self.TOKEN:
            raise ValueError("TOKEN environment variable is not set.")
            
        # Register commands
        self.setup_commands()

    async def setup_hook(self):
        self.send_reminder_message.start()
        
    async def get_weather(self, location: str) -> str:
        """Fetch current weather for a given location."""
        url = f"https://api.weatherbit.io/v2.0/current?city={location}&key={self.KEY_WEATHER}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            temp_c = data['data'][0]['temp']
            temp_f = (temp_c * 9/5) + 32
            city = data['data'][0]['city_name']
            description = data['data'][0]['weather']['description']
            
            message = (
                f"Current weather in **{city}**:\n"
                f"Temperature: **{temp_f:.1f}\u00b0F / {temp_c:.1f}\u00b0C**\n"
                f"Condition: **{description}**"
            )
            if "rain" in description.lower():
                message += "; and it is raining!"
            return message
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
            
    async def get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI API."""
        try:
            openai.api_key = self.KEY_OPENAI
            response = openai.Completion.create(
                engine="gpt-3.5-turbo-0125",
                prompt=prompt,
                max_tokens=150
            )
            return response.choices[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    @tasks.loop(hours=1)
    async def send_reminder_message(self):
        """Send daily reading reminders."""
        reminders = [
            'Try to read a mininum of 10 pages per day!',
            'Have you read today?',
            'How many pages have you read today?',
            'If you read 20 minutes a day, you would have read 1.8 million words in a year.',
            'Have you read? I\'m watching 🦉'
        ]
        
        sf_timezone = pytz.timezone('US/Pacific')
        now_pacific = datetime.now(tz=sf_timezone)
        
        if now_pacific.hour == 17:
            channel = self.get_channel(self.DEFAULT_CHANNEL)
            if channel:
                embed = discord.Embed(
                    title="📚 Daily Reading Reminder",
                    description=random.choice(reminders),
                    color=self.colors["purp"]
                )
                await channel.send(embed=embed)

    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        if message.author == self.user:
            return
            
        msg_content = message.content.lower()
        
        # Handle mentions
        if self.user in message.mentions:
            if random.random() < 0.4:
                await message.channel.send(random.choice(self.greetings))
            elif random.random() > 0.5:
                await message.add_reaction(random.choice(self.reactions))
                
        # Handle keywords
        if 'together' in msg_content:
            await message.channel.send('Reading is done best in community.')
        # Half-command menat to reach ChatGTP
        elif 'question:' in msg_content:
            prompt = msg_content.split(':', 1)[1]
            response = await self.get_openai_response(prompt)
            embed = discord.Embed(
                title="🤔 Question Response",
                description=response,
                color=self.colors["blank"]
            )
            await message.channel.send(embed=embed)
            
        # Random reactions
        if not message.content.startswith('!') and random.random() < 0.4:
            await message.add_reaction(random.choice(self.reactions))
            
        await self.process_commands(message)

    async def on_member_join(self, member: discord.Member):
        """Welcome new members."""
        channel = self.get_channel(self.DEFAULT_CHANNEL)
        if channel:
            greetings = ["Welcome", "Bienvenido", "Willkommen", "Bienvenue", "Bem-vindo", "Welkom", "Καλως"]
            embed = discord.Embed(
                title="👋 New Member!",
                description=f"{random.choice(greetings)}, {member.mention}!",
                color=self.colors["success"]
            )
            embed.set_footer(text="Welcome to the Book Club!")
            await channel.send(embed=embed)
            
    def setup_commands(self):
        @self.command()
        async def usage(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Quill's Commands",
                description="Here's everything I can help you with!",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="📖 Reading Commands",
                value="• `!session` - Show all session details\n"
                      "• `!book` - Show current book details\n"
                      "• `!duedate` - Show the session's due date\n"
                      "• `!discussions` - Show the session's discussion details",
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
                value="• `!weather <city>` - Get the city weather\n"
                      "• `!funfact` - Get a random book-related fact",
                inline=False
            )
            
            embed.set_footer(text="All commands start with !")
            await ctx.send(embed=embed)

        @self.command()
        async def choose(ctx: commands.Context, *, arguments):
            options = arguments.split()
            result = random.choice(options)
            responses = [
                f"**{result}**, I choose you!",
                f"I have selected **{result}**.",
                f"**{result}**. I have spoken.",
                f"The winner is: **{result}**!"
            ]
            
            embed = discord.Embed(
                title="🎯 Choice Made",
                description=random.choice(responses),
                color=self.colors["fun"]
            )
            await ctx.send(embed=embed)

        @self.command()
        async def book(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Current Book",
                description=f"**{self.session['book']['title']}**",
                color=self.colors["info"]
            )
            embed.add_field(name="Author", value=self.session['book']['author'])
            embed.set_footer(text="Happy reading! 📖")
            await ctx.send(embed=embed)

        @self.command()
        async def duedate(ctx: commands.Context):
            embed = discord.Embed(
                title="📅 Due Date",
                description=f"Session due date: **{self.session['due_date']}**",
                color=self.colors["warning"]
            )
            await ctx.send(embed=embed)

        @self.command()
        async def session(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Current Session Details",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="Session Number",
                value=f"#{self.session['number']}",
                inline=False
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
        async def discussions(ctx: commands.Context):
            embed = discord.Embed(
                title="📚 Book Discussion Details",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="Number of Discussions",
                value=f"#{self.session['discussions']['amount']}",
                inline=False
            )
            
            embed.add_field(
                name="Approximate Date",
                value=f"{self.session['discussions']['frequency']}",
                inline=False
            )
            
            embed.add_field(
                name="Progress Expectation",
                value=f"{self.session['discussions']['expectation']}",
                inline=False
            )
            
            embed.set_footer(text="Don't stop reading! 📖")
            await ctx.send(embed=embed)

        @self.command()
        async def weather(ctx: commands.Context, *, location: str):
            weather_info = await self.get_weather(location)
            
            embed = discord.Embed(
                title=f"\ud83c\udf24 Weather for {location.title()}",
                description=weather_info,
                color=self.colors["info"]
            )
            
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
            closers = [
              'Did you know? 🤓',
              'Riddle me this ❔❓',
              'Knowledge is power! 💡',
              'Now you know ‼️',
              'Food for thought! 🍎',
              'Curiosity never killed the bookworm! 🐛'
            ]
            
            embed = discord.Embed(
                title="📚 Book Fun Fact",
                description=random.choice(facts),
                color=self.colors["purp"]
            )
            embed.set_footer(text=random.choice(closers))
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

def main():
    bot = BookClubBot()
    bot.run(bot.TOKEN)

if __name__ == "__main__":
    main()