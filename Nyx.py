import os
import discord
import asyncio
import database
import exphandler
import inventory_management
import reminders
import shop_management
import minigames
import random
from discord.ext import commands
from discord.commands import Option
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
        # Extract the command with everything after it
            command_start = message.content.index(f"!{command.name}")
            new_content = message.content[command_start:]  # Keep arguments intact
        
        # Modify message content safely
            message.content = new_content  
        
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
                database.add_player(ctx.author.id,ctx.author.name)
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
        if not database.is_user(target_user.id):
            await ctx.send("Already ignoring :)")
            return
        del database.current_users[target_user.id]
        del database.player_exp[target_user.id]
        database.del_player("players",target_user.id)
        database.del_player("player_exp",target_user.id)
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
@bot.command()
async def checkwallet(ctx):
    user_id=ctx.author.id
    money=database.check_wallet(user_id)
    await ctx.send(f"You currently own **{money['user_gold']}** Gold and **{money['user_gems']}** Gems")

@bot.command()
async def checkinventory(ctx):
    player_inventory=inventory_management.inventory_table(ctx.author.id)
    await ctx.send(f"\nHere is your inventory:\n```{player_inventory}```")
    print(player_inventory)
@bot.command()
async def buy(ctx, arg: str, arg2: int = 1):
    name=arg.capitalize()
    quanity=arg2
    if name not in shop_management.shop:
        await ctx.send("That item is not in shop use `/shop` to see all available deals")
        return
    player_money=database.player_wallet[ctx.author.id]['user_gold']
    item_price=shop_management.shop[name]
    if player_money>=item_price*quanity:
        item_id=database.look_for_item_id(name)
        print(item_id)
        database.give_item(item_id,ctx.author.id,quanity)
        database.player_wallet[ctx.author.id]['user_gold']-=(item_price*quanity)
        await ctx.send(f"You bought {quanity} X {name} for {item_price*quanity} Gold ")
    elif(player_money<item_price):
        await ctx.send(f"You brokie you can't afford {name}.Make some money first!")
    else:
        afford=player_money//item_price
        await ctx.send(f"Nuh uh! Too broke to buy that many. However you can afford {afford} X {name}")
        

    
    
@bot.slash_command(name="shout", description="Shout something loudly")
async def shout(ctx, message: str):
    await ctx.respond(message.upper())  # Forces output to be uppercase

@bot.slash_command(name="give_gold",description="Gives gold to desired player")
async def give_gold(ctx,amount:int,target_user:discord.Member):
    if not database.is_user(target_user.id):
        await ctx.respond(f"{target_user.mention} is not registered can't tranfer gold!")
        return
    database.add_gold(target_user.id,amount)
    await ctx.respond(f"{ctx.author.mention} gave **{amount}** Gold to {target_user.mention}")
@bot.slash_command(name="give_items",description="give other player items")
async def give_items(ctx,item_name:str,amount:int,target_user:discord.Member):
    item_id=database.look_for_item_id(item_name.capitalize())
    if not item_id:
        auto=inventory_management.autocomplete(item_name)
        if auto:
            suggestions = " or maybe ".join(auto[:3])
            await ctx.respond(f"Couldn't find '{item_name}', did you mean {suggestions} ?" )
        else:
            await ctx.respond(f"There is no such item {item_name},not even close bruh")
        return
    if not database.is_user(target_user.id):
        await ctx.respond(f"{target_user.mention} is not part of database! Can't send items.")
        return
    database.give_item(item_id,target_user.id,amount)
    await ctx.respond(f"Transfered **{amount}**X {item_name.title()} to {target_user.mention}")
# @give_items.autocomplete("item_name")
# async def item_name_autocomplete(ctx:discord.AutocompleteContext):
#     items=inventory_management.autocomplete(ctx.value)
#     return items[:10] if items else []

