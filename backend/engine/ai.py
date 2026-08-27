import requests
from ..config import OPENAI_API_KEY,OPENAI_MODEL
def explain(signal):
    if not OPENAI_API_KEY: return {"enabled":False,"text":"AI explanation disabled. Add OPENAI_API_KEY to enable it."}
    prompt=f"Explain this market-research signal cautiously. Do not invent data or present certainty. Include thesis, supporting factors, risks, invalidation idea and DYOR reminder. Signal: {signal}"
    try:
        r=requests.post("https://api.openai.com/v1/responses",headers={"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},json={"model":OPENAI_MODEL,"input":prompt,"max_output_tokens":500},timeout=45); r.raise_for_status()
        j=r.json(); return {"enabled":True,"text":j.get("output_text","AI explanation returned no text.")}
    except Exception as e: return {"enabled":False,"text":f"AI explanation unavailable: {e}"}

