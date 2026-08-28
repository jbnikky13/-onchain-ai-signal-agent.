from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
# Vercel's writable filesystem is /tmp and is ephemeral between instances.
# For Render/local development we keep the SQLite file beside the project.
DEFAULT_DB = "/tmp/signals.db" if os.getenv("VERCEL") else str(ROOT / "signals.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "45"))
