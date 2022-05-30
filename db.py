import sqlite3
con = sqlite3.connect('echoall.db')
cursor = con.cursor()
def create():
    cursor.execute("CREATE TABLE IF NOT EXISTS users(name TEXT, id INT, msgs INT, ban INT)")
    con.commit()
def get(val_name, id):
    val = cursor.execute(f"SELECT {val_name} FROM users WHERE id={id}")[0]
    if cursor.fetchone() == None:
        return None
    else:
        return val
def set(val_name, new_val, id):
    cursor.execute(f"UPDATE users SET {val_name}={new_val} WHERE id={id}")
    con.commit()
def all():
    cursor.execute(f"SELECT id FROM users")
    return cursor.fetchall()
def insert(name, id):
    cursor.execute(f'INSERT INTO users VALUES ("{name}", {id}, 0, 0)')
    con.commit()