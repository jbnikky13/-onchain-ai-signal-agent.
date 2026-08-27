import requests, pandas as pd
BASE="https://api.binance.com"
def get_exchange_info():
    r=requests.get(f"{BASE}/api/v3/exchangeInfo",timeout=20); r.raise_for_status(); return r.json()
def get_symbols(quote="USDT"):
    return [s["symbol"] for s in get_exchange_info()["symbols"] if s.get("status")=="TRADING" and s.get("quoteAsset")==quote and s.get("isSpotTradingAllowed",True)]
def get_klines(symbol,interval="1d",limit=180):
    r=requests.get(f"{BASE}/api/v3/klines",params={"symbol":symbol.upper(),"interval":interval,"limit":limit},timeout=20); r.raise_for_status()
    cols=["open_time","open","high","low","close","volume","close_time","quote_volume","trades","taker_buy_base","taker_buy_quote","ignore"]
    d=pd.DataFrame(r.json(),columns=cols)
    for c in ["open","high","low","close","volume","quote_volume"]: d[c]=pd.to_numeric(d[c],errors="coerce")
    return d
def get_ticker_24h():
    r=requests.get(f"{BASE}/api/v3/ticker/24hr",timeout=20); r.raise_for_status(); return r.json()
