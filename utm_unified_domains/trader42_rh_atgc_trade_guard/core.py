from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation

PROTOCOL = "Trader-42-RH-ATGC-TradeGuard/1.0"
ALPHABET = "ATGC"


def _d(value) -> Decimal:
    try:
        x = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"invalid decimal: {value!r}") from exc
    if not x.is_finite():
        raise ValueError("non-finite decimal")
    return x


def canonical_body(candidate: dict, critical_gc: int) -> dict:
    if critical_gc <= 0:
        raise ValueError("critical_gc must be positive")
    t = dict(candidate.get("transition") or {})
    k = dict(candidate.get("kernel") or {})
    r = dict(candidate.get("risk") or {})
    return {
        "protocol": PROTOCOL,
        "critical_gc": int(critical_gc),
        "transition": {
            "transition_id": str(t.get("transition_id", "")),
            "tm_n": int(t.get("tm_n", 0)),
            "market": int(t.get("market", 0)),
            "requested_operation": str(t.get("requested_operation", "HOLD")).upper(),
            "from_state": str(t.get("from_state", "")),
            "target_state": str(t.get("target_state", "")),
            "quote": str(t.get("quote", "0")),
            "hard_cap": str(t.get("hard_cap", "0")),
            "volatility_factor": str(t.get("volatility_factor", "1")),
        },
        "kernel": {
            "C": k.get("C"),
            "CF": k.get("CF"),
        },
        "risk": {
            "kill_active": bool(r.get("kill_active", False)),
        },
    }


def encode_atgc(body: dict, critical_gc: int) -> tuple[str, int, int]:
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    bits = "".join(f"{b:08b}" for b in raw)
    payload = "".join("T" if bit == "1" else "A" for bit in bits)
    word = ("G" * critical_gc) + payload
    uid = 1
    for ch in word:
        uid = uid * 4 + ALPHABET.index(ch)
    gc = sum(ch in "GC" for ch in word)
    return word, uid, gc


def verify_atgc(body: dict, word: str, critical_gc: int) -> dict:
    expected, uid, gc = encode_atgc(body, critical_gc)
    exact = word == expected
    return {
        "exact": exact,
        "gc": sum(ch in "GC" for ch in word),
        "critical_gc": critical_gc,
        "critical": exact and gc == critical_gc,
        "uid": str(uid) if exact else None,
    }


def _operation_ok(t: dict) -> bool:
    op = t["requested_operation"]
    src = t["from_state"]
    dst = t["target_state"]
    if op == "BUY":
        return src == "FLAT" and dst == "LONG"
    if op == "SELL":
        return src == "LONG" and dst == "FLAT"
    if op == "HOLD":
        return src == dst
    return False


def evaluate(candidate: dict, critical_gc: int = 15) -> dict:
    body = canonical_body(candidate, critical_gc)
    t = body["transition"]
    k = body["kernel"]
    r = body["risk"]

    quote = _d(t["quote"])
    hard_cap = _d(t["hard_cap"])
    alpha = _d(t["volatility_factor"])

    kernel_ok = (k["C"] is True and k["CF"] is not False)
    operation_ok = _operation_ok(t)
    sizing_ok = (
        quote >= 0 and hard_cap >= 0 and quote <= hard_cap
        and Decimal(0) <= alpha <= Decimal(1)
    )
    kill_ok = not r["kill_active"]

    word, uid, gc = encode_atgc(body, critical_gc)
    critical_ok = gc == critical_gc
    allowed = bool(kernel_ok and operation_ok and sizing_ok and kill_ok and critical_ok)

    requested = t["requested_operation"]
    effective = requested if allowed else "HOLD"
    if requested == "HOLD" and allowed:
        effective = "HOLD"

    return {
        "protocol": PROTOCOL,
        "candidate_only": True,
        "live_execution": False,
        "critical_gc": critical_gc,
        "sigma": [gc, 2 * critical_gc],
        "critical": critical_ok,
        "certificate": {
            "atgc": word,
            "uid": str(uid),
            "gc": gc,
            "identity_injective_for_canonical_body": True,
        },
        "checks": {
            "kernel_ok": kernel_ok,
            "operation_ok": operation_ok,
            "sizing_decrease_only": sizing_ok,
            "kill_clear": kill_ok,
            "critical_gc_ok": critical_ok,
        },
        "requested_operation": requested,
        "effective_operation": effective,
        "allowed_candidate": allowed,
        "reason": "ok" if allowed else "fail-closed-to-HOLD",
        "claims": {
            "rh_proved": 0,
            "zeta_zero_test": 0,
            "profitability_guarantee": 0,
            "exchange_order_execution": 0,
        },
    }


def verify_certificate(candidate: dict, word: str, critical_gc: int = 15) -> dict:
    body = canonical_body(candidate, critical_gc)
    out = verify_atgc(body, word, critical_gc)
    return {
        "protocol": PROTOCOL,
        "live_execution": False,
        **out,
    }


def selftest() -> dict:
    safe = {
        "transition": {
            "transition_id": "tm-1-1",
            "tm_n": 1,
            "market": 1,
            "requested_operation": "BUY",
            "from_state": "FLAT",
            "target_state": "LONG",
            "quote": "5",
            "hard_cap": "10",
            "volatility_factor": "0.5",
        },
        "kernel": {"C": True, "CF": None},
        "risk": {"kill_active": False},
    }
    a = evaluate(safe, 15)
    over = json.loads(json.dumps(safe))
    over["transition"]["quote"] = "11"
    b = evaluate(over, 15)
    killed = json.loads(json.dumps(safe))
    killed["risk"]["kill_active"] = True
    c = evaluate(killed, 15)
    v = verify_certificate(safe, a["certificate"]["atgc"], 15)
    tampered = a["certificate"]["atgc"][:-1] + ("A" if a["certificate"]["atgc"][-1] != "A" else "T")
    vt = verify_certificate(safe, tampered, 15)
    ok = (
        a["allowed_candidate"] is True
        and a["certificate"]["gc"] == 15
        and b["allowed_candidate"] is False
        and c["allowed_candidate"] is False
        and v["critical"] is True
        and vt["critical"] is False
    )
    return {
        "ok": ok,
        "safe_buy": a,
        "over_cap_effective": b["effective_operation"],
        "kill_effective": c["effective_operation"],
        "certificate_roundtrip": v,
        "tamper_rejected": not vt["critical"],
    }
