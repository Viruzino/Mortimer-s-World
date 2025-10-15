import discord
from discord.ext import commands
import random
import sqlite3
from typing import Dict, List

# ─────────────────────────────────────────────
# 📌 Clase para manejar la lógica de creación
# ─────────────────────────────────────────────
class CharacterCreator:
    def __init__(self):
        self.stats_order = ['Fuerza', 'Destreza', 'Constitución', 'Inteligencia', 'Sabiduría', 'Carisma']
    
    def metodo_puntos_estandar(self) -> Dict:
        puntos = [15, 14, 13, 12, 10, 8]
        return {
            'metodo': 'Puntos Estándar',
            'puntos_base': puntos,
            'descripcion': 'Asigna estos valores a tus características: 15, 14, 13, 12, 10, 8'
        }
    
    def metodo_tirada_dados(self) -> Dict:
        stats = []
        tiradas_detalladas = []
        
        for i in range(6):
            dados = [random.randint(1, 6) for _ in range(4)]
            dados_ordenados = sorted(dados, reverse=True)
            total = sum(dados_ordenados[:3])
            
            stats.append(total)
            tiradas_detalladas.append({
                'tirada': dados,
                'descartado': dados_ordenados[3],
                'total': total
            })
        
        return {
            'metodo': 'Tirada de Dados',
            'stats_finales': stats,
            'tiradas_detalladas': tiradas_detalladas
        }
    
    def calcular_modificador(self, valor: int) -> int:
        return (valor - 10) // 2

