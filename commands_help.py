import discord
import asyncio

class Move_Button(discord.ui.View):
    def __init__(self,pages):
        super().__init__(timeout=50)
        self.current_page=0
        self.pages=pages
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="⬅️ Previous Page",style=discord.ButtonStyle.green)
    async def left(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.current_page-=1
        if self.current_page<0:
            self.current_page=2
        await interaction.response.edit_message(embed=self.pages[self.current_page],view=self)
    
    @discord.ui.button(label="Next Page ➡️",style=discord.ButtonStyle.green)
    async def right(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.current_page+=1
        if self.current_page==3:
            self.current_page=0
        await interaction.response.edit_message(embed=self.pages[self.current_page],view=self)


page1=discord.Embed(
    title="Guide to use Veyra",
    description="This page contains details about the bot itself next page is for ! commands and last page is for slash commads",
    color=discord.Colour.nitro_pink()
    )
page1.add_field(
    name="! Commands",value="All prefix commands are case insensitive except for `!helloNyx`" \
         " and they can be used in between the sentances." \
         "\n For example `Hey Veyra should I eat burger today? !flipcoin` will work just fine",
         inline=False
         )
page1.add_field(
    name="/ Commands",
    value="All the slash commands have description for them along with options" \
         "If you want deeper info you can check the website ",
    inline=False
)
page2=discord.Embed(
    title="Guide to use Veyra",
    description="This page contains details about the ! Commands",
    color=discord.Colour.nitro_pink()
    )
page2.add_field(name="`!helloNyx`",value="You have prolly used this already that's why you are seeing this rn",inline=False)
page2.add_field(name="`!flipcoin`",value="Flips a coin duh?",inline=False)
page2.add_field(name="`!ping`",value="Pretty useless don't use it please",inline=False)
page2.add_field(name="`!checkexp`",value="Shows your current level along with your exp points",inline=False)
page2.add_field(name="`!checkwallet`",value="Shows how much gold and gems you have",inline=False)
page2.add_field(name="`!buy <item_name> <item_quantity>`",value="Lets you buy specified items if not specified item quantity is 1 by default",inline=False)

page3=discord.Embed(
    title="Guide to use Veyra",
    description="This page contains details about all the / Commands",
    color=discord.Colour.nitro_pink()
    )
page3.add_field(name="`/rps`", value="Let's you invite anyone from server to  a game of rock paper and scissors you get to choose number of rounds and bet amount",inline=False)
page3.add_field(name="`/reactiongame`", value="Starts a mini game",inline=False)
page3.add_field(name="`/shout`", value="Useless af but my first slash command so don't wanna remove it",inline=False)
page3.add_field(name="`/shop`", value="Opens up the shop",inline=False)
page3.add_field(name="`/giveitem`", value="Send any item to anyone just like that",inline=False)
page3.add_field(name="`/givegold`", value="Send free gold to anyone",inline=False)
page3.add_field(name="`/test2 and test3`", value="Two inventory formats returns your inventory",inline=False)
page3.add_field(name="`/describe`", value="Can describe any item from database (try on sword I've yet to fill others)",inline=False)
page3.add_field(name="`/describe`", value="Can describe any item from database (try on sword I've yet to fill others)",inline=False)


pages=[page1,page2,page3]

async def commands_list(ctx):
    view=Move_Button(pages)
    msg = await ctx.respond(embed=page1, view=view)
    view.message = await msg.original_response()