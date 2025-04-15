import discord
import asyncio
import reactiongame


class Accept_Button(discord.ui.View):
    def __init__(self, challenger, target, timeout=30):
        super().__init__(timeout=timeout)
        self.challenger = challenger
        self.target = target
        self.accepted = False
    @discord.ui.button(label="Accept Duel ⚔️", style=discord.ButtonStyle.green)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):  # ✅ FIXED PARAMETER ORDER
        if interaction.user.id != self.target.id:  # ✅ Ensure correct user check
            await interaction.response.send_message("You're not the challenged one!", ephemeral=True)
            return
        # elif interaction.user.id==self.target.id:
        #     target_wallet=database.check_wallet(self.target.id)
        #     target_gold=target_wallet["User_gold"]
        #     if target_gold>
        self.accepted = True
        await interaction.response.defer()
        self.stop()

class RCP_button(discord.ui.View):
    def __init__(self, challenger, target, timeout=20):
        super().__init__(timeout=timeout)
        self.challenger = challenger
        self.target = target
        self.choices = {}  # Store player choices
        self.players_pressed = set()  # Track who has already played

    async def handle_choice(self, interaction: discord.Interaction, choice: str):
        # Prevent double selection
        if interaction.user.id in self.players_pressed:
            await interaction.response.send_message("You already selected!", ephemeral=True)
            return
        
        # Store choice
        self.choices[interaction.user.id] = choice
        self.players_pressed.add(interaction.user.id)

        # Acknowledge the button press
        await interaction.response.send_message(f"You chose {choice}. Waiting for the other player...", ephemeral=True)

        # If both players have chosen, determine winner
        if len(self.choices) == 2:
            p1 = self.challenger.id
            p2 = self.target.id
            p1choice = self.choices[p1]  # ✅ Fix dictionary access
            p2choice = self.choices[p2]
            print(p1choice,p2choice)

            WINNING_MOVES = {
                "Rock": "Scissors",
                "Paper": "Rock",
                "Scissors": "Paper"
            }

            if p1choice == p2choice:
                result_message = f"Both players chose **{p1choice}**! It's a **tie**! 🤝"
            elif WINNING_MOVES[p1choice] == p2choice:
                result_message = f"**{self.challenger.mention}** wins! 🎉 {p1choice} beats {p2choice}!"
            else:
                result_message = f"**{self.target.mention}** wins! 🎉 {p2choice} beats {p1choice}!"

            # Send result in thread
            # await interaction.channel.send(result_message)
            self.stop()  # Ends the View
    
    @discord.ui.button(label="Rock 🪨", style=discord.ButtonStyle.gray)
    async def accept_rock(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_choice(interaction, "Rock")

    @discord.ui.button(label="Paper 📜", style=discord.ButtonStyle.blurple)
    async def accept_paper(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_choice(interaction, "Paper")

    @discord.ui.button(label="Scissors ✂️", style=discord.ButtonStyle.red)
    async def accept_scissors(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.handle_choice(interaction, "Scissors")

async def rcp(ctx, target_user: discord.Member, rounds,bet):
    embed = discord.Embed(
        title="Rock, Paper, Scissors",
        description=f"{target_user.mention} You have been challenged to a game of Rock Paper Scissors by {ctx.author.mention}",
        color=discord.Colour.dark_grey()
    )
    embed.add_field(name="**Number of rounds**",value=rounds,inline=True)
    embed.add_field(name="**Bet proposed**",value=bet,inline=True)

    view = Accept_Button(ctx.author, target_user, timeout=30)

    # ✅ Send challenge embed with accept button
    message = await ctx.respond(embed=embed, view=view)

    await view.wait()  # Waits for 30 seconds or button press

    if not view.accepted:  # ⏳ If no response in time
        await message.edit(content=f"{target_user.name} didn't respond in time. Challenge canceled. ⏳", embed=None, view=None)
        return

    # ✅ If accepted, proceed
    await ctx.respond(f"Challenge accepted by {target_user.name}!")
    await start_rps(ctx, target_user, rounds,bet)

async def start_rps(ctx, target_user: discord.Member, rounds,bet):
    thread = await ctx.channel.create_thread(
        name=f"{ctx.author.name} vs {target_user.name} - RPS BATTLE",
        type=discord.ChannelType.public_thread,
    )

    p1_score = 0
    p2_score = 0
    # needed_wins = (rounds // 2) + 1  # Best-of-N rule
    for round_number in range(1, rounds + 1):
        view = RCP_button(ctx.author, target_user)
        embed = discord.Embed(
            title=f"🪨📜✂ {ctx.author.name} VS {target_user.name} \n Round {round_number}/{rounds}",
            description="Select your choice with the buttons below!",
            color=discord.Colour.dark_purple()
        )
        embed.add_field(name="**Current Score**", value=f"{ctx.author.name}: {p1_score} \n {target_user.name}: {p2_score}")
        
        await thread.send(embed=embed, view=view)

        await view.wait()

        p1choice = view.choices.get(ctx.author.id)
        p2choice = view.choices.get(target_user.id)

        if not p1choice:
            await thread.send(f"⏳ {ctx.author.mention} **didn't choose in time!** {target_user.mention} **wins the match by default!** 🏆")
            return
        if not p2choice:
            await thread.send(f"⏳ {target_user.mention} **didn't choose in time!** {ctx.author.mention} **wins the match by default!** 🏆")
            return

        WINNING_MOVES = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

        if p1choice == p2choice:
            result_message = f"🤝 **Tie!** Both players chose **{p1choice}**!"
        elif WINNING_MOVES[p1choice] == p2choice:
            result_message = f"🎉 **{ctx.author.mention} wins this round!** {p1choice} beats {p2choice}!"
            p1_score += 1
        else:
            result_message = f"🎉 **{target_user.mention} wins this round!** {p2choice} beats {p1choice}!"
            p2_score += 1

        await thread.send(result_message)

        # Check for match winner
        rounds_remaining=rounds-round_number
        if p1_score > p2_score + rounds_remaining:
            await ctx.send(f"🏆 **{ctx.author.mention} won the match against {target_user.mention}! This win them {bet *2} Gold** \n Final Score {p1_score}-{p2_score}")
            reactiongame.finished_game.add(thread.id)
            return
        if p2_score > p1_score + rounds_remaining:
            await ctx.send(f"🏆 **{target_user.mention} won the match against {ctx.author.mention}! This win them {bet *2} Gold** \n Final Score {p1_score}-{p2_score}")
            reactiongame.finished_game.add(thread.id)
            return

    # **Final results**
    if p1_score > p2_score:
        final_message = f"🏆 **{ctx.author.mention} won the match against {target_user.mention}! This win them {bet *2} Gold** \n Final Score {p1_score}-{p2_score}"
    elif p2_score > p1_score:
        final_message = f"🏆 **{target_user.mention} won the match against {ctx.author.mention}! This wins them {bet *2} Gold** \n Final Score {p2_score}-{p1_score}"
    else:
        final_message = f"⚔️ The match between {ctx.author.name} & {target_user.name} was a **draw**! 🤝 Pot Money Refunded"

    await ctx.send(final_message)
    reactiongame.finished_game.add(thread.id)

    