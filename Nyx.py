import os
import discord
import asyncio
import database
import exphandler
from discord.ext import commands
from dotenv import load_dotenv


# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.check
async def is_registered(ctx):
    """Global check to ensure user exists in the database before using any command."""
    if ctx.command.name == "helloNyx":  # ✅ Allow this command to run for everyone
        return True
    user_id = str(ctx.author.id)  # Convert to string since database uses TEXT for User_id
    if not database.is_user(user_id):  
        await ctx.send(f"{ctx.author.mention}, You are not friend with Nyx! Say `!helloNyx` to get started.")
        return False  # Deny command execution
    return True  # Allow execution if user exists

"""Functions"""



"""Bot Events"""
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Suppress the error so it doesn’t spam the terminal
        return
    raise error  # Only log actual errors

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(f"Received message: {message.content}") 
    await bot.process_commands(message)
    # await message.channel.send(f"{message.author.name} sent a message,the message was {message.content}") 
    await exphandler.give_exp(message.author.id)
    
"""Bot Commands"""

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# @bot.command()
# async def hello(ctx):
#     await ctx.send("Hy I'm Nyx ✨,Do you wanna be friends")
#      # Importing asyncio for handling async operations like waiting for messages

@bot.command()  # This decorator registers a command for the bot (!helloNyx)
async def helloNyx(ctx):  
    
    # Send a message asking if the user wants to be friends
    await ctx.send(f"Hy {ctx.author.mention} ✨, Do you wanna be friends? (yes/no)")

    # Function to check if the user's response is valid
    def check(msg):  
        return (
            msg.author == ctx.author  # Ensure the reply is from the same user who ran the command
            and msg.channel == ctx.channel  # Ensure the reply is in the same channel
            and msg.content.lower() in ["yes", "no"]  # Only accept "yes" or "no" (case insensitive)
        )

    try:
        # Wait for a valid response from the user within 30 seconds
        msg = await bot.wait_for("message", check=check, timeout=30.0)

        # If the user replied "yes"
        if msg.content.lower() == "yes":  
            
            user_id=str(ctx.author.id)
            if( database.check_user(user_id) ==0):
                database.add_user(user_id)
                await ctx.send(f"Hy {ctx.author.mention}! Welcome aboard! 🎉")
            else:
                await ctx.send(f"Hy {ctx.author.name}, Nice to see you again :)")
                

        # If the user replied "no"
        else:  
            await ctx.send(f"Go fk urself {ctx.author.mention} 😈")  # Funny rejection message

    except asyncio.TimeoutError:  # If the user doesn't reply within 30 seconds
        await ctx.send(f"{ctx.author.mention}, Too slow! Guess you don't wanna be friends. 💀")

@bot.command()
async def addexp(ctx):
    user_id=ctx.author.id
    database.add_exp(user_id,100)
    await ctx.send("addexp")
# Run the bot
bot.run(TOKEN)
