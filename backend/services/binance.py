import json
import time
import requests
import pandas as pd
from ..config import BINANCE_BASE_URL, BINANCE_FALLBACK_URL, REQUEST_TIMEOUT, CACHE_TTL

_cache = {}
_last_status = {"provider": None, "ok": False, "error": None, "checked_at": None}

def _get(path, params=None, ttl=CACHE_TTL):
    key = (path, tuple(sorted((params or {}).items())))
    now = time.time()
    cached = _cache.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1]
    last_error = None
    for base in (BINANCE_BASE_URL, BINANCE_FALLBACK_URL):
        if not base:
            continue
        try:
            r = requests.get(base.rstrip('/') + path, params=params, timeout=REQUEST_TIMEOUT, headers={'User-Agent':'OnchainAI/1.0','Accept':'application/json'})
            r.raise_for_status()
            data = r.json()
            _cache[key] = (time.time(), data)
            _last_status.update({"provider": base, "ok": True, "error": None, "checked_at": time.time()})
            return data
        except (requests.RequestException, ValueError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
    _last_status.update({"provider": None, "ok": False, "error": last_error, "checked_at": time.time()})
    if cached:
        return cached[1]
    raise RuntimeError(f'Binance market data unavailable: {last_error}')

def get_exchange_info():
    return _get('/api/v3/exchangeInfo', ttl=300)

def get_symbols(quote='USDT'):
    return [s['symbol'] for s in get_exchange_info()['symbols'] if s.get('status') == 'TRADING' and s.get('quoteAsset') == quote and s.get('isSpotTradingAllowed', True)]

def get_klines(symbol, interval='1d', limit=180):
    raw = _get('/api/v3/klines', {'symbol': symbol.upper(), 'interval': interval, 'limit': min(limit, 1000)}, ttl=30)
    cols = ['open_time','open','high','low','close','volume','close_time','quote_volume','trades','taker_buy_base','taker_buy_quote','ignore']
    d = pd.DataFrame(raw, columns=cols)
    for c in ['open','high','low','close','volume','quote_volume']:
        d[c] = pd.to_numeric(d[c], errors='coerce')
    return d

def get_ticker_24h():
    return _get('/api/v3/ticker/24hr', ttl=15)

def get_order_book(symbol, limit=20):
    return _get('/api/v3/depth', {'symbol': symbol.upper(), 'limit': min(limit, 100)}, ttl=5)

def get_price(symbol):
    return _get('/api/v3/ticker/price', {'symbol': symbol.upper()}, ttl=5)

def _known_usdt_tickers():
    symbols = ['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','TRXUSDT','AVAXUSDT','LINKUSDT','DOTUSDT','MATICUSDT','LTCUSDT','BCHUSDT','ATOMUSDT','UNIUSDT','ETCUSDT','XLMUSDT','NEARUSDT','APTUSDT','SUIUSDT','ARBUSDT','OPUSDT','PEPEUSDT','SHIBUSDT']
    return _get('/api/v3/ticker/24hr', {'symbols': json.dumps(symbols, separators=(',',':'))}, ttl=15)

def _coingecko_fallback():
    url='https://api.coingecko.com/api/v3/coins/markets'
    params={'vs_currency':'usd','order':'volume_desc','per_page':50,'page':1,'sparkline':'false','price_change_percentage':'24h'}
    r=requests.get(url,params=params,timeout=REQUEST_TIMEOUT,headers={'User-Agent':'OnchainAI/1.0','Accept':'application/json'})
    r.raise_for_status(); rows=[]
    for x in r.json():
        sym=(x.get('symbol') or '').upper()
        rows.append({'symbol':f'{sym}USDT','baseAsset':sym,'lastPrice':str(x.get('current_price') or 0),'priceChangePercent':str(x.get('price_change_percentage_24h') or 0),'quoteVolume':str(x.get('total_volume') or 0),'provider':'coingecko-fallback'})
    return rows

def market_snapshot():
    try:
        t=[x for x in get_ticker_24h() if x.get('symbol','').endswith('USDT')]
        provider='binance-public-market-data'
    except Exception as primary_error:
        try:
            t=_coingecko_fallback(); provider='coingecko-fallback'
            _last_status.update({"provider":provider,"ok":True,"error":str(primary_error),"checked_at":time.time()})
        except Exception:
            t=_known_usdt_tickers(); provider='binance-public-market-data'
    t.sort(key=lambda x: float(x.get('quoteVolume',0) or 0), reverse=True)
    movers=sorted(t,key=lambda x: abs(float(x.get('priceChangePercent',0) or 0)),reverse=True)
    return {'pairs':len(t),'top_volume':t[:12],'top_movers':movers[:12],'updated_at':time.time(),'provider':provider,'live':True,'source_status':dict(_last_status)}

def market_status():
    try:
        price=get_price('BTCUSDT')
        return {'ok':True,'live':True,'provider':_last_status.get('provider') or BINANCE_BASE_URL,'btc':price,'checked_at':time.time(),'last_error':_last_status.get('error')}
    except Exception as exc:
        return {'ok':False,'live':False,'provider':None,'error':str(exc),'checked_at':time.time()}

def get_new_listings(days=30):
    now=int(time.time()*1000); cutoff=now-days*86400000; out=[]
    for s in get_exchange_info()['symbols']:
        d=s.get('onboardDate')
        if s.get('status')=='TRADING' and s.get('quoteAsset')=='USDT' and d and int(d)>=cutoff:
            out.append({'symbol':s['symbol'],'baseAsset':s['baseAsset'],'onboardDate':d})
    return sorted(out,key=lambda x:int(x['onboardDate']),reverse=True)[:100]
