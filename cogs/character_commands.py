import discord
from discord.ext import commands
import random
from typing import Dict, List

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

class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.creator = CharacterCreator()
        self.character_creation = {}

    @commands.command(
        name='crear_personaje',
        help='Inicia la creación de un personaje',
        description='Muestra los métodos disponibles para crear un personaje'
    )
    async def crear_personaje(self, ctx, metodo: str = None):
        """Inicia la creación de un personaje - Elige método de generación de stats"""
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
                value="**Tirada de Dados**: 4d6, descarta el más bajo\n6 veces para generar tus stats",
                inline=False
            )
            
            embed.add_field(
                name=f"💰 `{self.bot.command_prefix}crear_personaje compra`",
                value="**Compra por Puntos**: 27 puntos para comprar stats\nCostos: 8(0), 9(1), 10(2), 11(3), 12(4), 13(5), 14(7), 15(9)",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return

        metodo = metodo.lower()
        user_id = str(ctx.author.id)
        
        if metodo == "puntos":
            resultado = self.creator.metodo_puntos_estandar()
            
            embed = discord.Embed(
                title="🏆 Método: Puntos Estándar",
                description=resultado['descripcion'],
                color=discord.Color.green()
            )
            
            self.character_creation[user_id] = {
                'metodo': 'puntos',
                'puntos_base': resultado['puntos_base'],
                'paso_actual': 'asignar_stats'
            }
            
            embed.add_field(
                name="📝 Próximo Paso",
                value=f"Usa `{self.bot.command_prefix}asignar_stats 15 14 13 12 10 8`\n(Ajusta el orden según prefieras)",
                inline=False
            )
            
        elif metodo == "tirada":
            resultado = self.creator.metodo_tirada_dados()
            
            embed = discord.Embed(
                title="🎲 Método: Tirada de Dados",
                color=discord.Color.orange()
            )
            
            # Mostrar tiradas detalladas
            detalles = ""
            for i, tirada in enumerate(resultado['tiradas_detalladas']):
                detalles += f"**Tirada {i+1}:** {tirada['tirada']} → descarta {tirada['descartado']} = **{tirada['total']}**\n"
            
            embed.add_field(
                name="Resultados de las Tiradas",
                value=detalles,
                inline=False
            )
            
            stats_str = ", ".join(map(str, resultado['stats_finales']))
            embed.add_field(
                name="🎯 Stats Generados",
                value=stats_str,
                inline=False
            )
            
            self.character_creation[user_id] = {
                'metodo': 'tirada',
                'stats_base': resultado['stats_finales'],
                'paso_actual': 'asignar_stats'
            }
            
            embed.add_field(
                name="📝 Próximo Paso",
                value=f"Usa `{self.bot.command_prefix}asignar_stats {stats_str}` para asignar estos valores",
                inline=False
            )
            
        elif metodo == "compra":
            embed = discord.Embed(
                title="💰 Método: Compra por Puntos",
                description="Sistema de compra con 27 puntos. Costos: 8(0), 9(1), 10(2), 11(3), 12(4), 13(5), 14(7), 15(9)",
                color=discord.Color.gold()
            )
            
            self.character_creation[user_id] = {
                'metodo': 'compra',
                'puntos_disponibles': 27,
                'paso_actual': 'comprar_stats'
            }
            
            embed.add_field(
                name="📝 Próximo Paso",
                value=f"Usa `{self.bot.command_prefix}comprar_stats 14 13 15 12 10 8`\n(Máximo 15, mínimo 8, costo total ≤ 27)",
                inline=False
            )
            
        else:
            await ctx.send("❌ Método no válido. Usa: `puntos`, `tirada` o `compra`")
            return
        
        await ctx.send(embed=embed)

    @commands.command(
        name='asignar_stats',
        help='Asigna stats a las características',
        description='Asigna los valores de stats a características específicas (Fuerza, Destreza, etc.)'
    )
    async def asignar_stats(self, ctx, fuerza: int, destreza: int, constitucion: int, 
                               inteligencia: int, sabiduria: int, carisma: int):
        """Asigna los stats generados a las características específicas"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.character_creation:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Primero inicia la creación con `{self.bot.command_prefix}crear_personaje`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        proceso = self.character_creation[user_id]
        
        if proceso['paso_actual'] != 'asignar_stats':
            embed = discord.Embed(
                title="❌ Error",
                description="No estás en la fase de asignación de stats",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        stats_asignados = {
            'Fuerza': fuerza,
            'Destreza': destreza,
            'Constitución': constitucion,
            'Inteligencia': inteligencia,
            'Sabiduría': sabiduria,
            'Carisma': carisma
        }
        
        # Validar según el método
        if proceso['metodo'] == 'puntos':
            puntos_usados = sorted([fuerza, destreza, constitucion, inteligencia, sabiduria, carisma])
            puntos_esperados = sorted(proceso['puntos_base'])
            
            if puntos_usados != puntos_esperados:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Debes usar exactamente estos valores: {proceso['puntos_base']}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
                
        elif proceso['metodo'] == 'tirada':
            stats_usados = sorted([fuerza, destreza, constitucion, inteligencia, sabiduria, carisma])
            stats_esperados = sorted(proceso['stats_base'])
            
            if stats_usados != stats_esperados:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Debes usar exactamente estos valores: {proceso['stats_base']}",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
        
        # Guardar stats asignados
        proceso['stats_asignados'] = stats_asignados
        proceso['paso_actual'] = 'completado'
        
        # Mostrar resumen
        embed = discord.Embed(
            title="✅ Personaje Creado Exitosamente",
            description="Estadísticas finales de tu personaje:",
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
        
        embed.add_field(
            name="🎯 Próximos Pasos",
            value=f"Usa `{self.bot.command_prefix}mi_personaje` para ver tu ficha completa\n`{self.bot.command_prefix}ayuda` para más comandos",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(
        name='mi_personaje',
        help='Muestra la ficha de tu personaje',
        description='Muestra la información completa de tu personaje actual'
    )
    async def mi_personaje(self, ctx):
        """Muestra la ficha del personaje (placeholder)"""
        embed = discord.Embed(
            title="📜 Tu Personaje",
            description="Funcionalidad en desarrollo - Próximamente mostrará tu ficha completa",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))