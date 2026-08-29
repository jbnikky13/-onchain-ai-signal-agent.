from .intelligence import intelligence


def build_signal_fusion(chain: str, token: str, market_score=None, market_bias=None):
    data = intelligence(chain, token)
    if not data.get("ok"):
        return data

    transfers = data.get("transfers", {})
    rows = transfers.get("transfers", []) if transfers.get("ok") else []
    whales = data.get("whales", {})
    whale_rows = whales.get("whale_transfers", []) if whales.get("ok") else []
    holders = data.get("holders", {})
    top = holders.get("top_holders", []) if holders.get("ok") else []
    liquidity = data.get("liquidity", {})
    risk = data.get("risk", {})

    reasons, risks = [], []

    # The indexed transfer list is a sample, so flow is deliberately capped.
    inbound = sum(float(x.get("amount") or 0) for x in rows if x.get("to"))
    outbound = sum(float(x.get("amount") or 0) for x in rows if x.get("from"))
    flow_ratio = (inbound - outbound) / (inbound + outbound) if inbound + outbound else 0
    flow = max(25, min(75, 50 + flow_ratio * 50))
    if flow_ratio > .12:
        reasons.append("Observed indexed transfers lean toward net inbound flow.")
    elif flow_ratio < -.12:
        risks.append("Observed indexed transfers lean toward net outbound flow.")
    else:
        reasons.append("Observed indexed transfer flow is broadly balanced.")

    whale = 60 if whale_rows else 50
    if whale_rows:
        reasons.append("Large transfers are present in the indexed observation window.")
    else:
        risks.append("No large-transfer activity was available in the indexed window.")

    top5 = sum(float(x.get("share_pct") or 0) for x in top[:5])
    holder = 80 if top5 < 25 else 65 if top5 < 50 else 45 if top5 < 75 else 25
    if top5 >= 75:
        risks.append("Observed top-five holder concentration is high.")
    elif top5 < 50 and top:
        reasons.append("Observed top-five concentration is below 50% of estimated balances.")

    liq_usd = float(liquidity.get("total_liquidity_usd") or 0) if liquidity.get("ok") else 0
    liq = 85 if liq_usd >= 5_000_000 else 70 if liq_usd >= 1_000_000 else 55 if liq_usd >= 100_000 else 35 if liq_usd else 20
    if liq_usd < 100_000:
        risks.append("Available DEX liquidity is low or unavailable.")
    else:
        reasons.append(f"DEX liquidity observed at approximately ${liq_usd:,.0f}.")

    flags = risk.get("flags", []) if risk.get("ok") else ["Risk data unavailable"]
    safety = max(0, 70 - min(40, len(flags) * 12))
    if flags:
        risks.append("Contract heuristics produced review flags; this is not a security audit.")
    else:
        reasons.append("No obvious bytecode risk flags were detected by the heuristic scanner.")

    market = 50
    if market_score is not None:
        try:
            market = max(0, min(100, float(market_score)))
        except (TypeError, ValueError):
            market = 50

    components = {
        "transfer_flow": round(flow, 1),
        "whale_activity": whale,
        "holder_concentration": holder,
        "dex_liquidity": liq,
        "contract_safety": safety,
        "market_context": round(market, 1),
    }
    score = round(
        flow * .22 + whale * .14 + holder * .18 + liq * .20 + safety * .16 + market * .10,
        1,
    )

    if score >= 70:
        label = "BULLISH ON-CHAIN BIAS"
    elif score >= 58:
        label = "POSITIVE / WATCH"
    elif score <= 30:
        label = "BEARISH ON-CHAIN BIAS"
    elif score <= 42:
        label = "NEGATIVE / WATCH"
    else:
        label = "NEUTRAL"

    return {
        "ok": True,
        "chain": chain,
        "token": token,
        "generated_at": data.get("generated_at"),
        "fusion_score": score,
        "label": label,
        "components": components,
        "market_bias": market_bias,
        "reasons": reasons,
        "risks": risks,
        "data_quality": {
            "indexed_transfers": len(rows),
            "observed_wallets": data.get("activity_summary", {}).get("unique_wallets", 0),
            "liquidity_pairs": len(liquidity.get("pairs", [])) if liquidity.get("ok") else 0,
            "holder_warning": holders.get("warning"),
        },
        "disclaimer": "Research signal only. Data can be incomplete and the score is heuristic; it is not financial advice or a security audit.",
    }
