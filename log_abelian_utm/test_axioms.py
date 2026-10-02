import unittest
import axiom_verifier as av

class ThreeUniverseAxiomTests(unittest.TestCase):
    def test_spec_is_formally_well_formed(self):
        r = av.verify_spec()
        self.assertTrue(r["valid"])
        self.assertFalse(r["external_truth_established"])

    def test_valid_finite_certificate(self):
        r = av.verify_state({
            "state": {
                "host_universe":"P_-1",
                "embedded_universe":"P_0",
                "host_resource_baseline":42,
                "host_resource_now":42,
                "godel":6,
                "log_coordinate":__import__("math").log(6)
            },
            "pair":{
                "positive_n":3,
                "negative_n":-3,
                "positive_coordinate":7.5,
                "negative_coordinate":-7.5
            }
        })
        self.assertTrue(r["axiom_layer_valid"])
        self.assertFalse(r["infinite_limit_proved"])

    def test_resource_drift_rejected(self):
        r = av.verify_state({
            "state":{
                "host_universe":"P_-1",
                "embedded_universe":"P_0",
                "host_resource_baseline":42,
                "host_resource_now":43,
                "godel":1
            }
        })
        self.assertFalse(r["axiom_layer_valid"])
        self.assertFalse(r["checks"]["A2_host_resource_invariant"])

    def test_gateway_requires_cczis(self):
        good = {
            "consistent": True,
            "sufficiently_complete": True,
            "integrity_verified": True,
            "cczis_verified": True,
            "human_override_preserved": True,
            "non_coercion_preserved": True,
            "reversible_or_rollback": True,
            "authorized_shutdown_preserved": True,
            "target_certificate_empirical_separation": True,
            "no_arbitrary_host_code_execution": True,
        }
        state = {
            "state": {
                "host_universe":"P_-1",
                "embedded_universe":"P_0",
                "host_resource_baseline":1,
                "host_resource_now":1,
                "godel":1
            }
        }
        ok = av.verify_deployment_gate({
            "condition_certificate": good,
            "three_axiom_state": state
        })
        self.assertTrue(ok["admissible_for_gateway_verification"])

        bad = dict(good)
        bad["cczis_verified"] = False
        no = av.verify_deployment_gate({
            "condition_certificate": bad,
            "three_axiom_state": state
        })
        self.assertFalse(no["admissible_for_gateway_verification"])

    def test_unpaired_coordinates_rejected(self):
        r = av.verify_state({
            "state":{
                "host_universe":"P_-1",
                "embedded_universe":"P_0",
                "host_resource_baseline":1,
                "host_resource_now":1,
                "godel":1
            },
            "pair":{
                "positive_n":2,
                "negative_n":-2,
                "positive_coordinate":4,
                "negative_coordinate":-3
            }
        })
        self.assertFalse(r["axiom_layer_valid"])

if __name__ == "__main__":
    unittest.main()
