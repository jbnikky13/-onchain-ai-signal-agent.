import numpy as np
from .technical import indicators
def project(df,score,horizon):
    d=indicators(df); x=d.iloc[-1]; p=float(x.close); atr=float(x.atr); direction=1 if score>=50 else -1
    invalid=2.8 if horizon=="long_term" else 1.25; tps=(2.2,3.8,5.8) if horizon=="long_term" else (.9,1.6,2.4)
    drift=direction*atr*(4 if horizon=="long_term" else 1.6)+p*float(np.clip(d.ret_7d.tail(20).median()*2,-.25,.25))*.25
    if direction>0: inv=p-atr*invalid; targets=[p+atr*m for m in tps]
    else: inv=p+atr*invalid; targets=[p-atr*m for m in tps]
    return {"price":p,"entry_low":round(p-atr*.25,8),"entry_high":round(p+atr*.25,8),"invalidation":round(inv,8),
            "tp1":round(targets[0],8),"tp2":round(targets[1],8),"tp3":round(targets[2],8),
            "projection_low":round(min(p+drift*.25,p+drift*.9),8),"projection_high":round(max(p+drift*.25,p+drift*.9),8)}

