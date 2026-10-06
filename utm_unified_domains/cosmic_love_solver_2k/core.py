import json,functools

PROTOCOL="Cosmic-Love-Solver/1.1-noSHA"
KERNEL=("truth","agency","harm","repair","future","feasible")
OBJECTIVE=(("cost",1),("complexity",1),("risk",2),("irreversibility",2))

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def godel_encode(s):
    return functools.reduce(lambda n,b:n*257+b+1,s.encode("utf-8"),1)

def residual(c):
    return max(abs(float(c.get(k,1))) for k in KERNEL)

def score(c):
    return sum(float(c.get(k,0))*w for k,w in OBJECTIVE)

def manifest():
    return {
        "protocol":PROTOCOL,
        "kernel":list(KERNEL),
        "objective":[k for k,_ in OBJECTIVE],
        "integrity":{"sha":False,"encoding":"reversible-base-257"},
        "claims":{"solves_all_problems":False,"oracle":False,"guaranteed_real_world_success":False}
    }

def solve(d):
    candidates=d.get("candidates",[])
    admissible=[c for c in candidates if residual(c)==0]
    best=min(admissible,key=score) if admissible else None
    out={
        "protocol":PROTOCOL,
        "status":"SOLVED" if best is not None else "NO_CERTIFIED_ZERO",
        "solution":best,
        "admissible_count":len(admissible),
        "checked":len(candidates),
        "semantics":"finite candidates; zero residual = certified in-model admissibility, not universal truth",
        "godel_scope":"canonical result excluding godel field"
    }
    out["godel"]=godel_encode(canonical(out))
    return out
