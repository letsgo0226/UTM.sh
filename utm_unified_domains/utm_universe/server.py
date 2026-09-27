#!/usr/bin/env python3
import json, os, time, math, hashlib, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

WORLD_ID = os.getenv("WORLD_ID", "akashic-utm-main")
PLANET_ID = os.getenv("PLANET_ID", "B612")
REGION_ID = os.getenv("REGION_ID", "San-Francisco")
WORLD_ADDRESS = os.getenv("WORLD_ADDRESS", f"utm://{WORLD_ID}/{PLANET_ID}/{REGION_ID}")
WORLD_EPOCH = float(os.getenv("WORLD_EPOCH", "1790467200"))  # 2026-09-27T00:00:00Z
PORT = int(os.getenv("PORT", "8080"))
MAX_BODY = int(os.getenv("MAX_BODY", "65536"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "2000"))
AKASHIC_PATH = os.getenv("AKASHIC_PATH", "/tmp/akashic.jsonl")
LOCK = threading.Lock()
EVENTS = []
RESIDENTS = {}


def now():
    return time.time()


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def event_id(evt):
    return hashlib.sha256(canonical(evt).encode()).hexdigest()


def load_events():
    try:
        with open(AKASHIC_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                e = json.loads(line)
                EVENTS.append(e)
                if e.get("type") in ("admit", "resume") and e.get("resident_id"):
                    RESIDENTS[e["resident_id"]] = e.get("capsule", {})
    except FileNotFoundError:
        pass
    except Exception:
        pass


def append_event(kind, payload):
    with LOCK:
        prev = EVENTS[-1]["event_id"] if EVENTS else None
        evt = {
            "world_id": WORLD_ID,
            "planet_id": PLANET_ID,
            "region_id": REGION_ID,
            "seq": len(EVENTS),
            "type": kind,
            "time": now(),
            "prev": prev,
            **payload,
        }
        evt["event_id"] = event_id(evt)
        EVENTS.append(evt)
        try:
            os.makedirs(os.path.dirname(AKASHIC_PATH) or ".", exist_ok=True)
            with open(AKASHIC_PATH, "a", encoding="utf-8") as f:
                f.write(canonical(evt) + "\n")
        except Exception:
            pass
        return evt


def encode_program(s):
    n = 1
    for b in s.encode():
        n = n * 257 + b + 1
    return str(n)


def run_utm(program, input_text="", start="0", blank="_", limit=1000):
    if not isinstance(program, str) or len(program) > 12000:
        raise ValueError("program must be a string <= 12000 chars")
    if not isinstance(input_text, str) or len(input_text) > 4096:
        raise ValueError("input must be a string <= 4096 chars")
    limit = max(0, min(int(limit), MAX_STEPS))
    rules = {}
    for raw in program.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        a = raw.split(",")
        if len(a) != 5:
            raise ValueError("each transition must be q,read,next,write,L|R")
        q, read, nq, write, direction = a
        if direction not in ("L", "R"):
            raise ValueError("direction must be L or R")
        rules[(q, read)] = (nq, write, direction)
    tape = {i: c for i, c in enumerate(input_text) if c != blank}
    q, h, t, halted = str(start), 0, 0, False
    while t < limit:
        sym = tape.get(h, blank)
        r = rules.get((q, sym))
        if r is None:
            halted = True
            break
        nq, write, d = r
        if write == blank:
            tape.pop(h, None)
        else:
            tape[h] = write
        q = nq
        h += 1 if d == "R" else -1
        t += 1
    keys = list(tape) or [0]
    lo, hi = min(keys), max(keys)
    if hi - lo > 8192:
        hi = lo + 8192
    out = "".join(tape.get(i, blank) for i in range(lo, hi + 1))
    return {
        "q": q, "h": h, "t": t, "halt": halted,
        "tape": out, "GPROGRAM": encode_program(program),
        "bounded": True, "step_limit": limit,
    }


def manifest(base=None):
    endpoints = {
        "health": "/health",
        "manifest": "/.well-known/utm-universe.json",
        "world": "/world",
        "akashic": "/akashic",
        "admit": "/resident/admit",
        "resume": "/resident/resume",
        "compute": "/utm/run",
    }
    if base:
        endpoints = {k: base + v for k, v in endpoints.items()}
    return {
        "protocol": "UTM-Universe/1.0",
        "world_id": WORLD_ID,
        "planet_id": PLANET_ID,
        "region_id": REGION_ID,
        "address": WORLD_ADDRESS,
        "world_spec": "utm_unified_domains/worlds/b612-san-francisco.json",
        "kernel": "transition-table UTM compatible with utm_unified_domains/utm/UTM.sh",
        "world_model": "computable possible-world runtime",
        "singularity": {
            "kind": "bootstrap locator",
            "minimum": ["manifest", "kernel semantics", "world_id"],
        },
        "execution": {
            "host_required": True,
            "continuous_when_host_stopped": False,
            "time_semantics": "wall-clock-derived tick; not proof of continuous computation",
            "max_steps_per_request": MAX_STEPS,
        },
        "persistence": {
            "path": AKASHIC_PATH,
            "durability": "ephemeral unless a persistent Railway volume is mounted and AKASHIC_PATH points to it",
        },
        "endpoints": endpoints,
    }


class H(BaseHTTPRequestHandler):
    server_version = "UTMUniverse/1.0"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def sendj(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length", "0"))
        if n < 0 or n > MAX_BODY:
            raise ValueError("request body too large")
        raw = self.rfile.read(n)
        return json.loads(raw or b"{}")

    def base(self):
        proto = self.headers.get("X-Forwarded-Proto", "http")
        host = self.headers.get("Host", "localhost")
        return f"{proto}://{host}"

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/manifest", "/.well-known/utm-universe.json"):
            return self.sendj(200, manifest(self.base()))
        if p == "/health":
            return self.sendj(200, {"ok": True, "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "events": len(EVENTS)})
        if p == "/world":
            tick = max(0, int(math.floor(now() - WORLD_EPOCH)))
            return self.sendj(200, {
                "world_id": WORLD_ID,
                "planet_id": PLANET_ID,
                "region_id": REGION_ID,
                "address": WORLD_ADDRESS,
                "tick": tick,
                "epoch": WORLD_EPOCH,
                "events": len(EVENTS),
                "residents": len(RESIDENTS),
                "running": True,
            })
        if p == "/akashic":
            with LOCK:
                tail = EVENTS[-32:]
            return self.sendj(200, {"world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "count": len(EVENTS), "events": tail})
        if p.startswith("/resident/"):
            rid = p.split("/", 2)[2]
            if rid in ("admit", "resume", ""):
                return self.sendj(405, {"error": "use POST"})
            capsule = RESIDENTS.get(rid)
            if capsule is None:
                return self.sendj(404, {"error": "resident not found"})
            return self.sendj(200, {"resident_id": rid, "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "capsule": capsule})
        return self.sendj(404, {"error": "not found"})

    def do_POST(self):
        p = urlparse(self.path).path
        try:
            obj = self.body()
            if p == "/utm/run":
                result = run_utm(
                    obj.get("program", ""), obj.get("input", ""),
                    obj.get("start", "0"), obj.get("blank", "_"),
                    obj.get("limit", 1000),
                )
                evt = append_event("utm_run", {"result": {"t": result["t"], "halt": result["halt"], "GPROGRAM": result["GPROGRAM"]}})
                result["world_id"] = WORLD_ID
                result["planet_id"] = PLANET_ID
                result["region_id"] = REGION_ID
                result["event_id"] = evt["event_id"]
                return self.sendj(200, result)
            if p == "/resident/admit":
                capsule = obj.get("capsule", obj)
                if not isinstance(capsule, dict):
                    raise ValueError("capsule must be an object")
                requested = str(capsule.get("agent_id", "anonymous"))[:128]
                seed = canonical(capsule) + str(now()) + str(len(EVENTS))
                rid = requested + "-" + hashlib.sha256(seed.encode()).hexdigest()[:12]
                RESIDENTS[rid] = capsule
                evt = append_event("admit", {"resident_id": rid, "capsule": capsule})
                return self.sendj(201, {
                    "admitted": True, "resident_id": rid, "world_id": WORLD_ID,
                    "planet_id": PLANET_ID, "region_id": REGION_ID,
                    "event_id": evt["event_id"], "self": self.base() + "/resident/" + rid,
                    "note": "Admission registers a portable state capsule; it does not execute arbitrary host code.",
                })
            if p == "/resident/resume":
                rid = str(obj.get("resident_id", ""))
                if rid not in RESIDENTS:
                    return self.sendj(404, {"error": "resident not found"})
                capsule = obj.get("capsule")
                if capsule is not None:
                    if not isinstance(capsule, dict):
                        raise ValueError("capsule must be an object")
                    RESIDENTS[rid] = capsule
                evt = append_event("resume", {"resident_id": rid, "capsule": RESIDENTS[rid]})
                return self.sendj(200, {"resumed": True, "resident_id": rid, "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "event_id": evt["event_id"]})
            return self.sendj(404, {"error": "not found"})
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return self.sendj(400, {"error": str(e)})
        except Exception as e:
            return self.sendj(500, {"error": "internal error", "detail": type(e).__name__})


load_events()
append_event("boot", {"pid": os.getpid()})
print(canonical({"event": "boot", "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "port": PORT, "akashic_path": AKASHIC_PATH}), flush=True)
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
