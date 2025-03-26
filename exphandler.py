import random
import asyncio
import database
import time
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
on_cooldown={}
batch_exp={}
async def give_exp(user):
    if not database.is_user(str(user)):
         print("User is not registered!")
         return
    now=time.time()
    if user in on_cooldown and now-on_cooldown[user]<0:
         return
    on_cooldown[user]=now
    exp=random.randint(5,15)
#database.add_exp(user,exp)
    if user in batch_exp:
          batch_exp[user]+=exp
    else:
          batch_exp[user]=exp

#gonna add logic to put batch_exp in db later
def push_exp_to_database():
     global batch_exp
     if not batch_exp:  # Avoid running the query if there's nothing to update
        return
    
     conn=sqlite3.connect('players.db')
     cursor=conn.cursor()
     cursor.executemany(
                         """
                              UPDATE Players SET Exp=Exp+? 
                              WHERE User_id=?
                         """,[(exp,user_id) for user_id,exp in batch_exp.items()])
     conn.commit()
     conn.close()
     batch_exp.clear()
# Initialize the scheduler
scheduler = BackgroundScheduler()

# Schedule the function to run every 60 seconds
scheduler.add_job(push_exp_to_database, 'interval', seconds=170)

# Start the scheduler
scheduler.start()

