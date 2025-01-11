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
        
    def setup_commands(self):
        @self.command()
        async def usage(ctx: commands.Context):
            commands_list = [
                "rolldice - Roll a six-sided die",
                "flipcoin - Flip a coin",
                "choose <options> - Choose from given options",
                "weather - Get SF weather",
                "currentBook - Show current book",
                "dueDate - Show due date",
                "currentSession - Show all session details"
            ]
            await ctx.send("**Current list of commands:**\n" + "\n".join(f"- {cmd}" for cmd in commands_list))
            
    async def get_weather(self) -> str:
        """Fetch current weather for San Francisco."""
        url = f"https://api.weatherbit.io/v2.0/current?city=San%20Francisco&state&country=US&key={self.KEY_WEATHER}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            temp_c = data['data'][0]['temp']
            temp_f = (temp_c * 9/5) + 32
            city = data['data'][0]['city_name']
            description = data['data'][0]['weather']['description']
            
            message = f"Current weather in {city}: {temp_f:.1f}°F ({description})"
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
            '10 pages a day!',
            'Have you read today?',
            'How many pages have you read today?',
            'If you read 20 minutes a day, you would have read 1.8 million words in a year.'
        ]
        
        sf_timezone = pytz.timezone('US/Pacific')
        now_pacific = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(sf_timezone)
        
        if now_pacific.hour == 17:
            channel = self.get_channel(self.DEFAULT_CHANNEL)
            if channel:
                await channel.send(random.choice(reminders))
                
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
        elif 'weather' in msg_content:
            weather = await self.get_weather()
            await message.channel.send(weather)
        elif 'question:' in msg_content:
            prompt = msg_content.split(':', 1)[1]
            response = await self.get_openai_response(prompt)
            await message.channel.send(response)
            
        # Random reactions
        if random.random() < 0.4:
            await message.add_reaction(random.choice(self.reactions))
            
        await self.process_commands(message)
            
    async def on_member_join(self, member: discord.Member):
        """Welcome new members."""
        channel = self.get_channel(self.DEFAULT_CHANNEL)
        if channel:
            greetings = ["Welcome", "Bienvenido", "Willkommen", "Bienvenue", "Bem-vindo", "Welkom", "Καλως"]
            await channel.send(f"{random.choice(greetings)}, {member.mention}!")

# Create and run bot
def main():
    bot = BookClubBot()
    bot.run(bot.TOKEN)

if __name__ == "__main__":
    main()