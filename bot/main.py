import asyncio, html
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, InlineQueryResultPhoto, InlineKeyboardMarkup, InlineKeyboardButton
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
    # El token se genera DURANTE la consulta inline, cuando ya conocemos al usuario.
    # Así el botón URL de la tarjeta queda vinculado al jugador que eligió el resultado.
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
        await m.answer(f"🏆 <b>{title}</b> — Temporada {n}\nSin puntuaciones todavía."); return
    lines=[f"🏆 <b>{title}</b> — Temporada {n}",""]
    for i,r in enumerate(rows,1):
        name=html.escape(r["display_name"] or r["username"] or str(r["user_id"]))
        value=r["score"] if game else r["total"]
        lines.append(f"{i}. {name} — <b>{value:,}</b>")
    await m.answer("\n".join(lines))

@dp.message(Command("start"))
async def start(m): await m.answer("🎮 <b>Q-ArcadeBot</b>\nEn el grupo escribe <code>@QArcadeBot</code> para abrir el catálogo.")

@dp.message(Command("help"))
async def help_(m): await m.answer("Inline: @QArcadeBot\nRankings: /top, /toppacman, /topmario, /topdoom, /topnaves, /topsunset, /topcarros, /topcircus\nAdmin: /resetscores, /nuevaedicion")

@dp.message(Command("top"))
async def top(m): await show_top(m)

for cmd,slug in [
    ("toppacman","pacman"),("topmario","mario"),("topdoom","doom"),
    ("topnaves","naves"),("topsunset","sunset"),("topcarros","carros"),("topcircus","circus")
]:
    async def handler(m,slug=slug,cmd=cmd):
        await show_top(m,slug,"TOP "+GAMES[slug][0].upper())
    dp.message.register(handler,Command(cmd))

def admin(m):
    return m.from_user and m.from_user.id in settings.admin_ids

@dp.message(Command("resetscores"))
async def reset(m):
    if not admin(m): await m.answer("⛔ Solo administradores."); return
    old=db.season()["number"]; new=db.new_season()
    await m.answer(f"🔄 Temporada {old} cerrada. Nueva temporada: {new}.")

@dp.message(Command("nuevaedicion"))
async def edition(m):
    if not admin(m): await m.answer("⛔ Solo administradores."); return
    old=db.season()["number"]; new=db.new_season()
    await m.answer(f"🎮 Nueva edición iniciada. Temporada {old} cerrada; temporada {new} activa.")

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
