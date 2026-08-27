import requests
from ..config import ALPHA_VANTAGE_API_KEY
def get_stock(symbol):
    if not ALPHA_VANTAGE_API_KEY: return {"symbol":symbol.upper(),"available":False,"message":"Set ALPHA_VANTAGE_API_KEY to enable live stock data."}
    r=requests.get("https://www.alphavantage.co/query",params={"function":"TIME_SERIES_DAILY","symbol":symbol.upper(),"outputsize":"compact","apikey":ALPHA_VANTAGE_API_KEY},timeout=20); r.raise_for_status()
    return {"symbol":symbol.upper(),"available":True,"data":r.json()}
