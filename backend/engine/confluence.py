WEIGHTS={'trend':1.35,'momentum':1.2,'volume':.9,'volatility':.65,'onchain':1.0,'whales':.75,'derivatives':.8,'liquidity':.9,'sentiment':.8,'fundamentals':.8,'macro':.8}
def combine(scores): return round(sum(v*WEIGHTS.get(k,1) for k,v in scores.items())/sum(WEIGHTS.get(k,1) for k in scores),1)
def action(score): return 'BULLISH' if score>=72 else 'BEARISH' if score<=38 else 'NEUTRAL'
def label(score): return 'BUY BIAS' if score>=72 else 'SELL BIAS' if score<=38 else 'NO CLEAR EDGE'
