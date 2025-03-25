import sqlite3  



# cursor = conn.cursor() 

# Create the 'Players' table 
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
    conn = sqlite3.connect('players.db')  
    cursor=conn.cursor()
    cursor.execute("""UPDATE Players 
                   SET Exp= Exp+?
                   WHERE user_id =?
                   """,(gained_exp,user_id))
    conn.commit()
    conn.close()
def add_user(user_id):
    conn = sqlite3.connect('players.db')  
    cursor=conn.cursor()
    cursor.execute(""" INSERT INTO Players (User_id)
                       VALUES(?)
                   """,(user_id,))
    conn.commit()
    conn.close()
def check_user(user_id):
    conn=sqlite3.connect('players.db')
    cursor=conn.cursor()
    cursor.execute(""" 
                   SELECT EXISTS(SELECT 1 FROM Players WHERE User_id =?)

    """,(user_id,))
    exists=cursor.fetchone()[0]
    return exists
    conn.close()