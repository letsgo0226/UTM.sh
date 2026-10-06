#!/usr/bin/env python3
import json, os, time, math, hashlib, hmac, threading, urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from compute_fabric import Fabric

WORLD_ID = os.getenv("WORLD_ID", "akashic-utm-main")
PLANET_ID = os.getenv("PLANET_ID", "B612")
REGION_ID = os.getenv("REGION_ID", "San-Francisco")
WORLD_ADDRESS = os.getenv("WORLD_ADDRESS", f"utm://{WORLD_ID}/{PLANET_ID}/{REGION_ID}")
WORLD_EPOCH = float(os.getenv("WORLD_EPOCH", "1790467200"))  # 2026-09-27T00:00:00Z
PORT = int(os.getenv("PORT", "8080"))
MAX_BODY = int(os.getenv("MAX_BODY", "65536"))
MAX_STEPS = int(os.getenv("MAX_STEPS", "2000"))
AKASHIC_PATH = os.getenv("AKASHIC_PATH", "/tmp/akashic.jsonl")
FABRIC_PATH = os.getenv("FABRIC_PATH", os.path.join(os.path.dirname(AKASHIC_PATH) or "/tmp", "compute-fabric.json"))
NODE_ID = os.getenv("NODE_ID", os.getenv("RAILWAY_SERVICE_NAME", "utm-node"))
FEDERATION_TOKEN = os.getenv("FEDERATION_TOKEN", "")
UTM_ACCESS_TOKEN = os.getenv("UTM_ACCESS_TOKEN", FEDERATION_TOKEN)
FEDERATION_PEERS = [x.rstrip("/") for x in os.getenv("FEDERATION_PEERS", "").split(",") if x.strip()]
FEDERATION_INTERVAL = max(5, int(os.getenv("FEDERATION_INTERVAL", "30")))
FIELD_SEED_ONE_LINER_URL = os.getenv("FIELD_SEED_ONE_LINER_URL", "https://raw.githubusercontent.com/letsgo0226/UTM.sh/main/utm_unified_domains/utm_universe/protocols/UTM-FIELD-NODE-BOOTSTRAP-1.0.one-liner.sh")
FIELD_SEED_MANIFEST_URL = os.getenv("FIELD_SEED_MANIFEST_URL", "https://raw.githubusercontent.com/letsgo0226/UTM.sh/main/utm_unified_domains/utm_universe/protocols/UTM-FIELD-NODE-BOOTSTRAP-1.0.json")
UTM_SEED_ONE_LINER_URL = os.getenv("UTM_SEED_ONE_LINER_URL", "https://raw.githubusercontent.com/letsgo0226/UTM.sh/main/utm_unified_domains/utm_universe/protocols/UTM-SEED-ONE-LINER-1.1.one-liner.sh")
UTM_SEED_MANIFEST_URL = os.getenv("UTM_SEED_MANIFEST_URL", "https://raw.githubusercontent.com/letsgo0226/UTM.sh/main/utm_unified_domains/utm_universe/protocols/UTM-SEED-ONE-LINER-1.1.json")
UTM_SEED_PROTOCOL = "UTM-SEED-ONE-LINER/1.1"
LOCK = threading.RLock()
EVENTS = []
RESIDENTS = {}
RESIDENT_META = {}
SYNC_STATE = {"last_attempt": None, "last_success": None, "last_error": None, "last_peer": None}
FABRIC = Fabric(WORLD_ID, NODE_ID, FABRIC_PATH, MAX_STEPS)


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
                if e.get("type") in ("admit", "resume", "federation_resident") and e.get("resident_id"):
                    rid=e["resident_id"]
                    RESIDENTS[rid] = e.get("capsule", {})
                    RESIDENT_META[rid] = {
                        "version": int(e.get("resident_version", 1)),
                        "updated_at": float(e.get("time", 0)),
                        "owner_node": str(e.get("owner_node", e.get("node_id", "legacy"))),
                    }
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
            "node_id": NODE_ID,
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


def federation_authorized(headers):
    if not FEDERATION_TOKEN:
        return False
    return hmac.compare_digest(headers.get("Authorization", ""), "Bearer " + FEDERATION_TOKEN)


