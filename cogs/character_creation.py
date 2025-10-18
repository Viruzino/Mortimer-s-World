import random
from models import database

def generar_stats(metodo: str):
    if metodo == "puntos":
        return [15, 14, 13, 12, 10, 8]
    elif metodo == "tirada":
        stats = []
        for _ in range(6):
            dados = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
            stats.append(sum(dados[:3]))
        return stats
    elif metodo == "compra":
        # Placeholder por ahora
        return [15, 14, 13, 12, 10, 8]
    else:
        return [10, 10, 10, 10, 10, 10]

def crear_personaje_db(user_id, nombre, metodo, raza, subraza, trasfondo, clase, subclase):
    stats = generar_stats(metodo)
    fuerza, destreza, constitucion, inteligencia, sabiduria, carisma = stats

    personaje_data = {
        "user_id": user_id,
        "name": nombre,
        "race": raza,
        "subrace": subraza if subraza != "Ninguna" else None,
        "background": trasfondo,
        "class": clase,
        "subclass": subclase if subclase != "Ninguna" else None,
        "level": 1,
        "hp": 10,
        "ac": 10,
        "stats_method": metodo,
        "str": fuerza,
        "dex": destreza,
        "con": constitucion,
        "int_stat": inteligencia,
        "wis": sabiduria,
        "cha": carisma
    }

    database.create_character(personaje_data)
    return personaje_data
