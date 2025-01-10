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

DEFAULT_CHANNEL = 1288337522027401256
# Get the TOKEN from the environment variable
TOKEN = os.getenv("TOKEN")
KEY_WEATHER = os.getenv("KEY_WEATHER")
KEY_OPENAI = os.getenv("KEY_OPEN_AI")

if not TOKEN:
    raise ValueError("TOKEN environment variable is not set.")
print(f'~~~~~~Got Discord TOKEN={TOKEN}~~~~~~')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'~~~~~~We have logged in as {client.user}~~~~~~')
    if not send_reminder_message.is_running():
      print(f'~~~~~~Starting send_reminder_message() tasks~~~~~~')
      send_reminder_message.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return # Avoid the bot responding to itself
    
    author = message.author.mention
    msgFormat = message.content.lower()
    allowed_mentions = discord.AllowedMentions(everyone = True)

    print(f'Got a new message=\'{message.content}\'\n\tguild={message.guild}\n\tauthor={message.author.name}')

    phillGreetings = [f'I am Phill', '👀']
    phillGreetReactions = [f'🙃', f'👽', f'🍄', f'🌙', f'🔥', f'🎗️']
    jeremyShouts = [f"I think Jeremy is cool", f"Listen to your professors!"]

    # The message to be sent out to the message.channel
    messageToSend = ""

    if client.user in message.mentions:
      go = random.randint(1, 10)
      if go < 4:
        messageToSend = random.choice(phillGreetings)
      elif go > 5:
        reaction = random.choice(phillGreetReactions)
        print(f"Adding reaction to message: {reaction}")
        await message.add_reaction(reaction)

    # Jeremy responses, and his quotes
    if 'jeremy' in msgFormat:
      go = random.randint(1, 2)
      if go == 1:
        messageToSend = random.choice(jeremyShouts)
    ### Philosophy is done best in community
    if 'together' in message.content:
      messageToSend = f'Philosophy is done best in community.\n\t\t-Jeremy Reid'
    if 'someone wants' in msgFormat:
      messageToSend = f'Philosophy is done best in community.\n\t\t-Jeremy Reid'
    if 'who wants' in msgFormat:
      messageToSend = f'Philosophy is done best in community.\n\t\t-Jeremy Reid'
    if 'share' in msgFormat:
      go = random.randint(1, 2)
      if go == 1:
        messageToSend = f'Philosophy is done best in community.\n\t\t-Jeremy Reid'
    
    # Papers
    if 'final paper' in msgFormat:
      messageToSend = f'Good papers grow themselves.'
    if 'papers' in msgFormat:
      messageToSend = f'Good papers grow themselves.'

    # Command redirects
    if 'weather' in msgFormat:
      messageToSend = get_weather()

    if 'question:' in msgFormat:
      prompt = msgFormat.split(':')[1]
      messageToSend = get_openai_response(prompt)

    # Only send messageToSend if the string is not empty
    if messageToSend:
      print(f"Sending message: {messageToSend}")
      await message.channel.send(messageToSend)

    # This line is necessary to process commands within on_message()
    await client.process_commands(message) 
    
@client.event
async def on_member_join(member):
    println(f"{member} joined")
    channel = client.get_channel(DEFAULT_CHANNEL)
    if not channel:
        return
    await channel.send(f"Welcome to PHIL 715, {member}!")

def get_weather():
    url = f"https://api.weatherbit.io/v2.0/current?city=San%20Francisco&state&country=US&key={KEY_WEATHER}"
    response = requests.get(url)
    data = response.json()
    temperature_celsius = data['data'][0]['temp']
    temperature_fahrenheit = (temperature_celsius * 9/5) + 32
    city = data['data'][0]['city_name']
    description = data['data'][0]['weather']['description']
    is_raining = "rain" in description.lower()
    message = f"Current weather in {city}: {temperature_fahrenheit:.1f}°F ({description})"
    if is_raining:
      message += "; and it is raining!"
    return message

############################# REMINDER MESSAGES #############################
# Define the async task running every hour that will send reminder messages
@tasks.loop(hours=1)
async def send_reminder_message():
  print(f'~~~~~~Running send_reminder_message()~~~~~~')
  # Create a timezone object for UTC
  utc_timezone = pytz.timezone('UTC')
  # Define the SF timezone (Pacific Standard Time)
  sf_timezone = pytz.timezone('US/Pacific')
  now_utc = datetime.utcnow()
  # Convert UTC time to LA time
  now_pacific = now_utc.replace(tzinfo=pytz.utc).astimezone(sf_timezone)
  # Check if it's Tuesday for the wishing good luck in class
  if now_pacific.weekday() == calendar.TUESDAY:
    if now_pacific.hour == 15: # Check if current hour matches target hour
      channel = client.get_channel(DEFAULT_CHANNEL)
      if channel:
        await channel.send("Have fun in class!")
  # Check if it's Monday for the homework reminder
  elif now_pacific.weekday() == calendar.MONDAY:
    if now_pacific.hour == 20: # Check if current hour matches target hour
      channel = client.get_channel(DEFAULT_CHANNEL)
      if channel:
        await channel.send("Don't forget to submit in your homework tonight!")
  else:
    print(f"Ran send_reminder_message() at {now_pacific}, but there's nothing to shout.")

############################# CUSTOM COMMANDS #############################
@client.command()
async def rolldice(ctx: commands.Context):
    print(f"Got a rolldice command")
    result = random.randint(1, 6)
    await ctx.send(f"You rolled a {result}!")

@client.command()
async def flipcoin(ctx: commands.Context):
    print(f"Got a flipcoin command")
    result = random.choice(["HEADS", "TAILS"])
    await ctx.send(f"You flipped a coin and got {result}!")

@client.command()
async def choose(ctx: commands.Context, *, argments):
    print(f"Got a choose command")
    options = argments.split(" ")
    result = random.choice(options)
    print(f"Selected result: {result}")
    rand = random.randint(1, 3)
    if rand == 1:
      await ctx.send(f"{result}, I choose you!")
    elif rand == 2:
      await ctx.send(f"I have selected {result}")
    else:
      await ctx.send(f"The winner is, {result}")

@client.command()
async def weather(ctx: commands.Context):
    print(f"Got a weather command")
    weather = get_weather()
    print(f"~~~{weather}~~~")
    await ctx.send(weather)

################################# OPENAI ##################################
def get_openai_response(prompt):
    openai.api_key = KEY_OPENAI
    response = openai.Completion.create(
      engine="gpt-3.5-turbo-0125",
      prompt=prompt,
      max_tokens=150  # Limits the length of the generated response
    )
    return response.choices[0].text



################################ EXEC INIT ################################
client.run(TOKEN) # Run the bot with your bot token
