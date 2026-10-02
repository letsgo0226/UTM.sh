#!/usr/bin/env python3
import json, subprocess, sys, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from compile_native_stage import compile_bundle
from run_native_stage import run_bundle

class NativeLogOmegaTests(unittest.TestCase):
    def test_scalar_and_vector_addition_run_in_utm(self):
        bundle=compile_bundle({0:2,3:1},{0:3,2:2},stage=42)
        self.assertEqual(len(bundle["jobs"]),3)
        r=run_bundle(bundle)
        self.assertTrue(r["all_verified"])
        lengths={x["coordinate"]:len(x["result"]["tape"].replace("_","")) for x in r["jobs"]}
        self.assertEqual(lengths,{0:5,2:2,3:1})

    def test_commutativity_at_bundle_result(self):
        a=run_bundle(compile_bundle({0:2,1:4},{0:3,2:1}))
        b=run_bundle(compile_bundle({0:3,2:1},{0:2,1:4}))
        da={x["coordinate"]:x["result"]["tape"] for x in a["jobs"]}
        db={x["coordinate"]:x["result"]["tape"] for x in b["jobs"]}
        self.assertEqual(da,db)

    def test_gprogram_round_trip_execution(self):
        b=compile_bundle({7:2},{7:1})
        self.assertTrue(b["jobs"][0]["GPROGRAM"].isdigit())
        self.assertTrue(run_bundle(b)["all_verified"])

if __name__=="__main__":
    unittest.main()
