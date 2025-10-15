# models/character.py
import sqlite3
from models.database import get_connection

class Character:
    def __init__(self, id=None, user_id=None, fuerza=10, destreza=10, constitucion=10,
                 inteligencia=10, sabiduria=10, carisma=10):
        self.id = id
        self.user_id = user_id
        self.fuerza = fuerza
        self.destreza = destreza
        self.constitucion = constitucion
        self.inteligencia = inteligencia
        self.sabiduria = sabiduria
        self.carisma = carisma

    def save(self):
        conn = get_connection()
        c = conn.cursor()
        if self.id is None:
            c.execute('''
                INSERT INTO characters (user_id, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.user_id, self.fuerza, self.destreza, self.constitucion,
                  self.inteligencia, self.sabiduria, self.carisma))
            self.id = c.lastrowid
        else:
            c.execute('''
                UPDATE characters
                SET fuerza=?, destreza=?, constitucion=?, inteligencia=?, sabiduria=?, carisma=?
                WHERE id=?
            ''', (self.fuerza, self.destreza, self.constitucion, self.inteligencia,
                  self.sabiduria, self.carisma, self.id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_user(user_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, user_id, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma FROM characters WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return Character(*row)
        return None