# ─────────────────────────────────────────────
# 📌 Clase principal del comando
# ─────────────────────────────────────────────
class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.creator = CharacterCreator()
        self.character_creation = {}

        # Conexión a la base de datos
        self.conn = sqlite3.connect('personajes.db')
        self.cursor = self.conn.cursor()
        self._crear_tabla_personajes()

    def _crear_tabla_personajes(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS personajes (
                user_id TEXT PRIMARY KEY,
                fuerza INTEGER,
                destreza INTEGER,
                constitucion INTEGER,
                inteligencia INTEGER,
                sabiduria INTEGER,
                carisma INTEGER,
                metodo TEXT
            )
        ''')
        self.conn.commit()

    def _guardar_personaje(self, user_id: str, stats: Dict[str, int], metodo: str):
        self.cursor.execute('''
            INSERT OR REPLACE INTO personajes 
            (user_id, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma, metodo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            stats['Fuerza'],
            stats['Destreza'],
            stats['Constitución'],
            stats['Inteligencia'],
            stats['Sabiduría'],
            stats['Carisma'],
            metodo
        ))
        self.conn.commit()

    def _obtener_personaje(self, user_id: str):
        self.cursor.execute('SELECT * FROM personajes WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()

    # ────────────────
    # 📜 CREAR PERSONAJE
    # ────────────────
    @commands.command(name='crear_personaje', help='Inicia la creación de un personaje')
    async def crear_personaje(self, ctx, metodo: str = None):
        if metodo is None:
            embed = discord.Embed(
                title="🎭 Creación de Personaje - Métodos de Stats",
                description="Elige un método para generar tus características:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name=f"🏆 `{self.bot.command_prefix}crear_personaje puntos`",
                value="**Puntos Estándar**: 15, 14, 13, 12, 10, 8\nAsigna estos valores a las características que prefieras",
                inline=False
            )
            
            embed.add_field(
                name=f"🎲 `{self.bot.command_prefix}crear_personaje tirada`",
                value="**Tirada de Dados**: 4d6, descarta el más bajo (x6)",
                inline=False
            )
            
            embed.add_field(
                name=f"💰 `{self.bot.command_prefix}crear_personaje compra`",
                value="**Compra por Puntos** (próximamente)",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return

        metodo = metodo.lower()
        user_id = str(ctx.author.id)
        
        if metodo == "puntos":
            resultado = self.creator.metodo_puntos_estandar()
            self.character_creation[user_id] = {
                'metodo': 'puntos',
                'puntos_base': resultado['puntos_base'],
                'paso_actual': 'asignar_stats'
            }
            embed = discord.Embed(
                title="🏆 Método: Puntos Estándar",
                description=resultado['descripcion'],
                color=discord.Color.green()
            )
            embed.add_field(
                name="📝 Próximo Paso",
                value=f"Usa `{self.bot.command_prefix}asignar_stats 15 14 13 12 10 8` (en el orden que quieras)",
                inline=False
            )
            await ctx.send(embed=embed)

        elif metodo == "tirada":
            resultado = self.creator.metodo_tirada_dados()
            self.character_creation[user_id] = {
                'metodo': 'tirada',
                'stats_base': resultado['stats_finales'],
                'paso_actual': 'asignar_stats'
            }
            detalles = "\n".join(
                [f"**Tirada {i+1}:** {t['tirada']} → descarta {t['descartado']} = **{t['total']}**"
                 for i, t in enumerate(resultado['tiradas_detalladas'])]
            )
            stats_str = ", ".join(map(str, resultado['stats_finales']))
            embed = discord.Embed(
                title="🎲 Método: Tirada de Dados",
                color=discord.Color.orange()
            )
            embed.add_field(name="Resultados", value=detalles, inline=False)
            embed.add_field(
                name="🎯 Stats Generados",
                value=stats_str,
                inline=False
            )
            embed.add_field(
                name="📝 Próximo Paso",
                value=f"Usa `{self.bot.command_prefix}asignar_stats {stats_str}` para asignar estos valores",
                inline=False
            )
            await ctx.send(embed=embed)

        else:
            await ctx.send("❌ Método no válido. Usa: `puntos` o `tirada`")
            return

    # ────────────────
    # 📜 ASIGNAR STATS
    # ────────────────
    @commands.command(name='asignar_stats', help='Asigna stats a las características')
    async def asignar_stats(self, ctx, fuerza: int, destreza: int, constitucion: int, inteligencia: int, sabiduria: int, carisma: int):
        user_id = str(ctx.author.id)
        
        if user_id not in self.character_creation:
            await ctx.send("❌ Primero inicia la creación con `!crear_personaje`")
            return
        
        proceso = self.character_creation[user_id]
        stats_asignados = {
            'Fuerza': fuerza,
            'Destreza': destreza,
            'Constitución': constitucion,
            'Inteligencia': inteligencia,
            'Sabiduría': sabiduria,
            'Carisma': carisma
        }

        # Validación
        if proceso['metodo'] == 'puntos':
            if sorted(stats_asignados.values()) != sorted(proceso['puntos_base']):
                await ctx.send(f"❌ Debes usar exactamente estos valores: {proceso['puntos_base']}")
                return
        elif proceso['metodo'] == 'tirada':
            if sorted(stats_asignados.values()) != sorted(proceso['stats_base']):
                await ctx.send(f"❌ Debes usar exactamente estos valores: {proceso['stats_base']}")
                return

        # Guardar en DB
        self._guardar_personaje(user_id, stats_asignados, proceso['metodo'])

        # Embed resumen
        embed = discord.Embed(
            title="✅ Personaje Creado Exitosamente",
            description="Estadísticas finales:",
            color=discord.Color.green()
        )
        for stat, valor in stats_asignados.items():
            modificador = self.creator.calcular_modificador(valor)
            signo = "+" if modificador >= 0 else ""
            embed.add_field(
                name=stat,
                value=f"**{valor}** ({signo}{modificador})",
                inline=True
            )
        await ctx.send(embed=embed)

    # ────────────────
    # 📜 MOSTRAR PERSONAJE
    # ────────────────
    @commands.command(name='mi_personaje', help='Muestra tu personaje actual')
    async def mi_personaje(self, ctx):
        user_id = str(ctx.author.id)
        personaje = self._obtener_personaje(user_id)

        if not personaje:
            await ctx.send("❌ No tenés un personaje creado todavía.")
            return

        # personaje = (user_id, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma, metodo)
        _, fuerza, destreza, constitucion, inteligencia, sabiduria, carisma, metodo = personaje

        embed = discord.Embed(
            title=f"📜 Personaje de {ctx.author.display_name}",
            description=f"Método de creación: **{metodo.capitalize()}**",
            color=discord.Color.blue()
        )

        stats = {
            'Fuerza': fuerza,
            'Destreza': destreza,
            'Constitución': constitucion,
            'Inteligencia': inteligencia,
            'Sabiduría': sabiduria,
            'Carisma': carisma
        }

        for stat, valor in stats.items():
            mod = self.creator.calcular_modificador(valor)
            signo = "+" if mod >= 0 else ""
            embed.add_field(name=stat, value=f"{valor} ({signo}{mod})", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))
