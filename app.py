from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Any

app=FastAPI(title='UTM Three-System Zero-Point Kernel',version='1.0.0')

class Req(BaseModel):
    candidates:list[dict[str,Any]]

def ok(x,ks): return all(bool(x.get(k,False)) for k in ks)

def solve(xs,req,cost):
    A=[x for x in xs if ok(x,req)]
    if not A: raise HTTPException(422,'NO_ADMISSIBLE_STATE')
    R=[(x,float(cost(x))) for x in A]; z=min(v for _,v in R)
    out=[{'id':x.get('id','?'),'raw_cost':v,'zero_cost':v-z,'candidate':x} for x,v in R]
    out.sort(key=lambda r:r['raw_cost'])
    return {'minimum_raw_cost':z,'zero_ids':[r['id'] for r in out if abs(r['zero_cost'])<1e-12],'admissible_count':len(out),'results':out}

D={
'utm':(['consistent','provenance','replayable','admissible'],lambda x:float(x.get('contradiction',0))+float(x.get('incomplete',0))+float(x.get('distance',0))+float(x.get('derivation_cost',0))),
'trader42':(['risk_safe','capital_safe','execution_valid','auditable'],lambda x:-float(x.get('expected_utility',0))+float(x.get('risk',0))+float(x.get('cost',0))+float(x.get('uncertainty',0))),
'omega':(['consistent','provenance','replayable','protocol_valid'],lambda x:float(x.get('contradiction',0))+float(x.get('missing_provenance',0))+float(x.get('distance',0)))
}

@app.get('/health')
def health(): return {'ok':True,'domains':list(D),'principle':'Invariant -> Admissible -> argmin(J) -> J0=0'}

@app.get('/schema/{domain}')
def schema(domain:str):
    if domain not in D: raise HTTPException(404,'unknown domain')
    return {'domain':domain,'required':D[domain][0]}

@app.post('/solve/{domain}')
def run(domain:str,r:Req):
    if domain not in D: raise HTTPException(404,'unknown domain')
    req,cost=D[domain]; return solve(r.candidates,req,cost)
