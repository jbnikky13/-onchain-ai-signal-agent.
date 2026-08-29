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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-5-mini"
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
DEXSCREENER_BASE_URL = os.getenv("DEXSCREENER_BASE_URL") or "https://api.dexscreener.com"
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL") or "https://api.binance.com"
REQUEST_TIMEOUT = max(3, env_int("REQUEST_TIMEOUT", 10))
CACHE_TTL = max(0, env_int("CACHE_TTL", 45))
ONCHAIN_CACHE_TTL = max(0, env_int("ONCHAIN_CACHE_TTL", 20))
EVM_RPCS = {
    "ethereum": os.getenv("EVM_RPC_ETHEREUM") or "https://cloudflare-eth.com",
    "base": os.getenv("EVM_RPC_BASE") or "https://mainnet.base.org",
    "arbitrum": os.getenv("EVM_RPC_ARBITRUM") or "https://arb1.arbitrum.io/rpc",
    "optimism": os.getenv("EVM_RPC_OPTIMISM") or "https://mainnet.optimism.io",
    "polygon": os.getenv("EVM_RPC_POLYGON") or "https://polygon-rpc.com",
    "bnb": os.getenv("EVM_RPC_BNB") or "https://bsc-dataseed.binance.org",
}
