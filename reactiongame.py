import discord
import asyncio

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

    guild = channel.guild
    joined_members = [guild.get_member(uid) for uid in view.joined_users if guild.get_member(uid)]

    if not joined_members:
        await channel.send("Nobody joined. Bunch of cowards.")
        return

    thread = await msg.create_thread(name="Secret Ops 🔒", type=discord.ChannelType.private_thread)

    for member in joined_members:
        try:
            await thread.add_user(member)
        except Exception as e:
            print(f"Failed to add {member}: {e}")

    await channel.send(f"Thread spawned with {len(joined_members)} legends.")