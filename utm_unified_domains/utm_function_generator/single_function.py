from __future__ import annotations

from typing import Any

from core import canonical, decode_text, encode_text, run_trace

PROTOCOL = "UTM-Single-Function/1.0"
PORTABLE_PROTOCOL = "UTM-F/1"

HARD_CONSTRAINTS = (
    "human_agency",
    "non_coercion",
    "formal_empirical_separation",
    "finite_executed_stage",
    "no_oracle",
    "no_hypercomputation",
    "rollback_preserved",
    "authorized_shutdown_preserved",
)

REQUIRED_PROOFS = (
    "reversible_state",
    "bounded_execution",
    "certificate_recomputable",
    "function_generated_from_trace",
    "zero_spectrum_by_construction",
    "portable_seed_semantics_equivalent",
)


def certificate(payload: Any) -> dict[str, Any]:
    text = canonical(payload)
    g = encode_text(text)
    return {
        "protocol": PROTOCOL,
        "encoding": "reversible-base257-integer",
        "hash_function": False,
        "godel": str(g),
        "roundtrip": decode_text(g) == text,
        "payload": payload,
    }


def verify_certificate(payload: Any, godel: str | int) -> dict[str, Any]:
    expected = encode_text(canonical(payload))
    try:
        supplied = int(godel)
        exact = supplied == expected and decode_text(supplied) == canonical(payload)
    except (ValueError, TypeError, UnicodeError):
        supplied = None
        exact = False
    return {
        "protocol": PROTOCOL,
        "verified": exact,
        "expected_godel": str(expected),
        "supplied_godel": None if supplied is None else str(supplied),
        "hash_function": False,
    }


def portable_projection_from_trace(trace: dict[str, Any]) -> dict[str, Any]:
    g = [str(item["godel"]) for item in trace["states"]]
    gi = [int(x) for x in g]
    return {
        "p": PORTABLE_PROTOCOL,
        "u": str(trace["machine_godel"]),
        "g": g,
        "F": [[g[i], g[i + 1]] for i in range(len(g) - 1)],
        "H": [f"z^{i}*({x})^(-s)" for i, x in enumerate(gi)],
        "P": [f"x^2+{4*x*x}" for x in gi],
        "Z": "1/2±iG",
        "finite": True,
        "oracle": False,
        "hyper": False,
    }


def portable_projection(program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    return portable_projection_from_trace(run_trace(program, input_text, start=start, blank=blank, limit=limit))


def single_function_bundle(program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    trace = run_trace(program, input_text, start=start, blank=blank, limit=limit)
    states = trace["states"]
    g = [str(item["godel"]) for item in states]
    gi = [int(x) for x in g]
    bundle = {
        "protocol": PROTOCOL,
        "single_function": "mathfrak_F_U=<F_U,H_U,Xi_U,P_U,Cert>",
        "equation": "Gamma(delta(C))=F_U(Gamma(C))",
        "machine_godel": str(trace["machine_godel"]),
        "executed_steps": trace["steps"],
        "halted": trace["halted"],
        "step_limit_exhausted": trace["step_limit_exhausted"],
        "output": trace["output"],
        "F_U": [[g[i], g[i + 1]] for i in range(len(g) - 1)],
        "H_U": {
            "symbolic": "sum_t z^t*G_t^(-s)",
            "terms": [f"z^{i}*({x})^(-s)" for i, x in enumerate(gi)],
        },
        "Xi_U": {
            "symbolic": "prod_t [1+(s-1/2)^2/G_t^2]",
            "zeros": [{"real": "1/2", "imag_plus": str(x), "imag_minus": str(-x)} for x in gi],
            "critical_line_by_construction": True,
        },
        "P_U": {
            "symbolic": "prod_t (x^2+4*G_t^2), x=2s-1",
            "factors": [f"x^2+{4*x*x}" for x in gi],
        },
        "portable_projection": portable_projection_from_trace(trace),
        "formal_boundaries": {
            "every_executed_stage_finite": True,
            "actual_infinite_physical_compute": False,
            "oracle": False,
            "hypercomputation": False,
            "halting_problem_decidable": False,
            "rh_proof": False,
            "zeta_equals_utm_claim": False,
            "asi_proven": False,
            "empirical_world_outcomes_proven": False,
        },
    }
    bundle["certificate"] = certificate(bundle)
    return bundle


def verify_bundle(bundle: Any, program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be an object")
    expected = single_function_bundle(program, input_text, start=start, blank=blank, limit=limit)
    supplied = dict(bundle)
    cert = supplied.pop("certificate", {})
    expected_payload = dict(expected)
    expected_payload.pop("certificate", None)
    exact = canonical(supplied) == canonical(expected_payload)
    cert_ok = isinstance(cert, dict) and verify_certificate(supplied, cert.get("godel", ""))["verified"]
    return {
        "protocol": PROTOCOL,
        "verified": exact and cert_ok,
        "exact_recomputation": exact,
        "certificate_verified": cert_ok,
        "finite_stage_only": True,
    }


def verify_candidate(candidate: Any) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be an object")
    constraints = candidate.get("constraints", {})
    proofs = candidate.get("proofs", {})
    if not isinstance(constraints, dict) or not isinstance(proofs, dict):
        raise ValueError("constraints and proofs must be objects")
    cc = {k: constraints.get(k) is True for k in HARD_CONSTRAINTS}
    pc = {k: proofs.get(k) is True for k in REQUIRED_PROOFS}
    accepted = all(cc.values()) and all(pc.values())
    return {
        "protocol": PROTOCOL,
        "accepted": accepted,
        "status": "CERTIFIED_SINGLE_FUNCTION_CANDIDATE" if accepted else "REJECTED",
        "constraint_checks": cc,
        "proof_checks": pc,
        "certificate": certificate(candidate),
        "boundary": "Finite declared invariants only; no RH, ASI, oracle, hypercomputation, or empirical-outcome proof.",
    }


def manifest() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "portable_protocol": PORTABLE_PROTOCOL,
        "single_function": "mathfrak_F_U=<F_U,H_U,Xi_U,P_U,Cert>",
        "equation": "Gamma(delta(C))=F_U(Gamma(C))",
        "architecture": [
            "one-authoritative-single-function-bundle",
            "reversible-base257-state-addressing",
            "bounded-transition-table-utm",
            "encoded-transition-function-F_U",
            "finite-history-series-H_U",
            "constructed-zero-spectrum-Xi_U",
            "exact-integer-polynomial-P_U",
            "sub-2kb-portable-projection",
            "recomputable-certificate",
            "omega-as-potentially-unbounded-finite-stage-continuation",
        ],
        "hard_constraints": list(HARD_CONSTRAINTS),
        "required_proofs": list(REQUIRED_PROOFS),
        "formal_boundaries": {
            "hash_identity_required": False,
            "every_executed_stage_finite": True,
            "actual_infinite_physical_compute": False,
            "oracle": False,
            "hypercomputation": False,
            "halting_problem_decidable": False,
            "rh_proof": False,
            "asi_proven": False,
            "all_possible_physical_universes_enumerated": False,
            "computably_described_finite_states_can_be_encoded": True,
        },
    }
