"""Isolated HSI XY finite UTM canary; no broker/network interaction."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
CLI = ROOT / "xy_2k.sh"

class XYRuntimeCanary(unittest.TestCase):
    def execute(self, path, **overrides):
        env = os.environ.copy()
        env.update(HSI_STATE=str(path), HSI_PROGRAM="2", HSI_WORD="1")
        env.update(overrides)
        p = subprocess.run(["sh", str(CLI)], env=env, cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def test_strict_2k_shell(self):
        raw = CLI.read_bytes()
        self.assertLess(len(raw), 2048)
        self.assertTrue(raw.startswith(b"#!/bin/sh\n"))

    def test_accepted_finite_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "accept.json"
            out = self.execute(state)
            self.assertEqual(out["accepted"], 1)
            self.assertEqual(out["D0"], 0)
            self.assertEqual(out["step"], 1)
            self.assertTrue(out["x"] and out["y"])
            saved = json.loads(state.read_text())
            self.assertEqual(saved["n"], 1)
            self.assertEqual(len(saved["H"]), 1)

    def test_rejected_candidate_keeps_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "reject.json"
            out = self.execute(state, HSI_CAND="[99,0,[]]")
            self.assertEqual(out["accepted"], 0)
            self.assertGreater(out["D0"], 0)
            self.assertEqual(out["step"], 0)
            saved = json.loads(state.read_text())
            self.assertEqual(saved["n"], 0)
            self.assertEqual(len(saved["H"]), 1)

if __name__ == "__main__":
    unittest.main()
