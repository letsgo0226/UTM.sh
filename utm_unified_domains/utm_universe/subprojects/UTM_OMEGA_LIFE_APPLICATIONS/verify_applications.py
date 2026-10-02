#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
FILES=[
 "IMMORTALITY_RESEARCH.json",
 "CULTURED_MEAT.json",
 "VEGETARIAN_NUTRITION.json",
 "CONTRACEPTION_ZERO_HARM.json",
 "BIRTH_ZERO_INJURY.json",
]
EXPECTED={
 "IMMORTALITY_RESEARCH","CULTURED_MEAT","VEGETARIAN_NUTRITION",
 "CONTRACEPTION_ZERO_HARM","BIRTH_ZERO_INJURY"
}

def load_all():
    return [json.loads((HERE/f).read_text(encoding="utf-8")) for f in FILES]

def verify_application(a):
    ex=a.get("execution_boundary",{})
    checks={
      "protocol":a.get("protocol")=="UTM-Omega-Application-Target/1.0",
      "scope":a.get("scope")=="formal-research-target-only",
      "target_declared":a.get("P_target_goal")==1,
      "formal_certificate":a.get("C_target")==1,
      "empirical_estimate_unset":a.get("P_empirical_hat") is None,
      "axiom_target":a.get("A_target")==1,
      "temporal_target":a.get("G_target")==1,
      "no_empirical_claim":a.get("empirical_claim") is False,
      "not_real_world_validated":a.get("real_world_validated") is False,
      "external_evidence_required":a.get("external_evidence_required") is True,
      "does_not_generate_intervention":ex.get("generates_real_world_intervention") is False,
      "does_not_authorize_clinical_use":ex.get("authorizes_clinical_use") is False,
      "medical_action_disabled":ex.get("medical_action_enabled") is False,
      "certificate_not_empirical_proof":ex.get("target_certificate_is_not_empirical_proof") is True,
      "evidence_gate_present":isinstance(a.get("evidence_gate"),list) and len(a["evidence_gate"])>0,
      "target_semantics_present":isinstance(a.get("target_semantics"),dict),
      "real_world_claim_not_established":a.get("target_semantics",{}).get("real_world_claim") not in ("ESTABLISHED","PROVEN","GUARANTEED")
    }
    if a.get("app_id")=="IMMORTALITY_RESEARCH":
        ss=a.get("subject_scope",{})
        classes={x.get("id") for x in ss.get("classes",[])}
        checks.update({
          "household_scope_inclusive":ss.get("inclusive") is True,
          "human_scope_present":"human" in classes,
          "feline_scope_present":"companion_feline" in classes,
          "canine_scope_present":"companion_canine" in classes,
          "other_companion_scope_present":"other_companion_animal" in classes,
          "ai_scope_present":"ai_system" in classes,
          "ai_consciousness_claim_disabled":ex.get("ai_consciousness_claim_enabled") is False,
          "ai_personhood_claim_disabled":ex.get("ai_personhood_claim_enabled") is False,
          "biological_immortality_claim_disabled":ex.get("biological_immortality_claim_enabled") is False,
          "subject_evidence_gates_present":isinstance(a.get("evidence_gate_by_subject"),dict) and len(a["evidence_gate_by_subject"])==5,
        })
    return {"app_id":a.get("app_id"),"verified":all(checks.values()),"checks":checks}

def verify_bundle():
    apps=load_all()
    results=[verify_application(a) for a in apps]
    ids={a.get("app_id") for a in apps}
    ok=(ids==EXPECTED and all(r["verified"] for r in results))
    return {
      "protocol":"UTM-Omega-Life-Applications/1.0",
      "status":"OMEGA_ADMITTED" if ok else "REJECTED",
      "verified":ok,
      "application_count":len(apps),
      "application_ids":sorted(ids),
      "results":results,
      "P_target_goal":1,
      "C_target":1 if ok else 0,
      "P_empirical_hat":None,
      "real_world_validated":False,
      "actual_infinite_physical_compute":False,
      "interpretation":"Certificate covers formal target specifications only; it is not evidence that the corresponding real-world technology exists or is clinically/industrially effective."
    }

if __name__=="__main__":
    print(json.dumps(verify_bundle(),ensure_ascii=False,sort_keys=True,separators=(",",":")))
