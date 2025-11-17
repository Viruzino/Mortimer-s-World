import os
import sqlite3
from typing import Dict, List, Optional, Tuple

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "database.db")


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_database():
    """Crea las tablas necesarias si no existen."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                race TEXT NOT NULL,
                subrace TEXT,
                background TEXT,
                class TEXT NOT NULL,
                subclass TEXT,
                level INTEGER DEFAULT 1,
                hp INTEGER DEFAULT 0,
                ac INTEGER DEFAULT 10,
                str INTEGER DEFAULT 10,
                dex INTEGER DEFAULT 10,
                con INTEGER DEFAULT 10,
                int_stat INTEGER DEFAULT 10,
                wis INTEGER DEFAULT 10,
                cha INTEGER DEFAULT 10,
                stats_method TEXT DEFAULT 'manual',
                gold INTEGER DEFAULT 0
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_name TEXT NOT NULL COLLATE NOCASE,
                quantity INTEGER NOT NULL DEFAULT 1,
                notes TEXT,
                UNIQUE(user_id, item_name)
            )
            """
        )

        _ensure_column(c, "characters", "gold", "INTEGER DEFAULT 0")
        conn.commit()
        print("[DB] Tablas 'characters' e 'inventory' listas.")


def _int_or_default(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _ensure_column(cursor, table: str, column: str, definition: str):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def save_character(user_id: str, data: Dict) -> str:
    """Crea o actualiza el registro de personaje para un usuario."""
    required_fields = ("name", "race", "class")
    for field in required_fields:
        if not data.get(field):
            raise ValueError(f"Falta el campo obligatorio '{field}' para guardar el personaje.")

    payload = {
        "user_id": user_id,
        "name": data.get("name"),
        "race": data.get("race"),
        "subrace": data.get("subrace"),
        "background": data.get("background"),
        "class": data.get("class"),
        "subclass": data.get("subclass"),
        "level": max(1, _int_or_default(data.get("level"), 1)),
        "hp": max(0, _int_or_default(data.get("hp"), 0)),
        "ac": max(0, _int_or_default(data.get("ac"), 10)),
        "str": _int_or_default(data.get("str"), 10),
        "dex": _int_or_default(data.get("dex"), 10),
        "con": _int_or_default(data.get("con"), 10),
        "int_stat": _int_or_default(data.get("int_stat", data.get("int")), 10),
        "wis": _int_or_default(data.get("wis"), 10),
        "cha": _int_or_default(data.get("cha"), 10),
        "stats_method": data.get("stats_method", "manual"),
        "gold": max(0, _int_or_default(data.get("gold"), 0)),
    }

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO characters
            (user_id, name, race, subrace, background, class, subclass, level, hp, ac,
             str, dex, con, int_stat, wis, cha, stats_method, gold)
            VALUES (:user_id, :name, :race, :subrace, :background, :class, :subclass, :level, :hp, :ac,
                    :str, :dex, :con, :int_stat, :wis, :cha, :stats_method, :gold)
            ON CONFLICT(user_id) DO UPDATE SET
                name=excluded.name,
                race=excluded.race,
                subrace=excluded.subrace,
                background=excluded.background,
                class=excluded.class,
                subclass=excluded.subclass,
                level=excluded.level,
                hp=excluded.hp,
                ac=excluded.ac,
                str=excluded.str,
                dex=excluded.dex,
                con=excluded.con,
                int_stat=excluded.int_stat,
                wis=excluded.wis,
                cha=excluded.cha,
                stats_method=excluded.stats_method,
                gold=excluded.gold
            """,
            payload,
        )
        conn.commit()

    return user_id


def create_character(data: Dict):
    """Alias para mantener compatibilidad."""
    return save_character(data["user_id"], data)


def get_character(user_id: str) -> Optional[Dict]:
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT user_id, name, race, subrace, background, class, subclass, level,
                   hp, ac, str, dex, con, int_stat, wis, cha, stats_method
            FROM characters
            WHERE user_id = ?
            """,
            (user_id,),
        )
        row = c.fetchone()

    if not row:
        return None

    keys = [
        "user_id",
        "name",
        "race",
        "subrace",
        "background",
        "class",
        "subclass",
        "level",
        "hp",
        "ac",
        "str",
        "dex",
        "con",
        "int_stat",
        "wis",
        "cha",
        "stats_method",
        "gold",
    ]
    return dict(zip(keys, row))


