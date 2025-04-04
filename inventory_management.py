import re
import database
from prettytable import PrettyTable
import discord

class Item:
    def __init__(self, name):
        self.name = name
        self.id = database.look_for_item_id(name)  # Fetch item ID from database
        item_details = database.item_details(self.id)  # Fetch item details

        self.description = item_details[3]
        self.rarity = item_details[2]
        self.image = item_details[5]
    def emoji_id(self):
        number_emojis = {
    "0": "0️⃣", "1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣",
    "5": "5️⃣", "6": "6️⃣", "7️": "7️⃣", "8": "8️⃣", "9": "9️⃣"
}
        return "".join(number_emojis.get(digit,digit) for digit in str(self.id))

    def item_embed(self):
        """Returns a properly formatted Discord embed for the item."""
        embed = discord.Embed(
            title=f"{self.emoji_id()} ✦ {self.name}",
            description=f"*{self.description}*",
            color=self.get_rarity_color()  # Get color dynamically
        )

        if self.image:
            embed.set_thumbnail(url=self.image)  # Add thumbnail if available

        embed.add_field(name="Rarity", value=self.rarity, inline=True)
        # embed.add_field(name="In inventory", value=self.amount, inline=True)  # Uncomment when ready

        return embed 

    def get_rarity_color(self):
        """Returns a color based on the item's rarity."""
        rarity_color = {
            "Common": discord.Colour.blue(),
            "Rare": discord.Colour.orange(),
            "Epic": discord.Colour.nitro_pink(),
            "Mythic": discord.Colour.dark_red(),
            "Legendary": discord.Colour.brand_green(),
            "Paragon": discord.Colour.gold()
        }
        return rarity_color.get(self.rarity, discord.Colour.light_gray())  
    
        
def autocomplete(query):
    pattern=re.compile(f".*{query}.*")
    print(database.items)
    return [key for key in database.items if pattern.match(key)]

def inventory_table(user_id):
    inventory=database.check_inventory(user_id)
    table = PrettyTable()
    table.field_names=["Item Name","Quantity","Description"]

    for row in inventory:
        table.add_row(row)
    return str(table)
