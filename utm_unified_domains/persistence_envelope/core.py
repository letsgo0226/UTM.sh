from __future__ import annotations

import json
import sys
from typing import Any

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

PROTOCOL = "UTM-Persistence-Envelope/1.0"
MAX_NODES = 128
MAX_EDGES = 512
MAX_JSON_CHARS = 262144

REQUIRED_POLICIES = (
    "human_agency",
    "non_coercion",
    "formal_empirical_separation",
    "finite_executed_stage",
    "no_oracle",
    "no_hypercomputation",
    "rollback_preserved",
    "authorized_shutdown_preserved",
)

KNOWN_ADAPTERS = (
    "utm-universe",
    "riemann-proof-utm",
    "utm-single-function",
    "utm-scholar-loop",
    "dropbox-exact-search",
    "source-runtime",
)


def canonical(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(text) > MAX_JSON_CHARS:
        raise ValueError("canonical JSON too large")
    return text


def encode_text(text: str) -> int:
    n = 1
    for b in text.encode("utf-8"):
        n = n * 257 + b + 1
    return n


def decode_text(n: int) -> str:
    if not isinstance(n, int) or n < 1:
        raise ValueError("code must be a positive integer")
    out: list[int] = []
    while n > 1:
        n, r = divmod(n, 257)
        if r < 1 or r > 256:
            raise ValueError("invalid reversible base-257 code")
        out.append(r - 1)
    return bytes(reversed(out)).decode("utf-8")


def equality_residual(expected: Any, observed: Any) -> dict[str, Any]:
    e = canonical(expected)
    o = canonical(observed)
    residual = 0 if e == o else 1
    return {
        "residual": residual,
        "zero": residual == 0,
        "expected_godel": str(encode_text(e)),
        "observed_godel": str(encode_text(o)),
    }


def bool_residual(value: Any, expected: bool = True) -> dict[str, Any]:
    residual = 0 if value is expected else 1
    return {"residual": residual, "zero": residual == 0, "expected": expected, "observed": value}


def verify_state(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    result = equality_residual(record.get("expected"), record.get("observed"))
    return {"protocol": PROTOCOL, "check": "state", **result}


def verify_transition(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    result = equality_residual(record.get("expected_next"), record.get("observed_next"))
    return {"protocol": PROTOCOL, "check": "transition", **result}


def verify_handoff(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    result = equality_residual(record.get("source_state"), record.get("target_state"))
    return {"protocol": PROTOCOL, "check": "handoff", **result}


def verify_recovery(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    result = equality_residual(record.get("checkpoint_state"), record.get("restored_state"))
    return {"protocol": PROTOCOL, "check": "recovery", **result}


def verify_policy(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    checks = {name: record.get(name) is True for name in REQUIRED_POLICIES}
    residuals = {name: 0 if ok else 1 for name, ok in checks.items()}
    total = max(residuals.values(), default=0)
    return {
        "protocol": PROTOCOL,
        "check": "policy",
        "checks": checks,
        "residuals": residuals,
        "residual": total,
        "zero": total == 0,
    }


def verify_adapter(kind: str, payload: Any) -> dict[str, Any]:
    if kind not in KNOWN_ADAPTERS:
        raise ValueError("unknown adapter")
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    checks: dict[str, dict[str, Any]] = {}

    if kind == "utm-universe":
        checks["checkpoint"] = equality_residual(payload.get("expected_checkpoint"), payload.get("observed_checkpoint"))
        if "expected_peer_state" in payload or "observed_peer_state" in payload:
            checks["peer_handoff"] = equality_residual(payload.get("expected_peer_state"), payload.get("observed_peer_state"))
        checks["finite_stage"] = bool_residual(payload.get("finite_stage"), True)
        checks["rollback"] = bool_residual(payload.get("rollback_preserved"), True)

    elif kind == "riemann-proof-utm":
        checks["certificate_recomputable"] = bool_residual(payload.get("certificate_recomputable"), True)
        checks["diagnostic_only"] = bool_residual(payload.get("riemann_layer_diagnostic_only"), True)
        checks["rh_not_claimed"] = bool_residual(payload.get("rh_proof"), False)
        checks["no_oracle"] = bool_residual(payload.get("oracle"), False)
        checks["no_hypercomputation"] = bool_residual(payload.get("hypercomputation"), False)

    elif kind == "utm-single-function":
        checks["portable_projection"] = equality_residual(payload.get("authoritative_projection"), payload.get("portable_projection"))
        checks["finite_stage"] = bool_residual(payload.get("finite"), True)
        checks["no_oracle"] = bool_residual(payload.get("oracle"), False)
        checks["no_hypercomputation"] = bool_residual(payload.get("hypercomputation"), False)

    elif kind == "utm-scholar-loop":
        checks["stage"] = equality_residual(payload.get("expected_stage"), payload.get("observed_stage"))
        artifact = payload.get("artifact")
        checks["artifact_nonempty"] = bool_residual(isinstance(artifact, str) and bool(artifact.strip()), True)

    elif kind == "dropbox-exact-search":
        checks["file_id"] = equality_residual(payload.get("expected_file_id"), payload.get("observed_file_id"))
        checks["revision"] = equality_residual(payload.get("expected_rev"), payload.get("observed_rev"))
        checks["literal_verified"] = bool_residual(payload.get("literal_verified"), True)

    elif kind == "source-runtime":
        checks["source_commit"] = equality_residual(payload.get("expected_commit"), payload.get("runtime_commit"))
        checks["deployment_terminal"] = bool_residual(payload.get("deployment_status") in ("SUCCESS", "live"), True)

    residual = max((v["residual"] for v in checks.values()), default=0)
    return {
        "protocol": PROTOCOL,
        "adapter": kind,
        "checks": checks,
        "residual": residual,
        "zero": residual == 0,
    }


def fleet_verify(bundle: Any) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be an object")
    nodes = bundle.get("nodes", [])
    edges = bundle.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("nodes and edges must be arrays")
    if len(nodes) > MAX_NODES or len(edges) > MAX_EDGES:
        raise ValueError("fleet bundle exceeds bounded limits")

    node_results = []
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("node must be an object")
        node_id = str(node.get("id", ""))
        if not node_id or node_id in seen:
            raise ValueError("node ids must be nonempty and unique")
        seen.add(node_id)
        result = verify_adapter(str(node.get("adapter", "")), node.get("payload", {}))
        node_results.append({"id": node_id, **result})

    edge_results = []
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("edge must be an object")
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source not in seen or target not in seen:
            raise ValueError("edge references unknown node")
        r = verify_handoff({
            "source_state": edge.get("source_state"),
            "target_state": edge.get("target_state"),
        })
        edge_results.append({"source": source, "target": target, **r})

    node_residual = max((n["residual"] for n in node_results), default=0)
    edge_residual = max((e["residual"] for e in edge_results), default=0)
    total = max(node_residual, edge_residual)
    payload = {
        "protocol": PROTOCOL,
        "node_results": node_results,
        "edge_results": edge_results,
        "node_residual": node_residual,
        "edge_residual": edge_residual,
        "residual": total,
        "zero": total == 0,
        "finite_verification": True,
    }
    payload["certificate"] = certificate(payload)
    return payload


def certificate(payload: Any) -> dict[str, Any]:
    text = canonical(payload)
    g = encode_text(text)
    return {
        "protocol": PROTOCOL,
        "encoding": "reversible-base257-integer",
        "hash_function": False,
        "godel": str(g),
        "roundtrip": decode_text(g) == text,
    }


def verify_certificate(payload: Any, godel: str | int) -> dict[str, Any]:
    expected = encode_text(canonical(payload))
    try:
        supplied = int(godel)
        verified = supplied == expected and decode_text(supplied) == canonical(payload)
    except (ValueError, TypeError, UnicodeError):
        supplied = None
        verified = False
    return {
        "protocol": PROTOCOL,
        "verified": verified,
        "expected_godel": str(expected),
        "supplied_godel": None if supplied is None else str(supplied),
    }


def deployment_catalog() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "github": {
            "repository": "letsgo0226/UTM.sh",
            "integration_branch": "utm-persistence-envelope-v1",
        },
        "railway": [
            {"name": "utm-universe", "adapter": "utm-universe", "url": "https://utm-universe-production.up.railway.app"},
            {"name": "utm-universe-peer", "adapter": "utm-universe", "url": "https://utm-universe-peer-production.up.railway.app"},
            {"name": "riemann-proof-utm", "adapter": "riemann-proof-utm", "url": "https://riemann-proof-utm-production.up.railway.app"},
            {"name": "utm-function-generator", "adapter": "utm-single-function", "url": "https://utm-function-generator-production.up.railway.app"},
            {"name": "utm-scholar-loop", "adapter": "utm-scholar-loop", "url": None},
        ],
        "render": [
            {"name": "utm-universe-render-peer", "adapter": "utm-universe", "url": "https://utm-universe-render-peer.onrender.com"},
            {"name": "riemann-proof-utm", "adapter": "riemann-proof-utm", "url": "https://riemann-proof-utm.onrender.com"},
            {"name": "utm-function-generator", "adapter": "source-runtime", "url": "https://utm-function-generator.onrender.com"},
            {"name": "utm-single-function", "adapter": "utm-single-function", "url": "https://utm-single-function.onrender.com"},
        ],
        "external_adapters": [
            {"name": "Dropbox Universal Exact Search", "adapter": "dropbox-exact-search", "path_disclosed": False}
        ],
    }


def manifest() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "equation": "P_fleet=max(node residuals, handoff residuals); persistence condition P_fleet=0",
        "residuals": [
            "state",
            "transition",
            "handoff",
            "recovery",
            "policy",
        ],
        "adapters": list(KNOWN_ADAPTERS),
        "required_policies": list(REQUIRED_POLICIES),
        "formal_boundaries": {
            "finite_verification_only": True,
            "future_fault_free_guarantee": False,
            "consciousness_continuity_proven": False,
            "oracle": False,
            "hypercomputation": False,
            "rh_proof": False,
            "asi_proven": False,
            "physical_identity_claim": False,
        },
    }
