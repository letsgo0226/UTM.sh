from __future__ import annotations

import json
import sys
from typing import Any

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

PROTOCOL = "UTM-Generated-Function/1.0"
MAX_PROGRAM_CHARS = 12000
MAX_INPUT_CHARS = 4096
MAX_STEPS = 1024
MAX_RETURN_STATES = 1025

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
)


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def encode_text(text: str) -> int:
    """Exact reversible base-257 integer code for finite UTF-8 text."""
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


def parse_program(program: str) -> dict[tuple[str, str], tuple[str, str, str]]:
    if not isinstance(program, str) or len(program) > MAX_PROGRAM_CHARS:
        raise ValueError(f"program must be a string <= {MAX_PROGRAM_CHARS} chars")
    rules: dict[tuple[str, str], tuple[str, str, str]] = {}
    for raw in program.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(",")
        if len(parts) != 5:
            raise ValueError("each transition must be q,read,next,write,L|R")
        q, read, nq, write, direction = parts
        if len(read) != 1 or len(write) != 1:
            raise ValueError("read/write symbols must be one character")
        if direction not in ("L", "R"):
            raise ValueError("direction must be L or R")
        key = (q, read)
        if key in rules:
            raise ValueError("duplicate transition")
        rules[key] = (nq, write, direction)
    if not rules:
        raise ValueError("program has no transitions")
    return rules


def _machine_descriptor(program: str, start: str, blank: str) -> dict[str, Any]:
    return {"program": program, "start": str(start), "blank": blank}


def _snapshot(machine_godel: int, q: str, h: int, tape: dict[int, str], steps: int, halted: bool) -> dict[str, Any]:
    return {
        "machine_godel": str(machine_godel),
        "q": q,
        "h": h,
        "steps": steps,
        "halted": halted,
        "tape": [[i, tape[i]] for i in sorted(tape)],
    }