@bot.slash_command(name="add_item", description="Adds any desired item to the database")
async def add_item(
    ctx: discord.ApplicationContext,
    item_id: int,
    item_name: str,
    item_price: int,
    item_description: str,
    item_rarity: Option(str, "Choose item rarity", choices=["Common", "Rare", "Epic", "Mythic", "Legendary", "Paragon"])
):
    if item_id in database.items.values():
        await ctx.respond("Another item with this key exists,try different key")
        return
    database.add_item(item_name.capitalize(), item_price, item_id, item_description, item_rarity)
    await ctx.respond(
        f"Successfully added a {item_rarity} item ({item_name.capitalize()}) for the price of {item_price} Golds.\n"
        f"The item is described as: '*{item_description}*'\n"
    )
@bot.slash_command(name="test")
async def test(ctx):
    embed=discord.Embed(
        title=f"{ctx.author.name}'s Inventory",
        description="Here are all the items owned by you",
        color=discord.Color.nitro_pink()
    )
    embed.add_field(name="Test1        `15 Gold`   `Rare`   `8 Owned`", value="Testing this embed")  # Invisible space character
    embed.add_field(name="A bigger name for testing embeds format   `24 Gold`      `Paragon`     `24 owned`", value="Now we need a bigger description too to test the format of embed. We are gonna find out how big descriptions will look in our embed. Let's hope they look nice",inline=False)
    embed.add_field(name="test3      `69 Gold`      `Common`      `2 Owned`", value="This item is to verify how tf items below big descriptions will look", inline=False)
    await ctx.respond(embed=embed)
@bot.slash_command(name="test2")
async def test2(ctx):
    embed=discord.Embed(
        title=f"**{ctx.author.name}'s inventory**",
        description="Here are all the items owned by you",
        color=discord.Colour.blue()
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/4230/4230567.png")
    inventory=database.check_inventory(ctx.author.id)
    if inventory:
        for i in inventory:
            embed.add_field(name=f"{i[0]}     X`{i[1]}`        `{i[3]}`",value=f"{i[2]}",inline=False)
        await ctx.respond(embed=embed)

    else:
        database.give_item(1,ctx.author.id,1)
        await ctx.respond(f"Awww poor baby {ctx.author.mention}, you don't own anything.Here have this ** Sword ** to defend yourself")


@bot.slash_command(name="test3")
async def test3(ctx):
    # Define rarity colors using emojis or colored squares
    rarity_colors = {
        "Common": "🟩 Common",
        "Rare": "🟦 Rare",
        "Epic": "🟪 Epic",
        "Legendary": "🟨 Legendary"
    }

    embed = discord.Embed(
        title=f"{ctx.author.name}'s inventory",
        description="Here are all the items owned by you",
        color=discord.Colour.blue()
    )

    for i in database.check_inventory(ctx.author.id):
        rarity_label = rarity_colors.get(i[3], i[3])  # Default to original if not found
        embed.add_field(
            name=f"{i[0]}     X`{i[1]}`        `{rarity_label}`",
            value=f"{i[2]}",
            inline=False
        )

    await ctx.respond(embed=embed)
@bot.slash_command(name="shop")
async def shop(ctx):
    shop_embed=shop_management.embed
    # shop_embed.set_footer(text=f" Current Gold  {database.player_wallet[ctx.author.id]['user_gold']}")
    await ctx.respond(embed=shop_embed)
@bot.slash_command(name="describe", description="Use it to describe any item")
async def describe(
    ctx,
    item_name: Option(str, "Enter the name of the item you want to describe")  # ✅ Adds a description
):
    name = item_name.capitalize()
    if name not in database.items:
        auto=inventory_management.autocomplete(item_name)
        if auto:
            await ctx.respond(f"No such item available.Perhaps you meant {auto[0]}")
            return
        else:
            await ctx.respond(f"I don't remeber anything like {item_name}")
            return

    item = inventory_management.Item(name)  # ✅ Create an instance
    embed = item.item_embed()  # ✅ Call method on instance

    await ctx.respond(embed=embed)
    # Run the bot
@bot.slash_command(name="rcp",description="Starts a game of Rock Paper Scissors")
async def rcp(ctx,select_your_opponent:discord.Member,rounds:int,bet:int):
    await minigames.rcp(ctx,select_your_opponent,rounds,bet)

bot.run(TOKEN)
