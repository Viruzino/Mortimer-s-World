from typing import Dict, List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from models import database


def _inventory_embed(title: str, items: List[Dict]) -> discord.Embed:
    embed = discord.Embed(title=title, color=discord.Color.gold())
    if not items:
        embed.description = "No hay items registrados."
        return embed

    for item in items[:25]:
        value = f"Cantidad: {item['quantity']}"
        if item.get("notes"):
            value += f"\nNotas: {item['notes']}"
        embed.add_field(name=item["item_name"], value=value, inline=False)

    if len(items) > 25:
        embed.set_footer(text=f"Mostrando 25 de {len(items)} items.")
    return embed


def _character_target_label(interaction: discord.Interaction, user_id: str, fallback_name: Optional[str] = None) -> str:
    member = None
    if interaction.guild:
        try:
            member = interaction.guild.get_member(int(user_id))
        except (ValueError, TypeError):
            member = None
    if member:
        return member.mention
    if fallback_name:
        return f"{fallback_name} (ID: {user_id})"
    return f"ID: {user_id}"


def _character_autocomplete_choices(interaction: discord.Interaction, current: str):
    term = current.strip()
    matches = database.search_characters_by_name(term, limit=25)
    guild = interaction.guild
    choices: List[app_commands.Choice[str]] = []

    for row in matches:
        label = row["name"]
        member = None
        if guild:
            try:
                member = guild.get_member(int(row["user_id"]))
            except (ValueError, TypeError):
                member = None
        if member:
            label = f"{row['name']} - {member.display_name}"
        else:
            label = f"{row['name']} (ID: {row['user_id']})"
        choices.append(app_commands.Choice(name=label[:100], value=row["user_id"]))

    if not choices and term:
        trimmed = term[:100]
        choices.append(app_commands.Choice(name=f"ID: {trimmed}", value=term))
    return choices


@app_commands.guild_only()
class InventarioGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="inventario", description="Gestiona tu inventario personal")

    @app_commands.command(name="ver", description="Muestra tu inventario actual")
    async def ver(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        items = database.get_inventory(user_id)
        embed = _inventory_embed(f"Inventario de {interaction.user.display_name}", items)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="descartar", description="Quita un item de tu inventario")
    @app_commands.describe(
        item="Nombre del item a descartar",
        cantidad="Cantidad a descartar (minimo 1)"
    )
    async def descartar(
        self,
        interaction: discord.Interaction,
        item: str,
        cantidad: app_commands.Range[int, 1, 999] = 1
    ):
        user_id = str(interaction.user.id)
        try:
            success, remaining = database.remove_item_from_inventory(user_id, item, cantidad)
        except ValueError as exc:
            await interaction.response.send_message(f"Error: {exc}", ephemeral=True)
            return

        if not success:
            await interaction.response.send_message(
                f"No tenes **{item}** en tu inventario.",
                ephemeral=True
            )
            return

        if remaining:
            msg = f"Se descarto {cantidad} de **{item}**. Restan {remaining}."
        else:
            msg = f"Se elimino **{item}** de tu inventario."

        await interaction.response.send_message(msg, ephemeral=True)


@app_commands.guild_only()
class DMInventarioGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="dm_inventario",
            description="Herramientas de inventario para DMs",
            default_permissions=discord.Permissions(administrator=True)
        )

    @app_commands.command(name="dar", description="Agrega un item al inventario de un jugador")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        personaje_id="ID del personaje que recibira el item",
        item="Nombre del item",
        cantidad="Cantidad a entregar (minimo 1)",
        notas="Notas u observaciones"
    )
    async def dar(
        self,
        interaction: discord.Interaction,
        personaje_id: str,
        item: str,
        cantidad: app_commands.Range[int, 1, 999] = 1,
        notas: Optional[str] = None
    ):
        character = database.get_character(personaje_id)
        if not character:
            await interaction.response.send_message(
                "No encontramos un personaje con ese ID.",
                ephemeral=True
            )
            return

        notes_clean = notas.strip() if notas else None
        try:
            database.add_item_to_inventory(personaje_id, item, cantidad, notes_clean)
        except ValueError as exc:
            await interaction.response.send_message(f"Error: {exc}", ephemeral=True)
            return

        target_label = _character_target_label(interaction, personaje_id, character.get("name"))
        message = f"Se agrego **{item}** x{cantidad} al inventario de {target_label}."
        if notes_clean:
            message += f"\nNotas: {notes_clean}"

        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name="quitar", description="Remueve items del inventario de un jugador")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        personaje_id="ID del personaje objetivo",
        item="Nombre del item",
        cantidad="Cantidad a remover (minimo 1)"
    )
    async def quitar(
        self,
        interaction: discord.Interaction,
        personaje_id: str,
        item: str,
        cantidad: app_commands.Range[int, 1, 999] = 1
    ):
        character = database.get_character(personaje_id)
        if not character:
            await interaction.response.send_message(
                "No encontramos un personaje con ese ID.",
                ephemeral=True
            )
            return

        try:
            success, remaining = database.remove_item_from_inventory(personaje_id, item, cantidad)
        except ValueError as exc:
            await interaction.response.send_message(f"Error: {exc}", ephemeral=True)
            return

        if not success:
            await interaction.response.send_message(
                f"Este personaje no tiene **{item}** en su inventario.",
                ephemeral=True
            )
            return

        if remaining:
            msg = f"Se removio {cantidad} de **{item}**. Restan {remaining}."
        else:
            msg = f"Se elimino **{item}** del inventario."

        target_label = _character_target_label(interaction, personaje_id, character.get("name"))
        msg = f"{msg}\nObjetivo: {target_label}"

        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="ver", description="Consulta el inventario de un jugador")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(personaje_id="ID del personaje cuyo inventario queres revisar")
    async def ver(self, interaction: discord.Interaction, personaje_id: str):
        character = database.get_character(personaje_id)
        if not character:
            await interaction.response.send_message(
                "No encontramos un personaje con ese ID.",
                ephemeral=True
            )
            return

        items = database.get_inventory(personaje_id)
        title = f"Inventario de {character['name']}"
        embed = _inventory_embed(title, items)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@DMInventarioGroup.dar.autocomplete("personaje_id")
