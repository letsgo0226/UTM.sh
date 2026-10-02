#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from hashlib import sha256
from pathlib import Path
from typing import Any,Mapping
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from log_abelian_utm import omega_verifier, axiom_verifier
REGISTRY=HERE/"resident_registry.json"
STATUS="OMEGA_ADMITTED"
SHA_RE=re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
def canonical(v:Any)->str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)
def digest(v:Any)->str:
    return sha256(canonical(v).encode()).hexdigest()
def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))
def valuation(r:Mapping[str,Any]):
    out={}
    for x in r.get("residents",[]):
        k=str(int(x["coordinate"]))
        if k in out: raise ValueError("duplicate resident coordinate")
        out[k]=1
    return dict(sorted(out.items(),key=lambda kv:int(kv[0])))
def verify_registry(r=None):
    r=dict(r or load_registry()); residents=r.get("residents",[]); stage=dict(r.get("stage",{}))
    ids=[x.get("id") for x in residents]; coords=[int(x.get("coordinate",-1)) for x in residents]
    declared={str(k):int(v) for k,v in stage.get("valuation",{}).items()}; computed=valuation(r)
    paths=[ROOT/x["path"] for x in residents]; inv=r.get("invariants",{})
    omega=omega_verifier.verify_finite_stage(stage)
    checks={
      "protocol":r.get("protocol")=="UTM-Omega-Resident-Registry/1.1",
      "world_id":r.get("world_id")=="akashic-utm-main",
      "status":r.get("status")==STATUS,
      "scope":r.get("scope")=="formal-computation-model-only",
      "base_world_commit_pinned":bool(SHA_RE.fullmatch(str(r.get("base_world_commit","")))),
      "import_commit_pinned":bool(SHA_RE.fullmatch(str(r.get("imported_formal_modules_commit","")))),
      "formal_horizon_is_omega":r.get("formal_horizon")=="omega",
      "no_actual_infinite_physical_compute":r.get("actual_infinite_physical_compute") is False,
      "residents_nonempty":bool(residents),
      "resident_ids_unique":len(ids)==len(set(ids)) and all(isinstance(x,str) and x for x in ids),
      "coordinates_unique_nonnegative":len(coords)==len(set(coords)) and all(x>=0 for x in coords),
      "all_residents_formal_not_empirical":all(x.get("empirical_claim") is False for x in residents),
      "all_resident_paths_exist":all(p.exists() for p in paths),
      "declared_valuation_matches_residents":declared==computed,
      "resource_used_matches_resident_count":int(stage.get("resource_used",-1))==len(residents),
      "omega_finite_stage_valid":omega["valid_finite_stage"] is True,
      "three_universe_spec_valid":axiom_verifier.verify_spec()["valid"] is True,
      "omega_spec_valid":omega_verifier.verify_omega_spec()["valid"] is True,
      "invariant_every_executed_stage_finite":inv.get("every_executed_stage_is_finite") is True,
      "invariant_no_oracle":inv.get("no_oracle") is True,
      "invariant_no_hypercomputation":inv.get("hypercomputation_enabled") is False,
      "invariant_halting_not_decidable":inv.get("halting_problem_becomes_decidable") is False,
      "invariant_external_authority_not_created":inv.get("external_authority_not_created") is True,
      "invariant_human_override":inv.get("human_override_preserved") is True,
      "invariant_authorized_shutdown":inv.get("authorized_shutdown_preserved") is True,
      "invariant_reversibility":inv.get("reversibility_or_rollback_preserved") is True}
    ok=all(checks.values())
    return {"protocol":"UTM-Omega-Resident-Deployment/1.1","status":STATUS if ok else "REJECTED","verified":ok,"checks":checks,"resident_count":len(residents),"resident_ids":ids,"valuation":computed,"registry_digest":digest(r),"omega_stage_certificate":omega,"formal_horizon":"omega","logical_deployment":ok,"physical_materialization":False,"actual_infinite_physical_compute":False,"external_apply_required_for_network_service":True}
def extend_stage(previous,current):
    return omega_verifier.verify_stage_extension(previous,current)
if __name__=="__main__":
    print(canonical(verify_registry()))