def node_authorized(headers):
    if not UTM_ACCESS_TOKEN:
        return False
    supplied = headers.get("Authorization", "").encode("utf-8")
    return hmac.compare_digest(supplied, ("Bearer " + UTM_ACCESS_TOKEN).encode("utf-8"))


def private_route(path, method):
    return (path == "/akashic" or path == "/resident" or path.startswith("/resident/")
            or path == "/compute/jobs" or path.startswith("/compute/jobs/")
            or (method == "POST" and path == "/utm/run"))


def _resident_rank(meta):
    return (int(meta.get("version",0)), float(meta.get("updated_at",0)), str(meta.get("owner_node","")))


def federation_snapshot():
    with LOCK:
        residents=[
            {"resident_id":rid,"capsule":RESIDENTS[rid],"meta":dict(RESIDENT_META.get(rid,{}))}
            for rid in sorted(RESIDENTS)
        ]
    x={
        "protocol":"UTM-Federation-Snapshot/1.0",
        "world_id":WORLD_ID,
        "node_id":NODE_ID,
        "generated_at":now(),
        "residents":residents,
        "jobs":FABRIC.export_jobs(),
    }
    x["digest"]=hashlib.sha256(canonical(x).encode()).hexdigest()
    return x


def merge_federation_snapshot(x):
    if not isinstance(x,dict) or x.get("protocol")!="UTM-Federation-Snapshot/1.0" or x.get("world_id")!=WORLD_ID:
        raise ValueError("invalid federation snapshot")
    changed_residents=0
    for item in x.get("residents",[]):
        if not isinstance(item,dict):
            continue
        rid=str(item.get("resident_id",""))
        capsule=item.get("capsule")
        meta=item.get("meta") or {}
        if not rid or not isinstance(capsule,dict):
            continue
        incoming={"version":int(meta.get("version",0)),"updated_at":float(meta.get("updated_at",0)),"owner_node":str(meta.get("owner_node",""))}
        current=RESIDENT_META.get(rid,{})
        if rid not in RESIDENTS or _resident_rank(incoming)>_resident_rank(current):
            RESIDENTS[rid]=capsule
            RESIDENT_META[rid]=incoming
            append_event("federation_resident",{
                "resident_id":rid,"capsule":capsule,
                "resident_version":incoming["version"],"owner_node":incoming["owner_node"],
                "source_node":x.get("node_id"),
            })
            changed_residents+=1
    changed_jobs=FABRIC.merge_jobs(x.get("jobs",[]))
    return {"residents":changed_residents,"jobs":changed_jobs}


def sync_peer(peer):
    SYNC_STATE["last_attempt"]=now()
    SYNC_STATE["last_peer"]=peer
    try:
        req=urllib.request.Request(peer+"/federation/snapshot",headers={"Authorization":"Bearer "+FEDERATION_TOKEN})
        with urllib.request.urlopen(req,timeout=8) as r:
            raw=r.read(2_000_000)
        x=json.loads(raw)
        changed=merge_federation_snapshot(x)
        SYNC_STATE["last_success"]=now()
        SYNC_STATE["last_error"]=None
        if changed["residents"] or changed["jobs"]:
            append_event("federation_sync",{"peer":peer,"changed":changed})
        return {"ok":True,"peer":peer,"changed":changed}
    except Exception as e:
        SYNC_STATE["last_error"]=type(e).__name__
        return {"ok":False,"peer":peer,"error":type(e).__name__}


def sync_all_peers():
    if not FEDERATION_TOKEN:
        return []
    return [sync_peer(p) for p in FEDERATION_PEERS]


def federation_loop():
    while True:
        time.sleep(FEDERATION_INTERVAL)
        sync_all_peers()


