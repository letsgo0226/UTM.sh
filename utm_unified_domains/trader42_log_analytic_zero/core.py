from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction
from typing import Any

PROTOCOL = "Trader42-Log-Analytic-Zero/1.1"
MAX_JSON_BYTES = 16384
MAX_CODEC_BYTES = 1024
REQUIRED = ("g_re", "g_im", "continuation_residual", "risk_residual", "certificate_residual")
SCALAR = re.compile(r"[+-]?(?:[0-9]+(?:/[0-9]+)?|(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)\Z")


def object_value(value: Any, name: str = "payload") -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def required(d: dict, fields: tuple | list) -> None:
    missing = [k for k in fields if k not in d]
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))


def validate_json(value: Any, depth: int = 0, budget: list | None = None) -> None:
    if budget is None:
        budget = [1024]
    budget[0] -= 1
    if depth > 16 or budget[0] < 0:
        raise ValueError("JSON structure limit exceeded")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite number")
    if isinstance(value, str) and len(value.encode()) > 4096:
        raise ValueError("string limit exceeded")
    if isinstance(value, int) and value.bit_length() > 256:
        raise ValueError("integer limit exceeded")
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError("JSON keys must be strings")
            validate_json(k, depth + 1, budget)
            validate_json(v, depth + 1, budget)
    elif isinstance(value, list):
        for v in value:
            validate_json(v, depth + 1, budget)


def canonical(x: Any) -> str:
    validate_json(x)
    s = json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if len(s.encode()) > MAX_JSON_BYTES:
        raise ValueError("canonical document too large")
    return s


def bounded(v: Fraction) -> Fraction:
    if max(v.numerator.bit_length(), v.denominator.bit_length()) > 2048:
        raise ValueError("arithmetic precision limit exceeded")
    return v


def q(v: Any) -> Fraction:
    if isinstance(v, bool) or not isinstance(v, (str, int, float)):
        raise ValueError("exact rational scalar required")
    s = str(v)
    if len(s) > 80 or not SCALAR.fullmatch(s):
        raise ValueError("invalid or oversized rational scalar")
    if "e" in s.lower() and abs(int(s.lower().split("e")[1])) > 64:
        raise ValueError("exponent limit exceeded")
    try:
        value = Fraction(s)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid rational scalar") from exc
    if max(value.numerator.bit_length(), value.denominator.bit_length()) > 256:
        raise ValueError("scalar precision limit exceeded")
    return value


def encode_text(s: str) -> int:
    raw = s.encode()
    if len(raw) > MAX_CODEC_BYTES:
        raise ValueError("codec input exceeds 1024 bytes")
    n = 1
    for b in raw:
        n = n * 257 + b + 1
    return n


def decode_text(n: int) -> str:
    if type(n) is not int or n < 1 or n.bit_length() > 8210:
        raise ValueError("bounded positive integer required")
    a = []
    while n > 1:
        n, r = divmod(n, 257)
        if not 1 <= r <= 256:
            raise ValueError("invalid code")
        a.append(r - 1)
    return bytes(reversed(a)).decode()


def cert(document: Any) -> dict:
    s = canonical(document)
    result = {"kind": "replay_receipt", "receipt": document,
              "sha256": hashlib.sha256(s.encode()).hexdigest(),
              "authenticated": False, "mathematical_proof_by_encoding": False}
    if len(s.encode()) <= MAX_CODEC_BYTES:
        g = encode_text(s)
        result.update(godel=str(g), roundtrip=decode_text(g) == s)
    else:
        result.update(godel=None, roundtrip=None, codec_status="omitted-size-limit")
    return result


def attach_receipt(d: dict, out: dict) -> dict:
    out["certificate"] = cert({"inputs": d, "result": dict(out)})
    return out


def coefficients(value: Any) -> list[Fraction]:
    if not isinstance(value, list) or not 1 <= len(value) <= 32:
        raise ValueError("coefficients must be an array of 1 to 32 scalars")
    result = [q(v) for v in value]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def polynomial_check(witness: Any, gr: Fraction, gi: Fraction) -> bool | None:
    if witness is None:
        return None
    w = object_value(witness, "analytic_witness")
    if w.get("kind") != "polynomial":
        return None
    required(w, ("source_coefficients", "candidate_coefficients", "z_re", "z_im", "target_domain"))
    source = coefficients(w["source_coefficients"])
    candidate = coefficients(w["candidate_coefficients"])
    zr, zi = q(w["z_re"]), q(w["z_im"])
    re, im = Fraction(0), Fraction(0)
    for a in reversed(candidate):
        re, im = bounded(re * zr - im * zi + a), bounded(re * zi + im * zr)
    return source == candidate and w["target_domain"] == "C" and (re, im) == (gr, gi)


def state(value: Any) -> tuple[Fraction, Fraction]:
    d = object_value(value, "state")
    required(d, ("cash", "base"))
    return q(d["cash"]), q(d["base"])


