from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = "/tmp/signals.db" if os.getenv("VERCEL") else str(ROOT / "signals.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "45"))

# Public RPC defaults; each can be overridden in Vercel/Render environment variables.
EVM_RPCS = {
    "ethereum": os.getenv("EVM_RPC_ETHEREUM", "https://cloudflare-eth.com"),
    "base": os.getenv("EVM_RPC_BASE", "https://mainnet.base.org"),
    "arbitrum": os.getenv("EVM_RPC_ARBITRUM", "https://arb1.arbitrum.io/rpc"),
    "optimism": os.getenv("EVM_RPC_OPTIMISM", "https://mainnet.optimism.io"),
    "polygon": os.getenv("EVM_RPC_POLYGON", "https://polygon-rpc.com"),
    "bnb": os.getenv("EVM_RPC_BNB", "https://bsc-dataseed.binance.org"),
}
