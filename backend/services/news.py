import requests
from datetime import date,timedelta
from ..config import FINNHUB_API_KEY,REQUEST_TIMEOUT

def get_company_news(symbol):
    if not FINNHUB_API_KEY: return {'available':False,'items':[],'message':'Add FINNHUB_API_KEY to enable company news.'}
    end=date.today(); start=end-timedelta(days=14)
    r=requests.get('https://finnhub.io/api/v1/company-news',params={'symbol':symbol.upper(),'from':start.isoformat(),'to':end.isoformat(),'token':FINNHUB_API_KEY},timeout=REQUEST_TIMEOUT); r.raise_for_status()
    items=r.json()[:30]; return {'available':True,'items':items}
