from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from typing import Any

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

PROTOCOL = "UTM-Analytic-Lift/1.0"
MAX_JSON_CHARS = 262144
MAX_TENSOR_K = 64
MAX_TENSOR_N = 8
SUPPORTED_AC_KINDS = (
    "polynomial",
    "geometric_series",
    "log_germ",
    "sqrt_germ",
    "lacunary_2n",
    "riemann_zeta",
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


def certificate(payload: Any) -> dict[str, Any]:
    text = canonical(payload)
    godel = encode_text(text)
    return {
        "protocol": PROTOCOL,
        "encoding": "reversible-base257-integer",
        "authoritative_identity": "godel",
        "godel": str(godel),
        "roundtrip": decode_text(godel) == text,
        "sha256_integrity_aid": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "sha256_authoritative_identity": False,
    }


def verify_certificate(payload: Any, godel: str | int) -> dict[str, Any]:
    text = canonical(payload)
    expected = encode_text(text)
    try:
        supplied = int(godel)
        verified = supplied == expected and decode_text(supplied) == text
    except (TypeError, ValueError, UnicodeError):
        supplied = None
        verified = False
    return {
        "protocol": PROTOCOL,
        "verified": verified,
        "expected_godel": str(expected),
        "supplied_godel": None if supplied is None else str(supplied),
    }


def _fraction_list(values: Any) -> list[Fraction]:
    if not isinstance(values, list) or not values:
        raise ValueError("coefficients must be a nonempty array")
    result = []
    for value in values:
        try:
            result.append(Fraction(str(value)))
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError("coefficients must be exact rational strings/numbers") from exc
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def _residual(ok: bool, label: str, detail: Any = None) -> dict[str, Any]:
    return {
        "label": label,
        "residual": 0 if ok else 1,
        "zero": ok,
        "detail": detail,
    }


def _finish(kind: str, status: str, checks: list[dict[str, Any]], result: dict[str, Any]) -> dict[str, Any]:
    residual = max((c["residual"] for c in checks), default=0)
    payload = {
        "protocol": PROTOCOL,
        "kind": kind,
        "status": status,
        "checks": checks,
        "residual": residual,
        "zero": residual == 0,
        "finite_verification": True,
        "result": result,
    }
    payload["certificate"] = certificate(payload)
    return payload


def solve_polynomial(request: dict[str, Any]) -> dict[str, Any]:
    source = _fraction_list(request.get("source_coefficients"))
    candidate = _fraction_list(request.get("candidate_coefficients", request.get("source_coefficients")))
    target_domain = request.get("target_domain", "C")
    coefficient_match = source == candidate
    supported_target = target_domain == "C"
    checks = [
        _residual(coefficient_match, "coefficient_identity"),
        _residual(supported_target, "target_domain_supported", {"required": "C", "observed": target_domain}),
    ]
    if coefficient_match and supported_target:
        status = "proved"
        explanation = "A polynomial is entire, so the identical polynomial is its unique analytic continuation to C."
    else:
        status = "rejected-candidate"
        explanation = "The supplied candidate did not satisfy the exact supported polynomial continuation schema."
    result = {
        "source_coefficients": [str(x) for x in source],
        "candidate_coefficients": [str(x) for x in candidate],
        "target_domain": target_domain,
        "carrier": "complex-plane",
        "explanation": explanation,
    }
    return _finish("polynomial", status, checks, result)


def solve_geometric_series(request: dict[str, Any]) -> dict[str, Any]:
    target = request.get("target_domain", "C-minus-{1}")
    checks = [_residual(target == "C-minus-{1}", "target_domain_exact")]
    status = "proved" if checks[0]["zero"] else "rejected-candidate"
    result = {
        "source": "sum_{n>=0} z^n on |z|<1",
        "continuation": "1/(1-z)",
        "target_domain": "C-minus-{1}",
        "obstruction": {"type": "simple-pole", "point": "1"},
        "identity": "(1-z) * sum_{n=0}^N z^n = 1-z^(N+1); limit on |z|<1 gives 1",
        "explanation": "The geometric series has the unique analytic continuation 1/(1-z) on C\\{1}.",
    }
    return _finish("geometric_series", status, checks, result)


def solve_log_germ(request: dict[str, Any]) -> dict[str, Any]:
    mode = request.get("mode", "riemann-surface")
    checks = [_residual(mode == "riemann-surface", "lift_mode_supported")]
    status = "proved-lift" if checks[0]["zero"] else "undetermined"
    result = {
        "planar_global_single_value_on_C_minus_0": False,
        "carrier": "C_w",
        "projection": "pi(w)=exp(w)",
        "lifted_function": "F(w)=w",
        "deck_action": "w -> w + 2*pi*i*k",
        "interpretation": "Different logarithm branches become different points/sheets above the same base point.",
    }
    return _finish("log_germ", status, checks, result)


def solve_sqrt_germ(request: dict[str, Any]) -> dict[str, Any]:
    mode = request.get("mode", "riemann-surface")
    checks = [_residual(mode == "riemann-surface", "lift_mode_supported")]
    status = "proved-lift" if checks[0]["zero"] else "undetermined"
    result = {
        "carrier": "C_w",
        "projection": "pi(w)=w^2",
        "lifted_function": "F(w)=w",
        "branch_point": "z=0",
        "interpretation": "The two planar branches are one single-valued holomorphic coordinate on the lifted surface.",
    }
    return _finish("sqrt_germ", status, checks, result)


def solve_lacunary_2n(request: dict[str, Any]) -> dict[str, Any]:
    target = request.get("target_domain", "cross-unit-circle")
    crossing = target == "cross-unit-circle"
    checks = [_residual(crossing, "target_crosses_natural_boundary")]
    status = "disproved-for-target-domain" if crossing else "undetermined"
    result = {
        "source": "sum_{n>=0} z^(2^n) on |z|<1",
        "natural_boundary": "|z|=1",
        "reason": "Hadamard gap theorem applies to exponents 2^n.",
        "target_domain": target,
        "explanation": (
            "No analytic continuation exists to any target domain that genuinely crosses the unit circle."
            if crossing
            else "This bounded schema only certifies the standard crossing obstruction."
        ),
    }
    return _finish("lacunary_2n", status, checks, result)


def solve_riemann_zeta(request: dict[str, Any]) -> dict[str, Any]:
    mode = request.get("mode", "meromorphic")
    target = request.get("target_domain", "C")
    exact_schema = mode == "meromorphic" and target == "C"
    checks = [
        _residual(mode == "meromorphic", "meromorphic_not_entire"),
        _residual(target == "C", "target_domain_supported"),
    ]
    status = "theorem-schema" if exact_schema else "undetermined"
    result = {
        "source": "zeta(s)=sum_{n>=1} n^(-s), Re(s)>1",
        "continuation_type": "meromorphic",
        "target_domain": "C",
        "pole": {"point": "s=1", "order": 1},
        "entire_regularization": "(s-1)*zeta(s) is entire",
        "rh_proof": False,
        "zeta_is_literal_utm": False,
        "note": "The runtime records the standard continuation theorem schema; it does not derive RH or hypercomputation.",
    }
    return _finish("riemann_zeta", status, checks, result)


def solve_ac(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    kind = request.get("kind")
    if kind not in SUPPORTED_AC_KINDS:
        payload = {
            "protocol": PROTOCOL,
            "kind": kind,
            "status": "undetermined",
            "checks": [],
            "residual": None,
            "zero": None,
            "finite_verification": True,
            "result": {
                "reason": "unsupported analytic-continuation class",
                "supported_kinds": list(SUPPORTED_AC_KINDS),
                "nonexistence_not_inferred": True,
            },
        }
        payload["certificate"] = certificate(payload)
        return payload
    return {
        "polynomial": solve_polynomial,
        "geometric_series": solve_geometric_series,
        "log_germ": solve_log_germ,
        "sqrt_germ": solve_sqrt_germ,
        "lacunary_2n": solve_lacunary_2n,
        "riemann_zeta": solve_riemann_zeta,
    }[kind](request)


def program_lift(payload: Any, level: int = 0) -> dict[str, Any]:
    if not isinstance(level, int) or level < 0 or level > 64:
        raise ValueError("level must be an integer in [0,64]")
    text = canonical(payload)
    godel = encode_text(text)
    coordinate = "X" if level == 0 else ("Y" if level == 1 else "Z/meta")
    result = {
        "protocol": PROTOCOL,
        "operation": "program-lift",
        "input_level": level,
        "output_level": level + 1,
        "coordinate": coordinate,
        "semantics": "the encoded object becomes data for the next computable transformation layer",
        "godel": str(godel),
        "roundtrip": decode_text(godel) == text,
        "oracle": False,
        "hypercomputation": False,
    }
    result["certificate"] = certificate(result)
    return result


def tensor_lift(k: Any, n: Any) -> dict[str, Any]:
    try:
        k = int(k)
        n = int(n)
    except (TypeError, ValueError) as exc:
        raise ValueError("k and n must be integers") from exc
    if not (1 <= k <= MAX_TENSOR_K):
        raise ValueError(f"k must be in [1,{MAX_TENSOR_K}]")
    if not (1 <= n <= MAX_TENSOR_N):
        raise ValueError(f"n must be in [1,{MAX_TENSOR_N}]")
    dimension = k ** n
    result = {
        "protocol": PROTOCOL,
        "operation": "tensor-lift",
        "base_dimension": k,
        "order": n,
        "interaction_coordinate_count": dimension,
        "formula": "k^n",
        "warning": "This is a tensor/self-interaction coordinate count, not a claim about physical spacetime dimension.",
    }
    result["certificate"] = certificate(result)
    return result


def manifest() -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "core_equation": "AC_{D->Omega}(F;f)=(dbar F, F|_D-f)=(0,0)",
        "supported_ac_kinds": list(SUPPORTED_AC_KINDS),
        "lift_semantics": {
            "UTM^UTM": "computable program transformations represented as data at a higher descriptive level",
            "UTM-X": "state/data coordinate",
            "UTM-Y": "program-transformation coordinate",
            "UTM-Z": "meta-transformation/certificate coordinate",
            "tensor": "k^n interaction-coordinate lift",
        },
        "statuses": [
            "proved",
            "proved-lift",
            "disproved-for-target-domain",
            "theorem-schema",
            "rejected-candidate",
            "undetermined",
        ],
        "formal_boundaries": {
            "finite_executed_stage": True,
            "generic_ac_solver": False,
            "nonexistence_from_undetermined": False,
            "oracle": False,
            "hypercomputation": False,
            "halting_problem_solved": False,
            "rh_proof": False,
            "physical_dimension_claim": False,
            "empirical_world_guarantee": False,
        },
    }
