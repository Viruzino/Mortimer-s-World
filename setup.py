# setup.py
import os

def crear_archivos_faltantes():
    # Crear .env.example
    with open('.env.example', 'w') as f:
        f.write('DISCORD_TOKEN=tu_token_de_discord_aqui\n')
    
    # Crear __init__.py en carpetas
    carpetas = ['cogs', 'utils', 'data', 'models']
    for carpeta in carpetas:
        init_path = os.path.join(carpeta, '__init__.py')
        if not os.path.exists(init_path):
            with open(init_path, 'w') as f:
                f.write('')
            print(f"✅ {init_path} creado")
    
    print("✅ Archivos de configuración creados")
    print("💡 Ahora crea un archivo .env con tu token real")

if __name__ == "__main__":
    crear_archivos_faltantes()