"""Everlife GitHub/Railway event bridge: bounded, read-only, fail-closed.

GitHub metadata is treated as untrusted input. No arbitrary program, shell,
GitHub/Railway mutation, medical action, or broker API is executed.
"""
import hashlib
import json
import os
import re
from pathlib import Path

from unified_machine import simulate, canonical
from resource_guard import check

ROOT = Path(__file__).resolve().parent
EXPECTED_REPO = "letsgo0226/UTM.sh"
EVENTS = {"push","pull_request","schedule","workflow_dispatch"}
HEX_SHA = re.compile(r"^[a-fA-F0-9]{40}$")


def github_event(env, event_document):
    kind = env.get("GITHUB_EVENT_NAME", "")
    repo = env.get("GITHUB_REPOSITORY", "")
    sha = env.get("GITHUB_SHA", "")
    ref = env.get("GITHUB_REF", "")
    run_id = env.get("GITHUB_RUN_ID", "")
    if kind not in EVENTS or repo != EXPECTED_REPO:
        return {"status":"REJECTED_EVENT","reason":"unsupported_event_or_repository"}
    if not HEX_SHA.fullmatch(sha) or not run_id.isdecimal() or len(run_id) > 24:
        return {"status":"REJECTED_EVENT","reason":"invalid_provenance"}
    if len(ref)>180 or not ref.startswith(("refs/heads/","refs/pull/")):
        return {"status":"REJECTED_EVENT","reason":"invalid_git_ref"}
    if not isinstance(event_document, dict):
        return {"status":"REJECTED_EVENT","reason":"invalid_event_document"}
    if kind == "pull_request":
        action = event_document.get("action","")
        if action not in {"opened","synchronize","reopened","ready_for_review","edited"}:
            return {"status":"REJECTED_EVENT","reason":"unsupported_pr_action"}
    digest = hashlib.sha256(canonical({"kind":kind,"repo":repo,"ref":ref,"sha":sha,"run_id":run_id})).hexdigest()
    return {"status":"OBSERVED_GITHUB_EVENT","kind":kind,"repo":repo,"ref":ref,
            "commit":sha.lower(),"run_id":run_id,"event_id":digest}


def classify(github, railway, budget, run):
    if github.get("status") != "OBSERVED_GITHUB_EVENT":
        decision = "REJECTED"
    elif budget.get("result") == "BLOCK":
        decision = "BLOCKED_RESOURCE_BUDGET"
    elif budget.get("result") == "REVIEW_REQUIRED":
        decision = "OPERATOR_REVIEW_REQUIRED"
    elif railway.get("status") not in ("OBSERVED",):
        decision = "WAIT_FOR_AUTHORIZED_PLATFORM_OBSERVATION"
    else:
        decision = "VERIFIED_FOR_PROPOSAL_REVIEW_ONLY"
    return {
        "schema":"Everlife-Event-Bridge/1.0",
        "github": github,
        "railway": railway,
        "budget": {"result":budget["result"], "hard_failures":budget["hard_failures"],
                   "requires_review":budget["requires_review"]},
        "virtual_scheduler":{"steps":run["total_steps"],"jobs":len(run["services"]),
                             "chain_final_sha256":run["chain_final_sha256"],
                             "all_halted":all(s["status"]=="HALTED" for s in run["services"])},
        "decision":decision, "external_apply":False, "deployments_triggered":0,
        "on_platform_outage":"retain GitHub verified artifacts; no external apply",
        "claims":{"real_time_railway_events":False,
                  "github_event_triggered":github.get("status")=="OBSERVED_GITHUB_EVENT",
                  "infinite_physical_resources":False,
                  "general_halting_solution":False}
    }


def build(env, event_document, railway):
    registry = json.loads((ROOT/"unified_registry.json").read_text(encoding="utf-8"))
    budget_policy = json.loads((ROOT/"resource_budget.json").read_text(encoding="utf-8"))
    return classify(github_event(env, event_document), railway,
                    check(budget_policy), simulate(registry))


def main():
    name = os.getenv("GITHUB_EVENT_NAME", "")
    event_path = os.getenv("GITHUB_EVENT_PATH", "")
    doc = {}
    if name and event_path:
        p=Path(event_path)
        if p.stat().st_size > 256*1024:
            raise SystemExit("event envelope too large")
        doc=json.loads(p.read_text(encoding="utf-8"))
    observed_path = ROOT/"public"/"railway-observation.json"
    railway = {"status":"NOT_CONFIGURED", "source":"none"}
    if observed_path.exists():
        record=json.loads(observed_path.read_text(encoding="utf-8"))
        railway=record.get("observation", railway)
    result=build(os.environ,doc,railway)
    out=ROOT/"public"/"control-plane.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"decision":result["decision"],"event":result["github"].get("kind"),
                      "readiness":result["railway"].get("status"),
                      "deployments_triggered":0}))


if __name__=="__main__":
    main()
