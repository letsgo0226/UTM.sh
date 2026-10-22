"""Build a bounded, integrity-addressed machine manifest from local CI outputs.

SHA-256 covers artifact bytes, not a cryptographic signature. Publication
requires review; this tool cannot authorize a cloud deployment.
"""
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
INPUTS = ("latest.json", "unified-run.json", "control-plane.json", "railway-observation.json")
HEX40 = re.compile(r"^[a-f0-9]{40}$", re.I)


def artifact(name):
    if name not in INPUTS:
        raise ValueError("unknown artifact")
    raw = (PUBLIC / name).read_bytes()
    if len(raw) > 256_000:
        raise ValueError("oversized artifact")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("artifact JSON object required")
    return value, {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "bytes":len(raw),
                   "content_type":"application/json"}


def create(env=None):
    env = env or {}
    data, objects = {}, {}
    for name in INPUTS:
        data[name], objects[name] = artifact(name)
    formal = data["latest.json"]
    unified = data["unified-run.json"]
    control = data["control-plane.json"]
    railway = data["railway-observation.json"]
    if formal.get("schema") != "Everlife-Open-Registry/1.0":
        raise ValueError("wrong research schema")
    if (unified.get("schema") != "Everlife-Unified-Run/1.0" or
        unified.get("deployments_triggered") != 0 or
        unified.get("universal_halting_decidable") is not False):
        raise ValueError("unbounded or executable virtual deployment claim")
    if (control.get("schema") != "Everlife-Event-Bridge/1.0" or
        control.get("external_apply") is not False or
        control.get("deployments_triggered") != 0 or
        control.get("decision") not in {"REJECTED", "BLOCKED_RESOURCE_BUDGET",
          "OPERATOR_REVIEW_REQUIRED", "WAIT_FOR_AUTHORIZED_PLATFORM_OBSERVATION",
          "VERIFIED_FOR_PROPOSAL_REVIEW_ONLY"}):
        raise ValueError("unexpected actual execution authority")
    if (railway.get("schema") != "Everlife-Railway-Observation/1.0" or
        railway.get("writes_performed") != 0 or railway.get("trading_interactions") != 0 or
        railway.get("observation", {}).get("status") not in
         {"NOT_CONFIGURED","INVALID_PROJECT_SCOPE","UNAVAILABLE","OBSERVED"}):
        raise ValueError("invalid or executable Railway observation")
    if (formal.get("model",{}).get("clinical_or_veterinary_efficacy") is not None
        or formal.get("formal",{}).get("universal_halting_solver") is not False):
        raise ValueError("misleading biomedical/halting claim")
    sha = env.get("GITHUB_SHA","").lower()
    revision = sha if HEX40.fullmatch(sha) else None
    run_id = env.get("GITHUB_RUN_ID","")
    run_id = run_id if run_id.isdecimal() and len(run_id) <= 24 else None
    return {
        "schema":"Everlife-Machine-Manifest/1.0",
        "status":"CI_OUTPUT_FOR_REVIEW_NOT_PLATFORM_DEPLOYED",
        "repository":"letsgo0226/UTM.sh",
        "source_branch":"everlife-open-sdg-v1",
        "provenance":{"github_event_revision":revision,"github_run_id":run_id,
                      "role":"hash manifest, not a digital signature"},
        "machine":{"logical_scheduler":"bounded BF8 round-robin with G257/ATGC representation",
                   "jobs":len(unified["services"]),
                   "logical_steps":unified["total_steps"],
                   "run_chain_sha256":unified["chain_final_sha256"],
                   "physical_infinity_claim":False,
                   "general_halting_decider":False},
        "observer":{"railway_status":railway["observation"]["status"],
                    "real_time":False,
                    "deployment_changes":0,
                    "operator_review_required":control["decision"] != "VERIFIED_FOR_PROPOSAL_REVIEW_ONLY"},
        "evidence":{"biomedical":"NOT_VALIDATED","veterinary":"NOT_VALIDATED",
                    "ai_persistence":"SOURCE_AND_DATA_ONLY"},
        "artifacts":objects,
        "resource_boundary":"finite; Railway plan limits and platform availability cannot be bypassed",
        "control_boundary":"read-only; UTM/trading services unchanged"
    }


def verify(manifest):
    for name, expected in manifest["artifacts"].items():
        _, current = artifact(name)
        if current != expected:
            raise ValueError("artifact digest mismatch for "+name)
    if manifest["observer"]["deployment_changes"] != 0:
        raise ValueError("invalid deployment count")
    return True


if __name__ == "__main__":
    m=create(os.environ)
    assert verify(m)
    PUBLIC.mkdir(exist_ok=True)
    path=PUBLIC/"manifest.json"
    path.write_text(json.dumps(m,sort_keys=True,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"manifest":"VERIFIED_LOCAL_DIGESTS","objects":len(m["artifacts"]),
                      "railway":m["observer"]["railway_status"],"external_deployments":0}))
