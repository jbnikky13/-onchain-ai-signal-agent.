# Onchain AI Signal Agent

Professional crypto/stock market-research dashboard.

Features:
- Binance USDT market discovery
- BUY / SELL / NO SIGNAL model
- Daily Swing and Long-Term modes
- Entry, invalidation/SL model, TP1/TP2/TP3
- Historical-trend projection
- 11-category confluence framework
- New Listings Lab
- Stock/news/NFP adapters
- AI explanation layer
- Signal history
- Responsive dark dashboard
- No order execution

Important: this is a research prototype. Outputs are probabilistic estimates, not financial advice or guarantees. DYOR.

## Run
Python 3.11+
`pip install -r requirements.txt`
`uvicorn backend.main:app --reload`

Open http://127.0.0.1:8000

Copy `.env.example` to `.env`. Never upload API keys.

## Render
Build: `pip install -r requirements.txt`
Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

For production, add PostgreSQL/Redis, scheduled workers, dedicated on-chain providers, derivatives/funding/OI data, news sentiment, and proper walk-forward backtesting.
