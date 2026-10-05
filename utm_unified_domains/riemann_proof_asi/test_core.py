import unittest
from core import certificate, decode_text, encode_text, manifest, riemann_coordinate, run_utm, verify_candidate, verify_certificate


class CoreTests(unittest.TestCase):
    def test_roundtrip(self):
        s = "Riemann ⇄ UTM 🌌"
        self.assertEqual(decode_text(encode_text(s)), s)

    def test_certificate(self):
        payload = {"x": 1, "y": [2, 3]}
        c = certificate(payload)
        self.assertTrue(c["roundtrip"])
        self.assertTrue(verify_certificate(payload, c["godel"])["verified"])

    def test_utm(self):
        program = "0,A,1,F,R;1,A,2,I,R;2,A,3,E,R;3,A,4,L,R;4,A,H,D,R"
        r = run_utm(program, "AAAAA", limit=100)
        self.assertTrue(r["halted"])
        self.assertEqual(r["output"], "FIELD")
        self.assertTrue(r["certificate"]["roundtrip"])

    def test_riemann(self):
        r = riemann_coordinate({"state": 42}, sigma=2.0, tau=3.0, terms=16)
        self.assertFalse(r["rh_proof"])
        self.assertFalse(r["zeta_equals_utm_claim"])

    def test_candidate_gate(self):
        m = manifest()
        candidate = {
            "constraints": {k: True for k in m["hard_constraints"]},
            "proofs": {k: True for k in m["required_proofs"]},
        }
        r = verify_candidate(candidate)
        self.assertTrue(r["accepted"])
        self.assertFalse(r["asi_proven"])


if __name__ == "__main__":
    unittest.main()
