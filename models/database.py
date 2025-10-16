import sqlite3

DB_PATH = "data/mortimer.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                race TEXT,
                class TEXT,
                level INTEGER,
                hp INTEGER,
                ac INTEGER,
                str INTEGER,
                dex INTEGER,
                con INTEGER,
                int_stat INTEGER,
                wis INTEGER,
                cha INTEGER
            )
        ''')
        conn.commit()

def save_character(user_id, char_data):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO characters 
            (user_id, name, race, class, level, hp, ac, str, dex, con, int_stat, wis, cha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            char_data["name"],
            char_data["race"],
            char_data["class"],
            char_data["level"],
            char_data["hp"],
            char_data["ac"],
            char_data["str"],
            char_data["dex"],
            char_data["con"],
            char_data["int"],
            char_data["wis"],
            char_data["cha"]
        ))
        conn.commit()

def get_character(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM characters WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if not row:
            return None
        keys = ["user_id","name","race","class","level","hp","ac","str","dex","con","int_stat","wis","cha"]
        return dict(zip(keys, row))
