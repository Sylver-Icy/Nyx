import discord
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
import random
import datetime

bot=None

class JoinView(discord.ui.View):
    def __init__(self, timeout=6):
        super().__init__(timeout=timeout)
        self.joined_users = set()

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id in self.joined_users:
            await interaction.response.send_message("Already joined, chillax.", ephemeral=True)
        else:
            self.joined_users.add(interaction.user.id)
            await interaction.response.send_message("You're in. Welcome to the chaos.", ephemeral=True)

async def start_reaction_game(ctx):
    embed = discord.Embed(
        title="Who wants in?",
        description="Click join. You have 2 minutes. After that, we go underground.",
        color=discord.Color.orange()
    )
    channel=ctx.channel
    view = JoinView()

    response = await ctx.respond(embed=embed, view=view)
    msg = await response.original_response()

    # Wait for view timeout
    await view.wait()
    
    for child in view.children:
        child.disabled = True
    await msg.edit(view=view)

    updated_embed = discord.Embed(
        title="Joining closed!",
        description="Time's up! The game has started in a private thread. No turning back now.",
        color=discord.Color.red()
    )
    await msg.edit(embed=updated_embed)

    guild = channel.guild
    joined_members = [guild.get_member(uid) for uid in view.joined_users if guild.get_member(uid)]

    if not joined_members:
        await channel.send("Nobody joined. Bunch of cowards.")
        return

    thread = await ctx.channel.create_thread(
        name="Reaction Game",
        type=discord.ChannelType.private_thread,
    )

    for member in joined_members:
        try:
            await thread.add_user(member)
        except Exception as e:
            print(f"Failed to add {member}: {e}")

    await begin_game(thread,joined_members)

    # Game Logic
async def begin_game(thread,joined_members):
    await thread.send("Send `⚡️` when I say Flash!")
    delay=random.randint(3,6)
    await asyncio.sleep(delay)
    await thread.send("Flash!")
    flash_time=datetime.datetime.utcnow()

    def check(m):
        return (
            isinstance(m.channel, discord.Thread) and
            m.channel.id == thread.id and
            m.content.strip() == "⚡️" and
            m.author in joined_members
        )
    reaction_time={}
    try:
        while True:
            msg=await bot.wait_for("message",timeout=7,check=check)
            user_id=msg.author.id
            if user_id not in reaction_time:
                msg_time=msg.created_at.replace(tzinfo=None)
                diff=(msg_time-flash_time).total_seconds() * 1000
                reaction_time[user_id]=diff
    except asyncio.TimeoutError:
        await thread.send("Time's up here is how everyone did:")
    
    if not reaction_time:
        await thread.send("No one could react fast enough")
    else:
        leaderboard=sorted(reaction_time.items(),key=lambda x: x[1])
        result="\n".join(
            [f"<@{user_id}>: {int(diff)} ms" for user_id,diff in leaderboard]
        )
        await thread.send(result)
        finished_game.add(thread.id)



    #===FOR THE DELETION OF FINISHED GAMES==
finished_game = set()

#Store the loop
loop = asyncio.get_event_loop()

# The async task
async def delete_finished_games(finished_games: set):
    for thread_id in finished_games:
        thread = bot.get_channel(thread_id)
        if thread and isinstance(thread, discord.Thread):
            try:
                await thread.delete()
            except Exception as e:
                print(f"Error deleting thread {thread_id}: {e}")
    finished_game.clear()

# Thread-safe wrapper
def schedule_cleanup():
    asyncio.run_coroutine_threadsafe(delete_finished_games(finished_game.copy()), loop)
# Step 4: Register job
scheduler = BackgroundScheduler()
scheduler.add_job(schedule_cleanup, 'interval', seconds=60)
scheduler.start()
