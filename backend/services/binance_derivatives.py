import time
import requests
from ..config import REQUEST_TIMEOUT
FUTURES='https://fapi.binance.com'
OPTIONS='https://eapi.binance.com'
_cache={}
def _get(base,path,params=None,ttl=10):
    key=(base,path,tuple(sorted((params or {}).items())))
    now=time.time(); hit=_cache.get(key)
    if hit and now-hit[0]<ttl:return hit[1]
    r=requests.get(base+path,params=params,timeout=REQUEST_TIMEOUT,headers={'User-Agent':'OnchainAI/1.0','Accept':'application/json'})
    r.raise_for_status(); data=r.json(); _cache[key]=(now,data); return data
def futures_ticker(): return _get(FUTURES,'/fapi/v1/ticker/24hr',ttl=10)
def futures_funding(symbol=None): return _get(FUTURES,'/fapi/v1/premiumIndex',({'symbol':symbol.upper()} if symbol else None),ttl=10)
def futures_open_interest(symbol): return _get(FUTURES,'/fapi/v1/openInterest',{'symbol':symbol.upper()},ttl=10)
def futures_exchange_info(): return _get(FUTURES,'/fapi/v1/exchangeInfo',ttl=300)
def futures_klines(symbol,interval='1h',limit=100): return _get(FUTURES,'/fapi/v1/klines',{'symbol':symbol.upper(),'interval':interval,'limit':min(limit,1500)},ttl=20)
def options_exchange_info(): return _get(OPTIONS,'/eapi/v1/exchangeInfo',ttl=300)
def options_mark_price(): return _get(OPTIONS,'/eapi/v1/mark',ttl=10)
def options_ticker(): return _get(OPTIONS,'/eapi/v1/ticker',ttl=10)
def derivatives_snapshot(symbol=None):
    symbol=symbol.upper() if symbol else None
    tickers=futures_ticker(); rows=[x for x in tickers if not symbol or x.get('symbol')==symbol]
    rows.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True)
    funding=futures_funding(symbol); oi=futures_open_interest(symbol) if symbol else None
    return {'futures':{'ticker':rows[:20],'funding':funding,'open_interest':oi},'options':{'ticker':options_ticker(),'mark':options_mark_price()},'updated_at':time.time(),'source':'Binance public derivatives market data'}
