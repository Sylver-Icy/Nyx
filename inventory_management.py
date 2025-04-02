import re
import database
from prettytable import PrettyTable

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
print(database.check_inventory(915837736819249223))