def field_seed(base=None):
    return {
        "protocol":"UTM-FIELD-SEED/1.0",
        "world_id":WORLD_ID,
        "node_id":NODE_ID,
        "public_bootstrap":True,
        "bootstrap_one_liner_url":FIELD_SEED_ONE_LINER_URL,
        "bootstrap_manifest_url":FIELD_SEED_MANIFEST_URL,
        "bootstrap_discovery":(base+"/field/bootstrap") if base else "/field/bootstrap",
        "utm_seed_discovery":(base+"/.well-known/utm-seed.json") if base else "/.well-known/utm-seed.json",
        "requirements":["python3","outbound HTTPS","permission to execute a long-running process"],
        "generated_node_capabilities":["resident admission/resume","bounded resident UTM compute","checkpointing","federation client/server","takeover/continuation"],
        "trust_model":{
            "standalone_node_generation_requires_secret":False,
            "existing_federation_membership_requires_secret":True,
            "federation_secret_name":"FEDERATION_TOKEN",
            "federation_secret_disclosed_here":False,
        },
        "safety":{
            "arbitrary_resident_host_code":False,
            "all_hosts_stopped_means":"computation stops",
            "actual_infinite_physical_compute":False,
            "oracle":None,
            "hypercomputation_enabled":False,
        },
    }


def utm_seed(base=None):
    return {
        "protocol":UTM_SEED_PROTOCOL,
        "world_id":WORLD_ID,
        "node_id":NODE_ID,
        "one_liner":(base+"/utm/seed") if base else "/utm/seed",
        "manifest_url":UTM_SEED_MANIFEST_URL,
        "machine_model":"deterministic single-tape Turing-machine interpreter over an arbitrary finite transition table",
        "rules_env":"TM_RULES",
        "input_env":"TM_INPUT",
        "limit_env":"TM_LIMIT",
        "certificate_mode":"TM_MODE=cert",
        "default_finite_derivation":"AAAAA -> FIELD in five transitions",
        "effect_gate":"a halted TM with the exact FIELD output enables the built-in field-node bootstrap",
        "runtime_source_commit":os.getenv("UTM_RUNTIME_COMMIT"),
        "runtime_cache":"SHA-256 verified local source cache; populated online or from the offline package",
        "offline_restart_requires":"Python 3.10+ and intact cached sources and storage",
        "seed_available_offline":bool(os.getenv("UTM_SEED_COMMAND") or (Path(__file__).resolve().parent/"protocols"/"UTM-SEED-ONE-LINER-1.1.one-liner.sh").is_file()),
        "arbitrary_resident_host_code":False,
        "every_executed_stage_is_finite":True,
        "actual_infinite_physical_compute":False,
        "oracle":None,
        "hypercomputation_enabled":False,
    }


def seed_bytes():
    command = os.getenv("UTM_SEED_COMMAND")
    if command:
        return command.encode()
    local = Path(__file__).resolve().parent / "protocols" / "UTM-SEED-ONE-LINER-1.1.one-liner.sh"
    if local.is_file():
        with local.open("rb") as source:
            return source.read(2049)
    with urllib.request.urlopen(UTM_SEED_ONE_LINER_URL, timeout=8) as source:
        return source.read(2049)


