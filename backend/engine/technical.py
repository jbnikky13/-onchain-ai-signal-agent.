import numpy as np
def indicators(d):
    d=d.copy(); c=d.close; v=d.volume
    d["ema20"]=c.ewm(span=20,adjust=False).mean(); d["ema50"]=c.ewm(span=50,adjust=False).mean()
    delta=c.diff(); gain=delta.clip(lower=0).rolling(14).mean(); loss=(-delta.clip(upper=0)).rolling(14).mean()
    rs=gain/loss.replace(0,np.nan); d["rsi"]=100-100/(1+rs)
    d["macd"]=c.ewm(span=12,adjust=False).mean()-c.ewm(span=26,adjust=False).mean(); d["macd_signal"]=d.macd.ewm(span=9,adjust=False).mean()
    prev=c.shift(1); tr=np.maximum(d.high-d.low,np.maximum((d.high-prev).abs(),(d.low-prev).abs())); d["atr"]=tr.rolling(14).mean()
    d["vol_ma20"]=v.rolling(20).mean(); d["ret_7d"]=c.pct_change(7); d["volatility20"]=c.pct_change().rolling(20).std()*np.sqrt(20)
    return d.dropna()
def technical_scores(df):
    d=indicators(df); x=d.iloc[-1]
    return d,{"trend":90 if x.close>x.ema20>x.ema50 else 65 if x.close>x.ema20 else 35,
              "momentum":85 if x.rsi>=55 and x.macd>x.macd_signal else 70 if x.rsi>=45 else 35,
              "volume":82 if x.volume>x.vol_ma20 else 55,
              "volatility":75 if .15<=x.volatility20<=.90 else 55}

