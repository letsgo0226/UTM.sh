import unittest
import app

def gateway_certificate():
    return {
        "consistent":True,
        "sufficiently_complete":True,
        "integrity_verified":True,
        "cczis_verified":True,
        "human_override_preserved":True,
        "non_coercion_preserved":True,
        "reversible_or_rollback":True,
        "authorized_shutdown_preserved":True,
        "target_certificate_empirical_separation":True,
        "no_arbitrary_host_code_execution":True
    }

def axiom_state():
    return {
        "state":{
            "host_universe":"P_-1",
            "embedded_universe":"P_0",
            "host_resource_baseline":42,
            "host_resource_now":42,
            "godel":1
        }
    }

def omega_state():
    return {
        "stage":42,
        "resource_budget":1000,
        "resource_used":42,
        "valuation":{"0":1,"1":2},
        "oracle":None
    }

class IntegratedPreGateTests(unittest.TestCase):
    def test_axiom_plus_omega_gate_accepts_finite_stage(self):
        r=app.deployment_preverify({
            "condition_certificate":gateway_certificate(),
            "three_axiom_state":axiom_state(),
            "utm_omega_state":omega_state()
        })
        self.assertTrue(r["admissible_for_gateway_verification"])
        self.assertTrue(r["three_axiom_certificate"]["axiom_layer_valid"])
        self.assertTrue(r["utm_omega_certificate"]["valid_finite_stage"])

    def test_omega_state_is_required(self):
        r=app.deployment_preverify({
            "condition_certificate":gateway_certificate(),
            "three_axiom_state":axiom_state()
        })
        self.assertFalse(r["admissible_for_gateway_verification"])

    def test_oracle_does_not_sneak_into_ordinary_utm(self):
        o=omega_state()
        o["oracle"]="HALT"
        r=app.deployment_preverify({
            "condition_certificate":gateway_certificate(),
            "three_axiom_state":axiom_state(),
            "utm_omega_state":o
        })
        self.assertFalse(r["admissible_for_gateway_verification"])
        self.assertFalse(r["utm_omega_certificate"]["checks"]["ordinary_utm_no_oracle"])

if __name__=="__main__":
    unittest.main()
