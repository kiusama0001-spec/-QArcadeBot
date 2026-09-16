import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str
    webapp_base_url: str
    database_path: str
    admin_ids: set[int]
    group_chat_id: int | None

def load_settings():
    token = os.getenv("BOT_TOKEN", "").strip()
    base = os.getenv("WEBAPP_BASE_URL", "").strip().rstrip("/")
    if not token:
        raise RuntimeError("Falta BOT_TOKEN en .env")
    if not base.startswith("https://"):
        raise RuntimeError("WEBAPP_BASE_URL debe usar HTTPS")
    admins = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
    raw = os.getenv("GROUP_CHAT_ID", "").strip()
    return Settings(token, base, os.getenv("DATABASE_PATH", "./data/arcade.sqlite3"),
                   admins, int(raw) if raw else None)
