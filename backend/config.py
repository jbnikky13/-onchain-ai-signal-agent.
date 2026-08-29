from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV") or os.getenv("AWS_LAMBDA_FUNCTION_VERSION"))
DEFAULT_DB = "/tmp/signals.db" if IS_SERVERLESS else str(ROOT / "signals.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB)
if IS_SERVERLESS and not DB_PATH.startswith("/tmp/"):
    DB_PATH = "/tmp/signals.db"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
DEXSCREENER_BASE_URL = os.getenv("DEXSCREENER_BASE_URL", "https://api.dexscreener.com")
BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "45"))
ONCHAIN_CACHE_TTL = int(os.getenv("ONCHAIN_CACHE_TTL", "20"))
EVM_RPCS = {
    "ethereum": os.getenv("EVM_RPC_ETHEREUM", "https://cloudflare-eth.com"),
    "base": os.getenv("EVM_RPC_BASE", "https://mainnet.base.org"),
    "arbitrum": os.getenv("EVM_RPC_ARBITRUM", "https://arb1.arbitrum.io/rpc"),
    "optimism": os.getenv("EVM_RPC_OPTIMISM", "https://mainnet.optimism.io"),
    "polygon": os.getenv("EVM_RPC_POLYGON", "https://polygon-rpc.com"),
    "bnb": os.getenv("EVM_RPC_BNB", "https://bsc-dataseed.binance.org"),
}
