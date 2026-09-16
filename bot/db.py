import sqlite3, secrets, time
from pathlib import Path

class Database:
    def __init__(self, path):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        return c

    def init(self):
        with self.connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS seasons(
              id INTEGER PRIMARY KEY AUTOINCREMENT, number INTEGER NOT NULL,
              started_at INTEGER NOT NULL, ended_at INTEGER, status TEXT NOT NULL DEFAULT 'active'
            );
            CREATE TABLE IF NOT EXISTS scores(
              id INTEGER PRIMARY KEY AUTOINCREMENT, season_id INTEGER NOT NULL, game TEXT NOT NULL,
              user_id INTEGER NOT NULL, username TEXT, display_name TEXT, score INTEGER NOT NULL,
              created_at INTEGER NOT NULL, FOREIGN KEY(season_id) REFERENCES seasons(id)
            );
            CREATE INDEX IF NOT EXISTS idx_scores ON scores(season_id, game, score DESC);
            CREATE TABLE IF NOT EXISTS launch_tokens(
              token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, username TEXT, display_name TEXT,
              game TEXT NOT NULL, chat_id INTEGER, created_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL, used INTEGER NOT NULL DEFAULT 0
            );
            """)
            if not c.execute("SELECT 1 FROM seasons WHERE status='active'").fetchone():
                c.execute("INSERT INTO seasons(number,started_at) VALUES(1,?)",(int(time.time()),))

    def season(self):
        with self.connect() as c:
            return c.execute("SELECT * FROM seasons WHERE status='active' ORDER BY id DESC LIMIT 1").fetchone()

    def new_season(self):
        now=int(time.time())
        with self.connect() as c:
            old=c.execute("SELECT * FROM seasons WHERE status='active' ORDER BY id DESC LIMIT 1").fetchone()
            n=(old["number"]+1) if old else 1
            if old:
                c.execute("UPDATE seasons SET status='closed',ended_at=? WHERE id=?",(now,old["id"]))
            c.execute("INSERT INTO seasons(number,started_at) VALUES(?,?)",(n,now))
            return n

    def token(self,user_id,username,name,game,chat_id):
        t=secrets.token_urlsafe(32); now=int(time.time())
        with self.connect() as c:
            c.execute("""INSERT INTO launch_tokens
              (token,user_id,username,display_name,game,chat_id,created_at,expires_at)
              VALUES(?,?,?,?,?,?,?,?)""",
              (t,user_id,username,name,game,chat_id,now,now+900))
        return t

    def consume(self,t,game):
        now=int(time.time())
        with self.connect() as c:
            r=c.execute("""SELECT * FROM launch_tokens
              WHERE token=? AND game=? AND used=0 AND expires_at>=?""",(t,game,now)).fetchone()
            if not r: return None
            c.execute("UPDATE launch_tokens SET used=1 WHERE token=?",(t,))
            return r

    def save_score(self,game,user_id,username,name,score):
        s=self.season()
        with self.connect() as c:
            personal=c.execute("""SELECT MAX(score) best FROM scores
              WHERE season_id=? AND game=? AND user_id=?""",(s["id"],game,user_id)).fetchone()["best"]
            record=c.execute("""SELECT MAX(score) best FROM scores
              WHERE season_id=? AND game=?""",(s["id"],game)).fetchone()["best"]
            c.execute("""INSERT INTO scores
              (season_id,game,user_id,username,display_name,score,created_at)
              VALUES(?,?,?,?,?,?,?)""",(s["id"],game,user_id,username,name,score,int(time.time())))
            return (personal is None or score>personal), (record is None or score>record), s["number"]

    def top(self,game=None,limit=10):
        s=self.season()
        with self.connect() as c:
            if game:
                return c.execute("""SELECT user_id,username,display_name,MAX(score) score
                  FROM scores WHERE season_id=? AND game=? GROUP BY user_id
                  ORDER BY score DESC LIMIT ?""",(s["id"],game,limit)).fetchall()
            return c.execute("""SELECT user_id,username,display_name,SUM(best) total FROM
              (SELECT user_id,username,display_name,game,MAX(score) best FROM scores
               WHERE season_id=? GROUP BY user_id,game)
              GROUP BY user_id ORDER BY total DESC LIMIT ?""",(s["id"],limit)).fetchall()
