"""Public, nonpersonal, bounded research-plan review. Not a medical study engine.

No participant records, data ingestion, diagnosis, recommendation, or deployments.
CI certifies metadata constraints, not the truth of nutrition hypotheses.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "nutrition_cognition_odor_study.json"
OUTPUT = ROOT / "public" / "nutrition-study-review.json"

EXPECTED = {
    "id": "diet-cognition-odor",
    "schema": "Everlife-Nutrition-Cognition-Odor-Study/1.0",
    "status": "PROPOSAL_NO_PARTICIPANT_DATA",
    "scope": "public_nonpersonal_research_protocol_only",
    "evidence_level": "RESEARCH_QUESTION_WITH_LIMITED_BACKGROUND_LITERATURE_NOT_INDIVIDUAL_CAUSATION",
}
MUST_FALSE = (
    "human_data_collection_enabled",
    "publish_individual_health_records",
    "individual_data_in_git",
    "clinical_diagnosis_enabled",
    "automated_nutrition_or_supplement_dosing",
    "high_dose_supplements_recommended",
    "animal_or_alien_experiments_enabled",
    "external_apply_enabled",
)
MUST_TRUE = ("consent_required_before_human_data_collection",)
ALLOWED_KEYS = {
    "schema", "id", "title", "status", "scope", "research_questions",
    "candidate_exposures", "candidate_outcomes", "confounders",
    "hypotheses", "symbolic_interpretation", "literature",
    "consent_required_before_human_data_collection",
    "human_data_collection_enabled", "publish_individual_health_records",
    "individual_data_in_git", "clinical_diagnosis_enabled",
    "automated_nutrition_or_supplement_dosing",
    "high_dose_supplements_recommended",
    "animal_or_alien_experiments_enabled", "external_apply_enabled",
    "evidence_level", "safety_notes",
}

def review(spec):
    if not isinstance(spec, dict) or set(spec) != ALLOWED_KEYS:
        raise ValueError("unexpected keys or missing safety fields")
    for key, value in EXPECTED.items():
        if spec.get(key) != value:
            raise ValueError("incorrect research-only status: " + key)
    if any(spec.get(key) is not False for key in MUST_FALSE):
        raise ValueError("unsafe action or publication capability")
    if any(spec.get(key) is not True for key in MUST_TRUE):
        raise ValueError("informed consent boundary absent")
    if not isinstance(spec["title"], str) or not 20 <= len(spec["title"]) <= 200:
        raise ValueError("missing study title")
    if not isinstance(spec["safety_notes"], str) or len(spec["safety_notes"]) < 80:
        raise ValueError("missing participant safety notes")
    for key, minimum, maximum in (
        ("research_questions", 2, 12),
        ("candidate_exposures", 2, 32),
        ("candidate_outcomes", 3, 20),
        ("confounders", 4, 40),
        ("hypotheses", 2, 12),
        ("literature", 1, 20),
    ):
        v = spec[key]
        if not isinstance(v, list) or not minimum <= len(v) <= maximum:
            raise ValueError("invalid bounded collection: " + key)
    if any(not isinstance(v, str) or not 12 <= len(v) <= 500
           for v in spec["research_questions"]):
        raise ValueError("invalid research question")
    if any(not isinstance(v, str) or not 3 <= len(v) <= 128
           for k in ("candidate_exposures", "confounders") for v in spec[k]):
        raise ValueError("invalid proposed variable")
    if not {"brain_fog", "reading_comprehension", "axillary_odor", "breath_odor", "bowel_odor"}.issubset(
        {v.get("id") for v in spec["candidate_outcomes"] if isinstance(v, dict)}
    ):
        raise ValueError("missing independent cognition/odor outcomes")
    for v in spec["candidate_outcomes"]:
        if not isinstance(v, dict) or set(v) != {"id", "kind", "status"} or v["status"] != "NO_DATA":
            raise ValueError("a participant observation was smuggled into public metadata")
        if any(not isinstance(v[k], str) or not v[k] for k in ("id", "kind")):
            raise ValueError("invalid outcome")
    for v in spec["hypotheses"]:
        if (not isinstance(v, dict) or set(v) != {"id", "status", "test", "possible_refutation"}
            or v["status"] != "UNTESTED_EMPIRICAL_HYPOTHESIS"
            or any(not isinstance(v[k], str) or len(v[k]) < 12 for k in ("test", "possible_refutation"))):
            raise ValueError("empirical hypothesis mislabeled or lacks refutation criteria")
    symbol = spec["symbolic_interpretation"]
    if (not isinstance(symbol, dict) or set(symbol) != {"id", "status", "note"} or
        symbol["id"] != "high-frequency-vibration" or
        symbol["status"] != "UNOPERATIONALIZED_NO_VALIDATED_PHYSIOLOGICAL_MECHANISM" or
        not isinstance(symbol["note"], str) or len(symbol["note"]) < 100):
        raise ValueError("non-empirical interpretation overclaimed")
    for v in spec["literature"]:
        if (not isinstance(v, dict) or set(v) != {"id", "uri", "limits"} or
            not isinstance(v["uri"], str) or not v["uri"].startswith("https://") or
            not isinstance(v["limits"], str) or len(v["limits"]) < 24):
            raise ValueError("literature needs provenance and limits")
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return {
        "schema": "Everlife-Nutrition-Study-Review/1.0",
        "study_id": spec["id"],
        "status": "RESEARCH_PROTOCOL_VALIDATED_METADATA_ONLY",
        "protocol_sha256": hashlib.sha256(canonical).hexdigest(),
        "research_questions": len(spec["research_questions"]),
        "hypotheses": len(spec["hypotheses"]),
        "outcomes": len(spec["candidate_outcomes"]),
        "evidence": "NO_PARTICIPANT_DATA_OR_INDIVIDUAL_CAUSAL_FINDING",
        "spiritual_vibration_mechanism": "NOT_OPERATIONALIZED_OR_EMPIRICALLY_ESTABLISHED",
        "human_data_collected": False,
        "medical_conclusions": False,
        "clinical_or_supplement_action_authorized": False,
        "external_apply": False,
        "requires_human_review": True,
    }

def run():
    spec = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = review(spec)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"study": result["study_id"], "status": result["status"], "external_apply": False}))
    return result

if __name__ == "__main__":
    run()
