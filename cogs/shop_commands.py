import discord
from discord.ext import commands

class ShopCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='tienda',
        help='Muestra las categorías de la tienda',
        description='Lista todas las categorías disponibles en la tienda'
    )
    async def tienda(self, ctx, categoria: str = None):
        """Muestra las categorías de la tienda"""
        if categoria:
            embed = discord.Embed(
                title=f"🏪 Tienda - {categoria.title()}",
                description="Funcionalidad en desarrollo - Próximamente mostrará items de esta categoría",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="🏪 Tienda de Aventureros",
                description="Selecciona una categoría para ver los items disponibles:",
                color=discord.Color.green()
            )
            
            categorias = [
                "Armas", "Armaduras", "Pociones", "Herramientas", 
                "Componentes", "Monturas", "Varios"
            ]
            
            for cat in categorias:
                embed.add_field(
                    name=cat,
                    value=f"`{self.bot.command_prefix}tienda {cat.lower()}`",
                    inline=True
                )
        
        await ctx.send(embed=embed)

    @commands.command(
        name='comprar',
        help='Compra un item de la tienda',
        description='Compra un item específico usando tu oro'
    )
    async def comprar(self, ctx, item: str = None):
        """Compra un item de la tienda"""
        if not item:
            embed = discord.Embed(
                title="❌ Especifica un item",
                description=f"Usa: `{self.bot.command_prefix}comprar <nombre_del_item>`",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="🛒 Compra Realizada",
                description=f"Has comprado: **{item}**\n\nFuncionalidad en desarrollo - Próximamente se descontará el oro",
                color=discord.Color.green()
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ShopCommands(bot))