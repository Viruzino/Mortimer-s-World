import discord
from discord import app_commands
from discord.ext import commands
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

@app_commands.guild_only()
class PersonajeGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="personaje", description="Comandos relacionados con tu personaje")

    # ✨ Crear personaje con opciones predefinidas
    @app_commands.command(name="crear", description="Crea un nuevo personaje")
    @app_commands.describe(
        nombre="Nombre de tu personaje",
        metodo="Método para generar estadísticas",
        raza="Raza del personaje",
        subraza="Subraza (opcional)",
        trasfondo="Trasfondo",
        clase="Clase",
        subclase="Subclase (opcional)"
    )
    @app_commands.choices(
        metodo=[
            app_commands.Choice(name="Tirada de Dados (4d6, descartar 1)", value="tirada"),
            app_commands.Choice(name="Puntos Estándar (15,14,13,12,10,8)", value="puntos"),
            app_commands.Choice(name="Compra por Puntos (27)", value="compra"),
        ],
        raza=[
            app_commands.Choice(name="Humano", value="Humano"),
            app_commands.Choice(name="Elfo", value="Elfo"),
            app_commands.Choice(name="Enano", value="Enano"),
            app_commands.Choice(name="Tiefling", value="Tiefling"),
        ],
        subraza=[
            app_commands.Choice(name="Ninguna", value="Ninguna"),
            app_commands.Choice(name="Alto Elfo", value="Alto Elfo"),
            app_commands.Choice(name="Drow", value="Drow"),
            app_commands.Choice(name="Enano de las Colinas", value="Enano de las Colinas"),
            app_commands.Choice(name="Enano de las Montañas", value="Enano de las Montañas"),
        ],
        trasfondo=[
            app_commands.Choice(name="Noble", value="Noble"),
            app_commands.Choice(name="Criminal", value="Criminal"),
            app_commands.Choice(name="Sabio", value="Sabio"),
        ],
        clase=[
            app_commands.Choice(name="Guerrero", value="Guerrero"),
            app_commands.Choice(name="Mago", value="Mago"),
            app_commands.Choice(name="Pícaro", value="Pícaro"),
            app_commands.Choice(name="Brujo", value="Brujo"),
        ],
        subclase=[
            app_commands.Choice(name="Ninguna", value="Ninguna"),
            app_commands.Choice(name="Campeón (Guerrero)", value="Campeón"),
            app_commands.Choice(name="Evocador (Mago)", value="Evocador"),
            app_commands.Choice(name="Ladrón (Pícaro)", value="Ladrón"),
        ]
    )
    async def crear(
        self,
        interaction: discord.Interaction,
        nombre: str,
        metodo: app_commands.Choice[str],
        raza: app_commands.Choice[str],
        subraza: app_commands.Choice[str],
        trasfondo: app_commands.Choice[str],
        clase: app_commands.Choice[str],
        subclase: app_commands.Choice[str],
    ):
        # Importar aquí para evitar dependencias circulares
        from cogs.character_creation import crear_personaje_db

        user_id = str(interaction.user.id)

        personaje = crear_personaje_db(
            user_id,
            nombre,
            metodo.value,
            raza.value,
            subraza.value,
            trasfondo.value,
            clase.value,
            subclase.value
        )

        embed = discord.Embed(
            title=f"✅ Personaje Creado: {personaje['name']}",
            description=f"{personaje['race']} {personaje['class']} - Nivel 1",
            color=discord.Color.green()
        )
        embed.add_field(name="Método Stats", value=metodo.name, inline=False)
        embed.add_field(
            name="🎲 Estadísticas Generadas",
            value=(
                f"**FUE** {personaje['str']} | "
                f"**DES** {personaje['dex']} | "
                f"**CON** {personaje['con']} | "
                f"**INT** {personaje['int_stat']} | "
                f"**SAB** {personaje['wis']} | "
                f"**CAR** {personaje['cha']}"
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

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
