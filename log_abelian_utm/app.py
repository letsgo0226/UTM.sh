import json, math, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from axiom_verifier import load_spec, verify_spec, verify_state, verify_deployment_gate
from omega_verifier import load_omega_spec, verify_omega_spec, verify_finite_stage, verify_stage_extension, verify_abelian_pair

MAX_EVENTS = 64
MAX_COORD = 200
MAX_GODEL_DIGITS = 20000

def cantor(a: int, b: int) -> int:
    s = a + b
    return s * (s + 1) // 2 + b

def unpair(z: int):
    w = (math.isqrt(8*z + 1) - 1) // 2
    t = w * (w + 1) // 2
    b = z - t
    a = w - b
    return a, b

def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0: return False
        d += 2
    return True

_PRIMES = [2]
def nth_prime(n: int) -> int:
    if n < 0: raise ValueError("prime index must be nonnegative")
    c = _PRIMES[-1] + 1
    if c % 2 == 0: c += 1
    while len(_PRIMES) <= n:
        if is_prime(c): _PRIMES.append(c)
        c += 2
    return _PRIMES[n]

def prime_index(p: int) -> int:
    if not is_prime(p): raise ValueError("factor is not prime")
    i = 0
    while True:
        q = nth_prime(i)
        if q == p: return i
        if q > p: raise ValueError("prime not in canonical enumeration")
        i += 1

def normalize_event(e):
    step = int(e["step"])
    op = int(e["op"])
    if step < 0 or op < 0 or step > MAX_COORD or op > MAX_COORD:
        raise ValueError(f"step/op must be integers in 0..{MAX_COORD}")
    return {"step": step, "op": op}

def event_prime(e):
    e = normalize_event(e)
    return nth_prime(cantor(e["step"], e["op"]))

def encode_events(events):
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise ValueError(f"events must be a list with at most {MAX_EVENTS} entries")
    norm = [normalize_event(e) for e in events]
    ps = [event_prime(e) for e in norm]
    g = math.prod(ps) if ps else 1
    x = math.fsum(math.log(p) for p in ps)
    return {
        "events": norm,
        "godel_product": str(g),
        "log_coordinate": x,
        "canonical_events": sorted(norm, key=lambda e:(e["step"], e["op"])),
    }

def decode_godel(godel):
    s = str(godel)
    if len(s) > MAX_GODEL_DIGITS: raise ValueError("godel integer too large")
    n = int(s)
    if n < 1: raise ValueError("godel must be a positive integer")
    factors = []
    pidx = 0
    while n > 1:
        p = nth_prime(pidx)
        while n % p == 0:
            factors.append(p)
            n //= p
            if len(factors) > MAX_EVENTS: raise ValueError("too many encoded events")
        pidx += 1
        if p*p > n and n > 1:
            if not is_prime(n): raise ValueError("factorization exceeded canonical bound")
            factors.append(n)
            n = 1
    events = []
    for p in factors:
        idx = prime_index(p)
        step, op = unpair(idx)
        if step > MAX_COORD or op > MAX_COORD:
            raise ValueError("decoded coordinate exceeds bound")
        events.append({"step": step, "op": op})
    return sorted(events, key=lambda e:(e["step"], e["op"]))

def compose(left, right):
    L, R = encode_events(left), encode_events(right)
    both = encode_events(left + right)
    rev = encode_events(right + left)
    gl, gr = int(L["godel_product"]), int(R["godel_product"])
    return {
        "left": L,
        "right": R,
        "composition": both,
        "law": "log(a)+log(b)=log(ab)",
        "proof": {
            "product_identity": int(both["godel_product"]) == gl * gr,
            "commutative_product": gl * gr == gr * gl,
            "commutative_log": math.isclose(
                both["log_coordinate"], rev["log_coordinate"], rel_tol=1e-12, abs_tol=1e-12
            ),
            "causal_order_recoverable": decode_godel(both["godel_product"]) == both["canonical_events"],
        },
    }

def deployment_preverify(payload):
    base = verify_deployment_gate(payload)
    omega_input = payload.get("utm_omega_state")
    if omega_input is None:
        base["utm_omega_certificate"] = {"valid_finite_stage":False,"error":"utm_omega_state_required"}
        base["admissible_for_gateway_verification"] = False
    else:
        omega = verify_finite_stage(omega_input)
        base["utm_omega_certificate"] = omega
        base["admissible_for_gateway_verification"] = base["admissible_for_gateway_verification"] and omega["valid_finite_stage"]
    return base

class H(BaseHTTPRequestHandler):
    def send_json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False, separators=(",",":")).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length","0"))
        if n > 1_000_000: raise ValueError("request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if self.path == "/health":
            return self.send_json(200, {"ok":True,"service":"log-abelian-utm"})
        if self.path == "/axioms":
            spec = load_spec()
            return self.send_json(200, {"spec":spec,"verification":verify_spec(spec)})
        if self.path == "/omega":
            spec = load_omega_spec()
            return self.send_json(200, {"spec":spec,"verification":verify_omega_spec(spec)})
        if self.path in ("/", "/spec"):
            return self.send_json(200, {
                "service":"Logarithmic Abelian UTM",
                "version":"1.2",
                "kernel":"x+y=log(a)+log(b)=log(ab)",
                "representation":"finite events (step,op) -> Cantor index -> nth prime",
                "composition":"integer multiplication / log-space addition",
                "semantics":"representation is Abelian; decoded UTM causality remains ordered",
                "limits":{"max_events":MAX_EVENTS,"max_coordinate":MAX_COORD},
                "axiom_layer":"UTM-Three-Universe-Axiom-Layer/1.0",
                "omega_layer":"UTM-Omega-Unbounded-Compute/1.0",
                "compute_semantics":"potentially-unbounded formal horizon; every executed stage remains finite",
                "endpoints":["GET /health","GET /spec","GET /axioms","GET /omega","POST /encode","POST /compose","POST /decode","POST /axioms/verify","POST /omega/verify","POST /omega/compose","POST /omega/extend","POST /deploy/preverify"],
            })
        return self.send_json(404, {"error":"not_found"})

    def do_POST(self):
        try:
            b = self.body()
            if self.path == "/encode":
                return self.send_json(200, encode_events(b.get("events",[])))
            if self.path == "/compose":
                return self.send_json(200, compose(b.get("left",[]), b.get("right",[])))
            if self.path == "/decode":
                return self.send_json(200, {"events":decode_godel(b["godel"])})
            if self.path == "/axioms/verify":
                return self.send_json(200, verify_state(b))
            if self.path == "/omega/verify":
                return self.send_json(200, verify_finite_stage(b))
            if self.path == "/omega/compose":
                return self.send_json(200, verify_abelian_pair(b.get("left",{}), b.get("right",{})))
            if self.path == "/omega/extend":
                return self.send_json(200, verify_stage_extension(b["previous"], b["current"]))
            if self.path == "/deploy/preverify":
                return self.send_json(200, deployment_preverify(b))
            return self.send_json(404, {"error":"not_found"})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            return self.send_json(400, {"error":"bad_request","detail":str(e)})

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT","8080"))
    print(f"Logarithmic Abelian UTM listening on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0",port), H).serve_forever()
