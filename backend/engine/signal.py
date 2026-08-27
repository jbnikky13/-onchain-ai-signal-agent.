from datetime import datetime,timezone
from .technical import technical_scores
from .confluence import combine,action
from .projection import project
def analyze_crypto(symbol,df,horizon="swing"):
    _,tech=technical_scores(df)
    scores={**tech,"onchain":55,"whales":55,"derivatives":55,"liquidity":60,"sentiment":55,"fundamentals":55,"macro":55}
    score=combine(scores); act=action(score); levels=project(df,score,horizon)
    reasons=["Price is above the main trend averages." if tech["trend"]>=80 else "Trend structure is mixed or bearish."]
    if tech["momentum"]>=80: reasons.append("Momentum indicators are aligned positively.")
    elif tech["momentum"]<50: reasons.append("Momentum is weak.")
    if tech["volume"]>=75: reasons.append("Recent volume is above its rolling baseline.")
    if act=="NO SIGNAL": reasons.append("Evidence is mixed; the model does not force a directional call.")
    return {"symbol":symbol,"asset_type":"crypto","horizon":horizon,"action":act,"score":score,"confidence":round(min(95,max(35,score if act!="NO SIGNAL" else 55)),1),
            **levels,"confluences":scores,"reasons":reasons,"risks":["Market regime can change quickly.","Projected levels are estimates, not guarantees.","Major news can invalidate a setup."],
            "generated_at":datetime.now(timezone.utc).isoformat(),"data_confidence":"Medium"}

