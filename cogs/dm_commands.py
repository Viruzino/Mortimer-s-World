import discord
from discord.ext import commands

class DMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='dar_exp',
        help='Da EXP a un jugador (Solo DM)',
        description='Otorga experiencia a un jugador específico'
    )
    @commands.has_permissions(administrator=True)
    async def dar_exp(self, ctx, usuario: discord.Member, exp: int):
        """Da EXP a un jugador (Solo DM)"""
        embed = discord.Embed(
            title="⭐ Experiencia Otorgada",
            description=f"Has dado **{exp} EXP** a {usuario.mention}",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='dar_oro',
        help='Da oro a un jugador (Solo DM)',
        description='Otorga monedas de oro a un jugador específico'
    )
    @commands.has_permissions(administrator=True)
    async def dar_oro(self, ctx, usuario: discord.Member, cantidad: int):
        """Da oro a un jugador (Solo DM)"""
        embed = discord.Embed(
            title="💰 Oro Otorgado",
            description=f"Has dado **{cantidad} PO** a {usuario.mention}",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='crear_encuentro',
        help='Crea un encuentro (Solo DM)',
        description='Genera un encuentro con enemigos para los jugadores'
    )
    @commands.has_permissions(administrator=True)
    async def crear_encuentro(self, ctx):
        """Crea un encuentro (Solo DM)"""
        embed = discord.Embed(
            title="⚔️ Generador de Encuentros",
            description="Funcionalidad en desarrollo - Próximamente",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DMCommands(bot))