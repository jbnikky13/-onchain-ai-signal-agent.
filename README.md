# Onchain AI — Market Intelligence

A Vercel-ready, research-only market intelligence terminal for crypto, equities and macro context.

## Production architecture

- Vercel hosts the static dashboard and Python/FastAPI serverless API.
- Binance public endpoints provide crypto spot market data.
- BLS provides U.S. employment/NFP series without an API key.
- Alpha Vantage is optional for equities.
- Finnhub is optional for company news.
- OpenAI is optional for concise research narratives.
- SQLite is used as a lightweight audit trail. On Vercel, the default database is `/tmp/signals.db`, so it is ephemeral; use a hosted database for durable production history.

## Modules

- Market Overview
- Daily Signals
- Swing Research
- Long-Term Research
- New Listings Radar
- Equity Intelligence
- NFP & Macro
- Performance & Audit

## Vercel deployment

1. Import this GitHub repository into Vercel.
2. Keep the repository root as the project root.
3. Vercel should detect `api/index.py` as the Python function and use `vercel.json` for routing.
4. Deploy.
5. Add environment variables in **Project → Settings → Environment Variables**.

Recommended variables:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
BINANCE_BASE_URL=https://api.binance.com
REQUEST_TIMEOUT=15
CACHE_TTL=45
```

No API key is required for the core crypto market feed or BLS employment feed.

## Local run

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open `http://localhost:8000`.

## Research disclaimer

This application is research software. It does not execute orders and its scores, scenarios and AI narratives are probabilistic outputs, not guarantees or financial advice. Always independently verify important market information.

Do not commit real API keys to GitHub.
