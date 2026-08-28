from fastapi import FastAPI, HTTPException, Query
from .services.binance import (
    get_symbols,
    get_klines,
    get_ticker_24h,
    market_snapshot,
    get_new_listings,
)
from .services.stocks import get_stock
from .services.news import get_company_news
from .services.macro import get_employment_snapshot
from .engine.signal import analyze_crypto
from .engine.ai import explain
from .db import init_db, save_signal, recent, stats

app = FastAPI(
    title="Onchain AI Market Intelligence API",
    version="2.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


@app.on_event("startup")
def startup():
    # Safe on Vercel: config.py points SQLite at /tmp there.
    init_db()


@app.get("/api")
def api_root():
    return {
        "ok": True,
        "service": "onchain-ai",
        "version": "2.1.0",
        "mode": "research-only",
    }


@app.get("/api/health")
def health():
    return {"ok": True, "service": "onchain-ai", "version": "2.1.0"}


@app.get("/api/overview")
def overview():
    return market_snapshot()


@app.get("/api/crypto/symbols")
def symbols():
    s = get_symbols()
    return {"count": len(s), "symbols": s}


@app.get("/api/crypto/ticker")
def ticker():
    rows = [x for x in get_ticker_24h() if x.get("symbol", "").endswith("USDT")]
    rows.sort(key=lambda x: float(x.get("quoteVolume", 0) or 0), reverse=True)
    return rows[:100]


@app.get("/api/crypto/{symbol}")
def crypto(
    symbol: str,
    horizon: str = Query("swing", pattern="^(swing|long_term)$"),
):
    try:
        symbol = symbol.upper()
        df = get_klines(symbol, "1d", 180)
        if len(df) < 60:
            raise HTTPException(400, "Not enough market history for this asset.")
        signal = analyze_crypto(symbol, df, horizon)
        signal["ai"] = explain(signal)
        save_signal(signal)
        return signal
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(502, "Market data unavailable for this symbol.")


@app.get("/api/new-listings")
def new_listings(days: int = 30):
    return get_new_listings(min(max(days, 1), 90))


@app.get("/api/stock/{symbol}")
def stock(symbol: str):
    return get_stock(symbol)


@app.get("/api/news/{symbol}")
def news(symbol: str):
    return get_company_news(symbol)


@app.get("/api/macro/nfp")
def nfp():
    return get_employment_snapshot()


@app.get("/api/history")
def history(limit: int = 100):
    return recent(min(max(limit, 1), 500))


@app.get("/api/performance")
def performance():
    return stats()
