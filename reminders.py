from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
import fun
import random
bot=None
scheduler = AsyncIOScheduler()

async def water_reminder(bot):
    channel = bot.get_channel(1353355604781174846)
    if channel:
        await channel.send(fun.get_new_message())
    else:
        print("❌ ERROR: Channel not found")

def schedule_next_reminder(bot):
    """Schedules the next water reminder with a new random interval."""
    x = random.randint(40, 60)  # ✅ Pick a new interval every time
    print(f"✅ Next reminder in {x} minutes")
    scheduler.add_job(water_reminder, 'interval', minutes=39, args=[bot])

async def start_reminder(bot):
    await water_reminder(bot) #first call right after bot starts
    schedule_next_reminder(bot)  # ✅ Start the first reminder
    scheduler.start()