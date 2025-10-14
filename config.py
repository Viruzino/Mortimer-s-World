# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Otras configuraciones
    PREFIX = "!"
    DATABASE_NAME = "dnd_bot.db"