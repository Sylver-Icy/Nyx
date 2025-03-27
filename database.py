import sqlite3  

# Create the 'Players' table 
# conn=sqlite3.connect('players.db')
# cursor = conn.cursor() 
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS Players(
#         User_id TEXT PRIMARY KEY,   -- Unique identifier for each user
#         Exp INTEGER DEFAULT 0,      -- Stores experience points, default is 0
#         Level INTEGER DEFAULT 1     -- Stores player level, default is 1
#     )
# """)

# conn.commit()
# conn.close()

def add_exp(user_id,gained_exp):
    conn = sqlite3.connect('Users.db')  
    cursor=conn.cursor()
    cursor.execute("""UPDATE Players 
                   SET Exp= Exp+?
                   WHERE user_id =?
                   """,(gained_exp,user_id))
    conn.commit()
    conn.close()
def add_user(user_id):
    active_users[user_id]={"Exp":0,"lvl":1}
    conn = sqlite3.connect('Users.db')  
    cursor=conn.cursor()
    cursor.execute(""" INSERT INTO Players (User_id)
                       VALUES(?)
                   """,(user_id,))
    conn.commit()
    conn.close()
def check_user(user_id):
    conn=sqlite3.connect('Users.db')
    cursor=conn.cursor()
    cursor.execute(""" 
                   SELECT EXISTS(SELECT 1 FROM Players WHERE User_id =?)

    """,(user_id,))
    exists=cursor.fetchone()[0]
    conn.close()
    return exists
active_users={}
conn=sqlite3.connect('Users.db')
cursor=conn.cursor()
cursor.execute("""SELECT User_id,Exp,Level FROM Players""")
users=cursor.fetchall()
active_users = {user_id:{"Exp":exp,"lvl":lvl} for user_id ,exp,lvl in users}
conn.close()
# Function to check if user is in database
def is_user(user_id):
    return user_id in active_users
"""Debugging"""
def delete_user(user_id):
    if not is_user(user_id):
        return
    del active_users[user_id]
    conn=sqlite3.connect('Users.db')
    cursor=conn.cursor()
    cursor.execute("""
                        DELETE FROM Players WHERE User_id=?
    """,(user_id,))
    conn.commit()
    conn.close()