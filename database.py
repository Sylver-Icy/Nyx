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

def add_player(user_id,user_name,premium_status=False):
    query="INSERT INTO players (user_id,user_name,premium_status) VALUES(%s,%s,%s)"
    cursor.execute(query,(user_id,user_name,premium_status))
    conn.commit()

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
load_to_dic("players",current_users)
player_exp={}
load_to_dic("player_exp",player_exp)
def is_user(user_id):
    if user_id in current_users:
        return True
    return False
def push_exp_to_database():
    load_to_table("player_exp",player_exp)
    load_to_table("players",current_users)

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(push_exp_to_database, 'interval', seconds=10)
scheduler.start()
