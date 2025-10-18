# models/database.py
import sqlite3
import os

DB_PATH = "data/characters.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            race TEXT,
            subrace TEXT,
            background TEXT,
            class TEXT,
            subclass TEXT,
            level INTEGER,
            hp INTEGER,
            ac INTEGER,
            stats_method TEXT
        )
        ''')
        conn.commit()

def create_character(data: dict):
    """Crea un personaje nuevo en la base de datos."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO characters
            (user_id, name, race, subrace, background, class, subclass, level, hp, ac, stats_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["user_id"],
            data["name"],
            data["race"],
            data.get("subrace"),
            data["background"],
            data["class"],
            data.get("subclass"),
            data["level"],
            data["hp"],
            data["ac"],
            data["stats_method"]
        ))
        conn.commit()
        return c.lastrowid  # ID interno (no se muestra al usuario)

def get_character_by_user(user_id: str):
    """Obtiene el personaje del usuario (por ahora 1 por usuario)."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM characters WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "race": row[3],
                "subrace": row[4],
                "background": row[5],
                "class": row[6],
                "subclass": row[7],
                "level": row[8],
                "hp": row[9],
                "ac": row[10],
                "stats_method": row[11]
            }
        return None

def delete_character_by_user(user_id: str):
    """Borra el personaje de un usuario."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM characters WHERE user_id = ?', (user_id,))
        conn.commit()
