"""Everlife Open deployment resource gate: finite, read-only, fail-closed.

This is a DECLARED BUDGET preflight, not a measurement, scheduler, platform
quota bypass, general halting decision procedure, or deployment authorization.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_POLICY = HERE / "resource_budget.json"


def g257(data):
    result = 1
    for octet in data:
        result = 257 * result + octet + 1
    return result


def decode257(number):
    if number < 1:
        raise ValueError("invalid G257")
    out = []
    while number > 1:
        number, digit = divmod(number, 257)
        if digit == 0:
            raise ValueError("invalid digit")
        out.append(digit - 1)
    return bytes(reversed(out))


def atgc(data):
    return "".join("TC" if byte & (1 << bit) else "AG"
                   for byte in data for bit in range(7, -1, -1))


def decode_atgc(value):
    if len(value) % 16 or any(value[i:i+2] not in ("AG", "TC")
                              for i in range(0, len(value), 2)):
        raise ValueError("invalid ATGC")
    return bytes(int("".join("1" if value[j:j+2] == "TC" else "0"
                             for j in range(i, i+16, 2)), 2)
                 for i in range(0, len(value), 16))


def bounded_vm(program, *, steps=10000, cells=4096, output=8192):
    """A bounded BF runner with explicit observable BLOCKED/BOUNDED/HALTED."""
    if any(ch not in "<>+-.,[]" for ch in program):
        return {"status": "REJECTED", "reason": "non-BF instruction"}
    if len(program.encode()) > 2048 or not (0 < steps <= 100000
                                           and 0 < cells <= 65536
                                           and 0 < output <= 65536):
        return {"status": "REJECTED", "reason": "resource bounds"}
    brackets, stack = {}, []
    for pos, op in enumerate(program):
        if op == "[":
            stack.append(pos)
        elif op == "]":
            if not stack:
                return {"status": "REJECTED", "reason": "unmatched bracket"}
            other = stack.pop()
            brackets[other] = pos
            brackets[pos] = other
    if stack:
        return {"status": "REJECTED", "reason": "unmatched bracket"}
    tape = [0] * cells
    head = ip = ticks = 0
    emitted = []
    while ip < len(program) and ticks < steps:
        op = program[ip]
        if op == ">":
            head += 1
        elif op == "<":
            head -= 1
        elif op == "+":
            tape[head] = (tape[head] + 1) % 256
        elif op == "-":
            tape[head] = (tape[head] - 1) % 256
        elif op == ".":
            if len(emitted) >= output:
                return {"status": "BOUNDED", "reason": "output_limit", "steps": ticks}
            emitted.append(tape[head])
        elif op == ",":
            tape[head] = 0
        elif op == "[" and tape[head] == 0:
            ip = brackets[ip]
        elif op == "]" and tape[head] != 0:
            ip = brackets[ip]
        if head < 0 or head >= cells:
            return {"status": "BOUNDED", "reason": "tape_limit", "steps": ticks+1}
        ip += 1
        ticks += 1
    return {"status": "HALTED" if ip == len(program) else "BOUNDED",
            "reason": "end_of_program" if ip == len(program) else "step_limit",
            "steps": ticks, "output_hex": bytes(emitted).hex()}


def check(policy):
    problems = []
    review = []
    for key in ("build_context_bytes", "runtime_memory_mb", "persistent_volume_mb"):
        estimate = policy.get("declared_estimate", {}).get(key)
        limit = policy.get("declared_ceiling", {}).get(key)
        if limit is None or estimate is None:
            review.append(key + ": missing measured estimate or applicable plan ceiling")
        elif not isinstance(estimate, (int, float)) or not isinstance(limit, (int, float)) or estimate < 0 or limit <= 0:
            problems.append(key + ": invalid nonnegative estimates/positive ceiling")
        elif estimate > limit:
            problems.append(key + ": exceeds declared ceiling")
    sample = "+."
    roundtrip = decode257(g257(sample)) == sample and decode_atgc(atgc(sample)) == sample
    vm = bounded_vm(sample)
    if not roundtrip or vm.get("status") != "HALTED" or vm.get("output_hex") != "01":
        problems.append("formal self-test failed")
    return {
        "protocol": "Everlife-Finite-Resource-Preflight/1.0",
        "result": "BLOCK" if problems else ("REVIEW_REQUIRED" if review else "PREFLIGHT_PASS"),
        "disclaimer": "Declared estimates are not physical measurements, successful deployment, or platform authorization.",
        "formal": {"g257_atgc_roundtrip": roundtrip,
                   "bounded_vm": vm,
                   "universal_halting_solved": False,
                   "infinite_resource_created": False},
        "hard_failures": problems,
        "requires_review": review,
        "scope": "read-only; no credentials, shell execution, deployment, or trading",
        "policy_sha256": hashlib.sha256(
            json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--policy", default=str(DEFAULT_POLICY))
    p.add_argument("--output", default="")
    a = p.parse_args()
    policy = json.loads(Path(a.policy).read_text(encoding="utf-8"))
    result = check(policy)
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if a.output:
        Path(a.output).write_text(payload, encoding="utf-8")
    print(payload, end="")
    raise SystemExit(2 if result["result"] == "BLOCK" else
                     3 if result["result"] == "REVIEW_REQUIRED" else 0)
