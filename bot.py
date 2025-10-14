import discord
from discord.ext import commands
import os

class DnDBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        print("🔄 Cargando extensiones...")
        
        # Cargar todos los cogs
        cogs = [
            'cogs.user_commands',
            'cogs.character_commands', 
            'cogs.dm_commands',
            'cogs.shop_commands',
            'cogs.help_commands',
            'cogs.slash_commands'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ {cog} cargado")
            except Exception as e:
                print(f"❌ Error cargando {cog}: {e}")

        # Sincronizar comandos de barra
        print("🔄 Sincronizando comandos...")
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} comandos de barra sincronizados")
        except Exception as e:
            print(f"❌ Error sincronizando comandos: {e}")

    async def on_ready(self):
        print(f'✅ {self.user} ha conectado a Discord!')
        print(f'📊 Conectado a {len(self.guilds)} servidores')
        
        if self.guilds:
            print("\n🏠 Servidores conectados:")
            for guild in self.guilds:
                print(f'   • {guild.name} (ID: {guild.id})')
        else:
            print("\n❌ El bot no está en ningún servidor")
            print("💡 Usa el link de invitación para agregarlo a un servidor")
        
        await self.change_presence(activity=discord.Game(name="D&D | /ayuda"))