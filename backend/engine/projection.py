import numpy as np
from .technical import indicators
def project(df,score,horizon):
    d=indicators(df); x=d.iloc[-1]; p=float(x.close); atr=max(float(x.atr),p*.005); direction=1 if score>=50 else -1; long=horizon=='long_term'
    inv_mult=2.8 if long else 1.25; targets=(2.2,3.8,5.8) if long else (.9,1.6,2.4)
    drift=direction*atr*(4 if long else 1.6)+p*float(np.clip(d.ret_7d.tail(20).median()*2,-.25,.25))*.25
    inv=p-direction*atr*inv_mult; t=[p+direction*atr*m for m in targets]; lo=p+min(drift*.25,drift*.9); hi=p+max(drift*.25,drift*.9)
    return {'price':p,'entry_low':round(p-atr*.25,8),'entry_high':round(p+atr*.25,8),'invalidation':round(inv,8),'tp1':round(t[0],8),'tp2':round(t[1],8),'tp3':round(t[2],8),'projection_low':round(min(lo,hi),8),'projection_high':round(max(lo,hi),8)}
