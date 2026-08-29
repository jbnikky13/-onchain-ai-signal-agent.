# Onchain AI — Market Intelligence

A Vercel-ready, research-only market intelligence terminal for crypto, equities, macro context and live EVM on-chain inspection.

## Working modules

- **Market Overview** — live Binance USDT spot universe, volume leaders and movers.
- **Daily / Swing / Long-Term Research** — technical indicators, confluence scoring and scenario ranges.
- **On-Chain Explorer** — read-only EVM analysis for Ethereum, Base, Arbitrum, Optimism, Polygon and BNB Chain.
  - Address classification: EOA vs contract
  - Native balance
  - Transaction count / nonce
  - Latest block and gas price
  - Contract bytecode size
  - ERC-20 metadata when exposed by the contract
  - Basic proxy-bytecode hint
  - Transaction lookup with receipt status, sender, recipient, value, block and gas used
- **New Listings Radar** — recently onboarded Binance USDT pairs.
- **Equity Intelligence** — optional Alpha Vantage adapter.
- **NFP & Macro** — BLS employment adapter without an API key.
- **Performance & Audit** — local/ephemeral research history.
- **AI narrative** — optional OpenAI explanation layer.

## Production architecture

- Vercel hosts the static dashboard and Python/FastAPI serverless API.
- Binance public endpoints provide crypto spot market data.
- Public EVM RPC endpoints provide read-only blockchain state; no wallet connection or transaction signing is used.
- BLS provides U.S. employment/NFP series without an API key.
- Alpha Vantage and Finnhub are optional adapters.
- SQLite is used as a lightweight audit trail. On Vercel, `/tmp/signals.db` is ephemeral; use a hosted database if durable history is required.

## Vercel deployment

1. Import this GitHub repository into Vercel.
2. Keep the repository root as the project root.
3. Vercel should detect `api/index.py` as the Python function and use `vercel.json` for routing.
4. Deploy.
5. Add optional environment variables in **Project → Settings → Environment Variables**.

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
BINANCE_BASE_URL=https://api.binance.com
REQUEST_TIMEOUT=15
CACHE_TTL=45
```

The core crypto feed, BLS feed and EVM read-only explorer do not require private API keys.

## Local run

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open `http://localhost:8000`.

API documentation is available at `/api/docs`.

## Research disclaimer

This application is research software. It does not execute orders. Market scores, scenarios, blockchain classifications and AI narratives are probabilistic or descriptive outputs, not guarantees or financial advice. Always independently verify important information.

Do not commit real API keys to GitHub.
