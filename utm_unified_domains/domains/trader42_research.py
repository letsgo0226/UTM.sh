from __future__ import annotations
import csv,json,math,os
from decimal import Decimal
from pathlib import Path
D=Decimal
MODEL='TRADER_42_UNIFIED_RESEARCH_V1'
DATA=Path(os.getenv('CANDLE_CSV',os.getenv('CANDLE_DATASET_PATH','./trader42-candles.csv')))
FAST=int(os.getenv('FAST_WINDOW','5'));SLOW=int(os.getenv('SLOW_WINDOW','20'))
FEE=D(os.getenv('MODEL_FEE_BPS','10'))/10000;SLIP=D(os.getenv('MODEL_SLIPPAGE_BPS','10'))/10000;MARGIN=D(os.getenv('EMPIRICAL_MIN_EDGE_BPS','5'))

def prices():
    if os.getenv('TRADER42_TEST_PRICES'):return [D(x) for x in os.environ['TRADER42_TEST_PRICES'].split(',') if x]
    if not DATA.exists():return []
    with DATA.open(newline='') as f:rows=list(csv.DictReader(f))
    key='close' if rows and 'close' in rows[0] else 'price'
    return [D(r[key]) for r in rows]

def req():return (((1+SLIP)/((1-SLIP)*(1-FEE)**2))-1)*10000+MARGIN

def sim(xs,fast,slow):
    cash=D(1000);base=D(0);fills=0;peak=D(1000);mdd=D(0);real=D(0);cost=D(0)
    for i,p in enumerate(xs):
        if i+1<slow:continue
        f=sum(xs[i-fast+1:i+1],D(0))/fast;s=sum(xs[i-slow+1:i+1],D(0))/slow;sig=1 if f>s else -1 if f<s else 0
        if base==0 and sig>0 and (f/s-1)*10000>=req() and cash>=10:
            spend=D(10);px=p*(1+SLIP);base=(spend/px)*(1-FEE);cash-=spend;cost=spend;fills+=1
        elif base>0 and sig<0:
            px=p*(1-SLIP);net=base*px*(1-FEE);real+=net-cost;cash+=net;base=D(0);cost=D(0);fills+=1
        eq=cash+base*p*(1-SLIP)*(1-FEE);peak=max(peak,eq);mdd=min(mdd,(eq/peak-1)*100)
    if xs:
        p=xs[-1];eq=cash+base*p*(1-SLIP)*(1-FEE)
    else:eq=cash
    return {'equity':eq,'return_pct':(eq/D(1000)-1)*100,'realized_pnl':real,'max_drawdown_pct':mdd,'fills':fills}

def oos(xs):
    train=int(os.getenv('OOS_TRAIN_CANDLES','1440'));test=int(os.getenv('OOS_TEST_CANDLES','360'));minimum=int(os.getenv('OOS_MIN_FOLDS','3'));pairs=[]
    for t in os.getenv('OOS_CANDIDATES','3:12,5:20,8:30,10:40').split(','):
        try:pairs.append(tuple(map(int,t.split(':'))))
        except:pass
    folds=[];k=0
    while pairs and k+train+test<=len(xs):
        tr=xs[k:k+train];te=xs[k+train:k+train+test];best=max(pairs,key=lambda p:sim(tr,*p)['equity']);r=sim(te,*best);folds.append({'fast':best[0],'slow':best[1],'positive':r['return_pct']>0,'return_pct':format(r['return_pct'],'.6f')});k+=test
    pos=sum(x['positive'] for x in folds);ratio=D(pos)/len(folds) if folds else None
    return {'fold_count':len(folds),'positive_oos_folds':pos,'P_real_profit_hat':format(ratio,'.6f') if ratio is not None and len(folds)>=minimum else None,'provisional_positive_fold_ratio':format(ratio,'.6f') if ratio is not None else None,'minimum_folds':minimum}

def main():
    xs=prices();r=sim(xs,FAST,SLOW);w=oos(xs);g=math.prod((2,3,5)[i]**v for i,v in enumerate((r['fills'],len(xs),w['fold_count'])));out={'model':MODEL,'mode':'research-paper-only','observations':len(xs),'FAST':FAST,'SLOW':SLOW,'required_edge_bps':format(req(),'.6f'),'metrics':{k:(format(v,'.6f') if isinstance(v,D) else v) for k,v in r.items()},'G':str(g),'CG':True,'P_target_profit':'1.000000','C_profit':int(r['return_pct']>0),'P_real_profit_hat':w['P_real_profit_hat'],'oos':w,'A_target':1,'G_target':1,'temporal_formula':'G(PROFIT_IS_OBJECTIVE)','scope':'offline/local paper research only; no exchange order path; future profit is not guaranteed'};print(json.dumps(out,separators=(',',':')))
if __name__=='__main__':main()
