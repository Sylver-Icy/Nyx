import os
import discord
import asyncio
import database
import exphandler
import reminders
import random
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime


# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)
exphandler.bot = bot
reminders.bot=bot
@bot.check
async def is_registered(ctx):
    """Global check to ensure user exists in the database before using any command."""
    if ctx.command.name == "helloNyx":  # ✅ Allow this command to run for everyone
        return True
    user_id = ctx.author.id
    if not database.is_user(user_id):  
        await ctx.send(f"{ctx.author.mention}, You are not friend with Nyx! Say `!helloNyx` to get started.")
        return False  # Deny command execution
    return True  # Allow execution if user exists
"""Functions"""
"""Bot Events"""
    #
@bot.event
async def on_level_up(user_id, new_level):
    user = await bot.fetch_user(user_id)
    print(f"✅ on_level_up event triggered for {user_id} (New Level: {new_level})")
    
    channel = bot.get_channel(1353355604781174846)
    if channel:
        await channel.send(f"🎉 {user.mention} has leveled up to **Level {new_level}**! Yippeeeeeee!")
    else:
        print("❌ ERROR: Channel not found")



async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        # Suppress the error so it doesn’t spam the terminal
        return
    raise error  # Only log actual errors

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print("Calling func properly")
    asyncio.create_task(reminders.start_reminder(bot)) 
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"Received message: {message.content}") 
    await exphandler.give_exp(message.author.id)  # Give EXP

    # Check if any command exists in the message
    for command in bot.commands:
        if f"!{command.name}" in message.content:
            message.content = f"!{command.name}"  # Extract command only
            ctx = await bot.get_context(message)
            await bot.invoke(ctx)
            return  

    await bot.process_commands(message)
    
#BOT COMMANDS

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
            
            user_id=ctx.author.id
            if not database.is_user(user_id):
                database.current_users[user_id] = {
    "user_id": user_id,
    "user_name": ctx.author.name,
    "premium_status": 0,
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
                await ctx.send(f"Hy {ctx.author.mention}! Welcome aboard! 🎉")
            else:
                await ctx.send(f"Hy {ctx.author.name}, Nice to see you again :)")
                

        # If the user replied "no"
        else:  
            await ctx.send(f"Go fk urself {ctx.author.mention} ")  # Funny rejection message

    except asyncio.TimeoutError:  # If the user doesn't reply within 30 seconds
        await ctx.send(f"{ctx.author.mention}, Too slow! Guess you don't wanna be friends. 💀")


@bot.command()
async def deluser(ctx):
    await ctx.send("Who do you want me to ignore? Tag them!")

    # Wait for the user's response
    def check(msg):
        return msg.author == ctx.author and msg.mentions

    try:
        msg = await bot.wait_for("message", check=check, timeout=30)  # Wait for reply (30 sec)
        target_user = msg.mentions[0]  # Get the first mentioned user
        del database.current_users[target_user.id]  

        await ctx.send(f"Fine, {target_user.mention} has been erased from my memory >:)")
    except asyncio.TimeoutError:
        await ctx.send("Bruh, you took too long. Try again.")
    except IndexError:
        await ctx.send("You didn't tag anyone... what do you want me to do? 💀")
@bot.command()
async def flipcoin(ctx):
    a=random.choice(["Head","Tails"])
    await ctx.send(f"Tossing the coin.... andddddddd its a {a} !🥁")
@bot.command()
async def checkexp(ctx):
    lvl=database.player_exp[ctx.author.id]["player_lvl"]
    exp=database.player_exp[ctx.author.id]["player_exp"]
    await ctx.send(f"You are currently at **{lvl}** with {exp} Experience points")


@bot.slash_command(name="shout", description="Shout something loudly")
async def shout(ctx, message: str):
    await ctx.respond(message.upper())  # Forces output to be uppercase
# Run the bot
bot.run(TOKEN)