async def dm_inv_dar_autocomplete(interaction: discord.Interaction, current: str):
    return _character_autocomplete_choices(interaction, current)


@DMInventarioGroup.quitar.autocomplete("personaje_id")
async def dm_inv_quitar_autocomplete(interaction: discord.Interaction, current: str):
    return _character_autocomplete_choices(interaction, current)


@DMInventarioGroup.ver.autocomplete("personaje_id")
async def dm_inv_ver_autocomplete(interaction: discord.Interaction, current: str):
    return _character_autocomplete_choices(interaction, current)


class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.command(name="comprar", description="Compra un item y se agrega a tu inventario")
    @app_commands.describe(
        item="Nombre del item a comprar",
        cantidad="Cantidad a comprar (minimo 1)",
        notas="Notas opcionales (ej. donde lo compraste)",
        oro="Oro total gastado en la transaccion (en PO)"
    )
    async def comprar(
        self,
        interaction: discord.Interaction,
        item: str,
        cantidad: app_commands.Range[int, 1, 999] = 1,
        notas: Optional[str] = None,
        oro: app_commands.Range[int, 0, 100000] = 0
    ):
        user_id = str(interaction.user.id)
        item_name = item.strip()
        if not item_name:
            await interaction.response.send_message("El nombre del item no puede estar vacio.", ephemeral=True)
            return

        notes_clean = notas.strip() if notas else None
        gold_update = None
        if oro > 0:
            try:
                gold_update = database.adjust_gold(user_id, -oro)
            except ValueError as exc:
                await interaction.response.send_message(
                    f"No se pudo registrar la compra: {exc}",
                    ephemeral=True
                )
                return

        try:
            database.add_item_to_inventory(user_id, item_name, cantidad, notes_clean)
        except ValueError as exc:
            if gold_update:
                database.adjust_gold(user_id, oro)
            await interaction.response.send_message(f"Error: {exc}", ephemeral=True)
            return

        embed = discord.Embed(
            title="Compra registrada",
            description=f"Se agrego **{item_name}** x{cantidad} a tu inventario.",
            color=discord.Color.green()
        )
        if notes_clean:
            embed.add_field(name="Notas", value=notes_clean, inline=False)
        if gold_update:
            embed.add_field(name="Oro gastado", value=f"{oro} PO", inline=True)
            embed.add_field(name="Oro restante", value=f"{gold_update[1]} PO", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.guild_only()
    @app_commands.command(name="vender", description="Vende o elimina un item de tu inventario")
    @app_commands.describe(
        item="Item a vender/eliminar",
        cantidad="Cantidad a vender (minimo 1)",
        oro="Oro recibido por la venta (en PO)"
    )
    async def vender(
        self,
        interaction: discord.Interaction,
        item: str,
        cantidad: app_commands.Range[int, 1, 999] = 1,
        oro: app_commands.Range[int, 0, 100000] = 0
    ):
        user_id = str(interaction.user.id)
        item_name = item.strip()
        if not item_name:
            await interaction.response.send_message("El nombre del item no puede estar vacio.", ephemeral=True)
            return

        if oro > 0:
            try:
                database.get_gold(user_id)
            except ValueError as exc:
                await interaction.response.send_message(
                    f"No se pudo registrar la venta: {exc}",
                    ephemeral=True
                )
                return

        try:
            success, remaining = database.remove_item_from_inventory(user_id, item_name, cantidad)
        except ValueError as exc:
            await interaction.response.send_message(f"Error: {exc}", ephemeral=True)
            return

        if not success:
            await interaction.response.send_message(
                f"No tenes **{item_name}** en tu inventario.",
                ephemeral=True
            )
            return

        if remaining:
            desc = f"Vendiste {cantidad} de **{item_name}**. Te quedan {remaining}."
        else:
            desc = f"Vendiste/eliminaste **{item_name}** de tu inventario."

        gold_update = None
        if oro > 0:
            try:
                gold_update = database.adjust_gold(user_id, oro)
            except ValueError as exc:
                await interaction.response.send_message(
                    f"La venta se registro pero no pudimos actualizar tu oro: {exc}",
                    ephemeral=True
                )
                return

        embed = discord.Embed(
            title="Venta registrada",
            description=desc,
            color=discord.Color.gold()
        )
        if gold_update:
            embed.add_field(name="Oro recibido", value=f"{oro} PO", inline=True)
            embed.add_field(name="Oro total", value=f"{gold_update[1]} PO", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))
    bot.tree.add_command(InventarioGroup())
    bot.tree.add_command(DMInventarioGroup())
