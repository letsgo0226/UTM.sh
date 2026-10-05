from __future__ import annotations

import cmath
import json
import math
from typing import Any

PROTOCOL = "Riemann-Proof-Carrying-UTM/1.0"
MAX_PROGRAM_CHARS = 12000
MAX_INPUT_CHARS = 4096
MAX_STEPS = 10000
MAX_ZETA_TERMS = 2048

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
    "riemann_layer_diagnostic_only",
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
    try:
        g = int(godel)
        expected = encode_text(canonical(payload))
        decoded = decode_text(g)
        exact = g == expected and decoded == canonical(payload)
    except (ValueError, TypeError, UnicodeError):
        g = None
        expected = encode_text(canonical(payload))
        exact = False
    return {
        "protocol": PROTOCOL,
        "verified": exact,
        "expected_godel": str(expected),
        "supplied_godel": None if g is None else str(g),
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


def run_utm(program: str, input_text: str, *, start: str = "0", blank: str = "_", limit: int = 2000) -> dict[str, Any]:
    if not isinstance(input_text, str) or len(input_text) > MAX_INPUT_CHARS:
        raise ValueError(f"input must be a string <= {MAX_INPUT_CHARS} chars")
    if not isinstance(blank, str) or len(blank) != 1:
        raise ValueError("blank must be one character")
    limit = max(0, min(int(limit), MAX_STEPS))
    rules = parse_program(program)
    tape = {i: c for i, c in enumerate(input_text) if c != blank}
    q = str(start)
    h = 0
    steps = 0
    halted = False
    while steps < limit:
        transition = rules.get((q, tape.get(h, blank)))
        if transition is None:
            halted = True
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
    state = {
        "q": q,
        "h": h,
        "steps": steps,
        "halted": halted,
        "step_limit_exhausted": not halted and steps >= limit,
        "output": output,
    }
    state["certificate"] = certificate(state)
    return state


def _log_bigint(n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    bits = n.bit_length()
    shift = max(0, bits - 53)
    mantissa = n >> shift
    return math.log(float(mantissa)) + shift * math.log(2.0)


def riemann_coordinate(payload: Any, *, sigma: float = 2.0, tau: float = 0.0, terms: int = 128) -> dict[str, Any]:
    """Map a reversible Goedel address into the Dirichlet basis n^{-s}.

    This is a diagnostic representation for Re(s)>1, not a proof of RH and not
    an assertion that the classical zeta function itself is a UTM.
    """
    sigma = float(sigma)
    tau = float(tau)
    terms = max(1, min(int(terms), MAX_ZETA_TERMS))
    if not math.isfinite(sigma) or not math.isfinite(tau) or sigma <= 1.0:
        raise ValueError("diagnostic Dirichlet series requires finite sigma > 1")
    g = encode_text(canonical(payload))
    s = complex(sigma, tau)
    log_g = _log_bigint(g)
    basis = cmath.exp(-s * log_g)
    zeta_partial = sum(cmath.exp(-s * math.log(k)) for k in range(1, terms + 1))
    return {
        "protocol": PROTOCOL,
        "godel": str(g),
        "s": {"sigma": sigma, "tau": tau},
        "dirichlet_basis": {"real": basis.real, "imag": basis.imag},
        "zeta_partial": {"terms": terms, "real": zeta_partial.real, "imag": zeta_partial.imag},
        "interpretation": "Goedel state mapped to n^-s inside the Dirichlet address space",
        "rh_proof": False,
        "zeta_equals_utm_claim": False,
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
    cert = certificate(candidate)
    return {
        "protocol": PROTOCOL,
        "status": "CERTIFIED_RESEARCH_CANDIDATE" if accepted else "REJECTED",
        "accepted": accepted,
        "constraint_checks": constraint_checks,
        "proof_checks": proof_checks,
        "certificate": cert,
        "asi_proven": False,
        "boundary": "Passing this finite gate is evidence about declared invariants, not proof of ASI, RH, or empirical-world outcomes.",
    }


def manifest() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "architecture": [
            "reversible-state-codec",
            "bounded-universal-transition-table-runtime",
            "riemann-dirichlet-address-layer",
            "proof-carrying-candidate-gate",
            "omega-as-potentially-unbounded-finite-stage-continuation",
            "scholar-loop-compatible-research-cycle",
            "normative-peace-and-cosmic-love-objective-layer",
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
            "riemann_layer_proves_rh": False,
            "candidate_gate_proves_asi": False,
            "empirical_claims_require_external_evidence": True,
        },
        "objective": {
            "ifr": "maximum admissible transformation with zero declared invariant loss",
            "peace": "minimize coercion and avoidable harm while preserving rights, agency, dialogue, repair, knowledge, wellbeing, and resilience",
            "cosmic_love": "normative admissibility/attractor principle, not asserted as a physical law",
        },
    }
