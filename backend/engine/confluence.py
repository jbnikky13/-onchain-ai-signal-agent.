def combine(s):
    w={"trend":1.3,"momentum":1.1,"volume":1,"volatility":.8,"onchain":1,"whales":.8,"derivatives":.8,"liquidity":.8,"sentiment":.7,"fundamentals":1,"macro":.7}
    return round(sum(v*w.get(k,1) for k,v in s.items())/sum(w.get(k,1) for k in s),1)
def action(x):
    return "BUY" if x>=72 else "SELL" if x<=38 else "NO SIGNAL"

