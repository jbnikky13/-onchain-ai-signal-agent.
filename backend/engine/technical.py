import numpy as np

def indicators(d):
    d=d.copy(); c=d.close; v=d.volume
    d['ema20']=c.ewm(span=20,adjust=False).mean(); d['ema50']=c.ewm(span=50,adjust=False).mean(); d['ema200']=c.ewm(span=200,adjust=False).mean()
    delta=c.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean(); rs=gain/loss.replace(0,np.nan); d['rsi']=100-100/(1+rs)
    fast=c.ewm(span=12,adjust=False).mean(); slow=c.ewm(span=26,adjust=False).mean(); d['macd']=fast-slow; d['macd_signal']=d['macd'].ewm(span=9,adjust=False).mean(); d['macd_hist']=d.macd-d.macd_signal
    prev=c.shift(1); tr=np.maximum(d.high-d.low,np.maximum((d.high-prev).abs(),(d.low-prev).abs())); d['atr']=pd_rolling(tr,14)
    d['vol_ma20']=v.rolling(20).mean(); d['ret_7d']=c.pct_change(7); d['ret_30d']=c.pct_change(30); d['volatility20']=c.pct_change().rolling(20).std()*np.sqrt(20)
    return d.dropna()

def pd_rolling(values,n):
    import pandas as pd
    return pd.Series(values,index=getattr(values,'index',None)).rolling(n).mean()

def technical_scores(df):
    d=indicators(df); x=d.iloc[-1]; close=float(x.close)
    trend=90 if close>x.ema20>x.ema50 else 78 if close>x.ema20 else 52 if close>x.ema50 else 30
    momentum=90 if x.rsi>=60 and x.macd_hist>0 else 78 if x.rsi>=52 and x.macd_hist>0 else 62 if x.rsi>=45 else 38
    volume=85 if x.volume>x.vol_ma20*1.25 else 72 if x.volume>x.vol_ma20 else 52
    volatility=78 if .12<=x.volatility20<=.75 else 58
    return d,{'trend':trend,'momentum':momentum,'volume':volume,'volatility':volatility}, {'rsi':round(float(x.rsi),1),'atr':float(x.atr),'ret_7d':round(float(x.ret_7d*100),2),'ret_30d':round(float(x.ret_30d*100),2),'price':close}
