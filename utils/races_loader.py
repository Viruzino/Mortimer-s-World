import json
import os

# Ruta del archivo races.json dentro de /data
RACES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'races.json')

# Cache de razas cargadas
_races_data = None

def _load_races():
    """Carga el JSON de razas una sola vez (lazy load)."""
    global _races_data
    if _races_data is None:
        with open(RACES_FILE, 'r', encoding='utf-8') as f:
            _races_data = json.load(f)
    return _races_data

def get_available_races(nivel_personaje: int = 1):
    """
    Devuelve una lista de razas disponibles según el nivel.
    Filtra por el campo 'availability' (✅, ⚠️ o ❌).
    """
    races = _load_races()
    disponibles = []

    for race_name, race_info in races.items():
        availability = race_info.get("availability", "❌")
        if availability == "✅":
            disponibles.append(race_name)
        elif availability == "⚠️" and nivel_personaje >= 5:
            disponibles.append(race_name)
        # ❌ no se incluyen
    return sorted(disponibles)

def get_subraces_for_race(race_name: str, nivel_personaje: int = 1):
    """
    Devuelve la lista de subrazas disponibles para una raza específica.
    Si no hay subrazas, devuelve una lista vacía.
    """
    races = _load_races()
    race_info = races.get(race_name)
    if not race_info:
        return []

    subraces = race_info.get("subraces", {})
    disponibles = []

    for subrace_name, subrace_info in subraces.items():
        availability = subrace_info.get("availability", "❌")
        if availability == "✅":
            disponibles.append(subrace_name)
        elif availability == "⚠️" and nivel_personaje >= 5:
            disponibles.append(subrace_name)
    return sorted(disponibles)

def race_exists(race_name: str) -> bool:
    """Verifica si una raza existe en la base de datos."""
    races = _load_races()
    return race_name in races

def subrace_exists(race_name: str, subrace_name: str) -> bool:
    """Verifica si una subraza existe para una raza dada."""
    races = _load_races()
    race_info = races.get(race_name)
    if not race_info:
        return False
    subraces = race_info.get("subraces", {})
    return subrace_name in subraces
