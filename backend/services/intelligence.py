import time
import requests
from ..config import ETHERSCAN_API_KEY, DEXSCREENER_BASE_URL, REQUEST_TIMEOUT

CHAIN_IDS={"ethereum":1,"base":8453,"arbitrum":42161,"optimism":10,"polygon":137,"bnb":56}

def valid(chain,address):
    if chain not in CHAIN_IDS: raise ValueError(f"Unsupported chain: {chain}")
    if not isinstance(address,str) or len(address)!=42 or not address.startswith("0x"): raise ValueError("Invalid EVM address")
    int(address[2:],16); return address

def scan_index(chain,params):
    if not ETHERSCAN_API_KEY: return {"ok":False,"configured":False,"message":"Set ETHERSCAN_API_KEY to enable indexed on-chain analytics."}
    p={"chainid":CHAIN_IDS[chain],"apikey":ETHERSCAN_API_KEY,**params}
    r=requests.get("https://api.etherscan.io/v2/api",params=p,timeout=REQUEST_TIMEOUT); r.raise_for_status(); d=r.json()
    if d.get("status")=="0" and d.get("message") not in ("No transactions found","No records found"): return {"ok":False,"configured":True,"message":d.get("result",d.get("message"))}
    return {"ok":True,"configured":True,"result":d.get("result",[])}

def transfers(chain,token,limit=100):
    token=valid(chain,token); x=scan_index(chain,{"module":"account","action":"tokentx","contractaddress":token,"page":1,"offset":min(max(limit,1),100),"sort":"desc"})
    if not x.get("ok"): return x
    out=[]
    for t in x["result"]:
        try: amount=int(t.get("value","0"))/(10**int(t.get("tokenDecimal") or 0))
        except Exception: amount=None
        out.append({"hash":t.get("hash"),"from":t.get("from"),"to":t.get("to"),"amount":amount,"symbol":t.get("tokenSymbol"),"timestamp":int(t.get("timeStamp",0)),"block":int(t.get("blockNumber",0))})
    return {"ok":True,"chain":chain,"token":token,"count":len(out),"transfers":out}

def whales(chain,token,limit=100):
    x=transfers(chain,token,limit)
    if not x.get("ok"): return x
    rows=sorted(x["transfers"],key=lambda a:float(a.get("amount") or 0),reverse=True)
    return {"ok":True,"chain":chain,"token":token,"count":len(rows),"whale_transfers":rows[:50],"note":"Ranked by token units; USD thresholds require historical price data."}

def liquidity(chain,token):
    token=valid(chain,token); r=requests.get(f"{DEXSCREENER_BASE_URL}/token-pairs/v1/{chain}/{token}",timeout=REQUEST_TIMEOUT)
    if r.status_code==404:return {"ok":True,"pairs":[]}
    r.raise_for_status(); data=r.json(); pairs=data if isinstance(data,list) else []
    rows=[]
    for p in pairs:
        rows.append({"dex":p.get("dexId"),"pair":p.get("pairAddress"),"base":p.get("baseToken",{}).get("symbol"),"quote":p.get("quoteToken",{}).get("symbol"),"price_usd":p.get("priceUsd"),"liquidity_usd":(p.get("liquidity") or {}).get("usd",0),"volume_24h_usd":(p.get("volume") or {}).get("h24",0),"url":p.get("url")})
    rows.sort(key=lambda a:float(a["liquidity_usd"] or 0),reverse=True)
    return {"ok":True,"chain":chain,"token":token,"pairs":rows[:50],"total_liquidity_usd":sum(float(a["liquidity_usd"] or 0) for a in rows)}

def risk(chain,token):
    token=valid(chain,token)
    from .onchain import _rpc
    code=_rpc(chain,"eth_getCode",[token,"latest"],ttl=30)
    if code in (None,"0x"): return {"ok":False,"message":"No contract bytecode found."}
    c=code.lower(); flags=[]
    if "f4" in c: flags.append("DELEGATECALL present; review upgrade/admin controls")
    if "ff" in c: flags.append("SELFDESTRUCT byte pattern present; manual review required")
    proxy="363d3d373d3d3d363d73" in c or "5af43d82803e903d91602b57fd5bf3" in c
    if proxy: flags.append("Proxy-style bytecode detected")
    return {"ok":True,"chain":chain,"token":token,"bytecode_bytes":max(0,(len(code)-2)//2),"proxy_detected":proxy,"flags":flags,"risk_level":"review" if flags else "no_obvious_bytecode_flags","disclaimer":"Heuristic only; not a security audit."}

def holders_from_transfers(chain,token,limit=100):
    x=transfers(chain,token,limit)
    if not x.get("ok"): return x
    b={}
    for t in x["transfers"]:
        a=(t.get("from") or "").lower(); z=(t.get("to") or "").lower(); v=float(t.get("amount") or 0)
        if a:b[a]=b.get(a,0)-v
        if z:b[z]=b.get(z,0)+v
    top=sorted(((a,v) for a,v in b.items() if v>0),key=lambda q:q[1],reverse=True)[:50]; total=sum(v for _,v in top)
    return {"ok":True,"chain":chain,"token":token,"holders_observed":len(b),"top_holders":[{"address":a,"observed_balance":v,"share_pct":v/total*100 if total else 0} for a,v in top],"warning":"Estimated from indexed transfers, not a complete holder snapshot."}

def intelligence(chain,token):
    token=valid(chain,token); tr=transfers(chain,token); out={"ok":True,"chain":chain,"token":token,"generated_at":time.time(),"transfers":tr,"whales":whales(chain,token),"holders":holders_from_transfers(chain,token),"risk":risk(chain,token)}
    try: out["liquidity"]=liquidity(chain,token)
    except Exception as e: out["liquidity"]={"ok":False,"message":str(e)}
    rows=tr.get("transfers",[]) if tr.get("ok") else []
    out["activity_summary"]={"transfer_count":len(rows),"unique_wallets":len({a for t in rows for a in (t.get("from"),t.get("to")) if a})}
    return out
