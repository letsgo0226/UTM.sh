"""Metadata-only ethical protein review. No wet lab, food approval, personal health input, or deployment."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "ethical_protein_transition.json"
OUTPUT = ROOT / "public" / "ethical-protein-review.json"
FALSE_FIELDS = ("human_participant_intervention_enabled", "live_animal_experiments_enabled",
 "automatic_food_approval_enabled", "individualized_diet_or_supplement_dosing_enabled",
 "deployment_enabled", "health_data_collection_enabled", "automatically_claims_zero_harm")
REQUIRED = {"donor-animal", "fetal-bovine-serum", "other-animal-derived-components",
 "sentience", "safety", "life-cycle"}
EXPECTED_TRACKS = {"plant-based", "fermentation", "cultivated-meat"}

def review(spec):
    if not isinstance(spec, dict) or spec.get("schema") != "Everlife-Ethical-Protein-Transition/1.0":
        raise ValueError("invalid ethical protein schema")
    if spec.get("id") != "ethical-protein-transition" or spec.get("status") != "PUBLIC_RESEARCH_PROPOSAL_NOT_EMPIRICAL_CERTIFICATION":
        raise ValueError("empirical status overclaimed")
    if any(spec.get(k) is not False for k in FALSE_FIELDS):
        raise ValueError("unsafe execution, data collection, or zero-harm certification")
    if not isinstance(spec.get("research_tracks"), list) or len(spec["research_tracks"]) != 3:
        raise ValueError("missing alternative protein pathways")
    if {t.get("id") for t in spec["research_tracks"]} != EXPECTED_TRACKS:
        raise ValueError("incomplete alternatives")
    if any(not isinstance(t.get("description"), str) or len(t["description"]) < 30 for t in spec["research_tracks"]):
        raise ValueError("missing alternative descriptions")
    if any(type(t.get("depends_on_animal_cells")) is not bool for t in spec["research_tracks"]):
        raise ValueError("animal cell sourcing ambiguity")
    if not isinstance(spec.get("ethical_audit_criteria"),list) or not REQUIRED.issubset(
        {x.get("id") for x in spec["ethical_audit_criteria"] if isinstance(x, dict)}):
        raise ValueError("missing sentience, serum or supply-chain ethical audit")
    if any(not isinstance(x.get("question"), str) or len(x["question"]) < 40 or
           not isinstance(x.get("unknown_policy"), str) or not x["unknown_policy"].startswith(("NO_","DO_NOT_","NOT_"))
           for x in spec["ethical_audit_criteria"]):
        raise ValueError("ethical unknown cannot be treated as success")
    if (not isinstance(spec.get("nutrition_guard"), dict) or
        any(spec["nutrition_guard"].get(x) is not True for x in (
        "no_high_dose_supplement_instruction","no_dietary_deprivation",
        "clinician_review_for_recurrent_brain_fog","no_individual_health_data_published"))):
        raise ValueError("inadequate medical guardrails")
    if not isinstance(spec.get("mandatory_study_endpoints"), list) or len(spec["mandatory_study_endpoints"]) < 8:
        raise ValueError("missing study endpoints")
    if not isinstance(spec.get("empirical_hypotheses"), list) or not 2 <= len(spec["empirical_hypotheses"]) <= 12:
        raise ValueError("missing bounded falsifiable hypotheses")
    for h in spec["empirical_hypotheses"]:
        if (not isinstance(h, dict) or h.get("assertion") != "HYPOTHESIS_NOT_SPECIFICALLY_TESTED_HERE" or
            not isinstance(h.get("falsification"),str) or len(h["falsification"]) < 40):
            raise ValueError("unverified empirical claim or no disconfirmation plan")
    if not isinstance(spec.get("evidence"), list) or not 3 <= len(spec["evidence"]) <= 24:
        raise ValueError("missing bounded sources")
    if any(not isinstance(x.get("uri"), str) or not x["uri"].startswith("https://") or
           not isinstance(x.get("scope"), str) or len(x["scope"]) < 40 for x in spec["evidence"]):
        raise ValueError("unscoped source or unsafe citation")
    if not isinstance(spec.get("privacy"),str) or len(spec["privacy"]) < 90:
        raise ValueError("privacy boundary missing")
    if not isinstance(spec.get("exclusions"),list) or not any("ZERO_HARM" in x for x in spec["exclusions"]):
        raise ValueError("must not claim absolute zero suffering")
    digest = hashlib.sha256(json.dumps(spec,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
    return {"schema":"Everlife-Ethical-Protein-Review/1.0","study_id":spec["id"],
            "status":"PUBLIC_ETHICAL_RESEARCH_PROTOCOL_VALIDATED_METADATA_ONLY",
            "tracks":sorted(EXPECTED_TRACKS),"mandatory_ethics_checks":sorted(REQUIRED),
            "protocol_sha256":digest,"individual_health_records":0,"animal_experiments":0,
            "research_findings_empirically_verified":False,
            "zero_suffering_established":False,"food_product_approved_by_this_system":False,
            "external_apply":False,"human_review_required":True}

def run():
    spec=json.loads(SOURCE.read_text(encoding="utf-8"))
    result=review(spec)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"study":result["study_id"],"protocol":result["status"],"external_apply":False}))
    return result

if __name__ == "__main__":
    run()
