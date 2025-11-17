import discord
from discord.ext import commands
import os

class DnDBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        print("�Y"" Cargando extensiones...")
        
        # Cargar todos los cogs
        cogs = [
            'cogs.user_commands',
            'cogs.character_commands', 
            'cogs.dm_commands',
            'cogs.shop_commands',
            'cogs.inventory_commands',
            'cogs.help_commands',
            'cogs.slash_commands'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"�o. {cog} cargado")
            except Exception as e:
                print(f"�?O Error cargando {cog}: {e}")

        # Sincronizar comandos de barra sin duplicados
        print("�Y"" Sincronizando comandos...")
        try:
            guild_id = os.getenv("DISCORD_GUILD_ID")
            if guild_id:
                try:
                    guild_obj = discord.Object(id=int(guild_id))
                    guild_synced = await self.tree.sync(guild=guild_obj)
                    print(f"�o. {len(guild_synced)} comandos sincronizados para el servidor {guild_id}")
                except ValueError:
                    print("�?O DISCORD_GUILD_ID no es un entero vǭlido. Omitiendo sync espec��fico.")
            else:
                synced = await self.tree.sync()
                print(f"�o. {len(synced)} comandos de barra sincronizados (globales)")
        except Exception as e:
            print(f"�?O Error sincronizando comandos: {e}")

    async def on_ready(self):
        print(f'�o. {self.user} ha conectado a Discord!')
        print(f'�Y"S Conectado a {len(self.guilds)} servidores')
        
        if self.guilds:
            print("\n�Y?� Servidores conectados:")
            for guild in self.guilds:
                print(f'   �?� {guild.name} (ID: {guild.id})')
        else:
            print("\n�?O El bot no estǭ en ningǧn servidor")
            print("�Y'� Usa el link de invitaci��n para agregarlo a un servidor")
        
        await self.change_presence(activity=discord.Game(name="D&D | /ayuda"))
