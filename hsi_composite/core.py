from __future__ import annotations
import hashlib, importlib.util, json
from pathlib import Path

PROTOCOL="HSI-COMPOSITE/1.0"
BASE=Path(__file__).resolve().parents[1]

def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

state_core=_load("hsi_state_core",BASE/"hsi_common"/"core.py")
intent_core=_load("hsi_intent_core",BASE/"hsi_intent"/"core.py")
REGISTRY=intent_core.load_registry(BASE/"hsi_intent"/"registry.json")

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def digest(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()

def certify(req):
    if not isinstance(req,dict):
        return {"protocol":PROTOCOL,"closed":0,"reason":"request must be object"}
    state=req.get("state")
    intent=req.get("intent")
    if not isinstance(state,dict) or not isinstance(intent,dict):
        return {"protocol":PROTOCOL,"closed":0,"reason":"state and intent objects are required"}
    try:
        state_cert=state_core.certify(state)
    except Exception as exc:
        state_cert={"protocol":getattr(state_core,"PROTOCOL","HSI-3SYS/1.0"),"closed":0,"error":f"{type(exc).__name__}: {exc}"}
    try:
        intent_cert=intent_core.certify_transition(REGISTRY,intent)
    except Exception as exc:
        intent_cert={"protocol":getattr(intent_core,"PROTOCOL","HSI-INTENT/1.1"),"closed":0,"error":f"{type(exc).__name__}: {exc}"}

    s_uid=str(state.get("subject_uid",""))
    i_uid=str(intent.get("subject_uid",""))
    same_subject=bool(s_uid) and s_uid==i_uid
    state_ok=state_cert.get("closed")==1
    intent_ok=intent_cert.get("closed")==1
    closed=state_ok and intent_ok and same_subject
    identity={
        "subject_uid":s_uid if same_subject else "",
        "state_godel":state_cert.get("godel"),
        "intent_transition_uid":intent_cert.get("transition_uid"),
        "blue_uid":intent_cert.get("blue_uid"),
        "state_protocol":state_cert.get("protocol"),
        "intent_protocol":intent_cert.get("protocol")
    }
    return {
        "protocol":PROTOCOL,
        "subject_uid":s_uid if same_subject else "",
        "composite_uid":digest(identity),
        "blue_uid":intent_cert.get("blue_uid"),
        "closed":int(closed),
        "checks":{
            "state_closed":state_ok,
            "intent_closed":intent_ok,
            "same_subject_uid":same_subject,
            "blue_preserved":bool((intent_cert.get("blue") or {}).get("preserved"))
        },
        "state_certificate":state_cert,
        "intent_certificate":intent_cert,
        "scope":"finite state + intent/Blue preservation certificate; no predictive or external-action authority"
    }
