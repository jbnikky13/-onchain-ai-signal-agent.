import requests
from datetime import date
from ..config import REQUEST_TIMEOUT

def get_employment_snapshot():
    y=date.today().year; payload={'seriesid':['CES0000000001','LNS14000000','CES0500000003'],'startyear':str(y-2),'endyear':str(y)}
    try:
        r=requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/',json=payload,timeout=REQUEST_TIMEOUT); r.raise_for_status(); data=r.json().get('Results',{}).get('series',[])
        return {'available':True,'series':data,'source':'U.S. Bureau of Labor Statistics','updated_at':date.today().isoformat()}
    except Exception as e: return {'available':False,'series':[],'error':'Macro data temporarily unavailable.'}
