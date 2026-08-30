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
def futures_open_interest_history(symbol,period='1h',limit=30): return _get(FUTURES,'/futures/data/openInterestHist',{'symbol':symbol.upper(),'period':period,'limit':min(limit,500)},ttl=30)
def futures_long_short(symbol,period='1h',limit=30): return _get(FUTURES,'/futures/data/globalLongShortAccountRatio',{'symbol':symbol.upper(),'period':period,'limit':min(limit,500)},ttl=30)
def futures_top_long_short(symbol,period='1h',limit=30): return _get(FUTURES,'/futures/data/topLongShortAccountRatio',{'symbol':symbol.upper(),'period':period,'limit':min(limit,500)},ttl=30)
def futures_taker_flow(symbol,period='1h',limit=30): return _get(FUTURES,'/futures/data/takerlongshortRatio',{'symbol':symbol.upper(),'period':period,'limit':min(limit,500)},ttl=30)
def futures_exchange_info(): return _get(FUTURES,'/fapi/v1/exchangeInfo',ttl=300)
def futures_klines(symbol,interval='1h',limit=100): return _get(FUTURES,'/fapi/v1/klines',{'symbol':symbol.upper(),'interval':interval,'limit':min(limit,1500)},ttl=20)
def futures_mark_price(symbol=None): return _get(FUTURES,'/fapi/v1/premiumIndex',({'symbol':symbol.upper()} if symbol else None),ttl=10)
def options_exchange_info(): return _get(OPTIONS,'/eapi/v1/exchangeInfo',ttl=300)
def options_mark_price(): return _get(OPTIONS,'/eapi/v1/mark',ttl=10)
def options_ticker(): return _get(OPTIONS,'/eapi/v1/ticker',ttl=10)
def options_klines(symbol,interval='1h',limit=100): return _get(OPTIONS,'/eapi/v1/klines',{'symbol':symbol.upper(),'interval':interval,'limit':min(limit,1000)},ttl=20)

def _futures_detail(symbol):
    symbol=symbol.upper(); ticker=next((x for x in futures_ticker() if x.get('symbol')==symbol),None)
    funding=futures_funding(symbol); oi=futures_open_interest(symbol)
    return {'symbol':symbol,'ticker':ticker,'funding':funding,'open_interest':oi,'open_interest_history':futures_open_interest_history(symbol),'long_short_ratio':futures_long_short(symbol),'top_trader_long_short':futures_top_long_short(symbol),'taker_flow':futures_taker_flow(symbol),'mark_price':funding,'source':'Binance USDⓈ-M Futures public market data'}

def derivatives_snapshot(symbol=None):
    symbol=symbol.upper() if symbol else None; tickers=futures_ticker(); rows=[x for x in tickers if not symbol or x.get('symbol')==symbol]; rows.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True)
    return {'futures':{'ticker':rows[:50],'funding':futures_funding(symbol),'open_interest':futures_open_interest(symbol) if symbol else None,'details':_futures_detail(symbol) if symbol else None},'options':{'ticker':options_ticker(),'mark':options_mark_price(),'exchange_info':options_exchange_info()},'updated_at':time.time(),'source':'Binance public derivatives market data'}

def derivatives_signal(symbol):
    d=_futures_detail(symbol); funding=d['funding'] if isinstance(d['funding'],dict) else {}; oi=d['open_interest'] if isinstance(d['open_interest'],dict) else {}; ls=d['long_short_ratio'][-1] if d['long_short_ratio'] else {}; taker=d['taker_flow'][-1] if d['taker_flow'] else {}
    fr=float(funding.get('lastFundingRate',0) or 0); ratio=float(ls.get('longShortRatio',1) or 1); taker_ratio=float(taker.get('buySellRatio',1) or 1)
    funding_score=max(0,min(100,50-fr*10000)); positioning_score=max(0,min(100,50+(ratio-1)*35)); flow_score=max(0,min(100,50+(taker_ratio-1)*35)); score=round(funding_score*.30+positioning_score*.35+flow_score*.35,1)
    bias='BULLISH' if score>=60 else 'BEARISH' if score<=40 else 'NEUTRAL'
    return {'symbol':symbol.upper(),'score':score,'bias':bias,'funding_rate':fr,'long_short_ratio':ratio,'taker_buy_sell_ratio':taker_ratio,'open_interest':float(oi.get('openInterest',0) or 0),'components':{'funding':round(funding_score,1),'positioning':round(positioning_score,1),'taker_flow':round(flow_score,1)},'source':'Binance USDⓈ-M Futures public market data'}
