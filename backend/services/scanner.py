import concurrent.futures
from .binance import get_ticker_24h, get_klines
from ..engine.fused_signal import build_fused_market_signal

def scan_market(limit=25, interval='1h'):
    tickers=[x for x in get_ticker_24h() if x.get('symbol','').endswith('USDT') and float(x.get('quoteVolume',0) or 0)>0]
    tickers.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True)
    candidates=tickers[:max(5,min(limit,50))]
    def one(t):
        try:
            df=get_klines(t['symbol'],interval,120)
            if len(df)<60:return None
            r=build_fused_market_signal(df)
            return {'symbol':t['symbol'],'price':float(t.get('lastPrice') or 0),'change_24h':float(t.get('priceChangePercent') or 0),'quote_volume':float(t.get('quoteVolume') or 0),'score':r['score'],'bias':r['bias'],'confidence':r['confidence'],'components':r['components']}
        except Exception:return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: rows=[r for r in ex.map(one,candidates) if r]
    rows.sort(key=lambda x:x['score'],reverse=True)
    return {'ok':True,'interval':interval,'count':len(rows),'scanned':len(candidates),'signals':rows}
