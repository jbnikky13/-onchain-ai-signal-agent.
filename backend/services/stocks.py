import requests
from datetime import date,timedelta
from ..config import ALPHA_VANTAGE_API_KEY,REQUEST_TIMEOUT

def get_stock(symbol):
    symbol=symbol.upper().strip()
    if not ALPHA_VANTAGE_API_KEY: return {'symbol':symbol,'available':False,'message':'Live stock data is disabled. Add ALPHA_VANTAGE_API_KEY in Render.'}
    r=requests.get('https://www.alphavantage.co/query',params={'function':'TIME_SERIES_DAILY','symbol':symbol,'outputsize':'compact','apikey':ALPHA_VANTAGE_API_KEY},timeout=REQUEST_TIMEOUT); r.raise_for_status(); j=r.json(); series=j.get('Time Series (Daily)',{})
    latest=next(iter(series),None); values=series.get(latest,{}) if latest else {}
    return {'symbol':symbol,'available':bool(series),'latest_date':latest,'latest':values,'data':series,'note':j.get('Note') or j.get('Information')}
