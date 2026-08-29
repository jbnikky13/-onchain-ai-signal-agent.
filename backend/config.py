from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("AWS_LAMBDA_FUNCTION_VERSION"))
DEFAULT_DB = "/tmp/signals.db" if IS_SERVERLESS else str(ROOT / "signals.db")
DB_PATH = os.getenv("DB_PATH") or DEFAULT_DB
if IS_SERVERLESS and not DB_PATH.startswith("/tmp/"):
    DB_PATH = "/tmp/signals.db"

def env_int(name, default):
    value = os.getenv(name)
    if value is None or not str(value).strip():
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def env_str(name, default=""):
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default

OPENAI_API_KEY = env_str("OPENAI_API_KEY")
OPENAI_MODEL = env_str("OPENAI_MODEL", "gpt-5-mini")
ALPHA_VANTAGE_API_KEY = env_str("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = env_str("FINNHUB_API_KEY")
ETHERSCAN_API_KEY = env_str("ETHERSCAN_API_KEY")
DEXSCREENER_BASE_URL = env_str("DEXSCREENER_BASE_URL", "https://api.dexscreener.com")
# Binance public market-data API: no API key is required for these endpoints.
BINANCE_BASE_URL = env_str("BINANCE_BASE_URL", "https://data-api.binance.vision")
BINANCE_FALLBACK_URL = env_str("BINANCE_FALLBACK_URL", "https://api.binance.com")
BINANCE_WS_URL = env_str("BINANCE_WS_URL", "wss://data-stream.binance.vision")
REQUEST_TIMEOUT = max(3, env_int("REQUEST_TIMEOUT", 10))
CACHE_TTL = max(5, env_int("CACHE_TTL", 15))
ONCHAIN_CACHE_TTL = max(0, env_int("ONCHAIN_CACHE_TTL", 20))
EVM_RPCS = {
    "ethereum": env_str("EVM_RPC_ETHEREUM", "https://cloudflare-eth.com"),
    "base": env_str("EVM_RPC_BASE", "https://mainnet.base.org"),
    "arbitrum": env_str("EVM_RPC_ARBITRUM", "https://arb1.arbitrum.io/rpc"),
    "optimism": env_str("EVM_RPC_OPTIMISM", "https://mainnet.optimism.io"),
    "polygon": env_str("EVM_RPC_POLYGON", "https://polygon-rpc.com"),
    "bnb": env_str("EVM_RPC_BNB", "https://bsc-dataseed.binance.org"),
}
