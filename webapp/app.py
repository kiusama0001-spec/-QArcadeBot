from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from aiogram import Bot
from bot.config import load_settings
from bot.db import Database
from bot.games import GAMES

settings = load_settings()
db = Database(settings.database_path)
telegram_bot = Bot(settings.bot_token)
app = FastAPI(title="Q-ArcadeBot web App")
BASE = Path(__file__).parent


class Score(BaseModel):
  token: str = Field(min_length=20, max_length=200)
  game: str
  score: int = Field(ge=0, le=10_000_000)


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
def home():
  return (BASE / "index.html").read_text(encoding="utf-8")


@app.get("/game/{game}", response_class=HTMLResponse)
def game_page(game):
  if game not in GAMES:
    raise HTTPException(404, "Juego inexistente")
  return (BASE / "index.html").read_text(encoding="utf-8")


@app.post("/api/score")
async def submit(p: Score):
  if p.game not in GAMES:
    raise HTTPException(400, "Juego inválido")

  user = db.consume(p.token, p.game)
  if not user:
    raise HTTPException(401, "Token inválido, usado o caducado")

  personal, record, season = db.save_score(
      p.game,
      user["user_id"],
      user["username"],
      user["display_name"],
      p.score,
  )

  if record and settings.group_chat_id:
    name = user["display_name"] or user["username"] or str(user["user_id"])
    title = GAMES[p.game][0]
    try:
      await telegram_bot.send_message(
          settings.group_chat_id,
          f"🏆 <b>¡NUEVO RÉCORD!</b>\n\n"
          f"🎮 {title}\n"
          f"👤 {name}\n"
          f"⭐ Puntuación: <b>{p.score:,}</b>\n"
          f"📅 Temporada: <b>{season}</b>",
      )
    except Exception as e:
      print("Error anunciando récord:", e)

  return {
      "ok": True,
      "personal_best": personal,
      "new_record": record,
      "season"
      : season,
  }
