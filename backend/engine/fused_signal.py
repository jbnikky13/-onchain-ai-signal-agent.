from .technical import technical_scores


def build_fused_market_signal(df, market_context=None):
    _, scores, raw = technical_scores(df)
    market_context = market_context or {}
    onchain = float(market_context.get("score", 50) or 50)
    onchain = max(0, min(100, onchain))
    weights = {"trend": .25, "momentum": .20, "volume": .15, "volatility": .10, "onchain": .30}
    score = sum(scores[k] * weights[k] for k in scores) + onchain * weights["onchain"]
    score = round(max(0, min(100, score)), 1)
    if score >= 75: bias = "STRONG BULLISH"
    elif score >= 60: bias = "BULLISH"
    elif score <= 25: bias = "STRONG BEARISH"
    elif score <= 40: bias = "BEARISH"
    else: bias = "NEUTRAL"
    confidence = round(min(95, 50 + abs(score - 50) * 0.9), 1)
    return {"score": score, "bias": bias, "confidence": confidence, "components": {**scores, "onchain": round(onchain, 1)}, "raw": raw}
