import requests
from ..config import OPENAI_API_KEY,OPENAI_MODEL,REQUEST_TIMEOUT

def explain(signal):
    if not OPENAI_API_KEY: return {'enabled':False,'text':'AI narrative is offline. Add OPENAI_API_KEY in Render environment variables to enable it.'}
    prompt=('You are a cautious market-research analyst. Explain the supplied signal using only the supplied data. '
            'Return a concise thesis, evidence, risks, invalidation conditions and what would change the view. '
            'Never claim certainty, guaranteed returns, or financial advice.\nDATA:\n'+str(signal))
    try:
        r=requests.post('https://api.openai.com/v1/responses',headers={'Authorization':f'Bearer {OPENAI_API_KEY}','Content-Type':'application/json'},json={'model':OPENAI_MODEL,'input':prompt,'max_output_tokens':650},timeout=REQUEST_TIMEOUT+20); r.raise_for_status(); j=r.json(); text=j.get('output_text','')
        if not text:
            for item in j.get('output',[]):
                for part in item.get('content',[]):
                    if part.get('type')=='output_text': text+=part.get('text','')
        return {'enabled':True,'text':text or 'No AI narrative returned.'}
    except Exception as e: return {'enabled':False,'text':'AI narrative unavailable; quantitative research remains available.'}
