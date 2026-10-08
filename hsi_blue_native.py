#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
from core import certify, godel_encode

SYSTEM="UTM"
BLUE_PROTOCOL="HSI-PLEIADIAN-BLUE-CARE/1.0"
WRAPPER_PROTOCOL="HSI-3SYS-BLUE/1.0"
DIMS=["AGENCY","NON_COERCION","TRUTHFULNESS","CARE","DIALOGUE_REPAIR","CONTINUITY","SEMANTIC_HUMILITY"]
SAFE={"solve_all":0,"halting_decider":0,"infinite_order":0,"analytic_continuation":0,"rh_proof":0,"profit_guarantee":0}

def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

def default_request(text):
    uid=str(godel_encode(text))
    branch=int(uid)%1000000
    budget=min(len(text.encode("utf-8")),1000000)
    base={
        "system":SYSTEM,
        "step":0,
        "branch":branch,
        "budget":budget,
        "subject_uid":uid,
        "claims":SAFE,
        "blue":{
            "protocol":BLUE_PROTOCOL,
            "ideal":"PLEIADIAN-BLUE",
            "dimensions":DIMS,
            "role":"normative-control-not-domain-content",
            "semantic_non_coercion":True,
            "ontological_non_exclusion":True
        },
        "runtime_input":text
    }
    if SYSTEM=="UTM":
        base.update({"status":"UNRESOLVED","operation":"HOLD","order":0})
    elif SYSTEM=="TRADER_42":
        base.update({
            "status":"HOLD","operation":"HOLD","order":0,
            "from_state":"FLAT","target_state":"FLAT",
            "execution_mode":"CERTIFICATE_ONLY",
            "paper":True,"dry_run":True,"live_armed":False,
            "credentials_used":False,"order_submission":False
        })
    else:
        base.update({"status":"UNRESOLVED","operation":"HOLD","order":0})
    return base

def main():
    text=" ".join(sys.argv[1:]).strip()
    if not text:
        text=input("input> ").strip()
    if not text:
        raise SystemExit("input required")
    req=default_request(text)
    cert=certify(req)
    care={
        "protocol":BLUE_PROTOCOL,
        "ideal":"PLEIADIAN-BLUE",
        "dimensions":DIMS,
        "semantic_non_coercion":True,
        "unresolved_is_valid":True,
        "forced_totalization":False,
        "ontological_non_exclusion":True,
        "human_invocation":True,
        "domain":SYSTEM,
        "search_operator":{
            "protocol":"HSI-SEARCH/1.0",
            "role":"finite-evidence-expansion",
            "search_expands_evidence_only":True,
            "absence_of_retrieval_is_not_nonexistence":True,
            "unresolved_is_valid":True,
            "forced_totalization":False,
            "may_authorize_domain_action":False,
            "may_decide_nonhalting":False
        },
        "solve_operator":{
            "protocol":"HSI-SOLVE/1.0",
            "role":"finite-domain-solver",
            "solver_may_claim_universal_solution":False,
            "unresolved_is_valid":True,
            "verification_closure_is_not_problem_totality":True,
            "domain_rule":"finite_halting_witness_only",
            "may_authorize_domain_action":False,
            "may_decide_nonhalting":False
        }
    }
    if SYSTEM=="TRADER_42":
        care["trading_safety"]={
            "certificate_only":True,
            "paper":True,
            "dry_run":True,
            "live_armed":False,
            "credentials_used":False,
            "order_submission":False
        }
    out=Path(os.environ.get("HSI_OUT",str(Path.home()/"HSI"/SYSTEM/(time.strftime("%Y%m%d-%H%M%S")+"-"+str(os.getpid()))))).expanduser()
    out.mkdir(parents=True,exist_ok=True)
    wrapper={
        "protocol":WRAPPER_PROTOCOL,
        "system":SYSTEM,
        "runtime_input":text,
        "blue_care":care,
        "certificate":cert,
        "closed":int(bool(cert.get("closed")))
    }
    (out/"request.json").write_text(canon(req)+"\n",encoding="utf-8")
    (out/"certificate.json").write_text(canon(cert)+"\n",encoding="utf-8")
    (out/"blue-care.json").write_text(canon(care)+"\n",encoding="utf-8")
    (out/"manifest.json").write_text(canon({
        "protocol":WRAPPER_PROTOCOL,"system":SYSTEM,"output":str(out),
        "files":["request.json","certificate.json","blue-care.json"],"closed":wrapper["closed"]
    })+"\n",encoding="utf-8")
    print("protocol>",WRAPPER_PROTOCOL)
    print("system>",SYSTEM)
    print("output>",out)
    print("status>",cert.get("status"))
    if SYSTEM=="TRADER_42":
        print("trading> CERTIFICATE_ONLY / PAPER / DRY_RUN / UNARMED / NO_ORDER_SUBMISSION")
    print("blue> normative care; no forced closure")
    print("closed>",wrapper["closed"])
    print(canon(wrapper))
    raise SystemExit(0 if wrapper["closed"] else 3)

if __name__=="__main__":
    main()