def get_character_by_user(user_id: str):
    return get_character(user_id)


def delete_character(user_id: str):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM characters WHERE user_id = ?", (user_id,))
        conn.commit()


def delete_character_by_user(user_id: str):
    delete_character(user_id)


# ===========================
# Oro
# ===========================
def get_gold(user_id: str) -> int:
    character = get_character(user_id)
    if not character:
        raise ValueError("No encontramos un personaje guardado para ese usuario.")
    return _int_or_default(character.get("gold"), 0)


def set_gold(user_id: str, amount: int) -> int:
    if amount < 0:
        raise ValueError("El oro no puede ser negativo.")
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE characters SET gold = ? WHERE user_id = ?", (amount, user_id))
        if c.rowcount == 0:
            raise ValueError("No encontramos un personaje guardado para ese usuario.")
        conn.commit()
    return amount


def adjust_gold(user_id: str, delta: int, allow_negative: bool = False) -> Tuple[int, int]:
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT gold FROM characters WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            raise ValueError("No encontramos un personaje guardado para ese usuario.")

        current_gold = _int_or_default(row[0], 0)
        new_gold = current_gold + delta
        if not allow_negative and new_gold < 0:
            raise ValueError("El personaje no tiene suficiente oro.")

        if new_gold < 0:
            new_gold = 0

        c.execute("UPDATE characters SET gold = ? WHERE user_id = ?", (new_gold, user_id))
        conn.commit()

    return current_gold, new_gold


def search_characters_by_name(query: str = "", limit: int = 25) -> List[Dict]:
    pattern = f"%{query}%" if query else "%"
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT user_id, name
            FROM characters
            WHERE name LIKE ?
            ORDER BY name COLLATE NOCASE
            LIMIT ?
            """,
            (pattern, limit),
        )
        rows = c.fetchall()
    return [{"user_id": user_id, "name": name} for user_id, name in rows]


def character_name_exists(name: str, exclude_user_id: Optional[str] = None) -> bool:
    clean_name = (name or "").strip()
    if not clean_name:
        return False

    query = "SELECT 1 FROM characters WHERE lower(name) = lower(?)"
    params: List = [clean_name]
    if exclude_user_id is not None:
        query += " AND user_id != ?"
        params.append(exclude_user_id)
    query += " LIMIT 1"

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(query, tuple(params))
        return c.fetchone() is not None


# ===========================
# Inventario
# ===========================
def add_item_to_inventory(user_id: str, item_name: str, quantity: int = 1, notes: Optional[str] = None):
    if quantity <= 0:
        raise ValueError("La cantidad a agregar debe ser mayor a 0.")

    clean_name = item_name.strip()
    if not clean_name:
        raise ValueError("El nombre del item no puede estar vacio.")

    normalized_notes = notes.strip() if notes else None

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO inventory (user_id, item_name, quantity, notes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, item_name)
            DO UPDATE SET
                quantity = inventory.quantity + excluded.quantity,
                notes = COALESCE(excluded.notes, inventory.notes)
            """,
            (user_id, clean_name, quantity, normalized_notes),
        )
        conn.commit()


def remove_item_from_inventory(user_id: str, item_name: str, quantity: int = 1) -> Tuple[bool, int]:
    if quantity <= 0:
        raise ValueError("La cantidad a eliminar debe ser mayor a 0.")

    target_name = item_name.strip()
    if not target_name:
        return False, 0

    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT id, quantity
            FROM inventory
            WHERE user_id = ? AND item_name = ?
            """,
            (user_id, target_name),
        )
        row = c.fetchone()

        if not row:
            return False, 0

        item_id, current_qty = row
        new_quantity = current_qty - quantity

        if new_quantity > 0:
            c.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id))
        else:
            c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            new_quantity = 0

        conn.commit()
        return True, new_quantity


def get_inventory(user_id: str) -> List[Dict]:
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT item_name, quantity, notes
            FROM inventory
            WHERE user_id = ?
            ORDER BY item_name COLLATE NOCASE
            """,
            (user_id,),
        )
        rows = c.fetchall()

    inventory = []
    for name, qty, notes in rows:
        inventory.append({"item_name": name, "quantity": qty, "notes": notes})
    return inventory


def clear_inventory(user_id: str):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
        conn.commit()
