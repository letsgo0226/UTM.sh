"""Bounded virtual-deployment UTM: one logical scheduler, no platform mutations.

Every job is a BF8 program, addressed by reversible G257/ATGC representations.
All work is bounded by explicit per-job/global limits. A bounded result does NOT
establish non-halting, and no proof here grants GitHub/Railway privileges.
"""
import hashlib
import json
import sys
from pathlib import Path
from resource_guard import g257, decode257, atgc, decode_atgc

ROOT = Path(__file__).resolve().parent
COMMANDS = "<>+-.,[]"

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()

def compile_job(raw, cap):
    if set(raw) - set(COMMANDS) or len(raw) > cap:
        raise ValueError("invalid program or overlong program")
    jump, stack = {}, []
    for i, op in enumerate(raw):
        if op == "[":
            stack.append(i)
        elif op == "]":
            if not stack:
                raise ValueError("unbalanced brackets")
            j = stack.pop()
            jump[i] = j
            jump[j] = i
    if stack:
        raise ValueError("unbalanced brackets")
    return jump

def simulate(spec):
    assert spec.get("schema") == "Everlife-Unified-Virtual-Deployment/1.0"
    limits = spec["limits"]
    step_limit, global_limit, tape_limit, output_limit, program_limit = (
        limits[k] for k in ("steps_per_job", "global_steps", "tape_cells", "output_bytes", "program_bytes"))
    if not (all(type(i) is int for i in (step_limit, global_limit, tape_limit, output_limit, program_limit))
            and 1 <= step_limit <= 10000 and 1 <= global_limit <= 100000
            and 1 <= tape_limit <= 4096 and 1 <= output_limit <= 8192
            and 1 <= program_limit <= 2048):
        raise ValueError("invalid resource envelope")
    jobs = spec["virtual_services"]
    if not 1 <= len(jobs) <= 32:
        raise ValueError("bounded catalog requires 1..32 jobs")
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate virtual service ID")
    states = []
    for job in sorted(jobs, key=lambda j: j["id"]):
        if any(k not in ("id", "domain", "program", "external_apply_enabled") for k in job):
            raise ValueError("unknown job keys")
        if job.get("external_apply_enabled") is not False:
            raise ValueError("all external actions must be disabled")
        if not isinstance(job["id"], str) or not job["id"].isascii() or not job["id"].replace("-", "").isalnum():
            raise ValueError("invalid job id")
        code = job["program"]
        jump = compile_job(code, program_limit)
        b = code.encode()
        if decode257(g257(b)) != b or decode_atgc(atgc(b)) != b:
            raise ValueError("reversible encoding failed")
        states.append({"id": job["id"], "domain": job["domain"], "program": code,
                       "jump": jump, "pc": 0, "head": 0, "tape": [0]*tape_limit,
                       "output": [], "steps": 0, "status": "READY", "g257":hex(g257(b)),
                       "atgc_sha256": hashlib.sha256(atgc(b).encode()).hexdigest(),
                       "code_sha256": hashlib.sha256(b).hexdigest()})
    initial_sha = hashlib.sha256(canonical({"schema":spec["schema"], "limits":limits,
                 "services": [{"id":j["id"],"program_sha256":j["code_sha256"]} for j in states]})).hexdigest()
    chain = initial_sha
    events = []
    total = 0
    while total < global_limit and any(s["status"] == "READY" for s in states):
        for s in states:
            if s["status"] != "READY" or total >= global_limit:
                continue
            code = s["program"]
            if s["pc"] >= len(code):
                s["status"] = "HALTED"
                continue
            op = code[s["pc"]]
            value = s["tape"][s["head"]]
            if op == ">": s["head"] += 1
            elif op == "<": s["head"] -= 1
            elif op == "+": s["tape"][s["head"]] = (value+1)%256
            elif op == "-": s["tape"][s["head"]] = (value-1)%256
            elif op == ",":
                s["tape"][s["head"]] = 0
            elif op == ".":
                if len(s["output"]) >= output_limit:
                    s["status"] = "BOUNDED_OUTPUT"
                else: s["output"].append(value)
            elif op == "[" and value == 0: s["pc"] = s["jump"][s["pc"]]
            elif op == "]" and value != 0: s["pc"] = s["jump"][s["pc"]]
            s["pc"] += 1
            s["steps"] += 1
            total += 1
            if s["head"] < 0 or s["head"] >= tape_limit:
                s["status"] = "BOUNDED_TAPE"
            elif s["pc"] >= len(code):
                s["status"] = "HALTED"
            elif s["steps"] >= step_limit and s["status"] == "READY":
                s["status"] = "BOUNDED_STEPS"
            e = {"clock":total, "id":s["id"], "pc":s["pc"],
                 "status":s["status"],"head":s["head"],"steps":s["steps"]}
            chain = hashlib.sha256(bytes.fromhex(chain)+canonical(e)).hexdigest()
            events.append(e)
    for s in states:
        if s["status"] == "READY":
            s["status"] = "BOUNDED_GLOBAL"
    return {
        "schema": "Everlife-Unified-Run/1.0",
        "evidence": "formal-bounded-only",
        "real_time_synchronization": False,
        "synchronization": "deterministic logical-clock round-robin (offline)",
        "deployments_triggered": 0,
        "unlimited_compute_or_storage": False,
        "universal_halting_decidable": False,
        "input_sha256": hashlib.sha256(canonical(spec)).hexdigest(),
        "chain_genesis_sha256": initial_sha,
        "chain_final_sha256": chain,
        "total_steps": total,
        "events_count":len(events),
        "services": [{k:s[k] for k in ("id","domain","status","steps","g257",
                     "atgc_sha256","code_sha256")} | {"output_hex":bytes(s["output"]).hex()}
                     for s in states]
    }

if __name__ == "__main__":
    file = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"unified_registry.json"
    result = simulate(json.loads(file.read_text(encoding="utf-8")))
    target = ROOT/"public"/"unified-run.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
