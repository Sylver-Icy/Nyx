import discord
# import database



embed=discord.Embed(
    title="Veyra's Bazar",
    description="A fancy shop for all your needs",
    color=discord.Colour.purple()
)
emoji="<:gold:1356937420733677629>"
shop={"Apples":2,"Bow":11,"Potion":702,"Shield":25,"Drugs":99,"Shoes":24,}
embed.add_field(name=f"`Apples`    2 {emoji}",value="*Sweet red apples*")
embed.add_field(name=f"`Bow`     11 {emoji}",value="*A bow to shoot down enemies from afar*")
embed.add_field(name=f"`Shield`    25 {emoji}",value="*A handy item to protect yourself*")

embed.add_field(name=f"`Potion`    702 {emoji}",value="*Incredily strong potion handcrafted by* **BELL THE WITCH**")
embed.add_field(name=f"`Shoes`     24 {emoji}",value="*Very handy to save from thorns in path*")
embed.add_field(name=f"`Drugs`     99 {emoji}",value="*If you wanna fly without wings*")
link="https://cdn-icons-png.flaticon.com/512/5542/5542421.png"
# embed.set_author(
#     name="Veyra's Bazar", 
#     icon_url="https://img.freepik.com/premium-psd/png-fantasy-flower-neon-art-illustration_53876-607319.jpg?semt=ais_hybrid", 
#     url="https://example.com"
# )
embed.set_thumbnail(url=link)
