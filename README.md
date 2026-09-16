# Q-ArcadeBot

Bot de Telegram en Python + aiogram 3, con modo Inline, rankings por juego, SQLite, temporadas y Web App HTML5 táctil.

## Restricción importante de Telegram

Telegram no permite `InlineKeyboardButton.web_app` en mensajes enviados a grupos: la Bot API limita ese botón Web App a chats privados entre el usuario y el bot. Por eso el starter usa un botón HTTPS `Abrir juego` en la tarjeta Inline. La página es móvil/táctil y el backend usa tokens de lanzamiento para asociar la partida al usuario.

Fuentes oficiales:
- https://core.telegram.org/bots/inline
- https://core.telegram.org/bots/api#inlinequeryresultphoto
- https://core.telegram.org/bots/webapps

## Instalación

1. En @BotFather crea el bot y ejecuta `/setinline`.
2. Copia `.env.example` como `.env`.
3. Instala Python 3.11+ y ejecuta:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

4. Sirve la API/Web App por HTTPS. La Web App debe tener una URL pública HTTPS.
5. Arranca la API con `python run_web.py`.
6. Arranca el bot con `python run_bot.py`.

## Variables

```env
BOT_TOKEN=TOKEN_DE_BOTFATHER
WEBAPP_BASE_URL=https://tu-dominio.example
DATABASE_PATH=./data/arcade.sqlite3
ADMIN_IDS=123456789,987654321
GROUP_CHAT_ID=-1001234567890
```

## Comandos

`/top`, `/toppacman`, `/topmario`, `/topdoom`, `/topnaves`, `/topsunset`, `/topcarros`, `/topcircus`

Admin: `/resetscores`, `/nuevaedicion`.

## Temporadas

Cada nueva edición cierra la temporada activa y crea otra. El historial queda en SQLite.

## Puntuaciones

El backend no acepta directamente un user_id desde JavaScript. Usa tokens de partida almacenados en SQLite y caducables. Para competición seria, añade anti-cheat específico por juego.

## Assets y copyright

El paquete no contiene ROMs, sprites, música ni código propietario de los juegos mencionados. Los gráficos incluidos son genéricos/originales. Sustituye los assets solo por material que tengas derecho a usar.


## Flujo real de token

El token de partida se crea dentro del `InlineQuery`, porque Telegram ya entrega al bot el usuario que está consultando `@QArcadeBot`. El token queda embebido en la URL de la tarjeta seleccionable y está asociado a ese usuario, juego y temporada.

Al enviarse la tarjeta al grupo no hace falta que el bot modifique el mensaje posteriormente.

## Anuncios

Para que los récords se anuncien en un grupo concreto, define `GROUP_CHAT_ID`. El bot debe estar dentro de ese grupo y tener permiso para enviar mensajes.

## Limitación del starter

La puntuación se valida mediante token, rango y uso único, pero el juego es un prototipo HTML5 genérico. Para una competición real conviene implementar un motor separado para cada uno de los siete juegos y validación anti-cheat específica. 
