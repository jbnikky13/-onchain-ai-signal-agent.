from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .services.binance import *
from .services.stocks import get_stock
from .services.news import get_company_news
from .services.macro import get_employment_snapshot
from .engine.signal import analyze_crypto
from .engine.ai import explain
from .db import init_db,save_signal,recent
app=FastAPI(title="Onchain AI Signal Agent")
ROOT=Path(__file__).resolve().parent.parent
app.mount("/static",StaticFiles(directory=ROOT/"frontend"),name="static")
@app.on_event("startup")
def startup(): init_db()
@app.get("/")
def home(): return FileResponse(ROOT/"frontend"/"index.html")
@app.get("/api/health")
def health(): return {"ok":True}
@app.get("/api/crypto/symbols")
def symbols():
    s=get_symbols(); return {"count":len(s),"symbols":s}
@app.get("/api/crypto/ticker")
def ticker():
    r=[x for x in get_ticker_24h() if x.get("symbol","").endswith("USDT")]; r.sort(key=lambda x:float(x.get("quoteVolume",0)),reverse=True); return r[:100]
@app.get("/api/crypto/{symbol}")
def crypto(symbol:str,horizon:str=Query("swing",pattern="^(swing|long_term)$")):
    try:
        df=get_klines(symbol,"1d",180)
        if len(df)<60: raise HTTPException(400,"Not enough history.")
        s=analyze_crypto(symbol.upper(),df,horizon); s["ai"]=explain(s); save_signal(s); return s
    except HTTPException: raise
    except Exception as e: raise HTTPException(502,str(e))
@app.get("/api/new-listings")
def new_listings():
    import time
    now=int(time.time()*1000); out=[]
    for s in get_exchange_info()["symbols"]:
        d=s.get("onboardDate")
        if s.get("status")=="TRADING" and s.get("quoteAsset")=="USDT" and d and now-int(d)<=14*86400000:
            out.append({"symbol":s["symbol"],"baseAsset":s["baseAsset"],"onboardDate":d})
    return out[:100]
@app.get("/api/stock/{symbol}")
def stock(symbol): return get_stock(symbol)
@app.get("/api/news/{symbol}")
def news(symbol): return get_company_news(symbol)
@app.get("/api/macro/nfp")
def nfp(): return get_employment_snapshot()
@app.get("/api/history")
def history(limit:int=100): return recent(min(max(limit,1),500))