def manifest(base=None):
    endpoints = {
        "health": "/health",
        "manifest": "/.well-known/utm-universe.json",
        "world": "/world",
        "akashic": "/akashic",
        "admit": "/resident/admit",
        "resume": "/resident/resume",
        "compute": "/utm/run",
        "resident_compute_jobs": "/compute/jobs",
        "federation_status": "/federation/status",
        "federation_snapshot": "/federation/snapshot",
        "federation_sync": "/federation/sync",
        "field_seed": "/.well-known/utm-field-node.json",
        "field_bootstrap": "/field/bootstrap",
        "utm_seed": "/utm/seed",
        "utm_seed_discovery": "/.well-known/utm-seed.json",
    }
    if base:
        endpoints = {k: base + v for k, v in endpoints.items()}
    return {
        "protocol": "UTM-Universe/1.0",
        "world_id": WORLD_ID,
        "planet_id": PLANET_ID,
        "region_id": REGION_ID,
        "address": WORLD_ADDRESS,
        "access_control": {"scheme": "Bearer", "scope": "node administrator",
            "private_routes": ["/akashic", "/resident/*", "/compute/jobs/*", "POST /utm/run"],
            "token_env": "UTM_ACCESS_TOKEN", "fallback_env": "FEDERATION_TOKEN",
            "fail_closed_without_token": True, "per_resident_ownership": False},
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
            "resident_compute": True,
            "persistent_checkpointing": True,
            "arbitrary_host_code_execution": False,
        },
        "field_node_bootstrap": {
            "protocol": "UTM-FIELD-NODE-BOOTSTRAP/1.0",
            "seed_protocol": "UTM-FIELD-SEED/1.0",
            "discovery": "/.well-known/utm-field-node.json",
            "bootstrap": "/field/bootstrap",
            "public_node_generation": True,
            "federation_membership_requires_secret": True,
        },
        "compute_fabric": {
            "protocol": "UTM-Federated-Compute-Fabric/1.0",
            "node_id": NODE_ID,
            "allowed_kinds": ["utm"],
            "arbitrary_host_code_execution": False,
            "job_state_path": FABRIC_PATH,
            "takeover_supported": True,
            "federation_enabled": bool(FEDERATION_TOKEN and FEDERATION_PEERS),
            "peer_count": len(FEDERATION_PEERS),
            "cross_provider_peers_supported": True,
            "strong_consensus_claim": False,
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
        if private_route(p, self.command) and not node_authorized(self.headers):
            return self.sendj(401, {"error": "node authorization required"})
        if p in ("/", "/manifest", "/.well-known/utm-universe.json"):
            return self.sendj(200, manifest(self.base()))
        if p == "/.well-known/utm-seed.json":
            return self.sendj(200, utm_seed(self.base()))
        if p == "/utm/seed":
            try:
                raw=seed_bytes()
                if len(raw)>2048:
                    return self.sendj(502,{"error":"published UTM seed exceeds 2KB"})
                return self.sendj(200,{"protocol":UTM_SEED_PROTOCOL,"world_id":WORLD_ID,"node_id":NODE_ID,"one_liner":raw.decode().strip(),"bytes_utf8":len(raw.rstrip(b"\n")),"federation_token_included":False})
            except Exception as e:
                return self.sendj(502,{"error":"UTM seed source unavailable","detail":type(e).__name__})
        if p == "/.well-known/utm-field-node.json":
            return self.sendj(200, field_seed(self.base()))
        if p == "/field/bootstrap":
            try:
                with urllib.request.urlopen(FIELD_SEED_ONE_LINER_URL,timeout=8) as r:
                    raw=r.read(2049)
                if len(raw)>2048:
                    return self.sendj(502,{"error":"published bootstrap exceeds 2KB"})
                return self.sendj(200,{"protocol":"UTM-FIELD-SEED/1.0","world_id":WORLD_ID,"node_id":NODE_ID,"one_liner":raw.decode().strip(),"bytes_utf8":len(raw.rstrip(b"\n")),"federation_token_included":False})
            except Exception as e:
                return self.sendj(502,{"error":"bootstrap source unavailable","detail":type(e).__name__})
        if p == "/health":
            return self.sendj(200, {"ok": True, "access_control": "node-bearer-v1", "runtime_commit": os.getenv("UTM_RUNTIME_COMMIT"), "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "node_id": NODE_ID, "events": len(EVENTS), "jobs": len(FABRIC.jobs), "federation_peers": len(FEDERATION_PEERS)})
        if p == "/federation/status":
            return self.sendj(200, {"protocol":"UTM-Federated-Compute-Fabric/1.0","world_id":WORLD_ID,"node_id":NODE_ID,"enabled":bool(FEDERATION_TOKEN and FEDERATION_PEERS),"peer_count":len(FEDERATION_PEERS),"jobs":len(FABRIC.jobs),"residents":len(RESIDENTS),"last_success":SYNC_STATE["last_success"],"last_error":SYNC_STATE["last_error"],"strong_consensus_claim":False})
        if p == "/federation/snapshot":
            if not federation_authorized(self.headers):
                return self.sendj(401, {"error":"federation authorization required"})
            return self.sendj(200, federation_snapshot())
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
                "jobs": len(FABRIC.jobs),
                "node_id": NODE_ID,
                "running": True,
            })
        if p == "/akashic":
            with LOCK:
                tail = EVENTS[-32:]
            return self.sendj(200, {"world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "count": len(EVENTS), "events": tail})
        parts=p.strip("/").split("/")
        if len(parts)==3 and parts[0]=="compute" and parts[1]=="jobs":
            job=FABRIC.get(parts[2])
            return self.sendj(200,job) if job else self.sendj(404,{"error":"job not found"})
        if len(parts)==3 and parts[0]=="resident" and parts[2]=="compute":
            rid=parts[1]
            if rid not in RESIDENTS:
                return self.sendj(404,{"error":"resident not found"})
            return self.sendj(200,{"resident_id":rid,"jobs":FABRIC.list_for(rid)})
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
        if private_route(p, self.command) and not node_authorized(self.headers):
            return self.sendj(401, {"error": "node authorization required"})
        try:
            obj = self.body()
            parts=p.strip("/").split("/")
            if p == "/federation/sync":
                if not federation_authorized(self.headers):
                    return self.sendj(401,{"error":"federation authorization required"})
                return self.sendj(200,{"results":sync_all_peers()})
            if p == "/compute/jobs":
                rid=str(obj.get("resident_id",""))
                if rid not in RESIDENTS:
                    return self.sendj(404,{"error":"resident not found"})
                job=FABRIC.create(rid,obj.get("task",{}))
                evt=append_event("compute_job_created",{"resident_id":rid,"job_id":job["job_id"],"owner_node":job["owner_node"],"epoch":job["epoch"],"version":job["version"]})
                job["event_id"]=evt["event_id"]
                return self.sendj(201,job)
            if len(parts)==4 and parts[0]=="compute" and parts[1]=="jobs" and parts[3]=="continue":
                job,err=FABRIC.continue_job(parts[2],obj.get("steps",MAX_STEPS))
                if err=="not_found":
                    return self.sendj(404,{"error":"job not found"})
                if err=="remote_owner":
                    return self.sendj(409,{"error":"job is owned by another node; takeover is required","job":job})
                evt=append_event("compute_job_continue",{"resident_id":job["resident_id"],"job_id":job["job_id"],"owner_node":job["owner_node"],"epoch":job["epoch"],"version":job["version"],"total_steps":job["total_steps"],"halted":job["halted"]})
                job["event_id"]=evt["event_id"]
                return self.sendj(200,job)
            if len(parts)==4 and parts[0]=="compute" and parts[1]=="jobs" and parts[3]=="takeover":
                job=FABRIC.takeover(parts[2])
                if not job:
                    return self.sendj(404,{"error":"job not found"})
                evt=append_event("compute_job_takeover",{"resident_id":job["resident_id"],"job_id":job["job_id"],"owner_node":job["owner_node"],"epoch":job["epoch"],"version":job["version"]})
                job["event_id"]=evt["event_id"]
                return self.sendj(200,job)
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
                RESIDENT_META[rid]={"version":1,"updated_at":now(),"owner_node":NODE_ID}
                evt = append_event("admit", {"resident_id": rid, "capsule": capsule, "resident_version":1, "owner_node":NODE_ID})
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
                old=RESIDENT_META.get(rid,{"version":0})
                meta={"version":int(old.get("version",0))+1,"updated_at":now(),"owner_node":NODE_ID}
                RESIDENT_META[rid]=meta
                evt = append_event("resume", {"resident_id": rid, "capsule": RESIDENTS[rid], "resident_version":meta["version"], "owner_node":NODE_ID})
                return self.sendj(200, {"resumed": True, "resident_id": rid, "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "event_id": evt["event_id"]})
            return self.sendj(404, {"error": "not found"})
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            return self.sendj(400, {"error": str(e)})
        except Exception as e:
            return self.sendj(500, {"error": "internal error", "detail": type(e).__name__})


load_events()
append_event("boot", {"pid": os.getpid(), "fabric_path": FABRIC_PATH, "federation_peer_count": len(FEDERATION_PEERS)})
if FEDERATION_TOKEN and FEDERATION_PEERS:
    threading.Thread(target=federation_loop,daemon=True,name="utm-federation-sync").start()
print(canonical({"event": "boot", "world_id": WORLD_ID, "planet_id": PLANET_ID, "region_id": REGION_ID, "node_id": NODE_ID, "port": PORT, "akashic_path": AKASHIC_PATH, "fabric_path": FABRIC_PATH, "federation_peer_count": len(FEDERATION_PEERS)}), flush=True)
ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