def risk_check(witness: Any) -> dict | None:
    if witness is None:
        return None
    w = object_value(witness, "risk_witness")
    required(w, ("state_before", "action", "state_after"))
    cash, base = state(w["state_before"])
    after = state(w["state_after"])
    action = object_value(w["action"], "action")
    required(action, ("side", "quantity", "price", "fee"))
    side = action["side"]
    if side not in ("BUY", "SELL", "HOLD"):
        raise ValueError("unsupported action side")
    qty, price, fee = (q(action[k]) for k in ("quantity", "price", "fee"))
    valid_before = cash >= 0 and base >= 0
    guard = qty >= 0 and price > 0 and fee >= 0
    if side == "BUY":
        expected = bounded(cash - qty * price - fee), bounded(base + qty)
        guard = guard and qty > 0 and expected[0] >= 0
    elif side == "SELL":
        expected = bounded(cash + qty * price - fee), bounded(base - qty)
        guard = guard and qty > 0 and expected[1] >= 0
    else:
        expected = cash, base
        guard = guard and qty == 0 and fee == 0
    nonnegative = all(v >= 0 for v in expected)
    matches = expected == after
    return {"scope": "provided long-only simulation state: exact balance arithmetic and nonnegative balances",
            "invariant_before": valid_before, "guard_passed": guard,
            "transition_preserves_invariant": nonnegative,
            "state_after_matches": matches,
            "verified": valid_before and guard and nonnegative and matches,
            "expected_state_after": {"cash": str(expected[0]), "base": str(expected[1])},
            "external_state_authenticated": False, "exchange_risk_checked": False}


def evaluate(d: dict) -> dict:
    object_value(d)
    canonical(d)
    required(d, REQUIRED)
    gr, gi = q(d["g_re"]), q(d["g_im"])
    y = bounded(gr * gr + gi * gi)
    rs = {k: q(d[k]) for k in REQUIRED[2:]}
    if any(v < 0 for v in rs.values()):
        raise ValueError("residuals must be nonnegative")
    analytic = polynomial_check(d.get("analytic_witness"), gr, gi)
    risk = risk_check(d.get("risk_witness"))
    zero = y == 0
    claims_zero = all(v == 0 for v in rs.values())
    verified = analytic is True and risk is not None and risk["verified"]
    accepted = zero and claims_zero and verified
    contradiction = analytic is False or (risk is not None and not risk["verified"])
    decision = "CERTIFIED_MODEL_CANDIDATE" if accepted else (
        "HOLD" if not zero or not claims_zero or contradiction else "UNDETERMINED")
    probability = 1.0 if zero else (0.0 if y >= 746 else math.exp(-float(y)))
    if not zero and probability == 1.0:
        probability = math.nextafter(1.0, 0.0)
    out = {"protocol": PROTOCOL, "g": {"re": str(gr), "im": str(gi)},
           "y_abs_g_sq": str(y), "formal_probability": probability,
           "formal_probability_is_approximate": not zero, "formal_probability_one": zero,
           "submitted_residuals_zero": claims_zero,
           "continuation_zero": analytic, "risk_zero": None if risk is None else risk["verified"],
           "certificate_zero": verified, "witnesses_verified": verified,
           "admissible_candidate": accepted, "decision": decision,
           "analytic_scope": "polynomial identity and exact evaluation on C only",
           "risk_verification": risk, "order_execution": False,
           "real_world_profit_guaranteed": False, "real_world_trade_authorized": False,
           "general_maximal_continuation_implemented": False}
    return attach_receipt(d, out)


def transition(d: dict) -> dict:
    object_value(d)
    canonical(d)
    fields = ("invariant_before", "guard_passed", "transition_preserves_invariant")
    required(d, fields)
    if any(type(d[k]) is not bool for k in fields):
        raise ValueError("transition flags must be JSON booleans")
    risk = risk_check(d.get("risk_witness"))
    verified = risk is not None and risk["verified"]
    claims_match = risk is not None and all(d[k] == risk[k] for k in fields)
    accepted = verified and claims_match and all(d[k] for k in fields)
    out = {"protocol": PROTOCOL, **{k: d[k] for k in fields},
           "claims_only_conjunction": all(d[k] for k in fields),
           "invariant_after_certified": accepted, "risk_verification": risk,
           "decision": "CERTIFIED_MODEL_TRANSITION" if accepted else (
               "UNDETERMINED" if risk is None and all(d[k] for k in fields) else "HOLD"),
           "order_execution": False, "profit_guaranteed": False,
           "real_world_trade_authorized": False}
    return attach_receipt(d, out)


def encode_payload(x: Any) -> dict:
    s = canonical(x)
    g = encode_text(s)
    return {"protocol": PROTOCOL, "operation": "godel-encode", "godel": str(g),
            "roundtrip": decode_text(g) == s, "certificate": cert(x)}


def manifest() -> dict:
    return {"protocol": PROTOCOL, "required_evaluate_fields": list(REQUIRED),
            "endpoints": ["/health", "/manifest", "/evaluate", "/transition", "/encode"],
            "boundaries": {"verification_only": True, "places_orders": False,
                           "real_world_profit_guarantee": False, "probability_one_is_formal": True,
                           "unsupported_general_maximal_continuation_is_not_inferred": True,
                           "general_maximal_continuation_implemented": False,
                           "missing_witnesses_are_uncertified": True,
                           "receipts_are_not_authenticated": True},
            "supported_evidence": ["polynomial identity and exact zero evaluation",
                                   "provided long-only simulation state transition"],
            "limits": {"request_bytes": MAX_JSON_BYTES, "codec_bytes": MAX_CODEC_BYTES,
                       "scalar_bits": 256, "arithmetic_bits": 2048, "polynomial_coefficients": 32}}
