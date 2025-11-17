import discord
from discord import app_commands
from discord.ext import commands
from models import database

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


@app_commands.guild_only()
@app_commands.command(name="dm_dar_oro", description="Otorga oro a un personaje usando su ID de ficha")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    personaje_id="ID del personaje (se muestra en el autocompletado)",
    cantidad="Cantidad de piezas de oro a otorgar"
)
async def dm_dar_oro(
    interaction: discord.Interaction,
    personaje_id: str,
    cantidad: app_commands.Range[int, 1, 100000]
):
    try:
        _, nuevo_total = database.adjust_gold(personaje_id, cantidad)
    except ValueError as exc:
        await interaction.response.send_message(
            f"No se pudo actualizar el oro: {exc}",
            ephemeral=True
        )
        return

    member_mention = None
    if interaction.guild:
        try:
            member = interaction.guild.get_member(int(personaje_id))
        except (ValueError, TypeError):
            member = None
        if member:
            member_mention = member.mention

    descripcion = f"Se dieron **{cantidad} PO**."
    if member_mention:
        descripcion = f"A {member_mention} se le dieron **{cantidad} PO**."

    embed = discord.Embed(
        title="Oro otorgado",
        description=f"{descripcion}\nNuevo total: **{nuevo_total} PO**.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@dm_dar_oro.autocomplete("personaje_id")
async def personaje_id_autocomplete(interaction: discord.Interaction, current: str):
    term = current.strip()
    matches = database.search_characters_by_name(term, limit=25)
    choices = []
    guild = interaction.guild
    for row in matches:
        display = row["name"]
        extra = row["user_id"]
        member = None
        if guild:
            try:
                member = guild.get_member(int(row["user_id"]))
            except (ValueError, TypeError):
                member = None
        if member:
            display = f"{row['name']} - {member.display_name}"
        else:
            display = f"{row['name']} (ID: {row['user_id']})"
        choices.append(app_commands.Choice(name=display[:100], value=row["user_id"]))
    if not choices and term:
        trimmed = term[:100]
        choices.append(app_commands.Choice(name=f"Usar ID {trimmed}", value=term))
    return choices


async def setup(bot):
    await bot.add_cog(DMCommands(bot))
    bot.tree.add_command(dm_dar_oro)
