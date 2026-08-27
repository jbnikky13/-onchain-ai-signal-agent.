import requests
from datetime import date,timedelta
from ..config import FINNHUB_API_KEY
def get_company_news(symbol):
    if not FINNHUB_API_KEY: return {"available":False,"items":[]}
    e=date.today(); s=e-timedelta(days=7)
    r=requests.get("https://finnhub.io/api/v1/company-news",params={"symbol":symbol.upper(),"from":s.isoformat(),"to":e.isoformat(),"token":FINNHUB_API_KEY},timeout=20); r.raise_for_status()
    return {"available":True,"items":r.json()[:20]}
