import json
import os
from pathlib import Path
import subprocess
import unittest

from single_function import manifest, portable_projection, single_function_bundle, verify_bundle, verify_candidate

PROGRAM = "0,A,1,F,R;1,A,2,I,R;2,A,3,E,R;3,A,4,L,R;4,A,H,D,R"
ROOT = Path(__file__).resolve().parent
SEED = ROOT / "one-liner-2kb.sh"


class SingleFunctionTests(unittest.TestCase):
    def test_bundle(self):
        b = single_function_bundle(PROGRAM, "AAAAA", limit=100)
        self.assertEqual(b["protocol"], "UTM-Single-Function/1.0")
        self.assertEqual(b["output"], "FIELD")
        self.assertEqual(len(b["F_U"]), 5)
        self.assertEqual(len(b["P_U"]["factors"]), 6)
        self.assertTrue(b["Xi_U"]["critical_line_by_construction"])
        self.assertFalse(b["formal_boundaries"]["rh_proof"])
        self.assertTrue(verify_bundle(b, PROGRAM, "AAAAA", limit=100)["verified"])

    def test_seed_is_under_2kb(self):
        self.assertLessEqual(SEED.stat().st_size, 2048)

    def test_seed_matches_authoritative_projection(self):
        env = dict(os.environ)
        env.update({"TM_RULES": PROGRAM, "TM_INPUT": "AAAAA", "TM_LIMIT": "100"})
        proc = subprocess.run(["sh", str(SEED)], check=True, capture_output=True, text=True, env=env)
        self.assertEqual(json.loads(proc.stdout), portable_projection(PROGRAM, "AAAAA", limit=100))

    def test_candidate_gate(self):
        m = manifest()
        candidate = {
            "constraints": {k: True for k in m["hard_constraints"]},
            "proofs": {k: True for k in m["required_proofs"]},
        }
        self.assertTrue(verify_candidate(candidate)["accepted"])


if __name__ == "__main__":
    unittest.main()
