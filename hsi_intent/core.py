from __future__ import annotations
import hashlib, json
from pathlib import Path

PROTOCOL="HSI-INTENT/1.0"
TYPES={"GOAL","INVARIANT","CONSTRAINT","HYPOTHESIS","CLAIM_BOUNDARY","DESIGN","STATE","DEPRECATED"}
STATUSES={"ACTIVE","HYPOTHESIS","LIMITED","DEPRECATED","REJECTED","SUPERSEDED"}

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def digest(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()

def load_registry(path=None):
    p=Path(path or Path(__file__).with_name("registry.json"))
    return json.loads(p.read_text(encoding="utf-8"))

def validate_registry(registry):
    if registry.get("protocol")!=PROTOCOL:
        return {"valid":False,"errors":["protocol"]}
    atoms=registry.get("atoms")
    if not isinstance(atoms,list):
        return {"valid":False,"errors":["atoms"]}
    ids=set(); errors=[]
    for i,a in enumerate(atoms):
        if not isinstance(a,dict):
            errors.append(f"atom[{i}]"); continue
        aid=str(a.get("id",""))
        if not aid or aid in ids: errors.append(f"id:{aid or i}")
        ids.add(aid)
        if a.get("type") not in TYPES: errors.append(f"type:{aid}")
        if a.get("status") not in STATUSES: errors.append(f"status:{aid}")
        if not isinstance(a.get("hard"),bool): errors.append(f"hard:{aid}")
        if int(a.get("priority",0)) not in {1,2,3}: errors.append(f"priority:{aid}")
        if not str(a.get("statement","")).strip(): errors.append(f"statement:{aid}")
    for a in atoms:
        for dep in a.get("dependencies",[]):
            if dep not in ids: errors.append(f"dependency:{a.get('id')}->{dep}")
    return {"valid":not errors,"errors":errors,"atom_count":len(atoms),"registry_digest":digest(registry)}

def certify_transition(registry, transition):
    v=validate_registry(registry)
    if not v["valid"]:
        return {"protocol":PROTOCOL,"closed":0,"reason":"invalid registry","errors":v["errors"]}
    by_id={a["id"]:a for a in registry["atoms"]}
    fields=("advanced","preserved","deferred","violated","resolved")
    sets={k:list(dict.fromkeys(transition.get(k,[]) or [])) for k in fields}
    referenced=set(sum((sets[k] for k in fields),[]))
    unknown=sorted(referenced-set(by_id))
    hard_violations=sorted(i for i in sets["violated"] if i in by_id and by_id[i].get("hard") and by_id[i].get("status")=="ACTIVE")
    invalid_resolutions=sorted(i for i in sets["resolved"] if i in by_id and by_id[i].get("status")=="ACTIVE" and by_id[i].get("hard"))
    priority=lambda i:int(by_id[i].get("priority",1)) if i in by_id else 0
    goal_delta=sum(priority(i) for i in sets["advanced"])-sum(priority(i) for i in sets["violated"])
    closed=not unknown and not hard_violations and not invalid_resolutions
    body={
        "registry_digest":v["registry_digest"],
        "transition":transition,
        "advanced":sets["advanced"],"preserved":sets["preserved"],
        "deferred":sets["deferred"],"violated":sets["violated"],"resolved":sets["resolved"]
    }
    return {
        "protocol":PROTOCOL,
        "registry_digest":v["registry_digest"],
        "transition_uid":digest(body),
        "goal_delta":goal_delta,
        "goals_advanced":sets["advanced"],
        "goals_preserved":sets["preserved"],
        "goals_deferred":sets["deferred"],
        "goals_violated":sets["violated"],
        "goals_resolved":sets["resolved"],
        "unknown_atoms":unknown,
        "hard_violations":hard_violations,
        "invalid_resolutions":invalid_resolutions,
        "closed":int(closed),
        "scope":"goal-preservation certificate only; no empirical, predictive or external-action authority"
    }
