from fastapi import FastAPI, HTTPException, Query
from .services.binance import get_symbols,get_klines,get_ticker_24h,market_snapshot,get_new_listings,market_status
from .services.stocks import get_stock
from .services.news import get_company_news
from .services.macro import get_employment_snapshot
from .services.onchain import RPCS,analyze_address,contract_metadata,transaction
from .services.intelligence import intelligence,transfers,whales,liquidity,risk,holders_from_transfers
from .services.fusion import build_signal_fusion
from .engine.signal import analyze_crypto
from .engine.technical import technical_scores
from .engine.fused_signal import build_fused_market_signal
from .engine.ai import explain
from .db import init_db,save_signal,recent,stats

app=FastAPI(title="Onchain AI Market Intelligence API",version="2.7.0",docs_url="/api/docs",redoc_url="/api/redoc")
@app.on_event("startup")
def startup():
    try:init_db()
    except Exception:pass
@app.get("/api")
def api_root():return {"ok":True,"service":"onchain-ai","version":"2.7.0","mode":"research-only"}
@app.get("/api/health")
def health():return {"ok":True,"service":"onchain-ai","version":"2.7.0"}
@app.get("/api/market/status")
def market_feed_status():return market_status()
@app.get("/api/overview")
def overview():
    try:return market_snapshot()
    except Exception as exc:raise HTTPException(502,f"Live market feed unavailable: {str(exc)[:180]}")
@app.get("/api/crypto/symbols")
def symbols():
    s=get_symbols();return {"count":len(s),"symbols":s}
@app.get("/api/crypto/ticker")
def ticker():
    rows=[x for x in get_ticker_24h() if x.get("symbol","").endswith("USDT")];rows.sort(key=lambda x:float(x.get("quoteVolume",0) or 0),reverse=True);return rows[:100]
@app.get("/api/crypto/{symbol}/technical")
def technical(symbol:str,interval:str=Query("1h",pattern="^(5m|15m|1h|4h|1d)$"),limit:int=300):
    try:
        df=get_klines(symbol.upper(),interval,min(max(limit,80),500))
        if len(df)<60:raise HTTPException(400,"Not enough market history for technical analysis.")
        d,scores,raw=technical_scores(df);x=d.iloc[-1]
        return {"symbol":symbol.upper(),"interval":interval,"price":float(x.close),"scores":scores,"indicators":{"ema20":float(x.ema20),"ema50":float(x.ema50),"ema200":float(x.ema200),"rsi":float(x.rsi),"macd":float(x.macd),"macd_signal":float(x.macd_signal),"macd_hist":float(x.macd_hist),"atr":float(x.atr),"volume":float(x.volume),"volume_ma20":float(x.vol_ma20),"volatility20":float(x.volatility20)},"returns":{"7d":raw["ret_7d"],"30d":raw["ret_30d"]},"bars":len(d)}
    except HTTPException:raise
    except Exception as exc:raise HTTPException(502,f"Technical data unavailable: {str(exc)[:160]}")
@app.get("/api/crypto/{symbol}/fused")
def fused(symbol:str,chain:str|None=None,token:str|None=None,interval:str=Query("1h",pattern="^(5m|15m|1h|4h|1d)$"),limit:int=300):
    try:
        df=get_klines(symbol.upper(),interval,min(max(limit,80),500))
        if len(df)<60:raise HTTPException(400,"Not enough market history for fused analysis.")
        context={"score":50,"liquidity":50,"safety":50,"label":"NOT PROVIDED"}
        onchain_detail=None
        if chain and token:
            fusion=build_signal_fusion(chain,token)
            if not fusion.get("ok"):raise HTTPException(502,"On-chain intelligence could not be loaded for this token.")
            oc=fusion.get("components",{})
            context={"score":fusion.get("fusion_score",50),"liquidity":oc.get("dex_liquidity",50),"safety":oc.get("contract_safety",50),"label":fusion.get("label","NEUTRAL")}
            onchain_detail=fusion
        result=build_fused_market_signal(df,context)
        result.update({"symbol":symbol.upper(),"interval":interval,"onchain":onchain_detail or {"score":50,"label":"NOT PROVIDED"},"data_mode":"multi-source" if onchain_detail else "market-only"})
        return result
    except HTTPException:raise
    except Exception as exc:raise HTTPException(502,f"Fused signal unavailable: {str(exc)[:160]}")
@app.get("/api/crypto/{symbol}")
def crypto(symbol:str,horizon:str=Query("swing",pattern="^(swing|long_term)$")):
    try:
        symbol=symbol.upper();df=get_klines(symbol,"1d",180)
        if len(df)<60:raise HTTPException(400,"Not enough market history for this asset.")
        signal=analyze_crypto(symbol,df,horizon);signal["ai"]=explain(signal)
        try:save_signal(signal)
        except Exception:pass
        return signal
    except HTTPException:raise
    except Exception as exc:raise HTTPException(502,f"Market data unavailable: {str(exc)[:120]}")
@app.get("/api/new-listings")
def new_listings(days:int=30):return get_new_listings(min(max(days,1),90))
@app.get("/api/onchain/chains")
def onchain_chains():return {"chains":sorted(RPCS.keys())}
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
@app.get("/api/onchain/{chain}/token/{address}/fusion")
def token_fusion(chain:str,address:str,market_score:float|None=None,market_bias:str|None=None):
    try:return build_signal_fusion(chain,address,market_score,market_bias)
    except ValueError as exc:raise HTTPException(400,str(exc))
    except Exception as exc:raise HTTPException(502,f"Signal fusion unavailable: {str(exc)[:160]}")
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
def stock(symbol:str):return get_stock(symbol)
@app.get("/api/news/{symbol}")
def news(symbol:str):return get_company_news(symbol)
@app.get("/api/macro/nfp")
def nfp():return get_employment_snapshot()
@app.get("/api/history")
def history(limit:int=100):
    try:return recent(min(max(limit,1),500))
    except Exception:return []
@app.get("/api/performance")
def performance():
    try:return stats()
    except Exception:return {"signals":0,"average_score":0,"buy_calls":0,"sell_calls":0}
