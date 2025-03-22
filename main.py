import os
import json
import random
import discord
from discord import app_commands, Color
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta
import pytz
import calendar
import requests
from typing import List, Optional
# from dotenv import load_dotenv
from database import Database
from airobot import OpenAIClient

class BookClubBot(commands.Bot):
    def __init__(self):
        print("~~~~~~~~~~~~ Initializing BookClubBot... ~~~~~~~~~~~~")
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)

        # load_dotenv(override=True)
        
        # Configuration
        self.DEFAULT_CHANNEL = 1327357851827572872

        self.ENV = os.getenv("ENV")
        if self.ENV == "dev":
            print("~~~~~~~~~~~~ Running in development mode ~~~~~~~~~~~~")
            self.TOKEN = os.getenv("DEV_TOKEN")
        else:
            self.TOKEN = os.getenv("TOKEN")
        
        print(f"[DEBUG] TOKEN: {'SET' if self.TOKEN else 'NOT SET'}")
        self.KEY_WEATHER = os.getenv("KEY_WEATHER")
        print(f"[DEBUG] KEY_WEATHER: {'SET' if self.KEY_WEATHER else 'NOT SET'}")
        self.KEY_OPENAI = os.getenv("KEY_OPEN_AI")
        print(f"[DEBUG] KEY_OPENAI: {'SET' if self.KEY_OPENAI else 'NOT SET'}")
        
        # Initialize database
        self.db = Database()
        self.load_session_details()

        # Initialize OpenAI client
        self.openai = OpenAIClient(self.KEY_OPENAI)
        
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

    def load_session_details(self):
        """Load session details from the database."""
        self.club = self.db.get_club()

    async def print_nickname(self):
        await self.wait_until_ready()
        for guild in self.guilds:
            nickname = guild.me.nick or guild.me.name
            print(f"~~~~~~~~~~~~ Instance initialized as '{nickname}' ~~~~~~~~~~~~\nwith metadata: \n{json.dumps(self.club, separators=(',', ':'))}")

    async def setup_hook(self):
        await self.tree.sync()  # Sync slash commands
        self.send_reminder_message.start()
        self.loop.create_task(self.print_nickname())
        
    async def get_weather(self, location: str) -> str:
        """Fetch current weather for a given location."""
        print(f"Fetching weather for location: {location}")
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
            print(f"Weather fetched successfully: {message}")
            return message
        except Exception as e:
            print(f"Error fetching weather: {str(e)}")
            return f"Error fetching weather: {str(e)}"

    @tasks.loop(hours=1)
    async def send_reminder_message(self):
        """Send daily reading reminders."""
        reminders = [
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
        
        sf_timezone = pytz.timezone('US/Pacific')
        now_pacific = datetime.now(tz=sf_timezone)
        
        if now_pacific.hour == 17 and random.random() < 0.4:
            # if it is 5PM Pacific time
            channel = self.get_channel(self.DEFAULT_CHANNEL)
            if channel:
                embed = discord.Embed(
                    title="📚 Daily Reading Reminder",
                    description=random.choice(reminders),
                    color=self.colors["purp"]
                )
                await channel.send(embed=embed)
                print("Reminder message sent.")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        if message.author == self.user:
            return
            
        print(f"Received message: {message.content}\n\tfrom: {message.author}\n\tin: {message.channel}\n\tat: {message.guild}")
        msg_content = message.content.lower()
        
        # Handle mentions
        if self.user in message.mentions:
            if random.random() < 0.4:
                await message.channel.send(random.choice(self.greetings))
                print("Sent greeting message.")
            elif random.random() > 0.5:
                await message.add_reaction(random.choice(self.reactions))
                print("Added reaction to message.")
                
        # Handle keywords
        if 'together' in msg_content:
            await message.channel.send('Reading is done best in community.')
            
        # Random reactions
        if not message.content.startswith('!') and random.random() < 0.3:
            await message.add_reaction(random.choice(self.reactions))
            
        await self.process_commands(message)

    async def on_member_join(self, member: discord.Member):
        """Welcome new members."""
        print(f"New member joined: {member.name}")
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
        
        # Save new member to the database
        self.db.save_club({
            "id": 0,  # Assuming club_id is 0
            "name": "Quill's Bookclub",
            "members": [{"id": member.id, "name": member.name, "points": 0, "number_of_books_read": 0}]
        })

    def setup_commands(self):
        print("Setting up slash commands...")
        
        @self.tree.command(name="help", description="Show help prompt")
        async def help(interaction: discord.Interaction):
            embed = discord.Embed(
                title="🦉 Quill's Orientation",
                description="Greetings human!  I'm here to help you with all things about our book club.",
                color=self.colors["info"]
            )

            embed.add_field(
                name=" How to use ❓",
                value="You can execute `/usage` to see all available commands.\n\nHere's a few more commands to get you started.",
                inline=False
            )

            embed.add_field(
                name="📖 Reading Commands",
                value="• `/session` - Show all session details\n"
                      "• `/book` - Show current book details\n"
                      "• `/duedate` - Show the session's due date\n"
                      "• `/discussions` - Show the session's discussion details",
                inline=False
            )

            embed.set_footer(text=f"Hope this helps! ✌️")
            await interaction.response.send_message(embed=embed)
            print("Sent help command response.")
        
        @self.tree.command(name="usage", description="Show all available commands")
        async def usage(interaction: discord.Interaction):
            embed = discord.Embed(
                title="📚 Quill's Commands",
                description="Here's everything I can help you with!",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="📖 Reading Commands",
                value="• `/session` - Show all session details\n"
                      "• `/book` - Show current book details\n"
                      "• `/duedate` - Show the session's due date\n"
                      "• `/discussions` - Show the session's discussion details",
                inline=False
            )
            
            embed.add_field(
                name="🎲 Fun Commands",
                value="• `/rolldice` - Roll a six-sided die\n"
                      "• `/flipcoin` - Flip a coin\n"
                      "• `/choose` - Choose from given options",
                inline=False
            )
            
            embed.add_field(
                name="🌤 Utility Commands",
                value="• `/weather <city>` - Get the city weather\n"
                      "• `/funfact` - Get a random book-related fact",
                inline=False
            )
            
            embed.set_footer(text=f"*Use / to access all commands!*")
            await interaction.response.send_message(embed=embed)
            print("Sent usage command response.")

        @self.tree.command(name="book", description="Show current book details")
        async def book(interaction: discord.Interaction):
            embed = discord.Embed(
                title="📚 Current Book",
                description=f"**{self.club['activeSession']['book']['title']}**",
                color=self.colors["info"]
            )
            embed.add_field(name="Author", value=f"{self.club['activeSession']['book']['author']}")
            embed.set_footer(text="Happy reading! 📖")
            await interaction.response.send_message(embed=embed)
            print("Sent book command response.")

        @self.tree.command(name="duedate", description="Show the session's due date")
        async def duedate(interaction: discord.Interaction):
            embed = discord.Embed(
                title="📅 Due Date",
                description=f"Session due date: **{self.club['activeSession']['dueDate']}**",
                color=self.colors["warning"]
            )
            await interaction.response.send_message(embed=embed)
            print("Sent duedate command response.")

        @self.tree.command(name="session", description="Show current session details")
        async def session(interaction: discord.Interaction):
            embed = discord.Embed(
                title="📚 Current Session Details",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="Book",
                value=f"{self.club['activeSession']['book']['title']}",
                inline=True
            )
            
            embed.add_field(
                name="Author",
                value=f"{self.club['activeSession']['book']['author']}",
                inline=True
            )
            
            embed.add_field(
                name="Due Date",
                value=f"{self.club['activeSession']['dueDate']}",
                inline=False
            )
            
            embed.set_footer(text="Keep reading! 📖")
            await interaction.response.send_message(embed=embed)
            print("Sent session command response.")

        @self.tree.command(name="discussions", description="Show the session's discussion details")
        async def discussions(interaction: discord.Interaction):
            embed = discord.Embed(
                title="📚 Book Discussion Details",
                color=self.colors["info"]
            )
            
            embed.add_field(
                name="Number of Discussions",
                value=f"#{len(self.club['activeSession']['discussions'])}",
                inline=False
            )
            
            embed.add_field(
                name="Next discussion",
                value=f"{self.club['activeSession']['discussions'][0]['date']}",
                inline=False
            )
            
            embed.set_footer(text="Don't stop reading! 📖")
            await interaction.response.send_message(embed=embed)
            print("Sent discussions command response.")

        @self.tree.command(name="weather", description="Get the weather for a specific city")
        @app_commands.describe(location="The city to get weather for")
        async def weather(interaction: discord.Interaction, location: str):
            print(f"Weather command received for location: {location}")
            await interaction.response.defer()  # Defer the response since weather API call might take time
            
            weather_info = await self.get_weather(location)
            embed = discord.Embed(
                title=f"🌤 Weather for {location.title()}",
                description=weather_info,
                color=self.colors["info"]
            )
            
            sf_timezone = pytz.timezone('US/Pacific')
            embed.timestamp = datetime.now(tz=sf_timezone)
            embed.set_footer(text="Weather information last updated")
            
            await interaction.followup.send(embed=embed)
            print("Sent weather command response.")

        @self.tree.command(name="funfact", description="Get a random book-related fun fact")
        async def funfact(interaction: discord.Interaction):
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
            await interaction.response.send_message(embed=embed)
            print("Sent funfact command response.")

        @self.tree.command(name="choose", description="I will choose from the options you give me")
        @app_commands.describe(options="Space-separated options to choose from")
        async def choose(interaction: discord.Interaction, options: str):
            choices = options.split()
            if not choices:
                await interaction.response.send_message("Please provide some options to choose from!", ephemeral=True)
                return
                
            result = random.choice(choices)
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
            await interaction.response.send_message(embed=embed)
            print("Sent choose command response.")

        @self.tree.command(name="rolldice", description="I will roll a six-sided die")
        async def rolldice(interaction: discord.Interaction):
            result = random.randint(1, 6)
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"You rolled a **{result}**!",
                color=self.colors["fun"]
            )
            await interaction.response.send_message(embed=embed)
            print("Sent rolldice command response.")

        @self.tree.command(name="flipcoin", description="Flip a coin")
        async def flipcoin(interaction: discord.Interaction):
            result = random.choice(["HEADS", "TAILS"])
            embed = discord.Embed(
                title="🪙 Coin Flip",
                description=f"You got **{result}**!",
                color=self.colors["fun"]
            )
            await interaction.response.send_message(embed=embed)
            print("Sent flipcoin command response.")

        @self.tree.command(name="book_summary", description="Let me provide a summary of the active book")
        async def booksummary(interaction: discord.Interaction):
            """Ask OpenAI for a summary of the active book."""
            response = await self.get_openai_response(f"What is {self.club['activeSession']['book']['title']} about?")
            embed = discord.Embed(
                title="🤖 Book Summary",
                description=response,
                color=self.colors["info"]
            )
            await interaction.response.send_message(embed=embed)
            print("Sent flipcoin command response.")

        @self.command()
        async def robot(ctx: commands.Context, *, prompt: str):
            """Make prompt to OpenAI."""
            response = await self.get_openai_response(prompt)
            embed = discord.Embed(
                title="🤖 Robot Response",
                description=response,
                color=self.colors["blank"]
            )
            await ctx.send(embed=embed)

    async def get_openai_response(self, prompt: str) -> str:
        """Get response from OpenAI API."""
        print(f"Fetching OpenAI response for prompt: {prompt}")
        try:
            messages = [
                {"role": "user", "content": f"{prompt}"}
            ]
            response = self.openai.create_chat_completion(messages)
            if response:
                print("GPT-3.5 Response:", response)
            else:
                print("Failed to get response after all retries")
            return response
        except ValueError as e:
            print(f"Configuration error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

def main():
    print("~~~~~~~~~~~~ Starting BookClubBot... ~~~~~~~~~~~~")
    bot = BookClubBot()
    bot.run(bot.TOKEN)

if __name__ == "__main__":
    main()