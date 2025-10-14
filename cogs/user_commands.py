import discord
from discord.ext import commands

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ping',
        help='Verifica la latencia del bot',
        description='Comando para verificar si el bot está funcionando y mostrar la latencia'
    )
    async def ping(self, ctx):
        """Verifica la latencia del bot"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latencia: **{latency}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='info',
        help='Muestra información sobre el bot',
        description='Muestra información general sobre el bot de D&D'
    )
    async def dnd_info(self, ctx):
        """Muestra información sobre el bot"""
        embed = discord.Embed(
            title="🎲 Mortimer's World - Bot de D&D",
            description="Bot especializado para partidas de Dungeons & Dragons 5e",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Estadísticas",
            value=f"• Latencia: {round(self.bot.latency * 1000)}ms\n• Servidores: {len(self.bot.guilds)}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Prefijo",
            value=f"`{self.bot.command_prefix}`",
            inline=True
        )
        
        embed.add_field(
            name="📋 Características",
            value="• Creación de personajes\n• Sistema de tienda\n• Gestión de inventario\n• Comandos para DM",
            inline=False
        )
        
        embed.set_footer(text="Usa dnd_ayuda para ver todos los comandos")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCommands(bot))