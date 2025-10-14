import discord
from discord.ext import commands

class HelpCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ayuda',
        help='Muestra todos los comandos disponibles',
        description='Sistema de ayuda del bot de D&D'
    )
    async def ayuda(self, ctx, categoria: str = None):
        """Sistema de ayuda personalizado"""
        prefix = self.bot.command_prefix
        
        if not categoria:
            embed = discord.Embed(
                title="🎲 Ayuda - Mortimer's World D&D Bot",
                description=f"Prefijo del bot: `{prefix}`\n\nSelecciona una categoría para ver comandos específicos:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="👤 Comandos de Usuario",
                value=f"`{prefix}ayuda usuario` - Comandos generales",
                inline=False
            )
            
            embed.add_field(
                name="🎭 Comandos de Personaje",
                value=f"`{prefix}ayuda personaje` - Creación y gestión de personajes",
                inline=False
            )
            
            embed.add_field(
                name="🏪 Comandos de Tienda",
                value=f"`{prefix}ayuda tienda` - Sistema de compra y venta",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Comandos de DM",
                value=f"`{prefix}ayuda dm` - Herramientas para Dungeon Master",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        elif categoria.lower() == "usuario":
            embed = discord.Embed(
                title="👤 Comandos de Usuario",
                color=discord.Color.green()
            )
            
            comandos = [
                (f"{prefix}ping", "Verifica la latencia del bot"),
                (f"{prefix}info", "Información general del bot"),
                (f"{prefix}ayuda", "Muestra este mensaje de ayuda")
            ]
            
            for comando, descripcion in comandos:
                embed.add_field(name=comando, value=descripcion, inline=False)
                
            await ctx.send(embed=embed)
            
        elif categoria.lower() == "personaje":
            embed = discord.Embed(
                title="🎭 Comandos de Personaje",
                color=discord.Color.orange()
            )
            
            comandos = [
                (f"{prefix}crear_personaje", "Inicia la creación de personaje"),
                (f"{prefix}asignar_stats", "Asigna stats a características"),
                (f"{prefix}mi_personaje", "Muestra tu ficha de personaje")
            ]
            
            for comando, descripcion in comandos:
                embed.add_field(name=comando, value=descripcion, inline=False)
                
            await ctx.send(embed=embed)
            
        elif categoria.lower() == "tienda":
            embed = discord.Embed(
                title="🏪 Comandos de Tienda",
                color=discord.Color.gold()
            )
            
            comandos = [
                (f"{prefix}tienda", "Muestra categorías de la tienda"),
                (f"{prefix}comprar", "Compra un item específico")
            ]
            
            for comando, descripcion in comandos:
                embed.add_field(name=comando, value=descripcion, inline=False)
                
            await ctx.send(embed=embed)
            
        elif categoria.lower() == "dm":
            embed = discord.Embed(
                title="🎮 Comandos de Dungeon Master",
                color=discord.Color.purple()
            )
            
            comandos = [
                (f"{prefix}dar_exp", "Da EXP a un jugador"),
                (f"{prefix}dar_oro", "Da oro a un jugador"),
                (f"{prefix}crear_encuentro", "Genera un encuentro")
            ]
            
            for comando, descripcion in comandos:
                embed.add_field(name=comando, value=descripcion, inline=False)
                
            embed.set_footer(text="⚠️ Requiere permisos de administrador")
            await ctx.send(embed=embed)
            
        else:
            embed = discord.Embed(
                title="❌ Categoría no encontrada",
                description="Categorías disponibles: usuario, personaje, tienda, dm",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommands(bot))