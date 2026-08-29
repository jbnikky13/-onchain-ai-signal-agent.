# Onchain AI — Market Intelligence

A Vercel-ready, research-only market intelligence terminal for crypto, equities, macro context and live EVM on-chain inspection.

## Working modules

- Market Overview — live Binance USDT spot market data
- Daily / Swing / Long-Term Research — technical scoring and scenario ranges
- On-Chain Explorer — live read-only EVM address, contract and transaction analysis
- New Listings Radar — recent Binance USDT listings
- Equity Intelligence — optional Alpha Vantage adapter
- NFP & Macro — BLS employment adapter
- Performance & Audit — research history
- Optional AI research narratives

## On-chain data

The explorer now uses live JSON-RPC calls rather than hardcoded blockchain results. Default public RPC endpoints are supplied for Ethereum, Base, Arbitrum, Optimism, Polygon and BNB Chain, and each provider can be replaced through environment variables.

Supported environment variables:

```text
EVM_RPC_ETHEREUM=
EVM_RPC_BASE=
EVM_RPC_ARBITRUM=
EVM_RPC_OPTIMISM=
EVM_RPC_POLYGON=
EVM_RPC_BNB=
```

Leave these blank to use the public defaults. For production, a dedicated RPC provider is recommended for better rate limits and reliability.

## Vercel deployment

Import the repository into Vercel with the repository root as the project root. Vercel uses `api/index.py` and `vercel.json` for the FastAPI serverless API and static dashboard.

Optional variables:

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
ALPHA_VANTAGE_API_KEY=
FINNHUB_API_KEY=
BINANCE_BASE_URL=https://api.binance.com
REQUEST_TIMEOUT=15
CACHE_TTL=45
EVM_RPC_ETHEREUM=
EVM_RPC_BASE=
EVM_RPC_ARBITRUM=
EVM_RPC_OPTIMISM=
EVM_RPC_POLYGON=
EVM_RPC_BNB=
```

No private API key is required for the default Binance, BLS or public EVM feeds.

## Local run

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open `http://localhost:8000`. API documentation is available at `/api/docs`.

## Research disclaimer

This application is research software. It does not execute orders or sign transactions. Blockchain data is descriptive and market scores/scenarios are probabilistic research outputs, not guarantees or financial advice. Always independently verify important information.

Do not commit real API keys or private RPC credentials to GitHub.
