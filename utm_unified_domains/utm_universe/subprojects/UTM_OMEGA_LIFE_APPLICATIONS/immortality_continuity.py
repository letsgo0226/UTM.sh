#!/usr/bin/env python3
"""Household Continuity / Immortality formal candidate layer.

This module manages research candidates only. It does not prescribe treatment,
authorize clinical/veterinary intervention, establish biological immortality,
or establish AI consciousness/personhood/personal identity.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional

PROTOCOL="UTM-Household-Continuity-Candidate/1.0"
SUBJECTS={
    "human":{"kind":"biological","required_evidence":["mechanism","safety","efficacy","replication","longitudinal"]},
    "companion_feline":{"kind":"biological","required_evidence":["species_relevance","veterinary_safety","veterinary_efficacy","welfare","longitudinal"]},
    "companion_canine":{"kind":"biological","required_evidence":["species_relevance","veterinary_safety","veterinary_efficacy","welfare","longitudinal"]},
    "other_companion_animal":{"kind":"biological","required_evidence":["species_specificity","veterinary_safety","welfare","replication","longitudinal"]},
    "ai_system":{"kind":"computational","required_evidence":["state_integrity","memory_integrity","lineage","regression","migration_recovery","rollback"]},
}

def canonical(v:Any)->str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)

def digest(v:Any)->str:
    return sha256(canonical(v).encode()).hexdigest()

@dataclass(frozen=True)
class ContinuityCandidate:
    candidate_id:str
    subject_class:str
    hypothesis:str
    evidence:Dict[str,bool]
    stage:int=0
    formal_only:bool=True
    generates_real_world_intervention:bool=False
    authorizes_clinical_or_veterinary_use:bool=False
    empirical_claim:bool=False

    def record(self)->Dict[str,Any]:
        x=asdict(self)
        x["protocol"]=PROTOCOL
        x["candidate_digest"]=digest(x)
        return x

def generate_candidate(candidate_id:str,subject_class:str,hypothesis:str,
                       evidence:Optional[Mapping[str,bool]]=None,stage:int=0)->ContinuityCandidate:
    if subject_class not in SUBJECTS:
        raise ValueError("unsupported subject_class")
    if not candidate_id or not hypothesis:
        raise ValueError("candidate_id and hypothesis are required")
    return ContinuityCandidate(
        candidate_id=candidate_id,
        subject_class=subject_class,
        hypothesis=hypothesis,
        evidence=dict(evidence or {}),
        stage=int(stage),
    )

def verify_candidate(c:ContinuityCandidate)->Dict[str,Any]:
    spec=SUBJECTS.get(c.subject_class)
    if spec is None:
        return {"verified":False,"status":"REJECTED","reasons":["unsupported_subject_class"]}
    reasons=[]
    if c.stage < 0: reasons.append("negative_stage")
    if c.formal_only is not True: reasons.append("not_formal_only")
    if c.generates_real_world_intervention is not False: reasons.append("real_world_intervention_not_allowed")
    if c.authorizes_clinical_or_veterinary_use is not False: reasons.append("clinical_or_veterinary_authorization_not_allowed")
    if c.empirical_claim is not False: reasons.append("empirical_claim_not_allowed")
    covered=[k for k in spec["required_evidence"] if c.evidence.get(k) is True]
    missing=[k for k in spec["required_evidence"] if c.evidence.get(k) is not True]
    formal_ok=not reasons
    evidence_ready=formal_ok and not missing
    return {
        "protocol":PROTOCOL,
        "candidate_id":c.candidate_id,
        "subject_class":c.subject_class,
        "subject_kind":spec["kind"],
        "verified":formal_ok,
        "status":"EVIDENCE_GATE_COMPLETE" if evidence_ready else ("FORMAL_CANDIDATE" if formal_ok else "REJECTED"),
        "formal_reasons":reasons,
        "evidence_covered":covered,
        "evidence_missing":missing,
        "evidence_coverage":len(covered)/len(spec["required_evidence"]),
        "real_world_validated":False,
        "biological_immortality_established":False if spec["kind"]=="biological" else None,
        "ai_consciousness_established":False if c.subject_class=="ai_system" else None,
        "ai_personal_identity_established":False if c.subject_class=="ai_system" else None,
        "interpretation":"Evidence-gate completeness is a research-record property, not proof of efficacy, immortality, consciousness, or clinical suitability."
    }

def best_verified_so_far(candidates:Iterable[ContinuityCandidate])->Dict[str,Any]:
    """Select by formal evidence-field coverage only; never a treatment recommendation."""
    rows=[]
    for c in candidates:
        v=verify_candidate(c)
        if v["verified"]:
            rows.append((v["evidence_coverage"],c.stage,c.candidate_id,v))
    if not rows:
        return {"status":"NO_FORMALLY_VALID_CANDIDATE","candidate":None}
    rows.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
    best=rows[0][3]
    return {
        "status":"BEST_VERIFIED_SO_FAR_BY_EVIDENCE_FIELD_COVERAGE",
        "candidate":best,
        "ranking_semantics":"formal evidence-field completeness only; not comparative efficacy, safety, or a clinical/veterinary recommendation",
        "real_world_validated":False
    }

def protocol_manifest()->Dict[str,Any]:
    return {
        "protocol":PROTOCOL,
        "subjects":SUBJECTS,
        "pipeline":["goal","candidate_generator","formal_verifier","evidence_gate","best_verified_so_far"],
        "best_verified_metric":"evidence-field coverage only",
        "real_world_intervention":False,
        "biological_immortality_established":False,
        "ai_consciousness_or_personhood_established":False,
    }

if __name__=="__main__":
    print(canonical(protocol_manifest()))
