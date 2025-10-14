class Character:
    def __init__(self, user_id: int, nombre: str, raza: str, clase: str):
        self.user_id = user_id
        self.nombre = nombre
        self.raza = raza
        self.clase = clase
        self.nivel = 1
        self.exp = 0
        self.trasfondo = ""
        self.stats = {
            'fuerza': 10, 'destreza': 10, 'constitucion': 10,
            'inteligencia': 10, 'sabiduria': 10, 'carisma': 10
        }
        self.dinero = {'oro': 0, 'plata': 0, 'cobre': 0}
        self.inventario = []
        self.peso_actual = 0
        self.peso_maximo = 0

    def calcular_nivel(self):
        from utils.config import LEVEL_THRESHOLDS
        for nivel, exp in reversed(LEVEL_THRESHOLDS.items()):
            if self.exp >= exp:
                self.nivel = nivel
                return nivel
        return 1