from datetime import datetime
from dotenv import load_dotenv
import os
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()
password=os.getenv('DATABASE_PASSWORD')
conn=mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="veyra_db"
)
cursor=conn.cursor()

def add_player(user_id, user_name, premium_status=False):
    """
    Adds a new player to the database and updates the cache dictionaries.
    Triggered when user sends `!helloNyx` in Discord.
    Affects: players table, wallet table, current_users, player_wallet caches.
    """
    query1 = "INSERT INTO players (user_id, user_name, premium_status) VALUES (%s, %s, %s)"
    query2 = "INSERT INTO wallet (user_id) VALUES (%s)"  # Only inserting user_id

    cursor.execute(query1, (user_id, user_name, premium_status))
    cursor.execute(query2, (user_id,))
    current_users[user_id] = {
    "user_id": user_id,
    "user_name": user_name,
    "premium_status": 0,
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
    player_wallet[user_id]={'user_id':user_id,'user_gold':0,'user_gems':0,'user_event_tokens':0}
    conn.commit()


def del_player(user_id):
    """
    Deletes a player from the database and removes them from the cache.
    Note: This is for debugging and test resets only.
    Affects: players table, player_exp table, current_users, player_exp caches.
    """
    del current_users[user_id]
    del player_exp[user_id]
    query = "DELETE FROM players WHERE user_id=%s"
    query2="DELETE FROM player_exp WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    cursor.execute(query2, (user_id,))
    conn.commit()


def add_gold(user_id,amount):
    """
    Adds or removes gold from a user's cache.
    (Used only for testing/debugging; values can be negative.)
    """
    player_wallet[user_id]['user_gold']=max(player_wallet[user_id]['user_gold']+amount,0)


def add_item(item_name:str,item_cost,item_id,item_description,item_rarity):
    """
    Adds a new item directly to the items table.
    Meant for admin use via Discord bot commands.
    """
    items[item_name]=item_id
    query="""INSERT INTO items(item_id,item_name,item_cost,item_rarity,item_description)
             VALUES(%s,%s,%s,%s,%s)"""
    cursor.execute(query,(item_id,item_name,item_cost,item_rarity,item_description))
    conn.commit()


def give_item(item_id,user_id,amount):
    """
    Gives a specific item to a user by adding it to their inventory in the database.
    Note: For testing/debugging purposes.
    """
    query="""INSERT INTO inventory (user_id,item_id,quantity)
             VALUES(%s,%s,%s)
             ON DUPLICATE KEY UPDATE quantity=quantity+%s
    """
    cursor.execute(query,(user_id,item_id,amount,amount))
    conn.commit()


def check_inventory(user_id):
    """
    Retrieves a user's inventory by joining item and inventory tables.
    Returns: List of (item_name, quantity, description, rarity).
    """
    query = """
        SELECT i.item_name, inv.quantity, i.item_description, i.item_rarity
        FROM inventory inv
        JOIN items i ON inv.item_id = i.item_id
        WHERE inv.user_id = %s
    """
    cursor.execute(query, (user_id,))
    results = cursor.fetchall()
    return results or []


def item_details(item_id):
    """
    Fetches details of a specific item by item_id.
    """
    query = "SELECT * FROM items WHERE item_id = %s"
    cursor.execute(query, (item_id,))  
    result = cursor.fetchone()  
    return result if result else []  
def check_wallet(user_id):
    """
    Returns a user's wallet data from cache (gold, gems, event tokens).
    """
    return player_wallet[user_id]


def  load_to_dic(table_name,dic):
    """
    Loads the entire table into the provided dictionary.
    Allows fast cache read/write access to avoid frequent DB calls.
    """
    query=f"SELECT * FROM {table_name}" #selects the func from where value is to be loaded from
    cursor.execute(query)
    rows=cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    dic.update({row[0]: dict(zip(columns,row))for row in rows}) #zips the data in a dic format


def load_to_table(table_name, dic):
    """
    Pushes cached dictionary data back to the corresponding database table.
    Performs upsert using ON DUPLICATE KEY.
    """
    if not dic: #check to ensure if the dic is empty
        print("Dictionary is empty. Nothing to insert.")
        return
    
    columns = list(next(iter(dic.values())).keys())  # Get column names
    placeholders = ', '.join(['%s'] * len(columns))
    update_clause = ', '.join([f"{col} = VALUES({col})" for col in columns])  # MySQL 5.x/8.x style

    query = f"""
        INSERT INTO {table_name} ({', '.join(columns)}) 
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
    """

    values = [tuple(entry[col] for col in columns) for entry in dic.values()]
    
    cursor.executemany(query, values)
    conn.commit()

#Making empty dics to be filled later from table and used as cache

current_users={}   #dic for all the users-used to check if user has registered or not
player_exp={}      #dic all users exp and lvl stats
player_wallet={}   #dic to store all users wallet details
player_inventory={}#dic to contain players inventory


def items_dic():
    """
    Returns a dictionary {ItemName: ItemID} for quick lookup and autocomplete.
    Uses capitalized item names for consistency.
    """
    cursor_new = conn.cursor(dictionary=True)  # ✅ Enables dictionary access
    query="SELECT item_id , item_name FROM items"
    cursor_new.execute(query)
    result=cursor_new.fetchall()
    return {row['item_name'].capitalize():row['item_id'] for row in result}

#loading all the data to cache at the start of bot 
load_to_dic("players",current_users)
load_to_dic("player_exp",player_exp)
load_to_dic("wallet",player_wallet)
items=items_dic()


def is_user(user_id):
    """
    Checks if a user is registered in the cache.
    Returns True if present, False otherwise.
    """
    return user_id in current_users

def push_to_database():
    """
    Pushes all cached data back to their respective database tables.
    Only runs if DB connection is active.
    """
    # global conn, cursor
    try:
        if not conn.is_connected():
            conn.reconnect()
        load_to_table("player_exp", player_exp)
        load_to_table("players", current_users)
        load_to_table("wallet",player_wallet)
        # print("pushed")
    except mysql.connector.Error as err:
        print(f"Database update failed: {err}")


def look_for_item_id(item_name):
    """
    Looks up item_id from the items dictionary using the item name.
    Returns 0 if item not found.
    """
    item_name=item_name.capitalize()
    return items.get(item_name,0)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(push_to_database, 'interval', seconds=1000)
scheduler.start()