def run_trace(program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    if not isinstance(input_text, str) or len(input_text) > MAX_INPUT_CHARS:
        raise ValueError(f"input must be a string <= {MAX_INPUT_CHARS} chars")
    if not isinstance(blank, str) or len(blank) != 1:
        raise ValueError("blank must be one character")
    limit = max(0, min(int(limit), MAX_STEPS))
    rules = parse_program(program)
    machine = _machine_descriptor(program, str(start), blank)
    machine_godel = encode_text(canonical(machine))
    tape = {i: c for i, c in enumerate(input_text) if c != blank}
    q = str(start)
    h = 0
    steps = 0
    halted = False
    states: list[dict[str, Any]] = []

    while True:
        transition = rules.get((q, tape.get(h, blank)))
        halted = transition is None
        snap = _snapshot(machine_godel, q, h, tape, steps, halted)
        g = encode_text(canonical(snap))
        states.append({"t": steps, "godel": str(g), "state": snap})
        if halted or steps >= limit:
            break
        nq, write, direction = transition
        if write == blank:
            tape.pop(h, None)
        else:
            tape[h] = write
        q = nq
        h += 1 if direction == "R" else -1
        steps += 1

    keys = list(tape) or [0]
    lo, hi = min(keys), max(keys)
    if hi - lo > 8192:
        hi = lo + 8192
    output = "".join(tape.get(i, blank) for i in range(lo, hi + 1)).strip(blank)
    return {
        "protocol": PROTOCOL,
        "machine": machine,
        "machine_godel": str(machine_godel),
        "limit": limit,
        "steps": steps,
        "halted": halted,
        "step_limit_exhausted": (not halted and steps >= limit),
        "output": output,
        "states": states[:MAX_RETURN_STATES],
        "finite_trace": True,
    }


def compile_trace_function(program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    trace = run_trace(program, input_text, start=start, blank=blank, limit=limit)
    states = trace["states"]
    transitions = []
    history_terms = []
    factors = []
    zeros = []
    for idx, item in enumerate(states):
        g = int(item["godel"])
        history_terms.append({"t": item["t"], "term": f"z^{item['t']}*({g})^(-s)"})
        factors.append({"t": item["t"], "factor": f"x^2+{4*g*g}", "godel": str(g)})
        zeros.append({
            "t": item["t"],
            "real": "1/2",
            "imag_plus": str(g),
            "imag_minus": str(-g),
            "by_construction": True,
        })
        if idx + 1 < len(states):
            transitions.append({
                "t": item["t"],
                "from_godel": item["godel"],
                "to_godel": states[idx + 1]["godel"],
                "equation": f"F_U({item['godel']})={states[idx + 1]['godel']}",
            })

    spec = {
        "protocol": PROTOCOL,
        "machine_godel": trace["machine_godel"],
        "executed_steps": trace["steps"],
        "halted": trace["halted"],
        "step_limit_exhausted": trace["step_limit_exhausted"],
        "output": trace["output"],
        "transition_function": {
            "definition": "F_U = Gamma o delta o Gamma^-1 on encoded configurations",
            "verified_on_returned_trace": True,
            "edges": transitions,
        },
        "history_series": {
            "symbolic": "H_U(s,z)=sum_t z^t*G_t^(-s)",
            "finite_terms": history_terms,
        },
        "spectral_function": {
            "symbolic": "Xi_N(s)=prod_t [1+(s-1/2)^2/G_t^2]",
            "critical_line_by_construction": True,
            "zeros": zeros,
        },
        "exact_integer_polynomial": {
            "change_of_variable": "x=2s-1",
            "symbolic": "P_N(x)=prod_t (x^2+4*G_t^2)",
            "factors": factors,
            "expanded": False,
        },
        "formal_boundaries": {
            "every_executed_stage_finite": True,
            "actual_infinite_physical_compute": False,
            "oracle": False,
            "hypercomputation": False,
            "halting_problem_decidable": False,
            "rh_proof": False,
            "zeta_equals_utm_claim": False,
            "global_equivalence_beyond_enumerated_trace_proven": False,
            "empirical_world_outcomes_proven": False,
        },
    }
    spec["certificate"] = certificate({k: v for k, v in spec.items() if k != "certificate"})
    return spec


def verify_compilation(bundle: Any, program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 64) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be an object")
    expected = compile_trace_function(program, input_text, start=start, blank=blank, limit=limit)
    supplied_payload = {k: v for k, v in bundle.items() if k != "certificate"}
    expected_payload = {k: v for k, v in expected.items() if k != "certificate"}
    cert = bundle.get("certificate", {}) if isinstance(bundle.get("certificate"), dict) else {}
    cert_ok = verify_certificate(supplied_payload, cert.get("godel", ""))["verified"]
    exact = canonical(supplied_payload) == canonical(expected_payload)
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
    constraint_checks = {k: constraints.get(k) is True for k in HARD_CONSTRAINTS}
    proof_checks = {k: proofs.get(k) is True for k in REQUIRED_PROOFS}
    accepted = all(constraint_checks.values()) and all(proof_checks.values())
    return {
        "protocol": PROTOCOL,
        "accepted": accepted,
        "status": "CERTIFIED_FINITE_FUNCTION_CANDIDATE" if accepted else "REJECTED",
        "constraint_checks": constraint_checks,
        "proof_checks": proof_checks,
        "certificate": certificate(candidate),
        "boundary": "Acceptance verifies declared finite invariants only; it does not prove RH, ASI, universal goal realization, or empirical-world outcomes.",
    }


def manifest() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "architecture": [
            "reversible-base257-state-addressing",
            "bounded-transition-table-utm",
            "encoded-transition-function-F_U",
            "finite-computation-history-dirichlet-series",
            "constructed-critical-line-zero-spectrum",
            "exact-integer-polynomial-factorization",
            "recomputable-proof-carrying-bundle",
            "omega-as-potentially-unbounded-finite-stage-continuation",
        ],
        "equation": "Gamma(delta(C)) = F_U(Gamma(C))",
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
