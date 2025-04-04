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
    query1 = "INSERT INTO players (user_id, user_name, premium_status) VALUES (%s, %s, %s)"
    query2 = "INSERT INTO wallet (user_id) VALUES (%s)"  # Only inserting user_id

    cursor.execute(query1, (user_id, user_name, premium_status))
    cursor.execute(query2, (user_id,))
    player_wallet[user_id]={'user_id':user_id,'user_gold':0,'user_gems':0,'user_event_tokens':0}
    conn.commit()
def del_player(table_name, user_id):
    # allowed_tables = {"players", "wallet", "inventory"}  # Whitelist
    # if table_name not in allowed_tables:
    #     raise ValueError("Invalid table name")

    query = f"DELETE FROM {table_name} WHERE user_id=%s"
    cursor.execute(query, (user_id,))
    conn.commit()
def add_gold(user_id,amount):
    # query="""UPDATE wallet
    #         SET user_gold =GREATEST(user_gold+%s,0)
    #         WHERE user_id=%s
    # """
    # cursor.execute(query,(amount,user_id))
    # conn.commit()
    player_wallet[user_id]['user_gold']=max(player_wallet[user_id]['user_gold']+amount,0)

def add_item(item_name:str,item_cost,item_id,item_description,item_rarity):

    items[item_name]=item_id
    query="""INSERT INTO items(item_id,item_name,item_cost,item_rarity,item_description)
             VALUES(%s,%s,%s,%s,%s)"""
    cursor.execute(query,(item_id,item_name,item_cost,item_rarity,item_description))
    conn.commit()

def give_item(item_id,user_id,amount):
    query="""INSERT INTO inventory (user_id,item_id,quantity)
             VALUES(%s,%s,%s)
             ON DUPLICATE KEY UPDATE quantity=quantity+%s
    """
    cursor.execute(query,(user_id,item_id,amount,amount))
    conn.commit()
def check_inventory(user_id):
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
    query = "SELECT * FROM items WHERE item_id = %s"
    cursor.execute(query, (item_id,))  
    result = cursor.fetchone()  
    return result if result else []  
def check_wallet(user_id):
    return (player_wallet[user_id])

def  load_to_dic(table_name,dic):
    query=f"SELECT * FROM {table_name}"
    cursor.execute(query)
    rows=cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    dic.update({row[0]: dict(zip(columns,row))for row in rows})
     
def load_to_table(table_name, dic):
    if not dic:
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
current_users={}
player_exp={}
player_wallet={}
player_inventory={}
def items_dic():
    cursor = conn.cursor(dictionary=True)  # ✅ Enables dictionary access
    query="SELECT item_id , item_name FROM items"
    cursor.execute(query)
    result=cursor.fetchall()
    return {row['item_name'].capitalize():row['item_id'] for row in result}


load_to_dic("players",current_users)
load_to_dic("player_exp",player_exp)
load_to_dic("wallet",player_wallet)
items=items_dic()
def is_user(user_id):
    return user_id in current_users
def push_exp_to_database():
    global conn, cursor
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
    item_name=item_name.capitalize()
    return items.get(item_name,0)
# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(push_exp_to_database, 'interval', seconds=1000)
scheduler.start()