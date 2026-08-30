from fastapi import FastAPI, HTTPException, Query
from .services.binance import get_symbols,get_klines,get_ticker_24h,market_snapshot,get_new_listings,market_status
from .services.binance_derivatives import derivatives_snapshot,futures_ticker,futures_funding,futures_open_interest,futures_mark_price,derivatives_signal,options_exchange_info,options_ticker,options_mark_price
from .services.scanner import scan_market
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
app=FastAPI(title='Onchain AI Market Intelligence API',version='3.1.0',docs_url='/api/docs',redoc_url='/api/redoc')
@app.on_event('startup')
def startup():
    try:init_db()
    except Exception:pass
@app.get('/api')
def api_root():return {'ok':True,'service':'onchain-ai','version':'3.1.0','mode':'research-only'}
@app.get('/api/health')
def health():return {'ok':True,'service':'onchain-ai','version':'3.1.0'}
@app.get('/api/market/status')
def market_feed_status():return market_status()
@app.get('/api/overview')
def overview():
    try:return market_snapshot()
    except Exception as exc:raise HTTPException(502,f'Live market feed unavailable: {str(exc)[:180]}')
@app.get('/api/derivatives')
def derivatives(symbol:str|None=None):
    try:return derivatives_snapshot(symbol)
    except Exception as exc:raise HTTPException(502,f'Binance derivatives data unavailable: {str(exc)[:180]}')
@app.get('/api/derivatives/futures')
def futures(symbol:str|None=None):
    try:
        rows=futures_ticker(); rows=[x for x in rows if not symbol or x.get('symbol')==symbol.upper()]; rows.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True)
        return {'count':len(rows),'symbols':rows[:100],'source':'Binance USDⓈ-M Futures public market data'}
    except Exception as exc:raise HTTPException(502,f'Futures data unavailable: {str(exc)[:160]}')
@app.get('/api/derivatives/futures/{symbol}')
def futures_symbol(symbol:str):
    try:return {'symbol':symbol.upper(),'funding':futures_funding(symbol),'mark_price':futures_mark_price(symbol),'open_interest':futures_open_interest(symbol),'ticker':next((x for x in futures_ticker() if x.get('symbol')==symbol.upper()),None),'signal':derivatives_signal(symbol),'source':'Binance USDⓈ-M Futures public market data'}
    except Exception as exc:raise HTTPException(502,f'Futures symbol data unavailable: {str(exc)[:160]}')
@app.get('/api/derivatives/futures/{symbol}/signal')
def futures_signal(symbol:str):
    try:return derivatives_signal(symbol)
    except Exception as exc:raise HTTPException(502,f'Derivatives signal unavailable: {str(exc)[:160]}')
@app.get('/api/derivatives/options')
def options():
    try:return {'exchange_info':options_exchange_info(),'ticker':options_ticker(),'mark':options_mark_price(),'source':'Binance Options public market data'}
    except Exception as exc:raise HTTPException(502,f'Options data unavailable: {str(exc)[:160]}')
@app.get('/api/scan')
def scan(limit:int=Query(20,ge=5,le=50),interval:str=Query('1h',pattern='^(5m|15m|1h|4h|1d)$')):
    try:return scan_market(limit,interval)
    except Exception as exc:raise HTTPException(502,f'Market scan unavailable: {str(exc)[:180]}')
@app.get('/api/crypto/symbols')
def symbols():return {'count':len(get_symbols()),'symbols':get_symbols()}
@app.get('/api/crypto/ticker')
def ticker():
    rows=[x for x in get_ticker_24h() if x.get('symbol','').endswith('USDT')];rows.sort(key=lambda x:float(x.get('quoteVolume',0) or 0),reverse=True);return rows[:100]
@app.get('/api/crypto/{symbol}/technical')
def technical(symbol:str,interval:str=Query('1h',pattern='^(5m|15m|1h|4h|1d)$'),limit:int=300):
    try:
        df=get_klines(symbol.upper(),interval,min(max(limit,80),500));d,scores,raw=technical_scores(df);x=d.iloc[-1]
        return {'symbol':symbol.upper(),'interval':interval,'price':float(x.close),'scores':scores,'indicators':{k:float(getattr(x,k)) for k in ['ema20','ema50','ema200','rsi','macd','macd_signal','macd_hist','atr','volume','vol_ma20','volatility20']},'returns':{'7d':raw['ret_7d'],'30d':raw['ret_30d']},'bars':len(d)}
    except Exception as exc:raise HTTPException(502,f'Technical data unavailable: {str(exc)[:160]}')
