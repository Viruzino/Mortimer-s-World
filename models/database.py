# models/database.py
import sqlite3

DB_PATH = "data/mortimer.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        fuerza INTEGER,
        destreza INTEGER,
        constitucion INTEGER,
        inteligencia INTEGER,
        sabiduria INTEGER,
        carisma INTEGER
    )''')
    conn.commit()
    conn.close()
