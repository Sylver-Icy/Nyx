import random
import asyncio
import database
import time
import sqlite3
bot = None  # Placeholder for the bot
on_cooldown = {}

exp_list = [
    0,100, 250, 400, 600, 900, 1250, 1600, 2200, 3000, 4200, 
    5500, 7000, 9000, 12000, 15000, 18000, 22000, 27000, 
    32000, 38000, 48000, 60000, 78000, 100000
]
async def lvlup(current_exp, user):
    print("lvlup func called")
    new_level = 0
    while new_level < len(exp_list) and current_exp >= exp_list[new_level]:
        new_level += 1
    current_lvl=database.player_exp[user]["player_lvl"]
    if new_level>current_lvl:
        database.player_exp[user]["player_lvl"] = new_level
        channel=bot.get_channel(1353355604781174846)
        await channel.send(f"<@{user}>Reached level {new_level} 🎉 yippeeeee!")

async def give_exp(user):
    if not database.is_user((user)):
        print("User is not registered!")
        return
    now = time.time()
    if user in on_cooldown and now - on_cooldown[user] < 60:
        print("user on cooldown")
        return
    on_cooldown[user] = now
    rand_exp = random.randint(5, 15)
    if user not in database.player_exp:
        database.player_exp[user]={'user_id':user,'player_exp':0,'player_lvl':1}
    database.player_exp[user]["player_exp"] += rand_exp  # ✅ Directly updating EXP
    print("exp granted",rand_exp)
    await lvlup(database.player_exp[user]["player_exp"], user)  # ✅ Ensure level-up logic runs