@app.get('/api/crypto/{symbol}/fused')
def fused(symbol:str,chain:str|None=None,token:str|None=None,interval:str=Query('1h',pattern='^(5m|15m|1h|4h|1d)$'),limit:int=300):
    try:
        symbol=symbol.upper();df=get_klines(symbol,interval,min(max(limit,80),500))
        if len(df)<60:raise HTTPException(400,'Not enough market history for fused analysis.')
        context={'score':50,'liquidity':50,'safety':50,'derivatives':50,'label':'NOT PROVIDED'};detail=None
        if chain and token:
            f=build_signal_fusion(chain,token);oc=f.get('components',{})
            if not f.get('ok'):raise HTTPException(502,'On-chain intelligence could not be loaded for this token.')
            context.update({'score':f.get('fusion_score',50),'liquidity':oc.get('dex_liquidity',50),'safety':oc.get('contract_safety',50),'label':f.get('label','NEUTRAL')});detail=f
        deriv=None
        try:
            deriv=derivatives_signal(symbol);context['derivatives']=deriv.get('score',50)
        except Exception:
            deriv={'symbol':symbol,'score':50,'bias':'UNAVAILABLE','components':{'funding':50,'positioning':50,'taker_flow':50},'source':'Binance derivatives unavailable'}
        result=build_fused_market_signal(df,context);result.update({'symbol':symbol,'interval':interval,'onchain':detail or {'score':50,'label':'NOT PROVIDED'},'derivatives':deriv,'data_mode':'multi-source' if detail else 'market+derivatives'});return result
    except HTTPException:raise
    except Exception as exc:raise HTTPException(502,f'Fused signal unavailable: {str(exc)[:160]}')
@app.get('/api/crypto/{symbol}')
def crypto(symbol:str,horizon:str=Query('swing',pattern='^(swing|long_term)$')):
    try:
        df=get_klines(symbol.upper(),'1d',180);signal=analyze_crypto(symbol.upper(),df,horizon);signal['ai']=explain(signal)
        try:save_signal(signal)
        except Exception:pass
        return signal
    except Exception as exc:raise HTTPException(502,f'Market data unavailable: {str(exc)[:120]}')
@app.get('/api/new-listings')
def new_listings(days:int=30):return get_new_listings(min(max(days,1),90))
@app.get('/api/onchain/chains')
def onchain_chains():return {'chains':sorted(RPCS.keys())}
@app.get('/api/onchain/{chain}/address/{address}')
def onchain_address(chain:str,address:str):return analyze_address(chain,address)
@app.get('/api/onchain/{chain}/contract/{address}')
def onchain_contract(chain:str,address:str):return contract_metadata(chain,address)
@app.get('/api/onchain/{chain}/tx/{tx_hash}')
def onchain_tx(chain:str,tx_hash:str):return transaction(chain,tx_hash)
@app.get('/api/onchain/{chain}/token/{address}')
def token_intel(chain:str,address:str):return intelligence(chain,address)
@app.get('/api/onchain/{chain}/token/{address}/fusion')
def token_fusion(chain:str,address:str,market_score:float|None=None,market_bias:str|None=None):return build_signal_fusion(chain,address,market_score,market_bias)
@app.get('/api/onchain/{chain}/token/{address}/transfers')
def token_transfer_api(chain:str,address:str,limit:int=100):return transfers(chain,address,min(max(limit,1),100))
@app.get('/api/onchain/{chain}/token/{address}/whales')
def whale_api(chain:str,address:str,limit:int=100):return whales(chain,address,min(max(limit,1),100))
@app.get('/api/onchain/{chain}/token/{address}/holders')
def holder_api(chain:str,address:str,limit:int=100):return holders_from_transfers(chain,address,min(max(limit,1),100))
@app.get('/api/onchain/{chain}/token/{address}/liquidity')
def liquidity_api(chain:str,address:str):return liquidity(chain,address)
@app.get('/api/onchain/{chain}/token/{address}/risk')
def risk_api(chain:str,address:str):return risk(chain,address)
@app.get('/api/stock/{symbol}')
def stock(symbol:str):return get_stock(symbol)
@app.get('/api/news/{symbol}')
def news(symbol:str):return get_company_news(symbol)
@app.get('/api/macro/nfp')
def nfp():return get_employment_snapshot()
@app.get('/api/history')
def history(limit:int=100):return recent(min(max(limit,1),500))
@app.get('/api/performance')
def performance():return stats()
