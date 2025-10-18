import discord
from discord import app_commands
from discord.ext import commands
from utils import races_loader
from models import database

# ===========================
# 📌 COMANDOS BÁSICOS
# ===========================

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🧪 Comando de prueba
    @app_commands.command(name="ping", description="Verifica si el bot está funcionando")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! Latencia: {round(self.bot.latency * 1000)} ms")

    # 📚 Ayuda
    @app_commands.command(name="ayuda", description="Muestra todos los comandos disponibles")
    async def ayuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 Ayuda - Mortimer's World D&D Bot",
            description="Lista de comandos disponibles:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🧭 Básicos",
            value="/ping → Verifica el bot\n"
                  "/ayuda → Muestra esta ayuda\n"
                  "/info → Información sobre el bot",
            inline=False
        )
        embed.add_field(
            name="🧍 Personaje",
            value="/personaje crear → Crea un personaje\n"
                  "/personaje mi → Muestra tu ficha\n"
                  "/personaje borrar → Borra tu personaje",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    # 🧠 Info del bot
    @app_commands.command(name="info", description="Información sobre el bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎲 Mortimer's World D&D Bot",
            description="Bot especializado para Dungeons & Dragons 5e",
            color=discord.Color.green()
        )
        embed.add_field(name="Versión", value="1.0.0", inline=True)
        embed.add_field(name="Servidores", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Latencia", value=f"{round(self.bot.latency * 1000)} ms", inline=True)
        await interaction.response.send_message(embed=embed)

# ===========================
# 🧍 GRUPO DE COMANDOS: /personaje
# ===========================

import discord
from discord import app_commands
from discord.ext import commands
from utils import races_loader  # 👈 Importamos el loader de razas
from models import database

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Comando de prueba
    @app_commands.command(name="ping", description="Verifica si el bot está funcionando")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! Latencia: {round(self.bot.latency * 1000)}ms")

# 🧠 Grupo de comandos /personaje
@app_commands.guild_only()
class PersonajeGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="personaje", description="Comandos relacionados con tu personaje")

    # --- AUTOCOMPLETADO ---
    async def race_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete dinámico para la raza."""
        races = races_loader.get_available_races()
        return [
            app_commands.Choice(name=race, value=race)
            for race in races if current.lower() in race.lower()
        ][:25]

    async def subrace_autocomplete(self, interaction: discord.Interaction, current: str):
        """Autocomplete dinámico para subrazas en función de la raza elegida."""
        # Recuperar la raza que el usuario escribió
        chosen_race = interaction.namespace.race
        subraces = races_loader.get_subraces_for_race(chosen_race)
        return [
            app_commands.Choice(name=sub, value=sub)
            for sub in subraces if current.lower() in sub.lower()
        ][:25]

    # --- CREAR PERSONAJE ---
    @app_commands.command(name="crear", description="Crea un nuevo personaje")
    @app_commands.describe(
        nombre="Nombre de tu personaje",
        raza="Selecciona la raza",
        subraza="Selecciona la subraza (si corresponde)"
    )
    @app_commands.autocomplete(raza=race_autocomplete, subraza=subrace_autocomplete)
    async def crear(self, interaction: discord.Interaction, nombre: str, raza: str, subraza: str = None):
        user_id = str(interaction.user.id)

        # Guardar en base de datos
        with database.get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO characters (user_id, name, race, subrace, level)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, nombre, raza, subraza or "", 1))
            conn.commit()

        embed = discord.Embed(
            title="🎭 Personaje Creado",
            description=f"**{nombre}** — {raza}" + (f" ({subraza})" if subraza else ""),
            color=discord.Color.green()
        )
        embed.add_field(name="Nivel", value="1", inline=True)
        embed.add_field(name="Usuario", value=interaction.user.mention, inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
    bot.tree.add_command(PersonajeGroup())

    # 📜 Mostrar personaje
    @app_commands.command(name="mi", description="Muestra tu personaje actual")
    async def mi(self, interaction: discord.Interaction):
        personaje = database.get_character(str(interaction.user.id))
        if not personaje:
            await interaction.response.send_message(
                "❌ No tenés ningún personaje guardado. Usá `/personaje crear` o `!importar_link <URL>`.",
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

    # 🧹 Borrar personaje (igual que antes)
    @app_commands.command(name="borrar", description="Borra tu personaje guardado")
    async def borrar(self, interaction: discord.Interaction):
        personaje = database.get_character(str(interaction.user.id))
        if not personaje:
            await interaction.response.send_message(
                "❌ No tenés ningún personaje guardado para borrar.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="⚠️ Confirmación requerida",
            description=f"¿Querés borrar **{personaje['name']}**? Esta acción no se puede deshacer.",
            color=discord.Color.red()
        )

        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.confirmed = False

            @discord.ui.button(label="✅ Confirmar", style=discord.ButtonStyle.danger)
            async def confirm(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                self.confirmed = True
                self.stop()
                await interaction_btn.response.defer()

            @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
            async def cancel(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
                self.confirmed = False
                self.stop()
                await interaction_btn.response.defer()

        view = ConfirmView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.confirmed:
            with database.get_connection() as conn:
                c = conn.cursor()
                c.execute('DELETE FROM characters WHERE user_id = ?', (str(interaction.user.id),))
                conn.commit()
            await interaction.followup.send(f"🧹 Personaje **{personaje['name']}** eliminado correctamente.", ephemeral=True)
        else:
            await interaction.followup.send("❎ Operación cancelada. Tu personaje no fue borrado.", ephemeral=True)


# ===========================
# ⚡ REGISTRO DE COGS
# ===========================

async def setup(bot):
    # Comandos slash globales
    await bot.add_cog(SlashCommands(bot))
    # Grupo de comandos /personaje
    bot.tree.add_command(PersonajeGroup())
