import unittest

from core import (
    decode_text,
    encode_text,
    program_lift,
    solve_ac,
    tensor_lift,
    verify_certificate,
)


class AnalyticLiftTests(unittest.TestCase):
    def test_base257_roundtrip(self):
        text = '{"hello":"宇宙"}'
        self.assertEqual(decode_text(encode_text(text)), text)

    def test_polynomial_entire_continuation(self):
        result = solve_ac({
            "kind": "polynomial",
            "source_coefficients": ["1", "2", "3/2"],
            "candidate_coefficients": ["1", "2", "3/2"],
            "target_domain": "C",
        })
        self.assertEqual(result["status"], "proved")
        self.assertEqual(result["residual"], 0)

    def test_polynomial_rejects_changed_candidate(self):
        result = solve_ac({
            "kind": "polynomial",
            "source_coefficients": ["1", "2"],
            "candidate_coefficients": ["1", "3"],
            "target_domain": "C",
        })
        self.assertEqual(result["status"], "rejected-candidate")
        self.assertEqual(result["residual"], 1)

    def test_geometric_series(self):
        result = solve_ac({"kind": "geometric_series"})
        self.assertEqual(result["status"], "proved")
        self.assertEqual(result["result"]["continuation"], "1/(1-z)")

    def test_log_is_lifted(self):
        result = solve_ac({"kind": "log_germ"})
        self.assertEqual(result["status"], "proved-lift")
        self.assertEqual(result["result"]["projection"], "pi(w)=exp(w)")

    def test_sqrt_is_lifted(self):
        result = solve_ac({"kind": "sqrt_germ"})
        self.assertEqual(result["status"], "proved-lift")
        self.assertEqual(result["result"]["projection"], "pi(w)=w^2")

    def test_natural_boundary_crossing_is_rejected(self):
        result = solve_ac({"kind": "lacunary_2n", "target_domain": "cross-unit-circle"})
        self.assertEqual(result["status"], "disproved-for-target-domain")

    def test_unknown_is_not_declared_false(self):
        result = solve_ac({"kind": "mystery_function"})
        self.assertEqual(result["status"], "undetermined")
        self.assertTrue(result["result"]["nonexistence_not_inferred"])

    def test_zeta_is_meromorphic_schema_not_rh_proof(self):
        result = solve_ac({"kind": "riemann_zeta"})
        self.assertEqual(result["status"], "theorem-schema")
        self.assertFalse(result["result"]["rh_proof"])
        self.assertEqual(result["result"]["pole"]["point"], "s=1")

    def test_tensor_lift(self):
        result = tensor_lift(3, 2)
        self.assertEqual(result["interaction_coordinate_count"], 9)

    def test_program_lift_certificate(self):
        result = program_lift({"program": "0,A,H,A,R"}, 1)
        self.assertTrue(result["roundtrip"])
        payload = {"x": 1, "y": [2, 3]}
        from core import certificate
        cert = certificate(payload)
        checked = verify_certificate(payload, cert["godel"])
        self.assertTrue(checked["verified"])


if __name__ == "__main__":
    unittest.main()
