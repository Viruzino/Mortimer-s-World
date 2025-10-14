import random
from typing import Dict, List, Tuple

class CharacterCreator:
    def __init__(self):
        self.stats_order = ['Fuerza', 'Destreza', 'Constitución', 'Inteligencia', 'Sabiduría', 'Carisma']
    
    def metodo_puntos_estandar(self) -> Dict[str, int]:
        puntos = [15, 14, 13, 12, 10, 8]
        return {
            'metodo': 'Puntos Estándar',
            'puntos_base': puntos,
            'descripcion': 'Asigna estos valores: 15, 14, 13, 12, 10, 8'
        }
    
    def metodo_tirada_dados(self) -> Dict[str, any]:
        stats = []
        for _ in range(6):
            dados = [random.randint(1, 6) for _ in range(4)]
            dados_ordenados = sorted(dados, reverse=True)
            total = sum(dados_ordenados[:3])
            stats.append(total)
        
        return {
            'metodo': 'Tirada de Dados',
            'stats_finales': stats,
            'descripcion': f'Resultados: {", ".join(map(str, stats))}'
        }