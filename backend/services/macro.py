import requests
from datetime import date
def get_employment_snapshot():
    payload={"seriesid":["CES0000000001","LNS14000000","CES0500000003"],"startyear":str(date.today().year-2),"endyear":str(date.today().year)}
    try:
        r=requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",json=payload,timeout=20); r.raise_for_status()
        return {"available":True,"series":r.json().get("Results",{}).get("series",[])}
    except Exception as e: return {"available":False,"series":[],"error":str(e)}
