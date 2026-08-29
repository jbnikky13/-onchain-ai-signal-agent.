from fastapi import FastAPI, HTTPException, Query
from .services.binance import get_symbols,get_klines,get_ticker_24h,market_snapshot,get_new_listings
from .services.stocks import get_stock
from .services.news import get_company_news
from .services.macro import get_employment_snapshot
from .services.onchain import RPCS,analyze_address,contract_metadata,transaction
from .services.intelligence import intelligence,transfers,whales,liquidity,risk,holders_from_transfers
from .engine.signal import analyze_crypto
from .engine.ai import explain
from .db import init_db,save_signal,recent,stats

app=FastAPI(title="Onchain AI Market Intelligence API",version="2.3.0",docs_url="/api/docs",redoc_url="/api/redoc")
@app.on_event("startup")
def startup(): init_db()
@app.get("/api")
def api_root(): return {"ok":True,"service":"onchain-ai","version":"2.3.0","mode":"research-only","modules":["market","technical","onchain","token-intelligence","whales","liquidity","risk","listings","stocks","macro","history"]}
@app.get("/api/health")
def health(): return {"ok":True,"service":"onchain-ai","version":"2.3.0"}
@app.get("/api/overview")
def overview(): return market_snapshot()
@app.get("/api/crypto/symbols")
def symbols():
    s=get_symbols(); return {"count":len(s),"symbols":s}
@app.get("/api/crypto/ticker")
def ticker():
    rows=[x for x in get_ticker_24h() if x.get("symbol","").endswith("USDT")]; rows.sort(key=lambda x:float(x.get("quoteVolume",0) or 0),reverse=True); return rows[:100]
@app.get("/api/crypto/{symbol}")
def crypto(symbol:str,horizon:str=Query("swing",pattern="^(swing|long_term)$")):
    try:
        symbol=symbol.upper(); df=get_klines(symbol,"1d",180)
        if len(df)<60: raise HTTPException(400,"Not enough market history for this asset.")
        signal=analyze_crypto(symbol,df,horizon); signal["ai"]=explain(signal); save_signal(signal); return signal
    except HTTPException: raise
    except Exception as exc: raise HTTPException(502,f"Market data unavailable: {str(exc)[:120]}")
@app.get("/api/new-listings")
def new_listings(days:int=30): return get_new_listings(min(max(days,1),90))
@app.get("/api/onchain/chains")
def onchain_chains(): return {"chains":sorted(RPCS.keys())}
@app.get("/api/onchain/{chain}/address/{address}")
def onchain_address(chain:str,address:str):
    try:return analyze_address(chain,address)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"On-chain RPC unavailable: {str(exc)[:160]}")
@app.get("/api/onchain/{chain}/contract/{address}")
def onchain_contract(chain:str,address:str):
    try:return contract_metadata(chain,address)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Contract lookup unavailable: {str(exc)[:160]}")
@app.get("/api/onchain/{chain}/tx/{tx_hash}")
def onchain_tx(chain:str,tx_hash:str):
    try:return transaction(chain,tx_hash)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Transaction lookup unavailable: {str(exc)[:160]}")
@app.get("/api/onchain/{chain}/token/{address}")
def token_intel(chain:str,address:str):
    try:return intelligence(chain,address)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Token intelligence unavailable: {str(exc)[:160]}")
@app.get("/api/onchain/{chain}/token/{address}/transfers")
def token_transfer_api(chain:str,address:str,limit:int=100):
    try:return transfers(chain,address,min(max(limit,1),100))
    except ValueError as exc:raise HTTPException(400,str(exc))
@app.get("/api/onchain/{chain}/token/{address}/whales")
def whale_api(chain:str,address:str,limit:int=100):
    try:return whales(chain,address,min(max(limit,1),100))
    except ValueError as exc:raise HTTPException(400,str(exc))
@app.get("/api/onchain/{chain}/token/{address}/holders")
def holder_api(chain:str,address:str,limit:int=100):
    try:return holders_from_transfers(chain,address,min(max(limit,1),100))
    except ValueError as exc:raise HTTPException(400,str(exc))
@app.get("/api/onchain/{chain}/token/{address}/liquidity")
def liquidity_api(chain:str,address:str):
    try:return liquidity(chain,address)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Liquidity provider unavailable: {str(exc)[:160]}")
@app.get("/api/onchain/{chain}/token/{address}/risk")
def risk_api(chain:str,address:str):
    try:return risk(chain,address)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Risk scan unavailable: {str(exc)[:160]}")
@app.get("/api/stock/{symbol}")
def stock(symbol:str): return get_stock(symbol)
@app.get("/api/news/{symbol}")
def news(symbol:str): return get_company_news(symbol)
@app.get("/api/macro/nfp")
def nfp(): return get_employment_snapshot()
@app.get("/api/history")
def history(limit:int=100): return recent(min(max(limit,1),500))
@app.get("/api/performance")
def performance(): return stats()
