import discord
from discord.ext import commands
import requests
from models import database  # 👈 para guardar en SQLite

class CharacterCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="importar_link", help="Importa un personaje desde un link público de Nivel20")
    async def importar_link(self, ctx, url: str):
        """Importa la ficha de un personaje directamente desde un enlace JSON de Nivel20"""

        # ✅ Validar URL base
        if not url.startswith("https://nivel20.com/"):
            await ctx.send("❌ El link debe comenzar con `https://nivel20.com/`.")
            return

        # ✅ Si el link no termina en .json, lo corregimos automáticamente
        if not url.endswith(".json"):
            url = url.rstrip("/") + ".json"

        # 🧠 Descargar JSON
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            await ctx.send(f"❌ No se pudo descargar el personaje. Error: {e}")
            return

        # --- Parsear datos principales ---
        try:
            info = data["printable_hash"]["info"]
            abilities = data["printable_hash"]["ability"]
            armor = data["printable_hash"]["armor"]
            speed = data["printable_hash"]["speed"]

            nombre = info["name"]
            raza = info["race_name"]
            clase = info["level_desc"]
            nivel = info["level"]
            hp = info["hit_points"]
            ca = armor["normal"]
            velocidad = speed["total"]

            fuerza = abilities["fue"]["total"]
            destreza = abilities["des"]["total"]
            constitucion = abilities["con"]["total"]
            inteligencia = abilities["int"]["total"]
            sabiduria = abilities["sab"]["total"]
            carisma = abilities["car"]["total"]
        except KeyError as e:
            await ctx.send(f"❌ No se pudo leer la estructura del personaje (clave faltante: {e}).")
            return

        # --- Guardar en base de datos ---
        try:
            database.save_character(str(ctx.author.id), {
                "name": nombre,
                "race": raza,
                "class": clase,
                "level": nivel,
                "hp": hp,
                "ac": ca,
                "str": fuerza,
                "dex": destreza,
                "con": constitucion,
                "int": inteligencia,
                "wis": sabiduria,
                "cha": carisma
            })
        except Exception as e:
            await ctx.send(f"⚠️ Personaje importado pero no se pudo guardar en la base de datos: {e}")
            return

        # --- Embed con datos del personaje ---
        embed = discord.Embed(
            title=f"✅ Personaje importado: {nombre}",
            description=f"{raza} - {clase} (Nivel {nivel})",
            color=discord.Color.green()
        )
        embed.add_field(name="❤️ HP", value=str(hp))
        embed.add_field(name="🛡 CA", value=str(ca))
        embed.add_field(name="🏃 Velocidad", value=f"{velocidad} ft")

        stats = [
            ("Fuerza", fuerza),
            ("Destreza", destreza),
            ("Constitución", constitucion),
            ("Inteligencia", inteligencia),
            ("Sabiduría", sabiduria),
            ("Carisma", carisma)
        ]
        for nombre_stat, valor in stats:
            mod = (valor - 10) // 2
            signo = "+" if mod >= 0 else ""
            embed.add_field(name=nombre_stat, value=f"{valor} ({signo}{mod})", inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CharacterCommands(bot))

