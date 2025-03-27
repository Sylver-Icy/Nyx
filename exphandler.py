import random
import asyncio
import database
import time
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
bot = None  # Placeholder for the bot
on_cooldown = {}

exp_list = [
    0,100, 250, 400, 600, 900, 1250, 1600, 2200, 3000, 4200, 
    5500, 7000, 9000, 12000, 15000, 18000, 22000, 27000, 
    32000, 38000, 48000, 60000, 78000, 100000
]
def lvlup(current_exp, user):
    # print("lvlup func called")
    new_level = 0
    while new_level < len(exp_list) and current_exp >= exp_list[new_level]:
        new_level += 1

    if new_level>database.active_users[user]["lvl"]:  
        database.active_users[user]["lvl"] = new_level
        bot.dispatch("level_up", user, new_level)

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

    database.active_users[user]["Exp"] += rand_exp  # ✅ Directly updating EXP
    print("exp granted",rand_exp)
    lvlup(database.active_users[user]["Exp"], user)  # ✅ Ensure level-up logic runs

def push_exp_to_database():
    # print("push func called")
    if not database.active_users:  # Avoid running the query if there's nothing to update
        return

    conn = sqlite3.connect('Users.db')
    cursor = conn.cursor()

    cursor.executemany(
    """
    UPDATE Players SET Exp=?, Level=? WHERE User_id=?
    """,
    [(data["Exp"], data["lvl"], user_id) for user_id, data in database.active_users.items()]
)

    conn.commit()
    conn.close()

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(push_exp_to_database, 'interval', seconds=10)
scheduler.start()
print(database.active_users)
print("Type of active_users:", type(database.active_users))  # Should be <class 'dict'>

# Print first key-value pair's data types
for key, value in database.active_users.items():
    print("Key Type:", type(key), "→ Value Type:", type(value))

    # If value is a dictionary, check its structure
    if isinstance(value, dict):
        for sub_key, sub_value in value.items():
            print(f"  {sub_key} → {sub_value} (Type: {type(sub_value)})")

    break  # Only print for one user to avoid spam