#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REGISTRY=HERE/"resident_registry.json"
FULL=HERE.parents[1]/"protocols"/"UTM-OMEGA-FULL-SYNC-1.0.json"
AGGREGATE_ID="utm-omega-full-sync-v1.0"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def git_blob_sha(path):
    b=path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def current_components(registry):
    out=[]
    for r in registry.get("residents",[]):
        if r.get("id")==AGGREGATE_ID:
            continue
        p=ROOT/r["path"]
        out.append({
            "id":r["id"],
            "protocol":r["protocol"],
            "path":r["path"],
            "coordinate":int(r["coordinate"]),
            "source_blob_sha":git_blob_sha(p),
        })
    return sorted(out,key=lambda x:x["coordinate"])

def evaluate(registry=None,manifest=None):
    r=registry or load(REGISTRY)
    m=manifest or load(FULL)
    cur=current_components(r)
    dec=sorted(m.get("components",[]),key=lambda x:int(x["coordinate"]))
    reasons=[]
    if int(m.get("component_count",-1))!=len(cur):
        reasons.append("component_count_changed")
    if dec!=cur:
        reasons.append("component_identity_or_content_changed")
    agg=[x for x in r.get("residents",[]) if x.get("id")==AGGREGATE_ID]
    if len(agg)!=1:
        reasons.append("aggregate_resident_not_unique")
        coord=None
    else:
        coord=int(agg[0]["coordinate"])
    stage=int(r.get("stage",{}).get("stage",-1))
    fixed=not reasons
    return {
        "protocol":"UTM-Omega-Idempotent-Full-Sync/1.0",
        "status":"OMEGA_FULL_SYNC_FIXED_POINT" if fixed else "OMEGA_FULL_SYNC_ADVANCE_REQUIRED",
        "verified":fixed,
        "reasons":reasons,
        "operator":"D_omega",
        "idempotent_when_unchanged":True,
        "law":"D_omega(D_omega(S))=D_omega(S) when component identities and blob contents are unchanged",
        "stage":stage,
        "resident_count":len(r.get("residents",[])),
        "component_count":len(cur),
        "aggregate_coordinate":coord,
        "allocate_new_resident":False,
        "advance_stage":False if fixed else True,
        "next_stage_if_changed":None if fixed else stage+1,
        "actual_infinite_physical_compute":False,
        "oracle":None,
        "hypercomputation_enabled":False,
    }

if __name__=="__main__":
    x=evaluate()
    print(json.dumps(x,sort_keys=True,separators=(",",":")))
    raise SystemExit(0 if x["verified"] else 1)
