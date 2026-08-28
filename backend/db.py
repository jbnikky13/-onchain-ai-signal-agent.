import sqlite3, json
from .config import DB_PATH

def connect():
    c=sqlite3.connect(DB_PATH,timeout=10); c.execute("PRAGMA journal_mode=WAL"); return c

def init_db():
    c=connect(); c.execute("CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY,created_at TEXT,symbol TEXT,horizon TEXT,action TEXT,score REAL,payload TEXT)"); c.execute("CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)"); c.commit(); c.close()

def save_signal(signal):
    c=connect(); c.execute("INSERT INTO signals(created_at,symbol,horizon,action,score,payload) VALUES(?,?,?,?,?,?)",(signal["generated_at"],signal["symbol"],signal["horizon"],signal["action"],signal["score"],json.dumps(signal))); c.commit(); c.close()

def recent(limit=100):
    c=connect(); rows=c.execute("SELECT payload FROM signals ORDER BY id DESC LIMIT ?",(limit,)).fetchall(); c.close(); return [json.loads(r[0]) for r in rows]

def stats():
    c=connect(); total,avg=c.execute("SELECT COUNT(*),COALESCE(AVG(score),0) FROM signals").fetchone(); buys=c.execute("SELECT COUNT(*) FROM signals WHERE action='BUY'").fetchone()[0]; sells=c.execute("SELECT COUNT(*) FROM signals WHERE action='SELL'").fetchone()[0]; c.close(); return {"signals":total,"average_score":round(avg,1),"buy_calls":buys,"sell_calls":sells}
