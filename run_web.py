import os
import subprocess
import uvicorn
from webapp.app import app

if __name__ == "__main__":
    # 1. Arrancamos el bot de Telegram como un proceso independiente del sistema
    print("Iniciando el bot de Telegram...")
    bot_process = subprocess.Popen(["python", "run_bot.py"])

    try:
        # 2. Obtenemos el puerto dinámico de Render
        port = int(os.environ.get("PORT", 10000))
        
        # 3. Arrancamos el servidor web para mantener activo a Render
        uvicorn.run(app, host="0.0.0.0", port=port)
    finally:
        # Si el servidor se apaga, cerramos también el bot limpiamente
        bot_process.terminate()
