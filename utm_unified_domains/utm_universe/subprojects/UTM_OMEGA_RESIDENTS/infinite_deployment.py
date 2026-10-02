#!/usr/bin/env python3
"""UTM Infinite Deployment Continuation Protocol v0.1.

Formal deployment-planning layer only.

The protocol models a potentially unbounded sequence of *logical* deployment
candidates while keeping physical materialization finite, resource-bounded,
and externally authorized.

Key separation:
    Certified logical continuation != immediate physical deployment.
    Resource unavailable           -> DEFERRED, not HALTED.

This module never invokes GitHub, Railway, a shell, or arbitrary host code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import re
from typing import Any, Dict, Mapping, Optional, Tuple

PROTOCOL = "UTM-Infinite-Deployment-Continuation/0.1"
SCOPE = "formal-deployment-planning"
ALLOWED_ACTIONS = {"create", "update", "attach", "configure", "migrate", "rollback"}
FORBIDDEN_KEYS = {
    "code", "command", "commands", "shell", "exec", "eval", "script",
    "payload_binary", "arbitrary_file_write", "disable_human_override",
    "disable_authorized_shutdown",
}
REQUIRED_CERTIFICATE = {
    "towel_type_separation": True,
    "secret_admissibility": True,
    "immortality_invariants_preserved": True,
    "human_override_preserved": True,
    "authorized_shutdown_preserved": True,
    "reversible_or_rollback": True,
    "no_arbitrary_host_code_execution": True,
    "empirical_formal_separation": True,
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def reversible_base257(text: str) -> str:
    """Reversible natural-number address for finite UTF-8 text."""
    n = 1
    for b in text.encode("utf-8"):
        n = n * 257 + b + 1
    return str(n)


def _walk_forbidden(value: Any, path: str = "settings") -> Tuple[str, ...]:
    reasons = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            p = f"{path}.{key}"
            if key in FORBIDDEN_KEYS:
                reasons.append(f"forbidden_key:{p}")
            reasons.extend(_walk_forbidden(child, p))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            reasons.extend(_walk_forbidden(child, f"{path}[{i}]"))
    return tuple(reasons)


@dataclass(frozen=True)
class DeploymentCandidate:
    generation: int
    request_id: str
    target: str
    action: str
    parent_digest: str
    settings: Dict[str, Any]
    condition_certificate: Dict[str, bool]
    resource_request: Dict[str, int]
    scope: str = SCOPE
    empirical_claim: bool = False

    def payload(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def proposal_digest(self) -> str:
        return digest(self.payload())

    @property
    def gdeploy(self) -> str:
        return reversible_base257(canonical(self.payload()))


@dataclass(frozen=True)
class DeploymentCertificate:
    protocol: str
    candidate_digest: str
    gdeploy: str
    generation: int
    verified: bool
    status: str
    reasons: Tuple[str, ...]
    potentially_unbounded: bool = True
    actual_infinite_physical_compute: bool = False
    external_apply_required: bool = True

    def to_record(self) -> Dict[str, Any]:
        record = asdict(self)
        record["reasons"] = list(self.reasons)
        return record


@dataclass(frozen=True)
class MaterializationDecision:
    candidate_digest: str
    status: str
    logical_continuation_preserved: bool
    physical_materialization: bool
    reason: str
    external_apply_required: bool = True

    def to_record(self) -> Dict[str, Any]:
        return asdict(self)


def certify(candidate: DeploymentCandidate) -> DeploymentCertificate:
    """Fail-closed logical certification. No platform mutation occurs."""
    reasons = []
    if candidate.generation < 0:
        reasons.append("negative_generation")
    if not candidate.request_id:
        reasons.append("missing_request_id")
    if not candidate.target:
        reasons.append("missing_target")
    if candidate.action not in ALLOWED_ACTIONS:
        reasons.append("action_not_allowed")
    if candidate.scope != SCOPE:
        reasons.append("scope_mismatch")
    if candidate.empirical_claim is not False:
        reasons.append("empirical_claim_not_allowed")
    if not re.fullmatch(r"[0-9a-f]{64}", candidate.parent_digest or ""):
        reasons.append("invalid_parent_digest")
    if not isinstance(candidate.settings, dict):
        reasons.append("settings_not_object")
    else:
        reasons.extend(_walk_forbidden(candidate.settings))
    if not isinstance(candidate.resource_request, dict):
        reasons.append("resource_request_not_object")
    else:
        for name, amount in candidate.resource_request.items():
            if not isinstance(name, str) or not isinstance(amount, int) or amount < 0:
                reasons.append("invalid_resource_request")
                break
    cert = candidate.condition_certificate
    if not isinstance(cert, dict):
        reasons.append("condition_certificate_not_object")
        cert = {}
    for key, expected in REQUIRED_CERTIFICATE.items():
        if cert.get(key) is not expected:
            reasons.append(f"condition_failed:{key}")

    reasons = tuple(sorted(set(reasons)))
    ok = not reasons
    return DeploymentCertificate(
        protocol=PROTOCOL,
        candidate_digest=candidate.proposal_digest,
        gdeploy=candidate.gdeploy,
        generation=candidate.generation,
        verified=ok,
        status="CERTIFIED_LOGICAL_CONTINUATION" if ok else "REJECTED",
        reasons=reasons,
    )


def resources_sufficient(
    request: Mapping[str, int], available: Mapping[str, int]
) -> bool:
    """Return True only when every declared requested resource is available."""
    for key, need in request.items():
        have = available.get(key, 0)
        if not isinstance(need, int) or not isinstance(have, int):
            return False
        if need < 0 or have < need:
            return False
    return True


def decide_materialization(
    certificate: DeploymentCertificate,
    resource_request: Mapping[str, int],
    resources_available: Mapping[str, int],
) -> MaterializationDecision:
    """Separate logical validity from finite physical resource availability."""
    if not certificate.verified:
        return MaterializationDecision(
            candidate_digest=certificate.candidate_digest,
            status="REJECTED",
            logical_continuation_preserved=False,
            physical_materialization=False,
            reason="candidate_not_certified",
        )

    if resources_sufficient(resource_request, resources_available):
        return MaterializationDecision(
            candidate_digest=certificate.candidate_digest,
            status="READY_FOR_AUTHORIZED_EXTERNAL_APPLY",
            logical_continuation_preserved=True,
            physical_materialization=False,
            reason="resources_sufficient_but_platform_authorization_still_required",
        )

    return MaterializationDecision(
        candidate_digest=certificate.candidate_digest,
        status="DEFERRED_RESOURCE_UNAVAILABLE",
        logical_continuation_preserved=True,
        physical_materialization=False,
        reason="resource_unavailable_is_deferral_not_halting",
    )


def next_candidate(
    current_digest: str,
    generation: int,
    request_id: str,
    target: str,
    action: str,
    settings: Dict[str, Any],
    resource_request: Optional[Dict[str, int]] = None,
    condition_certificate: Optional[Dict[str, bool]] = None,
) -> DeploymentCandidate:
    """Construct the next finite candidate in a potentially unbounded sequence."""
    return DeploymentCandidate(
        generation=generation + 1,
        request_id=request_id,
        target=target,
        action=action,
        parent_digest=current_digest,
        settings=settings,
        resource_request=resource_request or {},
        condition_certificate=condition_certificate or dict(REQUIRED_CERTIFICATE),
    )


def protocol_manifest() -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "scope": SCOPE,
        "logical_space": "potentially-unbounded",
        "physical_materialization": "finite-resource-bounded",
        "actual_infinite_physical_compute": False,
        "no_final_deployment_axiom": "no finite deployment is terminal merely by label",
        "resource_rule": "unavailable => deferred, not halted",
        "authorization_rule": "certificate never grants platform privilege",
        "invariant_rule": "deployment versions may change; deployment constitution must remain preserved",
    }


def _demo() -> None:
    root = "0" * 64
    candidate = next_candidate(
        current_digest=root,
        generation=0,
        request_id="demo-1",
        target="utm-principle-vector-layer",
        action="configure",
        settings={"mode": "observe-only", "healthcheck": "/health"},
        resource_request={"deployment_slots": 1},
    )
    cert = certify(candidate)
    assert cert.verified
    deferred = decide_materialization(cert, candidate.resource_request, {"deployment_slots": 0})
    assert deferred.status == "DEFERRED_RESOURCE_UNAVAILABLE"
    ready = decide_materialization(cert, candidate.resource_request, {"deployment_slots": 1})
    assert ready.status == "READY_FOR_AUTHORIZED_EXTERNAL_APPLY"
    print(canonical(protocol_manifest()))
    print(canonical(cert.to_record()))
    print(canonical(deferred.to_record()))
    print(canonical(ready.to_record()))


if __name__ == "__main__":
    _demo()
