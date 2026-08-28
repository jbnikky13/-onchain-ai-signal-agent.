# Onchain AI — Market Intelligence

Professional research dashboard for crypto, equities and macro context.

## Included
- Live Binance spot market discovery and movers
- Technical scoring: trend, RSI/momentum, MACD, volume and volatility
- Swing and long-term scenario research
- ATR-based projection ranges and invalidation levels
- New Listings Radar
- Optional Alpha Vantage stock adapter
- Optional Finnhub news adapter
- U.S. employment/NFP data through the BLS public API
- Optional OpenAI research narratives
- SQLite research audit trail and performance counters
- Mobile-first responsive terminal UI
- Research-only mode; no order execution

## Render
Use Docker. The included Dockerfile reads Render's `PORT` automatically.

## Environment variables
```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
DB_PATH=signals.db
BINANCE_BASE_URL=https://api.binance.com
REQUEST_TIMEOUT=15
CACHE_TTL=45
```

Keys are optional. Crypto and BLS modules work without the paid-provider keys. Never commit real API keys to GitHub.

## Important
The score is a research model, not a prediction guarantee. Some dimensions such as on-chain, whale, derivatives, sentiment and macro are intentionally neutral until connected to dedicated data providers; the dashboard labels this limitation rather than fabricating measurements.
