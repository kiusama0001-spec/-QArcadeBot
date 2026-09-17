import asyncio, html
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from .config import load_settings
from .games import GAMES, IMAGE
from .db import Database

settings=load_settings()
db=Database(settings.database_path)
bot=Bot(settings.bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher()

@dp.inline_query()
async def inline(query: InlineQuery):
    q=query.query.lower().strip()
    items=[(slug,*data) for slug,data in GAMES.items()]
    if q:
        items=[x for x in items if q in x[0] or q in x[1].lower()]

    results=[]
    for slug,title,desc in items:
        token=db.token(
            query.from_user.id,
            query.from_user.username,
            query.from_user.full_name,
            slug,
            settings.group_chat_id
        )
        url=f"{settings.webapp_base_url}/game/{slug}?token={token}"
        results.append(InlineQueryResultPhoto(
            id=f"game:{slug}:{token[:12]}",
            photo_url=IMAGE(slug),
            thumbnail_url=IMAGE(slug),
            photo_width=800,
            photo_height=450,
            title=title,
            description=desc,
            caption=f"<b>{html.escape(title)}</b>\n{html.escape(desc)}\n\nPulsa <b>🎮 Abrir juego</b> para jugar.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🎮 Abrir juego",url=url)
            ]])
        ))
    await query.answer(results,cache_time=0,is_personal=True)

async def announce_record(game, user, score, season):
    if not settings.group_chat_id:
        return
    title=html.escape(GAMES[game][0])
    name=html.escape(user["display_name"] or user["username"] or str(user["user_id"]))
    try:
        await bot.send_message(
            settings.group_chat_id,
            f"🏆 <b>¡NUEVO RÉCORD!</b>\n\n"
            f"🎮 {title}\n"
            f"👤 {name}\n"
            f"⭐ Puntuación: <b>{score:,}</b>\n"
            f"📅 Temporada: <b>{season}</b>"
        )
    except Exception as e:
        print("No se pudo anunciar el récord:", e)

async def show_top(m,game=None,title="TOP"):
    rows=db.top(game); n=db.season()["number"]
    if not rows:
        await m.answer(f"🏆 <b>{title}</b> — Temporada {n}\nSin puntu¡Perfecto! Ya revisé la estructura de tu proyecto. Veo que estás construyendo una plataforma muy completa con un bot de Telegram y una WebApp integrada.

Aquí tienes un resumen rápido de lo que comprendo sobre tu código:

*   **Arquitectura dual:** El proyecto se divide claramente en la ejecución del bot mediante `run_bot.py`[span_0](start_span)[span_0](end_span) y el servidor web para los juegos usando Uvicorn en `run_web.py`[span_1](start_span)[span_1](end_span).
*   **Catálogo arcade:** Tienes configurados 7 minijuegos clásicos (como Pac-Man, Mario, DOOM, etc.) gestionados desde `games.py`[span_2](start_span)[span_2](end_span).
*   **Lógica interactiva (`main.py`):**
    *   Aprovecha el modo *inline* de Telegram (`@QArcadeBot`) para buscar juegos y generar un botón con una URL única de la WebApp, validada mediante tokens[span_3](start_span)[span_3](end_span).
    *   Cuenta con un sistema de anuncios automáticos para los nuevos récords en el grupo principal[span_4](start_span)[span_4](end_span).
    *   Maneja diferentes tablas de clasificación (`/top`, `/toppacman`, etc.)[span_5](start_span)[span_5](end_span).
    *   Los comandos de administrador, especialmente `/nuevaedicion`[span_6](start_span)[span_6](end_span), están listos para cerrar la temporada actual y preparar la próxima edición, lo cual queda perfecto para cuando llegue el momento de hacer el corte, repartir las felicitaciones y que los jugadores puedan recolectar sus *pipesos* según su posición en el ranking.

¿Qué te gustaría hacer con estos archivos? ¿Necesitas que te ayude a encontrar algún error, agregar un juego nuevo a la lista, o ajustar la lógica de la base de datos?
