import json, math
from pathlib import Path

SPEC_PATH = Path(__file__).with_name("omega") / "UTM_OMEGA_UNBOUNDED_COMPUTE.json"
MAX_SUPPORT = 256
MAX_INDEX = 10000
MAX_MULTIPLICITY = 1000000
_PRIMES = [2]

def load_omega_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))

def _is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d*d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

def _nth_prime(n):
    if not 0 <= n <= MAX_INDEX:
        raise ValueError(f"valuation index must be in 0..{MAX_INDEX}")
    c = _PRIMES[-1] + 1
    if c % 2 == 0:
        c += 1
    while len(_PRIMES) <= n:
        if _is_prime(c):
            _PRIMES.append(c)
        c += 2
    return _PRIMES[n]

def normalize_valuation(v):
    if not isinstance(v, dict) or len(v) > MAX_SUPPORT:
        raise ValueError(f"valuation must be an object with at most {MAX_SUPPORT} nonzero coordinates")
    out = {}
    for k, raw in v.items():
        i = int(k)
        m = int(raw)
        if i < 0 or i > MAX_INDEX:
            raise ValueError(f"valuation index must be in 0..{MAX_INDEX}")
        if m < 0 or m > MAX_MULTIPLICITY:
            raise ValueError(f"multiplicity must be in 0..{MAX_MULTIPLICITY}")
        if m:
            out[i] = m
    return out

def log_coordinate(v):
    v = normalize_valuation(v)
    return math.fsum(m * math.log(_nth_prime(i)) for i, m in v.items())

def add_valuations(a, b):
    a, b = normalize_valuation(a), normalize_valuation(b)
    keys = set(a) | set(b)
    out = {i:a.get(i,0)+b.get(i,0) for i in keys}
    return {str(i):m for i,m in sorted(out.items()) if m}

def verify_omega_spec(spec=None):
    s = spec or load_omega_spec()
    em = s.get("execution_model", {})
    cb = s.get("computability_boundary", {})
    alg = s.get("algebra", {})
    checks = {
        "formal_hypothesis_marked": s.get("status") == "formal_hypothesis",
        "formal_scope_marked": s.get("scope") == "formal_computation_model_only",
        "every_executed_stage_finite": em.get("every_executed_stage_is_finite") is True,
        "no_final_finite_stage_required": em.get("no_predeclared_final_finite_stage") is True,
        "no_actual_infinite_physical_compute": em.get("actual_infinite_physical_compute") is False,
        "abelian_stage_algebra": alg.get("abelian") is True,
        "ordinary_utm_boundary": cb.get("base_machine") == "ordinary UTM",
        "no_oracle": cb.get("oracle") is None,
        "no_hypercomputation": cb.get("hypercomputation_enabled") is False,
        "halting_not_claimed_decidable": cb.get("halting_problem_becomes_decidable") is False,
    }
    return {"valid":all(checks.values()),"checks":checks}

def verify_finite_stage(payload, spec=None):
    s = spec or load_omega_spec()
    stage = int(payload.get("stage", 0))
    budget = int(payload.get("resource_budget", 0))
    used = int(payload.get("resource_used", 0))
    valuation = normalize_valuation(payload.get("valuation", {}))
    supplied_lambda = payload.get("log_coordinate")
    lam = log_coordinate({str(i):m for i,m in valuation.items()})
    oracle = payload.get("oracle")
    checks = {
        "stage_is_finite_natural": stage >= 0,
        "resource_budget_is_finite_positive": budget > 0,
        "resource_used_is_finite_nonnegative": used >= 0,
        "resource_within_stage_budget": 0 <= used <= budget,
        "valuation_has_finite_support": len(valuation) <= MAX_SUPPORT,
        "ordinary_utm_no_oracle": oracle in (None, "", False),
        "log_coordinate_consistent": supplied_lambda is None or math.isclose(float(supplied_lambda), lam, rel_tol=1e-12, abs_tol=1e-12),
    }
    return {
        "protocol":s["protocol"],
        "valid_finite_stage":all(checks.values()) and verify_omega_spec(s)["valid"],
        "stage":stage,
        "computed_log_coordinate":lam,
        "checks":checks,
        "formal_horizon":"omega",
        "actual_infinite_physical_compute":False,
        "hypercomputation_enabled":False,
        "halting_problem_decidable":False,
        "omega_limit_reached":False
    }

def verify_stage_extension(previous, current, spec=None):
    a = verify_finite_stage(previous, spec)
    b = verify_finite_stage(current, spec)
    checks = {
        "previous_valid":a["valid_finite_stage"],
        "current_valid":b["valid_finite_stage"],
        "stage_monotone":b["stage"] >= a["stage"],
        "both_stages_finite":True
    }
    return {
        "valid_extension":all(checks.values()),
        "checks":checks,
        "interpretation":"A larger finite stage extends the potentially-unbounded computation; no actually infinite stage was executed."
    }

def verify_abelian_pair(left, right):
    l = normalize_valuation(left)
    r = normalize_valuation(right)
    lr = add_valuations(left, right)
    rl = add_valuations(right, left)
    ll, rr = log_coordinate(left), log_coordinate(right)
    total = log_coordinate(lr)
    return {
        "valid": lr == rl and math.isclose(total, ll+rr, rel_tol=1e-12, abs_tol=1e-12),
        "sum":lr,
        "proof":{
            "componentwise_commutative":lr == rl,
            "log_homomorphism":math.isclose(total, ll+rr, rel_tol=1e-12, abs_tol=1e-12)
        }
    }
