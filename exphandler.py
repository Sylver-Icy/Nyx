import random
import asyncio
import database
on_cooldown={}
# batch_exp={}
async def give_exp(user):
    if user in on_cooldown:
         return
    on_cooldown[user]="cooldown"
    exp=random.randint(5,15)
    database.add_exp(user,exp)
    # batch_exp[user]=exp
    await asyncio.sleep(60)
    del on_cooldown[user]


