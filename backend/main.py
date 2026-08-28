from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .services.binance import get_symbols,get_klines,get_ticker_24h,market_snapshot,get_new_listings
from .services.stocks import get_stock
from .services.news import get_company_news
from .services.macro import get_employment_snapshot
from .engine.signal import analyze_crypto
from .engine.ai import explain
from .db import init_db,save_signal,recent,stats
app=FastAPI(title='Onchain AI Market Intelligence',version='2.0.0')
ROOT=Path(__file__).resolve().parent.parent
app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')
@app.on_event('startup')
def startup(): init_db()
@app.get('/')
def home(): return FileResponse(ROOT/'frontend'/'index.html')
@app.get('/api/health')
def health(): return {'ok':True,'service':'onchain-ai','version':'2.0.0'}
@app.get('/api/overview')
def overview(): return market_snapshot()
@app.get('/api/crypto/symbols')
def symbols():
    s=get_symbols(); return {'count':len(s),'symbols':s}
@app.get('/api/crypto/ticker')
def ticker():
    r=[x for x in get_ticker_24h() if x.get('symbol','').endswith('USDT')]; r.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True); return r[:100]
@app.get('/api/crypto/{symbol}')
def crypto(symbol:str,horizon:str=Query('swing',pattern='^(swing|long_term)$')):
    try:
        symbol=symbol.upper(); df=get_klines(symbol,'1d',180)
        if len(df)<60: raise HTTPException(400,'Not enough market history for this asset.')
        s=analyze_crypto(symbol,df,horizon); s['ai']=explain(s); save_signal(s); return s
    except HTTPException: raise
    except Exception as e: raise HTTPException(502,'Market data unavailable for this symbol.')
@app.get('/api/new-listings')
def new_listings(days:int=30): return get_new_listings(min(max(days,1),90))
@app.get('/api/stock/{symbol}')
def stock(symbol:str): return get_stock(symbol)
@app.get('/api/news/{symbol}')
def news(symbol:str): return get_company_news(symbol)
@app.get('/api/macro/nfp')
def nfp(): return get_employment_snapshot()
@app.get('/api/history')
def history(limit:int=100): return recent(min(max(limit,1),500))
@app.get('/api/performance')
def performance(): return stats()
