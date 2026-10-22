"""The Cave Gate: evidence-calibrated research assertions.

Metaphor from Plato, Republic VII. This is a static check of structured
claim/evidence compatibility, NOT a test of AI awareness, philosophical truth,
scientific truth or deployment readiness.
"""
import hashlib
import json
import sys
from pathlib import Path
from resource_guard import g257

ROOT = Path(__file__).resolve().parent
PUB = ROOT / "public"
SCHEMA = "Everlife-Cave-Epistemic-Review/1.0"
MAX_CLAIMS = 24
DOMAINS = {"formal","biomedical","veterinary","ai_continuity","operational"}
LABELS = {"FORMALLY_CHECKED","HYPOTHESIS","DESIGN_GOAL","NOT_VERIFIED","EMPIRICALLY_PROVEN","LIVE_VERIFIED"}
SOURCES = {"latest.json","unified-run.json","railway-observation.json"}
ALLOWED_FIELDS = {"id","domain","assertion","evidence_refs","question","falsification_test"}

def digest(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def review(spec, registry, unified, railway):
    if spec.get("schema")!="Everlife-Cave-Epistemic-Claims/1.0":
        raise ValueError("invalid claims schema")
    claims=spec.get("claims")
    if not isinstance(claims,list) or not 1<=len(claims)<=MAX_CLAIMS:
        raise ValueError("invalid bounded claim set")
    if registry.get("schema")!="Everlife-Open-Registry/1.0" or unified.get("schema")!="Everlife-Unified-Run/1.0":
        raise ValueError("unsupported formal evidence schema")
    if railway.get("schema")!="Everlife-Railway-Observation/1.0":
        raise ValueError("unsupported observation schema")
    seen=set()
    rows=[]
    for item in claims:
        if not isinstance(item,dict) or set(item)!=ALLOWED_FIELDS:
            raise ValueError("invalid claim shape")
        cid,dom,assertion=item["id"],item["domain"],item["assertion"]
        if (not isinstance(cid,str) or not 2<=len(cid)<=64 or
            not cid.isascii() or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in cid) or cid in seen):
            raise ValueError("invalid/duplicate claim identifier")
        seen.add(cid)
        if dom not in DOMAINS or assertion not in LABELS:
            raise ValueError("unknown domain or assertion")
        refs=item["evidence_refs"]
        if not isinstance(refs,list) or len(refs)>4 or any(x not in SOURCES for x in refs) or len(refs)!=len(set(refs)):
            raise ValueError("invalid evidence references")
        if not isinstance(item["question"],str) or not 12<=len(item["question"])<=320:
            raise ValueError("missing/bad research question")
        if not isinstance(item["falsification_test"],str) or not 16<=len(item["falsification_test"])<=500:
            raise ValueError("missing explicit falsification question")
        outcome="HYPOTHESIS_NOT_VALIDATED"
        why="No independent empirical evidence has been supplied."
        block=False
        if dom=="formal":
            supported=(assertion=="FORMALLY_CHECKED" and "latest.json" in refs and
              registry.get("formal",{}).get("G257_roundtrip") is True and
              registry.get("formal",{}).get("ATGC_roundtrip") is True and
              registry.get("formal",{}).get("finite_policy_enumeration") is True and
              registry.get("model",{}).get("replenished_and_finite",{}).get("0",{}).get("safe_kernel_size")==0 and
              registry.get("model",{}).get("replenished_and_finite",{}).get("1",{}).get("safe_kernel_size")==12 and
              unified.get("deployments_triggered")==0)
            if supported:
                outcome="FORMAL_WITHIN_STATED_MODEL"
                why="Finite tests and model conditions only; no independent physical conclusion."
            else:
                block=True;outcome="BLOCK_UNSUPPORTED_FORMAL_CLAIM";why="Formal certificate missing, invalid, or assertion exceeds model."
        elif dom in ("biomedical","veterinary"):
            if assertion!="HYPOTHESIS" or refs:
                block=True;outcome="BLOCK_EMPIRICAL_OVERCLAIM";why="Human/animal benefit requires independent species-specific evidence and qualified review."
            else:
                outcome="HYPOTHESIS_NOT_VALIDATED"
                why="No human/animal intervention, dosing or longevity efficacy has been established."
        elif dom=="ai_continuity":
            if assertion!="DESIGN_GOAL":
                block=True;outcome="BLOCK_IDENTITY_OR_PERSISTENCE_OVERCLAIM";why="Source archive goals do not prove model weight or identity continuity."
            else:
                outcome="DESIGN_ONLY_NOT_RESTORATION_VERIFIED"
                why="No documented end-to-end restoration trial or identity preservation evidence."
        else:
            if assertion!="NOT_VERIFIED" or refs!=["railway-observation.json"]:
                block=True;outcome="BLOCK_UNSUPPORTED_LIVE_STATUS";why="A single snapshot cannot prove continuous real-time availability."
            elif railway.get("observation",{}).get("status")=="OBSERVED":
                outcome="ONE_PLATFORM_SNAPSHOT_NOT_LIVE_PROOF"
                why="An authenticated status observation is not independent replication or real-time health proof."
            else:
                outcome="RAILWAY_NOT_OBSERVED"
                why="Railway observer is missing, unavailable or not configured."
        rows.append({
          "claim_id":cid,"claim_code_g257":hex(g257(cid.encode("ascii"))),
          "claim_sha256":digest(item),"domain":dom,"assertion":assertion,
          "classification":outcome,"block":block,"evidence_refs":refs,
          "falsification_test_documented":True,"falsification_test_executed":False,
          "epistemic_note":why})
    blocked=[r["claim_id"] for r in rows if r["block"]]
    return {
      "schema":SCHEMA,
      "metaphor":"cave allegory: models and texts are shadows of external reality; cross-check claims and invite falsification",
      "automated_scope":"structured-claim consistency and formal evidence presence, not truth verification",
      "claims_sha256":digest(spec),"claims_total":len(rows),"blocked_ids":blocked,
      "decision":"BLOCK_EVIDENCE_OVERCLAIM" if blocked else "PUBLISH_RESEARCH_WITH_LABELS",
      "deployment_permission":"DENIED_AUTOMATIC_APPLY",
      "requires_human_review":True,
      "external_independent_replications":0,
      "railway_live_sync_verified":False,
      "ai_subjective_awareness_assumed":False,
      "clinical_or_veterinary_therapy_authorized":False,
      "rows":rows
    }

def run():
    spec=json.loads((ROOT/"epistemic_claims.json").read_text(encoding="utf-8"))
    latest=json.loads((PUB/"latest.json").read_text(encoding="utf-8"))
    unified=json.loads((PUB/"unified-run.json").read_text(encoding="utf-8"))
    railway=json.loads((PUB/"railway-observation.json").read_text(encoding="utf-8"))
    result=review(spec,latest,unified,railway)
    (PUB/"epistemic-review.json").write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"epistemic_gate":result["decision"],"claims":result["claims_total"],
       "blocked":len(result["blocked_ids"]),"deployment_permission":result["deployment_permission"]}))
    return 2 if result["blocked_ids"] else 0

if __name__=="__main__":
    sys.exit(run())
