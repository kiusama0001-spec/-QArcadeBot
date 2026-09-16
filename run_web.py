import os
import threading
import uvicorn
from webapp.app import app
import asyncio
from bot.main import main as run_telegram_bot

def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_telegram_bot())
    except Exception as e:
        print(f"Error en el bot: {e}")

if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    print("Bot de Telegram iniciado en segundo plano...")

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
