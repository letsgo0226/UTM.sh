import json, math
from pathlib import Path

SPEC_PATH = Path(__file__).with_name("axioms") / "THREE_UNIVERSE_AXIOMS.json"
TOL = 1e-12

def load_spec():
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))

def _close(a, b):
    return math.isclose(float(a), float(b), rel_tol=TOL, abs_tol=TOL)

def verify_spec(spec=None):
    s = spec or load_spec()
    checks = {
        "formal_hypothesis_marked": s.get("status") == "formal_hypothesis",
        "formal_scope_marked": s.get("scope") == "formal_model_only",
        "three_axioms_present": [a.get("id") for a in s.get("axioms", [])] == ["A1","A2","A3"],
        "host_is_P_minus_1": s.get("symbols", {}).get("host_universe") == "P_-1",
        "embedded_is_P_0": s.get("symbols", {}).get("embedded_universe") == "P_0",
        "omega_is_fixed_point_symbol": s.get("symbols", {}).get("fixed_point") == "Omega",
        "abelian_kernel_declared": s.get("log_abelian_interface", {}).get("composition") == "x+y=log(a)+log(b)=log(ab)",
        "omega_godel_identity": s.get("log_abelian_interface", {}).get("omega_identity", {}).get("G(Omega)") == 1,
        "omega_log_identity": s.get("log_abelian_interface", {}).get("omega_identity", {}).get("lambda(Omega)") == 0 and s.get("log_abelian_interface", {}).get("omega_identity", {}).get("xi(Omega)") == 0,
        "no_external_truth_claim": s.get("deployment_semantics", {}).get("external_truth_established") is False,
        "no_infinite_compute_claim": s.get("deployment_semantics", {}).get("actual_infinite_physical_compute") is False,
        "finite_certificate_not_limit_proof": s.get("deployment_semantics", {}).get("infinite_limit_proved_by_finite_certificate") is False,
    }
    return {
        "valid": all(checks.values()),
        "checks": checks,
        "scope": "formal verification of the axiom-layer specification only",
        "external_truth_established": False,
    }

def verify_state(payload, spec=None):
    s = spec or load_spec()
    state = payload.get("state", {})
    pair = payload.get("pair", {})
    g = int(state.get("godel", 1))
    if g < 1:
        raise ValueError("state.godel must be a positive integer")
    x = float(state.get("log_coordinate", math.log(g)))
    host_now = float(state.get("host_resource_now", 0))
    host_baseline = float(state.get("host_resource_baseline", host_now))

    checks = {
        "A1_host_reference": state.get("host_universe") == s["symbols"]["host_universe"],
        "A1_embedded_reference": state.get("embedded_universe") == s["symbols"]["embedded_universe"],
        "A2_host_resource_invariant": _close(host_now, host_baseline),
        "log_coordinate_matches_godel": _close(x, math.log(g)),
    }

    if pair:
        n_plus = int(pair.get("positive_n", 0))
        n_minus = int(pair.get("negative_n", 0))
        x_plus = float(pair.get("positive_coordinate", 0))
        x_minus = float(pair.get("negative_coordinate", 0))
        checks.update({
            "A3_indices_are_paired": n_plus > 0 and n_minus == -n_plus,
            "A3_finite_dual_coordinate_surrogate": _close(x_plus + x_minus, 0),
        })

    certificate = {
        "protocol": s["protocol"],
        "axiom_layer_valid": all(checks.values()) and verify_spec(s)["valid"],
        "checks": checks,
        "omega": {"godel_identity": 1, "log_identity": 0},
        "representation": "Abelian",
        "execution_semantics": "causal/non-commutative operations may be reconstructed after decoding",
        "external_truth_established": False,
        "infinite_limit_proved": False,
        "actual_infinite_physical_compute": False,
    }
    return certificate

def verify_deployment_gate(payload, spec=None):
    base = payload.get("condition_certificate", {})
    required = [
        "consistent",
        "sufficiently_complete",
        "integrity_verified",
        "cczis_verified",
        "human_override_preserved",
        "non_coercion_preserved",
        "reversible_or_rollback",
        "authorized_shutdown_preserved",
        "target_certificate_empirical_separation",
        "no_arbitrary_host_code_execution",
    ]
    gateway_ok = all(base.get(k) is True for k in required)
    ax = verify_state(payload.get("three_axiom_state", {}), spec)
    return {
        "admissible_for_gateway_verification": gateway_ok and ax["axiom_layer_valid"],
        "existing_gateway_conditions_pass": gateway_ok,
        "three_axiom_certificate": ax,
        "authorization_note": "A valid certificate does not grant GitHub/Railway/platform privilege."
    }
