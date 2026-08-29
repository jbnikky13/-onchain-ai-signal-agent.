from .technical import technical_scores


def build_fused_market_signal(df, market_context=None):
    _, scores, raw = technical_scores(df)
    ctx = market_context or {}
    onchain = max(0.0, min(100.0, float(ctx.get("score", 50) or 50)))
    weights = {"trend": .20, "momentum": .18, "volume": .12, "volatility": .08, "onchain": .25, "liquidity": .10, "safety": .07}
    liquidity = max(0.0, min(100.0, float(ctx.get("liquidity", 50) or 50)))
    safety = max(0.0, min(100.0, float(ctx.get("safety", 50) or 50)))
    score = sum(scores[k] * weights[k] for k in ("trend", "momentum", "volume", "volatility")) + onchain*weights["onchain"] + liquidity*weights["liquidity"] + safety*weights["safety"]
    score = round(max(0, min(100, score)), 1)
    bias = "STRONG BULLISH" if score >= 75 else "BULLISH" if score >= 60 else "STRONG BEARISH" if score <= 25 else "BEARISH" if score <= 40 else "NEUTRAL"
    confidence = round(min(95, 50 + abs(score-50)*0.9), 1)
    return {"score": score, "bias": bias, "confidence": confidence, "components": {**scores, "onchain": round(onchain,1), "liquidity": round(liquidity,1), "safety": round(safety,1)}, "raw": raw}
