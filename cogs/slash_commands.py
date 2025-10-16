import discord
from discord import app_commands
from discord.ext import commands
from models import database

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # COMANDO DE PRUEBA MUY SIMPLE
    @app_commands.command(name="ping", description="Verifica si el bot está funcionando")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! Latencia: {round(self.bot.latency * 1000)}ms")

    # COMANDO DE AYUDA
    @app_commands.command(name="ayuda", description="Muestra todos los comandos disponibles")
    async def ayuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 Ayuda - Mortimer's World D&D Bot",
            description="Comandos disponibles:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Comandos Básicos",
            value="/ping - Verifica el bot\n/ayuda - Muestra esta ayuda\n/info - Información del bot",
            inline=False
        )
        
        embed.add_field(
            name="Comandos de Personaje", 
            value="/crear_personaje - Crea un personaje\n/mi_personaje - Muestra tu personaje",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    # COMANDO DE INFORMACIÓN
    @app_commands.command(name="info", description="Información sobre el bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 Mortimer's World D&D Bot",
            description="Bot especializado para Dungeons & Dragons 5e",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Versión", value="1.0.0", inline=True)
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latencia", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # COMANDO PARA CREAR PERSONAJE (VERSIÓN SIMPLIFICADA)
    @app_commands.command(name="crear_personaje", description="Crea un nuevo personaje de D&D")
    @app_commands.describe(
        nombre="Nombre de tu personaje",
        clase="Clase de tu personaje"
    )
    async def crear_personaje(self, interaction: discord.Interaction, nombre: str, clase: str = "Aventurero"):
        embed = discord.Embed(
            title="🎭 Personaje Creado",
            description=f"**{nombre}** el {clase}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="Nivel", value="1", inline=True)
        embed.add_field(name="EXP", value="0", inline=True)
        embed.add_field(name="PV", value="Por calcular", inline=True)
        
        await interaction.response.send_message(embed=embed)

    # COMANDO PARA VER PERSONAJEfrom models import database

    @app_commands.command(name="mi_personaje", description="Muestra tu personaje actual")
    async def mi_personaje(self, interaction: discord.Interaction):
        personaje = database.get_character(str(interaction.user.id))

        if not personaje:
            await interaction.response.send_message(
                "❌ No tenés ningún personaje guardado. Importá uno con `!importar_link <URL>`.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"📜 {personaje['name']}",
            description=f"{personaje['race']} - {personaje['class']} (Nivel {personaje['level']})",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ HP", value=str(personaje["hp"]))
        embed.add_field(name="🛡 CA", value=str(personaje["ac"]))

        stats = [
    ("Fuerza", "str"),
    ("Destreza", "dex"),
    ("Constitución", "con"),
    ("Inteligencia", "int_stat"),
    ("Sabiduría", "wis"),
    ("Carisma", "cha")
]


        for nombre_stat, clave in stats:
            valor = personaje[clave]
            mod = (valor - 10) // 2
            signo = "+" if mod >= 0 else ""
            embed.add_field(name=nombre_stat, value=f"{valor} ({signo}{mod})", inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(SlashCommands(bot))