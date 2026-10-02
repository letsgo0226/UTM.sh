import math, unittest
import omega_verifier as ov

class UTMOmegaTests(unittest.TestCase):
    def test_spec_boundary(self):
        r=ov.verify_omega_spec()
        self.assertTrue(r["valid"])

    def test_finite_stage(self):
        v={"0":2,"2":1}
        r=ov.verify_finite_stage({
            "stage":42,
            "resource_budget":100000,
            "resource_used":1234,
            "valuation":v,
            "log_coordinate":2*math.log(2)+math.log(5),
            "oracle":None
        })
        self.assertTrue(r["valid_finite_stage"])
        self.assertFalse(r["actual_infinite_physical_compute"])
        self.assertFalse(r["halting_problem_decidable"])
        self.assertFalse(r["omega_limit_reached"])

    def test_resource_overrun_rejected(self):
        r=ov.verify_finite_stage({
            "stage":3,
            "resource_budget":10,
            "resource_used":11,
            "valuation":{}
        })
        self.assertFalse(r["valid_finite_stage"])

    def test_oracle_rejected_from_ordinary_utm_mode(self):
        r=ov.verify_finite_stage({
            "stage":3,
            "resource_budget":10,
            "resource_used":1,
            "valuation":{},
            "oracle":"HALT"
        })
        self.assertFalse(r["valid_finite_stage"])

    def test_abelian_valuation(self):
        r=ov.verify_abelian_pair({"0":2,"4":1},{"1":3,"4":2})
        self.assertTrue(r["valid"])
        self.assertTrue(r["proof"]["componentwise_commutative"])
        self.assertTrue(r["proof"]["log_homomorphism"])

    def test_monotone_finite_extension(self):
        a={"stage":4,"resource_budget":10,"resource_used":2,"valuation":{"0":1}}
        b={"stage":9,"resource_budget":20,"resource_used":3,"valuation":{"0":1,"1":1}}
        self.assertTrue(ov.verify_stage_extension(a,b)["valid_extension"])

if __name__=="__main__":
    unittest.main()
