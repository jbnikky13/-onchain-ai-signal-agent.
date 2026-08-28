import time, requests, pandas as pd
from ..config import BINANCE_BASE_URL,REQUEST_TIMEOUT,CACHE_TTL
_cache={}
def _get(path,params=None,ttl=CACHE_TTL):
    key=(path,tuple(sorted((params or {}).items())))
    now=time.time()
    if key in _cache and now-_cache[key][0]<ttl: return _cache[key][1]
    r=requests.get(BINANCE_BASE_URL+path,params=params,timeout=REQUEST_TIMEOUT); r.raise_for_status(); data=r.json(); _cache[key]=(now,data); return data

def get_exchange_info(): return _get('/api/v3/exchangeInfo',ttl=300)
def get_symbols(quote='USDT'): return [s['symbol'] for s in get_exchange_info()['symbols'] if s.get('status')=='TRADING' and s.get('quoteAsset')==quote and s.get('isSpotTradingAllowed',True)]
def get_klines(symbol,interval='1d',limit=180):
    raw=_get('/api/v3/klines',{'symbol':symbol.upper(),'interval':interval,'limit':min(limit,1000)},ttl=30)
    cols=['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore']; d=pd.DataFrame(raw,columns=cols)
    for c in ['open','high','low','close','volume','quote_volume']: d[c]=pd.to_numeric(d[c],errors='coerce')
    return d

def get_ticker_24h(): return _get('/api/v3/ticker/24hr',ttl=20)
def market_snapshot():
    t=[x for x in get_ticker_24h() if x.get('symbol','').endswith('USDT')]
    t.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True); movers=sorted(t,key=lambda x:abs(float(x.get('priceChangePercent',0) or 0)),reverse=True)
    return {'pairs':len(t),'top_volume':t[:12],'top_movers':movers[:12],'updated_at':time.time()}

def get_new_listings(days=30):
    now=int(time.time()*1000); cutoff=now-days*86400000; out=[]
    for s in get_exchange_info()['symbols']:
        d=s.get('onboardDate')
        if s.get('status')=='TRADING' and s.get('quoteAsset')=='USDT' and d and int(d)>=cutoff: out.append({'symbol':s['symbol'],'baseAsset':s['baseAsset'],'onboardDate':d})
    return sorted(out,key=lambda x:int(x['onboardDate']),reverse=True)[:100]
