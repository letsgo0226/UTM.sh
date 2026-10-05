import unittest

from core import (
    compile_trace_function,
    decode_text,
    encode_text,
    manifest,
    run_trace,
    verify_candidate,
    verify_compilation,
)

PROGRAM = "0,A,1,F,R;1,A,2,I,R;2,A,3,E,R;3,A,4,L,R;4,A,H,D,R"


class CoreTests(unittest.TestCase):
    def test_roundtrip(self):
        value = "UTM ⇄ function 🌌"
        self.assertEqual(decode_text(encode_text(value)), value)

    def test_trace(self):
        trace = run_trace(PROGRAM, "AAAAA", limit=100)
        self.assertTrue(trace["halted"])
        self.assertEqual(trace["output"], "FIELD")
        self.assertEqual(trace["steps"], 5)
        self.assertEqual(len(trace["states"]), 6)

    def test_compile_function(self):
        bundle = compile_trace_function(PROGRAM, "AAAAA", limit=100)
        self.assertTrue(bundle["spectral_function"]["critical_line_by_construction"])
        self.assertEqual(len(bundle["transition_function"]["edges"]), 5)
        self.assertEqual(len(bundle["exact_integer_polynomial"]["factors"]), 6)
        self.assertFalse(bundle["formal_boundaries"]["rh_proof"])

    def test_recompute(self):
        bundle = compile_trace_function(PROGRAM, "AAAAA", limit=100)
        result = verify_compilation(bundle, PROGRAM, "AAAAA", limit=100)
        self.assertTrue(result["verified"])

    def test_candidate_gate(self):
        m = manifest()
        candidate = {
            "constraints": {k: True for k in m["hard_constraints"]},
            "proofs": {k: True for k in m["required_proofs"]},
        }
        self.assertTrue(verify_candidate(candidate)["accepted"])


if __name__ == "__main__":
    unittest.main()
