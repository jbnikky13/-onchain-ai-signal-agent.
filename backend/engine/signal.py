from datetime import datetime,timezone
from .technical import technical_scores
from .confluence import combine,action,label
from .projection import project

def analyze_crypto(symbol,df,horizon='swing'):
    _,tech,raw=technical_scores(df)
    scores={**tech,'onchain':55,'whales':55,'derivatives':55,'liquidity':60,'sentiment':55,'fundamentals':55,'macro':55}
    score=combine(scores); act=action(score); levels=project(df,score,horizon)
    reasons=[]
    reasons.append('Price structure is above the 20/50-period trend averages.' if tech['trend']>=78 else 'Trend structure is mixed or below key averages.')
    reasons.append('Momentum is supportive.' if tech['momentum']>=75 else 'Momentum is mixed or weak.')
    reasons.append('Volume is above its rolling baseline.' if tech['volume']>=72 else 'Volume confirmation is limited.')
    risks=['Market regime can change quickly.','Model inputs do not include every on-chain, derivatives or news source.','Projected levels are scenario estimates, not guarantees.']
    return {'symbol':symbol.upper(),'asset_type':'crypto','horizon':horizon,'action':act,'label':label(score),'score':score,'confidence':round(min(92,max(40,50+abs(score-50)*.9)),1),'data_confidence':'High' if len(df)>=150 else 'Medium','market':raw,**levels,'confluences':scores,'reasons':reasons,'risks':risks,'generated_at':datetime.now(timezone.utc).isoformat()}
