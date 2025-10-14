import os
import discord
from dotenv import load_dotenv
from bot import DnDBot

# Cargar variables de entorno
load_dotenv()

def main():
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ ERROR: No se encontró DISCORD_TOKEN en el archivo .env")
        print("💡 Crea un archivo .env con: DISCORD_TOKEN=tu_token_aqui")
        return
    
    print("🚀 Iniciando bot de D&D...")
    
    try:
        bot = DnDBot()
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Token inválido. Verifica tu token en el archivo .env")
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()