from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import fun
# bot = discord.Bot()
scheduler = AsyncIOScheduler()

async def water_reminder(bot):
    channel = bot.get_channel(1353355604781174846)
    if not channel is None:
        print(channel.name)
    if channel:
        await channel.send(fun.get_new_message())

def start_reminder(bot):
    scheduler.add_job(lambda: bot.loop.create_task(water_reminder(bot)), 'interval', seconds=10)
    scheduler.start()